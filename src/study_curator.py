"""Retrieve and rank songs for studying requests."""

import re

from .guide_retriever import retrieve_guide
from .recommender import recommend_songs


def rank_study_request(request, songs, *, allow_other_genres=False):
    """Rank studying tracks, optionally including other genres."""
    match = re.fullmatch(
        r"(?:give me )?(\d+) calm (.+?) songs? for studying",
        request.strip(),
        flags=re.IGNORECASE,
    )
    if match is None:
        raise ValueError(
            "Try a request like '3 calm jazz songs for studying'."
        )

    count = int(match.group(1))
    if not 1 <= count <= 10:
        raise ValueError("Request between 1 and 10 songs.")

    requested_genre = match.group(2).strip().casefold()
    known_genres = {
        song["genre"].strip().casefold()
        for song in songs
    }
    if requested_genre not in known_genres:
        raise ValueError(
            f"Unknown genre '{requested_genre}'. "
            f"Available genres: {', '.join(sorted(known_genres))}."
        )

    guide = retrieve_guide("studying")
    guide_text = " ".join(guide["content"].split())

    target_match = re.search(
        r"Target energy is ([0-9.]+)",
        guide_text,
    )
    maximum_match = re.search(
        r"Maximum energy is ([0-9.]+)",
        guide_text,
    )
    moods_match = re.search(
        r"Suitable mood tags are (.+?)\.",
        guide_text,
    )

    if not all((target_match, maximum_match, moods_match)):
        raise ValueError(
            "The studying guide must define target energy, "
            "maximum energy, and suitable mood tags."
        )

    target_energy = float(target_match.group(1).rstrip("."))
    maximum_energy = float(maximum_match.group(1).rstrip("."))

    if not 0 <= target_energy <= maximum_energy <= 1:
        raise ValueError("The studying guide has invalid energy rules.")

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
        raise ValueError("The studying guide must list suitable moods.")

    candidates = [
        song
        for song in songs
        if (
            allow_other_genres
            or song["genre"].strip().casefold() == requested_genre
        )
        and song["energy"] <= maximum_energy
        and song["mood"].strip().casefold() in suitable_moods
    ]

    prefer_instrumental = (
        "prefer instrumental tracks when other preferences are equal."
        in guide_text.casefold()
    )

    if prefer_instrumental:
        # The shared ranker preserves input order for equal scores.
        # Preordering candidates therefore supplies the tie-break rule.
        candidates.sort(
            key=lambda song: song.get("instrumentalness", 0.0),
            reverse=True,
        )

    preferences = {
        "favorite_genre": requested_genre,
        "favorite_mood": "focused",
        "target_energy": target_energy,
    }

    recommendations = recommend_songs(
        preferences,
        candidates,
        k=count,
    )

    results = []

    for song, score, explanation in recommendations:
        if song["genre"].strip().casefold() == requested_genre:
            genre_status = "requested genre"
        else:
            genre_status = "approved alternative genre"

        instrumental_evidence = ""
        if prefer_instrumental:
            instrumental_evidence = (
                f"instrumentalness {song.get('instrumentalness', 0.0):.2f} "
                "(tie-break preference); "
            )

        results.append(
            (
                song,
                score,
                f"{explanation}; studying guide match "
                f"(energy {song['energy']:.2f}, mood {song['mood']}); "
                f"{instrumental_evidence}"
                f"genre status: {genre_status}; "
                f"source: {guide['source']}",
            )
        )

    return results