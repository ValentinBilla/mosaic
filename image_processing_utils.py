import glob
import os
import sqlite3

import numpy as np
import tqdm
from matplotlib import pyplot as plt

import skimage
from sklearn.metrics import pairwise_distances_argmin

GRID_SIZE = 30
TILE_SIZE = 64

def generate_url_list_from_db(theme: str):
    db_path = 'images.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    rs = cursor.execute(f"SELECT url FROM image_data WHERE theme LIKE '{theme}' ORDER BY url")
    conn.commit()

    with open("downloads/urls.txt", "w") as f:
        f.writelines(url + '\n' for url, in rs.fetchall())

    conn.close()

def rename_files_from_db(theme: str):
    db_path = 'images.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    rs = cursor.execute(f"SELECT url FROM image_data WHERE theme LIKE '{theme}' ORDER BY url")
    mapping = {url: i for i, (url,) in enumerate(rs.fetchall())}

    for url in mapping.keys():
        filename = url.split('/')[-1]
        os.rename(os.path.join('downloads', filename), 'downloads/' + str(mapping[url]) + '.jpg')


def get_colors_from_db(theme: str) -> np.ndarray:
    db_path = 'images.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    rs = cursor.execute(f"SELECT avg_color FROM image_data WHERE theme LIKE '{theme}' ORDER BY url")
    conn.commit()

    colors = [tuple(int(h[1:][i:i+2], 16) for i in (0, 2, 4)) for h, in rs.fetchall()]
    conn.close()

    return np.array(colors)

def get_reference_image(name: str):
    pattern = os.path.join(f'images/{name}', 'reference.*')
    # We assume only one image matches the description.
    image_path = glob.glob(pattern).pop()
    image = skimage.io.imread(image_path)

    padding_x = image.shape[0] % GRID_SIZE
    padding_y = image.shape[1] % GRID_SIZE

    return image[
            padding_x // 2 : image.shape[0] - padding_x // 2,
            padding_y // 2 : image.shape[1] - padding_y // 2,
            :
    ]


def get_labeled_image(id: int):
    image_path = os.path.join('cropped', f'{id}.jpg')
    image = skimage.io.imread(image_path)

    # Center crop to square
    min_dim = min(image.shape[:2])
    start_x = (image.shape[0] - min_dim) // 2
    start_y = (image.shape[1] - min_dim) // 2
    cropped_image = image[start_x:start_x + min_dim, start_y:start_y + min_dim]

    # Resize to TILE_SIZE x TILE_SIZE
    return skimage.transform.resize(cropped_image, (TILE_SIZE, TILE_SIZE), anti_aliasing=True)

def generate_quantized_image(name: str, palette: np.ndarray):
    image = get_reference_image(name)
    scaled_image = skimage.transform.rescale(image, 1 / GRID_SIZE, channel_axis=2)

    w, h = scaled_image.shape[:2]
    scaled_image_array = np.resize(scaled_image, (w * h, 3))
    palette_array = np.array(palette, dtype=np.float32) / 255

    image_labels = pairwise_distances_argmin(palette_array, scaled_image_array, axis=0)
    quantized_image = palette_array[image_labels].reshape(w, h, -1)

    # Display all results, alongside original image
    plt.figure(1)
    plt.clf()
    plt.axis("off")
    plt.title("Original image (96,615 colors)")
    plt.imshow(image)

    plt.figure(2)
    plt.clf()
    plt.axis("off")
    plt.title(f"Quantized image ({palette.shape[0]} colors, Random)")
    plt.imshow(quantized_image)
    plt.show()

    canvas = np.zeros((w * TILE_SIZE, h * TILE_SIZE, 3), dtype=np.float32)

    progress = tqdm.tqdm(total=w * h)
    image_labels = np.resize(image_labels, (w, h))
    for label in range(len(palette)):
        matches = np.where(image_labels == label)
        if len(matches[0]) == 0:
            continue

        tile_image = get_labeled_image(label)
        for i, j in zip(matches[0], matches[1]):
            progress.update(1)

            canvas[i * TILE_SIZE:(i + 1) * TILE_SIZE, j * TILE_SIZE:(j + 1) * TILE_SIZE] = tile_image

    # Display the final canvas
    plt.figure(3)
    plt.clf()
    plt.axis("off")
    plt.title(f"Canvas image with tiled images")
    plt.imshow(canvas)

    big = skimage.transform.rescale(canvas, GRID_SIZE / TILE_SIZE, channel_axis=2)
    test = skimage.util.compare_images(big, image)
    plt.figure(4)
    plt.clf()
    plt.axis("off")
    plt.title(f"Difference between quantized and tiled")
    plt.imshow(test)
    plt.show()

    skimage.io.imsave('turtle.png', (canvas * 255).astype(np.uint8))


def main():
    random = get_colors_from_db('Ocean')
    generate_quantized_image('turtle', random)

if __name__ == '__main__':
    main()
