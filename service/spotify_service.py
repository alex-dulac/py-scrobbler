import spotipy
from spotipy.oauth2 import SpotifyOAuth

from config import settings
from models.artist import SpotifyArtist
from models.user import SpotifyUser

auth = SpotifyOAuth(
    client_id=settings.SPOTIFY_CLIENT_ID,
    client_secret=settings.SPOTIFY_CLIENT_SECRET,
    redirect_uri=settings.SPOTIFY_REDIRECT_URI,
    scope=['user-read-playback-state', 'user-modify-playback-state', 'user-read-currently-playing']

)
spotify = spotipy.Spotify(auth_manager=auth)


async def get_spotify_account_information():
    result: dict = spotify.current_user()
    if result:
        url = result['external_urls']['spotify']
        return SpotifyUser(
            name=result['display_name'],
            url=url,
            images=result['images']
        )
    else:
        return None


async def poll_spotify():
    result: dict = spotify.current_user_playing_track()
    if result:
        return result['item']['album']['name'], result['item']['artists'][0]['name'], result['item']['name']
    else:
        return None


async def get_artist_from_name(artist_name: str) -> SpotifyArtist:
    spotify_artist = spotify.search(q=artist_name, type='artist')
    artist_id = spotify_artist['artists']['items'][0]['id']
    result = spotify.artist(artist_id)
    artist = SpotifyArtist(
        id=result['id'],
        name=result['name'],
        image_url=result['images'][0]['url']
    )
    return artist


