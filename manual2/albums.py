def getAlbums(artist_id):
    import requests
    import mysql.connector
    from mysql.connector import Error
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

    def fetch_and_insert_data(artist_id):
        connection = get_db_connection()
        if connection is None:
            print("MySQL Connection not available.")
            return

        try:
            artist_id = int(artist_id)  # Convert input to integer
            print()
            
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

                    albumCount = 0

                    # Iterate over each album and print the required information
                    for album in albums:
                        albumCount += 1
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
                        print(f"Albums fetched: {albumCount}", end='\r', flush=True)

                        insert_album_data(connection, album_id, name, full_title, url, cover_art_thumbnail_url, cover_art_url, release_date, artist_id, artist_name, artist_slug, artist_url)
                    
                    print("Albums fetched:", albumCount)

                    # Extract the next page number
                    next_page = data.get("response", {}).get("next_page")

                    # Check if there is a next page
                    if next_page is None:
                        print()
                        break
                    else:
                        page = next_page
                        print(f"Fetching page {page}...")

                else:
                    print("Failed to retrieve data from Genius API")
                    break
        except ValueError:
            print("Invalid input. Please enter a valid artist ID.")

    fetch_and_insert_data(artist_id)