"""Generate playlist explanations grounded in retrieved records."""

import json
import os

from google import genai
from google.genai import types
from httpx2 import TransportError

from .prompts import build_prompt


def generate_explanations(
    request, recommendations, guide, *, specialized=False
):
    """Return recommendations with validated model-written explanations."""
    if not recommendations:
        return []

    api_key = os.environ.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL")

    if not api_key or not model:
        raise ValueError(
            "Set GEMINI_API_KEY and GEMINI_MODEL before using --ai."
        )

    evidence = [
        {
            "id": song["id"],
            "title": song["title"],
            "artist": song["artist"],
            "genre": song["genre"],
            "mood": song["mood"],
            "energy": song["energy"],
            "score": score,
            "ranking_evidence": explanation,
        }
        for song, score, explanation in recommendations
    ]

    prompt = build_prompt(
        request,
        evidence,
        guide,
        specialized=specialized,
    )

    try:
        with genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=60000),
        ) as client:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    max_output_tokens=2048,
                ),
            )
    except (TransportError, OSError) as error:
        raise ValueError(
            "Could not complete the Gemini request because of "
            "a connection failure or network timeout."
        ) from error

    try:
        items = json.loads(response.text or "")
    except (json.JSONDecodeError, TypeError) as error:
        raise ValueError("The model returned invalid JSON.") from error

    if not isinstance(items, list):
        raise ValueError("The model must return a list of explanations.")

    expected_ids = {song["id"] for song, _, _ in recommendations}
    explanations = {}

    for item in items:
        if not isinstance(item, dict):
            raise ValueError(
                "The model returned an invalid explanation record."
            )

        song_id = item.get("id")
        explanation = item.get("explanation")

        if type(song_id) is not int or song_id not in expected_ids:
            raise ValueError("The model returned an unknown song ID.")

        if song_id in explanations:
            raise ValueError("The model returned a duplicate song ID.")

        if (
            not isinstance(explanation, str)
            or not explanation.strip()
            or len(explanation.split()) > 50
        ):
            raise ValueError(
                "Each explanation must contain between 1 and 50 words."
            )

        explanations[song_id] = explanation.strip()

    if set(explanations) != expected_ids:
        raise ValueError("The model omitted a selected song.")

    return [
        (
            song,
            score,
            f"{explanations[song['id']]} "
            f"[Source: {guide['source']}; catalog ID: {song['id']}]",
        )
        for song, score, _ in recommendations
    ]