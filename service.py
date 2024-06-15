import time
from datetime import datetime

import applescript
import pylast

import settings
from model import AppleMusicTrack

API_KEY = settings.API_KEY
API_SECRET = settings.API_SECRET
USERNAME = settings.USERNAME
PASSWORD_HASH = pylast.md5(settings.PASSWORD)

# Create a Last.fm network object
network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET,
    username=USERNAME,
    password_hash=PASSWORD_HASH
)


def poll_apple_music() -> AppleMusicTrack | None:
    script = """
    tell application "Music"
        if it is running then
            if player state is playing then
                set trackName to name of current track
                set artistName to artist of current track
                set albumName to album of current track
                return {trackName, artistName, albumName}
            end if
        end if
    end tell
    """
    result = applescript.AppleScript(script).run()
    if result:
        track_info = result
        return AppleMusicTrack(
            track=track_info[0],
            artist=track_info[1],
            album=track_info[2]
        )
    else:
        return None


def scrobble_to_lastfm(current_song: AppleMusicTrack) -> bool:
    artist = current_song.artist
    track = current_song.track
    album = current_song.album
    timestamp = int(time.time())

    if artist and track and album:
        try:
            network.scrobble(artist=artist, title=track, timestamp=timestamp, album=album)
            return True
        except pylast.WSError as e:
            print(f"Error: {e}")
            return False


def print_current_song(current_song: AppleMusicTrack) -> None:
    if current_song:
        print("Apple Music playing: ", current_song.track)
    else:
        print("Apple Music not playing")


def print_most_recent_scrobble() -> None:
    user_lastfm = network.get_user(settings.USERNAME)
    print("LastFM user: ", user_lastfm.name)
    user_recent_tracks = user_lastfm.get_recent_tracks()
    most_recent_scrobble = user_recent_tracks[0]

    timestamp = int(most_recent_scrobble.timestamp)
    scrobbled_at = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    if most_recent_scrobble:
        print("Most recent scrobble: '", most_recent_scrobble.track.title, "' by ",
              most_recent_scrobble.track.artist, " from '", most_recent_scrobble.album, "'")
        print("Scrobbled at ", scrobbled_at)
    else:
        print("No scrobbles yet")

