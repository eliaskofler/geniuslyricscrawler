from manual.artist import getArtist
from manual.albums import getAlbums

if __name__ == "__main__":
    artist_id = input("Enter Artist ID: ")
    getArtist(artist_id)
    getAlbums(artist_id)
