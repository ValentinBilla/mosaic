import itertools as it
import glob
import os

from PIL import Image, ImageEnhance
from PIL.ImageDraw import ImageDraw

import image_search
from css_colors import CSS_COLORS
from image_search import GOOGLE_SEARCH_COLORS

SUB_WIDTH = 20
SUB_HEIGHT = 20

def crop_image_to_nearest_sub_multiple(image) -> Image:
    width_delta = image.width % SUB_WIDTH
    start_x = width_delta // 2
    end_x = image.width - width_delta // 2

    height_delta = image.height % SUB_HEIGHT
    start_y = height_delta // 2
    end_y = image.height - height_delta // 2

    return image.crop((start_x, start_y, end_x, end_y))

def rescale_image_to_tile_grid(image):
    image = crop_image_to_nearest_sub_multiple(image)
    image.show()

    width_tiles = image.width // SUB_WIDTH
    height_tiles = image.height // SUB_HEIGHT

    print(width_tiles * height_tiles, 'tiles')

    scaled = image.resize((width_tiles, height_tiles), resample=Image.Resampling.LANCZOS)

    palette_image = Image.new('P', (1, 1))
    palette_image.putpalette(it.chain.from_iterable(CSS_COLORS.values()))

    scaled = ImageEnhance.Color(scaled).enhance(1.5)
    quantized = scaled.convert('RGB').quantize(
        palette=palette_image,
        dither=Image.Dither.NONE
    )

    quantized.resize((image.width, image.height), resample=Image.Resampling.LANCZOS).show()

    return quantized

def get_color_stats(image) -> list[int]:

    palette_image = Image.new('P', (1, 1))
    palette_image.putpalette(it.chain.from_iterable(GOOGLE_SEARCH_COLORS.values()))

    image = ImageEnhance.Color(image).enhance(2)
    quantized = image.convert('RGB').quantize(
        palette=palette_image,
        dither=Image.Dither.FLOYDSTEINBERG
    )
    quantized.show()

    stats = [0] * len(GOOGLE_SEARCH_COLORS)
    for x, y in it.product(range(image.width), range(image.height)):
        # .getpixel returns an integer for quantized images.
        color = quantized.getpixel((x, y))
        # noinspection PyTypeChecker
        stats[color] += 1

    return stats

def get_image(name: str) -> Image:
    pattern = os.path.join(f'images/{name}', 'reference.*')
    # We assume only one image matches the description.
    image_path = glob.glob(pattern).pop()
    return Image.open(image_path)

def main():

    img = get_image('lgbt')
    scaled = rescale_image_to_tile_grid(img)
    # stats = get_color_stats(scaled)

    # image_search.scrap_using_stats('forrest fire', stats)

if __name__ == '__main__':
    main()