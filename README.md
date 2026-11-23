# 🎧 Playlist Intelligence

An applied AI music recommender that combines transparent Python ranking,
retrieved activity guidance, and Gemini-generated explanations.

Built for **CodePath AI110 — Project 4: Applied AI System**.

## Project Summary

Playlist Intelligence helps listeners find songs for workouts or studying
and understand why each track was recommended. It provides a Streamlit
visual interface and a command-line interface.

The application searches an 18-song catalog, retrieves rules from a custom
activity guide, and ranks eligible tracks in Python. Gemini optionally
explains those selections using the retrieved evidence.

When a studying request has too few exact matches, the application asks
before including other genres. Output validation and identified
catalog-based fallbacks help preserve recommendations during handled
generation failures.

## Original Project and Extensions

This project extends **Project 3: Music Recommender Simulation**, named
**VibeFinder 1.0**. The original application ranked songs for three taste
profiles using genre, mood, and energy, then displayed scores and
explanations. Optional features included advanced metadata, two scoring
modes, artist diversity, and table output.

The original Project 3 files and commit history were copied into this
dedicated repository.

Project 4 adds:

- Workout and studying playlist requests.
- Retrieval from the song catalog and custom activity guide.
- Gemini explanations grounded in retrieved evidence.
- Listener approval before broadening a studying search.
- Instrumentalness as a tie-break preference for studying.
- Model-output validation and generation-failure fallback.
- Few-shot specialized explanations.
- Automated tests, a CLI evaluation harness, and a live prompt comparison.
- A Streamlit interface with an embedded music-themed background.
- Playlist summary metrics, expandable evidence, and CSV download.
- A revised prompt that restricts approval claims to appropriate
  studying requests.

## Visual Interface

The Streamlit interface lets listeners:

- Choose Workout or Studying.
- Request between 1 and 10 songs.
- Select a genre for studying.
- Enable Gemini explanations.
- Choose baseline or concise specialized explanations.
- Approve or decline other genres when studying matches are insufficient.
- Inspect song cards, relevance scores, and catalog evidence.
- View track count, distinct artist count, and average energy.
- Download the displayed playlist as a CSV.
- Clear the displayed results.

The music-themed background is embedded in `streamlit_app.py`; it does
not require a separate background image file.

The application displays recommendations and explanations. Audio playback
and music-service integration are future improvements.

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

Workout requests search across genres and favor energizing tracks.
Studying requests initially preserve the requested genre and favor
focused tracks.

Genre, mood, and energy relevance determine the primary score.

For studying requests, higher instrumentalness breaks ties between
equally scored tracks when the retrieved guide requests that preference.
The tie-break is applied before selecting the final number of tracks.

Instrumentalness uses the catalog's 0–1 values. Missing values default
to `0.0`. Equal scores and equal instrumentalness preserve catalog order.

Relevance scores describe rule-based catalog matches. They are not
probabilities or guarantees of listener enjoyment.

### Human Approval

If a studying request has too few exact matches, the application asks
whether other genres may be included.

In the CLI, an explicit `y` or `yes`, ignoring capitalization and
surrounding spaces, authorizes broadening. Declining, pressing Enter,
or reaching end-of-input preserves the requested genre.

In Streamlit, the listener chooses:

- **Include other genres** to approve broadening.
- **Keep my genre** to retain only exact genre matches.

The broader search retains the studying mood and energy restrictions
and the instrumentalness tie-break preference.

Workout searches already include all genres and do not require this
genre-broadening approval.

### Grounded Generation

When AI explanations are enabled, Gemini receives:

- The listener request.
- Selected catalog records.
- Ranking evidence.
- Retrieved activity guidance.
- Approval context when a studying search was explicitly broadened.

**Python selects the tracks. Gemini writes their explanations.**

The application verifies:

- JSON list format.
- Expected integer song IDs.
- Unique song IDs.
- An explanation for every selected track.
- Explanation length between 1 and 50 words.

