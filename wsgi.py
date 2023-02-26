import os
from spotify_sync_app import app

port = 5001

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

from spotify_sync_app import routes