import requests
from typing import List

from .config import CHUNK_SIZE

def get_own_track_uris(url: str, token: str) -> List[str]:
    resp = requests.get(url, headers={
        "Authorization": "Bearer " + token
    })
    resp.raise_for_status()
    next_link = resp.json()["next"]
    own_track_items = resp.json()["items"]
    own_track_uris = [oti["track"]["uri"] for oti in own_track_items]
    if next_link:
        return own_track_uris + get_own_track_uris(next_link, token)
    return own_track_uris

def get_external_track_uris(url: str, token: str, own_track_uris: List[str]) -> List[str]:
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

def sync_tracks(url: str, token: str, track_uris: List[str]) -> None:
    tracks_chunked = [track_uris[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE] for i in range((len(track_uris) + CHUNK_SIZE - 1) // CHUNK_SIZE )]
    for chunk in tracks_chunked:
        resp = requests.post(url, headers={
            "Authorization": "Bearer " + token
        }, json={
            "uris": chunk
        })
        resp.raise_for_status()