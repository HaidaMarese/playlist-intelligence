# AI Interactions Log

> This log records the four optional challenges from Project 3 and the
> implemented features and workflow evidence for Project 4.
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

For the follow-up check, I asked the assistant to use the Chill Lofi
profile and Midnight Coding. Each trial used a fresh copy of the song,
changed one field, and reported the score difference.

**What did the agent generate or change?**

- Added the five attributes to `data/songs.csv`.
- Added their scoring contributions and explanations in
  `src/recommender.py`.
- Added `--advanced` in `src/main.py`.

**What did you verify or fix manually?**

I reviewed the CSV diff and confirmed that all 18 songs and their
existing fields were preserved.

```cmd
python -m src.main
python -m src.main --advanced
python -m src.main --advanced --mode energy-focused --diversity --table
python -m pytest
git diff --check
```

The default run matched the Project 3 baseline.

For Chill Lofi, Midnight Coding moved from #2 at 3.83 to #1 at 4.81 with
`--advanced`. Its explanation included all five new attributes.

In the combined run, Midnight Coding ranked #1 at 4.64. Focus Flow ranked
#4 at 2.99 with `artist diversity penalty (-0.50)`.

The original advanced score for the individual feature check was
**4.814**.

| Field changed | Replacement | Modified score | Change |
|---|---|---:|---:|
| Popularity | `50` | 4.749 | -0.065 |
| Release decade | `2010s` | 4.614 | -0.200 |
| Detailed mood | `energetic` | 4.614 | -0.200 |
| Instrumentalness | `0.10` | 4.670 | -0.144 |
| Vocal language | `English` | 4.614 | -0.200 |

Each field independently changed the score. Both starter tests passed,
and the whitespace check reported no errors.

### Optional Challenge 2 — Multiple Scoring Modes

**What task did you give the agent?**

I asked the assistant to turn my weight experiment into a selectable
feature. Genre-First would remain the default, with Energy-Focused
available as a second mode.

I applied the changes and ran the checks myself.

**Prompts used**

These are paraphrases of my requests.

- Give me `src/recommender.py` with two modes and shared scoring logic.
- Add command-line mode selection in `src/main.py`.
- Help resolve the circular import shown in the traceback.

**What did the agent generate or change?**

- Added the `SCORING_MODES` dictionary.
- Updated scoring and explanations to use selected weights.
- Passed the mode through `recommend_songs()`.
- Added `--mode` with `genre-first` as its default.

**What did you verify or fix manually?**

I corrected a circular import by keeping CLI imports in `src/main.py`
and scoring definitions in `src/recommender.py`.

Both modes loaded 18 songs.

| Song | Genre-First | Energy-Focused |
|---|---|---|
| Focus Flow | #3, 2.85 | #4, 2.70 |
| Spacewalk Thoughts | #4, 1.97 | #3, 2.94 |

Both starter tests passed at this stage.

### Optional Challenge 3 — Artist Diversity

**What task did you give the agent?**

I requested an optional artist diversity penalty that worked with both
scoring modes.

**Prompts used**

> Add Optional Challenge 3 to my music recommender. Add a `--diversity` flag in `src/main.py` that works with both existing scoring modes. In `recommend_songs()`, score each song once using the selected mode. When diversity is enabled, select recommendations one at a time. Subtract 0.50 points from a candidate’s base score if its artist already appears in the selected results. Use the adjusted score to pick the next song, keep CSV order for ties, and display the penalty in the explanation when applied. Use a single penalty per candidate and leave the default rankings and output unchanged when the flag is omitted. Show me how to verify the change using my Chill Lofi profile.

**What did the agent generate or change?**

The assistant added the flag and sequential selection using adjusted
scores. Repeat artists receive one 0.50-point deduction per candidate.
Explanations identify the deduction.

**What did you verify or fix manually?**

I checked the repository path after an edit was proposed in another
project copy. I continued in the Foundations project on
`experiment/artist-diversity`.

```cmd
python -m src.main
python -m src.main --diversity
python -m src.main --mode energy-focused --diversity
python -m pytest
```

