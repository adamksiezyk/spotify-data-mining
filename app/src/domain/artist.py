from dataclasses import dataclass


@dataclass
class Artist:
    id: str
    name: str
    followers: int
    genres: list[str]
    popularity: int
