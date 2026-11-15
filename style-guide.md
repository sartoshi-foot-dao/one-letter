# Style guide: *One Letter*

Reference: the *Emission Time* film pages (`z/blog/lab-site/films/emission-time/site.css`) and the *Closest Approach* render code. Only the visual grammar is borrowed: palette, type, restraint. No shots, subjects or copy are taken from them.

## Palette (exact, sRGB)

| Token | Hex | Use in the film |
|---|---|---|
| ground | `#0b0c10` | frame background, always |
| ground-2 | `#12141a` | panels: vector strips, the probability tray |
| ink | `#e6e3dc` | letters, primary numbers |
| ink-2 | `#a9a8a2` | secondary labels |
| ink-3 | `#85868b` | axis ticks, captions (≥ 4.5:1 on ground) |
| rule | `#262932` | grid lines, cell borders |
| gold | `#e2b45c` | **the current letter / the chosen outcome only.** At most one gold object per frame |
| cyan | `#5ae6f0` | attention arcs from the current position (current selection) |

Value maps: activations use a diverging map from `#2a6a8c` (sea) through ground-2 to `#8e3340` (oxblood), clamped symmetrically at the 98th percentile of |x| across the whole trace. The clamp is fixed once for the whole film, so brightness means the same thing in every shot.

## Typography

- Letters (tokens): serif (Iowan Old Style → Palatino → DejaVu Serif on ser5), large and lowercase, which is how names appear in the data.
- Numbers: monospace with tabular figures (DejaVu Sans Mono on ser5). Probabilities show 2 decimals; activations are shown as colour, never printed.
- Labels: sans, ink-3, all lowercase, ≤ 4 words (`attention · 4 heads`).
- Minimum size: 16:9 labels 28 px, 9:16 labels 40 px.

## Composition

- The eye goes to the **current letter** first. It is gold and it always holds the same screen position within a shot.
- The flow of computation goes left → right in 16:9 and top → bottom in 9:16.
- The context (prefix letters) stays visible the whole film as a row of serif letters. It is the continuity object, as the article puts it: the same object changing role, not new objects appearing.
- Safe area: 6% inset on every side. Nothing important crosses it.

## Motion rules

| Class | Behaviour |
|---|---|
| letters | arrive with a short drop and a slight settle (critically damped spring, ~180 ms) |
| vector cells | fill column-wise, 12 ms stagger, no overshoot |
| attention arcs | draw from the current letter to past letters over 300 ms, then hold; thickness ∝ weight |
| probability bars | grow from zero, linear-out, 400 ms; the sampled bar alone turns gold |
| camera | only one move in the film: a slow push into the probability tray (shot 6) |
| text labels | cut on, never fade; hold ≥ 1.2 s |

Seekability: every animated quantity is a pure function of `t`. Springs are evaluated in closed form, not integrated step by step.

## Banned defaults

Bokeh, glow, lens flares, gradient backgrounds, particles, node-and-edge "neural net" diagrams, 3D, typewriter code, a logo sting at the end, and anything that fades in purely as decoration.
