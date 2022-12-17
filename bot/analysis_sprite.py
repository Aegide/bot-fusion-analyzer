from typing import Any

import requests
from analysis import Analysis
from discord import Message
from enums import Severity
from issues import AsepriteUser, ColorAmount, ColorExcess, InvalidSize
from PIL import Image

VALID_SIZE = (288,288)
UPPER_COLOR_LIMIT = 1000
COLOR_LIMIT = 100


colorType = int|tuple

ASESPRITE_RATIO = 2


class SpriteContext():
    def __init__(self, message:Message):
        first_attachment = message.attachments[0].url
        raw_data = requests.get(first_attachment, stream=True).raw
        self.image = Image.open(raw_data)

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

def remove_useless_colors(old_colors:list):
    new_colors = []
    for old_color in old_colors:
        _color_amount, color_value = old_color
        if not is_useless_color(color_value):
            new_colors.append(old_color)
    return new_colors

def is_useless_color(color:colorType):
    if is_palette(color):
        return False
    return is_invisible(color)  # type: ignore

def is_palette(color:colorType):
    return isinstance(color, int)

def is_invisible(color:tuple):
    return alpha(color) == 0

def alpha(color:tuple):
    return color[3]

def main(analysis:Analysis):
    if analysis.severity == Severity.accepted:
        handle_valid_sprite(analysis)

def handle_valid_sprite(analysis:Analysis):
    content_context = SpriteContext(analysis.message)
    content_context.handle_sprite_size(analysis)
    content_context.handle_sprite_colours(analysis)
    # content_context.handle_sprite_transparency(analysis)

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
