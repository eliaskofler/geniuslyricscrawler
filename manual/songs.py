def getSongs(artist_id):
    import requests

    def fetch_and_save_songs(artist_id):
        try:
            artist_id = int(artist_id)  # Convert input to integer
            print()
            
            # Define the base URL for songs
            base_url = "https://genius.com/api/artists"
            page = 1
            total_songs_fetched = 0  # Initialize total songs counter

            with open("songs.txt", "w") as file:  # Open the file in write mode
                while True:
                    # Construct the URL with the current page number
                    url = f"{base_url}/{artist_id}/songs?page={page}"
                    
                    # Make a request to the API
                    response = requests.get(url)

                    # Check if the request was successful
                    if response.status_code == 200:
                        # Parse the JSON response
                        data = response.json()

                        # Extract the list of songs
                        songs = data.get("response", {}).get("songs", [])

                        # Iterate over each song and save the required information
                        for song in songs:
                            total_songs_fetched += 1
                            song_url = song.get("url")
                            
                            # Write the song URL to the file
                            file.write(song_url + "\n")

                            # Cool output: Total songs fetched counter with current page
                            print(f"Page: {page} | Total songs fetched: {total_songs_fetched}", end='\r', flush=True)

                        # Extract the next page number
                        next_page = data.get("response", {}).get("next_page")

                        # Check if there is a next page
                        if next_page is None:
                            print(f"\nFinished fetching all songs. Total songs fetched: {total_songs_fetched}")
                            break
                        else:
                            page = next_page

                    else:
                        print("Failed to retrieve data from Genius API")
                        break
        except ValueError:
            print("Invalid input. Please enter a valid artist ID.")

    fetch_and_save_songs(artist_id)

artistid = input("id> ")
getSongs(artistid)