import os
from spotify_sync_app import app

port = os.environ.get("port", 5001)

if __name__ == "__main__":
    app.run(port=port)

from spotify_sync_app import routes