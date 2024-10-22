#!/usr/bin/env python3
import requests
import sqlite3
import os


def scrape_image_urls(url):
    api_key = os.getenv('PEXELS_API_KEY')
    params = {
        # 'query': 'flowers',
        'query': 'Ocean',
        # 'color': '#3f53eb',
        # 'orientation': 'landscape',
        'per_page': 10,
        'page': 7
    }

    headers = {
        'Authorization': f'{api_key}'
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # images = BeautifulSoup(response.content, 'html.parser').find_all("photos")
        images=data["photos"]
        theme=params["query"]
        if images :
            images_data=[]
            for image in images:
                image_url = image["src"]["original"]
                color = image["avg_color"]
                images_data.append((image_url, color, theme))

            print(images_data)
            return images_data
        
    else:
        print(f"Erreur : {response.status_code}")

def save_to_database(images_data):
    db_path = 'images.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS image_data
                      (url TEXT PRIMARY KEY, avg_color TEXT, theme TEXT)''')

    for url, color, theme in images_data:
        cursor.execute("INSERT OR IGNORE INTO image_data (url, avg_color, theme) VALUES (?, ?, ?)", (url, color, theme))

    conn.commit()
    conn.close()

def main():
    target_url = 'https://api.pexels.com/v1/search'
    image_urls = scrape_image_urls(target_url)
    save_to_database(image_urls)
    
    print(f"Scrapé {len(image_urls)} URLs d'images")
    print(f"URLs sauvegardées dans {os.path.abspath('images.db')}")

if __name__ == "__main__":
    main()