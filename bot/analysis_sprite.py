
import requests
from analysis import Analysis
from enums import Severity
from issues import (AsepriteUser, ColorAmount, ColorExcess, InvalidSize,
                    TransparencyAmount, HalfPixelsAmount)
from PIL.Image import Image, open
from PIL.PyAccess import PyAccess


colorType = int|tuple


VALID_SIZE = (288,288)
UPPER_COLOR_LIMIT = 1000
MAX_SIZE = 288
COLOR_LIMIT = 64
STEP = 3
ASEPRITE_RATIO = 2


PINK =  (255, 0, 255, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
RED =   (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)


class SpriteContext():
    def __init__(self, analysis:Analysis):
        if analysis.attachment_url is None:
            raise RuntimeError()
        
        response = requests.get(analysis.attachment_url, stream=True)

        print(type(response))
        print(type(response.raw))

        self.raw_data = response.raw
        self.image = open(self.raw_data)
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
            transparency_amount, image = self.highlight_transparency()
            if transparency_amount > 0:
                analysis.transparency_issue = True
                analysis.transparency_image = image
                if analysis.severity is not Severity.refused:
                    analysis.severity = Severity.controversial
                analysis.issues.add(TransparencyAmount(transparency_amount))

    def handle_sprite_half_pixels(self, analysis:Analysis):
        if analysis.size_issue is False:
            half_pixels_amount, image = self.highlight_half_pixels()
            if half_pixels_amount > 0:
                analysis.half_pixels_issue = True
                analysis.transparency_image = image
                analysis.severity = Severity.refused
                analysis.issues.add(HalfPixelsAmount(half_pixels_amount))

    def highlight_transparency(self)->tuple[int, Image]:
        local_image = open(self.raw_data)
        local_pixels = get_pixels(local_image)
        first_pixel = self.pixels[0, 0]
        transparency_amount = 0
        if is_indexed(first_pixel):
            return (transparency_amount, local_image)
        for i in range(0, 288):
            for j in range(0, 288):
                color = self.pixels[i, j]
                alpha = get_alpha(color)
                if is_half_transparent(alpha):
                    local_pixels[i, j] = PINK
                    transparency_amount += 1
                elif not is_transparent(alpha):
                    local_pixels[i, j] = BLACK
                else:
                    local_pixels[i, j] = WHITE
        return (transparency_amount, local_image)

    def highlight_half_pixels(self)->tuple[int, Image]:
        local_image = open(self.raw_data)
        local_pixels = get_pixels(local_image)
        (delta_i, delta_j) = find_first_pixel(self.pixels)
        max_i = 288 - (STEP - delta_i)
        max_j = 288 - (STEP - delta_j)
        half_pixels_amount = 0
        for i in range(delta_i, max_i, STEP):
            for j in range(delta_j, max_j, STEP):
                color_set = get_color_set(i, j, self.pixels)
                color = get_color_from_set(color_set)
                recolor_pixels(i, j, local_pixels, color)
        return half_pixels_amount, local_image


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


def find_first_pixel(pixels:PyAccess):
    default_value = pixels[0, 0]
    for i in range(0, 288):
        for j in range(0, 288):
            if default_value != pixels[i, j]:
                return (i%3, j%3)
    return (0, 0)


def get_color_set(i:int, j:int, pixels:PyAccess):
    color_set = set()
    for increment_i in range(0, STEP):
        for increment_j in range(0, STEP):
            local_i = i + increment_i
            local_j = j + increment_j
            color_set.add(pixels[local_i, local_j])
    return color_set


def get_color_from_set(color_set:set):
    if len(color_set) > 1:
        return RED
    return GREEN


def recolor_pixels(i:int, j:int, pixels:PyAccess, color:tuple):
    for increment_i in range(0, STEP):
        for increment_j in range(0, STEP):
            local_i = i + increment_i
            local_j = j + increment_j
            pixels[local_i, local_j] = color


def main(analysis:Analysis):
    if analysis.severity == Severity.accepted:
        handle_valid_sprite(analysis)


def handle_valid_sprite(analysis:Analysis):
    content_context = SpriteContext(analysis)
    content_context.handle_sprite_size(analysis)
    content_context.handle_sprite_colours(analysis)
    content_context.handle_sprite_transparency(analysis)
    content_context.handle_sprite_half_pixels(analysis)
