import os
from typing import List

import utils
import pandas as pd
from api import tracks
from api.albums import get_albums
from api.artists import get_artists
from api.tracks import get_tracks_audio_features, get_tracks
from api.users import get_user_top_tracks
from domain.track import AudioFeatures
from recommendation.user_vector import UserVector
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import pathlib
import time

token = os.environ['USER_TOKEN']
popularity_rate = float(os.environ['POPULARITY'])

FEATURE_NAMES = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
                 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature', 'popularity']
CAT_FEATURES = ['key', 'mode', 'time_signature']
CAT_COLUMN_NAMES = ['key_0', 'key_1', 'key_2', 'key_3', 'key_4', 'key_5', 'key_6', 'key_7', 'key_8', 'key_9', 'key_10',
                    'key_11', 'mode_0', 'mode_1', 'time_signature_0', 'time_signature_1', 'time_signature_2',
                    'time_signature_3', 'time_signature_4', 'time_signature_5']

scaler = MinMaxScaler()

FILE_NAME = 'features_with_popularity.pkl'
VOL_MOUNT = "/recommendation"


def preprocess_features(features_df: pd.DataFrame, fit_scaler=False) -> pd.DataFrame:
    features_df = features_df[FEATURE_NAMES]
    for cat_feature in CAT_FEATURES:
        dummies = pd.get_dummies(features_df[cat_feature], prefix=cat_feature)
        features_df = pd.concat([features_df, dummies], axis=1)
    for col in CAT_COLUMN_NAMES:
        if not any([c.startswith(col) for c in features_df.columns]):
            features_df[col] = 0
    features_df = features_df.drop(columns=CAT_FEATURES)
    if fit_scaler:
        scaler.fit(features_df.to_numpy())
    features_df_scaled = pd.DataFrame(scaler.transform(features_df.to_numpy()),
                                      columns=features_df.columns,
                                      index=features_df.index)
    return features_df_scaled


def get_similarities(features_scaled: pd.DataFrame, user_vector: UserVector, popularity_rate: float = 0):
    popularity = features_scaled.popularity.to_numpy().reshape(-1, 1)

    audio_similarities = cosine_similarity(features_scaled, user_vector.vec)
    similarities = audio_similarities + popularity_rate * popularity

    return similarities


def create_recommendations(features_scaled: pd.DataFrame, tracks_user: List[AudioFeatures], popularity_rate: float) -> \
        List[str]:
    tracks_user_df = pd.DataFrame(tracks_user, index=[t.track_id for t in tracks_user]).drop(['track_id'], axis=1)
    user_vector = UserVector(preprocess_features(append_popularity(tracks_user_df)), scaler)

    similarities = get_similarities(features_scaled, user_vector, popularity_rate)
    tracks_with_similarities = features_scaled.assign(similarity=similarities)

    # Drop tracks that are already there in user history
    # to not recommend what user listened to already
    tracks_with_similarities.drop(tracks_user_df.index, inplace=True, errors='ignore')

    top_recommendations = tracks_with_similarities.sort_values('similarity', ascending=False).iloc[:10]
    return [track_id for track_id in top_recommendations.index]


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

    artists_fetched = get_artists(artists)
    albums_fetched = get_albums(albums)

    pathlib.Path('recommendations').mkdir(exist_ok=True)
    with open(f'{VOL_MOUNT}/recommendations-{time.strftime("%Y%m%d-%H%M%S")}.txt', "w") as output_file:
        output_file.write("Here are your recommendations!\n")
        for track in tracks:
            artist = ''
            for index, artist_id in enumerate(track.artists_ids):
                if index > 0:
                    artist += ', '
                artist += next(artist.name for artist in artists_fetched if artist.id == artist_id)
            album = next(album.name for album in albums_fetched if album.id == track.album_id)
            output_file.write(f'"{track.name}" by {artist} from album "{album}"\n')


def main():
    user_tracks_ids = []
    user_tracks = get_user_top_tracks(token, 'medium_term')
    user_tracks_ids.extend([track['id'] for track in user_tracks])
    user_tracks_features = get_tracks_audio_features(user_tracks_ids)
    features_with_popularity = pd.read_pickle(f'{VOL_MOUNT}/{FILE_NAME}')
    features_scaled = preprocess_features(features_with_popularity, fit_scaler=True)
    recommendations_ids = create_recommendations(features_scaled, user_tracks_features, popularity_rate)
    recommendations_tracks = get_tracks(recommendations_ids)
    format_recommended_tracks(recommendations_tracks)


if __name__ == "__main__":
    main()
