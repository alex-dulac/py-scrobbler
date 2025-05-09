from fastapi import APIRouter, Depends
from loguru import logger

from api.spotify_router import spotify_router
from api.data_router import data_router
from api.scrobble_router import scrobble_router
from api.state import get_app_state
from api.user_router import user_router
from config.security import verify_token
from service.apple_music_service import poll_apple_music, get_current_track_artwork_data
from service.lastfm_service import get_lastfm_account_details, LastFmService
from utils import poll_comparison
from service.spotify_service import SpotifyService

router = APIRouter(dependencies=[
    Depends(get_app_state),
    Depends(verify_token)
])

router.include_router(data_router)
router.include_router(scrobble_router)
router.include_router(spotify_router)
router.include_router(user_router)

lasfm = LastFmService()
spotify = SpotifyService()


@router.get("/poll-song/")
async def get_current_song():
    app_state = await get_app_state()
    active_integration = app_state.active_integration

    match active_integration:
        case active_integration.APPLE_MUSIC:
            poll = await poll_apple_music()
        case active_integration.SPOTIFY:
            poll = await spotify.poll_spotify()
        case _:
            raise ValueError("Invalid active integration")

    compare = await poll_comparison(poll, app_state.current_song, app_state.lastfm_album)

    if compare.is_same_song:
        data = {
            "current_song": app_state.current_song,
            "lastfm_album": app_state.lastfm_album,
            "artist_image": app_state.artist_image,
        }

        return {"data": data}

    if compare.update_song:
        app_state.current_song = poll
        spotify_artist = await spotify.get_artist_from_name(app_state.current_song.artist) if app_state.current_song else None
        app_state.artist_image = spotify_artist.image_url[0] if spotify_artist else None
        logger.info(f"Updated current song: {poll.name}")

    if compare.update_song_playing_status:
        app_state.current_song.playing = poll.playing
        logger.info(f"Updated '{poll.name}' playing status: {poll.playing}")

    if compare.update_lastfm_now_playing:
        app_state.current_song.lastfm_updated_now_playing = await lasfm.update_now_playing(app_state.current_song)

    if compare.update_lastfm_album:
        app_state.lastfm_album = await lasfm.get_album(app_state.current_song.album, app_state.current_song.artist)

    data = {
        "current_song": app_state.current_song,
        "lastfm_album": app_state.lastfm_album,
        "artist_image": app_state.artist_image,
    }

    return {"data": data}


@router.get("/poll-song/artwork")
async def get_current_song():
    app_state = await get_app_state()
    active_integration = app_state.active_integration
    artwork = None

    match active_integration:
        case active_integration.APPLE_MUSIC:
            artwork = await get_current_track_artwork_data()
        case active_integration.SPOTIFY:
            pass
        case _:
            raise ValueError("Invalid active integration")

    return {"artwork": artwork}


@router.get("/state/")
async def sync():
    app_state = await get_app_state()
    return {
        "current_song": app_state.current_song,
        "lastfm_album": app_state.lastfm_album,
        "is_scrobbling": app_state.is_scrobbling,
        "active_integration": app_state.active_integration,
        "user": await get_lastfm_account_details()
    }
