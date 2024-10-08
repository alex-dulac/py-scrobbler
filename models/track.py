class Track:
    def __init__(
            self,
            name: str = None,
            artist: str = None,
            album: str = None,
            playing: bool = False,
            time_played: int = 0,
            scrobbled: bool = False,
            lastfm_updated_now_playing: bool = False,
    ):
        self.name = name
        self.artist = artist
        self.album = album
        self.playing = playing
        self.time_played = time_played
        self.scrobbled = scrobbled
        self.lastfm_updated_now_playing = lastfm_updated_now_playing


class AppleMusicTrack(Track):
    def __init__(self, track_info, playing):
        super().__init__(playing=playing)
        self.id = None
        self.index = None
        self.persistent_id = None
        self.time = None
        self.duration = None
        self.album_artist = None
        self.composer = None
        self.genre = None
        self.track_number = None
        self.disc_number = None
        self.year = None
        self.release_date = None
        self.loved = None
        self.disliked = None
        self.album_loved = None
        self.album_disliked = None

        ae_type_map = {
            "AEType(b'ID  ')": 'id',
            "AEType(b'pidx')": 'index',
            "AEType(b'pnam')": 'name',
            "AEType(b'pPIS')": 'persistent_id',
            "AEType(b'pTim')": 'time',
            "AEType(b'pDur')": 'duration',
            "AEType(b'pArt')": 'artist',
            "AEType(b'pAlA')": 'album_artist',
            "AEType(b'pCmp')": 'composer',
            "AEType(b'pAlb')": 'album',
            "AEType(b'pGen')": 'genre',
            "AEType(b'pTrN')": 'track_number',
            "AEType(b'pDsN')": 'disc_number',
            "AEType(b'pYr ')": 'year',
            "AEType(b'pRlD')": 'release_date',
            "AEType(b'pLov')": 'loved',
            "AEType(b'pHat')": 'disliked',
            "AEType(b'pALv')": 'album_loved',
            "AEType(b'pAHt')": 'album_disliked'
        }

        for key, value in track_info.items():
            attr_name = ae_type_map.get(str(key))
            if attr_name:
                setattr(self, attr_name, value)


class LastFmTrack(Track):
    def __init__(
            self,
            name: str = None,
            artist: str = None,
            album: str = None,
            scrobbled_at: str = None,
            loved_at: str = None
    ):
        super().__init__(name=name, artist=artist, album=album)
        self.scrobbled_at = scrobbled_at
        self.loved_at = loved_at


class SpotifyTrack(Track):
    pass
