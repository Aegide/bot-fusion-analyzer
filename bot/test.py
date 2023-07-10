from collections import OrderedDict
import os
from typing import Any
import unittest

from PIL.ImagePalette import ImagePalette
from PIL.Image import Image, open, new
from PIL.PyAccess import PyAccess
from numpy import array
from utils import get_fusion_id_from_filename as gfiff
from math import sqrt


# Fuck colormath
import numpy
def patch_asscalar(a):
    return a.item()
setattr(numpy, "asscalar", patch_asscalar)


from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000, delta_e_cmc


UPPER_COLOR_LIMIT = 1000
DELTA_COLOR_LIMIT = 10

PINK = (255, 0, 255, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)

MAX_TRANSPARENCY = 0
MIN_TRANSPARENCY = 255
STEP = 3
MAX_SIZE = 288

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


# class TestTransparencyAmount(unittest.TestCase):
#     def test_colour_amount(self):
#         sprites = os.listdir("fixtures")
#         for sprite in sprites:
#             sprite_path = os.path.join("fixtures", sprite)
#             with open(sprite_path) as image:
#                 palette = get_palette(image)
#                 pixels = get_pixels(image)
#                 update_transparency(pixels, image.mode, palette)
#                 # image.show()


# def get_pixels(image:Image) -> PyAccess:
#     return image.load()  # type: ignore


# def update_transparency(pixels:PyAccess, image_mode:str, palette:ImagePalette|None):
#     if image_mode == RGBA_MODE:
#         update_rgba(pixels)
#     elif image_mode == PALETTE_MODE:
#         update_palette(pixels, palette)  # type: ignore
#     elif image_mode == RGB_MODE:
#         pass
#     else:
#         raise RuntimeError(image_mode)


# def is_half_transparent(alpha):
#     return alpha != 0 and alpha != 255


# def is_transparent(alpha):
#     return alpha == 0


# def get_palette(image:Image) -> ImagePalette:
#     return image.palette


# def update_rgba(pixels:PyAccess):
#     for i in range(0, 288):
#         for j in range(0, 288):
#             _r, _g, _b, alpha = pixels[i, j]
#             if is_half_transparent(alpha):
#                 pixels[i, j] = PINK
#             elif not is_transparent(alpha):
#                 pixels[i, j] = BLACK
#             else:
#                 pixels[i, j] = WHITE


# def update_palette(pixels:PyAccess, palette:ImagePalette):
#     color_set = set()
#     inverse_palette = {v: k for k, v in palette.colors.items()}
#     for i in range(0, 288):
#         for j in range(0, 288):
#             palette_index = pixels[i, j]
#             pixel_color = inverse_palette.get(palette_index)
#             if pixel_color not in color_set:
#                 color_set.add(pixel_color)
#                 # print(palette_index, (i, j), pixel_color)


# class TestHalfPixels(unittest.TestCase):
#     def test_half_pixels(self):
#         sprites = os.listdir("fixtures")
#         for sprite in sprites:
#             sprite_path = os.path.join("fixtures", sprite)
#             with open(sprite_path) as image:
#                 print(sprite, image.mode)
#                 pixels = get_pixels(image)
#                 update_half_pixels(pixels)
#                 # image.show()


# def find_first_pixel(pixels:PyAccess):
#     default_value = pixels[0, 0]
#     for i in range(0, 288):
#         for j in range(0, 288):
#             if default_value != pixels[i, j]:
#                 return (i%3, j%3)
#     return (0, 0)


# def update_half_pixels(pixels:PyAccess):

#     exposed_image = new(RGBA_MODE, (MAX_SIZE, MAX_SIZE))
#     exposed_pixels = get_pixels(exposed_image)

#     (delta_i, delta_j) = find_first_pixel(pixels)

#     print((delta_i, delta_j), pixels[delta_i, delta_j])
#     print(" ")

#     issue_counter = 0

#     max_i = MAX_SIZE - (STEP - delta_i)
#     max_j = MAX_SIZE - (STEP - delta_j)
#     for i in range(delta_i, max_i, STEP):
#         for j in range(delta_j, max_j, STEP):
    
