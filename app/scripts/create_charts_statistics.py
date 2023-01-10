import logging
import os
import pandas as pd
from itertools import chain
from processing import create_chart_statistics, get_charts, get_chart_tracks, get_tracks_with_genres


logging.config.fileConfig(fname=os.environ['LOG_CONF'])
logger = logging.getLogger("scripts")


def main():
    df_tracks = get_chart_tracks().merge(get_tracks_with_genres(), left_on='track_id', right_index=True)

    df_charts = get_charts()[['date']]
    for date, charts in df_charts.groupby('date'):
        logger.info(f"Procesing charts from {date} ")
        grp = charts.merge(df_tracks, left_index=True, right_on='chart_id') \
            .groupby('chart_id')
        df_mean = grp.mean().reset_index()
        df_stats = df_mean[['chart_id']].copy()
        df_stats['mean_danceability'] = df_mean['danceability']
        df_stats['mean_energy'] = df_mean['energy']
        df_stats['mode_key'] = grp['key'].agg(lambda x: x.mode()[0]).reset_index(drop=True)
        df_stats['mean_loudness'] = df_mean['loudness']
        df_stats['mean_mode'] = df_mean['mode']
        df_stats['mean_speechiness'] = df_mean['speechiness']
        df_stats['mean_acousticness'] = df_mean['acousticness']
        df_stats['mean_instrumentalness'] = df_mean['instrumentalness']
        df_stats['mean_liveness'] = df_mean['liveness']
        df_stats['mean_valence'] = df_mean['valence']
        df_stats['mean_tempo'] = df_mean['tempo']
        df_stats['mean_duration_ms'] = df_mean['duration_ms']
        df_stats['mode_time_signature'] = grp['time_signature'].agg(lambda x: x.mode()[0]).reset_index(drop=True)
        df_stats['mode_genre'] = grp['genres'].agg(lambda x: pd.Series(list(chain.from_iterable(x.values))).mode()[0]).reset_index(drop=True)
        create_chart_statistics(df_stats)


if __name__ == "__main__":
    main()
