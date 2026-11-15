"""Test studying approval decisions through the CLI entry point."""

import sys

import pytest

from src.main import main


@pytest.mark.parametrize("answer", ["n", "N", ""])
def test_declining_preserves_requested_genre(
    monkeypatch, capsys, answer
):
    """Declining or pressing Enter keeps only the jazz match."""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "playlist-intelligence",
            "--request",
            "3 calm jazz songs for studying",
        ],
    )
    monkeypatch.setattr("builtins.input", lambda prompt: answer)

    main()

    output = capsys.readouterr().out
    assert "Found 1 matching track(s) out of 3 requested." in output
    assert "Keeping only the requested genre." in output
    assert "Coffee Shop Stories" in output
    assert "Focus Flow" not in output
    assert "Library Rain" not in output


@pytest.mark.parametrize("answer", ["y", "YES"])
def test_approval_includes_other_genres(
    monkeypatch, capsys, answer
):
    """Explicit approval adds eligible alternative tracks."""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "playlist-intelligence",
            "--request",
            "3 calm jazz songs for studying",
        ],
    )
    monkeypatch.setattr("builtins.input", lambda prompt: answer)

    main()

    output = capsys.readouterr().out
    assert "Other genres approved by the listener." in output
    assert "Found 3 track(s) after broadening the search." in output
    assert "Coffee Shop Stories" in output
    assert "Focus Flow" in output
    assert "Library Rain" in output


def test_missing_input_preserves_requested_genre(monkeypatch, capsys):
    """An unavailable input stream never authorizes broadening."""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "playlist-intelligence",
            "--request",
            "3 calm jazz songs for studying",
        ],
    )

    def unavailable_input(prompt):
        raise EOFError

    monkeypatch.setattr("builtins.input", unavailable_input)

    main()

    output = capsys.readouterr().out
    assert "Keeping only the requested genre." in output
    assert "Coffee Shop Stories" in output
    assert "Focus Flow" not in output


def test_complete_request_does_not_prompt(monkeypatch, capsys):
    """A request with enough exact matches needs no approval."""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "playlist-intelligence",
            "--request",
            "3 calm lofi songs for studying",
        ],
    )

    def unexpected_prompt(prompt):
        pytest.fail("Approval was requested despite enough exact matches.")

    monkeypatch.setattr("builtins.input", unexpected_prompt)

    main()

    output = capsys.readouterr().out
    assert "Focus Flow" in output
    assert "Library Rain" in output
    assert "Midnight Coding" in output
    assert "Other genres approved" not in output