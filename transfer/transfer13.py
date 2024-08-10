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

# Fetch data from the "album_songs" table in "geniuslyrics"
print("Fetching album_songs data from 'geniuslyrics'...")
cursor_geniuslyrics.execute("SELECT song_url, album_id FROM album_songs")
album_songs_data = cursor_geniuslyrics.fetchall()
print(f"Fetched {len(album_songs_data)} records from 'geniuslyrics'.")

# Prepare insert query for "lyrics" database
insert_query = """
INSERT INTO album_songs (song_url, album_id)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE 
    song_url = VALUES(song_url),
    album_id = VALUES(album_id)
"""

# Insert data into the "album_songs" table in "lyrics"
print("Inserting data into 'lyrics' database...")
for record in album_songs_data:
    cursor_lyrics.execute(insert_query, (
        record['song_url'],
        record['album_id']
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