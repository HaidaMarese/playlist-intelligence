# 🎧 Model Card: Playlist Intelligence

## 1. System Name

**Playlist Intelligence — Applied AI System**

Base project — **VibeFinder 1.0: Music Recommender Simulation**

Playlist Intelligence extends my CodePath AI110 Project 3. The original
system ranked songs for predefined taste profiles using genre, mood,
and energy preferences. It displayed numeric scores and explanations,
with optional scoring modes, advanced attributes, artist diversity,
and table output.

Project 4 adds activity-guide retrieval, playlist requests, Gemini
explanations, output validation, listener approval before broadening
a studying search, instrumentalness tie-breaking, network-failure
handling, and a Streamlit visual interface.

---

## 2. Intended Use

Playlist Intelligence is an educational application that helps listeners
explore a small song catalog and understand why tracks were recommended.

The application provides two interfaces that reuse the recommendation
and generation modules.

| Interface | Intended interaction |
|---|---|
| Command line | Enter supported requests and run reproducible demonstrations |
| Streamlit | Select preferences, review recommendations, approve alternatives, and download results |

Both interfaces support workout and genre-specific studying requests.

### Command-Line Examples

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout"
python -m src.main --request "3 calm lofi songs for studying"
python -m src.main --request "3 calm jazz songs for studying"
```

The original three-profile demonstration remains available:

```cmd
python -m src.main
```

Gemini explanations are enabled with `--ai`. The specialized style is
enabled with `--ai --specialized`.

### Visual Interface

```cmd
python -m streamlit run streamlit_app.py
```

Listeners choose an activity, count, and studying genre. They can enable
AI explanations, review catalog evidence, download a CSV, and clear
displayed results.

The system supports classroom demonstrations, portfolio review, and
experimentation with retrieval, ranking, AI explanations, and reliability.

Recommendations come from the supplied catalog. Listener enjoyment has
not been measured.

---

## 3. How the System Works

### Original Project 3 Ranking

The default scoring function compares each song with a listener's
favorite genre, favorite mood, and target energy.

- An exact genre match earns **2 points**.
- An exact mood match earns **1 point**.
- Energy similarity earns **up to 1 point**, calculated as
  `1 - abs(song_energy - target_energy)`.

The maximum default score is **4 points**. Scores represent rule-based
relevance. They are not probabilities or calibrated confidence values.

The original demo displays up to five songs per profile. Equal scores
preserve catalog order.

Energy-Focused mode uses genre, mood, and energy weights of
`(1.0, 1.0, 2.0)`. Advanced scoring adds contributions from illustrative
metadata. Artist diversity can apply a 0.50-point penalty.

### Project 4 Retrieval and Activity Rules

The application retrieves information from two sources.

| Source | Retrieved information |
|---|---|
| `data/songs.csv` | Track records and attributes |
| `data/curation_guides.md` | Activity-specific guidance |

For workouts, the guide defines:

- Target energy of `0.90`.
- Minimum energy of `0.75`.
- Suitable moods of happy, energizing, intense, aggressive,
  playful, and uplifting.

For studying, the guide defines:

- Target energy of `0.35`.
- Maximum energy of `0.50`.
- Suitable moods of chill, focused, relaxed, and peaceful.
- An instrumental preference when other preferences are equal.

Python applies the retrieved rules and ranks eligible tracks.
Workout ranking favors energizing tracks. Studying ranking favors the
requested genre and focused mood.

### Instrumentalness Tie-Breaking

When the studying guide requests the instrumental preference, higher
instrumentalness breaks ties between equal primary scores.

Instrumentalness uses the catalog's 0–1 values. Missing values default
to `0.0`.

Candidates are preordered by instrumentalness. The existing ranker
preserves this order for equal primary scores before selecting the
requested number of tracks.

Genre, mood, and energy relevance determine the primary score.
Equal scores and equal instrumentalness preserve catalog order.

Catalog-based explanations identify the instrumentalness value and
its role as a tie-break preference.

### Human-in-the-Loop Workflow

The initial studying search preserves the requested genre.

When fewer tracks match than requested, the application asks whether
the listener approves other genres. Approval triggers another search
with the same studying mood and energy restrictions.

In the CLI, `y` or `yes`, ignoring capitalization and surrounding spaces,
authorizes broadening. Declining, pressing Enter, or reaching end-of-input
preserves the original genre constraint.

In Streamlit, the listener chooses **Include other genres** or
**Keep my genre**.

The instrumentalness preference also applies to the broader search.

Catalog explanations label approved alternatives. Gemini's input
includes the listener's approval when AI explanations are enabled.

### Retrieval-Augmented Generation

Python selects the tracks. Gemini writes explanations using the
listener request, retrieved guide, selected records, and ranking evidence.

The generator returns JSON records containing song IDs and explanations.

The application verifies:

- JSON list format.
- Expected integer song IDs.
- Unique song IDs.
- An explanation for every selected song.
- Explanation length between 1 and 50 words.

It attaches source references and displays titles, artists, and scores
from catalog records.

### Specialized Prompting

The specialized prompt adds illustrative few-shot examples and requests:

- Explanations of at most 25 words.
- An explicit `Mood:` label with the catalog mood.
- An explicit `Energy:` label formatted to two decimal places.
- A connection to the requested activity.
- Identification of approved alternative genres.
- Precise wording about exact and nearby energy values.

The shared validator enforces 50 words. The comparison measures compliance
with the specialized 25-word target.

### API and Network-Failure Handling

Handled API errors and invalid responses trigger identified catalog
fallback explanations.

The model client catches `httpx2.TransportError` and `OSError`, converting
them into a handled application error.

Two simulated tests verify:

- A connection error during generation becomes a handled error.
- A connection error during client creation triggers the CLI fallback
  and preserves recommendations.

Timeout exceptions are covered by the transport-error handler.
A dedicated timeout-specific test remains a future improvement.

The Streamlit interface also catches handled generation errors and
identifies its catalog fallback. Its failure path has not received a
separate automated interface test.

### Visual Presentation and Export

The Streamlit interface uses form submission and session state to
associate results and approval decisions with submitted preferences.

It displays:

- Recommendation cards.
- Track count, distinct artist count, and average energy.
- Catalog attributes and expandable evidence.
- Approved-alternative labels.
- Explanation mode and fallback notices.

CSV export includes displayed track records, scores, explanation mode,
and explanations.

The background is an SVG illustration embedded in `streamlit_app.py`.

---

## 4. Data

The catalog contains **18 songs**. I kept all 10 starter songs and added
eight fictional tracks to expand genres and moods.

The CSV contains:

- ID, title, and artist.
- Genre and mood.
- Energy, tempo, valence, danceability, and acousticness.
- Popularity, release decade, detailed mood, instrumentalness,
  and vocal language.

The five advanced attributes were added as illustrative metadata during
Project 3. They are not verified music-service measurements.

The catalog covers pop, lofi, rock, ambient, jazz, synthwave, indie pop,
electronic, country, soul, metal, classical, disco, folk, and reggae.

The data contains no listener ratings, listening history, or feedback
about recommendation quality.

The custom guide reflects project design choices. Its mood labels and
thresholds may not fit every listener.

---

## 5. Strengths

### Transparent Ranking

Scoring explanations make ranking decisions inspectable.

In the original demo:

| Profile | First recommendation | Score |
|---|---|---:|
| High-Energy Pop | Sunrise City | 3.97 |
| Chill Lofi | Library Rain | 3.90 |
| Deep Intense Rock | Storm Runner | 3.99 |

Sunrise City's pop genre, happy mood, and energy of `0.82` fit the
High-Energy Pop profile and its `0.85` target.

### Retrieved Guidance Changes Behavior

The initial energy-only workout filter selected Winter Signal, which
has sad and melancholic tags.

Adding suitable mood rules removed it. The revised playlist contained
Neon Tide, Storm Runner, and Gym Hero.

An automated test confirms that increasing the retrieved energy threshold
removes a lower-energy candidate.

The studying guide also activates instrumentalness tie-breaking.

### Listener Control

A three-track jazz studying request finds Coffee Shop Stories as its
single exact match.

Other genres are included after approval. Focus Flow and Library Rain
then become eligible alternatives under the studying rules.

### Grounded Explanations and Fallback

Successful Gemini runs used catalog mood and energy values.

Observed API-error runs continued displaying catalog recommendations.
Simulated connection-failure tests verified the model-client and CLI
fallback paths.

### Accessible Visual Workflow

The Streamlit interface exposes preferences, approval decisions,
recommendation explanations, and catalog evidence through visual controls.

Manual checks confirmed recommendations, approval choices, CSV download,
clearing results, and Gemini explanations.

### Verified Installation

A separate Windows clone installed successfully, passed dependency
checks, passed 41 tests, and passed eight CLI evaluation cases.

A studying request returned the expected tracks and evidence.

---

## 6. Limitations and Biases

### Small and Uneven Catalog

Several genres contain only one track. Coverage is too limited to
represent real music preferences or cultural diversity.

Some requests cannot be fully satisfied.

### Subjective Activity Rules

Mood labels and activity thresholds reflect design assumptions.
Aggressive tracks may suit some workout listeners and exclude others.

The instrumental preference has not been evaluated with listeners.

### Limited Request Language

The CLI accepts specific patterns. Streamlit builds supported requests
from form selections.

More flexible language and combinations of preferences require further
development.

### Ranking Bias

Exact genre bonuses can outweigh stronger mood or energy alignment.

Repeatedly favoring genres can reduce discovery. Approval-based
broadening gives listeners control over one way to expand results.

### Metadata and Tie-Breaking Limits

Baseline scoring does not use tempo, danceability, or acousticness.

Instrumentalness affects equal primary scores. Its influence may be
limited with the current catalog.

Defaulting missing instrumentalness to `0.0` can disadvantage incomplete
records when scores are equal.

### Guide Format Dependency

Retrieval expects headings, and rule parsing expects documented phrases.

The instrumental preference depends on its documented sentence.
Rewording it can disable that preference.

### Generated Wording

Some explanations describe nearby energy values as matching a target.

Structural checks validate format and IDs. Factual wording can still
need correction.

### External Service Availability

Live generation depends on access, quotas, connectivity, and service
availability.

Catalog fallback is available during handled failures.

### Interface Limitations

Visual interactions were checked manually. Automated coverage currently
focuses on shared logic and CLI behavior.

Some CSS selectors depend on Streamlit markup and may require revision
after upgrades.

Changing form values takes effect after submitting the form. Displayed
results remain associated with the last submitted request.

### Evaluation Scope

Tests cover predefined behaviors. Listener satisfaction requires
separate evaluation.

Connection failures are simulated. Dedicated timeout tests and broader
network experiments remain future improvements.

The prompt comparison used one request and one generation per style.

### Reproducibility Scope

Fresh-clone verification covered the CLI revision before the visual
interface was added.

Live generation and Streamlit behavior were verified separately during
development.

Dependencies are unpinned. Full macOS and Linux checks remain future work.

---

## 7. Evaluation and Reliability Results

### Project 3 Baseline Evaluation

The original CLI loaded 18 songs and displayed five recommendations
with scores and reasons for each profile.

Both starter tests passed at that stage.

| Profile | Genre | Mood | Target energy | First recommendation | Score |
|---|---|---|---:|---|---:|
| High-Energy Pop | pop | happy | 0.85 | Sunrise City | 3.97 |
| Chill Lofi | lofi | chill | 0.25 | Library Rain | 3.90 |
| Deep Intense Rock | rock | intense | 0.90 | Storm Runner | 3.99 |

### Profile Comparisons

- Sunrise City matched the pop profile's genre and mood.
- Library Rain matched the lofi profile's genre and mood.
- Gym Hero earned genre points for pop and mood points for intense rock.
- Spacewalk Thoughts benefited from the chill mood and low energy target.
- Winter Signal earned its Deep Intense Rock score from energy similarity.

### Manual Weight Comparison

For High-Energy Pop, Gym Hero scored **2.92** and Rooftop Lights **1.91**
with baseline weights.

Giving mood two points and genre one point reversed their order.
Rooftop Lights scored **2.91**, and Gym Hero **1.92**.

### Project 3 Edge-Case Test

I tested rock, sad mood, and target energy `0.90`.

```text
Sad and High Energy - Top 5 Recommendations
Favorite genre: rock | Favorite mood: sad | Target energy: 0.90
1. Storm Runner | Score: 2.99
   Reasons: genre match (+2.00), energy similarity (+0.99)
