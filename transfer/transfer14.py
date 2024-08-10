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

# Fetch data from the "lyrics" table in "geniuslyrics"
print("Fetching lyrics data from 'geniuslyrics'...")
cursor_geniuslyrics.execute("SELECT url, title, artist, lyrics, release_date, views, cover FROM lyrics")
lyrics_data = cursor_geniuslyrics.fetchall()
print(f"Fetched {len(lyrics_data)} records from 'geniuslyrics'.")

# Prepare insert query for "lyrics" database
insert_query = """
INSERT INTO lyrics (url, title, artist, lyrics, cover, release_date, views)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE 
    title = VALUES(title),
    artist = VALUES(artist),
    lyrics = VALUES(lyrics),
    cover = VALUES(cover),
    release_date = VALUES(release_date),
    views = VALUES(views)
"""

# Insert data into the "lyrics" table in "lyrics"
print("Inserting data into 'lyrics' database...")
for record in lyrics_data:
    cursor_lyrics.execute(insert_query, (
        record['url'],
        record['title'],
        record['artist'],
        record['lyrics'],
        record['cover'],
        record['release_date'],
        record['views']
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