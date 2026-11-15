# Gate 5: repair the three highest-impact defects

Output: `out/one-letter-16x9-gate5.mp4` (1920×1080, 30 fps, 720 frames, 24.00 s). Rendered on ser5, about 20 s.
Sheets: `contact-gate5-beats.png`, `contact-gate5-die-strip.png` (from ser5's encoded frames), and `contact-gate5-transitions.png` (decoded from the mp4).

| Gate 4 defect | Repair | Verified on |
|---|---|---|
| 1. Not readable at phone size | Labels 34→48 px, values 28–30→40 px, captions and "start" 24→36 px, matrix head names 26→36 px, closing cards 40→56 px | beats sheet, all shots |
| 2. Awkward mid-draw arcs | Arcs appear at full shape; thickness and opacity grow 0→weight over 300 ms (closed-form ease, still seekable) | transitions 9.05 / 9.15 / 9.30 s |
| 3. Hook didn't say "choosing" | Opens on the first real choice: 27 bars, full size, growing 0.08–0.43 s; k's bar turns gold at 0.73 s even though a is taller (0.31 vs 0.12); k lands at 0.85 s. Later letters tick every 0.45 s and still finish by 2.65 s, so no shot boundaries moved | transitions 0.10 / 0.30 / 0.78 / 1.00 s |

## Regression found and fixed in the same gate

The larger type made shot 6 collide: "0.37" ran into "most likely", "chosen" sat on the 0.27 bar, and the 0.03 value sat on the l bar. Repairs: "most likely" moved above its value; the chosen bar's value moved into its gold label (`chosen · 0.03`), which sits left of the bars on a leader; the shot labels moved to the right, above the die strip. Checked at 20.3 s and across the die strip at 18.6–20.0 s.

## Remaining, accepted for now

- 19.6–19.8 s: the flying m crosses the "chosen · 0.03" label for about 4 frames. It reads as motion, not as a collision.
- At 2.6 s, the later letters' 150 ms flicker strips are small. That's intentional: the hook carries the idea, and the ticks only echo it.

## Left for Gate 6

Sound on the beat grid, the 9:16 composition, the serif choice (DejaVu on ser5 vs a mounted licensed serif), and the final poster frame.
