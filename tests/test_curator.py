"""Tests for playlist requests and workout filtering."""

import pytest

from src.curator import rank_request


def make_song(song_id, mood, energy):
    """Build a small catalog record for request tests."""
    return {
        "id": song_id,
        "title": f"Track {song_id}",
        "artist": f"Artist {song_id}",
        "genre": "pop",
        "mood": mood,
        "energy": energy,
    }


def test_workout_request_filters_mood_and_energy():
    """Exclude sad and low-energy tracks, then rank eligible tracks."""
    songs = [
        make_song(1, "sad", 0.90),
        make_song(2, "happy", 0.40),
        make_song(3, "intense", 0.91),
        make_song(4, "energizing", 0.88),
        make_song(5, "happy", 0.80),
    ]

    results = rank_request("Give me 3 upbeat songs for a workout", songs)

    assert [song["id"] for song, _, _ in results] == [4, 3, 5]


@pytest.mark.parametrize("playlist_request", ["", "   "])
def test_blank_request_is_rejected(playlist_request):
    """Reject empty or whitespace-only requests."""
    with pytest.raises(ValueError, match="Enter a playlist request"):
        rank_request(playlist_request, [])


@pytest.mark.parametrize("count", [0, 11])
def test_invalid_song_count_is_rejected(count):
    """Enforce the supported range of one to ten songs."""
    with pytest.raises(ValueError, match="between 1 and 10"):
        rank_request(f"{count} upbeat songs for a workout", [])


def test_unsupported_request_is_rejected():
    """Explain which request format is currently supported."""
    with pytest.raises(ValueError, match="Try a request"):
        rank_request("Find calm jazz for studying", [])