The application displays song titles, artists, and scores from its
catalog records and appends source references to generated explanations.

A handled API error or invalid model response triggers an identified
catalog-based fallback.

Connection failures and network timeouts are converted into a handled
error that also triggers the fallback. Simulated tests verify
connection-failure handling in the model client and CLI. A dedicated
timeout-specific test remains a future improvement.

Structural validation checks response format and IDs. It does not verify
every factual claim or statement about listener approval.

### Specialized Explanations

The specialized prompt adds illustrative few-shot examples and requests:

- At most 25 words per explanation.
- An explicit `Mood:` label with the catalog mood.
- An explicit `Energy:` label formatted to two decimal places.
- A connection to the requested activity.
- Accurate distinctions between exact, nearby, above, and below-target
  energy values.
- Approval wording only when supported by the actual studying request.

The shared validator permits up to 50 words. The specialized 25-word
target is evaluated separately.

### Approval-Wording Revision

A live specialized workout run incorrectly called some tracks
“approved alternatives,” although no genre approval had occurred.

The prompt was revised to:

- Prohibit invented approval claims.
- Restrict “approved alternative” wording to explicitly approved
  studying searches and tracks outside the requested genre.
- Prohibit that wording for workout requests.
- Give few-shot examples separate, explicit contexts.

A subsequent live workout run contained correct mood and energy facts
without unsupported approval claims.

The observed revised output is saved in
[evidence/workout_specialized_revised.txt](evidence/workout_specialized_revised.txt).

This verifies the correction in that observed run. Future generated
responses still require review.

## Architecture

The Mermaid architecture source is saved in
[diagrams/architecture.mmd](diagrams/architecture.mmd).

It documents:

- CLI requests and Streamlit preferences.
- Input validation and activity-guide retrieval.
- Catalog filtering and ranking.
- Listener approval and broader studying searches.
- Baseline or specialized generation.
- Output validation and catalog fallback.
- Terminal output and visual recommendation cards.
- CSV download and result clearing.
- Connections to the CLI evaluation harness and automated tests.

The original three-profile demonstration remains a separate CLI path.

## Project Structure

| Path | Responsibility |
|---|---|
| `streamlit_app.py` | Visual interface, embedded background, approval controls, summaries, evidence, and CSV export |
| `src/main.py` | CLI, approval prompts, generation orchestration, and output |
| `src/recommender.py` | Catalog loading, scoring, and ranking |
| `src/curator.py` | Workout requests and activity routing |
| `src/study_curator.py` | Studying filters, tie-breaking, and approved genre broadening |
| `src/guide_retriever.py` | Activity-guide retrieval |
| `src/llm_client.py` | Gemini generation, network-error handling, and response validation |
| `src/prompts.py` | Baseline and specialized prompts with approval-context rules |
| `data/songs.csv` | Existing 18-song catalog |
| `data/curation_guides.md` | Custom activity guidance |
| `tests/` | Automated behavior tests |
| `evaluate.py` | Predefined CLI evaluation cases |
| `compare_prompts.py` | Live baseline and specialized prompt comparison |
| `diagrams/architecture.mmd` | Mermaid architecture source |
| `evidence/` | Recorded outputs and comparison results |
| `model_card.md` | Responsible-AI reflection and evaluation analysis |
| `ai_interactions.md` | Development history and workflow traces |

## Setup Instructions

### Requirements

Development and historical fresh-clone verification used
**Python 3.13.9 on Windows**.

The dependency file contains:

```text
pandas
pytest
streamlit
google-genai
httpx2
```

Dependencies are currently unpinned.

Run the following commands from the repository root unless otherwise
specified.

### 1. Clone the Repository

```cmd
git clone https://github.com/HaidaMarese/playlist-intelligence.git
cd playlist-intelligence
```

### 2. Create a Virtual Environment

On Windows:

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

For macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Setup and execution have been verified on Windows. Full macOS and Linux
verification remains future work.

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
python -m pip check
```

Observed dependency-check result in the historical fresh environment:

```text
No broken requirements found.
```

### 5. Launch the Visual Interface

```cmd
python -m streamlit run streamlit_app.py
```

Open the local URL printed in the terminal, typically:

```text
http://localhost:8501
```

To use catalog explanations:

1. Choose an activity.
2. Select the number of songs.
3. Choose a genre if studying.
4. Leave **Generate AI explanations** unchecked.
5. Click **Recommend songs**.
6. Approve or decline other genres if prompted.

Catalog explanations require no API key.

Stop the server with `Ctrl+C` in the terminal.

### 6. Run the CLI Without Gemini

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout"
python -m src.main --request "3 calm lofi songs for studying"
python -m src.main --request "3 calm jazz songs for studying"
```

These commands use catalog-based explanations and require no API key.

### 7. Configure Gemini

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

Keep the key out of source files, screenshots, logs, and Git commits.

`gemini-3.5-flash-lite` was used successfully in the recorded executions.
Model access, quotas, and availability depend on the API account and
service.

Verify configuration without printing the key:

```cmd
python -c "import os; print('API key configured:', bool(os.environ.get('GEMINI_API_KEY'))); print('Model:', os.environ.get('GEMINI_MODEL'))"
```

If Streamlit is already running, stop it and restart it from the terminal
where these variables are configured:

```cmd
python -m streamlit run streamlit_app.py
```

The running app inherits the environment of the terminal that launched it.

### 8. Enable AI in Streamlit

For baseline explanations:

1. Check **Generate AI explanations**.
2. Uncheck **Use concise curator style with AI**.
3. Click **Recommend songs**.

A successful result displays:

```text
Explanation mode · Gemini · Baseline
```

For specialized explanations:

1. Check **Generate AI explanations**.
2. Check **Use concise curator style with AI**.
3. Click **Recommend songs**.

A successful result displays:

```text
Explanation mode · Gemini · Specialized
```

The concise-style option applies only when AI explanations are enabled.

If generation fails, the application identifies the catalog fallback
and preserves catalog recommendations.

### 9. Run the CLI With AI

Baseline prompt:

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai
```

Specialized prompt:

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai --specialized
```

Studying request with an approval decision:

```cmd
python -m src.main --request "3 calm jazz songs for studying" --ai
```

Answer `y` to include eligible tracks from other genres.

### 10. Run Checks and Evaluation

```cmd
python -m py_compile streamlit_app.py src/prompts.py
python -m pytest -q
python evaluate.py
git diff --check
```

The automated test suite and CLI evaluation harness make no live Gemini
requests.

Run the live prompt comparison separately:

```cmd
python compare_prompts.py
```

The comparison makes two model requests and writes
`evidence/prompt_comparison.md`.

The committed comparison measurements describe the earlier prompt
version. Running this command with the revised prompts creates a new
experiment; its results may differ.

## Supported Requests and Options

| Example or option | Behavior |
|---|---|
| `3 upbeat songs for a workout` | Retrieve and rank suitable workout tracks |
| `Give me 3 upbeat songs for a workout` | Same request with an optional introductory phrase |
| `3 calm lofi songs for studying` | Preserve lofi and apply studying rules |
| `3 calm jazz songs for studying` | Ask before broadening when exact matches are insufficient |
| `--ai` | Generate CLI explanations with Gemini |
| `--ai --specialized` | Use the few-shot curator style in the CLI |

Requests support counts from **1 to 10**. Fewer tracks may be returned
when the active constraints cannot supply the requested count.

The CLI parser accepts the documented request patterns. The Streamlit
interface builds requests from the selected controls.

## Reproducible Execution Evidence

The following examples summarize observed executions. Wrapped lines and
table formatting are condensed for readability.

Earlier approval logs were recorded before instrumentalness tie-breaking
was added. The historical fresh-clone example below includes the
instrumentalness evidence.

Live model wording can vary between runs.

### Example 1 — Revised Specialized Workout in Streamlit

Selections:

