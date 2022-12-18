from io import BytesIO
from typing import Any

import requests
from analysis import Analysis
from discord.message import Message
from discord.file import File
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

ASESPRITE_RATIO = 3

PINK = (255, 0, 255, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)


class SpriteContext():
    def __init__(self, message:Message):
        attachment_url = message.attachments[0].url
        raw_data = requests.get(attachment_url, stream=True).raw
        self.image = open(raw_data)
        self.pixels = get_pixels(self.image)

    def handle_sprite_size(self, analysis:Analysis):
        size = self.image.size
        if size != VALID_SIZE:
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
        asesprite_ratio = self.useless_amount/self.useful_amount
        if asesprite_ratio > ASESPRITE_RATIO:
            analysis.issues.add(AsepriteUser(asesprite_ratio))

    def handle_sprite_transparency(self, analysis:Analysis):
        transparency_amount = self.highlight_transparency()
        if transparency_amount > TRANSPARENCY_LIMIT:
            analysis.transparency = True
            analysis.transparency_image = self.image
            bytes = BytesIO()
            self.image.save(bytes, format="PNG")
            bytes.seek(0)
            analysis.transparency_file = File(bytes, filename="image.png")
            analysis.issues.add(TransparencyAmount(transparency_amount))

    def highlight_transparency(self) -> int:
        transparency_amount = 0
        first_pixel = self.pixels[0, 0]
        if is_indexed(first_pixel):
            return transparency_amount
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
    _r, _g, _b, alpha = color
    return alpha


def is_indexed(color:colorType) -> bool:
    return isinstance(color, int)


def main(analysis:Analysis):
    if analysis.severity == Severity.accepted:
        handle_valid_sprite(analysis)


def handle_valid_sprite(analysis:Analysis):
    content_context = SpriteContext(analysis.message)
    content_context.handle_sprite_size(analysis)
    content_context.handle_sprite_colours(analysis)
    content_context.handle_sprite_transparency(analysis)


    # """
    # if valid_fusion:
    #     results = sprite_analyzer.test_sprite(attachment_url)
    #     if utils.interesting_results(results):
    #         valid_fusion, description, warning, file_name = results
    #         if file_name is not None:
    #             file_path = os.path.join(os.getcwd(), "tmp", file_name)
    #             file = discord.File(file_path, filename="image.png")
    #             message_file = await sprite_stash_channel.send(file=file)
    #             os.remove(file_path)
    #             autogen_url = message_file.attachments[0].url
    # """
