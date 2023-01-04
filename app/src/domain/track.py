from dataclasses import dataclass


@dataclass
class Track:
    id: str
    name: str
    popularity: int
    explicit: bool
    album_id: str
    artists_ids: list[str]
    url: str


@dataclass
class AudioFeatures:
    track_id: str
    danceability:  float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    duration_ms: int
    time_signature: int

