"""Rank catalog tracks using retrieved activity guidance."""

import re

from .guide_retriever import retrieve_guide
from .recommender import recommend_songs


def read_workout_rules(guide_text):
    """Extract and validate the workout rules from the guide."""
    normalized_text = " ".join(guide_text.split())

    target_match = re.search(
        r"Target energy is ([0-9.]+)",
        normalized_text,
    )
    minimum_match = re.search(
        r"Minimum energy is ([0-9.]+)",
        normalized_text,
    )
    moods_match = re.search(
        r"Suitable mood tags are (.+?)\.",
        normalized_text,
    )

    if not all((target_match, minimum_match, moods_match)):
        raise ValueError(
            "The workout guide must define target energy, "
            "minimum energy, and suitable mood tags."
        )

    target_energy = float(target_match.group(1).rstrip("."))
    minimum_energy = float(minimum_match.group(1).rstrip("."))

    if not 0 <= minimum_energy <= target_energy <= 1:
        raise ValueError(
            "Workout energy rules must satisfy "
            "0 <= minimum energy <= target energy <= 1."
        )

    mood_text = re.sub(
        r"\band\b",
        ",",
        moods_match.group(1),
        flags=re.IGNORECASE,
    )
    suitable_moods = {
        mood.strip().casefold()
        for mood in mood_text.split(",")
        if mood.strip()
    }

    if not suitable_moods:
        raise ValueError("The workout guide must list suitable moods.")

    return target_energy, minimum_energy, suitable_moods


def rank_request(request, songs):
    """Retrieve workout guidance, filter tracks, and rank matches."""
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

    guide = retrieve_guide("workout")
    target_energy, minimum_energy, suitable_moods = read_workout_rules(
        guide["content"]
    )

    preferences = {
        "favorite_genre": "",
        "favorite_mood": "energizing",
        "target_energy": target_energy,
    }

    workout_tracks = [
        song
        for song in songs
        if song["energy"] >= minimum_energy
        and song["mood"].strip().casefold() in suitable_moods
    ]

    recommendations = recommend_songs(
        preferences,
        workout_tracks,
        k=count,
    )

    return [
        (
            song,
            score,
            (
                f"{explanation}; "
                f"workout guide match "
                f"(energy {song['energy']:.2f}, mood {song['mood']}); "
                f"source: {guide['source']}"
            ),
        )
        for song, score, explanation in recommendations
    ]