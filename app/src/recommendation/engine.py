from typing import List

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

import utils
from api import tracks
from db.gateway import TracksGateway
from domain.track import AudioFeatures
from recommendation.user_vector import UserVector

FEATURE_NAMES = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
                 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']
CAT_FEATURES = ['key', 'mode', 'time_signature']
CAT_COLUMN_NAMES = ['key_0', 'key_1', 'key_2', 'key_3', 'key_4', 'key_5', 'key_6', 'key_7', 'key_8', 'key_9', 'key_10',
                    'key_11', 'mode_0', 'mode_1', 'time_signature_0', 'time_signature_1', 'time_signature_2',
                    'time_signature_3', 'time_signature_4', 'time_signature_5']

scaler = MinMaxScaler()

tracks_gw = TracksGateway()
features = tracks_gw.fetch_all().dropna()


def append_popularity(features: pd.DataFrame):
    # features['popularity'] = 0
    # return features
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


features_scaled = preprocess_features(features, fit_scaler=True)
features_scaled = append_popularity(features_scaled)


def get_similarities(user_vector: UserVector, popularity_rate: float = 0):
    popularity = features_scaled.popularity.to_numpy().reshape(-1, 1)
    features = features_scaled.drop(['popularity'], axis=1)

    audio_similarities = cosine_similarity(features, user_vector.vec)
    similarities = audio_similarities + popularity_rate * popularity

    return similarities


def create_recommendations(tracks_user: List[AudioFeatures], popularity_rate: float) -> List[str]:
    tracks_user_df = pd.DataFrame(tracks_user, index=[t.track_id for t in tracks_user]).drop(['track_id'], axis=1)
    user_vector = UserVector(preprocess_features(tracks_user_df), scaler)

    similarities = get_similarities(user_vector, popularity_rate)
    tracks_with_similarities = features_scaled.assign(similarity=similarities)

    # Drop tracks that are already there in user history
    # to not recommend what user listened to already
    tracks_with_similarities.drop(tracks_user_df.index, inplace=True, errors='ignore')

    top_recommendations = tracks_with_similarities.sort_values('similarity', ascending=False).iloc[:10]
    return [track_id for track_id in top_recommendations.index]
