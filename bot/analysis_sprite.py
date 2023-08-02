import requests
from analysis import Analysis
from enums import Severity
from exceptions import TransparencyException
from issues import (AsepriteUser, ColorAmount, ColorExcessControversial,
                    ColorExcessRefused, ColorOverExcess, GraphicsGaleUser,
                    HalfPixelsAmount, InvalidSize, MissingTransparency,
                    SimilarityAmount, TransparencyAmount)


# Pillow
from PIL.Image import open as image_open
from PIL.Image import Image, new
from PIL.PyAccess import PyAccess


# Fuck colormath
import numpy
def patch_asscalar(a):
    return a.item()
setattr(numpy, "asscalar", patch_asscalar)


from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000, delta_e_cmc


colorType = int|tuple


MAX_SIZE = 288
VALID_SIZE = (MAX_SIZE, MAX_SIZE)


ALL_COLOR_LIMIT = 256
REFUSED_COLOR_LIMIT = 64
CONTROVERSIAL_COLOR_LIMIT = 32
DIFFERENCE_COLOR_LIMIT = 32
DELTA_COLOR_LIMIT = 10


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

        raw_data = requests.get(analysis.attachment_url, stream=True, timeout=1).raw
        self.image = image_open(raw_data)
        self.pixels = get_pixels(self.image)

        self.useful_amount: int = 0
        self.useless_amount: int = 0

        self.useful_colors: list = []
        self.similar_color_dict: dict = {}

    def handle_sprite_size(self, analysis:Analysis):
        size = self.image.size
        if size != VALID_SIZE:
            analysis.size_issue = True
            analysis.severity = Severity.refused
            analysis.issues.add(InvalidSize(size))

    def handle_sprite_colors(self, analysis:Analysis):
        all_colors = self.image.getcolors(ALL_COLOR_LIMIT)
        if is_color_excess(all_colors):
            analysis.severity = Severity.refused
            analysis.issues.add(ColorOverExcess(ALL_COLOR_LIMIT))
        else:
            self.handle_color_count(analysis, all_colors)
            self.handle_color_limit(analysis)
            self.handle_color_similarity(analysis)
            self.handle_aseprite(analysis)
            self.handle_graphics_gale(analysis)

    def handle_color_count(self, analysis:Analysis, all_colors:list):
        try:
            self.useful_colors = remove_useless_colors(all_colors)
            self.handle_color_amount(analysis, all_colors)
        except TransparencyException:
            analysis.severity = Severity.refused
            analysis.issues.add(MissingTransparency())

    def handle_color_amount(self, analysis:Analysis, all_colors):
        all_amount = len(all_colors)
        self.useful_amount = len(self.useful_colors)
        self.useless_amount = all_amount - self.useful_amount
        analysis.issues.add(ColorAmount(self.useful_amount))

    def handle_color_similarity(self, analysis:Analysis):
        similarity_amount = self.get_similarity_amount()
        analysis.issues.add(SimilarityAmount(similarity_amount))
        # if similarity_amount > 1:
            # if analysis.severity is not Severity.refused:
                # analysis.severity = Severity.controversial

    def handle_color_limit(self, analysis:Analysis):
        if self.useful_amount > REFUSED_COLOR_LIMIT:
            analysis.issues.add(ColorExcessRefused(REFUSED_COLOR_LIMIT))
            analysis.severity = Severity.refused
        elif self.useful_amount > CONTROVERSIAL_COLOR_LIMIT:
            analysis.issues.add(ColorExcessControversial(CONTROVERSIAL_COLOR_LIMIT))
            if analysis.severity is not Severity.refused:
                analysis.severity = Severity.controversial

    def handle_aseprite(self, analysis:Analysis):
        if self.useful_amount != 0:
            aseprite_ratio = self.useless_amount / self.useful_amount
            if aseprite_ratio > ASEPRITE_RATIO:
                analysis.issues.add(AsepriteUser(aseprite_ratio))

    def handle_graphics_gale(self, analysis:Analysis):
        is_graphics_gale = "GLDPNG" in self.image.info.get("Software", "")
        if is_graphics_gale:
            analysis.issues.add(GraphicsGaleUser())

    def handle_sprite_transparency(self, analysis:Analysis):
        try:
            if analysis.size_issue is False:
                transparency_amount, image = self.highlight_transparency()
                if transparency_amount > 0:
                    analysis.transparency_issue = True
                    analysis.transparency_image = image
                    if analysis.severity is not Severity.refused:
                        analysis.severity = Severity.controversial
                    analysis.issues.add(TransparencyAmount(transparency_amount))
        except TransparencyException:
            pass

    # FIXME : add support for indexed sprites
    def get_similarity_amount(self):
        similarity_amount = 0
        try:
            rgb_color_list = get_rgb_color_list(self.useful_colors)
            self.similar_color_dict = get_similar_color_dict(rgb_color_list)
            self.similar_color_dict = sort_color_dict(self.similar_color_dict)
            similarity_amount = len(self.similar_color_dict)
        except Exception:
            pass
        return similarity_amount

    def handle_sprite_half_pixels(self, analysis:Analysis):
        if analysis.size_issue is False:
            half_pixels_amount, image = self.highlight_half_pixels()
            if half_pixels_amount > 0:
                analysis.half_pixels_issue = True
                analysis.half_pixels_image = image
                analysis.severity = Severity.refused
                analysis.issues.add(HalfPixelsAmount(half_pixels_amount))

    def highlight_transparency(self) -> tuple[int, Image]:
        """# TransparencyException"""
        local_image = new("RGBA", (MAX_SIZE, MAX_SIZE))
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

    def highlight_half_pixels(self) -> tuple[int, Image]:
        local_image = new("RGBA", (MAX_SIZE, MAX_SIZE))
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
                if color == RED:
                    half_pixels_amount += 9
        return half_pixels_amount, local_image


