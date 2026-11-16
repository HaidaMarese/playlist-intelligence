# AI Interactions Log

> This log records the four optional challenges from Project 3 and the
> implemented AI features and workflow evidence for Project 4.
> Project 4's graded responsible-AI reflection belongs in `model_card.md`.

---

## Agentic Workflow (SF8)

> Record the requested task, AI-assisted changes, and manual verification.

### Optional Challenge 1 — Advanced Song Features

**What task did you give the agent?**

I asked the VS Code coding assistant to add five illustrative attributes
to all 18 songs and use them in scoring when `--advanced` is enabled.
I wanted the default rankings preserved and the new flag to work with
both scoring modes, artist diversity, and table output.

**Prompts used**

> Implement Optional Challenge 1. Add five new columns to all 18 songs in `data/songs.csv`: `popularity` (0–100), `release_decade`, `detailed_mood`, `instrumentalness` (0–1), and `vocal_language`. Preserve the existing rows and columns, and treat the added values as illustrative metadata. Add an `--advanced` option that uses all five attributes in scoring and explains how each contributed. Keep the existing scores and rankings when `--advanced` is omitted. Make the option work with `--mode`, `--diversity`, and `--table`. Show me how to verify that each new attribute can affect a score.

For the follow-up check, I asked the assistant to use the existing scoring
function with the Chill Lofi profile and Midnight Coding. I asked it to
start with a fresh copy of the song for each trial, change one field at a
time, and report the original score, modified score, and difference.

**What did the agent generate or change?**

- In `data/songs.csv`, the assistant added `popularity`, `release_decade`,
  `detailed_mood`, `instrumentalness`, and `vocal_language` as illustrative
  metadata.
- In `src/recommender.py`, it added scoring and explanations for the five
  attributes.
- In `src/main.py`, it added the `--advanced` flag.

**What did you verify or fix manually?**

I reviewed the CSV diff and confirmed that the original 18 songs and
their existing fields were preserved. I ran the default, advanced, and
combined commands from the project folder.

```cmd
python -m src.main
python -m src.main --advanced
python -m src.main --advanced --mode energy-focused --diversity --table
python -m pytest
git diff --check
```

The default run matched the baseline recorded during Project 3.
For Chill Lofi, Midnight Coding moved from #2 at 3.83 in the default
run to #1 at 4.81 with `--advanced`. Its explanation showed contributions
from all five new fields.

In the combined run, Midnight Coding ranked #1 at 4.64. Focus Flow
ranked #4 at 2.99, and the table showed its
`artist diversity penalty (-0.50)`.

I reviewed the assistant's individual feature checks. The Chill Lofi
profile stayed fixed, and each trial changed one field on a fresh copy
of Midnight Coding. The original advanced score was **4.814**.

| Field changed | Replacement | Modified score | Change from original |
|---|---|---:|---:|
| Popularity | `50` | 4.749 | -0.065 |
| Release decade | `2010s` | 4.614 | -0.200 |
| Detailed mood | `energetic` | 4.614 | -0.200 |
| Instrumentalness | `0.10` | 4.670 | -0.144 |
| Vocal language | `English` | 4.614 | -0.200 |

Each field changed the score independently in this check. Both starter
tests passed at this stage, and `git diff --check` reported no whitespace
errors.

### Optional Challenge 2 — Multiple Scoring Modes

**What task did you give the agent?**

I asked the AI assistant to help turn my weight experiment into a feature
users could select from the command line. I wanted Genre-First to remain
the default and Energy-Focused to be available as a second mode.
I applied the suggested changes in VS Code and ran the checks myself.

**Prompts used**

These are paraphrases of my requests during the coding session.

- Give me the complete `src/recommender.py` with both scoring modes and
  one shared scoring function.
- Update `src/main.py` so users can select a mode from the command line.
  Keep the existing output format and identify this as an optional challenge.
- Help me fix the circular import shown in the terminal traceback.

**What did the agent generate or change?**

