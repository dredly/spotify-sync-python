from spotify_sync_app import app
from flask import redirect
from .config import AUTHORIZE_URL, CLIENT_ID, REDIRECT_URI, SCOPES

# Health check to quickly verify if the API is running or not
@app.route("/")
def home():
    return {"marco": "polo"}

@app.route("/login")
def login():
    return redirect(AUTHORIZE_URL 
        + "?response_type=code" 
        + "&client_id=" + CLIENT_ID
        + "&redirect_uri=" + REDIRECT_URI
        + "&scope=" + SCOPES
    )

@app.route("/callback")
def callback():
    return {"callback": "success"}