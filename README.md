# 🎧 Playlist Intelligence

An applied AI music recommender that combines transparent Python ranking,
retrieved activity guidance, and Gemini-generated explanations.

Built for **CodePath AI110 — Project 4: Applied AI System**.

## Project Summary

Playlist Intelligence helps listeners find songs that fit a workout or
studying session and understand why those tracks were recommended.

The application searches an 18-song catalog, applies rules from a custom
activity guide, and ranks matching tracks. Gemini explains the selected
tracks using the retrieved evidence.

When a studying request has too few exact matches, the application asks
before including other genres. Output validation and catalog-based
fallback explanations help the application handle invalid responses and
API failures.

## Original Project and Extensions

This project extends **Project 3: Music Recommender Simulation**, named
**VibeFinder 1.0**. The original application ranked songs for three taste
profiles using genre, mood, and energy, then displayed scores and
explanations. Optional features included advanced metadata, two scoring
modes, artist diversity, and table output.

Project 4 adds:

- Workout and studying playlist requests.
- Retrieval from the song catalog and custom activity guide.
- Gemini explanations grounded in retrieved evidence.
- Human approval before broadening a studying search.
- Model-output validation and API-error fallback.
- Few-shot specialized explanations.
- Automated tests, a CLI evaluation harness, and a live prompt comparison.

The original Project 3 files and commit history were copied into this
dedicated repository.

## How It Works

### Retrieval and Ranking

The application retrieves activity guidance from
`data/curation_guides.md` and song records from `data/songs.csv`.

Python applies the retrieved mood and energy rules, then ranks eligible
tracks using the existing scoring function.

| Activity | Target energy | Energy restriction | Suitable moods |
|---|---:|---|---|
| Workout | 0.90 | Minimum 0.75 | happy, energizing, intense, aggressive, playful, uplifting |
| Studying | 0.35 | Maximum 0.50 | chill, focused, relaxed, peaceful |

Workout requests favor energizing tracks. Studying requests preserve the
requested genre and favor focused tracks.

### Human Approval

If a studying request has too few exact matches, the application asks
whether other genres may be included.

Only an explicit `y` or `yes` authorizes broadening. Declining, pressing
Enter, or reaching end-of-input preserves the requested genre.

The broader search retains the studying mood and energy restrictions.

### Grounded Generation

With `--ai`, Gemini receives the request, selected tracks, ranking
evidence, and retrieved activity guidance.

Python selects the tracks. Gemini writes their explanations.

The application verifies the returned JSON, song IDs, completeness,
uniqueness, and explanation length. It displays an identified
catalog-based fallback when a handled API error or invalid response
prevents successful generation.

### Specialized Explanations

With `--ai --specialized`, the prompt adds illustrative few-shot examples.
It requests concise explanations with labeled mood and energy evidence.

## Architecture

The required Mermaid source is saved in
[diagrams/architecture.mmd](diagrams/architecture.mmd).

The diagram shows the Project 4 playlist-request workflow:

- Input validation and guide retrieval.
- Catalog filtering and ranking.
- Listener approval and broader retrieval.
- Baseline or specialized generation.
- Output verification, fallback, and display.
- Connections to the evaluation harness and automated tests.

The original three-profile demo is a separate CLI path.

## Project Structure

| Path | Responsibility |
|---|---|
| `src/main.py` | CLI, approval prompts, generation orchestration, and output |
| `src/recommender.py` | Catalog loading, scoring, and ranking |
| `src/curator.py` | Workout requests and activity routing |
| `src/study_curator.py` | Studying rules and approved genre broadening |
| `src/guide_retriever.py` | Activity-guide retrieval |
| `src/llm_client.py` | Gemini generation and response validation |
| `src/prompts.py` | Baseline and specialized prompts |
| `data/songs.csv` | Existing 18-song catalog |
| `data/curation_guides.md` | Custom activity guidance |
| `tests/` | Automated behavior tests |
| `evaluate.py` | Predefined CLI evaluation cases |
| `compare_prompts.py` | Live baseline and specialization comparison |
| `diagrams/architecture.mmd` | Mermaid architecture source |
| `evidence/` | Recorded outputs and comparison results |
| `model_card.md` | Responsible-AI reflection and evaluation analysis |
| `ai_interactions.md` | Development history and workflow traces |

## Setup Instructions

### Requirements

Development was verified with **Python 3.13.9 on Windows**.

The dependency file contains:

```text
pandas
pytest
streamlit
google-genai
```

The current interface is a command-line application.

### 1. Clone the Repository

```cmd
git clone https://github.com/HaidaMarese/playlist-intelligence.git
cd playlist-intelligence
```

### 2. Create a Virtual Environment