- In `src/recommender.py`, the assistant proposed a `SCORING_MODES`
  dictionary that maps each mode to its genre, mood, and energy weights.
- It updated `score_song()` to use the selected weights in both the score
  and its explanation.
- It updated `recommend_songs()` to pass the mode to `score_song()`.
- In `src/main.py`, it added `argparse` support for `--mode` and set
  `genre-first` as the default.

**What did you verify or fix manually?**

I fixed a circular import after the CLI import ended up in
`src/recommender.py`. I kept that import in `src/main.py`, where the CLI
uses it, and kept the scoring definitions in `src/recommender.py`.

I ran `python -m src.main` and `python -m src.main --mode energy-focused`.
Both runs loaded 18 songs. I compared the Chill Lofi rankings and checked
that each explanation showed the points awarded in the selected mode.

| Song | Genre-First | Energy-Focused |
|---|---|---|
| Focus Flow | #3, 2.85 | #4, 2.70 |
| Spacewalk Thoughts | #4, 1.97 | #3, 2.94 |

Both starter tests passed at this stage.

### Optional Challenge 3 — Artist Diversity

**What task did you give the agent?**

I asked the VS Code coding assistant to add an optional artist diversity
penalty that works with both scoring modes and preserves the default
rankings when the flag is omitted.

**Prompts used**

> Add Optional Challenge 3 to my music recommender. Add a `--diversity` flag in `src/main.py` that works with both existing scoring modes. In `recommend_songs()`, score each song once using the selected mode. When diversity is enabled, select recommendations one at a time. Subtract 0.50 points from a candidate’s base score if its artist already appears in the selected results. Use the adjusted score to pick the next song, keep CSV order for ties, and display the penalty in the explanation when applied. Use a single penalty per candidate and leave the default rankings and output unchanged when the flag is omitted. Show me how to verify the change using my Chill Lofi profile.

**What did the agent generate or change?**

- In `src/main.py`, the assistant added the `--diversity` flag and passed
  it to `recommend_songs()` along with the selected scoring mode.
- In `src/recommender.py`, it updated `recommend_songs()` to score each
  song once and select recommendations one at a time when diversity is
  enabled.
- A candidate receives one 0.50-point deduction if its artist already
  appears in the selected results.
- Selection uses the adjusted score, preserves CSV order for ties,
  and includes any deduction in the explanation.

**What did you verify or fix manually?**

I checked the repository path after the assistant requested an edit in
another copy of the project. I continued in the Foundations project on
`experiment/artist-diversity`.

```cmd
python -m src.main
python -m src.main --diversity
python -m src.main --mode energy-focused --diversity
python -m pytest
```

The default run loaded 18 songs and matched the Project 3 baseline.

For Chill Lofi, Midnight Coding was selected before Focus Flow. Both
tracks are by LoRoom, so Focus Flow received the penalty in each scoring
mode when diversity was enabled.

| Scoring mode | Focus Flow without diversity | Focus Flow with diversity |
|---|---|---|
| Genre-First | #3, 2.85 | #3, 2.35 |
| Energy-Focused | #4, 2.70 | #4, 2.20 |

Both diversity runs displayed `artist diversity penalty (-0.50)` in
Focus Flow's explanation. Its score dropped by 0.50 and its rank stayed
the same within each mode. Both starter tests passed at this stage.

### Optional Challenge 4 — Visual Summary Table

**What task did you give the agent?**

I asked the VS Code coding assistant to add an optional table view for
the top five recommendations. I wanted the table to make scores and
reasons easier to compare across songs.

**Prompts used**

> Add a `--table` flag to `src/main.py` for Optional Challenge 4. Use Python’s standard library to display Rank, Song, Artist, Score, and Reasons in aligned columns. Wrap long explanations and include the artist diversity penalty whenever it applies. Keep the current list format as the default and make `--table` work with `--mode` and `--diversity`.

**What did the agent generate or change?**

The assistant added `--table` and a `print_recommendation_table()` helper
in `src/main.py`. The helper formats recommendation results as five
aligned columns and wraps long explanations under Reasons.

