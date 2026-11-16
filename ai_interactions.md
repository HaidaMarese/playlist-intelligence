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

- The assistant proposed a `SCORING_MODES` dictionary in
  `src/recommender.py` that maps modes to genre, mood, and energy weights.
- It updated `score_song()` to use the selected weights in the score
  and explanation.
- It updated `recommend_songs()` to pass the mode to `score_song()`.
- It added `argparse` support for `--mode` in `src/main.py`, with
  `genre-first` as the default.

**What did you verify or fix manually?**

I fixed a circular import after the CLI import ended up in
`src/recommender.py`. I kept that import in `src/main.py`, where the CLI
uses it, and kept the scoring definitions in `src/recommender.py`.

I ran both scoring modes. Both runs loaded 18 songs. I compared the
Chill Lofi rankings and checked the scoring explanations.

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

- It added the `--diversity` flag and passed it to `recommend_songs()`.
- It updated ranking to score each song once and select tracks one
  at a time when diversity is enabled.
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
tracks are by LoRoom, so Focus Flow received the penalty in each mode.

| Scoring mode | Focus Flow without diversity | Focus Flow with diversity |
|---|---|---|
| Genre-First | #3, 2.85 | #3, 2.35 |
| Energy-Focused | #4, 2.70 | #4, 2.20 |

Both diversity runs displayed `artist diversity penalty (-0.50)`.
Focus Flow's score dropped by 0.50 and its rank stayed the same within
each mode. Both starter tests passed at this stage.

### Optional Challenge 4 — Visual Summary Table

**What task did you give the agent?**

I asked the VS Code coding assistant to add an optional table view for
the top five recommendations. I wanted scores and reasons to be easier
to compare across songs.

**Prompts used**

> Add a `--table` flag to `src/main.py` for Optional Challenge 4. Use Python’s standard library to display Rank, Song, Artist, Score, and Reasons in aligned columns. Wrap long explanations and include the artist diversity penalty whenever it applies. Keep the current list format as the default and make `--table` work with `--mode` and `--diversity`.

**What did the agent generate or change?**

The assistant added `--table` and a `print_recommendation_table()` helper
in `src/main.py`. It formats results as five aligned columns and wraps
long explanations under Reasons.

**What did you verify or fix manually?**

```cmd
python -m src.main
python -m src.main --table
python -m src.main --mode energy-focused --diversity --table
python -m pytest
```

The default command loaded 18 songs and printed the original list.
The table showed all five columns for all three profiles. Its rankings
and scores matched the list output.

In the combined run, Focus Flow ranked fourth for Chill Lofi at 2.20.
Its explanation included `artist diversity penalty (-0.50)`.

Both starter tests passed at this stage.

---

## Design Pattern (SF10)

**Which design pattern did you use?**

For Challenge 2, I used a lightweight, Strategy-style design. Each mode
supplies a named set of weights to the same scoring function.

**How did AI help you brainstorm or implement it?**

The assistant suggested a dictionary of weight sets because both modes
use the same formula and differ in their weights. This let me reuse
the scoring and ranking code.

**How does the pattern appear in the code?**

`SCORING_MODES` in `src/recommender.py` stores weights in genre, mood,
and energy order.

- `genre-first` uses `(2.0, 1.0, 1.0)`.
- `energy-focused` uses `(1.0, 1.0, 2.0)`.

`src/main.py` passes the selected mode to `recommend_songs()`, which
passes it to `score_song()`.

Challenge 1 adds feature contributions during scoring.
Challenge 3 applies the artist penalty during ranking.
Challenge 4 formats the ranked results.

---

## Project 4 — Playlist Intelligence

> Project 4 extends Project 3 using the existing 18-song catalog and
> scoring functions. Development was guided step by step. I applied
> proposed changes in VS Code and ran verification commands myself.

### AI-Assisted Development Workflow

**What task did you give the assistant?**

I asked for guidance through the required features and all four optional
enhancements. I requested complete files that I could copy into VS Code,
then ran commands and shared their outputs.

**Prompts used**

These are paraphrases of my requests.

- Extend my existing recommender to meet the assignment and rubric.
- Give me complete updates to the Python modules.
- Explain whether Python or Gemini selects the songs.
- Keep the existing catalog.
- Check our progress against Steps 0–6 and submission requirements.
- Update documentation to match verified results.
- Add connection-failure handling and tests.
- Verify installation and execution from a separate clone.

