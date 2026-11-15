# Assets

| File | Source | Made by |
|---|---|---|
| `trace.json` | instrumented run of `../../microgpt.py` (seed 42), Python 3.11.6 | `src/record_trace.py` |
| `reference-run.log`, `trace-run.log` | stdout of the unmodified and the instrumented run | (same) |
| `featured.json` | featured step chosen by rule v2 | `src/check_trace.py` |
| `cues.json` | the 53 sound cues, each tied to a picture event | `src/audio.py` |

No external images, footage or music. All sound is synthesised from the timeline. Fonts are system fonts (DejaVu on ser5, Iowan/Menlo/Helvetica Neue for Mac stills) and are not distributed.

## Re-recorded from the public gist (2026-11-14)

The film was first recorded from a local copy of `microgpt.py` that differed from Karpathy's gist only in comments, data loading and print formatting. For this public repository the trace was re-recorded from the gist at revision `14fb038` (Python 3.11.18, Linux). Result: the same 20 names, the same final loss (2.6497), the same featured step (`kamon`, position 2, `m` at 0.0271 against `r` at 0.3727) and the same 67 of 118. Every recorded value agrees with the first recording to within 1.2e-14 (floating-point rounding), and stills rendered from either trace are pixel-identical, so the films in `out/` were not re-rendered.
