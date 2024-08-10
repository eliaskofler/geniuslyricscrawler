import mysql.connector

# Database connection details
db_config = {
    'user': 'root',
    'password': '!Stiefel(123)',
    'host': 'obunic.net',
    'database': 'lyrics',
}

# Connect to the "lyrics" database
print("Connecting to the 'lyrics' database...")
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()
print("Connected to 'lyrics'.")

# Index creation queries
index_queries = [
    # URLs Tables
    "CREATE INDEX idx_urls_url ON urls_artist(url);",
    "CREATE INDEX idx_urls_url ON urls_song(url);",
    "CREATE INDEX idx_urls_url ON urls_album(url);",
    "CREATE INDEX idx_urls_url ON urls_translation(url);",
    "CREATE INDEX idx_urls_url ON urls_tag(url);",
    "CREATE INDEX idx_urls_url ON urls_crap(url);",
    
    # Artists Table
    "CREATE INDEX idx_artists_url ON artists(url);",
    "CREATE INDEX idx_artists_name ON artists(name);",
    "CREATE INDEX idx_artists_slug ON artists(slug);",
    "CREATE INDEX idx_artists_genius_id ON artists(genius_id);",

    # Albums Table
    "CREATE INDEX idx_albums_url ON albums(url);",
    "CREATE INDEX idx_albums_name ON albums(name);",
    "CREATE INDEX idx_albums_artist_url ON albums(artist_url);",
    "CREATE INDEX idx_albums_genius_id ON albums(genius_id);",

    # Album Songs Table
    "CREATE INDEX idx_album_songs_song_url ON album_songs(song_url);",
    "CREATE INDEX idx_album_songs_album_id ON album_songs(album_id);",

    # Lyrics Table
    "CREATE INDEX idx_lyrics_url ON lyrics(url);",
    "CREATE INDEX idx_lyrics_title ON lyrics(title);",
    "CREATE INDEX idx_lyrics_artist ON lyrics(artist);"
]

# Execute the index creation queries
for query in index_queries:
    print(f"Executing: {query}")
    cursor.execute(query)

# Commit the changes
connection.commit()
print("Indexes created and committed to the database.")

# Close the database connection
cursor.close()
connection.close()
print("Connection closed. Indexing complete!")