The default matched the baseline. Midnight Coding was selected before
Focus Flow, so Focus Flow received the LoRoom repeat-artist penalty.

| Mode | Without diversity | With diversity |
|---|---|---|
| Genre-First | #3, 2.85 | #3, 2.35 |
| Energy-Focused | #4, 2.70 | #4, 2.20 |

Both explanations displayed the 0.50-point penalty. Both starter tests
passed.

### Optional Challenge 4 — Visual Summary Table

**What task did you give the agent?**

I requested a table view to make recommendation scores and reasons
easier to compare.

**Prompts used**

> Add a `--table` flag to `src/main.py` for Optional Challenge 4. Use Python’s standard library to display Rank, Song, Artist, Score, and Reasons in aligned columns. Wrap long explanations and include the artist diversity penalty whenever it applies. Keep the current list format as the default and make `--table` work with `--mode` and `--diversity`.

**What did the agent generate or change?**

The assistant added `--table` and `print_recommendation_table()`.

**What did you verify or fix manually?**

```cmd
python -m src.main
python -m src.main --table
python -m src.main --mode energy-focused --diversity --table
python -m pytest
```

The table showed all five columns for all three profiles. Rankings
and scores matched the list output.

In the combined run, Focus Flow ranked fourth for Chill Lofi at 2.20.
Its explanation included the artist penalty. Both starter tests passed.

---

## Design Pattern (SF10)

**Which design pattern did you use?**

A lightweight, Strategy-style design supplies named weight sets to
one scoring function.

**How did AI help?**

The assistant suggested a dictionary because both modes use the same
formula with different weights.

**How does it appear in the code?**

`SCORING_MODES` stores weights in genre, mood, and energy order.

- `genre-first` uses `(2.0, 1.0, 1.0)`.
- `energy-focused` uses `(1.0, 1.0, 2.0)`.

The CLI passes the mode through `recommend_songs()` to `score_song()`.

Advanced attributes contribute during scoring. Artist diversity adjusts
selection scores. Table formatting presents the resulting recommendations.

---

## Project 4 — Playlist Intelligence

> Project 4 extends Project 3 using the existing 18-song catalog.
> I applied proposed changes in VS Code and ran verification commands.
> Browser interactions were checked manually.

### AI-Assisted Development Workflow

**What task did you give the assistant?**

I requested step-by-step guidance covering the assignment and all four
optional enhancements. I asked for complete files, ran the proposed
commands, and shared the results.

**Prompts used**

These are paraphrases of my requests.

- Extend my existing recommender to meet the assignment and rubric.
- Give me complete updates to the Python modules.
- Explain whether Python or Gemini selects songs.
- Keep the existing catalog.
- Check progress against Steps 0–6 and submission requirements.
- Update documentation to match verified results.
- Add connection-failure handling and tests.
- Verify a fresh clone.
- Add an attractive, organized visual interface.
- Keep the background inside the Python file.
- Add professional interface features.

**What did the assistant generate or change?**

| File | Contribution |
|---|---|
| `src/curator.py` | Workout handling and activity routing |
| `src/guide_retriever.py` | Activity-guide retrieval |
| `data/curation_guides.md` | Workout and studying guidance |
| `src/llm_client.py` | Generation, response validation, and network handling |
| `src/study_curator.py` | Studying constraints, tie-breaking, and broader searches |
| `src/main.py` | CLI orchestration and approval |
| `src/prompts.py` | Baseline and specialized prompts |
| `evaluate.py` | CLI evaluation |
| `compare_prompts.py` | Live prompt comparison |
| `streamlit_app.py` | Visual interface and export |
| `tests/` | Behavior and guardrail checks |
| `diagrams/architecture.mmd` | Architecture source |

**What did you verify or fix manually?**

I fixed an indentation problem that prevented studying dispatch.

The initial tests used the reserved pytest parameter name `request`.
Changing it to `playlist_request` fixed collection.

I reactivated the project environment after discovering that installation
had used my user-wide Python.

