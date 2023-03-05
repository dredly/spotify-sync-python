import os
from dotenv import load_dotenv

load_dotenv()

AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPES = "playlist-modify-private playlist-modify-public"
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:5001/callback" #TODO make this change dynamically in prod environment
API_BASE_URL = "https://api.spotify.com/v1/"
USERS = os.environ["USERS"].split(",")
