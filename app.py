import urllib.parse, urllib.request, urllib.error, json, requests, pprint

# Obtaining access token from Spotify
from keys import client_id, secret_id
url = 'https://accounts.spotify.com/api/token'

access = requests.post(url, {'grant_type': 'client_credentials', 'client_id': client_id, 'secret_id': secret_id}).json()['access_token']

# Accessing API
baseurl = 'https://api.spotify.com/v1'