I removed an unused comparison variable and applied corrected regular
expressions.

I replaced a long dash in the evaluation title to resolve an encoding
issue in the saved log.

### Multi-Source Retrieval and Grounded Generation

**What task was addressed?**

Use the song catalog and custom activity guide to produce grounded
recommendations and explanations.

**What changed?**

Python retrieves guidance, filters tracks, and ranks candidates.
Gemini receives the selected records and guide when AI is enabled.

The response validator checks JSON, IDs, uniqueness, completeness,
and explanation length.

**What did you verify?**

The first energy-only filter selected Winter Signal, which has sad
and melancholic tags. Suitable-mood filtering removed it.

| Version | Behavior | Observed result |
|---|---|---|
| Initial workout filter | Energy only | Winter Signal appeared |
| Revised filter | Retrieved energy and mood rules | Winter Signal excluded |
| Stricter guide test | Minimum energy raised from 0.75 to 0.90 | Lower-energy candidate excluded |

The revised playlist contained Neon Tide, Storm Runner, and Gym Hero.

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai
python -m src.main --request "3 calm lofi songs for studying" --ai
```

Successful outputs used retrieved mood, energy, and guidance.

[Recorded workout execution](evidence/workout_ai.txt)

The observed improvement concerns alignment with activity rules.
Listener enjoyment has not been measured.

**Reliability observations**

Some requests returned 503 or 504 errors. The app displayed identified
catalog fallbacks.

The tested 2.5 models reported unavailable access for new users.
Successful full generation was verified with `gemini-3.5-flash-lite`.

Some explanations used imprecise wording about nearby energy values.
Factual review remains necessary.

### Agentic Workflow Enhancement — Studying Approval

**What task was addressed?**

Detect insufficient exact matches and ask before including other genres.

**Implemented decision chain**

1. Validate the request.
2. Retrieve the activity guide.
3. Search and rank within the requested genre.
4. Check the result count.
5. Ask the listener when matches are insufficient.
6. Search across genres only after approval.
7. Preserve activity restrictions and display results.

**Observed workflow trace**

Request — `3 calm jazz songs for studying`

| Step | Action | Observed result | Next decision |
|---|---|---|---|
| 1 | Validate | Three tracks, jazz, studying | Retrieve guide |
| 2 | Retrieve | Target 0.35, maximum 0.50, suitable moods | Search catalog |
| 3 | Search jazz | One matching track | Ask for approval |
| 4A | Listener declines | Genre constraint retained | Return exact match |
| 4B | Listener approves | Broader search authorized | Search other genres |
| 5B | Rank broader results | Jazz match and two lofi tracks | Label and display |

**Verified results**

| Decision | Song | Genre | Score |
|---|---|---|---:|
| Decline | Coffee Shop Stories | jazz | 2.98 |
| Approve | Coffee Shop Stories | jazz | 2.98 |
| Approve | Focus Flow | lofi | 1.95 |
| Approve | Library Rain | lofi | 1.00 |

```cmd
echo n| python -m src.main --request "3 calm jazz songs for studying"
echo y| python -m src.main --request "3 calm jazz songs for studying"
```

- [Declined search log](evidence/studying_declined.txt)
- [Approved search log](evidence/studying_approved.txt)

These logs predate instrumentalness tie-breaking.

**Historical milestone**

```text
32 passed in 0.51s
```

Tests verified approval, decline, empty approval input, end-of-input,
and avoiding unnecessary prompts when enough exact matches exist.

**Gemini after approval**

```cmd
echo y| python -m src.main --request "3 calm jazz songs for studying" --ai > evidence\studying_approved_ai.txt 2>&1
```

The recorded output identified the lofi tracks as approved alternatives.

[Approved AI execution](evidence/studying_approved_ai.txt)

### Studying Instrumentalness Preference

**What task was addressed?**

Apply the guide's instrumental preference when other preferences
are equal.

**What changed?**

The guide's documented preference activates descending instrumentalness
preordering. The ranker retains that order for equal primary scores.

Higher primary relevance ranks first. Missing instrumentalness defaults
to `0.0`.

**Controlled test**

| Track | Mood | Energy | Instrumentalness |
|---|---|---:|---:|
| Lower Instrumentalness | chill | 0.35 | 0.10 |
| Higher Instrumentalness | chill | 0.35 | 0.90 |
| Stronger Mood Match | focused | 0.35 | 0.00 |

Expected and verified two-track selection:

```text
Stronger Mood Match
Higher Instrumentalness
```

**Historical milestone**

```text
39 passed in 1.19s
```

The CLI harness continued to pass eight cases.

### Specialization Enhancement

**What task was addressed?**

Produce concise explanations with clearly labeled catalog evidence.

**What changed?**

Few-shot examples request explanations of at most 25 words with exact
mood labels and energy formatted to two decimals.

Both interfaces expose the specialized setting.

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai --specialized
```