```text
Activity: Workout
Number of songs: 3
Generate AI explanations: Enabled
Concise curator style: Enabled
```

Observed output excerpt:

```text
Request: 3 upbeat songs for a workout
Explanation mode: Gemini · Specialized

Selected tracks: 3
Distinct artists: 3
Average energy: 0.91

Neon Tide | Score: 1.98
Mood: energizing. Energy: 0.88. Fits your workout and is close to the guide target of 0.90.
[Source: data/curation_guides.md#workout; catalog ID: 11]

Storm Runner | Score: 0.99
Mood: intense. Energy: 0.91. Fits your workout and is slightly above the guide target of 0.90.
[Source: data/curation_guides.md#workout; catalog ID: 3]

Gym Hero | Score: 0.97
Mood: intense. Energy: 0.93. Fits your workout and is above the guide target of 0.90.
[Source: data/curation_guides.md#workout; catalog ID: 5]
```

All three explanations used correct mood and energy labels, stayed
within the 25-word target excluding appended references, and avoided
unsupported approval claims.

This is a manually transcribed record of one live Streamlit execution:

[Revised specialized workout evidence](evidence/workout_specialized_revised.txt)

### Example 2 — Declining Other Genres

Command:

```cmd
python -m src.main --request "3 calm jazz songs for studying"
```

Historical observed interaction excerpt:

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

The requested genre remains active after declining.

The Streamlit **Keep my genre** action was also manually checked and
returned Coffee Shop Stories only.

### Example 3 — Approving Other Genres

Command:

```cmd
python -m src.main --request "3 calm jazz songs for studying" --ai
```

Answer `y` at the prompt.

The recorded approved search returned:

| Track | Genre | Score | Status |
|---|---|---:|---|
| Coffee Shop Stories | jazz | 2.98 | Requested genre |
| Focus Flow | lofi | 1.95 | Approved alternative |
| Library Rain | lofi | 1.00 | Approved alternative |

The historical Gemini run identified the lofi tracks as approved
alternatives. One explanation described energy `0.37` as “matching”
the target `0.35`, illustrating the need to review numerical wording.

The Streamlit approval workflow was also manually checked. It returned
the same three tracks, identified the alternative genres, and displayed
an average energy of `0.37`.

### Guardrail Example — Blank Input

```cmd
python -m src.main --request ""
```

Observed error excerpt:

```text
Loaded songs: 18
main.py: error: Enter a playlist request, such as '3 upbeat songs for a workout'.
```

### Observed Fallback Behavior

During development, a live CLI request returned:

```text
AI explanation unavailable. Showing catalog-based explanations.
Reason: 504 DEADLINE_EXCEEDED.
```

The application continued displaying catalog recommendations.

A Streamlit run without configured environment variables displayed:

```text
Explanation mode · Catalog fallback

AI explanations are unavailable.
Your playlist uses catalog-based explanations.
```

The three workout recommendations remained available.

After configuring the environment variables and restarting Streamlit,
baseline and specialized Gemini generation succeeded.

### Simulated Connection-Failure Verification

The model-client test raises a simulated connection error and verifies
that it becomes a handled application error.

The CLI test simulates a connection failure while creating the Gemini
client. It verifies the fallback notice and the continued presence of
Neon Tide, Storm Runner, and Gym Hero.

These checks make no live API requests.

### Evidence Files

- [Earlier workout AI execution](evidence/workout_ai.txt)
- [Revised specialized workout](evidence/workout_specialized_revised.txt)
- [Declined studying search](evidence/studying_declined.txt)
- [Approved studying search](evidence/studying_approved.txt)
- [Approved studying search with AI](evidence/studying_approved_ai.txt)
- [Automated test log](evidence/tests.txt)
- [Evaluation summary](evidence/evaluation.txt)
- [Historical baseline and specialized comparison](evidence/prompt_comparison.md)

Saved logs represent the implementation and prompts used when recorded.
They are not all captures of the latest revision.

## Reliability and Evaluation