2. Winter Signal | Score: 2.00
   Reasons: mood match (+1.00), energy similarity (+1.00)
3. Rainwashed Letters | Score: 1.51
   Reasons: mood match (+1.00), energy similarity (+0.51)
4. Neon Tide | Score: 0.98
   Reasons: energy similarity (+0.98)
5. Gym Hero | Score: 0.97
   Reasons: energy similarity (+0.97)
```

The genre bonus placed Storm Runner above Winter Signal despite Winter
Signal's exact mood and energy matches.

### Project 3 Weight Experiment

Genre weight changed from `2.0` to `1.0`, and energy weight from `1.0`
to `2.0`. Mood weight stayed `1.0`.

| Chill Lofi song | Baseline rank | Baseline score | Experiment rank | Experiment score |
|---|---:|---:|---:|---:|
| Spacewalk Thoughts | 4 | 1.97 | 3 | 2.94 |
| Focus Flow | 3 | 2.85 | 4 | 2.70 |

Spacewalk Thoughts benefited from its chill mood and energy close to
the target. Library Rain stayed first.

High-Energy Pop and Deep Intense Rock retained their top-five order.

### Project 4 Automated Tests

After adding the visual interface:

```cmd
python -m pytest -q
```

```text
41 passed in 1.05s
```

Test duration varies.

Coverage includes:

- Original ranking behavior.
- Request validation.
- Guide retrieval and parsing.
- Studying constraints.
- Model-output validation.
- Listener approval behavior.
- Instrumentalness tie-breaking.
- Score priority over instrumentalness.
- Simulated connection-failure handling.
- CLI catalog fallback.

These tests do not automate browser interactions or make live Gemini
requests.

### Instrumentalness Test

| Track | Mood | Energy | Instrumentalness |
|---|---|---:|---:|
| Lower Instrumentalness | chill | 0.35 | 0.10 |
| Higher Instrumentalness | chill | 0.35 | 0.90 |
| Stronger Mood Match | focused | 0.35 | 0.00 |

For two requested tracks, the test verifies:

```text
Stronger Mood Match
Higher Instrumentalness
```

This checks primary relevance and tie-breaking before truncation.

### Simulated Network-Failure Tests

| Test | Simulated failure | Verified behavior |
|---|---|---|
| Model client | Connection error during generation | Handled application error |
| CLI fallback | Connection error during client creation | Fallback notice and catalog recommendations |

The CLI test checks for Neon Tide, Storm Runner, and Gym Hero and
confirms that successful Gemini generation is not reported.

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

This result applies to the eight predefined cases. The harness passed
both in the fresh clone and after adding the visual interface.

### Manual Visual-Interface Evaluation

Launch command:

```cmd
python -m streamlit run streamlit_app.py
```

| Scenario | Evaluation criterion | Observed result |
|---|---|---|
| Workout, three tracks | Display expected recommendations | Pass — Neon Tide, Storm Runner, Gym Hero |
| Workout summary | Correct playlist metrics | Pass — three tracks, three artists, average energy 0.91 |
| Studying jazz, keep genre | Preserve jazz | Pass — Coffee Shop Stories only |
| Studying jazz, approve alternatives | Include eligible alternatives | Pass — Coffee Shop Stories, Focus Flow, Library Rain |
| Broader studying summary | Correct metrics | Pass — three tracks, three artists, average energy 0.37 |
| Catalog evidence | Display source attributes | Visually inspected |
| CSV download | Export displayed tracks | User confirmed successful |
| Clear results | Remove displayed results | User confirmed successful |
| AI explanations | Generate through the visual interface | User confirmed successful |
| Embedded background | Render without separate image assets | Visually inspected |

Python syntax compilation also succeeded:

```cmd
python -m py_compile streamlit_app.py
```

### Observed Guardrail Behavior

| Condition | Expected behavior | Observed result |
|---|---|---|
| Blank request | Explain required input | Pass |
| Zero requested tracks | Reject invalid count | Pass |
| Unknown studying genre | Explain unavailable genre | Pass |
| Declined broadening | Preserve requested genre | Pass |
| Missing approval input | Preserve requested genre | Pass |
| Enough exact matches | Avoid approval prompt | Pass |
| Unknown or duplicate model IDs | Reject response | Pass in simulated tests |
| API 503/504 | Identify catalog fallback | Pass in observed live runs |
| Connection error | Handle failure and preserve recommendations | Pass in simulated tests |
| Numeric wording | Distinguish nearby and exact values | Needs further improvement |

### Recorded Evidence

- [Workout AI execution](evidence/workout_ai.txt)
- [Declined studying search](evidence/studying_declined.txt)
- [Approved studying search](evidence/studying_approved.txt)
- [Approved studying search with Gemini](evidence/studying_approved_ai.txt)
- [Automated test log](evidence/tests.txt)
- [CLI evaluation summary](evidence/evaluation.txt)

Earlier studying logs predate instrumentalness tie-breaking.

### Fresh-Clone Verification

I cloned revision `2ce6823` into `playlist-intelligence-verify` and created
a new environment using Python 3.13.9 on Windows.

This revision preceded the Streamlit interface.

| Check | Result |
|---|---|
| Dependency installation | Successful |
| `python -m pip check` | No broken requirements found |
| `python -m pytest -q` | 41 passed in 1.23s |
| `python evaluate.py` | 8/8 cases passed |
| Studying request | Expected three tracks returned |

```cmd
python -m src.main --request "3 calm lofi songs for studying"
```

Condensed observed results:

```text
1. Focus Flow | Score: 3.95 | Instrumentalness: 0.82
2. Library Rain | Score: 3.00 | Instrumentalness: 0.92
3. Midnight Coding | Score: 2.93 | Instrumentalness: 0.88
```

The output also included reasons, genre status, and the guide source.

Live Gemini generation and the visual interface were checked separately
during development.

---

## 8. Baseline vs. Specialized Output

### Method

I compared prompts using `gemini-3.5-flash-lite`.

Both runs used:

- `Give me 3 upbeat songs for a workout`.
- The same selected tracks.
- The same workout guide.
- The same model, output limit, and validation.

The specialized prompt added illustrative few-shot examples and
requested concise, labeled evidence.

```cmd
python compare_prompts.py
```

The experiment used one generation per style.

### Observed Results

| Style | Average words | At most 25 words | Correct mood labels | Correct energy labels |
|---|---:|---:|---:|---:|
| Baseline | 23.3 | 3/3 | 0/3 | 0/3 |
| Specialized | 16.0 | 3/3 | 3/3 | 3/3 |

Average explanation length decreased by approximately **31%**.

Both styles stayed within 25 words. All specialized explanations used
the requested labels with correct catalog values.

### Baseline Example — Neon Tide

> For your workout request, Neon Tide features an energizing mood and an energy level of 0.88, closely matching the target energy of 0.90.

### Specialized Example — Neon Tide

> Mood: energizing. Energy: 0.88. Fits a workout and is close to the guide target of 0.90.

### Interpretation

The specialized output was shorter and consistently labeled.

The baseline also described correct mood and energy values. Label
scores measure style compliance. Factual accuracy requires separate review.

Word counts exclude appended source references. The selected tracks were
the same in both runs.

### Application Integration

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai --specialized
```

