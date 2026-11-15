# Baseline vs. Specialized Prompt Comparison

Model: `gemini-3.5-flash-lite`

Request: `Give me 3 upbeat songs for a workout`

Both styles use the same retrieved tracks, guide, model, output limit, and validation. The prompt instructions differ.

This is one live run per style. Results can vary between runs.

## Baseline Outputs

| Song | Words | Correct mood label | Correct energy label |
|---|---:|---|---|
| Neon Tide | 23 | False | False |
| Storm Runner | 23 | False | False |
| Gym Hero | 24 | False | False |

### Neon Tide

For your workout request, Neon Tide features an energizing mood and an energy level of 0.88, closely matching the target energy of 0.90.

### Storm Runner

For your workout request, Storm Runner provides an intense mood with an energy level of 0.91, meeting the minimum energy requirement of 0.75.

### Gym Hero

For your workout request, Gym Hero delivers an intense mood and a high energy level of 0.93, aligning with the workout guide's target energy.

## Specialized Outputs

| Song | Words | Correct mood label | Correct energy label |
|---|---:|---|---|
| Neon Tide | 16 | True | True |
| Storm Runner | 16 | True | True |
| Gym Hero | 16 | True | True |

### Neon Tide

Mood: energizing. Energy: 0.88. Fits a workout and is close to the guide target of 0.90.

### Storm Runner

Mood: intense. Energy: 0.91. Fits a workout and is close to the guide target of 0.90.

### Gym Hero

Mood: intense. Energy: 0.93. Fits a workout and is close to the guide target of 0.90.

## Measured Summary

| Style | Average words | At most 25 words | Correct mood labels | Correct energy labels |
|---|---:|---:|---:|---:|
| Baseline | 23.3 | 3/3 | 0/3 | 0/3 |
| Specialized | 16.0 | 3/3 | 3/3 | 3/3 |

## Interpretation

These measurements assess concise wording and compliance with the specialized evidence-label format. A baseline explanation may describe correct facts without those labels. Label scores measure compliance with the requested style. Overall factual accuracy requires separate review.

The 25-word measurement excludes application-added source references. Both styles use the same selected songs. This experiment measures explanation behavior.
