import os
from typing import Any
import unittest

from PIL.ImagePalette import ImagePalette
from PIL.Image import Image, open
from PIL.PyAccess import PyAccess
from utils import get_fusion_id_from_filename as gfiff

UPPER_COLOR_LIMIT = 1000


PINK = (255, 0, 255, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)


MAX_TRANSPARENCY = 0
MIN_TRANSPARENCY = 255


RGB_MODE = "RGB"
RGBA_MODE = "RGBA"
PALETTE_MODE = "P"


# class TestGalleryNames(unittest.TestCase):

#     def test_valid_filenames(self):
#         self.assertIsNotNone(gfiff("100.200.png"))
#         self.assertIsNotNone(gfiff("413.120c.png"))
#         self.assertIsNotNone(gfiff("SPOILER_225.85.png"))
#         self.assertIsNotNone(gfiff("SPOILER_355.73a.png"))
        
#     def test_invalid_filenames(self):
#         self.assertIsNone(gfiff("MagikarpSneasel129.215.png"))
#         self.assertIsNone(gfiff("CrobatKlinklang_169.337.png"))
#         self.assertIsNone(gfiff("Lapras_Cofragrigus_131.362.png"))
#         self.assertIsNone(gfiff("413.120ab.png"))
#         self.assertIsNone(gfiff("182.256-1.png"))
#         self.assertIsNone(gfiff("138.412.H.png"))
#         self.assertIsNone(gfiff("299.287_alt.png"))
#         self.assertIsNone(gfiff("411.367_ALT.png"))
#         self.assertIsNone(gfiff("299.287.png.png"))
#         self.assertIsNone(gfiff("299.287.jpeg"))


# class TestColourAmount(unittest.TestCase):
#     def test_colour_amount(self):
#         sprites = os.listdir("fixtures")
#         for sprite in sprites:
#             sprite_path = os.path.join("fixtures", sprite)
#             with Image.open(sprite_path) as image:
#                 colors = image.getcolors(UPPER_COLOR_LIMIT)
#                 useful_colors = remove_useless_colors(colors)


class TestTransparencyAmount(unittest.TestCase):
    def test_colour_amount(self):
        sprites = os.listdir("fixtures")
        for sprite in sprites:
            sprite_path = os.path.join("fixtures", sprite)
            with open(sprite_path) as image:
                palette = get_palette(image)
                pixels = get_pixels(image)
                update_transparency(pixels, image.mode, palette)
                # image.show()


def get_pixels(image:Image) -> PyAccess:
    return image.load()  # type: ignore


def update_transparency(pixels:PyAccess, image_mode:str, palette:ImagePalette|None):
    if image_mode == RGBA_MODE:
        update_rgba(pixels)
    elif image_mode == PALETTE_MODE:
        update_palette(pixels, palette)  # type: ignore
    elif image_mode == RGB_MODE:
        pass
    else:
        raise RuntimeError(image_mode)


def is_half_transparent(alpha):
    return alpha != 0 and alpha != 255


def is_transparent(alpha):
    return alpha == 0


def get_palette(image:Image) -> ImagePalette:
    return image.palette


def update_rgba(pixels:PyAccess):
    for i in range(0, 288):
        for j in range(0, 288):
            _r, _g, _b, alpha = pixels[i, j]
            if is_half_transparent(alpha):
                pixels[i, j] = PINK
            elif not is_transparent(alpha):
                pixels[i, j] = BLACK
            else:
                pixels[i, j] = WHITE


def update_palette(pixels:PyAccess, palette:ImagePalette):
    color_set = set()
    inverse_palette = {v: k for k, v in palette.colors.items()}
    for i in range(0, 288):
        for j in range(0, 288):
            palette_index = pixels[i, j]
            pixel_color = inverse_palette.get(palette_index)
            if pixel_color not in color_set:
                color_set.add(pixel_color)
                # print(palette_index, (i, j), pixel_color)


if __name__ == '__main__':
    unittest.main()