### Automated Tests

After the approval-wording prompt revision, the observed result was:

```cmd
python -m pytest -q
```

```text
41 passed in 0.99s
```

Test duration varies between runs.

Coverage includes:

- Original recommendation behavior.
- Blank inputs and invalid counts.
- Guide retrieval and malformed rules.
- Guide changes affecting filtering.
- Studying genre, mood, and energy constraints.
- Approved and declined broader searches.
- Missing approval input.
- Model JSON, IDs, duplicates, completeness, and length.
- Instrumentalness breaking equal-score ties before result truncation.
- Primary relevance taking priority over instrumentalness.
- Conversion of simulated connection failures into handled errors.
- CLI fallback after a simulated connection failure.

A controlled instrumentalness test verifies that a stronger mood match
ranks first and higher instrumentalness selects between otherwise
equally scored candidates.

These tests do not establish the factual accuracy of every live
explanation or provide automated coverage of the complete Streamlit UI.

### CLI Evaluation Harness

```cmd
python evaluate.py
```

Observed result:

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

The pass rate applies to these eight predefined scenarios. Listener
satisfaction and broader explanation quality require separate evaluation.

### Visual Interface Verification

The Streamlit interface was manually exercised on Windows.

| Check | Observed result |
|---|---|
| Workout request | Three expected tracks displayed |
| Workout summary | 3 tracks, 3 artists, average energy 0.91 |
| Studying jazz, decline alternatives | Coffee Shop Stories only |
| Studying jazz, approve alternatives | Coffee Shop Stories, Focus Flow, and Library Rain |
| Alternative labels | Lofi tracks identified after approval |
| Catalog evidence | Track attributes and guide source displayed |
| Baseline AI mode | Gemini · Baseline displayed |
| Specialized AI mode | Gemini · Specialized displayed |
| Missing API configuration | Identified catalog fallback with recommendations preserved |
| Revised specialized wording | No unsupported workout approval claims in the reviewed run |

The interface also provides CSV download and clear-results controls.
Comprehensive automated UI, accessibility, and cross-browser checks
remain future work.

### Review of Observed and Tested Behavior

| Case | Criterion | Result | Evidence type |
|---|---|---|---|
| Initial workout filter | Respect upbeat intent | Needed revision: selected a sad track | Manual execution review |
| Revised workout filter | Apply energy and suitable moods | Winter Signal excluded | Execution and tests |
| Studying request, decline | Preserve requested genre | Exact genre match retained | Execution and tests |
| Studying request, approve | Broaden only with approval | Eligible alternatives included | Execution and tests |
| Historical numeric wording | Distinguish nearby and exact values | Imprecise wording observed | Live execution review |
| Earlier specialized workout | Avoid invented approval | Unsupported approval wording observed | Live execution review |
| Revised specialized workout | Avoid invented approval | Correct wording in one reviewed run | Live execution review |
| API 503/504 response | Preserve recommendations | Identified fallback observed | Live execution review |
| Connection failure | Preserve recommendations | Simulated tests passed | Automated tests |

## Stretch Features and Evidence

### Multi-Source RAG

The app combines the song catalog with a custom activity guide.

The initial workout filter used energy alone and recommended Winter
Signal. Adding suitable mood rules removed that sad track. The revised
playlist contained Neon Tide, Storm Runner, and Gym Hero.

A guide-threshold test confirms that changing the retrieved minimum
energy changes which tracks are eligible.

For studying, the retrieved guide activates an instrumentalness
preference when primary scores are equal.

These changes improve alignment with the project's activity rules.
Listener enjoyment has not been measured.

### Agentic Decision Workflow

The runtime workflow validates, retrieves, ranks, checks the result
count, requests approval when needed, and searches again after approval.

The decision chain is implemented in Python. Listener approval controls
genre broadening through a CLI prompt or Streamlit buttons.

Actions, intermediate decisions, and observed results are documented in
[ai_interactions.md](ai_interactions.md) and the linked execution logs.

