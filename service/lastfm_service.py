import time
from datetime import datetime

import pylast
from loguru import logger

from config import settings
from model import AppleMusicTrack, LastFmTrack, LastFmUser, LastFmAlbum, LastFmTopItem, LastFmArtist

LASTFM_API_KEY = settings.LASTFM_API_KEY
LASTFM_API_SECRET = settings.LASTFM_API_SECRET
LASTFM_USERNAME = settings.LASTFM_USERNAME
LASTFM_PASSWORD_HASH = pylast.md5(settings.LASTFM_PASSWORD)

network = pylast.LastFMNetwork(
    api_key=LASTFM_API_KEY,
    api_secret=LASTFM_API_SECRET,
    username=LASTFM_USERNAME,
    password_hash=LASTFM_PASSWORD_HASH
)


"""
LastFM API related methods
"""


async def get_user() -> pylast.User:
    return network.get_user(settings.LASTFM_USERNAME)


async def get_user_minimal() -> LastFmUser:
    user = await get_user()
    return LastFmUser(
        name=user.get_name(),
        image_url=user.get_image(),
        url=user.get_url()
    )


async def get_user_playcount() -> str:
    user = await get_user()
    playcount = user.get_playcount()
    playcount = format(playcount, ',')
    return playcount


async def get_user_recent_tracks() -> list[LastFmTrack]:
    user = await get_user()

    recent_tracks = user.get_recent_tracks(limit=20)
    tracks = []
    for track in recent_tracks:
        scrobbled_at = datetime.fromtimestamp(int(track.timestamp))
        t = LastFmTrack(
            name=track.track.title,
            artist=track.track.artist.name,
            album=track.album,
            scrobbled_at=scrobbled_at.strftime('%Y-%m-%d %H:%M:%S')
        )
        tracks.append(t)

    return tracks


async def get_user_loved_tracks() -> list[LastFmTrack]:
    user = await get_user()

    loved_tracks = user.get_loved_tracks()
    tracks = []
    for track in loved_tracks:
        loved_at = datetime.fromtimestamp(int(track.timestamp))
        t = LastFmTrack(
            name=track.track.title,
            artist=track.track.artist.name,
            loved_at=loved_at.strftime('%Y-%m-%d %H:%M:%S')
        )
        tracks.append(t)

    return tracks


async def get_user_top_artists() -> list[LastFmTopItem]:
    user = await get_user()

    top_artists = user.get_top_artists(limit=10)
    artists = []
    for artist in top_artists:
        details = artist.item
        model = LastFmArtist(
            name=details.name,
            playcount=details.get_playcount(),
            url=details.get_url()
        )
        top_item = LastFmTopItem(
            name=artist.item.track_name,
            weight=artist.weight,
            details=model
        )
        artists.append(top_item)

    return artists


async def get_user_top_albums() -> list[LastFmTopItem]:
    user = await get_user()

    top_albums = user.get_top_albums(limit=10)
    albums = []
    for album in top_albums:
        details = album.item
        model = LastFmAlbum(
            title=details.title,
            artist=details.artist.name,
            image_url=details.get_cover_image(size=pylast.SIZE_LARGE),
            url=details.get_url()
        )
        top_item = LastFmTopItem(
            name=album.item.title,
            weight=album.weight,
            details=model
        )
        albums.append(top_item)

    return albums


async def update_lastfm_now_playing(current_song: AppleMusicTrack) -> None:
    try:
        network.update_now_playing(
            artist=current_song.artist,
            title=current_song.track_name,
            album=current_song.album
        )
        logger.info("Updated Last.fm now playing")
    except pylast.WSError as e:
        logger.error("Failed to update Last.fm now playing")
        logger.error(f"{e}")


async def scrobble_to_lastfm(current_song: AppleMusicTrack) -> bool:
    artist = current_song.artist
    track = current_song.track_name
    album = current_song.album
    timestamp = int(time.time())

    if artist and track and album:
        try:
            network.scrobble(artist=artist, title=track, timestamp=timestamp, album=album)
            logger.info(f"Scrobbled to LastFm: '{artist}' - {track}")
            return True
        except pylast.WSError as e:
            logger.error("Failed to scrobble to Last.fm")
            logger.error(f"{e}")
            return False


async def get_lastfm_album(title: str, artist: str) -> LastFmAlbum | None:
    album = network.get_album(title=title, artist=artist)
    if album:
        return LastFmAlbum(
            title=album.title,
            artist=album.artist.name,
            image_url=album.get_cover_image(),
            url=album.get_url()
        )
    else:
        return None


async def current_track_user_scrobbles(current_song: AppleMusicTrack) -> list[LastFmTrack]:
    user = await get_user()
    track_scrobbles = user.get_track_scrobbles(current_song.artist, current_song.track_name)

    tracks = []
    for t in track_scrobbles:
        timestamp = int(t.timestamp)
        timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        track = LastFmTrack(
            name=t.track.title,
            artist=t.track.artist.name,
            album=t.album,
            scrobbled_at=timestamp
        )
        tracks.append(track)

    return tracks


async def user_weekly_album_charts(from_date, to_date):
    user = await get_user()
    albums = user.get_weekly_album_charts(from_date, to_date)
    for album in albums:
        details = album.item
        model = LastFmAlbum(
            title=details.title,
            artist=details.artist.name
        )
        print(model.title, model.artist)