**What did the assistant generate or change?**

- `src/curator.py` handles workout requests and activity routing.
- `src/guide_retriever.py` retrieves activity-guide sections.
- `data/curation_guides.md` defines workout and studying guidance.
- `src/llm_client.py` generates and validates explanations and handles
  network failures.
- `src/study_curator.py` applies studying rules, instrumentalness
  tie-breaking, and approved genre broadening.
- `src/main.py` connects input, retrieval, approval, generation, and display.
- `src/prompts.py` builds baseline and specialized prompts.
- `evaluate.py` evaluates predefined CLI cases.
- `compare_prompts.py` measures live explanation differences.
- Automated tests verify behavior and guardrails.
- `diagrams/architecture.mmd` documents the request workflow.

**What did you verify or fix manually?**

I corrected an indentation problem that made studying dispatch
unreachable.

The assistant initially used the reserved pytest parameter name
`request`. Renaming it to `playlist_request` fixed collection.

I reactivated the project environment after discovering that package
installation used my user-wide Python installation.

I removed an unused variable and applied corrected regular expressions
in the comparison script.

I corrected an encoding issue in the evaluation title by replacing its
long dash with a standard hyphen.

### Multi-Source Retrieval and Grounded Generation

**What task was addressed?**

I wanted explanations to use the song catalog and custom activity
guidance.

**What changed in the application?**

Python retrieves the activity guide, applies mood and energy rules,
and ranks eligible catalog tracks. With `--ai`, Gemini receives those
tracks, scoring evidence, the request, and the guide.

The response validator checks JSON format, IDs, duplicates, completeness,
and explanation length.

**What did you verify?**

The initial energy-only workout filter selected Winter Signal, which
has sad and melancholic tags. Adding suitable mood rules removed it.

| Version | Filtering behavior | Observed result |
|---|---|---|
| Initial workout implementation | Energy threshold only | Winter Signal appeared |
| Revised implementation | Retrieved energy and mood rules | Winter Signal excluded |
| Stricter guide test | Minimum energy increased from 0.75 to 0.90 | Lower-energy candidate excluded |

The revised workout playlist contained Neon Tide, Storm Runner,
and Gym Hero.