```cmd
py -3.13 -m venv .venv
```

Activate it in Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

For PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

For macOS or Linux, create and activate it using:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Confirm the Interpreter

```cmd
python -c "import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)"
```

The path should point inside the project's `.venv`, and the second line
should print `True`.

### 4. Install Dependencies

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Run Without Gemini

Run all commands from the repository root.

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout"
python -m src.main --request "3 calm lofi songs for studying"
python -m src.main --request "3 calm jazz songs for studying"
```

These commands use catalog-based explanations and require no API key.

### 6. Configure Gemini

Create or use an API key in
[Google AI Studio](https://aistudio.google.com/apikey).

In Windows Command Prompt:

```cmd
set "GEMINI_API_KEY=YOUR_API_KEY"
set "GEMINI_MODEL=gemini-3.5-flash-lite"
```

In PowerShell:

```powershell
$env:GEMINI_API_KEY = "YOUR_API_KEY"
$env:GEMINI_MODEL = "gemini-3.5-flash-lite"
```

In macOS or Linux:

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
export GEMINI_MODEL="gemini-3.5-flash-lite"
```

Replace the placeholder with your private key. These settings apply to
the current terminal session.

`gemini-3.5-flash-lite` was verified in the recorded executions. Model
access, quotas, and availability depend on the API account and service.

Verify configuration without printing the key:

```cmd
python -c "import os; print('API key configured:', bool(os.environ.get('GEMINI_API_KEY'))); print('Model:', os.environ.get('GEMINI_MODEL'))"
```

### 7. Run With AI Explanations

Baseline prompt:

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai
```

Specialized prompt:

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai --specialized
```

Approved studying alternatives:

```cmd
python -m src.main --request "3 calm jazz songs for studying" --ai
```

Answer `y` to include eligible tracks from other genres.

### 8. Run Tests and Evaluation

```cmd
python -m pytest -q
python evaluate.py
```

These checks do not make live Gemini requests.

Run the live prompt comparison separately:

```cmd
python compare_prompts.py
```

The comparison makes two model requests and writes
`evidence/prompt_comparison.md`.

## Supported Requests and Options

| Example | Behavior |
|---|---|
| `3 upbeat songs for a workout` | Retrieve and rank suitable workout tracks |
| `Give me 3 upbeat songs for a workout` | Same request with the optional introductory phrase |
| `3 calm lofi songs for studying` | Preserve lofi and apply studying rules |
| `3 calm jazz songs for studying` | Ask before broadening when exact matches are insufficient |
| `--ai` | Generate explanations with Gemini |
| `--ai --specialized` | Use the few-shot curator style |

Requests support counts from **1 to 10**. Fewer tracks may be returned
when the active constraints cannot supply the requested count.

The parser currently accepts the documented request patterns.

## Reproducible Execution Evidence

The following excerpts come from observed executions. Table columns are
condensed here for readability. Full recorded logs are linked below.

Live explanations can vary across runs.

### Example 1 — Workout With Specialized AI Explanations

Command:

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai --specialized
```

Observed output excerpt:

```text
Loaded songs: 18

Playlist request: Give me 3 upbeat songs for a workout
Explanation mode: Gemini
Prompt style: specialized

