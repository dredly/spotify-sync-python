from spotify_sync_app import app
from flask import redirect, request, url_for
from .config import AUTHORIZE_URL, CLIENT_ID, SCOPES, CLIENT_SECRET, TOKEN_URL, API_BASE_URL, USERS
import requests

# Health check to quickly verify if the API is running or not
@app.route("/")
def home():
    return {"marco": "polo"}

@app.route("/login", methods=["POST"])
def login():
    request_data: dict = request.get_json()
    username = request_data.get('username', None)
    password = request_data.get('password', None)
    if not username or not password:
        return {
            "error": "login credentials not provided"
        }, 401

    usernames = [u.split(":")[0] for u in USERS]
    passwords = [u.split(":")[1] for u in USERS]

    if not username in usernames or not password in passwords:
        return {
            "error": "invalid login credentials"
        }, 401

    if usernames.index(username) != passwords.index(password):
        return {
            "error": "invalid login credentials"
        }, 401

    return {
        "url": AUTHORIZE_URL 
            + "?response_type=code" 
            + "&client_id=" + CLIENT_ID
            + "&redirect_uri=" + url_for("callback", _external=True)
            + "&scope=" + SCOPES
    }
    # return redirect(AUTHORIZE_URL 
    #     + "?response_type=code" 
    #     + "&client_id=" + CLIENT_ID
    #     + "&redirect_uri=" + url_for("callback", _external=True)
    #     + "&scope=" + SCOPES
    # )

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

@app.route("/sync", methods=["POST"])
def sync():
    request_data: dict = request.get_json()
    token = request_data.get('token', None)
    if not token:
       return {"error": "token not provided"}, 401
    
    own_playlist_id = request_data.get('own_playlist_id', None)
    if not own_playlist_id:
        return {"error": "own_playlist_id not provided"}, 400
    
    external_playlist_id = request_data.get('external_playlist_id', None)
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
        return {"error": "could not add tracks to playlist"}, 400

    return {
        "success": "playlist synced"
    }  