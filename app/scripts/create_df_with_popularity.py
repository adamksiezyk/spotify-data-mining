import pandas as pd
import utils
from api import tracks
from db.gateway import TracksGateway

FILE_NAME = 'features_with_popularity.pkl'

tracks_gw = TracksGateway()
features = tracks_gw.fetch_all().dropna()


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


def main():
    features_with_popularity = append_popularity(features)
    features_with_popularity.to_pickle(FILE_NAME)


if __name__ == "__main__":
    main()