Neon Tide | Score: 1.98
Mood: energizing. Energy: 0.88. Fits a workout and is close to the guide target of 0.90.
[Source: data/curation_guides.md#workout; catalog ID: 11]

Storm Runner | Score: 0.99
Mood: intense. Energy: 0.91. Fits a workout and is close to the guide target of 0.90.
[Source: data/curation_guides.md#workout; catalog ID: 3]

Gym Hero | Score: 0.97
Mood: intense. Energy: 0.93. Fits a workout and is close to the guide target of 0.90.
[Source: data/curation_guides.md#workout; catalog ID: 5]
```

This demonstrates catalog retrieval, activity guidance, ranking, and
specialized generation.

### Example 2 — Declining Other Genres

Command:

```cmd
python -m src.main --request "3 calm jazz songs for studying"
```

Observed interaction excerpt:

```text
Loaded songs: 18

Playlist request: 3 calm jazz songs for studying
Found 1 matching track(s) out of 3 requested.
Include other genres while keeping the studying energy and mood rules? [y/N]: N
Keeping only the requested genre.
Explanation mode: catalog scoring

Coffee Shop Stories | Score: 2.98
genre match (+2.00), energy similarity (+0.98);
studying guide match (energy 0.37, mood relaxed);
genre status: requested genre;
source: data/curation_guides.md#studying
```

The listener's genre preference remains active after declining.

### Example 3 — Approving Other Genres With AI

Command:

```cmd
python -m src.main --request "3 calm jazz songs for studying" --ai
```

Answer `y` at the prompt.

Observed interaction excerpt:

```text
Loaded songs: 18

Playlist request: 3 calm jazz songs for studying
Found 1 matching track(s) out of 3 requested.
Other genres approved by the listener.
Found 3 track(s) after broadening the search.
Explanation mode: Gemini

Coffee Shop Stories | Score: 2.98
This jazz track fits the studying request with a relaxed mood and an energy of 0.37, matching the target studying energy of 0.35.
[Source: data/curation_guides.md#studying; catalog ID: 7]

Focus Flow | Score: 1.95
As an approved alternative genre, this lofi track supports studying with a focused mood and an energy of 0.4, closely matching the target energy.
[Source: data/curation_guides.md#studying; catalog ID: 9]

Library Rain | Score: 1.00
This lofi track serves as an approved alternative genre for studying, featuring a chill mood and an energy of 0.35 that exactly meets the target energy.
[Source: data/curation_guides.md#studying; catalog ID: 4]
```

The energy target comes from the studying guide. The first explanation's
word “matching” describes a nearby value, rather than numerical equality.
This is an observed wording limitation discussed in the model card.

### Guardrail Example — Blank Input

```cmd
python -m src.main --request ""
```

Observed error excerpt:

```text
Loaded songs: 18
main.py: error: Enter a playlist request, such as '3 upbeat songs for a workout'.
```

### API Failure Example

During testing, a live request returned:

```text
AI explanation unavailable. Showing catalog-based explanations.
Reason: 504 DEADLINE_EXCEEDED.
```

The application then displayed the verified catalog recommendations.

### Full Execution Logs

- [Workout AI execution](evidence/workout_ai.txt)
- [Declined studying search](evidence/studying_declined.txt)
- [Approved studying search](evidence/studying_approved.txt)
- [Approved studying search with AI](evidence/studying_approved_ai.txt)
- [Evaluation summary](evidence/evaluation.txt)
- [Baseline and specialized comparison](evidence/prompt_comparison.md)

## Reliability and Evaluation

### Automated Tests

Latest verified result after integrating specialized prompting:

```cmd
python -m pytest -q
```

```text
38 passed in 0.93s
```

Coverage includes:

- Original recommendation behavior.
- Blank inputs and invalid counts.
- Guide retrieval and malformed rules.
- Guide changes affecting filtering.
- Studying genre, mood, and energy constraints.
- Approved and declined broader searches.
- Missing approval input.
- Model JSON, IDs, duplicates, completeness, and length.

### CLI Evaluation Harness

```cmd
python evaluate.py
```

```text
Playlist Intelligence - CLI Evaluation
Live Gemini calls: disabled

PASS | Workout recommendations
PASS | Exact studying recommendations
PASS | Declined genre broadening
PASS | Approved genre broadening
PASS | Blank request guardrail
PASS | Invalid count guardrail
PASS | Unknown genre guardrail
PASS | AI requires a request

Summary: 8/8 cases passed
Pass rate: 100%
```

The pass rate applies to these eight predefined scenarios. It does not
measure listener satisfaction or the factual accuracy of every generated
sentence.

### Human Review of Observed Behavior

| Case | Criterion | Observed result |
|---|---|---|
| Initial workout filter | Respect upbeat intent | Needed revision — energy-only filtering selected a sad track |
| Revised workout filter | Apply energy and suitable moods | Pass — Winter Signal excluded |
| Jazz request, answer N | Preserve jazz | Pass — one exact match |
| Jazz request, answer y | Broaden only with approval | Pass — jazz match and two eligible lofi tracks |
| Approved AI explanations | Identify alternative genres | Pass in recorded run |
| Numeric explanation wording | Distinguish nearby and exact values | Needs improvement — some wording is imprecise |
| API 503/504 response | Provide an identified fallback | Pass in observed runs |

## Stretch Features and Evidence

### Multi-Source RAG

The app combines the song catalog with a custom activity guide.

The initial workout filter used energy alone and recommended Winter
Signal. Adding suitable mood rules removed that sad track. The revised
playlist contained Neon Tide, Storm Runner, and Gym Hero.

A guide-threshold test also confirms that changing the retrieved minimum
energy changes which tracks are eligible.

This improved alignment with the project's activity rules. Listener
enjoyment has not been measured.

### Agentic Decision Workflow

The runtime workflow validates, retrieves, ranks, checks the result
count, requests approval when needed, and searches again after approval.

The decision chain is implemented in Python. Human approval controls
genre broadening.

Actions, observed results, and committed execution logs are documented in
[ai_interactions.md](ai_interactions.md).

### Specialization

The specialized prompt adds few-shot examples and requests short,
consistently labeled evidence.

Observed live comparison:

| Style | Average words | At most 25 words | Correct mood labels | Correct energy labels |
|---|---:|---:|---:|---:|
| Baseline | 23.3 | 3/3 | 0/3 | 0/3 |
| Specialized | 16.0 | 3/3 | 3/3 | 3/3 |

Average length decreased by approximately **31%**.

The baseline also used correct catalog facts. Label scores measure
compliance with the specialized format.

Full outputs and interpretation appear in
[model_card.md](model_card.md) and
[evidence/prompt_comparison.md](evidence/prompt_comparison.md).

### Evaluation Harness

`evaluate.py` executes the actual CLI on predefined inputs, checks exit
codes and expected behavior, and prints a summary.

The verified run passed **8/8 cases**.

## Design Decisions

| Decision | Reason and trade-off |
|---|---|
| Reuse Project 3 scoring | Keeps ranking inspectable, while inheriting its weighting assumptions |
| Retrieve activity guidance | Makes rules traceable to a document, but requires predictable guide formatting |
| Keep selection in Python | Provides reproducible ranking and constraint handling |
| Use Gemini for explanations | Adds readable explanations with service dependency and wording risks |
| Require approval to broaden genre | Gives listeners control over changing an explicit preference |
| Validate model output | Rejects structural errors while leaving semantic accuracy for further evaluation |
| Preserve catalog fallback | Keeps recommendations available during handled generation failures |
| Separate live and simulated checks | Supports repeatable tests alongside recorded live generation |

## Preserved Project 3 Features

Run the original three-profile demo:

```cmd
python -m src.main
```

| Profile | First recommendation | Score |
|---|---|---:|
| High-Energy Pop | Sunrise City | 3.97 |
| Chill Lofi | Library Rain | 3.90 |
| Deep Intense Rock | Storm Runner | 3.99 |

The baseline score uses a genre weight of `2.0`, mood weight of `1.0`,
and energy-similarity weight of `1.0`.

The original options remain available for the three-profile demo:

```cmd
python -m src.main --advanced
python -m src.main --mode energy-focused
python -m src.main --diversity
python -m src.main --table
python -m src.main --advanced --mode energy-focused --diversity --table
```

| Option | Purpose |
|---|---|
| `--advanced` | Include five additional illustrative metadata attributes |
| `--mode energy-focused` | Use genre, mood, and energy weights of `(1.0, 1.0, 2.0)` |
| `--diversity` | Apply a 0.50-point repeat-artist penalty during selection |
| `--table` | Format the profile-demo output as a table |

These options apply to the original profile demo. Playlist requests
currently use their activity-specific ranking settings.

Earlier experiments and detailed profile comparisons remain documented
in [model_card.md](model_card.md) and
[ai_interactions.md](ai_interactions.md).

## Limitations and Remaining Work

- The catalog is small and contains illustrative metadata.
- Request parsing supports specific documented patterns.
- Activity moods and thresholds reflect design assumptions.
- Structural validation does not verify every generated factual claim.
- Live generation can fail or vary between runs.
- The studying guide's instrumental preference still needs implementation
  or revision.
- Network transport exceptions need additional safe handling.
- Dependencies are currently unpinned. Exact package-version reproduction
  has not yet been established.
- Final setup verification from a fresh clone is pending.

## Reflection

Extending the recommender taught me that matching a numeric feature is
only part of satisfying a request. A high-energy song can still conflict
with an upbeat mood, and a readable explanation can contain imprecise
wording.

I learned to inspect outputs, revise rules, test failure cases, and
preserve evidence of the system's behavior.

The graded responsible-AI reflection, accepted and revised AI
suggestions, limitations, misuse analysis, and testing surprises are in
[model_card.md](model_card.md).

## Presentation and Portfolio

The planned 5–7 minute Engineer's Pitch follows four topics:

- **The Problem** — Find activity-appropriate tracks and explain the picks.
- **The Logic** — Retrieve guidance, rank songs, and generate explanations.
- **The Reliability** — Show tests, approval controls, and fallback behavior.
- **The Reflection** — Explain what testing revealed and what changed.

### Portfolio Reflection

This project shows my approach to building understandable AI systems.
I extended an existing Python recommender, integrated retrieved
guidance and model-generated explanations, and verified key behaviors
with automated tests and recorded executions. I also added listener
approval and fallback behavior so the system handles uncertainty and
failures explicitly.

[GitHub repository](https://github.com/HaidaMarese/playlist-intelligence)

The presentation and optional Loom walkthrough are still in preparation.

## Author

**Haida Makouangou**

B.S. in Computer Science, UNC Charlotte, Cum Laude

Built for CodePath AI110.