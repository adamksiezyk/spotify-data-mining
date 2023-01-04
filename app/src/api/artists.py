from threading import Thread

import requests

from api import NETWORK_EXCEPTIONS, token, async_utils
from api.albums import _create_album_from_json
from api.tracks import _create_track_from_json
from domain.album import Album
from domain.artist import Artist
from utils import retry


@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def get_artist(artist_id: str) -> Artist:
    json = requests.get(
        url=f'https://api.spotify.com/v1/artists/{artist_id}',
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    return _create_artist_from_json(json)


@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def get_artists(artist_ids: list[str]) -> list[Artist]:
    json = requests.get(
        url=f'https://api.spotify.com/v1/artists',
        params={'ids': ','.join(artist_ids)},
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    return [_create_artist_from_json(j) for j in json['artists']]


@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def get_artists_async(artist_ids: list[str], callback) -> Thread:
    return async_utils.async_request(
        'get',
        url=f'https://api.spotify.com/v1/artists',
        params={'ids': ','.join(artist_ids)},
        headers={'Authorization': f'Bearer {token}'},
        callback=lambda r: callback([_create_artist_from_json(j) for j in r.json()['artists']])
    )


@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def get_artist_albums(artist_id: str, country_code: str = None) -> list[Album]:
    json = requests.get(
        url=f'https://api.spotify.com/v1/artists/{artist_id}/albums',
        params={'market': country_code, 'limit': 50},
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    return [_create_album_from_json(j) for j in json['items']]


@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def get_artist_top_tracks(artist_id: str, country_code: str):
    json = requests.get(
        url=f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks',
        params={'market': country_code},
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    return [_create_track_from_json(j) for j in json['tracks']]


@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def get_related_artists(artist_id: str):
    json = requests.get(
        url=f'https://api.spotify.com/v1/artists/{artist_id}/related-artists',
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    return [_create_artist_from_json(j) for j in json['artists']]


def _create_artist_from_json(json: dict) -> Artist:
    return Artist(json['id'], json['name'], json['followers']['total'], json['genres'], json['popularity'])
