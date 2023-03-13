# Referenced for accessing Spotify's API through OAuth: 
# Day 18 slides, Professors Sean Munson and Sayamindu Dasgupta

# import relevant modules and secret keys
from flask import Flask, redirect, session, url_for, render_template
from authlib.integrations.flask_client import OAuth
from keys import secret_key_keys, client_id_keys, client_secret_keys

# create new Flask instance, set secret key
app = Flask(__name__)
app.secret_key = secret_key_keys

# set up authentication with Spotify API with all relevant information
oauth = OAuth(app)
oauth.register(
    name="spotify", 
    client_id=client_id_keys, 
    client_secret=client_secret_keys,
    authorize_url="https://accounts.spotify.com/authorize",
    access_token_url="https://accounts.spotify.com/api/token", #set 3 base urls for accessing the API
    api_base_url="https://api.spotify.com/v1/",
    client_kwargs={
        'scope': 'user-top-read playlist-modify-public' #access user's top songs/artists and the ability to make playlists
    }
)

# define home page
@app.route('/')
def index():
    if "spotify-token" in session:
        return redirect(url_for("summary")) #redirect to summary if already logged in
    return render_template("index.html") #otherwise render home page

# define login
@app.route('/login')
def login():
    return oauth.spotify.authorize_redirect('http://localhost:5000/authorize') #initiate authorization process

# define authorization/redirect
@app.route('/authorize')
def authorize():
    session['spotify-token'] = oauth.spotify.authorize_access_token() #retrieve access token from Spotify
    return redirect(url_for('index')) #return to index (which if successfully logged in, redirects to summary)

# define data summary page
@app.route("/summary")
def summary():
    token = session.get("spotify-token", None)
    if token is None:
        return redirect(url_for("login")) #if not logged in, redirect to login
    
    # retrieve the top 5 tracks, artists, and recommendations for authenticated user with token
    tracks = oauth.spotify.get("me/top/tracks?limit=5", token=token).json()["items"] # top 5 tracks
    artists = oauth.spotify.get("me/top/artists?limit=5", token=token).json()["items"] # top 5 artists
    rec_tracks = oauth.spotify.get("recommendations?seed_tracks={}".format(",".join([t["id"] for t in tracks])), token=token).json()["tracks"] # recommendations from top 5 tracks

    return render_template("summary.html", tracks=tracks, artists=artists, rec_tracks=rec_tracks[:5]) #render summary page with relevant info

#define playlist creation
@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    token = session.get("spotify-token", None)
    if token is None:
        return redirect(url_for("login")) #if not logged in, redirect to login
    
    # get top track ids
    tracks = oauth.spotify.get("me/top/tracks?limit=5", token=token).json()["items"] # top 5 tracks
    rec_tracks = oauth.spotify.get("recommendations?seed_tracks={}".format(",".join([t["id"] for t in tracks])), token=token).json()["tracks"] # recommendations from top 5 tracks
    user_data = oauth.spotify.get("me", token=token).json() #get user data

    # create playlist with name and description
    playlist = oauth.spotify.post(f"users/{user_data['id']}/playlists", json={
        "name": "STTA Recommendations",
        "description": "A playlist of recommended tracks, made by Spotify Top Tracks Analyzer",
        "public": True
         }, token=token).json()
    
    # add recommended tracks to playlist
    oauth.spotify.post(f"playlists/{playlist['id']}/tracks", json={
        "uris": [t["uri"] for t in rec_tracks]
    }, token=token)

    return redirect(url_for('summary')) #stay on summary page

#run app
if __name__ == '__main__':
    app.run()

    