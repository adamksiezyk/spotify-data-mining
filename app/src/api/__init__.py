import base64
import json
import os
import requests
from dotenv import load_dotenv

from utils import retry


NETWORK_EXCEPTIONS = (KeyError, json.decoder.JSONDecodeError, requests.exceptions.JSONDecodeError, requests.exceptions.ConnectionError)
token = None

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

@retry(times=3, exceptions=NETWORK_EXCEPTIONS)
def refresh_api_token():
    global token
    load_dotenv()
    authorization = f"Basic {base64.b64encode(bytes(f'{CLIENT_ID}:{CLIENT_SECRET}', 'utf-8')).decode('utf-8')}"
    response = requests.post(
        url='https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': authorization
        }
    )
    token = response.json()['access_token']


refresh_api_token()
