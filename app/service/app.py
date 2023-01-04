import os
import uuid

from flask import Flask, request, redirect, send_from_directory

from api import CLIENT_ID
from api.artists import get_artists
from api.auth import get_access_token
from api.tracks import get_tracks_audio_features, get_tracks
from api.users import get_user_top_tracks
from domain.track import Track
from recommendation.engine import create_recommendations

app = Flask(__name__)

SERVER_HOST = os.environ['SERVER_HOST']

REDIRECT_URI = f'http://{SERVER_HOST}:8080/recommendations'
states = {}


def authorize_redirect(state):
    return f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&' \
           f'redirect_uri={REDIRECT_URI}&state={state}&scope=user-top-read'


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    params = request.args
    if 'code' not in params:
        time_range = params.get('time_range', 'medium_term')
        popularity_rate = float(params.get('popularity_rate', '0'))
        state = str(uuid.uuid4())
        states[state] = time_range, popularity_rate
        return redirect(authorize_redirect(state))
    time_range, popularity_rate = states[params['state']]
    token = get_access_token(params['code'], REDIRECT_URI)
    user_tracks = get_user_top_tracks(token, time_range)
    user_tracks_ids = [track['id'] for track in user_tracks]
    user_tracks_features = get_tracks_audio_features(user_tracks_ids)
    recommendations_ids = create_recommendations(user_tracks_features, popularity_rate)
    recommendations_tracks = get_tracks(recommendations_ids)
    return format_response(recommendations_tracks)


def format_response(user_tracks: list):
    return {'tracks': user_tracks}


def format_track(track: Track) -> str:
    artist_names = [a.name for a in get_artists(track.artists_ids)]
    return f"{', '.join(artist_names)} - {track.name} {track.id}"


@app.route('/notebooks/<path:path>')
def send_report(path):
    return send_from_directory('../data/outputs', path)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