def get_similar_color_dict(rgb_color_list):
    color_dict = {}
    for color_a in rgb_color_list:
        for color_b in rgb_color_list:
            if color_a == color_b:
                continue
            color_delta = get_color_delta(color_a, color_b)
            if is_similar(color_delta):
                frozen_set = frozenset([color_a, color_b])
                color_dict[frozen_set] = color_delta
    return color_dict


def sort_color_dict(some_dict:dict):
    return {k: v for k, v in sorted(some_dict.items(), key=sort_element)}


def sort_element(x):
    return x[1][2]


def print_color_dict(color_dict:dict):
    for key, value in color_dict.items():
        color:list = list(key)
        deltas = f"({value[0]}, {value[1]}) : {value[2]}"
        print(deltas, color)

def get_rgb_color_list(color_data_list:list) -> list[tuple[int, int, int]]:
    rgb_color_list = []
    for color_data in color_data_list:
        rgb_color = color_data[1][0:3]
        rgb_color_list.append(rgb_color)
    return rgb_color_list


# Maximum number of colors. If this number is exceeded, this method returns None.
def is_color_excess(color_list:list|None):
    return color_list is None


def is_half_transparent(alpha):
    return alpha != 0 and alpha != 255


def is_transparent(alpha:int) -> bool:
    return alpha == 0


def get_pixels(image:Image) -> PyAccess:
    return image.load()  # type: ignore


def remove_useless_colors(old_colors:list):
    """# TransparencyException"""
    new_colors = []
    for old_color in old_colors:
        _color_amount, color_value = old_color
        if not is_useless_color(color_value):
            new_colors.append(old_color)
    return new_colors


def is_useless_color(color:colorType):
    """# TransparencyException"""
    if is_indexed(color):
        return False
    alpha = get_alpha(color) # type: ignore
    return is_transparent(alpha)


def get_alpha(color:tuple) -> int:
    """# TransparencyException"""
    if len(color) != 4:
        raise TransparencyException()
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


def is_similar(color_delta):
    if color_delta[0] > DELTA_COLOR_LIMIT:
        return False
    if color_delta[1] > DELTA_COLOR_LIMIT:
        return False
    if color_delta[2] > DIFFERENCE_COLOR_LIMIT:
        return False
    return True


def get_max_difference(rgb_a:tuple, rgb_b:tuple):
    red_difference = abs(rgb_a[0] - rgb_b[0])
    green_difference = abs(rgb_a[1] - rgb_b[1])
    blue_difference = abs(rgb_a[2] - rgb_b[2])
    return max(red_difference, green_difference, blue_difference)


def get_color_delta(rgb_a:tuple, rgb_b:tuple):
    color_rgb_a = sRGBColor(rgb_a[0], rgb_a[1], rgb_a[2], True)
    color_rgb_b = sRGBColor(rgb_b[0], rgb_b[1], rgb_b[2], True)
    color_lab_a = convert_color(color_rgb_a, LabColor)
    color_lab_b = convert_color(color_rgb_b, LabColor)
    cie2000 = delta_e_cie2000(color_lab_a, color_lab_b)
    cmc = delta_e_cmc(color_lab_a, color_lab_b)
    max_difference = get_max_difference(rgb_a, rgb_b)
    return [int(cie2000), int(cmc), max_difference]


def main(analysis:Analysis, is_reply: bool):

    if is_reply:
        handle_valid_sprite(analysis)
    elif analysis.severity == Severity.accepted:
        handle_valid_sprite(analysis)


def handle_valid_sprite(analysis:Analysis):
    context = SpriteContext(analysis)
    context.handle_sprite_size(analysis)
    context.handle_sprite_colors(analysis)
    context.handle_sprite_transparency(analysis)
    context.handle_sprite_half_pixels(analysis)