**What did you verify or fix manually?**

```cmd
python -m src.main
python -m src.main --table
python -m src.main --mode energy-focused --diversity --table
python -m pytest
```

I confirmed that the default run loaded 18 songs and printed the
original list. The table showed all five columns for all three profiles.
The baseline table matched the list rankings and scores.

In the combined run, Focus Flow ranked fourth for Chill Lofi with
a score of 2.20. Its wrapped explanation included
`artist diversity penalty (-0.50)`.

Both starter tests passed at this stage.

---

## Design Pattern (SF10)

**Which design pattern did you use?**

For Challenge 2, I used a lightweight, Strategy-style design. Each mode
supplies a named set of weights to the same scoring function.

**How did AI help you brainstorm or implement it?**

The assistant suggested a dictionary of named weight sets because both
modes use the same formula and differ in their weights. This let me
reuse the scoring and ranking code and keep Genre-First as the default.

**How does the pattern appear in the code?**

`SCORING_MODES` in `src/recommender.py` stores the weights in genre, mood,
and energy order.

- `genre-first` uses `(2.0, 1.0, 1.0)`.
- `energy-focused` uses `(1.0, 1.0, 2.0)`.

`src/main.py` reads `--mode` and passes it to `recommend_songs()`.
That function passes the mode to `score_song()`, which calculates and
explains each contribution.

Challenge 1 adds optional feature contributions during scoring.
Challenge 3 applies the artist penalty during ranking.
Challenge 4 formats the ranked results for display.

---

## Project 4 — Playlist Intelligence

> Project 4 extends Project 3, Music Recommender Simulation, using the
> existing 18-song catalog and scoring functions.
> Development was guided step by step. I applied the proposed changes
> in VS Code and ran verification commands myself.

### AI-Assisted Development Workflow

**What task did you give the assistant?**

I asked the assistant to guide me through the final project, including
the required features and all four optional enhancements.

I requested complete Python files that I could copy into VS Code,
then ran commands and shared their actual outputs for verification.

**Prompts used**

These are paraphrases of my requests during development.

- Extend my existing music recommender to meet the Applied AI System
  requirements and grading rubric.
- Give me complete updates to `src/main.py`, `src/curator.py`, and
  `src/study_curator.py`.
- Explain whether Python or Gemini selects the songs.
- Keep the existing catalog and continue building on the project.
- Check our progress against Steps 0–6 and the submission requirements.
- Update the README, model card, and interaction log to match verified
  implementation results.
- Update the model client to handle connection failures and add tests
  that verify the catalog fallback.

**What did the assistant generate or change?**

- `src/curator.py` validates workout requests and applies retrieved rules.
- `src/guide_retriever.py` retrieves activity sections from the custom guide.
- `data/curation_guides.md` defines workout and studying guidance.
- `src/llm_client.py` generates explanations, validates responses, and
  converts network errors into handled application errors.
- `src/study_curator.py` applies studying rules, instrumentalness
  tie-breaking, and approved genre broadening.
- `src/main.py` connects requests, retrieval, ranking, approval,
  generation, fallback, and table output.
- `src/prompts.py` builds baseline and specialized prompts.
- `evaluate.py` evaluates predefined CLI cases.
- `compare_prompts.py` measures live explanation differences.
- Automated tests verify recommendation behavior and guardrails.
- `diagrams/architecture.mmd` documents the request workflow.

**What did you verify or fix manually?**

I applied the code in VS Code and ran the commands myself.

I corrected an indentation problem that made the studying dispatch
unreachable.

The assistant initially used `request` as a pytest parameter name.
Pytest rejected that reserved name. I applied the revision using
`playlist_request`, then reran the suite successfully.

I checked the Python interpreter after package installation used my
user-wide Python installation. Reactivating the project's `.venv`
restored the intended interpreter.

I removed an unused `energy_pattern` variable from the comparison
script and applied the corrected regular expressions.

I also corrected a character-encoding problem in the evaluation log
title by replacing its long dash with a standard hyphen.

