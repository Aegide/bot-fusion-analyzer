
import requests
from analysis import Analysis
from discord.message import Message
from enums import Severity
from issues import (AsepriteUser, ColorAmount, ColorExcess, InvalidSize,
                    TransparencyAmount)
from PIL.Image import Image, open
from PIL.PyAccess import PyAccess

VALID_SIZE = (288,288)
UPPER_COLOR_LIMIT = 1000
COLOR_LIMIT = 100
TRANSPARENCY_LIMIT = 0

colorType = int|tuple

ASEPRITE_RATIO = 3

PINK = (255, 0, 255, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)


class SpriteContext():
    def __init__(self, analysis:Analysis):
        if analysis.attachment_url is None:
            raise RuntimeError()
        raw_data = requests.get(analysis.attachment_url, stream=True).raw
        self.image = open(raw_data)
        self.pixels = get_pixels(self.image)

    def handle_sprite_size(self, analysis:Analysis):
        size = self.image.size
        if size != VALID_SIZE:
            analysis.size_issue = True
            analysis.severity = Severity.refused
            analysis.issues.add(InvalidSize(size))

    def handle_sprite_colours(self, analysis:Analysis):
        all_colors = self.image.getcolors(UPPER_COLOR_LIMIT)
        useful_colors = remove_useless_colors(all_colors)
        self.handle_color_amount(analysis, all_colors, useful_colors)
        self.handle_color_limit(analysis)
        self.handle_aseprite(analysis)

    def handle_color_amount(self, analysis:Analysis, all_colors, useful_colors):
        self.all_amount = len(all_colors)
        self.useful_amount = len(useful_colors)
        self.useless_amount = self.all_amount - self.useful_amount
        analysis.issues.add(ColorAmount(self.useful_amount))

    def handle_color_limit(self, analysis:Analysis):
        if self.useful_amount > COLOR_LIMIT:
            analysis.severity = Severity.refused
            analysis.issues.add(ColorExcess(COLOR_LIMIT))

    def handle_aseprite(self, analysis:Analysis):
        aseprite_ratio = self.useless_amount/self.useful_amount
        if aseprite_ratio > ASEPRITE_RATIO:
            analysis.issues.add(AsepriteUser(aseprite_ratio))

    def handle_sprite_transparency(self, analysis:Analysis):
        if analysis.size_issue is False:
            transparency_amount = self.highlight_transparency()
            if transparency_amount > TRANSPARENCY_LIMIT:
                analysis.transparency = True
                analysis.transparency_image = self.image
                if analysis.severity is not Severity.refused:
                    analysis.severity = Severity.controversial
                analysis.issues.add(TransparencyAmount(transparency_amount))

    def highlight_transparency(self) -> int:
        i, j = -1, -1
        transparency_amount = 0
        first_pixel = self.pixels[0, 0]
        if is_indexed(first_pixel):
            return transparency_amount
        try:
            for i in range(0, 288):
                for j in range(0, 288):
                    color = self.pixels[i, j]
                    alpha = get_alpha(color)
                    if is_half_transparent(alpha):
                        self.pixels[i, j] = PINK
                        transparency_amount += 1
                    elif not is_transparent(alpha):
                        self.pixels[i, j] = BLACK
                    else:
                        self.pixels[i, j] = WHITE
        except IndexError as index_error:
            raise IndexError(i, j) from index_error
        return transparency_amount


def is_half_transparent(alpha):
    return alpha != 0 and alpha != 255


def is_transparent(alpha:int) -> bool:
    return alpha == 0


def get_pixels(image:Image) -> PyAccess:
    return image.load()  # type: ignore


def remove_useless_colors(old_colors:list):
    new_colors = []
    for old_color in old_colors:
        _color_amount, color_value = old_color
        if not is_useless_color(color_value):
            new_colors.append(old_color)
    return new_colors


def is_useless_color(color:colorType):
    if is_indexed(color):
        return False
    alpha = get_alpha(color)        # type: ignore
    return is_transparent(alpha)    # type: ignore


def get_alpha(color:tuple) -> int:
    if len(color) != 4:
        raise ValueError(len(color), color)
    _r, _g, _b, alpha = color
    return alpha


def is_indexed(color:colorType) -> bool:
    return isinstance(color, int)


def main(analysis:Analysis):
    if analysis.severity == Severity.accepted:
        handle_valid_sprite(analysis)


def handle_valid_sprite(analysis:Analysis):
    content_context = SpriteContext(analysis)
    content_context.handle_sprite_size(analysis)
    content_context.handle_sprite_colours(analysis)
    content_context.handle_sprite_transparency(analysis)
