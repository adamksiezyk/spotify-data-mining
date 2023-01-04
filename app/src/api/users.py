import requests

from domain.track import Track


def get_user_top_tracks(user_token: str, time_range: str) -> list[Track]:
    print(user_token)
    response = requests.get(
        url=f'https://api.spotify.com/v1/me/top/tracks',
        params={
            'limit': 50,
            'time_range': time_range
        },
        headers={
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json'
        }
    )
    json = response.json()
    return json['items']
