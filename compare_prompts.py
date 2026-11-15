"""Compare baseline and specialized explanations using live Gemini calls."""

import os
import re
from pathlib import Path

from google.genai import errors

from src.curator import rank_request
from src.guide_retriever import retrieve_guide
from src.llm_client import generate_explanations
from src.recommender import load_songs


PROJECT_ROOT = Path(__file__).resolve().parent


def measure_results(results):
    """Measure explanation length and labeled catalog evidence."""
    rows = []

    for song, _, explanation in results:
        # Exclude the source reference appended by the application.
        text = explanation.rsplit(" [Source:", 1)[0].strip()

        mood_pattern = (
            r"\bMood:\s*"
            + re.escape(song["mood"])
            + r"\s*\."
        )

        energy_match = re.search(
            r"\bEnergy:\s*([0-9]+(?:\.[0-9]+)?)",
            text,
            flags=re.IGNORECASE,
        )
        correct_energy = (
            energy_match is not None
            and energy_match.group(1) == f"{song['energy']:.2f}"
        )

        rows.append(
            {
                "title": song["title"],
                "text": text,
                "words": len(text.split()),
                "correct_mood_label": bool(
                    re.search(mood_pattern, text, flags=re.IGNORECASE)
                ),
                "correct_energy_label": correct_energy,
            }
        )

    return rows


def main():
    """Run the same retrieved tracks through both prompt styles."""
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))
    request = "Give me 3 upbeat songs for a workout"
    recommendations = rank_request(request, songs)
    guide = retrieve_guide("workout")

    if not recommendations:
        print("Comparison stopped: no tracks matched the request.")
        return 1

    report = [
        "# Baseline vs. Specialized Prompt Comparison",
        "",
        f"Model: `{os.environ.get('GEMINI_MODEL', 'not configured')}`",
        "",
        f"Request: `{request}`",
        "",
        "Both styles use the same retrieved tracks, guide, model, "
        "output limit, and validation. The prompt instructions differ.",
        "",
        "This is one live run per style. Results can vary between runs.",
        "",
    ]
    measurements = {}

    for style, specialized in [
        ("Baseline", False),
        ("Specialized", True),
    ]:
        print(f"Generating {style.lower()} explanations...", flush=True)

        try:
            results = generate_explanations(
                request,
                recommendations,
                guide,
                specialized=specialized,
            )
        except (ValueError, errors.APIError) as error:
            print(f"Comparison stopped: {error}")
            return 1

        rows = measure_results(results)
        measurements[style] = rows

        report.extend(
            [
                f"## {style} Outputs",
                "",
                "| Song | Words | Correct mood label | Correct energy label |",
                "|---|---:|---|---|",
            ]
        )

        for row in rows:
            report.append(
                f"| {row['title']} | {row['words']} | "
                f"{row['correct_mood_label']} | "
                f"{row['correct_energy_label']} |"
            )

        report.append("")

        for row in rows:
            report.extend(
                [
                    f"### {row['title']}",
                    "",
                    row["text"],
                    "",
                ]
            )

    report.extend(
        [
            "## Measured Summary",
            "",
            "| Style | Average words | At most 25 words | "
            "Correct mood labels | Correct energy labels |",
            "|---|---:|---:|---:|---:|",
        ]
    )

    for style, rows in measurements.items():
        count = len(rows)
        average_words = sum(row["words"] for row in rows) / count
        concise = sum(row["words"] <= 25 for row in rows)
        mood_labels = sum(row["correct_mood_label"] for row in rows)
        energy_labels = sum(row["correct_energy_label"] for row in rows)

        report.append(
            f"| {style} | {average_words:.1f} | {concise}/{count} | "
            f"{mood_labels}/{count} | {energy_labels}/{count} |"
        )

    report.extend(
        [
            "",
            "## Interpretation",
            "",
            "These measurements assess concise wording and compliance "
            "with the specialized evidence-label format. A baseline "
            "explanation may describe correct facts without those labels. "
            "Label scores measure compliance with the requested style. "
            "Overall factual accuracy requires separate review.",
            "",
            "The 25-word measurement excludes application-added source "
            "references. Both styles use the same selected songs. "
            "This experiment measures explanation behavior.",
            "",
        ]
    )

    output_path = PROJECT_ROOT / "evidence" / "prompt_comparison.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report), encoding="utf-8")

    print("\n".join(report))
    print(f"\nSaved comparison to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())