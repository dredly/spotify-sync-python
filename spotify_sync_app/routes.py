from spotify_sync_app import app
from flask import redirect, request, url_for
from .config import AUTHORIZE_URL, CLIENT_ID, SCOPES, CLIENT_SECRET, TOKEN_URL, API_BASE_URL
import requests

# Health check to quickly verify if the API is running or not
@app.route("/")
def home():
    return {"marco": "polo"}

@app.route("/login")
def login():
    return redirect(AUTHORIZE_URL 
        + "?response_type=code" 
        + "&client_id=" + CLIENT_ID
        + "&redirect_uri=" + url_for("callback", _external=True)
        + "&scope=" + SCOPES
    )

@app.route("/callback")
def callback():
    auth_code = request.args.get('code', None)
    if not auth_code:
        return {"error": "could not find auth code"}, 401

    token_resp = requests.post(TOKEN_URL, {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": url_for("callback", _external=True)
        },
        auth=(CLIENT_ID, CLIENT_SECRET)
    )

    token_resp.raise_for_status()
    print(token_resp.json())
    return {
        "access_token": token_resp.json()["access_token"],
        "refresh_token": token_resp.json()["refresh_token"]
    }

@app.route("/sync")
def sync():
    token = request.args.get('token', None)
    if not token:
       return {"error": "token not provided"}, 401
    
    own_playlist_id = request.args.get('own_playlist_id', None)
    if not own_playlist_id:
        return {"error": "own_playlist_id not provided"}, 400
    
    external_playlist_id = request.args.get('external_playlist_id', None)
    if not external_playlist_id:
        return {"error": "external_playlist_id not provided"}, 400

    own_playlist_resp = requests.get(API_BASE_URL + "playlists/" + own_playlist_id, headers={
        "Authorization": "Bearer " + token
    })

    try:
        own_playlist_resp.raise_for_status()
    except requests.exceptions.HTTPError:
        return {"error": "own_playlist not found"}, 404

    external_playlist_resp = requests.get(API_BASE_URL + "playlists/" + external_playlist_id + "/tracks", headers={
        "Authorization": "Bearer " + token
    })

    try:
        external_playlist_resp.raise_for_status()
    except requests.exceptions.HTTPError:
        return {"error": "external_playlist not found"}, 404
    
    external_track_items = external_playlist_resp.json()["items"]
    external_track_uris = [eti["track"]["uri"] for eti in external_track_items]

    print({
        "uris": external_track_uris
    })

    add_to_playlist_resp =  requests.post(API_BASE_URL + "playlists/" + own_playlist_id + "/tracks", json={
        "uris": external_track_uris
    }, headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    })

    try:
        add_to_playlist_resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        return {"error": "could not add tracks to playlist"}, 400

    return {
        "external track uris": ",".join(external_track_uris)
    }  