import mysql.connector

# Database connection details
db_config = {
    'user': 'root',
    'password': '!Stiefel(123)',
    'host': 'obunic.net',
    'database': 'geniuslyrics',
}

# Connect to the database
print("Connecting to the database...")
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(buffered=True)
print("Connected to the database.")

# Fetch all entries from the lyrics table
print("Fetching entries from the lyrics table...")
cursor.execute("SELECT id, url FROM lyrics")
lyrics_entries = cursor.fetchall()
print(f"Fetched {len(lyrics_entries)} entries from the lyrics table.")

# Process each entry
for entry in lyrics_entries:
    lyrics_id, url = entry
    print(f"Processing lyrics entry with ID: {lyrics_id}, URL: {url}")
    
    # Search for the url in the album_songs table
    cursor.execute("SELECT album_id FROM album_songs WHERE song_url = %s", (url,))
    result = cursor.fetchone()
    
    if result:
        album_id = result[0]
        print(f"Found matching album_id: {album_id} for URL: {url}. Updating lyrics table.")
        # Update the album_id in the lyrics table
        cursor.execute("UPDATE lyrics SET album_id = %s WHERE id = %s", (album_id, lyrics_id))
        conn.commit()
        print(f"Updated lyrics entry with ID: {lyrics_id}.")
    else:
        # No match found, continue to the next entry
        print(f"No matching album_id found for URL: {url}.")
        continue

# Close the cursor and connection
print("Closing cursor and connection...")
cursor.close()
conn.close()
print("Closed cursor and connection.")