The Streamlit interface exposes the same setting through its concise
curator style checkbox.

### Full Evidence

[Actual outputs and measurements](evidence/prompt_comparison.md)

---

## 9. Potential Misuse and Mitigations

### Overstating Recommendation Quality

A user could treat a high score as a guarantee of suitability or enjoyment.

Documentation explains the scoring rules and illustrative metadata.
Listener feedback would be needed to assess enjoyment.

### Unsupported Generated Claims

Explanations could introduce unsupported claims about lyrics, health,
or performance.

The prompt restricts explanations to retrieved facts. Output validation
checks IDs and format. Factual review remains necessary.

### Ignoring Preferences

Silently broadening a genre could undermine the request.

Both interfaces require listener approval before broadening a studying
search.

### API Credential Exposure

The key is read from an environment variable. It should be kept out
of source files, screenshots, evidence, and commits.

### Retrieved Content Quality

Guide edits change behavior. Parsing rejects some malformed rules but
does not assess whether a rule is appropriate for listeners.

Changes should be reviewed and followed by tests and evaluation.

### Exported Results

CSV downloads contain displayed catalog records and explanations.
They may therefore include the same wording inaccuracies as the screen.

---

## 10. AI Collaboration and Design Reflection

### How I Used AI

I used an assistant to plan the project, reuse ranking code, write
modules, design tests, interpret errors, build the interface, and prepare
documentation.

