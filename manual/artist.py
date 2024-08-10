def getArtist(artist_id):
    import requests
    import json
    import mysql.connector
    from mysql.connector import Error
    import logging
    import time

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Function to insert artist data into the database
    def insert_artist_data(artist_data, db_config):
        try:
            print("Found artist: " + artist_data['name'])
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
            print("Artist saved.")
        except Error as e:
            logging.error(f"Error inserting data into MySQL table: {e}")
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

    try:
        fetch_and_store_artist_data(artist_id, db_config)
        
        # Optional: Sleep for a short duration to avoid hitting API rate limits
        time.sleep(1)

    except ValueError:
        logging.error("Invalid input. Please enter a valid number.")
    except Error as e:
        logging.error(f"Error connecting to MySQL: {e}")