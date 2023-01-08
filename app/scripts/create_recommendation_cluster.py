import math
import os
from typing import List

import numpy as np
import utils
import pandas as pd
from api import tracks
from api.albums import get_albums
from api.artists import get_artists
from api.tracks import get_tracks_audio_features, get_tracks
from api.users import get_user_top_tracks
from domain.track import AudioFeatures
from recommendation.user_vector import UserVector
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pathlib
import time

token = os.environ['USER_TOKEN']
popularity_rate = float(os.environ['POPULARITY'])

FEATURE_NAMES = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
                 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature', 'popularity']
CAT_FEATURES = ['key', 'mode', 'time_signature']

scaler = MinMaxScaler()
beta = 0.9

FILE_NAME = 'features_with_popularity.pkl'


def get_similarities(cluster_vectors: pd.DataFrame, user_vector: UserVector):
    return cluster_vectors.apply(lambda row: cosine_similarity(row['vector'], user_vector.vec), axis=1)


def create_recommendations(cluster_vectors: pd.DataFrame, tracks_user: List[AudioFeatures]) -> \
        List[str]:
    tracks_user_df = pd.DataFrame(tracks_user, index=[t.track_id for t in tracks_user]).drop(['track_id'], axis=1)
    user_vector = UserVector(append_popularity(tracks_user_df), scaler)

    similarities = get_similarities(cluster_vectors, user_vector)
    clusters_with_similarities = cluster_vectors.assign(similarity=similarities)

    return clusters_with_similarities.sort_values('similarity', ascending=False).iloc[:1].iloc[0]['cluster']


def append_popularity(features: pd.DataFrame):
    ids = features.index
    chunked_ids = utils.split_into_chunks(ids, 50)
    d = {}
    fetched = 0
    all_tracks = len(ids)
    print('Fetching popularity...')
    for track_ids in chunked_ids:
        fetched_tracks = tracks.get_tracks(list(track_ids))
        for t_id, t in zip(track_ids, fetched_tracks):
            d[t_id] = t.popularity / 100
        fetched += len(track_ids)
        print(f'{(fetched / all_tracks * 100):.2f}% fetched')
    return pd.concat((features, pd.DataFrame(d.values(), index=d.keys(), columns=['popularity'])), axis=1)


def flatten(l):
    return [item for sublist in l for item in sublist]


def format_recommended_tracks(tracks: List):
    artists = [t.artists_ids for t in tracks]
    artists = flatten(artists)
    albums = [t.album_id for t in tracks]

    albums_fetched = []
    artists_fetched = []

    chunked_albums_ids = utils.split_into_chunks(albums, 20)
    chunked_artists_ids = utils.split_into_chunks(artists, 50)

    for albums_ids in chunked_albums_ids:
        albums_fetched.extend(get_albums(albums_ids))
    for artists_ids in chunked_artists_ids:
        artists_fetched.extend(get_artists(artists_ids))

    pathlib.Path('recommendations').mkdir(exist_ok=True)
    with open(f'./recommendations/recommendations-cluster-{time.strftime("%Y%m%d-%H%M%S")}.txt', "w") as output_file:
        output_file.write("Here are your recommendations!\n")
        for track in tracks:
            artist = ''
            for index, artist_id in enumerate(track.artists_ids):
                if index > 0:
                    artist += ', '
                artist += next(artist.name for artist in artists_fetched if artist.id == artist_id)
            album = next(album.name for album in albums_fetched if album.id == track.album_id)
            output_file.write(f'"{track.name}" by {artist} from album "{album}"\n')


def cluster_features(features: pd.DataFrame):
    n_clusters = math.floor(len(features) / 20)
    song_cluster_pipeline = Pipeline([('scaler', StandardScaler()),
                                      ('kmeans', KMeans(n_clusters=n_clusters,
                                                        verbose=False))
                                      ], verbose=False)

    X = features.select_dtypes(np.number)
    song_cluster_pipeline.fit(X)
    song_cluster_labels = song_cluster_pipeline.predict(X)
    features['cluster_label'] = song_cluster_labels
    return n_clusters, features


def build_vec(tracks):
    tracks = tracks.drop('title', axis=1)
    tracks = tracks.drop('cluster_label', axis=1)
    vec = tracks.to_numpy()
    vec_weighted = 0
    for t in range(1, vec.shape[0] + 1):
        vec_weighted = beta * vec_weighted + (1 - beta) * vec[t - 1]
    return vec_weighted.reshape(1, -1)


def get_clusters_vectors(clustered_features: pd.DataFrame, n_clusters: int):
    vectors = pd.DataFrame({'cluster': range(0, n_clusters)})
    vectors['vector'] = vectors.apply(lambda row: build_vec(clustered_features.loc[clustered_features['cluster_label']
                                                                                   == row.cluster]), axis=1)
    return vectors


def get_tracks_from_cluster(cluster_id: int, features: pd.DataFrame):
    tracks = features.loc[features['cluster_label'] == cluster_id].index.tolist()
    return get_tracks(tracks)


def main():
    user_tracks_ids = []
    user_tracks = get_user_top_tracks(token, 'medium_term')
    user_tracks_ids.extend([track['id'] for track in user_tracks])
    user_tracks_features = get_tracks_audio_features(user_tracks_ids)
    features_with_popularity = pd.read_pickle(FILE_NAME)
    features_with_popularity = features_with_popularity.loc[features_with_popularity['popularity'] >= popularity_rate]
    n_clusters, clustered_features = cluster_features(features_with_popularity)
    vectors = get_clusters_vectors(clustered_features, n_clusters)
    cluster_id = create_recommendations(vectors, user_tracks_features)
    recommendations_tracks = get_tracks_from_cluster(cluster_id, clustered_features)
    format_recommended_tracks(recommendations_tracks)


if __name__ == "__main__":
    main()