Observed example:

```text
Mood: energizing. Energy: 0.88. Fits a workout and is close to the guide target of 0.90.
```

**Measured comparison**

```cmd
python compare_prompts.py
```

Both styles used the same request, tracks, guide, and model,
`gemini-3.5-flash-lite`.

| Style | Average words | At most 25 words | Correct mood labels | Correct energy labels |
|---|---:|---:|---:|---:|
| Baseline | 23.3 | 3/3 | 0/3 | 0/3 |
| Specialized | 16.0 | 3/3 | 3/3 | 3/3 |

Average length decreased by approximately 31%.

Both styles used correct mood and energy facts in the observed outputs.
Label scores measure style compliance. Factual accuracy requires
separate review.

The comparison used one generation per style.

- [Comparison evidence](evidence/prompt_comparison.md)
- [Model-card interpretation](model_card.md)

### Evaluation Harness Enhancement

**What task was addressed?**

Run predefined cases through the actual CLI and report results.

**What changed?**

`evaluate.py` uses the active Python interpreter, supplies inputs,
captures output, and checks exit codes and expected or excluded text.

Cases have timeouts. Failures print diagnostics and cause a nonzero
script exit code.

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

[Saved evaluation output](evidence/evaluation.txt)

### Network-Failure Handling

**What task was addressed?**

Preserve catalog recommendations when generation encounters
a connection failure.

**What changed?**

The model client catches `httpx2.TransportError` and `OSError` and
converts them into a handled `ValueError`.

The CLI identifies its fallback and displays catalog recommendations.

**Simulated verification**

| Test | Failure | Verified behavior |
|---|---|---|
| Model client | Connection error during generation | Handled application error |
| CLI | Connection error during client creation | Fallback notice and tracks |

The CLI test checks for the fallback notice and the three expected
workout tracks. These tests make no live calls.

Timeout exceptions are covered by the transport-error handler.
A dedicated timeout-specific test remains future work.

**Historical milestone**

```text
41 passed in 0.89s
```

### Fresh-Clone Verification

**What task was addressed?**

Check installation and execution in a separate environment.

**What did I do?**

I cloned revision `2ce6823` into `playlist-intelligence-verify`, created
a new environment, and installed dependencies using Python 3.13.9
on Windows.

This revision preceded the visual interface.

```cmd
python -m pip check
python -m pytest -q
python evaluate.py
python -m src.main --request "3 calm lofi songs for studying"
```

| Check | Observed result |
|---|---|
| Installation | Successful |
| Dependency check | No broken requirements found |
| Tests | 41 passed in 1.23s |
| CLI evaluation | 8/8 cases passed |
| Studying request | Expected tracks returned |

| Rank | Track | Score | Instrumentalness |
|---|---|---:|---:|
| 1 | Focus Flow | 3.95 | 0.82 |
| 2 | Library Rain | 3.00 | 0.92 |
| 3 | Midnight Coding | 2.93 | 0.88 |

The output included reasons, genre status, and the guide source.

Live generation and the visual interface were checked separately.

### Streamlit Visual Interface

**What task did you give the assistant?**

I asked whether the project could have a clearly organized visual
interface. I requested an attractive background and professional features.

