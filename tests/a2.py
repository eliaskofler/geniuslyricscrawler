import requests
import json
import mysql.connector
from mysql.connector import Error
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to insert artist data into the database
def insert_artist_data(artist_data, db_config):
    try:
        print("inserting new data: " + artist_data['name'])
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO artists (url, name, slug, artist_id, description, image_url, header_image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                slug = VALUES(slug),
                description = VALUES(description),
                image_url = VALUES(image_url),
                header_image_url = VALUES(header_image_url),
                last_updated = CURRENT_TIMESTAMP
        """
        cursor.execute(insert_query, (
            artist_data['url'],
            artist_data['name'],
            artist_data['slug'],
            artist_data['artist_id'],
            artist_data['description'],
            artist_data['image_url'],
            artist_data['header_image_url']
        ))
        connection.commit()
    except Error as e:
        logging.error(f"Error inserting data into MySQL table: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()

# Function to get the highest artist_id from the database
def get_highest_artist_id(db_config):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT artist_id FROM artists ORDER BY artist_id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            highest_id = int(result[0])
            return highest_id
        else:
            return 0
    except Error as e:
        logging.error(f"Error fetching data from MySQL table: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()

# Function to get the current count of artist entries in the database
def get_artist_count(db_config):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM artists")
        result = cursor.fetchone()
        return result[0]
    except Error as e:
        logging.error(f"Error counting entries in MySQL table: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()

def fetch_and_store_artist_data(artist_id, db_config):
    url = f'https://genius.com/api/artists/{artist_id}/'
    response = requests.get(url)
    
    if response.status_code == 200:
        json_data = response.json()
        
        artist_data = json_data.get('response', {}).get('artist', {})
        artist_data_to_insert = {
            'url': artist_data.get('url', ''),
            'name': artist_data.get('name', ''),
            'slug': artist_data.get('slug', ''),
            'artist_id': artist_data.get('id', ''),
            'description': artist_data.get('description_preview', ''),
            'image_url': artist_data.get('image_url', ''),
            'header_image_url': artist_data.get('header_image_url', '')
        }

        # Insert data into the database
        insert_artist_data(artist_data_to_insert, db_config)
    else:
        logging.info(f"Failed to retrieve the data for artist_id {artist_id}. Status code: {response.status_code}")

# Database connection configuration
db_config = {
    'host': 'obunic.net',
    'user': 'root',
    'password': '!Stiefel(123)',
    'database': 'geniuslyrics'
}

target_count = 250000

try:
    while True:
        # Get the current count of artist entries in the database
        current_count = get_artist_count(db_config)
        
        if current_count >= target_count:
            logging.info(f"Reached target of {target_count} entries. Stopping crawler.")
            break
        
        # Get the highest artist_id from the database
        highest_artist_id = get_highest_artist_id(db_config)
        next_artist_id = highest_artist_id + 1

        # Number of threads to use
        num_threads = 100
        batch_size = 1000  # Adjust the range as needed

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(fetch_and_store_artist_data, artist_id, db_config)
                       for artist_id in range(next_artist_id, next_artist_id + batch_size)]
            
            for future in as_completed(futures):
                try:
                    future.result()  # This will raise exceptions if any occurred in the threads
                except Exception as e:
                    logging.error(f"Error in thread execution: {e}")
        
        # Optional: Sleep for a short duration to avoid hitting API rate limits
        time.sleep(1)

except Error as e:
    logging.error(f"Error connecting to MySQL: {e}")