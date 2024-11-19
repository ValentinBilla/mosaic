import os
import random
from re import match
from typing import Literal

import numpy as np
from PIL import Image

from colour.plotting import *

ORIGINAL_FOLDER = 'downloads'
CROPPED_FOLDER = 'cropped'

BASE_SIZE = 1080

def crop_image(
        image: Image,
        horizontal_alignment: Literal['r', 'c', 'l'] = 'center',
        vertical_alignment: Literal['t', 'c', 'b'] = 'center'
        ) -> Image:
    image_width, image_height = image.size

    if horizontal_alignment == 'r':
        left = image_width - BASE_SIZE
        right = image_width
    elif horizontal_alignment == 'l':
        left = 0
        right = BASE_SIZE
    else:
        left = (image_width - BASE_SIZE) / 2
        right = (image_width + BASE_SIZE) / 2

    if vertical_alignment == 't':
        top = 0
        bottom = BASE_SIZE
    elif vertical_alignment == 'b':
        top = image_height - BASE_SIZE
        bottom = image_height
    else:
        top = (image_height - BASE_SIZE) / 2
        bottom = (image_height + BASE_SIZE) / 2

    cropped_img = image.crop((left, top, right, bottom))
    return cropped_img


def crop_images():
    goal = BASE_SIZE

    for filename in os.listdir(ORIGINAL_FOLDER):
        if filename.startswith('done.'):
           continue
        if not filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            continue

        image_path = os.path.join(ORIGINAL_FOLDER, filename)
        with Image.open(image_path) as img:
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height

            if img_width > img_height:
                new_height = goal
                new_width = int(goal * aspect_ratio)
            else:
                new_width = goal
                new_height = int(goal / aspect_ratio)

            new_img = img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)

            print(f'Resized {filename} to {new_width}x{new_height}')
            new_img.show()


            while True:
                align = input('> ').lower()
                horizontal_align, vertical_align = align[1], align[0]
                
                if horizontal_align not in ('r', 'c', 'l'):
                    print('# wrong horizontal alignment parameter')
                    continue

                if vertical_align not in ('t', 'c', 'b'):
                    print('# wrong vertical alignment parameter')
                    continue

                break

            # noinspection PyTypeChecker
            new_img = crop_image(new_img, 'c', 'c')
            new_img.save(os.path.join(CROPPED_FOLDER, filename))

            os.rename(
                os.path.join(ORIGINAL_FOLDER, filename),
                os.path.join(ORIGINAL_FOLDER, f'done.{filename}')
            )
            print(f'Saved {filename}\n')

def total_squared_distance(color, image):
    diff = image - color
    squared_distance = np.sum(diff ** 2, axis=(0, 1))
    return np.sum(squared_distance)

def get_average_color(img: Image):
    np_img = np.array(img)
    mean_color = np.mean(np_img, axis=(0, 1))

    return tuple(mean_color.astype(int))

def get_unsplash_colors():
    colors = []

    for filename in os.listdir(CROPPED_FOLDER):
        if match('^[0-9a-f]{6}\\.', filename):
            hex = filename.split('.')[0]
            colors.append(tuple(int(hex, 16) >> bitshift & 255 for bitshift in (16, 8, 0)))
            continue
        if not filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            continue

        image_path = os.path.join(CROPPED_FOLDER, filename)
        with Image.open(image_path) as img:
            mean_color = get_average_color(img)

        r, g, b = mean_color
        colors.append((int(r), int(g), int(b)))
        hex = f'{r:02x}{g:02x}{b:02x}'

        os.rename(
            os.path.join(CROPPED_FOLDER, filename),
            os.path.join(CROPPED_FOLDER, f'{hex}.{filename}')
        )

    return colors


def create_patchwork(crop: bool = False, shuffle: bool = False, checkered: bool = False):
    filenames = os.listdir(CROPPED_FOLDER)
    random.shuffle(filenames)

    tile = 135
    size = 14

    positions = list(range(len(filenames)))
    if shuffle:
        random.shuffle(positions)

    canvas = Image.new('RGB', (tile * size, tile * size))

    for i, filename in enumerate(filenames):
        if not filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            continue

        image_path = os.path.join(CROPPED_FOLDER, filename)
        with Image.open(image_path) as img:
            scaled = img.resize((tile, tile), resample=Image.Resampling.LANCZOS)

        j, k = (i // size * 2 + (i % 2 if checkered else 0)) % size, i % size
        canvas.paste(scaled, (j * tile, k * tile))

        p = positions[i]
        j, k = (p // size * 2 + 1 + (p % 2 if checkered else 0)) % size, p % size
        mean_color = get_average_color(img)
        mean_color_image = Image.new('RGB', (tile, tile), mean_color)
        canvas.paste(mean_color_image, (j * tile, k * tile))

    if crop:
        canvas = canvas.crop((tile*size*.25, tile*size*.25, tile*size*.75, tile*size*.75))
    canvas.show()

if __name__ == '__main__':
    crop_images()
    create_patchwork()

    colors = get_unsplash_colors()
    plot_RGB_chromaticities_in_chromaticity_diagram_CIE1931(colors)