I applied code in VS Code, ran commands, checked browser behavior, and
shared outputs for review.

### One Suggestion I Accepted

I accepted reusing Python ranking and giving Gemini the selected tracks
and retrieved guide.

This made selection inspectable through scores while adding readable
explanations.

I also accepted approval before broadening a studying search so listeners
control that preference change.

### One Suggestion I Revised

The initial workout filter relied on high energy and selected Winter
Signal, which has sad and melancholic tags.

I applied a revision requiring a suitable mood as well as sufficient
energy. The revised playlist excluded Winter Signal and returned Neon
Tide, Storm Runner, and Gym Hero.

This revised an early AI-assisted implementation after inspecting output.

### What Surprised Me During Reliability Testing

High energy could satisfy a numeric condition while conflicting with
the request's upbeat mood.

A successful API connection test also did not guarantee later generation.
Service failures made fallback behavior necessary.

### What I Learned About Verification

A reserved pytest parameter name caused collection failure. Renaming
`request` to `playlist_request` fixed it.

An indentation problem prevented studying dispatch. Running the request
revealed the issue.

Controlled tests checked tie-breaking and simulated connection failures.

A fresh clone checked installation and CLI behavior. Browser checks
then verified the visual interface separately.

### System Design Trade-Offs

Rules make ranking reproducible but limit flexible interpretation.

