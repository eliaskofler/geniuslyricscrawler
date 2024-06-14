import requests
from bs4 import BeautifulSoup
import mysql.connector
import random
import time
from colorama import Fore
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed

# Database connection parameters
db_params = {
    'host': 'obunic.net',
    'user': 'root',
    'password': '!Stiefel(123)',
    'database': 'geniuslyrics'
}

def delay(seconds):
    time.sleep(seconds)

def fetch_url_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def initialize_genius(db_params):
    print(Fore.MAGENTA + "[+] Initializing crawler" + Fore.RESET)
    start_workers(db_params)

def start_workers(db_params, num_workers=20):
    print(Fore.MAGENTA + "[+] Starting workers" + Fore.RESET)
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        urls = get_all_urls_to_fetch(db_params)
        futures = [executor.submit(lyrics_crawling, db_params, url) for url in urls]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Error fetching URL: {exc}")

def get_all_urls_to_fetch(db_params):
    try:
        dbconn = mysql.connector.connect(**db_params)
        cursor = dbconn.cursor()
        cursor.execute('SELECT url FROM song_urls WHERE visited=0')
        rows = cursor.fetchall()
        dbconn.close()
        return [row[0] for row in rows]
    except mysql.connector.Error as error:
        print(f'Error fetching URLs from the database: {error}')
        return []

def lyrics_crawling(db_params, url):
    try:
        dbconn = mysql.connector.connect(**db_params)
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} crawling.. {url}")
        with open('blacklist.txt', 'r') as file:
            blacklist = file.read().split('\n')
        blacklist = [line.strip() for line in blacklist if line.strip()]

        page_content = fetch_url_content(url)
        delay(1)

        soup = BeautifulSoup(page_content, 'html.parser')
        tree = html.fromstring(page_content)

        lyrics = '\n'.join([element.get_text(separator='\n') for element in soup.select('div[data-lyrics-container="true"]')])
        author_element = soup.select_one('#application main div div span span a')
        author = author_element.get_text(strip=True) if author_element else "Unknown"

        try:
            release_date = tree.xpath('/html/body/div[1]/main/div[1]/div[3]/div[1]/div[2]/div[2]/span[1]/span/text()')
            release_date = release_date[0].strip() if release_date else "No release date given."
        except Exception as error:
            print(f"Error retrieving release date: {error}")
            release_date = "Error occurred while retrieving release date"

        try:
            views = tree.xpath('/html/body/div[1]/main/div[1]/div[3]/div[1]/div[2]/div[2]/span[3]/span/text()')
            views = views[0].strip() if views else "No views given."
        except Exception as error:
            print(Fore.RED + f"Error retrieving views: {error}" + Fore.RESET)
            views = "Error occurred while retrieving views"

        title_element = soup.select_one('h1')
        title = title_element.get_text(strip=True) if title_element else "Unknown"

        meta_tag = soup.find('meta', property='og:image')
        cover = meta_tag.get('content') if meta_tag else None

        if cover is None:
            print(Fore.RED + "Meta tag with property='og:image' not found." + Fore.RESET)

        insert_lyrics(dbconn, url, title, author, lyrics, release_date, views, cover)

        hrefs = [a['href'] for a in soup.find_all('a', href=True)]
        filtered_hrefs = [href for href in hrefs if 'https://genius.com' in href and href not in blacklist]

        for href in filtered_hrefs:
            put_into_database(dbconn, href)

        wipe_out_url(dbconn, url)
        dbconn.close()
    except Exception as error:
        print(f"Error during lyrics crawling: {error}")

def insert_lyrics(dbconn, url, title, artist, lyrics, release_date, views, cover):
    try:
        insert_query = """
            INSERT INTO lyrics (url, title, artist, lyrics, release_date, views, cover)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (url, title, artist, lyrics, release_date, views, cover)

        cursor = dbconn.cursor()
        cursor.execute(insert_query, values)
        dbconn.commit()

        print(Fore.GREEN + 'Lyrics inserted successfully' + Fore.RESET)
    except mysql.connector.Error as error:
        print(f'Error inserting lyrics: {error}')

def wipe_out_url(dbconn, url):
    try:
        cursor = dbconn.cursor()
        cursor.execute('UPDATE song_urls SET visited = 1 WHERE url = %s', (url,))
        dbconn.commit()
        print('URL marked as visited:', url)
        return True
    except mysql.connector.Error as error:
        print(f'Error marking URL as visited: {error}')
        return False

def put_into_database(dbconn, url):
    url_type = url_identifier(url)
    try:
        cursor = dbconn.cursor()
        cursor.execute(f'INSERT INTO {url_type} (url, visited) VALUES (%s, %s)', (url, 0))
        dbconn.commit()
        print(Fore.LIGHTGREEN_EX  + f'Data inserted into {url_type} successfully' + Fore.RESET)
    except mysql.connector.Error as error:
        ok = "ok"

def url_identifier(url):
    if "/tags/" in url:
        return "tag_urls"
    elif "https://genius.com/Genius-" in url:
        return "translation_urls"
    elif url.endswith("-lyrics"):
        return "song_urls"
    elif "/artists/" in url:
        return "artist_urls"
    elif "/albums/" in url:
        return "album_urls"
    else:
        return "crap_urls"

# Start the script
initialize_genius(db_params)