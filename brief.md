# Brief: *One Letter* (working title)

Status: **Gate 6 complete (2026-11-08).** Both formats are rendered with sound. Open items are in `reviews/human-review.md`.
Gate log: `reviews/gate3-stills.md`, `gate4-roughcut.md`, `gate5-repairs.md`, `sync-report-*.md`.

## Film

**One sentence the viewer should remember:**
A language model picks the next letter by turning everything it has seen into 27 probabilities and rolling a weighted die. In this model every one of those numbers fits on one screen.

- **Audience:** curious technical readers of the lab. They know what a neural net is in general but have not seen one compute something end to end.
- **Duration:** 24 s of action. After the first watch, reading holds were added, so the real film is 33.7 s (see `shotlist.md`).
- **Formats:** 16:9 (1920×1080) as the primary cut. 9:16 (1080×1920) is a separate composition, not a crop.
- **Home:** the "Inside a tiny language model" entry on lab.zidingz.com, which currently has no accepted artifact.

## Product facts (the only numbers the film may show)

These come from `microgpt.py` (originally a local copy; since the public release, Karpathy's gist at revision `14fb038`, see `README.md`). Anything else on screen must come from `assets/trace.json` (see below).

| Fact | Value |
|---|---|
| Training data | ~32k first names, one per line (makemore `names.txt`) |
| Vocabulary | 27 tokens: 26 letters + BOS |
| Parameters | 4,192 |
| Shape | 1 layer, 4 attention heads, 16-dim embeddings, MLP 16→64→16, context 16 |
| Nonlinearity | plain ReLU (not ReLU², which is what `visualizer/` uses) |
| Training | 1,000 Adam steps, seed 42 |
| Sampling | temperature 0.5, stops at BOS |
| Dependencies | none: stdlib Python, scalar autograd |

## Assets

| Asset | Path | State |
|---|---|---|
| Recorded trace | `assets/trace.json` | **Missing. Blocker for Gate 3.** |
| Model source | `third_party/microgpt.py`, downloaded by `scripts/fetch_microgpt.sh` (not redistributed) | Present after fetch |
| Audio | — | **Open decision**, see below |
| Logo or wordmark | — | None. The film ends on a text card, not a logo |

**trace.json contract.** An instrumented copy of `microgpt.py` that uses the same seed and the same code path records, for every sample of the 20-name inference run:
for each position, the token, `wte` and `wpe` rows, the residual stream before and after each block, attention weights per head, the 64 MLP pre- and post-ReLU activations, the logits, the temperature-0.5 probabilities, and the sampled token.

Acceptance check: the 20 names in the trace must exactly match the 20 names printed by unmodified `python3 microgpt.py`. If they differ, the trace is rejected. We do not patch it by hand.

**The featured name** is not chosen by taste. It is the first sample of length ≥ 4 that contains a position whose sampled letter is *not* the argmax. Rationale: that step shows the weighted die honestly. If no sample has one, use the step with the highest entropy and say "most likely letter" on screen. The name is unknown until the trace exists. The shot list uses `⟨name⟩`.

### Gate 3 record (2026-11-08)

- **Trace: ACCEPTED.** `src/record_trace.py` patches 7 anchors in `microgpt.py` with record-only calls and execs it unchanged otherwise. The 20 names match the unmodified run exactly (`assets/reference-run.log`). The final loss is identical in both runs (2.6497) and `num params` is 4192. Python 3.11.6. Source SHA-256 is stored in `trace.json`.
- **Featured-name rule v1: DEFECT.** It selects `kamon` at position 0 (BOS→`k`, 12% vs `a` 31%). Position 0 has no prefix and all four heads put weight 1.0 on the only position, so shots 3–4 would be empty. This is a flaw in the rule, not in the trace.
- **Rule v2: ADOPTED (zi, 2026-11-08).** Adds `pos ≥ 2`. Implemented in `src/check_trace.py`, with the output in `assets/featured.json`. It selects `kamon`, position 2: `ka` → `m` at **2.7%**, where the favourite was `r` at 37%. Heads at that step: h1 ≈ uniform (.36/.32/.32), h3 puts .98 on `k`. MLP: 7 of 64 units active. `m` is not in the top 5 (r .37, n .27, l .07, y .06, i .04).
- **New fact available for the film:** in the whole 20-name run, **67 of 118** sampled tokens were not the model's top choice. Off-favourite sampling is the norm here, not a cherry-picked event.

## Visual rules

- **Keep:** the house film look from *Emission Time* (see `style-guide.md`): dark ground, one warm accent, numbers set in monospaced figures.
- **Avoid:** glowing neural-net node graphs, particle swarms, "brain" imagery, centred headline over a gradient, everything-fades-in, fake code typing.
- **Never:** invent activations, probabilities, names or loss values. Never show a number that is not in the table above or in `trace.json`. Never show the visualizer's UI or its config as if it were this model.
- On-screen text: at most 8 words at a time, readable at phone size.

## Audio (decision needed at Gate 1)

1. **Synthesised cues on the beat grid** (recommended): a soft tick per token, a low tone that tracks entropy, and one struck note when the die lands. All of it is generated from the same timeline as the picture.
2. Silent, with captions only.
3. A licensed track supplied by zi.

## Renderer

Python + NumPy + Pillow frame functions on ser5, with the same contract as `closest_approach.py`: `frame = scene(ctx, t)`, pure and seekable, rendered out of order in parallel, and encoded with ffmpeg. No hidden clocks and no unseeded randomness. Any jitter is seeded from `(shot, t)`. Remotion is not used: one deterministic Python pipeline already exists and this film will be re-rendered, not templated.

## Deliverables

`out/one-letter-16x9.mp4`, `out/one-letter-9x16.mp4`, a poster frame for each, a contact sheet per format in `reviews/`, `src/` with a single render command, `assets/` with an asset list, and `reviews/human-review.md`, a short note on what still needs a human eye.

## Unacceptable results

- Any number on screen that cannot be traced to `trace.json` or the facts table.
- A featured name chosen or edited by hand.
- A viewer who can't tell, with the sound off, where to look after each move.
- A 9:16 cut that is the 16:9 cut cropped.

## Gates

1. Approve this brief, the audio choice and the asset list.
2. Approve `style-guide.md` and `shotlist.md`.
3. Record `trace.json`, pass the acceptance check, and inspect representative stills (one per beat).
4. Rough cut plus contact sheet.
5. Fix the three highest-impact defects, each with a timestamp, the evidence and a local fix.
6. Audio sync, the 9:16 composition, and final deliverables.
