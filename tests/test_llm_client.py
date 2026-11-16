"""Test model-output validation and network errors without API calls."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from httpx2 import ConnectError

from src.llm_client import generate_explanations


@pytest.fixture
def model_setup(monkeypatch):
    """Provide a simulated Gemini client and sample retrieved evidence."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "test-model")

    client = MagicMock()
    client.__enter__.return_value = client

    monkeypatch.setattr(
        "src.llm_client.genai.Client",
        MagicMock(return_value=client),
    )

    recommendations = [
        (
            {
                "id": 11,
                "title": "Neon Tide",
                "artist": "Crystal Harbor",
                "genre": "electronic",
                "mood": "energizing",
                "energy": 0.88,
            },
            1.98,
            "mood match and energy similarity",
        )
    ]
    guide = {
        "activity": "Workout",
        "content": "Target energy is 0.90. Minimum energy is 0.75.",
        "source": "data/curation_guides.md#workout",
    }

    return client, recommendations, guide


def test_valid_response_preserves_track_and_score(model_setup):
    """Accept a valid explanation and attach its evidence references."""
    client, recommendations, guide = model_setup
    client.models.generate_content.return_value = SimpleNamespace(
        text=json.dumps(
            [
                {
                    "id": 11,
                    "explanation": (
                        "Its energizing mood and energy of 0.88 "
                        "fit your workout."
                    ),
                }
            ]
        )
    )

    results = generate_explanations(
        "Give me 1 upbeat song for a workout",
        recommendations,
        guide,
    )

    song, score, explanation = results[0]
    assert song == recommendations[0][0]
    assert score == 1.98
    assert "energy of 0.88" in explanation
    assert guide["source"] in explanation
    assert "catalog ID: 11" in explanation

    prompt = client.models.generate_content.call_args.kwargs["contents"]
    assert "Neon Tide" in prompt
    assert guide["content"] in prompt


@pytest.mark.parametrize(
    ("response_text", "expected_error"),
    [
        ("invalid JSON", "invalid JSON"),
        ('{"id": 11}', "must return a list"),
        (
            '[{"id": 999, "explanation": "Unknown track."}]',
            "unknown song ID",
        ),
        (
            json.dumps(
                [
                    {"id": 11, "explanation": "First explanation."},
                    {"id": 11, "explanation": "Duplicate explanation."},
                ]
            ),
            "duplicate song ID",
        ),
        ("[]", "omitted a selected song"),
        (
            '[{"id": 11, "explanation": ""}]',
            "between 1 and 50 words",
        ),
        (
            json.dumps(
                [{"id": 11, "explanation": "word " * 51}]
            ),
            "between 1 and 50 words",
        ),
    ],
)
def test_invalid_model_output_is_rejected(
    model_setup, response_text, expected_error
):
    """Reject malformed, incomplete, or invalid model responses."""
    client, recommendations, guide = model_setup
    client.models.generate_content.return_value = SimpleNamespace(
        text=response_text
    )

    with pytest.raises(ValueError, match=expected_error):
        generate_explanations(
            "Give me 1 upbeat song for a workout",
            recommendations,
            guide,
        )


def test_missing_api_key_is_rejected(model_setup, monkeypatch):
    """Explain the missing configuration before calling Gemini."""
    client, recommendations, guide = model_setup
    monkeypatch.delenv("GEMINI_API_KEY")

    with pytest.raises(ValueError, match="Set GEMINI_API_KEY"):
        generate_explanations(
            "Give me 1 upbeat song for a workout",
            recommendations,
            guide,
        )

    client.models.generate_content.assert_not_called()


def test_empty_recommendations_skip_generation(model_setup):
    """Return an empty result without making a model request."""
    client, _, guide = model_setup

    assert generate_explanations("workout", [], guide) == []
    client.models.generate_content.assert_not_called()


def test_network_failure_becomes_handled_error(model_setup):
    """Convert a transport failure into a handled application error."""
    client, recommendations, guide = model_setup
    client.models.generate_content.side_effect = ConnectError(
        "Simulated connection failure"
    )

    with pytest.raises(ValueError, match="connection failure"):
        generate_explanations(
            "Give me 1 upbeat song for a workout",
            recommendations,
            guide,
        )