### Multi-Source Retrieval and Grounded Generation

**What task did you give the assistant?**

I wanted explanations to use both the existing song catalog and custom
activity guidance.

**What changed in the application?**

The application retrieves records from `data/songs.csv` and an activity
section from `data/curation_guides.md`.

Python applies the guide's mood and energy rules, then ranks eligible
tracks. With `--ai`, Gemini receives the selected tracks, scoring
evidence, listener request, and retrieved guide.

Python validates returned IDs, duplicates, missing tracks, JSON format,
and explanation length before displaying generated output.

**What did you verify manually?**

The initial workout filter used energy alone and selected Winter Signal,
which has sad and melancholic tags.

Adding suitable mood rules removed it from the workout results.
The revised playlist contained Neon Tide, Storm Runner, and Gym Hero.

| Version | Retrieval and filtering behavior | Observed result |
|---|---|---|
| Initial workout implementation | Energy threshold only | Winter Signal appeared |
| Revised workout implementation | Retrieved energy and suitable-mood rules | Winter Signal excluded |
| Stricter guide test | Minimum energy changed from 0.75 to 0.90 | Lower-energy candidate excluded |

I checked the parsed threshold change manually. An automated test
confirmed that changing the guide affects the resulting selection.

Successful Gemini runs used retrieved mood, energy, and guidance in
their explanations.

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai
python -m src.main --request "3 calm lofi songs for studying" --ai
```

The recorded workout execution is available in
[evidence/workout_ai.txt](evidence/workout_ai.txt).

The observed improvement is alignment with the activity rules.
Listener enjoyment has not been measured.

**What reliability issues did you observe?**

Some generation requests returned 503 high-demand errors or 504 deadline
errors. The application displayed identified catalog-based fallbacks.

The 2.5 models tested returned messages stating that they were
unavailable to new users. Successful full playlist generation was
verified with `gemini-3.5-flash-lite`.

Generated explanations sometimes used imprecise wording about nearby
and exact energy values. Structural validation checks format and IDs.
Factual wording still needs review.

### Agentic Workflow Enhancement — Studying Playlist Approval

**What task did you give the assistant?**

I wanted the application to detect insufficient exact matches and ask
the listener before including tracks from other genres.

**What changed in the application?**

- The initial studying search preserves the requested genre.
- `src/main.py` checks whether enough tracks match.
- A shortage triggers a listener approval prompt.
- Explicit `y` or `yes` authorizes a broader search.
- Declining, pressing Enter, or reaching end-of-input preserves the
  original genre.
- The broader search keeps the studying mood and energy rules.
- Catalog explanations identify approved alternative genres.
- Gemini's input includes the listener's approval when applicable.

**Observed workflow trace**

The following table records actions and decisions observed for
`3 calm jazz songs for studying`.

| Step | Action | Observed result | Next decision |
|---|---|---|---|
| 1 | Validate the request | Count 3, genre jazz, activity studying | Retrieve the studying guide |
| 2 | Retrieve guidance | Target energy 0.35, maximum energy 0.50, suitable moods | Filter and rank catalog tracks |
| 3 | Search within jazz | Coffee Shop Stories is the only match | Request approval for other genres |
| 4A | Listener enters N | Broadening declined | Return Coffee Shop Stories |
| 4B | Listener enters y | Broadening approved | Search across genres with the same mood and energy rules |
| 5B | Rank broader candidates | Coffee Shop Stories, Focus Flow, Library Rain | Label alternative genres and display results |

**What did you verify manually?**

I ran the request twice. Answering `N` returned one track. Answering `y`
returned three.

| Listener decision | Song | Genre | Score | Status |
|---|---|---|---:|---|
| Decline | Coffee Shop Stories | jazz | 2.98 | Requested genre |
| Approve | Coffee Shop Stories | jazz | 2.98 | Requested genre |
| Approve | Focus Flow | lofi | 1.95 | Approved alternative genre |
| Approve | Library Rain | lofi | 1.00 | Approved alternative genre |

**Reproducible commands**

Run these from the project root in Windows Command Prompt.

```cmd
echo n| python -m src.main --request "3 calm jazz songs for studying"
echo y| python -m src.main --request "3 calm jazz songs for studying"
```

**Saved execution logs**

- [Declined broader search](evidence/studying_declined.txt)
- [Approved broader search](evidence/studying_approved.txt)

These logs capture the catalog-scoring approval workflow before the
instrumentalness update. The runtime decision chain is implemented in
Python and includes human approval.

**Historical verification milestone**

After adding approval tests, the suite reported:

```text
32 passed in 0.51s
```

| Approval scenario | Verified behavior | Result |
|---|---|---|
| Answer n | Preserve jazz only | Pass |
| Answer N | Preserve jazz only | Pass |
| Press Enter | Preserve jazz only | Pass |
| Answer y | Include eligible alternative genres | Pass |
| Answer YES | Include eligible alternative genres | Pass |
| Input stream unavailable | Preserve jazz only | Pass |
| Enough exact lofi matches | Return results without prompting | Pass |

**Gemini verification after approval**

I recorded the approved workflow with AI explanations:

```cmd
echo y| python -m src.main --request "3 calm jazz songs for studying" --ai > evidence\studying_approved_ai.txt 2>&1
```

The recorded run displayed `Explanation mode: Gemini`.

Coffee Shop Stories was described as jazz. Focus Flow and Library Rain
were described as approved lofi alternatives.

The observed output is saved in
[evidence/studying_approved_ai.txt](evidence/studying_approved_ai.txt).

### Studying Instrumentalness Preference

**What task was addressed?**

The studying guide said to prefer instrumental tracks when other
preferences were equal. The implementation initially used only the
guide's energy and mood rules.

**What changed in the application?**

When the retrieved guide contains the documented instrumental-preference
sentence, candidates are preordered by descending instrumentalness.

The existing ranker preserves that order for equal primary scores.
Higher primary relevance ranks first.

Missing instrumentalness values default to `0.0`. Equal scores and equal
instrumentalness preserve catalog order.

Catalog explanations identify the instrumentalness value and tie-break
preference.

**What did you verify?**

I added a controlled test with three lofi tracks:

| Track | Mood | Energy | Instrumentalness |
|---|---|---:|---:|
| Lower Instrumentalness | chill | 0.35 | 0.10 |
| Higher Instrumentalness | chill | 0.35 | 0.90 |
| Stronger Mood Match | focused | 0.35 | 0.00 |

For a request for two tracks, the verified order was:

```text
Stronger Mood Match
Higher Instrumentalness
```

The test confirms that primary relevance takes priority and that
instrumentalness resolves equal scores before results are truncated.

**Historical verification milestone**

After the instrumentalness update:

```cmd
python -m pytest -q
```

```text
39 passed in 1.19s
```

The CLI evaluation also continued to pass all eight cases.

### Specialization Enhancement — Implemented and Measured

**What task was addressed?**

I wanted a specialized explanation style that was concise and made
catalog evidence easy to identify.

**What changed in the application?**

- `src/prompts.py` provides baseline and specialized prompts.
- The specialized prompt includes illustrative few-shot examples.
- It requests at most 25 words per explanation.
- It requests exact mood and two-decimal energy labels.
- `src/llm_client.py` accepts the optional `specialized` setting.
- `src/main.py` exposes `--specialized`, requiring `--ai`.
- `compare_prompts.py` records live outputs and measurable differences.

**Application command**

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai --specialized
```

