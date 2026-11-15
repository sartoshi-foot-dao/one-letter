# One Letter: what still needs a human

Status: Gate 6 is complete. Both formats are rendered with sound and passed the automatic checks. The items below are the ones a script can't judge.

## Deliverables (`out/`)

| File | What |
|---|---|
| `one-letter-16x9.mp4` | 1920×1080, 30 fps, 33.70 s, H.264 + AAC 192k, −18.2 LUFS integrated |
| `one-letter-9x16.mp4` | 1080×1920, its own composition (not a crop), same timeline and soundtrack |
| `one-letter-16x9-poster.jpg`, `one-letter-9x16-poster.jpg` | the last frame (32.8 s real): all 20 names, dots for not-the-favourite, "4,192 numbers · pure Python" |

Rebuild everything: `sh render.sh 30 8` inside the `one-letter-render` image (see `Dockerfile`). On ser5 the full build took about a minute.

## Checked automatically

- **Numbers:** every value on screen is read from `assets/trace.json` (accepted against the unmodified run, 20/20 names) or `featured.json`.
- **Sync:** `reviews/sync-report-{16x9,9x16}.md`. 53 cues. Isolated onsets are within 3 ms of their cue. Every discrete picture event changes the frame at or after its cue, up to 33 ms later because of 30 fps. Muxed audio offset vs the WAV is 0.0 ms in both files.
- **Die clicks:** the 12 wheel clicks are the exact times the marker crosses each segment boundary before m. They are computed by inverting the picture's ease, not placed by ear.
- **Contact sheets:** `contact-final-{16x9,9x16}-beats.png` and `-die-strip.png`, taken from the frames that were encoded.

## Needs your eyes and ears

1. **Listen once with eyes closed** (the article's test). I couldn't listen. Sync is measured, but taste isn't. Specifically:
   - Is the entropy drone too quiet or too droning?
   - Does the bell at 19.6 s feel like a payoff?
   - Are the 20 name ticks at 20.7–21.5 s busy?
2. **The 20.5 s downbeat sits only +3.8 dB above the ringing bell.** Audible in measurement, maybe weak in practice.
3. **Font: DejaVu (current) vs a licensed serif.** ser5 renders with DejaVu Serif and Sans, which are heavier and wider than the Iowan Old Style used in the Mac stills. Using another serif means mounting it into the container, a single change in `film.py`'s `FONTS`. This is a brand decision, so I left it to you.
4. **Phone check, 9:16:** play `one-letter-9x16.mp4` on an actual phone. The 36 px captions ("after attention", "start") are the smallest text.
5. **Wording of the claim.** The closing card says "67 of 118 letters were not its favourite". That's true for this seeded run at temperature 0.5. If the film travels without context, consider "in this run".
6. **Attribution:** the model is Karpathy's microgpt (`microgpt.py` header) and the data is makemore `names.txt`. The film doesn't credit either on screen. Add a line to the lab page or an end card.

## Known, accepted

- 19.6–19.8 s (16:9): the flying m crosses its "chosen · 0.03" label for about 4 frames.
- At 9:16, the tray shows the top 6 letters plus the chosen m plus "other 0.13". The 27-way story is carried by the die strip above it.

## Pacing revision (after the first watch)

Feedback: "both go a little fast". I added 9.7 s of reading holds at 12 rest points, with no motion slowed (see `shotlist.md`). Checks:
- every hold starts on a frame already at rest (0.00 mean pixel change), apart from the camera push, which glides through 17.3 and 20.2 by design
- the sync report still shows 0 failures, and the mux offset is 0.0 ms
- loudness fell to −18.2 LUFS, because there's more drone-only time

Still to judge by eye: whether 33.7 s now drags anywhere, especially the 1.5 s hold after the die lands.
