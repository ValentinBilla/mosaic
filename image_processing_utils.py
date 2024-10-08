import math
import os
import random as rd

import numpy as np
from scipy.optimize import linear_sum_assignment

from PIL import Image
from PIL.ImageDraw import ImageDraw

SUB_WIDTH = 40
SUB_HEIGHT = 40

def crop_image_to_nearest_sub_multiple():

def rescale_image_to_tile_grid(image):

    width_tiles, height_tiles = grid_size, grid_size
    tile_width, tile_height = tile_aspect_ratio

    # Calculate the final size of the rescaled image
    final_width = width_tiles * tile_width
    final_height = height_tiles * tile_height


    rescaled_img = image.resize((final_width, final_height))
    output_img = Image.new("RGB", (final_width, final_height))

    draw = ImageDraw(output_img)

    for i in range(height_tiles):
        for j in range(width_tiles):
            tile_x = j * tile_width
            tile_y = i * tile_height

            # Calculate the average color of the tile
            tile = rescaled_img.crop((tile_x, tile_y, tile_x + tile_width, tile_y + tile_height))
            avg_color = tile.resize((1, 1), resample=Image.Resampling.BILINEAR).getpixel((0, 0))

            # Fill the tile area with the average color
            draw.rectangle([tile_x, tile_y, tile_x + tile_width, tile_y + tile_height], fill=avg_color)

    return output_img


def sample_colors_from_grid(image, grid_size, tile_size=(16, 9)):
    width_tiles, height_tiles = grid_size, grid_size
    tile_width, tile_height = tile_size
    colors = []

    for i in range(height_tiles):
        for j in range(width_tiles):
            tile_x = j * tile_width
            tile_y = i * tile_height
            colors.append(image.getpixel((tile_x, tile_y)))

    return colors


def random_colors_from_grid(image, grid_size):

    image = image.convert("RGB")
    colors = list()

    for i in range(grid_size * grid_size):
        random_x = rd.randint(0, image.width - 1)
        random_y = rd.randint(0, image.height - 1)
        colors.append(image.getpixel((random_x, random_y)))

    return colors


def create_flat_color_image(colors, tile_size=(16, 9)):
    grid_size = int(math.sqrt(len(colors)))
    width_tiles = grid_size
    height_tiles = grid_size
    tile_width, tile_height = tile_size

    # Calculate the final size of the flat color image.
    final_width = width_tiles * tile_width
    final_height = height_tiles * tile_height

    flat_color_image = Image.new("RGB", (final_width, final_height))
    draw = ImageDraw(flat_color_image)

    for i, color in enumerate(colors):
        tile_x = i % width_tiles * tile_width
        tile_y = i // width_tiles * tile_height
        draw.rectangle([tile_x, tile_y, tile_x + tile_width, tile_y + tile_height], fill=color)

    return flat_color_image

def color_difference(c1, c2):
    return np.linalg.norm(np.array(c1) - np.array(c2))

def rearrange_colors(random_colors, sampled_colors):
    cost_matrix = np.zeros((len(random_colors), len(sampled_colors)))

    for i, rc in enumerate(random_colors):
        for j, sc in enumerate(sampled_colors):
            diff = color_difference(rc, sc)
            cost_matrix[i, j] = diff

    # Apply the Hungarian algorithm to minimize the total cost
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    ids = [(r, c) for r, c in zip(row_ind, col_ind)]
    ids.sort(key=lambda x: x[1])
    # Rearrange random_colors based on the optimal assignment
    rearranged_random_colors = [random_colors[r] for r, c in ids]

    return rearranged_random_colors


def calculate_mean_color(image):
    np_image = np.array(image)
    mean_color = tuple(np.mean(np_image, axis=(0, 1)).astype(int))
    return mean_color

def process_images(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        input_image_path = os.path.join(input_directory, filename)
        with Image.open(input_image_path) as img:
            mean_color = calculate_mean_color(img)
            mean_color_str = "_".join(map(str, mean_color[:3]))
            output_filename = f"kiss_mean{mean_color_str}.png"
            output_image_path = os.path.join(output_directory, output_filename)
            img.save(output_image_path, 'PNG')
            print(f"Processed and saved: {output_image_path}")

def random_colors_from_scrapped(input_directory):
    colors = list()

    for filename in os.listdir(input_directory):
        mean = filename.removeprefix("kiss_mean").removesuffix(".png")
        color = mean.split("_")
        colors.append(tuple(map(int, color)))

    return colors

def main():


    input_directory = "./images"
    output_directory = "./processed"

    # process_images(input_directory, output_directory)

    with Image.open('kiss.png') as img:

        grid_size = 20

        rescaled_image = rescale_image_to_tile_grid(img, grid_size=grid_size, tile_aspect_ratio=(16, 9))
        sampled_colors = sample_colors_from_grid(rescaled_image, grid_size=grid_size)

        # random_colors = random_colors_from_grid(img, grid_size=grid_size)
        random_colors = random_colors_from_scrapped(output_directory)
        rearranged_colors = rearrange_colors(random_colors, sampled_colors)
        create_flat_color_image(rearranged_colors).show()


if __name__ == '__main__':
    main()