"""Verify CLI fallback after a simulated network failure."""

import sys

from httpx2 import ConnectError

from src.main import main


def test_network_failure_displays_catalog_fallback(monkeypatch, capsys):
    """Keep recommendations available when the model connection fails."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "test-model")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "playlist-intelligence",
            "--request",
            "3 upbeat songs for a workout",
            "--ai",
        ],
    )

    def failed_connection(*args, **kwargs):
        raise ConnectError("Simulated network failure")

    monkeypatch.setattr(
        "src.llm_client.genai.Client",
        failed_connection,
    )

    main()

    output = capsys.readouterr().out
    assert "AI explanation unavailable." in output
    assert "Showing catalog-based explanations." in output
    assert "connection failure or network timeout" in output
    assert "Neon Tide" in output
    assert "Storm Runner" in output
    assert "Gym Hero" in output
    assert "Explanation mode: Gemini" not in output