Gemini improves readability but introduces latency, external dependency,
and wording risks.

Approval adds an interaction when exact matches are scarce.

Instrumentalness tie-breaking influences equal primary scores without
adding a score bonus.

The visual interface improves access to controls and evidence but adds
session-state and presentation behavior that needs separate verification.

### Personal Reflection

Seeing Gym Hero outrank Rooftop Lights originally taught me how scoring
weights influence apparently personal recommendations.

Project 4 showed that retrieval, ranking, explanation, and verification
must all serve the request. An explanation can sound reasonable while
a filter misses intent.

I learned to inspect outputs, revise assumptions, test failures, and
document evidence. Presenting the workflow visually also helped me make
approval decisions and recommendation evidence clearer to listeners.

---

## 11. Future Improvements

- Add dedicated timeout tests and broader network-failure scenarios.
- Expand factual checks for explanations and numeric comparisons.
- Add automated Streamlit interaction and export tests.
- Test session behavior across changed preferences and approval decisions.
- Test instrumentalness activation and missing metadata more extensively.
- Repeat prompt comparisons across more requests.
- Support multiple preferred genres and moods.
- Collect listener feedback.
- Verify setup and execution on macOS and Linux.
- Expand catalog coverage after reviewing metadata quality.

---

## 12. Reproducibility and Supporting Files