#             color_set = get_color_set(i, j, pixels)
#             color = get_color_from_set(color_set)
#             recolor_pixels(i, j, exposed_pixels, color)
                    
#             if color == RED:
#                 print((i, j), color_set)
#                 issue_counter += 1

#     if issue_counter > 0:
#         exposed_image.show()


# def get_color_from_set(color_set:set):
#     if len(color_set) > 1:
#         return RED
#     return GREEN


# def get_color_set(i:int, j:int, pixels:PyAccess):
#     color_set = set()
#     for increment_i in range(0, STEP):
#         for increment_j in range(0, STEP):
#             local_i = i + increment_i
#             local_j = j + increment_j
#             color_set.add(pixels[local_i, local_j])
#     return color_set


# def recolor_pixels(i:int, j:int, pixels:PyAccess, color:tuple):
#     for increment_i in range(0, STEP):
#         for increment_j in range(0, STEP):
#             local_i = i + increment_i
#             local_j = j + increment_j
#             pixels[local_i, local_j] = color


def get_colors(image:Image, color_limit:int) -> list[tuple[int, tuple[int]]]:
    return image.getcolors(color_limit) # type: ignore


def factor(rgb_256:tuple[int, int, int]):
    red = rgb_256[0] / 255.0
    green= rgb_256[0] / 255.0
    blue = rgb_256[0] / 255.0
    return array([red, green, blue])


def get_color_distance(rgb_a:tuple, rgb_b:tuple):
    red = (rgb_a[0] - rgb_b[0])**2
    green = (rgb_a[1] - rgb_b[1])**2
    blue = (rgb_a[1] - rgb_b[2])**2
    return sqrt(red + green + blue)


def get_color_delta(rgb_a:tuple, rgb_b:tuple):
    color_rgb_a = sRGBColor(rgb_a[0], rgb_a[1], rgb_a[2], True)
    color_rgb_b = sRGBColor(rgb_b[0], rgb_b[1], rgb_b[2], True)
    color_lab_a = convert_color(color_rgb_a, LabColor)
    color_lab_b = convert_color(color_rgb_b, LabColor)
    cie2000 = delta_e_cie2000(color_lab_a, color_lab_b)
    cmc = delta_e_cmc(color_lab_a, color_lab_b)
    combination = cie2000 * cmc
    return [int(cie2000), int(cmc), int(combination)]


def get_rgb_color_list(image:Image) -> list[tuple[int, int, int]]:
    rgb_color_list = []
    color_data_list = get_colors(image, UPPER_COLOR_LIMIT)
    for color_data in color_data_list:
        rgb_color = color_data[1][0:3]
        rgb_color_list.append(rgb_color)
    return rgb_color_list


def get_color_dict(rgb_color_list:list):
    color_dict = {}
    for color_a in rgb_color_list:
        for color_b in rgb_color_list:
            if color_a == color_b:
                continue
            color_delta = get_color_delta(color_a, color_b)
            condition = color_delta[0] < DELTA_COLOR_LIMIT and color_delta[1] < DELTA_COLOR_LIMIT
            if condition:
                frozen_set = frozenset([color_a, color_b])
                color_dict[frozen_set] = color_delta
    return color_dict


def print_color_dict(color_dict:dict):
    for key, value in color_dict.items():
        color:list = list(key)
        deltas = f"({value[0]}, {value[1]}) : {value[2]}"
        print(deltas, color)


def sort_color_dict(some_dict:dict):
    return {k: v for k, v in sorted(some_dict.items(), key=sort_element)}


def sort_element(x):
    return x[1][2]


class TestVisualDiversity(unittest.TestCase):
    def test_visual_diversity(self):
        sprites = os.listdir("fixtures")
        for sprite in sprites:
            sprite_path = os.path.join("fixtures", sprite)
            with open(sprite_path) as image:
                print(sprite)
                rgb_color_list = get_rgb_color_list(image)
                color_dict = get_color_dict(rgb_color_list)
                color_dict = sort_color_dict(color_dict)
                print_color_dict(color_dict)
                print("\n")


if __name__ == '__main__':
    unittest.main()
