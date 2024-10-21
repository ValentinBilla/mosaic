#!/usr/bin/env python3
import requests
import sqlite3
import os


def scrape_image_urls(url):
    api_key = os.getenv('PEXELS_API_KEY')
    params = {
        'query': 'flowers',
        'orientation': 'landscape',
        'per_page': 20,
        'page': 1
    }

    headers = {
        'Authorization': f'{api_key}'
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # images = BeautifulSoup(response.content, 'html.parser').find_all("photos")
        images=data["photos"]
        if images :
            image_urls = [image["src"]["original"] for image in images]
            return image_urls
        
    else:
        print(f"Erreur : {response.status_code}")

def save_to_database(image_urls):
    db_path = 'images.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS image_urls
                      (url TEXT PRIMARY KEY)''')
    
    for url in image_urls:
        cursor.execute("INSERT OR IGNORE INTO image_urls (url) VALUES (?)", (url,))
    
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