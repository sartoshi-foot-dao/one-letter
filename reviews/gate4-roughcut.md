# Gate 4: rough cut (16:9, silent)

- Output: `out/one-letter-16x9-roughcut.mp4`, 1920×1080, 30 fps, 720 frames, 24.00 s, 0.6 MB (x264 CRF 16).
- Render: on ser5 in the `one-letter-render` image (python 3.11-slim + ffmpeg + pillow 12.2.0), 8 workers, 20 s wall time. Command: `sh render.sh 30 8` in `~/jobs/one-letter`.
- Fonts: ser5 renders with **DejaVu** (mounted read-only). The Gate 3 stills used Iowan Old Style on the Mac, so the serif looks heavier and wider here. Decision for Gate 6: keep DejaVu (reproducible anywhere), or mount a licensed serif into the container.
- Sheets: `contact-roughcut-beats.png` (one frame per beat, taken from the encoded frames) and `contact-roughcut-transitions.png` (8 frames decoded from the mp4 at transition points).

## Before this render: Gate 3 open items, all fixed

Shot 5 captions ("after attention", "output"). Attention arcs given room; the candidate row steps aside during 9.0–16.0. Poster legend "• not its favourite". Labels sit next to what they label. A dim m is left in the candidate row after the flight.

## Judged on rendered frames only: three largest defects (for Gate 5)

| Rank | t | Evidence | Local fix |
|---|---|---|---|
| 1 | whole film | **Not readable at phone size.** Labels are 34 px, values 28–30 px, captions and "start" 24 px. Played full-width on a 390 px phone, they're about 6–7 px tall. Fails checklist item 1. | Labels ≥ 48 px, values ≥ 40 px, captions ≥ 36 px. Fewer printed values in the attention matrix if they don't fit (keep h3's 0.98). |
| 2 | 9.0–9.3, then each head +1.1 s | **Awkward mid-draw arcs.** The draw-on path makes partial arcs read as a hook or a "P" (frame 9.15). Fails "no awkward mid-transition frames". | Draw each arc at full shape and grow its thickness from 0 to the weight over 300 ms, instead of drawing it along its path. |
| 3 | 0.0–2.6 | **The hook doesn't say "choosing".** The 27-way strip that precedes each letter is up for 150 ms, ~300 px wide, at 55% opacity (frame 0.20). What reads is letters landing in a row: the generic opening the brief bans. | Give the first letter's strip ~0.6 s at full size before it lands; later letters keep the quick flicker. Time is taken from shot 2's empty hold (4.4–5.5). |

Also seen, lower priority: frames 3.6–4.4 show "k a" travelling with no start ring or slot yet, which reads fine in motion. The first 0.25 s is an empty ground.

## Not yet checked (Gate 6)

Sound (none yet), the 9:16 composition, and the final poster frame choice.
