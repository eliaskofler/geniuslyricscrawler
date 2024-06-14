import requests
import json
import mysql.connector
from mysql.connector import Error

# Function to insert artist data into the database
def insert_artist_data(connection, artist_data):
    try:
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
        print(f"Error inserting data into MySQL table: {e}")
    finally:
        cursor.close()

# Function to get the highest artist_id from the database
def get_highest_artist_id(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT artist_id FROM artists ORDER BY artist_id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            highest_id = int(result[0])
            return highest_id
        else:
            return 0
    except Error as e:
        print(f"Error fetching data from MySQL table: {e}")
        return 0
    finally:
        cursor.close()

def fetch_and_store_artist_data(artist_id, connection):
    url = f'https://genius.com/api/artists/{artist_id}/'
    response = requests.get(url)
    
    if response.status_code == 200:
        json_data = response.json()
        
        artist_data = json_data.get('response', {}).get('artist', {})
        name = artist_data.get('name', '')
        slug = artist_data.get('slug', '')
        description_preview = artist_data.get('description_preview', '')
        image_url = artist_data.get('image_url', '')
        header_image_url = artist_data.get('header_image_url', '')
        artist_url = artist_data.get('url', '')
        artist_id = artist_data.get('id', '')

        artist_data_to_insert = {
            'url': artist_url,
            'name': name,
            'slug': slug,
            'artist_id': artist_id,
            'description': description_preview,
            'image_url': image_url,
            'header_image_url': header_image_url
        }

        # Print the extracted fields
        print(f"Description Preview: {description_preview}")
        print(f"Image URL: {image_url}")
        print(f"Header Image URL: {header_image_url}")
        print(f"Artist URL: {artist_url}")
        print(f"Name: {name}")
        print(f"Slug: {slug}")
        print(f"Artist ID: {artist_id}")

        # Insert data into the database
        insert_artist_data(connection, artist_data_to_insert)
    else:
        print(f"Failed to retrieve the data for artist_id {artist_id}. Status code: {response.status_code}")

# Database connection configuration
try:
    connection = mysql.connector.connect(
        host='obunic.net',
        user='root',
        password='!Stiefel(123)',
        database='geniuslyrics'
    )
    if connection.is_connected():
        print("Successfully connected to the database")
        
        # Get the highest artist_id from the database
        highest_artist_id = get_highest_artist_id(connection)
        next_artist_id = highest_artist_id + 1

        while True:
            fetch_and_store_artist_data(next_artist_id, connection)
            next_artist_id += 1
except Error as e:
    print(f"Error connecting to MySQL: {e}")
finally:
    if connection.is_connected():
        connection.close()