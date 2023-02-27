from spotify_sync_app import app
from flask import redirect, request, url_for
from .config import AUTHORIZE_URL, CLIENT_ID, SCOPES, CLIENT_SECRET, TOKEN_URL
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