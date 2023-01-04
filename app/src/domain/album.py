from dataclasses import dataclass


@dataclass
class Album:
    id: str
    name: str
    type: str
    genres: list[str]
    popularity: int
    release_date: str
    total_tracks: int
    artists_ids: list[str]
    tracks_ids: list[str]
