"""Rank catalog tracks for Playlist Intelligence requests."""

import re

from .recommender import recommend_songs


WORKOUT_MOODS = {
    "happy",
    "energizing",
    "intense",
    "aggressive",
    "playful",
    "uplifting",
}


def rank_request(request, songs):
    """Return ranked tracks for an upbeat workout request."""
    if not request.strip():
        raise ValueError(
            "Enter a playlist request, such as "
            "'3 upbeat songs for a workout'."
        )

    match = re.fullmatch(
        r"(?:give me )?(\d+) upbeat songs? for a workout",
        request.strip(),
        flags=re.IGNORECASE,
    )
    if match is None:
        raise ValueError(
            "Try a request like '3 upbeat songs for a workout'."
        )

    count = int(match.group(1))
    if not 1 <= count <= 10:
        raise ValueError("Request between 1 and 10 songs.")

    preferences = {
        "favorite_genre": "",
        "favorite_mood": "energizing",
        "target_energy": 0.90,
    }

    workout_tracks = [
        song
        for song in songs
        if song["energy"] >= 0.75
        and song["mood"].strip().casefold() in WORKOUT_MOODS
    ]

    return recommend_songs(preferences, workout_tracks, k=count)