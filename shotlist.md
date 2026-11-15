# Shot list: *One Letter* (24 s of action + 9.7 s of reading holds = 33.7 s, 16:9 primary)

`⟨name⟩` is the featured sample and `⟨k⟩` is its featured position. Both are chosen by the rule in `brief.md` after `trace.json` exists. `⟨c⟩` is the letter sampled at `⟨k⟩`. Every value in brackets is read from the trace, never typed.

**Resolved by rule v2** (`assets/featured.json`): `⟨name⟩` = **kamon**, `⟨k⟩` = 2 (prefix `ka`), `⟨c⟩` = **m** at 0.03, favourite **r** at 0.37. `⟨n_active⟩` = 7. The run-wide fact is that 67 of 118 picks were not the favourite.
Shot 6 labels the top 5 *plus* the chosen letter, since `m` is ranked below the top 5. Shot 7's card becomes: `67 of 118 letters: not the favourite`.

The viewer's knowledge at each exit state is the contract. If a shot can't change what the viewer knows, it is cut.

| # | Time | Beat | Entry state | What happens | Exit state (viewer knows) | Data source |
|---|---|---|---|---|---|---|
| 1 | 0.0–3.0 | HOOK | Empty ground | `⟨name⟩` spells itself letter by letter. Before each letter lands, a faint 27-bar strip flickers underneath it for 150 ms. | "Something is choosing these letters, and it's choosing between options." | sampled tokens; per-position probs |
| 2 | 3.0–5.5 | PROBLEM | full name | The name rewinds to position `⟨k⟩`. The remaining letters fall away. 27 candidates (a–z, ⏎) appear as a dim row. Label: `27 options · which one?` | "We're about to watch one choice." | vocab |
| 3 | 5.5–9.0 | VECTORS | prefix + candidates | Each prefix letter drops a 16-cell column (token + position embedding, after rmsnorm). They are coloured by the real values. Label: `each letter → 16 numbers` | "Letters become lists of numbers." | `wte`, `wpe`, normed x |
| 4 | 9.0–13.5 | ATTENTION | columns | Cyan arcs are drawn from the current position back to every prefix position, one head at a time, 4 heads in about 1 s each. Thickness is the real weight. The heads show different patterns. Label: `attention · 4 heads` | "It looks back at what it has written, in four different ways." | attn weights [4 × ⟨k⟩] |
| 5 | 13.5–16.0 | MLP | arcs collapse into one column | The column expands to 64 cells. Cells with ReLU > 0 light up and the rest go to ground. The count is printed: `⟨n_active⟩ / 64 active` | "Then it transforms that mix." | MLP post-ReLU |
| 6 | 16.0–20.5 | PROOF | 16-cell output column | Slow camera push. The column projects onto the 27 candidates as bars (temperature-0.5 probabilities, 2-decimal labels on the top 5). A die-roll mark sweeps along the cumulative distribution and stops: `⟨c⟩` turns gold and drops into place. If `⟨c⟩` ≠ argmax, the argmax bar gets the label `most likely` and `⟨c⟩` gets `chosen`. | "It wasn't certain. It rolled a weighted die, and the die didn't land on the favourite." | probs, sampled token |
| 7 | 20.5–24.0 | CLOSE | `⟨name⟩` completed | The full 20-sample list from the run fades up in a column, with `⟨name⟩` in gold. Card: `4,192 numbers · pure Python` | Poster frame: the names, and how small the machine is. | 20 samples; facts table |

## Beat grid (sound and picture share these)

| t (s) | Cue |
|---|---|
| 0.0, then each letter in shot 1 | tick |
| 3.0 | rewind (reverse ticks) |
| 5.5, 9.0, 13.5, 16.0 | section downbeat |
| 9.0 + 1.1·h | head h arc |
| ~19.6 (from roll) | die lands: struck note, gold |
| 20.5 | close downbeat, hold to 24.0 |

Shot 1 timing (revised at Gate 5): the first choice is held. Its 27 real bars grow from 0.08 s, the sampled bar turns gold at 0.73 s, and `k` lands at 0.85 s. Each later letter lands 0.45 s after the previous one, so `n` lands at 2.65 s. These times are computed in `film.py` (`LETTER_T`), not hand-placed per frame.

## 9:16 composition (separate layout, same timeline)

- The flow runs top → bottom. The prefix row is at the top third and the probability tray at the bottom third.
- Shot 4 shows heads 2×2 stacked, not side by side.
- Shot 6 shows the top 8 candidates as horizontal bars, with the rest folded into `other ⟨Σ⟩`. The full 27 does not fit legibly.
- Labels at 40 px minimum.

## Open questions for Gate 2

- Shot 5 is the weakest beat; it only says "it transforms". It could be cut to give shot 6 more hold. The film would then be 21.5 s.
- Should shot 7 show 20 names, or only the 5 that follow `⟨name⟩`, for phone legibility?

## Reading holds (added after the first watch: "goes a little fast")

The table above is in **film time** (24 s). At each rest point below, film time stops while real time runs on. The real film is 33.7 s. Picture (`film_t`) and sound (`real_t`) both go through `HOLDS` in `film.py`, so sync is unchanged. The camera push in shot 6 runs on real time, so it keeps gliding through the holds at 17.3 and 20.2.

| Film t | Hold | What the viewer is reading |
|---|---|---|
| 2.95 | 0.8 s | the finished name |
| 5.3 | 0.8 | 27 options |
| 8.6 | 1.0 | the three 16-number columns |
| 9.4 / 10.5 / 11.6 | 0.4 each | each head's weights |
| 12.7 | 0.6 | the full 4-head matrix |
| 15.6 | 1.0 | 7 / 64 active, output column |
| 17.3 | 1.0 | the 27 bars before the roll |
| 20.2 | 1.5 | where the die landed (the bell rings out) |
| 21.9 | 1.0 | "67 of 118" card |
| 23.9 | 0.8 | poster frame |
