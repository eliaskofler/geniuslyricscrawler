import requests
import mysql.connector
from mysql.connector import Error
import random
import concurrent.futures

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='obunic.net',
            user='root',
            password='!Stiefel(123)',
            database='geniuslyrics'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_random_artist_id(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT artist_id FROM artists WHERE albums_fetched = 0")
        artists = cursor.fetchall()
        if artists:
            artist_id = random.choice(artists)[0]
            return artist_id
        else:
            print("No artists found with albums_fetched = 0.")
            return None
    except Error as e:
        print(f"Error fetching artist_id from MySQL table: {e}")
        return None
    finally:
        cursor.close()

def update_artist_fetched_status(connection, artist_id):
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE artists SET albums_fetched = 1 WHERE artist_id = %s", (artist_id,))
        connection.commit()
    except Error as e:
        print(f"Error updating artist status in MySQL table: {e}")
    finally:
        cursor.close()

def insert_album_data(connection, album_id, name, full_title, url, cover_art_thumbnail_url, cover_art_url, timestamp, artist_id, artist_name, artist_slug, artist_url):
    try:
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO albums (url, full_title, name, album_id, cover_art_thumbnail, cover_art_url, release_date, artist_id, artist_name, artist_slug, artist_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                full_title = VALUES(full_title),
                name = VALUES(name),
                cover_art_thumbnail = VALUES(cover_art_thumbnail),
                cover_art_url = VALUES(cover_art_url),
                release_date = VALUES(release_date),
                artist_name = VALUES(artist_name),
                artist_slug = VALUES(artist_slug),
                artist_url = VALUES(artist_url),
                last_updated = CURRENT_TIMESTAMP
        """
        cursor.execute(insert_query, (
            url,
            full_title,
            name,
            album_id,
            cover_art_thumbnail_url,
            cover_art_url,
            timestamp,
            artist_id,
            artist_name,
            artist_slug,
            artist_url
        ))
        connection.commit()
    except Error as e:
        print(f"Error inserting data into MySQL table: {e}")
    finally:
        cursor.close()

def fetch_and_insert_data():
    connection = get_db_connection()
    if connection is None:
        print("MySQL Connection not available.")
        return

    artist_id = get_random_artist_id(connection)
    if artist_id is None:
        print("No artist_id to process.")
        return

    # Define the base URL
    base_url = "https://genius.com/api/artists"
    page = 1

    while True:
        # Construct the URL with the current page number
        url = f"{base_url}/{artist_id}/albums?page={page}"
        
        # Make a request to the API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Extract the list of albums
            albums = data.get("response", {}).get("albums", [])

            # Iterate over each album and print the required information
            for album in albums:
                cover_art_thumbnail_url = album.get("cover_art_thumbnail_url")
                cover_art_url = album.get("cover_art_url")
                album_id = album.get("id")
                name = album.get("name")
                full_title = album.get("full_title")
                url = album.get("url")
                
                # Extract release date components
                release_date_components = album.get("release_date_components", {})
                year = release_date_components.get("year", "9999") if release_date_components else "9999"
                month = release_date_components.get("month", "99") if release_date_components else "99"
                day = release_date_components.get("day", "99") if release_date_components else "99"

                # Format the release date
                release_date = f"{year}-{month}-{day}" if year and month and day else None
                
                # Extract artist information
                artist = album.get("artist", {})
                artist_id = artist.get("id")
                artist_name = artist.get("name")
                artist_slug = artist.get("slug")
                artist_url = artist.get("url")

                # Print the information
                print(f"Album ID: {album_id}")
                print(f"Name: {name}")
                print(f"Full Title: {full_title}")
                print(f"URL: {url}")
                print(f"Cover Art Thumbnail URL: {cover_art_thumbnail_url}")
                print(f"Cover Art URL: {cover_art_url}")
                print(f"Release Date: {release_date}")
                print(f"Artist ID: {artist_id}")
                print(f"Artist Name: {artist_name}")
                print(f"Artist Slug: {artist_slug}")
                print(f"Artist URL: {artist_url}")
                print("-" * 40)

                insert_album_data(connection, album_id, name, full_title, url, cover_art_thumbnail_url, cover_art_url, release_date, artist_id, artist_name, artist_slug, artist_url)
            
            # Extract the next page number
            next_page = data.get("response", {}).get("next_page")

            # Check if there is a next page
            if next_page is None:
                print("No more pages.")
                break
            else:
                page = next_page
                print(f"Fetching page {page}...")

        else:
            print("Failed to retrieve data from Genius API")
            break

    update_artist_fetched_status(connection, artist_id)

if __name__ == "__main__":
    while True:
        fetch_and_insert_data()