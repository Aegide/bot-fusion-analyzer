import os
import unittest

from PIL.Image import Image, open
from PIL.PyAccess import PyAccess
from utils import get_fusion_id_from_filename as gfiff

UPPER_COLOR_LIMIT = 1000


PINK = (255, 0, 255, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)


MAX_TRANSPARENCY = 0
MIN_TRANSPARENCY = 255

class TestGalleryNames(unittest.TestCase):

    def test_valid_filenames(self):
        self.assertIsNotNone(gfiff("100.200.png"))
        self.assertIsNotNone(gfiff("413.120c.png"))
        self.assertIsNotNone(gfiff("SPOILER_225.85.png"))
        self.assertIsNotNone(gfiff("SPOILER_355.73a.png"))
        
    def test_invalid_filenames(self):
        self.assertIsNone(gfiff("MagikarpSneasel129.215.png"))
        self.assertIsNone(gfiff("CrobatKlinklang_169.337.png"))
        self.assertIsNone(gfiff("Lapras_Cofragrigus_131.362.png"))
        self.assertIsNone(gfiff("413.120ab.png"))
        self.assertIsNone(gfiff("182.256-1.png"))
        self.assertIsNone(gfiff("138.412.H.png"))
        self.assertIsNone(gfiff("299.287_alt.png"))
        self.assertIsNone(gfiff("411.367_ALT.png"))
        self.assertIsNone(gfiff("299.287.png.png"))
        self.assertIsNone(gfiff("299.287.jpeg"))


# class TestColourAmount(unittest.TestCase):
#     def test_colour_amount(self):
#         sprites = os.listdir("fixtures")
#         for sprite in sprites:
#             sprite_path = os.path.join("fixtures", sprite)
#             with Image.open(sprite_path) as image:
#                 colors = image.getcolors(UPPER_COLOR_LIMIT)
#                 useful_colors = remove_useless_colors(colors)


# class TestTransparencyAmount(unittest.TestCase):
#     def test_colour_amount(self):
#         sprites = os.listdir("fixtures")
#         for sprite in sprites:
#             sprite_path = os.path.join("fixtures", sprite)
#             with open(sprite_path) as image:
#                 print(sprite)
#                 pixels = get_pixels(image)
#                 explore(pixels)
#                 print(" ")
#                 image.show()

# def func(value):
#     print(value, type(value))
#     return value


# def get_pixels(image:Image) -> PyAccess:
#     return image.load()  # type: ignore


# def explore(pixels:PyAccess):
#     if isinstance(pixels[0, 0], tuple):
#         explore_rgb(pixels)



# def explore_rgb(pixels:PyAccess):
#     for i in range(0, 288):
#         for j in range(0, 288):
#             color = pixels[i, j]
#             _r, _g, _b, alpha = color
#             if is_half_transparent(alpha):
#                 pixels[i, j] = PINK
#             elif not is_transparent(alpha):
#                 pixels[i, j] = BLACK
#             else:
#                 pixels[i, j] = WHITE


# def is_half_transparent(alpha):
#     return alpha != 0 and alpha != 255


# def is_transparent(alpha):
#     return alpha == 0



if __name__ == '__main__':
    unittest.main()
