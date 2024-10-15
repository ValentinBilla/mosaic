import os

from google_images_search import GoogleImagesSearch

developer_key = os.getenv('DEVELOPER_KEY')
custom_search_cx = os.getenv('CUSTOM_SEARCH_CX')

GOOGLE_SEARCH_COLORS = {
    'red': (204, 0, 0),
    'orange': (251, 148, 11),
    'yellow': (255, 255, 0),
    'green': (0, 204, 0),
    'teal': (0, 204, 0),
    'blue': (0, 0, 255),
    'purple': (118, 44, 167),
    'pink': (255, 152, 191),
    'white': (255, 255, 255),
    'gray': (153, 153, 153),
    'black': (0, 0, 0),
    'brown': (136, 84, 24)
}

def scrap_using_stats(theme: str, stats: list[int]):
    color = 'red'
    count = 0
    total = sum(stats)
    urls = {color: set() for color in GOOGLE_SEARCH_COLORS.keys()}

    def my_progressbar(url, progress):
        if url not in urls[color]:
            urls[color].add(url)
        done = sum(map(len, urls.values()))
        total_progress = 100 * done / total

        print(f'{total_progress:.2f}%\t[{len(urls[color]):03}/{count:03}] {color:10} - {progress:.2f}% {url}')

    gis = GoogleImagesSearch(
        developer_key, custom_search_cx,
        progressbar_fn=my_progressbar,
        validate_images=True
    )

    for color, count in zip(GOOGLE_SEARCH_COLORS.keys(), stats):

        _search_params = {
            'q': theme + ' photo',
            'num': count,
            'color': color
        }

        gis.search(
            search_params=_search_params,
            width=150, height=150,
            path_to_dir='images/autumn/scrapped', custom_image_name=color
        )
