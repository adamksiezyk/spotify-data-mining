import requests

from api import NETWORK_EXCEPTIONS, token
from domain.track import Track, AudioFeatures
from utils import retry


@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def get_track(track_id: str, country_code: str = None) -> Track:
    json = requests.get(
        url=f'https://api.spotify.com/v1/tracks/{track_id}',
        params={'market': country_code},
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    return _create_track_from_json(json)


@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def get_tracks(tracks_ids: list[str], country_code: str = None) -> list[Track]:
    json = requests.get(
        url=f'https://api.spotify.com/v1/tracks',
        params={'market': country_code, 'ids': ','.join(tracks_ids)},
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    return [_create_track_from_json(j) for j in json['tracks']]


@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def get_track_audio_features(track_id: str) -> AudioFeatures:
    json = requests.get(
        url=f'https://api.spotify.com/v1/audio-features/{track_id}',
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    return _create_audio_features_from_json(json)


@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def get_tracks_audio_features(tracks_ids: list[str]) -> list[AudioFeatures]:
    json = requests.get(
        url=f'https://api.spotify.com/v1/audio-features/',
        params={'ids': ','.join(tracks_ids)},
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    return [_create_audio_features_from_json(j) for j in json['audio_features'] if j]


def _create_audio_features_from_json(json: dict):
    try:
        return AudioFeatures(json['id'], json['danceability'], json['energy'], json['key'], json['loudness'], json['mode'],
                         json['speechiness'], json['acousticness'], json['instrumentalness'], json['liveness'],
                         json['valence'], json['tempo'], json['duration_ms'], json['time_signature'])
    except Exception as e:
        print(e)
        print(json)


def _create_track_from_json(json: dict) -> Track:
    return Track(json['id'], json['name'], json.get('popularity'), json['explicit'], json.get('album', {}).get('id'),
                 [artist['id'] for artist in json['artists']], json['external_urls'].get('spotify'))
