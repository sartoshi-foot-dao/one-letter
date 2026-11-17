# Viewer study: does *One Letter* teach that language models sample?

Status: design draft (2026-11-14). Not run, not preregistered, no ethics review yet.
Goal: the evidence the paper is missing. Without it the paper is a system description; with it, it can claim the film teaches something.

## Question

The film's one-sentence claim is that a language model **rolls a weighted die** over its options instead of always taking the favourite. Do viewers come away understanding that, and is it the die beat that does it, rather than simply watching a well-made animation of a transformer?

- **H1 (primary):** viewers of *One Letter* score higher on a sampling-understanding test than viewers of an otherwise identical film that shows the model taking its favourite letter.
- **H2:** viewers of *One Letter* score higher than readers of a text explanation of the same length and content.
- **H3 (exploratory):** the advantage in H1 is larger for people with little prior machine-learning experience.

## Design

Between-subjects, three arms, randomised 1:1:1. There is a pre-test, the material, an immediate post-test, and an optional delayed post-test one week later.

| Arm | Material | What it isolates |
|---|---|---|
| **A: One Letter** | The published 16:9 film, 34 s, with sound. The die lands on `m` (p = 0.03, favourite `r` 0.37). The closing card says that in this run 67 of 118 letters were not the favourite. | the full treatment |
| **B: Favourite-only film** | **Rendered** (`out/one-letter-B-{16x9,9x16}.mp4`, 33.70 s like A, −18.0 vs −18.2 LUFS). The same step `ka` → ?, with **identical** embeddings, attention, MLP and probabilities, taken from the run's third name, **karai**, where the model wrote its favourite `r` (0.37). The model is deterministic given the prefix, so every number in shots 2–6 matches A; the check script asserts this. Shot 6 says "the most likely letter" and `r` lands in gold, with no die strip, no wheel clicks and no "chosen" leader. Shot 7 has no not-the-favourite dots and no "67 of 118" card. The timeline, holds, bell and every other cue are unchanged. | the sampling story, with production, numbers and length held constant |
| **C: Text** | About 120 words covering the same five steps and the same numbers as A, including the die and the 67/118 count, shown for a minimum of 34 s with the same five-step diagram as a static image. | the medium: film vs text with the same content |

Arm B keeps the brief's rule "never invent numbers". It doesn't fake an argmax outcome for kamon; it shows karai, a real name from the same run that reached the same prefix and took the favourite. The selection rule ("the first other sample with the same prefix whose step took the argmax") is in `src/check_trace.py`. B is the kind of explanation that stops at "the most likely next letter", which is what the paper argues is common.

## Participants

- Recruited online (e.g. Prolific). Adults, fluent in English, desktop or laptop (the 16:9 cut). A phone arm with the 9:16 cut can come later.
- Screening: none on ML experience. It is measured and used for H3, because the film's audience is curious readers, not specialists.
- **Sample size:** for H1, a contrast of two arms on the post-test score adjusted for the pre-test (ANCOVA), assuming d = 0.4, α = 0.05 two-sided and power 0.80, needs about 100 per arm. Recruit 110 per arm (330) to allow about 10% exclusions. H1 and H2 are corrected with Holm.
- **Cost estimate:** about 7 minutes per person. At roughly £9/hour plus platform fees that is about £1.40 each, or around £500 in total, plus about £100 for the pilot and the delayed follow-up.

## Procedure (about 7 minutes)

1. Consent, demographics, prior experience (3 items: used a chatbot; can say what a neural network is; has trained a model).
2. **Pre-test:** the 6 core items below.
3. **Material** for the assigned arm. Play controls are disabled until the first full play has finished, then rewatching is allowed and logged. Sound-on is checked with a short tone test before the film.
4. **Post-test:** the 6 core items in a parallel form (same structure, different numbers), plus 3 transfer items and a confidence rating on each.
5. Perceived understanding (1 item, 7-point) and engagement (2 items).
6. Optional: invitation to a 2-minute delayed post-test 7 days later.

## Measures

**Primary outcome:** the sampling-understanding score, 0–9 (6 core + 3 transfer items). Items are scored automatically; free-text answers use a rubric, and two coders score a 20% subsample.

Core items (pre and post use parallel numbers):
1. *A model gives `r` a 37% chance and `m` a 3% chance as the next letter. What does it write?* (Always `r` / Usually `r`, sometimes another letter / Always the rarest / Can't say). Correct: usually `r`, sometimes another letter.
2. *Out of 100 runs from the same point, about how many times would it write `m`?* (number; correct within 1–6)
3. *You run the same model twice from the same starting point. Will it write the same name both times?* (Yes always / Not necessarily). Correct: not necessarily.
4. True/false: *A language model always outputs its most likely next letter.* Correct: false.
5. *Where does the randomness come from?* (free text; credit for any mention of drawing or sampling from the probabilities)
6. *The model wrote a letter it gave only 3%. Was that a malfunction?* (Yes / No, it's expected sometimes). Correct: no.

Transfer items (post only, not shown in any arm):
7. *A model gives four options 50/30/15/5%. Sketch or describe what happens over 20 runs.*
8. *A setting called temperature makes the probabilities more even. What happens to how often the favourite is chosen?*
9. *Why might a chatbot give a different answer if you ask the same question again?*

**Secondary:** confidence calibration (the gap between confidence and correctness), perceived understanding, engagement, rewatch count, and score at 7 days.

**Manipulation check (end of study, so it doesn't prime):** *In what you watched or read, was the letter the model wrote its most likely option?* A should answer no and B yes.

## Exclusions (set before data collection)

- The material wasn't played or displayed in full (from the playback log).
- The sound check failed (A and B only).
- Failed one of two instructed-response checks.
- Finished in under 3 minutes.

## Analysis

- H1, H2: ANCOVA of the post-test score on arm, with the pre-test score as a covariate; planned contrasts A−B and A−C, Holm-corrected; effect sizes with 95% CIs.
- H3: add prior experience and its interaction with arm (A vs B only), reported as exploratory.
- Ceiling check: if the pilot shows a mean pre-test score above 7 of 9, harden the items before the main study (item 2 and the transfer items are the likely discriminators).
- Report everything, including null results. A null on H1 would mean the die beat doesn't add much beyond the explanation the rest of the film already gives, and that is worth stating in the paper.

## Before running

1. **Ethics:** most venues need ethics review for human-participant research. Without an institutional board, the options are an independent review board or a collaborator's institutional review board. This needs deciding first.
2. ~~Render arm B~~ Done 2026-11-16: `ARM=B sh render.sh 30 8`. 40 cues (A's 53 minus 12 die clicks and the run-count chord), worst onset error 3 ms, 0 failures, mux offset 0.0 ms in both cuts. Arm A is unchanged: 24 test frames are pixel-identical to the published render. Still to watch once: B holds still bars from 17.4 to 19.6 s film time with nothing moving, where A has the die.
3. **Write arm C** and have someone who hasn't seen the film check it against A for content parity.
4. **Pilot:** n = 20 per arm, to check item difficulty, timing and the sound check. Pilot data are not used in the main analysis.
5. **Preregister** on OSF or AsPredicted: hypotheses, items, exclusions and analysis exactly as above.
6. Build the survey (e.g. Qualtrics or a small self-hosted page with logged playback). No personal data beyond the platform ID, deleted after payment.

## Later questions (not in this study)

- Sound on vs off (does the die click and bell help?).
- 9:16 on phones vs 16:9 on desktop.
- An honest-numbers film vs one with tidied, invented numbers: does provenance change trust or learning? This is the paper's deeper claim but needs its own design.