### Specialization

The specialized prompt adds few-shot examples and requests concise,
consistently labeled evidence.

A historical live comparison produced:

| Style | Average words | At most 25 words | Correct mood labels | Correct energy labels |
|---|---:|---:|---:|---:|
| Baseline | 23.3 | 3/3 | 0/3 | 0/3 |
| Specialized | 16.0 | 3/3 | 3/3 | 3/3 |

Average length decreased by approximately **31%**.

The baseline also used correct catalog facts. Label scores measure
compliance with the specialized format.

The comparison used one workout request and one generation per style.
It describes the prompt version used before the approval-wording revision.

The revised prompt was reviewed in a separate live workout run. That
run does not replace the earlier baseline-versus-specialized experiment.

Full outputs and interpretation appear in:

- [model_card.md](model_card.md)
- [Historical prompt comparison](evidence/prompt_comparison.md)
- [Revised specialized workout](evidence/workout_specialized_revised.txt)

### Evaluation Harness

`evaluate.py` executes the actual CLI on predefined inputs, checks exit
codes and expected behavior, and prints a summary.

The verified run passed **8/8 cases**.

## Design Decisions

| Decision | Reason and trade-off |
|---|---|
| Reuse Project 3 scoring | Keeps ranking inspectable while inheriting its weighting assumptions |
| Retrieve activity guidance | Makes rules traceable to a document but requires predictable formatting |
| Keep selection in Python | Provides reproducible ranking and constraint handling |
| Use Gemini for explanations | Adds readable explanations with service dependencies and wording risks |
| Require approval to broaden genre | Gives listeners control over changing an explicit preference |
| Use instrumentalness for equal scores | Applies a secondary preference while keeping primary relevance first |
| Validate model output | Rejects structural errors; semantic accuracy needs further review |
| Preserve catalog fallback | Keeps recommendations available during handled generation failures |
| Reuse ranking modules in Streamlit | Provides visual controls around the existing recommendation logic |
| Embed the background | Keeps the visual design in one Python file without a separate image asset |
| Simulate network errors in tests | Exercises failure handling without relying on a live outage |
| Separate few-shot contexts | Reduces transfer of approval language into unrelated workout requests |

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

The original options remain available:

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
use activity-specific ranking settings.

Earlier experiments and profile comparisons remain documented in
[model_card.md](model_card.md) and
[ai_interactions.md](ai_interactions.md).

## Limitations

- The catalog contains only 18 songs and includes illustrative metadata.
- Several genres have sparse coverage.
- CLI parsing supports specific documented request patterns.
- Activity moods and thresholds reflect design assumptions.
- Guide parsing depends on documented phrases and section headings.
- Structural validation does not verify every generated factual claim.
- Live generation can fail or vary between runs.
- Prompt revisions reduce observed wording problems without guaranteeing
  that future responses will always comply.
- Instrumentalness affects only equal primary scores.
- Missing instrumentalness defaults to `0.0`, which can disadvantage
  incomplete records when primary scores are equal.
- The current app provides recommendations rather than audio playback.
- The Streamlit interface has been manually reviewed; comprehensive
  automated UI testing remains future work.
- Dependencies are unpinned, so future installations may resolve
  different package versions.
- Full setup verification on macOS and Linux remains future work.
- Listener enjoyment and satisfaction have not been measured.

## Future Improvements

- Expand beyond the 18-song illustrative catalog by integrating real
  tracks and reliable metadata from an authorized music source.
- Add playable previews through a music service that permits playback
  or embedding, so listeners can sample recommended tracks.
- Collect listener feedback on whether recommendations fit their
  activity and preferences, then use that feedback to evaluate and
  improve ranking rules.
- Add factual checks for generated numeric comparisons and claims
  about approved alternative genres.
- Repeat baseline-versus-specialized comparisons with the revised
  prompts across more requests and multiple runs.