I checked the threshold change manually. An automated test confirmed
that changing the guide changes selection.

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai
python -m src.main --request "3 calm lofi songs for studying" --ai
```

Successful Gemini outputs used retrieved mood, energy, and guidance.

[Recorded workout execution](evidence/workout_ai.txt)

The observed improvement is alignment with project rules. Listener
enjoyment has not been measured.

**What reliability issues did you observe?**

Some requests returned 503 high-demand or 504 deadline errors. The app
displayed identified catalog-based fallbacks.

The tested 2.5 models reported that they were unavailable to new users.
Successful full generation was verified with `gemini-3.5-flash-lite`.

Some explanations used imprecise wording about nearby and exact energy
values. Structural validation checks format and IDs. Factual wording
still requires review.

### Agentic Workflow Enhancement — Studying Playlist Approval

**What task was addressed?**

I wanted the application to detect insufficient matches and ask before
including other genres.

**What changed in the application?**

- The initial search preserves the requested genre.
- A shortage triggers an approval prompt.
- Explicit `y` or `yes` authorizes a broader search.
- Declining, pressing Enter, or reaching end-of-input preserves genre.
- Broadening retains the studying mood and energy rules.
- Catalog explanations label approved alternatives.
- Gemini's input includes the listener's approval.

**Observed workflow trace**

Request — `3 calm jazz songs for studying`

| Step | Action | Observed result | Next decision |
|---|---|---|---|
| 1 | Validate request | Count 3, genre jazz, activity studying | Retrieve guide |
| 2 | Retrieve guidance | Target 0.35, maximum 0.50, suitable moods | Filter and rank |
| 3 | Search jazz | Coffee Shop Stories is the only match | Ask for approval |
| 4A | Listener enters N | Broadening declined | Return exact match |
| 4B | Listener enters y | Broadening approved | Search other genres |
| 5B | Rank broader results | Coffee Shop Stories, Focus Flow, Library Rain | Label and display |

**What did you verify manually?**

| Decision | Song | Genre | Score | Status |
|---|---|---|---:|---|
| Decline | Coffee Shop Stories | jazz | 2.98 | Requested genre |
| Approve | Coffee Shop Stories | jazz | 2.98 | Requested genre |
| Approve | Focus Flow | lofi | 1.95 | Approved alternative |
| Approve | Library Rain | lofi | 1.00 | Approved alternative |

**Reproducible commands**

```cmd
echo n| python -m src.main --request "3 calm jazz songs for studying"
echo y| python -m src.main --request "3 calm jazz songs for studying"
```

**Execution logs**

- [Declined search](evidence/studying_declined.txt)
- [Approved search](evidence/studying_approved.txt)

These logs record the workflow before instrumentalness tie-breaking.
The decision chain is implemented in Python and includes human approval.

**Historical verification milestone**

After adding approval tests:

```text
32 passed in 0.51s
```

| Scenario | Verified behavior |
|---|---|
| Answer n or N | Preserve jazz |
| Press Enter | Preserve jazz |
| Answer y or YES | Include eligible alternatives |
| Input unavailable | Preserve jazz |
| Enough exact matches | Avoid approval prompt |

**Gemini verification after approval**

```cmd
echo y| python -m src.main --request "3 calm jazz songs for studying" --ai > evidence\studying_approved_ai.txt 2>&1
```

The recorded run displayed `Explanation mode: Gemini`. Coffee Shop
Stories was described as jazz. Focus Flow and Library Rain were
described as approved lofi alternatives.

[Recorded approved AI execution](evidence/studying_approved_ai.txt)

### Studying Instrumentalness Preference

**What task was addressed?**

The guide requested an instrumental preference that the initial
studying implementation had not applied.

**What changed in the application?**

When the guide contains the documented preference sentence, candidates
are preordered by descending instrumentalness.

The ranker preserves that order for equal primary scores. Higher
relevance scores rank first.

Missing instrumentalness defaults to `0.0`. Equal scores and equal
instrumentalness preserve catalog order.

**What did you verify?**

| Test track | Mood | Energy | Instrumentalness |
|---|---|---:|---:|
| Lower Instrumentalness | chill | 0.35 | 0.10 |
| Higher Instrumentalness | chill | 0.35 | 0.90 |
| Stronger Mood Match | focused | 0.35 | 0.00 |

For a two-track request, the test verified:

```text
Stronger Mood Match
Higher Instrumentalness
```

This checks score priority and tie-breaking before result truncation.

**Historical verification milestone**

```text
39 passed in 1.19s
```

The evaluation harness also continued to pass eight cases.

### Specialization Enhancement — Implemented and Measured

**What task was addressed?**

I wanted concise explanations with clearly labeled catalog evidence.

**What changed in the application?**

- `src/prompts.py` provides baseline and few-shot specialized prompts.
- The specialized style requests at most 25 words.
- It requests exact mood and two-decimal energy labels.
- `src/llm_client.py` accepts a `specialized` setting.
- `src/main.py` exposes `--specialized`, requiring `--ai`.
- `compare_prompts.py` records outputs and measurements.

**Application command**

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai --specialized
```

**Observed example**

```text
Mood: energizing. Energy: 0.88. Fits a workout and is close to the guide target of 0.90.
```

**Comparison command**

```cmd
python compare_prompts.py
```

Both styles used `gemini-3.5-flash-lite`, the same request, three selected
tracks, and retrieved guide.

| Style | Average words | At most 25 words | Correct mood labels | Correct energy labels |
|---|---:|---:|---:|---:|
| Baseline | 23.3 | 3/3 | 0/3 | 0/3 |
| Specialized | 16.0 | 3/3 | 3/3 | 3/3 |

Average length decreased by approximately 31%.

Both styles used correct mood and energy facts in the observed outputs.
Label scores measure style compliance. Overall factual accuracy
requires separate review.

The comparison used one generation per style. Results may vary.

- [Actual outputs and measurements](evidence/prompt_comparison.md)
- [Required model-card comparison](model_card.md)

### Evaluation Harness Enhancement — Implemented and Verified

**What task was addressed?**

