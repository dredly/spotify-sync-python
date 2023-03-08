import requests
from typing import List

from .config import API_BASE_URL

def get_external_track_uris(url: str, token: str, own_track_uris: List[str]):
    resp = requests.get(url, headers={
        "Authorization": "Bearer " + token
    })
    resp.raise_for_status()
    next_link = resp.json()["next"]
    external_track_items = resp.json()["items"]
    external_track_uris = (eti["track"]["uri"] for eti in external_track_items)
    track_uris_to_add = [etu for etu in external_track_uris if etu not in own_track_uris]
    if next_link:
        return track_uris_to_add + get_external_track_uris(next_link, token, own_track_uris)
    return track_uris_to_add