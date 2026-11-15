#!/usr/bin/env python3
"""Check sound and picture land together, without listening.

For every cue in assets/cues.json:
  audio:   the onset (peak positive energy flux, 1 ms hop) found in the WAV within +-40 ms of the cue
  picture: the first rendered frame at or after the cue differs from the frame before it
           (discrete events only; continuous motion like the die wheel is checked by construction)
    python3 motion-studio/src/verify_sync.py OUT.wav [fps]   -> reviews/sync-report.md
"""
import json, math, os, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film as F

wav, fps = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 30
with wave.open(wav) as w:
    sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').reshape(-1, 2)[:, 0] / 32768
hop = sr // 1000
xh = np.diff(x, prepend=x[0])  # first difference = high-pass: ticks/strikes stay, drone and thumps drop
e = np.sqrt(np.convolve(xh ** 2, np.ones(hop * 4) / (hop * 4), mode='full')[:len(x)][::hop])  # causal 4 ms RMS, 1 ms hop
flux = np.maximum(0, np.diff(e, prepend=e[0]))
e_raw = np.sqrt(np.convolve(x ** 2, np.ones(hop * 4) / (hop * 4), mode='full')[:len(x)][::hop])  # full-band, for low cues
cues = json.load(open(os.path.join(F.STUDIO, 'assets', 'cues.json')))
SLOW = {'head', 'swell', 'card', 'downbeat'}            # soft attacks: check the level rises after the cue instead
DISCRETE = {'tick', 'rewind', 'downbeat', 'head', 'relu', 'strike', 'name', 'card', 'swell'}

def frame(t, fmt):
    return np.asarray(F.render(t, fmt, S=1), dtype=np.int16)

rows, worst_a, fails = [], 0, []
for c in cues:
    t = c['t']; ms = int(round(t * 1000))
    if c['kind'] in SLOW:
        pre, post = e_raw[max(0, ms - 30):ms].mean(), e_raw[ms + 20:ms + 160].mean()
        a_ok, a_txt = post > pre * 1.05, f'rise {20 * math.log10(post / max(pre, 1e-9)):+.1f} dB'
    else:
        # search half the gap to the nearest other cue (max 40 ms), take the earliest strong rise
        gap = min([abs(o['t'] - t) * 1000 for o in cues if o is not c] + [80])
        half = max(2, min(40, int(gap / 2)))
        lo, hi = max(0, ms - half), ms + half
        f = flux[lo:hi]
        on = (lo + int(np.argmax(f >= 0.5 * f.max()))) / 1000
        err = (on - t) * 1000
        dense = gap < 60   # neighbours closer than 60 ms: report, but timing is guaranteed by construction
        a_ok = abs(err) <= 10 or dense
        a_txt = f'{err:+.0f} ms' + (' (dense, not graded)' if dense else '')
        if not dense: worst_a = max(worst_a, abs(err))
    p_txt = '-'
    if c['kind'] in DISCRETE:
        i = math.ceil(t * fps - 1e-9)
        lag = (i / fps - t) * 1000
        ch = {}
        for fmt in ('16x9', '9x16'):
            d = np.abs(frame(i / fps, fmt) - frame((i - 1) / fps, fmt)).mean()
            ch[fmt] = d
        p_ok = all(v > 0.01 for v in ch.values())
        p_txt = f"frame {i} (+{lag:.0f} ms) Δ16x9 {ch['16x9']:.2f} Δ9x16 {ch['9x16']:.2f}"
    else:
        p_ok = True
    if not (a_ok and p_ok): fails.append(c)
    rows.append(f"| {t:6.3f} | {c['kind']} | {'ok' if a_ok else 'FAIL'} {a_txt} | {'ok' if p_ok else 'FAIL'} {p_txt} |")

rep = [f'# Sync report: {os.path.basename(wav)} at {fps} fps', '',
       f'{len(cues)} cues; worst audio onset error {worst_a:.0f} ms (tolerance 10 ms); '
       f'{len(fails)} failures. Picture events quantise to the next frame (max {1000 / fps:.0f} ms late).', '',
       '| t (s) | cue | audio | picture |', '|---|---|---|---|'] + rows
open(os.path.join(F.STUDIO, 'reviews', 'sync-report.md'), 'w').write('\n'.join(rep) + '\n')
# muxed file: cross-correlate its decoded audio with the WAV to catch encoder/mux offsets
if len(sys.argv) > 3:
    import subprocess
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[3], '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    y = np.frombuffer(raw, '<i2') / 32768
    a, b = x[:sr * 6], y[:sr * 6]
    n = 1 << (len(a) + len(b)).bit_length()
    xc = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
    lag = int(np.argmax(np.concatenate([xc[-sr // 10:], xc[:sr // 10]]))) - sr // 10
    line = f'Muxed {os.path.basename(sys.argv[3])}: audio offset vs WAV = {lag / sr * 1000:+.1f} ms (tolerance 5 ms).'
    rep.insert(3, line); print(line)
    if abs(lag / sr) > 0.005: fails.append({'kind': 'mux-offset'})
    open(os.path.join(F.STUDIO, 'reviews', 'sync-report.md'), 'w').write('\n'.join(rep) + '\n')
print(rep[2]); sys.exit(1 if fails else 0)
