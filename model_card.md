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
explanations, output validation, and listener approval before broadening
a studying search to other genres.

---

## 2. Intended Use

Playlist Intelligence is an educational application that helps listeners
explore a small song catalog and understand why tracks were recommended.

The current command-line application supports workout requests and
genre-specific studying requests. Example inputs include:

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout"
python -m src.main --request "3 calm lofi songs for studying"
python -m src.main --request "3 calm jazz songs for studying"
```

The original three-profile demonstration remains available:

```cmd
python -m src.main
```

Gemini explanations are enabled with `--ai`. A specialized explanation
style is enabled with `--ai --specialized`.

The system is intended for classroom demonstrations, portfolio review,
and experimentation with retrieval, ranking, AI explanations, and
reliability testing.

It does not predict real listeners' enjoyment from behavioral data.
It also does not stream music or connect to Spotify.

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

The original demo ranks the catalog and displays up to five songs per
profile. Equal scores preserve catalog order.

The optional Energy-Focused mode uses genre, mood, and energy weights
of `(1.0, 1.0, 2.0)`. Advanced scoring adds contributions from illustrative
metadata, and artist diversity can apply a 0.50-point penalty.

### Project 4 Retrieval and Activity Rules

The application retrieves information from two sources:

- `data/songs.csv` provides track records.
- `data/curation_guides.md` provides activity guidance.

For workouts, the guide currently defines:

- Target energy of `0.90`.
- Minimum energy of `0.75`.
- Suitable mood tags of happy, energizing, intense, aggressive,
  playful, and uplifting.

For studying, the guide currently defines:

- Target energy of `0.35`.
- Maximum energy of `0.50`.
- Suitable mood tags of chill, focused, relaxed, and peaceful.

Python reads these rules, filters the catalog, and ranks eligible tracks.
The workout profile gives an additional mood preference to energizing
tracks. The studying profile favors the requested genre and focused mood.

The studying guide also describes an instrumental preference. That
preference has not yet been incorporated into the studying ranking.

### Human-in-the-Loop Workflow

The initial studying search preserves the requested genre.

When fewer tracks match than requested, the application asks whether
the listener approves including other genres. Explicit approval triggers
another search while preserving the studying mood and energy rules.

Declining, pressing Enter, or reaching end-of-input preserves the original
genre constraint.

Catalog explanations label tracks from other genres as approved
alternatives. When Gemini is enabled, its input includes the listener's
approval.

### Retrieval-Augmented Generation

Python selects the tracks. Gemini generates explanations for the selected
tracks using the listener request, retrieved guide, catalog attributes,
and ranking evidence.

The generator is instructed to use the supplied facts. It returns JSON
records containing song IDs and explanations.

The application verifies that:

- The response is a JSON list.
- Each record has an expected integer song ID.
- Song IDs are unique.
- Every selected song has an explanation.
- Each explanation contains between 1 and 50 words.

The application then attaches source references and displays titles,
artists, and scores from its catalog records.

### Specialized Prompting

The specialized prompt adds illustrative few-shot examples. It requests:

- Explanations of at most 25 words.
- An explicit `Mood:` label with the catalog mood.
- An explicit `Energy:` label with energy formatted to two decimal places.
- A connection to the requested activity.
- Identification of approved alternative genres.

The shared output validator enforces a maximum of 50 words. Compliance
with the specialized 25-word target is measured in the comparison.

### API Failure Handling

For handled API errors or invalid model output, the application displays
catalog-based explanations and identifies the fallback.

Safe handling of network transport exceptions remains to be completed.

---

## 4. Data

The catalog contains **18 songs**. I kept all 10 starter songs and added
eight fictional tracks to expand the range of genres and moods.

The CSV contains:

- ID, title, and artist.
- Genre and mood.
- Energy, tempo, valence, danceability, and acousticness.
- Popularity, release decade, detailed mood, instrumentalness,
  and vocal language.

The five advanced attributes were added as illustrative metadata during
Project 3. They are not verified measurements from a music service.

The catalog covers pop, lofi, rock, ambient, jazz, synthwave, indie pop,
electronic, country, soul, metal, classical, disco, folk, and reggae.

The data contains no listener ratings, listening history, or feedback
about actual recommendation quality.

The custom activity guide reflects project design choices. Its mood
labels and thresholds may not fit every listener.

---

## 5. Strengths

### Transparent Ranking

The scoring explanations make it possible to inspect why tracks rank
above one another.

In the original demo, Sunrise City ranked first for High-Energy Pop
with **3.97**. Its pop genre, happy mood, and energy of `0.82` matched
the profile's preferences and `0.85` energy target.

Library Rain ranked first for Chill Lofi with **3.90**, and Storm Runner
ranked first for Deep Intense Rock with **3.99**.

### Retrieved Guidance Changes Behavior

The workout filter initially considered energy alone and selected
Winter Signal, which is tagged sad and melancholic.

Adding suitable mood rules removed it from the workout recommendations.
The verified revised playlist contained Neon Tide, Storm Runner,
and Gym Hero.

An automated test confirms that increasing the retrieved minimum energy
threshold removes a lower-energy candidate.

### Listener Control

A request for three calm jazz songs for studying finds one exact match,
Coffee Shop Stories.

The application preserves that genre constraint until the listener
approves alternatives. After approval, Focus Flow and Library Rain can
be included while retaining the studying energy and mood restrictions.

### Grounded Explanations and Fallback

Successful Gemini runs explained selected tracks using their actual
catalog mood and energy values.

When API calls returned service errors, the application continued
displaying catalog-based recommendations.

---

## 6. Limitations and Biases

### Small and Uneven Catalog

Several genres have only one track. The catalog cannot represent the
range of artists, languages, cultures, or preferences in real music
listening.

Sparse coverage can make a request impossible to satisfy fully.

### Subjective Activity Rules

Mood labels, suitable workout moods, and studying thresholds reflect
design assumptions. For example, including aggressive tracks in a
workout playlist may suit some listeners and exclude others.

### Limited Request Language

The application accepts specific request patterns. It does not yet
support unrestricted conversation, multiple activities in one request,
or arbitrary combinations of preferences.

### Ranking Bias

The original genre bonus can place an exact genre match above a track
that better matches mood and energy.

Repeatedly favoring exact genres can reduce exposure to relevant tracks
from other genres. Approval-based broadening gives listeners control
over one way to expand their results.

### Incomplete Use of Metadata

Baseline scoring does not use tempo, danceability, or acousticness.
The studying guide's instrumental preference is currently descriptive
and still needs implementation or revision.

### Generated Wording

Gemini can use imprecise language. During testing, it sometimes described
a nearby energy value as matching the target.

Structural validation does not prove that every statement in an
explanation is accurate. A returned song ID can be valid while its
explanation still needs correction.

### External Service Availability

Live generation depends on model access, API limits, connectivity, and
service availability. A fallback run does not establish successful
AI generation for that request.

### Evaluation Scope

Automated tests check defined behaviors. They do not measure listener
satisfaction or establish reliability across every possible input.

The prompt comparison used one request and one generation per style.
Broader experiments are needed before generalizing the results.

---

## 7. Evaluation and Reliability Results

### Project 3 Baseline Evaluation

I ran the original CLI and confirmed that it loaded 18 songs and
displayed five recommendations with scores and reasons for each profile.
Both starter tests passed at that stage.

| Profile | Preferred genre | Preferred mood | Target energy | First recommendation | Score |
|---|---|---|---:|---|---:|
| High-Energy Pop | pop | happy | 0.85 | Sunrise City | 3.97 |
| Chill Lofi | lofi | chill | 0.25 | Library Rain | 3.90 |
| Deep Intense Rock | rock | intense | 0.90 | Storm Runner | 3.99 |

### Profile Comparisons

- Sunrise City led High-Energy Pop because it matched the genre and
  mood and was close to the higher energy target.
- Library Rain led Chill Lofi because it matched both categories
  and was close to the lower energy target.
- Gym Hero earned genre points for High-Energy Pop and mood points
  for Deep Intense Rock.
- Spacewalk Thoughts benefited from the low energy target and chill
  mood in the Chill Lofi profile.
- Winter Signal ranked third for Deep Intense Rock because its energy
  exactly matched the target, despite mismatched genre and mood.

### Manual Weight Comparison

For High-Energy Pop, Gym Hero scored **2.92** and Rooftop Lights scored
**1.91** using the baseline weights.

Giving mood two points and genre one point reversed their order.
Rooftop Lights scored **2.91**, and Gym Hero scored **1.92**.

The tracks and listener preferences stayed the same.

### Project 3 Edge-Case Test

I tested a profile requesting rock, a sad mood, and energy of `0.90`.

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

Storm Runner ranked first because the genre bonus outweighed Winter
Signal's exact mood and energy matches.

### Project 3 CLI Weight Experiment

I lowered genre weight from `2.0` to `1.0` and increased energy weight
from `1.0` to `2.0`. Mood weight remained `1.0`.

| Chill Lofi song | Baseline rank | Baseline score | Experiment rank | Experiment score |
|---|---:|---:|---:|---:|
| Spacewalk Thoughts | 4 | 1.97 | 3 | 2.94 |
| Focus Flow | 3 | 2.85 | 4 | 2.70 |

Spacewalk Thoughts moved ahead because it matched the chill mood and
its energy of `0.28` was close to the `0.25` target.

Library Rain stayed first for Chill Lofi. The top-five order for
High-Energy Pop and Deep Intense Rock stayed the same, although scores
changed.

### Project 4 Automated Tests

The latest verified suite result after integrating specialized prompting
was:

```cmd
python -m pytest -q
```

```text
38 passed in 0.93s
```

The suite covers the original recommender, request validation, guide
retrieval and parsing, studying constraints, model-output validation,
and listener approval behavior.

Model-output tests use simulated responses. They do not make live
Gemini calls.

### Project 4 CLI Evaluation Harness

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

The 100% result applies to these eight predefined cases.

### Observed Guardrail and Workflow Behavior

| Input or condition | Evaluation criterion | Observed result |
|---|---|---|
| Blank request | Explain the required input | Pass — validation message displayed |
| Request for zero songs | Enforce count range | Pass — request rejected |
| Unknown studying genre | Explain unavailable genre | Pass — request rejected |
| Three calm jazz songs, answer N | Preserve requested genre | Pass — Coffee Shop Stories only |
| Three calm jazz songs, answer y | Broaden only after approval | Pass — jazz match plus two eligible lofi tracks |
| End-of-input at approval | Preserve original constraint | Pass — broader search not authorized |
| Three calm lofi songs | Avoid unnecessary approval | Pass — three exact matches returned |
| Model returns unknown or duplicate IDs | Reject invalid response | Pass in simulated-response tests |
| API returns 503 or 504 | Show an identified fallback | Pass in observed live runs |

### Live Generation Evidence

Successful live runs were verified for:

- Workout explanations.
- Lofi studying explanations.
- Approved cross-genre studying explanations.
- Specialized workout explanations.

Recorded evidence includes:

- [Workout AI execution](evidence/workout_ai.txt)
- [Declined studying search](evidence/studying_declined.txt)
- [Approved studying search](evidence/studying_approved.txt)
- [Approved studying search with Gemini](evidence/studying_approved_ai.txt)
- [CLI evaluation summary](evidence/evaluation.txt)

---

## 8. Baseline vs. Specialized Output

### Method

I compared baseline and specialized prompts using
`gemini-3.5-flash-lite`.

Both runs used:

- The request `Give me 3 upbeat songs for a workout`.
- The same three retrieved tracks.
- The same workout guide.
- The same model, output limit, and validation.

The specialized prompt added illustrative few-shot examples and
requested concise explanations with explicit mood and energy labels.

```cmd
python compare_prompts.py
```

This experiment used one live generation per style.

### Observed Results

| Style | Average words | At most 25 words | Correct mood labels | Correct energy labels |
|---|---:|---:|---:|---:|
| Baseline | 23.3 | 3/3 | 0/3 | 0/3 |
| Specialized | 16.0 | 3/3 | 3/3 | 3/3 |

Average explanation length decreased by approximately **31%**.
Both styles stayed within 25 words.

All three specialized explanations used the requested labels with
the correct catalog values.

### Baseline Example — Neon Tide

> For your workout request, Neon Tide features an energizing mood and an energy level of 0.88, closely matching the target energy of 0.90.

### Specialized Example — Neon Tide

> Mood: energizing. Energy: 0.88. Fits a workout and is close to the guide target of 0.90.

### Interpretation

The specialized prompt produced shorter explanations with consistently
labeled evidence in this experiment.

The baseline also described the correct mood and energy values.
Label scores measure compliance with the requested style. They do not
measure overall factual accuracy.

Word counts exclude source references appended by the application.
Both styles use the same selected songs, so this comparison measures
explanation behavior.

### Application Integration

```cmd
python -m src.main --request "Give me 3 upbeat songs for a workout" --ai --specialized
```

### Full Comparison Evidence

The actual outputs and measurements are saved in
[evidence/prompt_comparison.md](evidence/prompt_comparison.md).

---

## 9. Potential Misuse and Mitigations

### Overstating Recommendation Quality

A user could interpret a high score as a guarantee that a track is
suitable or enjoyable.

The documentation explains that scores come from rules and illustrative
metadata. Listener feedback would be needed to assess enjoyment.

### Unsupported Claims in Generated Text

Generated explanations could introduce unsupported statements about
lyrics, health, or performance.

The prompt restricts explanations to retrieved facts and excludes
invented health effects. Output validation checks IDs and format.
Manual factual review remains necessary because those checks do not
validate every claim.

### Ignoring Listener Preferences

An application could silently replace a requested genre when exact
matches are scarce.

This application asks before broadening a studying search. Declining
or providing no approval preserves the original genre constraint.

### API Credential Exposure

The application reads the API key from an environment variable.
The key should be kept out of source files, screenshots, execution
evidence, and Git commits.

### Retrieved Content Quality

Editing the guide changes system behavior. Malformed numeric rules
are rejected, but the application cannot determine whether every
well-formed rule is appropriate.

The catalog and guide should be reviewed when changed, followed by
the test suite and evaluation harness.

---

## 10. AI Collaboration and Design Reflection

### How I Used AI

I used an AI assistant to plan the project, reuse the existing ranking
code, write Python modules, design tests, interpret errors, and prepare
documentation.

I copied proposed changes into VS Code, ran commands, and shared their
outputs for review. I checked the recommendations and test results
throughout development.

### One Suggestion I Accepted

I accepted the suggestion to reuse the existing Python ranking function
and give Gemini the selected tracks and retrieved guidance.

This kept selection understandable through numeric scores while adding
natural-language explanations grounded in catalog evidence.

I also accepted a human approval step before broadening a studying
request because it gives the listener control over a meaningful change.

### One Suggestion I Revised

The initial workout filter used high energy as its main suitability
condition. It selected Winter Signal, which has sad and melancholic tags.

I applied a revision that requires both sufficient energy and a suitable
mood from the retrieved guide. The revised playlist excluded Winter
Signal and returned Neon Tide, Storm Runner, and Gym Hero.

This changed an early AI-assisted implementation after inspecting its
actual output.

### What Surprised Me During Reliability Testing

A high-energy track could pass a workout filter while still conflicting
with the request's upbeat mood. This showed me that a valid numeric
match can miss part of the listener's intent.

I also observed that a successful API connection test did not guarantee
that later generation requests would succeed. Service errors made the
fallback behavior necessary.

### What I Learned About Verification

I initially encountered a pytest collection error because the assistant
used the reserved parameter name `request`. Renaming it to
`playlist_request` fixed collection.

Testing also exposed an indentation problem that prevented studying
requests from reaching their intended handler.

These experiences reinforced the need to run suggested code and inspect
its behavior before accepting it as complete.

### System Design Trade-Offs

Python rules make ranking and constraint checks reproducible. Their
limited request patterns and fixed preferences reduce flexibility.

Gemini makes explanations easier to read, but introduces latency,
service dependencies, and possible wording errors.

Human approval adds one interaction when matches are scarce. That
interaction makes a change to the listener's preference explicit.

### Personal Reflection

My original learning moment was seeing Gym Hero rank above Rooftop
Lights for the High-Energy Pop profile. The genre bonus was worth more
than the mood match, which explained a result I had not expected.

Project 4 extended that lesson. Retrieval, ranking, generation, and
verification each need to serve the listener's request. An explanation
can sound reasonable while a filter is incomplete, and a working API
call can be followed by a service failure.

I learned to inspect outputs, revise assumptions, test failure cases,
and keep evidence of the decisions made during development.

---

## 11. Future Improvements

- Apply the studying guide's instrumental preference consistently.
- Add safe handling for network transport exceptions.
- Expand factual checks for generated explanations, including numeric
  comparisons and approved-alternative wording.
- Evaluate more requests and repeat prompt comparisons across runs.
- Support multiple preferred genres and moods.
- Collect listener feedback to compare ranking strategies.
- Add a visual interface that reuses the tested recommendation logic.
- Expand the catalog in future versions after reviewing coverage and
  metadata quality.

---

## 12. Reproducibility and Supporting Files

The verified live model for the recorded comparison is
`gemini-3.5-flash-lite`. Model access and availability can change.

Configuration uses the `GEMINI_API_KEY` and `GEMINI_MODEL`
environment variables.

| File | Purpose |
|---|---|
| `README.md` | Setup, commands, demonstrations, and project overview |
| `data/songs.csv` | Existing 18-song catalog |
| `data/curation_guides.md` | Custom activity guidance |
| `src/recommender.py` | Song scoring and ranking |
| `src/curator.py` | Workout handling and activity routing |
| `src/study_curator.py` | Studying filters and approved genre broadening |
| `src/guide_retriever.py` | Guide-section retrieval |
| `src/llm_client.py` | Model generation and response validation |
| `src/prompts.py` | Baseline and specialized prompts |
| `tests/` | Automated behavior checks |
| `evaluate.py` | Predefined CLI evaluation cases |
| `compare_prompts.py` | Live prompt comparison |
| `ai_interactions.md` | Development history and workflow traces |
| `evidence/` | Recorded executions and comparison results |

The final README, Mermaid architecture source, presentation, and
fresh-clone verification remain to be completed at this stage.