I wanted a reproducible script that exercises the CLI and prints results.

**What changed in the application?**

`evaluate.py` launches the CLI using the active Python interpreter,
supplies inputs, captures output, and checks exit codes and expected
or excluded text.

Each case has a timeout. Failures print diagnostic information.
The script returns a nonzero exit code when a case fails.

**Observed result**

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

[Saved evaluation output](evidence/evaluation.txt)

The harness verifies these predefined CLI scenarios. Model-response
tests and live generation logs provide additional evidence.

### Network-Failure Handling

**What task was addressed?**

I wanted connection failures to trigger the catalog fallback.

**What changed in the application?**

- The model client catches `httpx2.TransportError` and `OSError`.
- It converts them into a handled `ValueError`.
- The CLI displays a fallback notice and catalog recommendations.
- `httpx2` is included in `requirements.txt`.

**What did you verify?**

| Test | Simulated failure | Verified behavior |
|---|---|---|
| Model-client test | Connection error during generation | Handled application error |
| CLI fallback test | Connection error during client creation | Fallback and catalog tracks displayed |

The CLI test checks this notice:

```text
AI explanation unavailable. Showing catalog-based explanations.
```

It verifies that Neon Tide, Storm Runner, and Gym Hero remain available
and that successful Gemini generation is not reported.

These tests make no live API calls.

Timeout exceptions are covered by the transport-error handler.
A dedicated timeout-specific test remains a future improvement.

**Historical verification milestone**

```text
41 passed in 0.89s
```

### Architecture and Documentation

The request workflow is documented in
[diagrams/architecture.mmd](diagrams/architecture.mmd).

It includes retrieval, ranking, approval, generation, validation,
fallback, and testing connections.

The README includes setup instructions, demonstrations, evaluation,
and design decisions.

The model card includes limitations, misuse analysis, testing surprises,
AI collaboration, accepted and revised suggestions, and specialization
measurements.

### Fresh-Clone Verification — Completed

**What task was addressed?**

I wanted to check that the committed project could install and run
from GitHub in a separate environment.

**What did I do?**

I cloned revision `2ce6823` into `playlist-intelligence-verify`, created
a new virtual environment, and installed `requirements.txt` using
Python 3.13.9 on Windows.

**Verification commands**

```cmd
python -m pip check
python -m pytest -q
python evaluate.py
python -m src.main --request "3 calm lofi songs for studying"
```

**Observed results**

| Check | Result |
|---|---|
| Dependency installation | Successful |
| Dependency compatibility | No broken requirements found |
| Automated tests | 41 passed in 1.23s |
| CLI evaluation | 8/8 cases passed |
| Studying recommendations | Expected three tracks returned |

The studying results were:

| Rank | Song | Score | Instrumentalness |
|---|---|---:|---:|
| 1 | Focus Flow | 3.95 | 0.82 |
| 2 | Library Rain | 3.00 | 0.92 |
| 3 | Midnight Coding | 2.93 | 0.88 |

Output included scoring reasons, genre status, and the studying guide
source.

This verification covered installation, dependencies, automated checks,
and catalog execution. Live Gemini generation was verified separately
during development.

### Latest Verification Summary

| Check | Latest verified result |
|---|---|
| Automated tests | 41 passed in the fresh clone |
| CLI evaluation harness | 8/8 cases passed |
| Dependency compatibility | No broken requirements found |
| Fresh-clone studying request | Expected tracks and evidence displayed |
| Workout Gemini explanations | Successful recorded run |
| Studying Gemini explanations | Successful observed run |
| Approved alternatives with Gemini | Successful recorded run |
| Specialized prompt comparison | Outputs and measurements saved |
| Instrumentalness tie-breaking | Controlled test passed |
| Model-client connection failure | Simulated test passed |
| CLI connection-failure fallback | Simulated test passed |

### Remaining Project 4 Work

- Continue factual evaluation of generated explanations.
- Add dedicated timeout tests as a future reliability improvement.
- Refresh final execution evidence after further code changes.
- Check final documentation consistency.
- Prepare the 5–7 minute Engineer's Pitch.
- Finalize presentation materials and review the portfolio reflection.
- Record and link a Loom walkthrough if included.
- Verify any added visual interface.
- Commit and push final changes before submission.