import time
from datetime import datetime

import applescript
import pylast

import settings
from model import AppleMusicTrack, LastFmTrack, LastFmUser

LASTFM_API_KEY = settings.LASTFM_API_KEY
LASTFM_API_SECRET = settings.LASTFM_API_SECRET
USERNAME = settings.USERNAME
PASSWORD_HASH = pylast.md5(settings.PASSWORD)

# Create a Last.fm network object
network = pylast.LastFMNetwork(
    api_key=LASTFM_API_KEY,
    api_secret=LASTFM_API_SECRET,
    username=USERNAME,
    password_hash=PASSWORD_HASH
)


def poll_apple_music() -> AppleMusicTrack | None:
    script = """
    tell application "Music"
        if it is running then
            set currentTrack to the current track
            set trackInfo to (get properties of currentTrack)
            return {trackInfo, player state is playing}
        else
            return {missing value, false}
        end if
    end tell
    """
    try:
        result = applescript.AppleScript(script).run()
        track = result[0]
        playing = result[1]

        if track != "AEType(b'msng')":
            return AppleMusicTrack(track_info=track, playing=playing)
        else:
            return None
    except applescript.ScriptError as e:
        print("Applescript Error:")
        print(f"{e}")


def update_lastfm_now_playing(current_song: AppleMusicTrack) -> None:
    if current_song.playing:
        network.update_now_playing(
            artist=current_song.artist,
            title=current_song.name,
            album=current_song.album
        )
    else:
        print("Not playing")


def scrobble_to_lastfm(current_song: AppleMusicTrack) -> bool:
    artist = current_song.artist
    track = current_song.name
    album = current_song.album
    timestamp = int(time.time())

    if artist and track and album:
        try:
            network.scrobble(artist=artist, title=track, timestamp=timestamp, album=album)
            print("Scrobbled current song to Last.fm")
            return True
        except pylast.WSError as e:
            print("pylast Error:")
            print(f"{e}")
            return False


def get_user() -> pylast.User:
    return network.get_user(settings.USERNAME)


def get_user_details() -> LastFmUser:
    user = get_user()
    return LastFmUser(
        name=user.name,
        playcount=user.get_playcount(),
        now_playing=user.get_now_playing(),
        loved_tracks=user.get_loved_tracks(),
        recent_tracks=user.get_recent_tracks(),
        image_url=user.get_image(),
        top_artists=user.get_top_artists(),
        url=user.get_url(),
    )


def print_polled_apple_music_song(current_song: AppleMusicTrack | None) -> None:
    if current_song:
        print("Apple Music current song: ", current_song.name, " by ", current_song.artist)
        print("Song is paused") if not current_song.playing else None
    else:
        print("Apple Music not playing")


def get_most_recent_scrobble() -> LastFmTrack | None:
    user_lastfm = get_user()
    user_recent_tracks = user_lastfm.get_recent_tracks()
    most_recent_scrobble = user_recent_tracks[0]
    timestamp = int(most_recent_scrobble.timestamp)
    scrobbled_at = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return LastFmTrack(
        name=most_recent_scrobble.track,
        artist=most_recent_scrobble.track.artist,
        album=most_recent_scrobble.album,
        scrobbled_at=scrobbled_at
    )


def print_most_recent_scrobble() -> None:
    most_recent_scrobble = get_most_recent_scrobble()
    print("Most recent scrobble: '", most_recent_scrobble.name,
          "' by ", most_recent_scrobble.artist,
          " from '", most_recent_scrobble.album,
          "' at ", most_recent_scrobble.scrobbled_at)

