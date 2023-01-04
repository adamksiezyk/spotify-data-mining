import base64

import requests
from api import CLIENT_ID, CLIENT_SECRET


def authorize(redirect_uri: str):
    response = requests.get(
        url=f'https://accounts.spotify.com/authorize',
        params={
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': 'user-top-read'
        }
    )
    return response.text


def get_access_token(code: str, redirect_uri: str) -> str:
    authorization = f"Basic {base64.b64encode(bytes(f'{CLIENT_ID}:{CLIENT_SECRET}', 'utf-8')).decode('utf-8')}"
    response = requests.post(
        url=f'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': authorization
        }
    )
    json = response.json()
    return json['access_token']