**Observed specialized example**

```text
Mood: energizing. Energy: 0.88. Fits a workout and is close to the guide target of 0.90.
```

**Comparison command**

```cmd
python compare_prompts.py
```

The comparison used `gemini-3.5-flash-lite`, the same request, the same
three selected tracks, and the same guide for both styles.

| Style | Average words | At most 25 words | Correct mood labels | Correct energy labels |
|---|---:|---:|---:|---:|
| Baseline | 23.3 | 3/3 | 0/3 | 0/3 |
| Specialized | 16.0 | 3/3 | 3/3 | 3/3 |

Average length decreased by approximately 31%.

Both styles used correct catalog mood and energy facts in the observed
outputs. Label scores measure compliance with the specialized style.
Overall factual accuracy requires separate review.

This comparison used one live generation per style. Results may vary.

Full outputs are saved in
[evidence/prompt_comparison.md](evidence/prompt_comparison.md).

The required comparison and interpretation are also documented in
[model_card.md](model_card.md).

### Evaluation Harness Enhancement — Implemented and Verified

**What task was addressed?**

I wanted a reproducible script that exercises the real CLI on predefined
requests and prints a summary.

**What changed in the application?**

`evaluate.py` launches the CLI using the active Python interpreter,
supplies predefined inputs, captures output, and checks exit codes and
expected or excluded text.

