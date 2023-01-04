import ast
import os
from time import sleep

import pandas as pd

from api import refresh_api_token
from api.albums import get_album_async
from api.artists import get_artists_async, get_artists
from api.tracks import get_tracks_audio_features, get_tracks
from domain.album import Album
from domain.artist import Artist


# Basic examples

# print(get_track('7ouMYWpwJ422jRcDASZB7P', 'US'))
# print(get_tracks(['7ouMYWpwJ422jRcDASZB7P', '4VqPOruhp5EdPBeR92t6lQ', '2takcwOaAZWiXQijPHIx7B'], 'US'))
# print(get_track_audio_features('7ouMYWpwJ422jRcDASZB7P'))
# print(get_tracks_audio_features(['7ouMYWpwJ422jRcDASZB7P', '4VqPOruhp5EdPBeR92t6lQ', '2takcwOaAZWiXQijPHIx7B']))
# print()
# print(get_album('4aawyAB9vmqN3uQ7FjRGTy', 'US'))
# print(get_albums(['382ObEPsp2rxGrnsizN5TX', '1A2GTWGtFfWp7KSQTwWOyo', '2noRn2Aes5aoNVsU6iWThc'], 'US'))
# print(get_album_tracks('4aawyAB9vmqN3uQ7FjRGTy', 'US'))
# print()
# print(get_artist('0TnOYISbd1XYRBk9myaseg'))
# print(get_artists(['2CIMQHirSU0MQqyYHq0eOx', '57dN52uHvrHOxijzpIgu3E', '1vCWHaC5f2uS3yhpwWbIA6']))
# print(get_artist_albums('0TnOYISbd1XYRBk9myaseg'))
# print(get_artist_top_tracks('0TnOYISbd1XYRBk9myaseg', 'US'))
# print(get_related_artists('0TnOYISbd1XYRBk9myaseg'))

def get_ids() -> list[str]:
    """fetches all track ids from charts (possible improvement - caching ids in separate file)"""
    data_root_dir = 'data/scraped_data'
    all_files = [f'{dir_name}/{file}' for dir_name, _, files in os.walk(data_root_dir) for file in files]
    all_ids = set()
    for file_name in all_files:
        df = pd.read_csv(file_name, sep=';')
        all_ids.update(df['track_id'])
    return list(all_ids)


def fetch_features():
    """fetches all features for tracks returned by get_ids()
    does not fetch data other than those from GET /v1/audio-features"""
    all_ids = get_ids()
    chunk_size = 100
    chunked_list = [all_ids[i:i + chunk_size] for i in range(0, len(all_ids), chunk_size)]
    all_features = []
    for chunk in chunked_list:
        all_features += get_tracks_audio_features(chunk)
    all_features = [vars(features) for features in all_features]
    pd.DataFrame(all_features).to_csv('data/features.csv', index=False)


# this is a mutable holder for fetched values and callback functions used by asynchronous calls
# turned out to be a bad idea, because asynchronous calls were too fast and caused request rate exceeded error
values = {'track_id': [], 'artists': [], 'album': [], 'artists_genres': [], 'album_genres': []}


def clear_values():
    values['track_id'] = []
    values['album'] = []
    values['album_genres'] = []
    values['artists'] = []
    values['artists_genres'] = []


def append_album(album: Album):
    values['album'].append(album.name)
    values['album_genres'].append(album.genres)


def append_artists(artists: list[Artist]):
    values['artists'].append([a.name for a in artists])
    values['artists_genres'].append([g for a in artists for g in a.genres])


def add_artists_to_features():
    features = pd.read_csv('data/features.csv')
    artists = pd.read_csv('data/artists.csv')
    tracks = pd.read_csv('data/tracks.csv')

    artists_ids = {}
    for _, t in tracks.iterrows():
        artists_ids[t['id']] = ast.literal_eval(t['artists_ids'])[0]

    artists_names = {}
    for _, t in artists.iterrows():
        artists_names[t['id']] = t['name']
    print(artists_names)

    names = pd.Series([artists_names.get(artists_ids.get(track_id, ""), "") for track_id in features['track_id']])
    print(names)

    features['artist'] = names
    features.to_csv('data/features.csv', index=False)


def aggregate_albums():
    data_root_dir = 'data/albums'
    all_files = [f'{dir_name}/{file}' for dir_name, _, files in os.walk(data_root_dir) for file in files]
    pd.concat([pd.read_csv(f) for f in all_files]).to_csv('data/albums.csv', index=False)


# IMPORTANT: chunk sizes cannot be larger than API limits


def fetch_artists():
    """function to fetch all artists which are listed in previously fetched tracks
    assumes that file data/tracks.csv exists"""
    chunks_to_skip = set(int(f.split('.')[0]) for f in os.listdir('data/artists'))
    tracks = pd.read_csv('data/tracks.csv')
    artists_ids = set()
    for s in tracks['artists_ids']:
        artists_ids.update(ast.literal_eval(s))
    artists_ids = list(artists_ids)
    chunk_size = 20
    chunked_ids = [artists_ids[i:i + chunk_size] for i in range(0, len(artists_ids), chunk_size)]
    for i, chunk in enumerate(chunked_ids):
        if i in chunks_to_skip:
            print(f'skipping chunk {i}')
            continue
        print(f'chunk {i}')
        fetched_tracks = get_artists(chunk)
        pd.DataFrame([vars(track) for track in fetched_tracks]).to_csv(f'data/artists/{i}.csv', index=False)


def fetch_tracks():
    chunks_to_skip = set(int(f.split('.')[0]) for f in os.listdir('data/tracks'))
    all_ids = get_ids()
    print('fetching')
    chunk_size = 50
    chunked_list = [all_ids[i:i + chunk_size] for i in range(0, len(all_ids), chunk_size)]
    for i, track_ids in enumerate(chunked_list):
        if i in chunks_to_skip:
            print(f'skipping chunk {i}')
            continue
        print(f'chunk {i}')
        fetched_tracks = get_tracks(track_ids)
        pd.DataFrame([vars(track) for track in fetched_tracks]).to_csv(f'data/tracks/{i}.csv', index=False)


# code that fetches genres asynchronously
# as mentioned before not the best idea, just leaving it as a reference
def fetch_genres():
    chunks_to_skip = set(int(f.split('.')[0]) for f in os.listdir('data/tracks'))
    all_ids = get_ids()
    chunk_size = 50
    chunked_list = [all_ids[i:i + chunk_size] for i in range(0, len(all_ids), chunk_size)]
    for i, track_ids in enumerate(chunked_list):
        if i in chunks_to_skip:
            print(f'skipping chunk {i}')
            continue
        try:
            print(f'chunk {i}')
            threads = []
            for track in get_tracks(track_ids):
                values['track_id'].append(track.id)
                threads.append(get_album_async(track.album_id, callback=append_album))
                threads.append(get_artists_async(track.artists_ids, callback=append_artists))
            sleep(0.2)
            for t in threads:
                t.join()
            pd.DataFrame(values).to_csv(f'data/genres/{i}.csv', index=False)
            clear_values()
        except Exception:
            print(f'chunk {i} failed')
            refresh_api_token()
            sleep(1)
    print(len(values['track_id']), len(values['album']), len(values['artists']))
    pd.DataFrame(values).to_csv('data/genres.csv', index=False)
