#import relevant modules and secret keys
import json
from flask import Flask, redirect, session, url_for
from authlib.integrations.flask_client import OAuth
from keys import secret_key_keys, client_id_keys, client_secret_keys

#create new Flask instance
app = Flask(__name__)
app.secret_key = secret_key_keys

#set up authentication with Spotify API with all relevant information
oauth = OAuth(app)
oauth.register(
   name = "spotify", client_id = client_id_keys, client_secret = client_secret_keys,
   authorize_url = "https://accounts.spotify.com/authorize",
   access_token_url = "https://accounts.spotify.com/api/token",
   api_base_url = "https://api.spotify.com/v1/",

   #add all needed scopes based on permissions
   client_kwargs={
       'scope': 'playlist-read-private user-top-read'
   }
)

#Home page
@app.route('/')
def index():
    try:
        token = session['spotify-token'] #retrieve token
    except KeyError:
        return redirect(url_for('login')) #redirect to login if session key isn't present
    data = oauth.spotify.get('me/top/tracks?limit=5', token=token).text
    return json.loads(data) #return user data

#Login page
@app.route('/login')
def login():
    redirect_uri = 'http://erikonsager.pythonanywhere.com/callback/'
    return oauth.spotify.authorize_redirect(redirect_uri) #authorize then redirect back to uri

#Redirect page
@app.route('/callback/')
def callback():
    token = oauth.spotify.authorize_access_token()
    session['spotify-token'] = token
    return redirect(url_for('index')) 

#run app
if __name__ == '__main__':
    app.run()