I asked to keep the background inside `streamlit_app.py` and requested
complete code to copy and paste.

**Prompts used**

These are paraphrases of my requests.

- Add an attractive, well-organized background.
- Put the image background directly inside the Python file.
- Give me complete code with professional app features.
- Update the architecture and documentation to include the interface.

**What changed?**

The assistant proposed `streamlit_app.py`, reusing the existing
recommendation, guide retrieval, studying, and Gemini functions.

The interface includes:

- Activity, track-count, and studying-genre controls.
- Optional Gemini and specialized explanations.
- Approval buttons for insufficient studying matches.
- Recommendation cards and summary metrics.
- Expandable catalog evidence.
- CSV download.
- Clear-results control.
- An embedded SVG background.

A generated raster background was explored first. The current
copy-and-paste implementation uses an SVG illustration embedded in
the Python file.

The form submits preferences together. Session state preserves
the submitted request, pending approval, and resulting playlist.

**What did you verify manually?**

I launched the app:

```cmd
python -m streamlit run streamlit_app.py
```

I inspected the screen and tested its controls.

| Scenario | Observed result |
|---|---|
| Workout with three songs | Neon Tide, Storm Runner, and Gym Hero |
| Workout metrics | Three tracks, three artists, average energy 0.91 |
| Studying jazz, keep genre | Coffee Shop Stories only |
| Studying jazz, include other genres | Coffee Shop Stories, Focus Flow, and Library Rain |
| Approved alternatives | Lofi tracks labeled as alternatives |
| Broader studying metrics | Three tracks, three artists, average energy 0.37 |
| Catalog evidence | Attributes and source displayed |
| CSV download | Confirmed successful |
| Clear results | Confirmed successful |
| Gemini explanations | Confirmed successful |
| Background and layout | Visually inspected |

Browser checks were manual. The existing automated tests exercise shared
logic and CLI behavior.

**Code verification after the interface update**

```cmd
python -m py_compile streamlit_app.py
python -m pytest -q
python evaluate.py
git diff --check
```

Observed results:

```text
Python compilation completed without an error.
41 passed in 1.05s
Summary: 8/8 cases passed
Pass rate: 100%
```

### Architecture and Documentation

The updated Mermaid source includes both interfaces:

[diagrams/architecture.mmd](diagrams/architecture.mmd)

It shows retrieval, ranking, approval, generation, validation, fallback,
visual output, CSV download, clear results, and testing connections.

The README includes setup, Streamlit launch instructions, demonstrations,
evaluation, and design decisions.

The model card includes the responsible-AI reflection, limitations,
misuse analysis, testing surprises, specialization comparison, and manual
interface evaluation.

### Latest Verification Summary

| Check | Latest verified result |
|---|---|
| Streamlit syntax | Compilation passed |
| Automated tests after UI addition | 41 passed in 1.05s |
| CLI evaluation | 8/8 cases passed |
| Dependency compatibility | Passed in the earlier fresh clone |
| Workout UI | Manually verified |
| Studying approval UI | Both choices manually verified |
| CSV download | User confirmed successful |
| Clear results | User confirmed successful |
| Gemini UI explanations | User confirmed successful |
| Catalog evidence display | Visually inspected |
| Specialized prompt comparison | Outputs and measurements saved |
| Instrumentalness tie-breaking | Controlled test passed |
| Connection-failure handling | Simulated tests passed |

### Remaining Project 4 Work

- Check final documentation consistency.
- Refresh execution evidence after further code changes.
- Prepare the 5–7 minute Engineer's Pitch.
- Finalize presentation materials and review the portfolio reflection.
- Record and link a Loom walkthrough if included.
- Commit and push the interface and updated documentation.
- Perform the final submission checklist.

### Future Reliability Improvements

- Add dedicated timeout tests.
- Expand factual evaluation of generated explanations.
- Add automated Streamlit interaction and CSV-export tests.
- Test changed preferences and approval state more extensively.
- Verify the visual interface from a fresh clone.
- Check setup on macOS and Linux.