import datetime as dt
import os

import pandas as pd
from dotenv import load_dotenv

from db import Table, Base
from db._connection.connection import Connection, connection_factory
from db.gateway.gateway import TracksGateway, ChartsGateway, ChartTracksGateway
from db.tables import Track, WeeklyChart, ChartTrack


def _create_tables(conn: Connection, base: Table) -> None:
    # Create DDL
    conn.create_ddl(base)


def _insert_tracks(gw: TracksGateway) -> None:
    # Insert tracks
    tracks_path = "../data/features_with_empty_artists.csv"
    df = pd.read_csv(tracks_path)
    tracks = [Track(**track[1].to_dict()) for track in df.iterrows()]
    gw.create_all(tracks)


def _insert_chart(gw: ChartsGateway) -> None:
    # Insert chart
    chart = WeeklyChart(country_code="global", date=dt.date(2016, 12, 23))
    gw.create(chart)


def _insert_chart_tracks(gw: ChartTracksGateway) -> None:
    # Insert chart tracks
    chart_path = "../data/global_2016-12-23-2016-12-30.csv"
    df = pd.read_csv(chart_path)
    df.drop(['title', 'artist'], axis=1, inplace=True)
    df['chart_id'] = 1
    chart_tracks = [ChartTrack(**track[1].to_dict()) for track in df.iterrows()]
    gw.create_all(chart_tracks)


def main() -> None:
    load_dotenv()
    conn_type = os.environ['DB_TYPE']
    db_addr = os.environ['DB_ADDRESS']
    db_port = os.environ['DB_PORT']
    db_name = os.environ['DB_NAME']
    db_user = os.environ['DB_USERNAME']
    db_password = os.environ['DB_PASSWORD']
    conn = connection_factory(conn_type, db_addr, db_port, db_name, db_user, db_password)

    tracks_gw = TracksGateway()
    charts_gw = ChartsGateway()
    chart_tracks_gw = ChartTracksGateway()

    # Init DB
    _create_tables(conn, Base)
    _insert_tracks(tracks_gw)
    _insert_chart(charts_gw)
    _insert_chart_tracks(chart_tracks_gw)

    tracks = chart_tracks_gw.fetch_all()
    print(tracks)


if __name__ == "__main__":
    main()