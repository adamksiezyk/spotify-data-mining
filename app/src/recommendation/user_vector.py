import numpy as np


class UserVector:
    def __init__(self, tracks, scaler, beta=0.9):
        # self.scaler = scaler
        self.beta = beta
        # self.popularity_col_idx = self._get_popularity_col_idx(tracks)
        self.vec = self.build_vec(tracks)

    def build_vec(self, tracks):
        vec = tracks.to_numpy()
        # vec = self.scaler.transform(vec)

        # Determine n_streams column number and remove it
        # vec = np.delete(vec, self.popularity_col_idx, 1)

        # EMA  
        vec_weighted = 0
        for t in range(1, vec.shape[0]+1):
            vec_weighted = self.beta*vec_weighted + (1-self.beta)*vec[t-1]  
                
        vec_weighted = vec_weighted.reshape(1, -1)

        return vec_weighted

    def add_track(self, track):
        track_vec = track.to_numpy().reshape(1, -1)
        # track_vec = self.scaler.transform(track_vec)

        # Determine n_streams column number and remove it
        # track_vec = np.delete(track_vec, self.popularity_col_idx, 1)

        self.vec = self.beta*self.vec + (1-self.beta)*track_vec

    def _get_popularity_col_idx(self, df):
        return np.nonzero(df.columns == 'n_streams')[0][0]