# One Letter

**A tiny language model picks the next letter by rolling a weighted die.** This repository holds the source for a 34-second film that shows one real prediction inside [microgpt](https://karpathy.github.io/2026/02/12/microgpt/), Andrej Karpathy's 4,192-parameter GPT written in plain Python.

Watch it: **https://zidingz.com/one-letter/**

The film follows the model as it writes the made-up name `kamon`. After `ka` its favourite next letter is `r` (37%), but the weighted die lands on `m` (2.7%). In the same run, 67 of the 118 letters the model wrote were not its first choice. Every number on screen comes from a recorded run, not from an illustration.

## What is here

| Path | What |
|---|---|
| `src/film.py` | the renderer: every frame is a pure function of time, in two separate compositions (16:9 and 9:16) |
| `src/audio.py` | the soundtrack, synthesised on the same timeline as the picture |
| `src/verify_sync.py` | checks without listening that each sound starts on its picture event |
| `src/record_trace.py`, `src/check_trace.py` | record every intermediate value of microgpt's 20-name run, check it against the unmodified run, and pick the featured step by a fixed rule |
| `scripts/` | fetch the model and data, and re-record |
| `assets/` | the recorded trace, the featured step, the sound cues |
| `brief.md`, `style-guide.md`, `shotlist.md` | the written brief, look and shot plan |
| `reviews/` | contact sheets, stills, sync reports and notes from each review gate |
| `out/` | the finished films and posters (`one-letter-B-*` is the viewer-study control film, see below) |
| `paper/` | a 3-page LaTeX working draft about the method, and the design of a viewer study |

## Arm B: a control film for a viewer study

`paper/viewer-study.md` designs a study of whether the film teaches that a language model samples rather than always taking its favourite. Its control film, arm B, is rendered here as `out/one-letter-B-{16x9,9x16}.mp4`.

Arm B shows the same step, `ka` → ?, with identical numbers. It comes from `karai`, another name in the same run that reached the same prefix and wrote the favourite `r` (37%). The model is deterministic given its prefix, so every embedding, attention weight, MLP value and probability matches the main film; `src/check_trace.py` picks the step by a fixed rule and checks this. Arm B has no die, no not-the-favourite marks and no "67 of 118" card, and is otherwise the same length, timeline and sound. Render it with `ARM=B sh render.sh 30 8`.

The study has not been run. The paper is a working draft, not peer reviewed or submitted.

## Not included: microgpt and its data

This repository does not contain Karpathy's `microgpt.py` or the training names. `scripts/fetch_microgpt.sh` downloads both, pinned and checked by SHA-256, into `third_party/` (ignored by git):

- `microgpt.py` from [Karpathy's gist](https://gist.github.com/karpathy/8627fe009c40f57531cb18360106ce95), revision `14fb038`.
- `names.txt` from [karpathy/makemore](https://github.com/karpathy/makemore) at commit `988aa59` (MIT licence), about 32,000 first names.

The recorder doesn't edit the model. It reads `microgpt.py`, inserts record-only calls at seven exact text anchors and runs it. If an anchor doesn't match exactly once it stops. The trace is accepted only if its 20 names equal the unmodified script's output.

## Rebuild

Re-record the data (CPython 3.11; about 10 minutes, because training is pure Python):

```sh
sh scripts/record.sh
```

Render both films, contact sheets and sync reports (inside the image from `Dockerfile`, with DejaVu fonts available):

```sh
docker build -t one-letter-render .
docker run --rm -v "$PWD":/work -v /usr/share/fonts/truetype/dejavu:/usr/share/fonts/truetype/dejavu:ro one-letter-render sh render.sh 30 8
```

## Credits

- Model: microgpt by Andrej Karpathy.
- Data: makemore `names.txt` by Andrej Karpathy (MIT).
- Film, sound and recording code: Claude (Anthropic) for Ziding Zhang, following a "motion engineering" workflow: written brief, seekable frame function, contact-sheet review, and sound placed on the picture's clock.

## Licence

- Code (`src/`, `scripts/`, `render.sh`, `Dockerfile`): [MIT](LICENSE).
- Film, posters, stills, contact sheets, recorded data and documents (`out/`, `reviews/`, `assets/`, `paper/`, the `.md` files): [CC BY 4.0](LICENSE-CC-BY-4.0.txt). Credit "One Letter, by Ziding Zhang with Claude", with a link to https://zidingz.com/one-letter/.
- microgpt and makemore `names.txt` are not covered by these licences and are not in this repository.