Development used **Python 3.13.9 on Windows**.

The verified live model was `gemini-3.5-flash-lite`. Access and availability
can change.

Configuration uses `GEMINI_API_KEY` and `GEMINI_MODEL`.

Dependencies include `pandas`, `pytest`, `streamlit`, `google-genai`,
and `httpx2`. They are unpinned.

Fresh-clone verification covered revision `2ce6823`. The visual interface
was added and manually checked afterward.

| File | Purpose |
|---|---|
| `README.md` | Setup, commands, demonstrations, and overview |
| `streamlit_app.py` | Visual interface, approval controls, metrics, evidence, and export |
| `data/songs.csv` | Existing catalog |
| `data/curation_guides.md` | Activity guidance |
| `src/recommender.py` | Scoring and ranking |
| `src/curator.py` | Workout handling and routing |
| `src/study_curator.py` | Studying rules and approved broadening |
| `src/guide_retriever.py` | Guide retrieval |
| `src/llm_client.py` | Generation, network handling, and validation |
| `src/prompts.py` | Baseline and specialized prompts |
| `tests/` | Automated checks |
| `evaluate.py` | CLI evaluation |
| `compare_prompts.py` | Live prompt comparison |
| `diagrams/architecture.mmd` | Mermaid architecture source |
| `ai_interactions.md` | Development history and workflow traces |
| `evidence/` | Recorded executions and comparisons |

The visual interface, README, and updated architecture source have been
prepared. Final documentation checks, refreshed execution evidence, and
the presentation remain in progress.