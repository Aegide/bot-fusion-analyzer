from os.path import join
from os import sep as os_sep
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import traceback
from PIL import Image
from PIL import PyAccess
from PIL.PngImagePlugin import PngImageFile
import requests
from description import Description


BLACK_TRANSPARENCY = (0, 0, 0, 0)
WHITE_TRANSPARENCY = (255, 255, 255, 0)
PINK = (255, 0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

UPPER_COLOR_LIMIT = 1000
COLOR_LIMIT = 100
HALF_TRANSPARENCY_LIMIT = 1000

path_custom = "CustomBattlers"
path_debug = "debug"
path_result = "CustomBattlersVisible"
bad_fusions = []


main_path = path_custom


TEST_SIZE = False
TEST_PALETTE = False
TEST_HIGH_DIVERSITY = False
TEST_MASSIVE_DIVERSITY = False

TEST_TRANSPARENCY = True

VERBOSE_MODE = False


def is_valid_size(image):
    return image.size == (288,288)

def show_sprite(element):
    
    image = mpimg.imread(join(main_path, element))

    print("show_sprite", type(image))

    fig, ax = plt.subplots(figsize=(4, 4))
    imgplot = plt.imshow(image)
    plt.show()

def apply_borders(pixels):
    for i in range(0, 288): 
            pixels[i, 0] = PINK
            pixels[i, 287] = PINK
            pixels[0, i] = PINK
            pixels[287, i] = PINK

def have_normal_transparency(pixels, i, j):
    if isinstance(pixels[i, j], tuple) and len(pixels[i, j]) == 4:
        return pixels[i, j][3] == 0
    else:
        return True

def have_weird_transparency(pixels, i, j):
    if isinstance(pixels[i, j], tuple) and len(pixels[i, j]) == 4:
        return pixels[i, j][3] != 0 and pixels[i, j][3] != 255
    else:
        return False

def is_not_transparent(pixels, i, j):
    return pixels[i, j][3] != 0

def detect_half_transparency(pixels):
    half_transparent_pixels = 0
    if isinstance(pixels[0, 0], tuple) and len(pixels[0, 0]) == 4:
        for i in range(0, 288):
            for j in range(0, 288):

                # Weird pixels : PINK
                if have_weird_transparency(pixels, i, j):
                    # print(i, j, pixels[i, j])
                    pixels[i, j] = PINK
                    half_transparent_pixels += 1

                # Background : WHITE
                elif have_normal_transparency(pixels, i, j):
                    pixels[i, j] = WHITE

                # Actual sprite : BLACK
                else:
                    pixels[i, j] = BLACK
    return half_transparent_pixels

def find_one_pixel(pixels):
    one_pixel = None
    should_break = False
    size = 50

    for i in range(0, size):
        for j in range(0, size):
            if is_not_transparent(pixels, i, j):
                print(i, j, pixels[i, j])
                pixels[i, j] = PINK
                one_pixel = i, j
                should_break = True
                break
        if should_break:
            break
    return one_pixel

def is_using_palette(pixels):
    return isinstance(pixels[0,0], int)

def is_missing_colors(image):
    return image.getcolors(UPPER_COLOR_LIMIT) is None

def get_non_transparent_colors(image):
    old_colors = image.getcolors(UPPER_COLOR_LIMIT)
    new_colors = []

    # TODO : be careful of RGB-A with 3 channels
    if old_colors is not None and isinstance(old_colors[0][1], tuple) and len(old_colors[0][1]) == 4:
        for old_color in old_colors:
            if old_color[1][3]==255:
                new_colors.append(old_color)

    return new_colors

def is_overusing_colors(image):
    colors = get_non_transparent_colors(image)
    if colors is None:
        result = True
    else: 
        color_amount = len(colors)
        result = color_amount > COLOR_LIMIT
    return result

def test_colors(image):
    return_value = 0
    if TEST_MASSIVE_DIVERSITY:
        try:
            if is_missing_colors(image):
                print("[MASSIVE COLOR DIVERSITY]")
                return_value = 1
        except Exception as e:
            print("test_colors", e)
            return_value = 100
    return return_value

def test_palette(pixels):
    return_value = 0
    if TEST_PALETTE:
        try:
            if is_using_palette(pixels):
                print("[COLOR PALETTE USAGE]")
                return_value = 1
        except Exception as e:
            print("test_palette", e)
            return_value = 100
    return return_value

class sprite_analysis():

    warning = ""
    valid_fusion = True
    file_name = None

    def __init__(self, image: PngImageFile, pixels: PyAccess, url: str):
        self.image = image
        self.pixels = pixels
        self.file_name = url.split("/")[-1]

    def test_size(self):
        try:
            if not is_valid_size(self.image):
                self.warning += f"{self.image.size} is an invalid size" + "\n"
                self.valid_fusion = False
        except Exception as e:
            print("test_size()", e)
            print(traceback.format_exc())

    def test_color_diversity(self):
        try:
            if is_overusing_colors(self.image):
                color_list = get_non_transparent_colors(self.image)
                if color_list is None:
                    self.warning += f"Using +{UPPER_COLOR_LIMIT} colors is weird" + "\n"
                    self.valid_fusion = False
                else:
                    color_amount = len(color_list)
                    self.warning += f"Using {color_amount} colors is not recommended" + "\n"
        except Exception as e:
            print("test_color_diversity()", e)
            print(traceback.format_exc())

    def test_half_transparency(self):
        try:
            half_transparent_pixels = detect_half_transparency(self.pixels)
            if half_transparent_pixels > HALF_TRANSPARENCY_LIMIT:
                self.warning += f"Contains {half_transparent_pixels} half-transparent pixels" + "\n"
                self.valid_fusion = False
                self.image.save(f"tmp{os_sep}{self.file_name}")
        except Exception as e:
            print("test_half_transparency()", e)
            if str(e) != "image index out of range":
                print(traceback.format_exc())
                
    def handle_results(self):
        description = None
        if len(self.warning) > 0:
            if self.valid_fusion :
                description = str(Description.sprite_issue.value)
            else:
                description = str(Description.sprite_error.value)
        return self.valid_fusion, description, self.warning, self.file_name

def get_data(url):
    image = Image.open(requests.get(url, stream=True).raw)
    pixels = image.load()
    analysis = sprite_analysis(image, pixels, url)
    return analysis

def test_sprite(url):
    analysis = get_data(url)
    analysis.test_size()
    analysis.test_color_diversity()
    analysis.test_half_transparency()
    results = analysis.handle_results()
    # image.show()
    return results
    
if __name__ == "__main__":
    url = "https://cdn.discordapp.com/attachments/858107956326826004/925366536292687872/209.246.png"
    test_sprite(url)