- Add dedicated timeout tests and broader network-failure scenarios.
- Expand tests for missing metadata and instrumental-preference activation.
- Add automated Streamlit workflow tests.
- Review accessibility, mobile layouts, and cross-browser behavior.
- Pin dependency versions for more precise environment reproduction.
- Verify the latest visual interface and prompt revision from a fresh clone.
- Verify setup and execution on macOS and Linux.

## Historical Fresh-Clone Verification

I cloned the GitHub repository into `playlist-intelligence-verify`,
created a new virtual environment, and installed dependencies from
`requirements.txt` using Python 3.13.9 on Windows.

The verified revision was `2ce6823`, before the Streamlit interface
and later prompt revision were added.

| Check | Observed result |
|---|---|
| Dependency installation | Successful |
| `python -m pip check` | No broken requirements found |
| `python -m pytest -q` | 41 passed in 1.23s |
| `python evaluate.py` | 8/8 cases passed |
| Studying CLI request | Focus Flow, Library Rain, and Midnight Coding returned |

The catalog demonstration used:

```cmd
python -m src.main --request "3 calm lofi songs for studying"
```

Observed output excerpt:

```text
Loaded songs: 18

Playlist request: 3 calm lofi songs for studying
Explanation mode: catalog scoring

Focus Flow | Score: 3.95
genre match (+2.00), mood match (+1.00), energy similarity (+0.95);
studying guide match (energy 0.40, mood focused);
instrumentalness 0.82 (tie-break preference);
genre status: requested genre;
source: data/curation_guides.md#studying

Library Rain | Score: 3.00
genre match (+2.00), energy similarity (+1.00);
studying guide match (energy 0.35, mood chill);
instrumentalness 0.92 (tie-break preference);
genre status: requested genre;
source: data/curation_guides.md#studying

Midnight Coding | Score: 2.93
genre match (+2.00), energy similarity (+0.93);
studying guide match (energy 0.42, mood chill);
instrumentalness 0.88 (tie-break preference);
genre status: requested genre;
source: data/curation_guides.md#studying
```

This verification covered installation, dependency compatibility,
automated checks, and catalog execution at that revision.

The visual interface and live Gemini generation were checked separately
during development. A fresh-clone check of the latest version remains
future work.

## Reflection

Extending the recommender taught me that matching a numeric feature is
only part of satisfying a request. A high-energy song can still conflict
with an upbeat mood, and a readable explanation can contain unsupported
wording.

I learned to inspect outputs, revise rules, test failure cases, and
preserve evidence. Instrumentalness tie-breaking showed how a secondary
preference can influence selection while primary relevance stays first.

The unsupported approval wording demonstrated that structural validation
and factual review serve different purposes. The response had valid IDs
and format, but still needed a prompt revision and another live check.

Building the Streamlit interface helped make the system's decisions
visible through approval controls, scores, evidence panels, and fallback
notices.

The graded responsible-AI reflection, accepted and revised AI suggestions,
limitations, misuse analysis, and testing surprises are documented in
[model_card.md](model_card.md).

## Presentation and Portfolio

The planned 5–7 minute Engineer's Pitch covers:

- **The Problem** — Find activity-appropriate tracks and explain the picks.
- **The Logic** — Retrieve guidance, rank songs, and generate explanations.
- **The Reliability** — Demonstrate tests, approval controls, validation,
  and fallback behavior.
- **The Reflection** — Explain what testing revealed and what changed.

The demonstration includes a specialized workout playlist and a studying
request that requires a listener decision.


### Portfolio Reflection

This project shows my approach to building understandable AI systems.
I extended an existing Python recommender, integrated retrieved guidance
and model-generated explanations, and added a Streamlit interface.
I verified key behaviors with automated tests and recorded executions,
then revised rules and prompts when review exposed problems. Listener
approval and catalog fallback make preference changes and generation
failures visible.

[GitHub repository](https://github.com/HaidaMarese/playlist-intelligence)

## Author

**Haida Makouangou**

B.S. in Computer Science, UNC Charlotte, Cum Laude

Built for CodePath AI110.
