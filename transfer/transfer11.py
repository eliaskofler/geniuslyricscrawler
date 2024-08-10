import mysql.connector

# Database connection details for "geniuslyrics"
db_config_geniuslyrics = {
    'user': 'root',
    'password': '!Stiefel(123)',
    'host': 'obunic.net',
    'database': 'geniuslyrics',
}

# Database connection details for "lyrics"
db_config_lyrics = {
    'user': 'root',
    'password': '!Stiefel(123)',
    'host': 'obunic.net',
    'database': 'lyrics',
}

# Connect to the "geniuslyrics" database
print("Connecting to the 'geniuslyrics' database...")
connection_geniuslyrics = mysql.connector.connect(**db_config_geniuslyrics)
cursor_geniuslyrics = connection_geniuslyrics.cursor(dictionary=True)
print("Connected to 'geniuslyrics'.")

# Connect to the "lyrics" database
print("Connecting to the 'lyrics' database...")
connection_lyrics = mysql.connector.connect(**db_config_lyrics)
cursor_lyrics = connection_lyrics.cursor()
print("Connected to 'lyrics'.")

# Fetch data from the "artists" table in "geniuslyrics"
print("Fetching artist data from 'geniuslyrics'...")
cursor_geniuslyrics.execute("SELECT url, name, slug, artist_id, description, image_url, header_image_url FROM artists")
artists_data = cursor_geniuslyrics.fetchall()
print(f"Fetched {len(artists_data)} artists from 'geniuslyrics'.")

# Prepare insert query for "lyrics" database
insert_query = """
INSERT INTO artists (url, name, slug, genius_id, description, image_url, header_image_url)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    slug = VALUES(slug),
    genius_id = VALUES(genius_id),
    description = VALUES(description),
    image_url = VALUES(image_url),
    header_image_url = VALUES(header_image_url)
"""

# Insert data into the "artists" table in "lyrics"
print("Inserting data into 'lyrics' database...")
for artist in artists_data:
    cursor_lyrics.execute(insert_query, (
        artist['url'],
        artist['name'],
        artist['slug'],
        artist['artist_id'],  # Map artist_id to genius_id
        artist['description'],
        artist['image_url'],
        artist['header_image_url']
    ))

# Commit the changes
connection_lyrics.commit()
print("Data inserted and committed to 'lyrics' database.")

# Close the database connections
cursor_geniuslyrics.close()
connection_geniuslyrics.close()
cursor_lyrics.close()
connection_lyrics.close()

print("Connections closed. Transfer complete!")