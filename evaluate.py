"""Evaluate Playlist Intelligence through its CLI without live API calls."""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

CASES = [
    {
        "name": "Workout recommendations",
        "arguments": [
            "--request",
            "3 upbeat songs for a workout",
        ],
        "input": None,
        "exit_code": 0,
        "expected": ["Neon Tide", "Storm Runner", "Gym Hero"],
        "excluded": ["Winter Signal"],
    },
    {
        "name": "Exact studying recommendations",
        "arguments": [
            "--request",
            "3 calm lofi songs for studying",
        ],
        "input": None,
        "exit_code": 0,
        "expected": ["Focus Flow", "Library Rain", "Midnight Coding"],
        "excluded": ["Include other genres"],
    },
    {
        "name": "Declined genre broadening",
        "arguments": [
            "--request",
            "3 calm jazz songs for studying",
        ],
        "input": "n\n",
        "exit_code": 0,
        "expected": [
            "Keeping only the requested genre.",
            "Coffee Shop Stories",
        ],
        "excluded": ["Focus Flow", "Library Rain"],
    },
    {
        "name": "Approved genre broadening",
        "arguments": [
            "--request",
            "3 calm jazz songs for studying",
        ],
        "input": "y\n",
        "exit_code": 0,
        "expected": [
            "Other genres approved by the listener.",
            "Coffee Shop Stories",
            "Focus Flow",
            "Library Rain",
        ],
        "excluded": ["Winter Signal"],
    },
    {
        "name": "Blank request guardrail",
        "arguments": ["--request", ""],
        "input": None,
        "exit_code": 2,
        "expected": ["Enter a playlist request"],
        "excluded": ["Explanation mode:"],
    },
    {
        "name": "Invalid count guardrail",
        "arguments": [
            "--request",
            "0 upbeat songs for a workout",
        ],
        "input": None,
        "exit_code": 2,
        "expected": ["Request between 1 and 10 songs."],
        "excluded": ["Explanation mode:"],
    },
    {
        "name": "Unknown genre guardrail",
        "arguments": [
            "--request",
            "3 calm imaginary songs for studying",
        ],
        "input": None,
        "exit_code": 2,
        "expected": ["Unknown genre 'imaginary'"],
        "excluded": ["Explanation mode:"],
    },
    {
        "name": "AI requires a request",
        "arguments": ["--ai"],
        "input": None,
        "exit_code": 2,
        "expected": ["--ai requires --request."],
        "excluded": ["Explanation mode:"],
    },
]


def main():
    """Run predefined CLI scenarios and report observed results."""
    passed = 0

    print("Playlist Intelligence - CLI Evaluation")
    print("Live Gemini calls: disabled")
    print()

    for case in CASES:
        command = [
            sys.executable,
            "-m",
            "src.main",
            *case["arguments"],
        ]

        try:
            result = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                input=case["input"] or "",
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
            )
        except (subprocess.TimeoutExpired, OSError) as error:
            print(f"FAIL | {case['name']}")
            print(f"  Could not complete the command: {error}")
            continue

        output = result.stdout + result.stderr
        problems = []

        if result.returncode != case["exit_code"]:
            problems.append(
                f"Expected exit code {case['exit_code']}, "
                f"received {result.returncode}."
            )

        for expected_text in case["expected"]:
            if expected_text not in output:
                problems.append(f"Missing expected text: {expected_text}")

        for excluded_text in case["excluded"]:
            if excluded_text in output:
                problems.append(f"Unexpected text: {excluded_text}")

        if problems:
            print(f"FAIL | {case['name']}")
            for problem in problems:
                print(f"  {problem}")
            print("  Captured output:")
            print(output)
        else:
            passed += 1
            print(f"PASS | {case['name']}")

    total = len(CASES)
    print()
    print(f"Summary: {passed}/{total} cases passed")
    print(f"Pass rate: {passed / total:.0%}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())