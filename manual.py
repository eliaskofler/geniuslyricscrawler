from manual2.artist import getArtist
from manual2.albums import getAlbums

if __name__ == "__main__":
    artist_id = input("Enter Artist ID: ")
    getArtist(artist_id)
    getAlbums(artist_id)
