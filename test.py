import glob
import itertools as it
import os

from PIL import Image, ImageOps, ImageStat
from PIL.ImageDraw import ImageDraw

RATIO_BASE_WIDTH = 16
RATIO_BASE_HEIGHT = 9

HD_WIDTH = RATIO_BASE_WIDTH * 128
HD_HEIGHT = RATIO_BASE_HEIGHT * 128

tiles = dict()

def load_images():
    for filename in glob.glob("cropped/*.jpg"):
        with Image.open(filename) as image:
            cropped = ImageOps.fit(image, (HD_WIDTH // 4, HD_HEIGHT // 4))
            stats = ImageStat.Stat(cropped)
            tiles[tuple(stats.median)] = cropped

def find_closest_color(color, excluded):
    available = set(tiles.keys())
    available.difference_update(set(excluded))
    return min(available, key=lambda c: (color[0] - c[0]) ** 2 + (color[1] - c[1]) ** 2 + (color[2] - c[2]) ** 2)

def quadtree(drawing, x, y, size = 128, excluded = None):
    if excluded is None:
        excluded = list()

    width = size * RATIO_BASE_WIDTH
    height = size * RATIO_BASE_HEIGHT

    cropped = drawing.crop((x, y, x + width, y + height))
    stats = ImageStat.Stat(cropped)

    if max(stats.stddev) < 32 or size <= 1:
        color = find_closest_color(stats.median, excluded)
        tile = tiles[color]
        excluded.append(color)
        scaled = ImageOps.scale(tile, height / tile.height)
        drawing.paste(scaled, (x, y))

        if len(excluded) > 10:
            excluded.pop(0)
        return

    w = width // 2
    h = height // 2
    for i, j in it.product(range(2), range(2)):
        quadtree(drawing, x + i * w, y + j * h, size // 2, excluded)

def process_image(image_path):
    image = Image.open(image_path)

    cropped_image = ImageOps.fit(image, (HD_WIDTH, HD_HEIGHT))
    cropped_image = ImageOps.scale(cropped_image, 15 / 120)
    cropped_image = ImageOps.scale(cropped_image, 120 / 15)

    quadtree(cropped_image, 0, 0)
    cropped_image.show(title="BTree Image")


if __name__ == '__main__':
    load_images()
    process_image("images/turtle/reference.jpg")