Each case has a timeout. Failed cases print diagnostic information.
The script returns a nonzero exit code if any case fails.

**Verification command**

```cmd
python evaluate.py
```

**Observed result**

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

The saved output is available in
[evidence/evaluation.txt](evidence/evaluation.txt).

This harness verifies its predefined CLI scenarios. Simulated model
tests and recorded live generation provide separate evidence.

### Network-Failure Handling

**What task was addressed?**

I wanted connection failures to trigger the catalog fallback instead of
ending the application with an unhandled traceback.

**What changed in the application?**

- `src/llm_client.py` catches `httpx2.TransportError` and `OSError`.
- It converts those errors into a `ValueError` with an actionable message.
- The existing CLI handler displays the fallback notice and catalog
  recommendations.
- `httpx2` is listed as a direct dependency in `requirements.txt`.

**What did you verify?**

Two simulated tests exercise different parts of the workflow.

| Test | Simulated failure | Verified behavior |
|---|---|---|
| Model-client test | `ConnectError` during generation | Converted into a handled `ValueError` |
| CLI fallback test | `ConnectError` while creating the client | Fallback notice and catalog recommendations displayed |

The CLI test verifies that the output includes:

```text
AI explanation unavailable. Showing catalog-based explanations.
```

It also verifies that Neon Tide, Storm Runner, and Gym Hero are displayed
and that the output does not report successful Gemini generation.

These tests make no live API calls.

Network timeout exceptions are covered by the transport-error handler.
A dedicated timeout-specific test is still pending.

**Latest observed suite result**

```cmd
python -m pytest -q
```

```text
41 passed in 0.89s
```

### Architecture and Documentation

The implemented request workflow is documented in the Mermaid source:

[diagrams/architecture.mmd](diagrams/architecture.mmd)

The diagram includes retrieval, ranking, listener approval, generation,
output validation, fallback, and testing connections.

The Project 4 README includes setup instructions, recorded input/output
examples, guardrail behavior, evaluation results, and design decisions.

The model card contains limitations, misuse analysis, testing surprises,
AI collaboration, accepted and revised suggestions, and the measured
specialization comparison.

### Latest Verification Summary

| Check | Latest verified result |
|---|---|
| Automated tests | 41 passed |
| CLI evaluation harness | 8/8 cases passed |
| Workout Gemini explanations | Successful recorded run |
| Studying Gemini explanations | Successful observed run |
| Approved alternative genres with Gemini | Successful recorded run |
| Specialized prompt comparison | Outputs and measurements saved |
| Instrumentalness tie-breaking | Controlled automated test passed |
| Model-client connection failure | Simulated test passed |
| CLI connection-failure fallback | Simulated test passed |

### Remaining Project 4 Verification

- Add dedicated timeout tests as a future reliability improvement.
- Continue factual evaluation of generated explanations.
- Refresh final execution evidence after remaining code changes.
- Check documentation for consistency with the final implementation.
- Prepare the 5–7 minute Engineer's Pitch.
- Finalize presentation materials and review the portfolio reflection.
- Record and link a Loom walkthrough if included.
- Verify setup, tests, and execution from a fresh clone.
- Commit and push final changes before submission.