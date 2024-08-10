import mysql.connector

# Database connection details
db_config_geniuslyrics = {
    'user': 'root',
    'password': '!Stiefel(123)',
    'host': 'obunic.net',
    'database': 'geniuslyrics',
}

db_config_lyrics = {
    'user': 'root',
    'password': '!Stiefel(123)',
    'host': 'obunic.net',
    'database': 'lyrics',
}
print("connecting to databases")
# Connect to the "geniuslyrics" database
connection_geniuslyrics = mysql.connector.connect(**db_config_geniuslyrics)
cursor_geniuslyrics = connection_geniuslyrics.cursor()

# Connect to the "lyrics" database
connection_lyrics = mysql.connector.connect(**db_config_lyrics)
cursor_lyrics = connection_lyrics.cursor()
print("connected to database")

print('Fetch URLs from the "album_songs" table in "geniuslyrics"')
cursor_geniuslyrics.execute("SELECT song_url FROM album_songs")
song_urls = cursor_geniuslyrics.fetchall()
print("done with that fetching of urls")

# Insert URLs into the "urls_song" table in "lyrics" database
insert_query = "INSERT IGNORE INTO urls_song (url) VALUES (%s)"

print("inserting urls")
for url in song_urls:
    cursor_lyrics.execute(insert_query, (url[0],))

# Commit the changes to "lyrics" database
connection_lyrics.commit()

print("done")

# Close the connections
cursor_geniuslyrics.close()
connection_geniuslyrics.close()
cursor_lyrics.close()
connection_lyrics.close()

print("Transfer complete!")