"""Verify studying constraints and approved genre broadening."""

import pytest

from src.study_curator import rank_study_request


@pytest.fixture
def study_songs():
    """Provide eligible tracks and deliberately unsuitable candidates."""
    return [
        {
            "id": 1,
            "title": "Calm Jazz",
            "artist": "Artist A",
            "genre": "jazz",
            "mood": "relaxed",
            "energy": 0.37,
        },
        {
            "id": 2,
            "title": "Focused Lofi",
            "artist": "Artist B",
            "genre": "lofi",
            "mood": "focused",
            "energy": 0.40,
        },
        {
            "id": 3,
            "title": "High Energy Jazz",
            "artist": "Artist C",
            "genre": "jazz",
            "mood": "relaxed",
            "energy": 0.90,
        },
        {
            "id": 4,
            "title": "Sad Jazz",
            "artist": "Artist D",
            "genre": "jazz",
            "mood": "sad",
            "energy": 0.30,
        },
        {
            "id": 5,
            "title": "High Energy Lofi",
            "artist": "Artist E",
            "genre": "lofi",
            "mood": "focused",
            "energy": 0.85,
        },
        {
            "id": 6,
            "title": "Sad Lofi",
            "artist": "Artist F",
            "genre": "lofi",
            "mood": "sad",
            "energy": 0.30,
        },
    ]


def test_exact_search_preserves_genre_mood_and_energy(study_songs):
    """Only the eligible jazz track passes the exact search."""
    results = rank_study_request(
        "3 calm jazz songs for studying",
        study_songs,
    )

    assert [song["id"] for song, _, _ in results] == [1]


def test_broadening_preserves_mood_and_energy(study_songs):
    """Approval relaxes genre while retaining the other restrictions."""
    results = rank_study_request(
        "3 calm jazz songs for studying",
        study_songs,
        allow_other_genres=True,
    )

    assert [song["id"] for song, _, _ in results] == [1, 2]
    assert "requested genre" in results[0][2]
    assert "approved alternative genre" in results[1][2]


def test_unknown_genre_is_rejected(study_songs):
    """Explain when the requested genre is absent from the catalog."""
    with pytest.raises(ValueError, match="Unknown genre"):
        rank_study_request(
            "3 calm imaginary songs for studying",
            study_songs,
        )


@pytest.mark.parametrize("count", [0, 11])
def test_invalid_studying_count_is_rejected(study_songs, count):
    """Apply the supported count range to studying requests."""
    with pytest.raises(ValueError, match="between 1 and 10"):
        rank_study_request(
            f"{count} calm jazz songs for studying",
            study_songs,
        )


def test_no_eligible_tracks_returns_empty_result(study_songs):
    """Handle an existing genre whose tracks fail the activity rules."""
    unsuitable_tracks = [
        song for song in study_songs if song["id"] in {3, 4}
    ]

    results = rank_study_request(
        "3 calm jazz songs for studying",
        unsuitable_tracks,
    )

    assert results == []


def test_instrumental_preference_breaks_ties_after_relevance():
    """Prefer instrumentalness among equal scores before truncating."""
    songs = [
        {
            "id": 1,
            "title": "Lower Instrumentalness",
            "artist": "Artist A",
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "instrumentalness": 0.10,
        },
        {
            "id": 2,
            "title": "Higher Instrumentalness",
            "artist": "Artist B",
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "instrumentalness": 0.90,
        },
        {
            "id": 3,
            "title": "Stronger Mood Match",
            "artist": "Artist C",
            "genre": "lofi",
            "mood": "focused",
            "energy": 0.35,
            "instrumentalness": 0.00,
        },
    ]

    results = rank_study_request(
        "2 calm lofi songs for studying",
        songs,
    )

    assert [song["id"] for song, _, _ in results] == [3, 2]
    assert results[0][1] > results[1][1]
    assert "instrumentalness 0.90" in results[1][2]