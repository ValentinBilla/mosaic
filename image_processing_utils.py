import itertools as it
import glob
import os

from PIL import Image, ImageEnhance
from PIL.ImageDraw import ImageDraw

import image_search
from image_search import GOOGLE_SEARCH_COLORS

SUB_WIDTH = 150
SUB_HEIGHT = 150

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

    width_tiles = image.width // SUB_WIDTH
    height_tiles = image.height // SUB_HEIGHT

    output_img = Image.new("RGB", (width_tiles, height_tiles))
    draw = ImageDraw(output_img)

    for i in range(height_tiles):
        for j in range(width_tiles):
            tile_x = j * SUB_WIDTH
            tile_y = i * SUB_HEIGHT

            # Calculate the average color of the tile
            tile = image.crop((tile_x, tile_y, tile_x + SUB_WIDTH, tile_y + SUB_HEIGHT))
            avg_color = tile.resize((1, 1), resample=Image.Resampling.BILINEAR).getpixel((0, 0))

            draw.point([j, i], fill=avg_color)

    return output_img


def get_color_stats(image) -> list[int]:

    palette_image = Image.new('P', (1, 1))
    palette_image.putpalette(it.chain.from_iterable(GOOGLE_SEARCH_COLORS.values()))

    image = ImageEnhance.Color(image).enhance(2)
    quantized = image.convert('RGB').quantize(
        palette=palette_image,
        dither=Image.Dither.FLOYDSTEINBERG
    )

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

    img = get_image('autumn')
    scaled = rescale_image_to_tile_grid(img)
    stats = get_color_stats(scaled)

    image_search.scrap_using_stats('forrest fire', stats)

if __name__ == '__main__':
    main()