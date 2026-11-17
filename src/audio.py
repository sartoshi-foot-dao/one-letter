#!/usr/bin/env python3
"""ONE LETTER soundtrack: every cue is placed from the same constants that drive the picture (film.py).

Synthesised, deterministic (no noise, no randomness): sines with exponential envelopes.
    python3 motion-studio/src/audio.py OUT.wav      # also writes assets/cues.json
Cues (shotlist.md beat grid):
  tick      each letter landing in shot 1 (LETTER_T)
  rewind    each letter falling away at 3.0 s (descending)
  downbeat  section starts 5.5, 9.0, 13.5, 16.0, 20.5
  head      attention head h appears (HEAD_T); loudness = that head's largest weight
  relu      the 7 active units light (14.5)
  wheel     the die marker crosses each cumulative boundary before it stops (exact crossing times)
  strike    the die lands: struck note (LAND_T)
  name      each closing name appears (20.7 + 0.04 i)
  drone     a low tone whose loudness follows the entropy of the step being decided
"""
import json, math, os, sys, wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film as F

SR = 48000
N = int(F.DUR * SR)
T = np.arange(N) / SR

def env_tone(t0, freqs, amps, decay, attack=0.004, dur=None):
    """Sum of sines starting at t0 with a short linear attack and exponential decay."""
    t0 = F.real_t(t0)                       # cue times are film times; place them on the real timeline
    dur = dur or min(decay * 7, F.DUR - t0)
    i0, i1 = int(t0 * SR), min(N, int((t0 + dur) * SR))
    if i0 >= N: return
    s = T[i0:i1] - t0
    e = np.minimum(1.0, s / attack) * np.exp(-s / decay)
    out = sum(a * np.sin(2 * math.pi * f * s) for f, a in zip(freqs, amps))
    MIX[i0:i1] += out * e

MIX = np.zeros(N)
CUES = []
def cue(kind, t, **kw): CUES.append(dict(kind=kind, t=round(float(F.real_t(t)), 5), film_t=round(float(t), 5), **kw))

# ---- drone: loudness follows entropy (nats) of the step being decided
H = lambda p: -sum(x * math.log(x) for x in p if x > 0)
steps = F.SAMPLE['positions']
ent = np.zeros(N)
TF = np.array([F.film_t(x) for x in T[::48]]).repeat(48)[:N]   # film time of every sample (1 ms resolution)
bounds = [F.HOOK_T0] + F.LETTER_T  # step i is being decided between bounds[i] and bounds[i+1]
for i in range(len(F.NAME)):
    ent[(TF >= bounds[i]) & (TF < bounds[i + 1])] = H(steps[i]['probs'])
ent[(TF >= 3.0) & (TF < F.LAND_T)] = H(F.STEP['probs'])
k = int(0.06 * SR); ent = np.convolve(ent, np.ones(k) / k, mode='same')        # 60 ms smoothing
LAND_R = F.real_t(F.LAND_T)
tail = np.clip(1 - (T - LAND_R) / 1.2, 0, 1); ent = np.where(T > LAND_R, H(F.STEP["probs"]) * tail, ent)  # the drone resolves after the die lands
drone = (np.sin(2 * math.pi * 55 * T) + 0.5 * np.sin(2 * math.pi * 82.41 * T) + 0.25 * np.sin(2 * math.pi * 110 * T))
MIX += 0.05 * (ent / 3.3) * drone

# ---- shot 1: ticks as letters land (the first, the hook, is struck harder)
for i, t in enumerate(F.LETTER_T):
    env_tone(t, [1760, 2640], [0.30 if i == 0 else 0.18, 0.08], 0.022); cue('tick', t, letter=F.NAME[i])
# ---- shot 2: rewind, the later letters fall away (same timing as the picture)
for i in range(len(F.NAME) - 1, F.K - 1, -1):
    t = 3.0 + 0.18 * (len(F.NAME) - 1 - i)
    env_tone(t, [1320 - 160 * (len(F.NAME) - 1 - i)], [0.12], 0.03); cue('rewind', t, letter=F.NAME[i])
# ---- section downbeats
for t in [5.5, 9.0, 13.5, 16.0, 20.5]:
    tr = F.real_t(t); i0 = int(tr * SR); s = T[i0:i0 + int(0.6 * SR)] - tr
    f = 45 + 30 * np.exp(-s / 0.05)
    MIX[i0:i0 + len(s)] += 0.38 * np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-s / 0.22) * np.minimum(1, s / 0.003)
    env_tone(t, [3000], [0.04], 0.008); cue('downbeat', t)
# ---- attention heads: one tone per head, loudness = that head's sharpest weight
for h, t in enumerate(F.HEAD_T):
    w = max(F.STEP['attn'][h])
    env_tone(t, [392 * 2 ** (h / 12 * 3), 784 * 2 ** (h / 12 * 3)], [0.10 + 0.14 * w, 0.03], 0.28, attack=0.12)
    cue('head', t, head=h + 1, max_weight=round(w, 3))
# ---- relu: the active units light together
env_tone(14.5, [1046.5, 1568], [0.08, 0.05], 0.12); cue('relu', 14.5, active=F.FEAT['mlp_active'])
# (a swell under the growing bars was cut at Gate 6: the 16.0 downbeat's tail masked it, -2.6 dB)
# ---- the die: a click at each boundary the marker actually crosses (inverse of the picture's ease_out)
cw = list(np.cumsum(F.PROBS)); tot = cw[-1]; u = F.STEP['u'] * F.STEP['u_total'] / tot
for j, c in enumerate(cw[:-1]):
    frac = c / tot
    if frac >= u: break
    r = 1 - (1 - frac / u) ** (1 / 3)                  # ease_out(r) = frac/u
    t = F.ROLL_T0 + (F.ROLL_T1 - F.ROLL_T0) * r
    if F.ARM == 'A': env_tone(t, [2200, 3300], [0.14, 0.05], 0.012); cue('wheel', t, after=F.V[j])
# ---- the strike: the die lands on m
base = 523.25
env_tone(F.LAND_T, [base, base * 2.76, base * 5.4, base * 8.93], [0.42, 0.16, 0.07, 0.03], 1.1, dur=3.6)
cue('strike', F.LAND_T, letter=F.V[F.CHOSEN], p=round(F.PROBS[F.CHOSEN], 4))
# ---- closing names and cards
for si in range(len(F.TRACE['samples'])):
    t = 20.7 + 0.04 * si
    env_tone(t, [1568 + 20 * si], [0.06 if si else 0.14], 0.03); cue('name', t, name=F.TRACE['samples'][si]['name'])
for t in ([21.2, 22.6] if F.ARM == 'A' else [22.6]):   # arm B has no run-count card
    env_tone(t, [261.63, 392, 523.25], [0.10, 0.07, 0.05], 0.9, attack=0.02, dur=2.5); cue('card', t)

# ---- master: fade the last 0.4 s, peak to -1 dBFS
MIX *= np.clip((F.DUR - T) / 0.4, 0, 1)
MIX *= 10 ** (-1 / 20) / np.abs(MIX).max()

if __name__ == '__main__':
    out = sys.argv[1]
    pcm = (MIX * 32767).astype('<i2')
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
    CUES.sort(key=lambda c: c['t'])
    json.dump(CUES, open(F.CUES_PATH, 'w'), indent=1)
    print(f'wrote {out}: {len(CUES)} cues, {F.DUR:.2f} s')
