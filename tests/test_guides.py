"""Tests for guide retrieval and its effect on recommendations."""

import pytest

from src.curator import rank_request, read_workout_rules
from src.guide_retriever import retrieve_guide


def test_workout_guide_has_source_and_content():
    """Retrieve the workout section with its source reference."""
    guide = retrieve_guide("workout")

    assert guide["source"] == "data/curation_guides.md#workout"
    assert "Minimum energy is 0.75" in guide["content"]
    assert "Maximum energy" not in guide["content"]


def test_unknown_activity_is_rejected():
    """Explain when the document has no matching section."""
    with pytest.raises(ValueError, match="No guide found"):
        retrieve_guide("swimming")


@pytest.mark.parametrize(
    "guide_text",
    [
        "",
        "Target energy is 0.90.",
        (
            "Target energy is 0.90. "
            "Minimum energy is 0.95. "
            "Suitable mood tags are happy."
        ),
        (
            "Target energy is 1.20. "
            "Minimum energy is 0.75. "
            "Suitable mood tags are happy."
        ),
    ],
)
def test_invalid_guide_rules_are_rejected(guide_text):
    """Reject missing rules and invalid energy ranges."""
    with pytest.raises(ValueError):
        read_workout_rules(guide_text)


def test_guide_threshold_changes_recommendations(monkeypatch):
    """A stricter retrieved threshold removes lower-energy tracks."""
    songs = [
        {
            "id": 1,
            "title": "Lower Energy",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.80,
        },
        {
            "id": 2,
            "title": "Higher Energy",
            "artist": "Artist B",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.95,
        },
    ]
    guide = retrieve_guide("workout")

    monkeypatch.setattr(
        "src.curator.retrieve_guide",
        lambda activity: guide,
    )
    original_results = rank_request(
        "2 upbeat songs for a workout", songs
    )

    stricter_guide = {
        **guide,
        "content": guide["content"].replace(
            "Minimum energy is 0.75",
            "Minimum energy is 0.90",
        ),
    }
    monkeypatch.setattr(
        "src.curator.retrieve_guide",
        lambda activity: stricter_guide,
    )
    stricter_results = rank_request(
        "2 upbeat songs for a workout", songs
    )

    assert {song["id"] for song, _, _ in original_results} == {1, 2}
    assert [song["id"] for song, _, _ in stricter_results] == [2]