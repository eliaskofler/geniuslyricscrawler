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

print("Connecting to the 'geniuslyrics' database...")
# Connect to the "geniuslyrics" database
connection_geniuslyrics = mysql.connector.connect(**db_config_geniuslyrics)
cursor_geniuslyrics = connection_geniuslyrics.cursor()
print("Connected to 'geniuslyrics'.")

print("Connecting to the 'lyrics' database...")
# Connect to the "lyrics" database
connection_lyrics = mysql.connector.connect(**db_config_lyrics)
cursor_lyrics = connection_lyrics.cursor()
print("Connected to 'lyrics'.")

print("Fetching tag URLs from the 'tag_urls' table in 'geniuslyrics'...")
# Fetch URLs from the "tag_urls" table in "geniuslyrics"
cursor_geniuslyrics.execute("SELECT url FROM tag_urls")
tag_urls = cursor_geniuslyrics.fetchall()
print(f"Fetched {len(tag_urls)} tag URLs from 'tag_urls'.")

print("Inserting tag URLs into the 'urls_tag' table in 'lyrics'...")
insert_query = "INSERT IGNORE INTO urls_tag (url) VALUES (%s)"
for count, url in enumerate(tag_urls, start=1):
    cursor_lyrics.execute(insert_query, (url[0],))
    if count % 10000 == 0:  # Print progress every 10,000 URLs
        print(f"Inserted {count} tag URLs into 'urls_tag'.")

# Commit the changes to the "lyrics" database
connection_lyrics.commit()
print("Committed the changes to 'lyrics'.")

# Close the database connections
cursor_geniuslyrics.close()
connection_geniuslyrics.close()
cursor_lyrics.close()
connection_lyrics.close()

print("Connections closed.")
print("Transfer complete!")