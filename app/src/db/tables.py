import sqlalchemy.orm
import sqlalchemy.schema

from db import Base


class WeeklyChart(Base):
    __tablename__ = "weekly_charts"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    country_code = sqlalchemy.Column(sqlalchemy.VARCHAR(2),
                                     sqlalchemy.ForeignKey("countries.id"))
    # country = sqlalchemy.orm.relationship("Country", lazy="joined")
    date = sqlalchemy.Column(sqlalchemy.Date)
    # tracks = sqlalchemy.orm.relationship("ChartTrack", lazy="joined")


class Country(Base):
    __tablename__ = "countries"

    id = sqlalchemy.Column(sqlalchemy.VARCHAR(2), primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)


class ChartTrack(Base):
    __tablename__ = "chart_tracks"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    chart_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("weekly_charts.id"))
    position = sqlalchemy.Column(sqlalchemy.Integer)
    track_id = sqlalchemy.Column(sqlalchemy.VARCHAR(22),
                                 sqlalchemy.ForeignKey("tracks.id"))
    # track = sqlalchemy.orm.relationship("Track", lazy="joined")
    n_streams = sqlalchemy.Column(sqlalchemy.Integer)


class Artist(Base):
    __tablename__ = "artists"

    id = sqlalchemy.Column(sqlalchemy.VARCHAR(length=22), primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    followers = sqlalchemy.Column(sqlalchemy.Integer)
    genres = sqlalchemy.Column(sqlalchemy.JSON)
    popularity = sqlalchemy.Column(sqlalchemy.Integer)


class TrackArtist(Base):
    __tablename__ = "track_artists"
    __table_args__ = (
        sqlalchemy.schema.UniqueConstraint("track_id", "artist_id", name="unique_track_artist"),
    )

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    track_id = sqlalchemy.Column(sqlalchemy.ForeignKey("tracks.id"))
    artist_id = sqlalchemy.Column(sqlalchemy.ForeignKey("artists.id"))


class Track(Base):
    __tablename__ = "tracks"

    id = sqlalchemy.Column(sqlalchemy.VARCHAR(length=22), primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    # artists = sqlalchemy.orm.relationship("Artist", secondary=track_artists)
    danceability = sqlalchemy.Column(sqlalchemy.Float)
    energy = sqlalchemy.Column(sqlalchemy.Float)
    key = sqlalchemy.Column(sqlalchemy.Float)
    loudness = sqlalchemy.Column(sqlalchemy.Float)
    mode = sqlalchemy.Column(sqlalchemy.Float)
    speechiness = sqlalchemy.Column(sqlalchemy.Float)
    acousticness = sqlalchemy.Column(sqlalchemy.Float)
    instrumentalness = sqlalchemy.Column(sqlalchemy.Float)
    liveness = sqlalchemy.Column(sqlalchemy.Float)
    valence = sqlalchemy.Column(sqlalchemy.Float)
    tempo = sqlalchemy.Column(sqlalchemy.Float)
    duration_ms = sqlalchemy.Column(sqlalchemy.Float)
    time_signature = sqlalchemy.Column(sqlalchemy.Float)
