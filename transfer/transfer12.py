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

# Fetch data from the "albums" table in "geniuslyrics"
print("Fetching album data from 'geniuslyrics'...")
cursor_geniuslyrics.execute("SELECT url, full_title, name, album_id, cover_art_thumbnail, cover_art_url, release_date, artist_name, artist_slug, artist_url FROM albums")
albums_data = cursor_geniuslyrics.fetchall()
print(f"Fetched {len(albums_data)} albums from 'geniuslyrics'.")

# Prepare insert query for "lyrics" database
insert_query = """
INSERT INTO albums (url, full_title, name, genius_id, cover_art_thumbnail, cover_art_url, release_date, artist_name, artist_slug, artist_url)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE 
    full_title = VALUES(full_title),
    name = VALUES(name),
    genius_id = VALUES(genius_id),
    cover_art_thumbnail = VALUES(cover_art_thumbnail),
    cover_art_url = VALUES(cover_art_url),
    release_date = VALUES(release_date),
    artist_name = VALUES(artist_name),
    artist_slug = VALUES(artist_slug),
    artist_url = VALUES(artist_url)
"""

# Insert data into the "albums" table in "lyrics"
print("Inserting data into 'lyrics' database...")
for album in albums_data:
    cursor_lyrics.execute(insert_query, (
        album['url'],
        album['full_title'],
        album['name'],
        album['album_id'],  # Map album_id to genius_id
        album['cover_art_thumbnail'],
        album['cover_art_url'],
        album['release_date'],
        album['artist_name'],
        album['artist_slug'],
        album['artist_url']
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