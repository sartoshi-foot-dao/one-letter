# Gate 3: representative stills (16:9)

Render: `python3 motion-studio/src/film.py stills`, about 1 s on the Mac (no ser5 needed for stills).
Sheets: `contact-16x9-beats.png` (one frame per beat), `contact-16x9-die-strip.png` (the fastest transition, 18.6–20.0 s).
9:16 is not started; that's Gate 6, per the brief.

## Data checks

- Trace re-recorded with the uniform draw `u` captured. `random.choices` is restated exactly as in CPython 3.11: one `random()` call, then a bisect over the cumulative weights. 20/20 names still match the unmodified run, so the RNG stream is unchanged.
- Featured step: u·total = 0.2264, which falls in m's cumulative segment [0.2098, 0.2369]. The die marker in shot 6 stops at the recorded value, not an illustrative one.
- Every number on screen is read from `trace.json` or `featured.json`. None is typed into `film.py`.

## Round 1: five defects, all fixed in round 2

| # | Shot / t | Evidence | Fix |
|---|---|---|---|
| 1 | 7 / 23.9 | The prefix row "○ k a" drew over "kamon" | Prefix row ends at 20.5 |
| 2 | 3 / 8.6 | `→` rendered as a missing-glyph box (Helvetica Neue) | Label is now "each letter becomes 16 numbers" |
| 3 | 5 / 15.8 | The 7 active units were barely visible: positive MLP values are small against the film-wide clamp | sqrt colour curve, still one clamp and one curve for the whole film (style guide's rule kept) |
| 4 | 6 / 20.3 | "most likely" was hidden behind the die strip; "chosen" collided with the 0.07 and 0.03 labels | Bar scale lowered; "most likely" sits beside the r bar; "chosen" is raised on a gold leader |
| 5 | 5 / 15.8 | The dimmed input columns stayed up next to the MLP | Inputs leave at 13.5, when the mixed vector arrives |

## Open after round 2 (for Gate 4, ranked)

1. **Shot 5 has two unlabelled columns** (the mixed vector and the output). A viewer can't tell what they are. Add short mono captions, or drop the output column and let shot 6 begin from the grid.
2. **Shot 4 arcs are cramped** under the columns, and the self-loop is hard to read. The weight matrix carries the meaning. Either give the arcs more room (move them above the row) or drop them in favour of the matrix.
3. **The poster frame (23.9 s) doesn't explain the dots.** The "67 of 118" card only shows 21.2–22.6. Keep a small legend on the final card. The dots are also small at phone size.
4. Labels are 32 px in the top-left corner, far from where the eye is. They're legible but disconnected from the content.
5. After the die lands, the m slot in the candidate row is empty. That reads as a missing letter. Leave a dim m.

## Style-guide note

Shot 6 shows gold in three linked places (die segment, bar, letter) for the one chosen outcome. The guide says "at most one gold object per frame". I'm reading that as one gold *meaning* per frame. Confirm, or I'll reduce it to the letter only.
