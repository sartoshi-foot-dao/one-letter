#!/usr/bin/env python3
"""ONE LETTER: frame = render(t, fmt). Pure, seekable: every frame is a function of t and the trace only.

No hidden clock, no integration across frames, no randomness at all (jitter is not used).
Every number drawn comes from assets/trace.json or assets/featured.json.

Two compositions share one timeline: 16x9 and 9x16 (a separate layout, not a crop).
    python3 motion-studio/src/film.py still 16x9 19.6 out.png     # one frame
    python3 motion-studio/src/film.py stills 9x16                 # reviews/stills-9x16/*.png + contact sheets
    python3 motion-studio/src/film.py frames 16x9 OUTDIR 30 8     # every frame, parallel, any order
"""
import json, math, os, sys
from types import SimpleNamespace
from itertools import accumulate
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(HERE)
TRACE = json.load(open(os.path.join(STUDIO, 'assets', 'trace.json')))
FEAT = json.load(open(os.path.join(STUDIO, 'assets', 'featured.json')))

# ------------------------------------------------------------------ style tokens (style-guide.md)
def hx(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
GROUND, GROUND2 = hx('#0b0c10'), hx('#12141a')
INK, INK2, INK3, RULE = hx('#e6e3dc'), hx('#a9a8a2'), hx('#85868b'), hx('#262932')
GOLD, CYAN, SEA, OXBLOOD = hx('#e2b45c'), hx('#5ae6f0'), hx('#2a6a8c'), hx('#8e3340')

def mix(a, b, k):  # k=0 -> a, k=1 -> b
    k = max(0.0, min(1.0, k)); return tuple(round(x + (y - x) * k) for x, y in zip(a, b))
def dim(c, a):  # a = opacity over ground
    return mix(GROUND, c, a)

FONTS = {
    'serif': ['/System/Library/Fonts/Supplemental/Iowan Old Style.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'],
    'mono': ['/System/Library/Fonts/Menlo.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'],
    'sans': ['/System/Library/Fonts/HelveticaNeue.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'],
}
_fc = {}
def font(kind, px):
    key = (kind, px)
    if key not in _fc:
        path = next(p for p in FONTS[kind] if os.path.exists(p))
        _fc[key] = ImageFont.truetype(path, px)
    return _fc[key]

# ------------------------------------------------------------------ time helpers (closed form only)
def ramp(t, a, b):
    return 0.0 if t <= a else 1.0 if t >= b else (t - a) / (b - a)
def ease_out(x): return 1 - (1 - x) ** 3
def spring(t, t0, dur=0.18, zeta=0.72):
    """Damped spring step response at time t (0 -> 1, slight settle). Closed form, so seekable."""
    if t <= t0: return 0.0
    w = 2 * math.pi / dur; s = t - t0; wd = w * math.sqrt(1 - zeta ** 2)
    return 1 - math.exp(-zeta * w * s) * (math.cos(wd * s) + zeta * w / wd * math.sin(wd * s))

# ------------------------------------------------------------------ data
V = TRACE['meta']['vocab']; BOS = TRACE['meta']['BOS']
SAMPLE = TRACE['samples'][FEAT['sample']]
NAME, K = FEAT['name'], FEAT['pos']
STEP = SAMPLE['positions'][K]
PREFIX_STEPS = SAMPLE['positions'][:K + 1]             # inputs BOS, k, a
CHOSEN, ARGMAX = STEP['sampled'], max(range(27), key=STEP['probs'].__getitem__)
_all = [abs(v) for s in TRACE['samples'] for p in s['positions']
        for key in ('x_in', 'resid_attn', 'mlp_post', 'x_out') for v in p[key]]
CLAMP = sorted(_all)[int(0.98 * (len(_all) - 1))]       # one clamp for the whole film
def vcol(x, a=1.0):
    k = max(-1.0, min(1.0, x / CLAMP))
    # sqrt keeps small values visible; one clamp and one curve for the whole film
    return dim(mix(GROUND2, OXBLOOD if k > 0 else SEA, abs(k) ** 0.5), a)
def is_fav(p): return p['sampled'] == max(range(27), key=p['probs'].__getitem__)
OFF, TOTAL = FEAT['run_off_argmax']

# ------------------------------------------------------------------ timeline (shotlist.md)
SHOTS = [0.0, 3.0, 5.5, 9.0, 13.5, 16.0, 20.5, 24.0]
FILM_DUR = SHOTS[-1]
# Reading holds (added after the first full watch: "goes a little fast"). Film time stops at each
# rest point for the given seconds while real time runs on; picture and sound both go through this map.
HOLDS = [(2.95, 0.8, 'name complete'), (5.3, 0.8, '27 options'), (8.6, 1.0, 'columns built'),
         (9.4, 0.4, 'head 1'), (10.5, 0.4, 'head 2'), (11.6, 0.4, 'head 3'), (12.7, 0.6, 'head 4, full matrix'),
         (15.6, 1.0, 'mlp and output'), (17.3, 1.0, 'bars grown'), (20.2, 1.5, 'die landed'),
         (21.9, 1.0, 'card: 67 of 118'), (23.9, 0.8, 'poster')]
DUR = FILM_DUR + sum(d for _, d, _ in HOLDS)          # real duration

def real_t(tf):
    """First real moment that shows film time tf."""
    return tf + sum(d for h, d, _ in HOLDS if h < tf)

def film_t(tr):
    """Film time shown at real time tr (constant during a hold)."""
    acc = 0.0
    for h, d, _ in HOLDS:
        if tr < h + acc: return tr - acc
        if tr < h + acc + d: return h
        acc += d
    return min(tr - acc, FILM_DUR)
LETTER_T = [0.85 + i * 0.45 for i in range(len(NAME))]  # first choice held, then even ticks over the name
HOOK_T0 = 0.08  # the first 27-way choice starts growing here
HEAD_T = [9.0 + 1.1 * h for h in range(4)]
ROLL_T0, ROLL_T1, LAND_T = 18.0, 19.4, 19.6

# ------------------------------------------------------------------ painter with camera + supersampling
class Painter:
    def __init__(self, W, H, S=2, cam=None):
        self.W, self.H, self.S = W, H, S
        self.cam = cam or (W / 2, H / 2, 1.0)
        self.img = Image.new('RGB', (W * S, H * S), GROUND)
        self.d = ImageDraw.Draw(self.img)
    def P(self, x, y):
        cx, cy, z = self.cam
        return (((x - cx) * z + self.W / 2) * self.S, ((y - cy) * z + self.H / 2) * self.S)
    def k(self, v): return v * self.cam[2] * self.S
    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        a, b = self.P(x0, y0), self.P(x1, y1)
        self.d.rectangle([a, b], fill=fill, outline=outline, width=max(1, round(self.k(width))))
    def line(self, pts, fill, width=2):
        self.d.line([self.P(*p) for p in pts], fill=fill, width=max(1, round(self.k(width))), joint='curve')
    def ring(self, x, y, r, fill=None, outline=None, width=2):
        (a, b), rr = self.P(x, y), self.k(r)
        self.d.ellipse([a - rr, b - rr, a + rr, b + rr], fill=fill, outline=outline, width=max(1, round(self.k(width))))
    def text(self, x, y, s, kind, px, fill, anchor='ms'):
        self.d.text(self.P(x, y), s, font=font(kind, max(1, round(self.k(px)))), fill=fill, anchor=anchor)
    def done(self):
        return self.img.resize((self.W, self.H), Image.LANCZOS) if self.S > 1 else self.img

def glyph(p, tok, x, y, px, col):
    """A token: a letter in serif, or BOS as a small ring (it has no letter)."""
    if tok == BOS: p.ring(x, y - px * 0.32, px * 0.16, outline=col, width=max(2, px / 28))
    else: p.text(x, y, V[tok], 'serif', px, col)

# ------------------------------------------------------------------ layouts: one per format, same timeline
def _l169():
    L = SimpleNamespace(name='16x9', W=1920, H=1080, vertical=False)
    L.TX, L.SLOT_X, L.ROW_Y, L.ROW_PX = [300, 480, 660], 840, 230, 120
    L.COL_Y0 = 340
    L.CX0, L.CX1, L.CAND_Y, L.CAND_PX = 190, 1730, 990, 44
    L.cand = lambda c: (L.CX0 + c * (L.CX1 - L.CX0) / 26, L.CAND_Y)
    L.NAME1_X = [960 + (i - (len(NAME) - 1) / 2) * 170 for i in range(len(NAME))]
    L.NAME1_Y, L.NAME1_PX, L.HOOK_CX = 500, 200, 960
    L.lab = dict(opts=(180, 920), vec=(270, 840), attn=(1120, 320), mlp=(1140, 318), probs=(1240, 336))
    L.CAP_Y = 836
    L.MX = (1120, 400)
    L.RESID_X, L.GRID, L.OUT_X = 1000, (1140, 340), 1700
    L.STRIP = (190, 1730, 360, 408)
    L.focus, L.zoom = (960, 700), 0.08
    return L

def _l916():
    L = SimpleNamespace(name='9x16', W=1080, H=1920, vertical=True)
    L.TX, L.SLOT_X, L.ROW_Y, L.ROW_PX = [250, 430, 610], 790, 420, 120
    L.COL_Y0 = 560
    L.CAND_PX = 52
    L.cand = lambda c: (140 + (c % 9) * 100, 1560 + (c // 9) * 90)     # 27 options as 3 rows of 9
    L.NAME1_X = [540 + (i - (len(NAME) - 1) / 2) * 170 for i in range(len(NAME))]
    L.NAME1_Y, L.NAME1_PX, L.HOOK_CX = 1000, 200, 540
    L.lab = dict(opts=(130, 1470), vec=(190, 1090), attn=(330, 1300), mlp=(300, 540), probs=(115, 610))
    L.CAP_Y = 1056
    L.MX = (330, 1400)
    L.RESID_X, L.GRID, L.OUT_X = 160, (300, 560), 860
    L.STRIP = (115, 965, 640, 700)
    L.focus, L.zoom = (540, 1150), 0.06
    return L

LAYOUTS = {'16x9': _l169(), '9x16': _l916()}
L = LAYOUTS['16x9']
CELL_W, CELL_H, CELL_G = 56, 26, 2

def label(p, t, a, b, s, key):
    """Labels cut on and off (never fade), placed next to what they label."""
    if a <= t < b: p.text(*L.lab[key], s, 'sans', 48, INK2, 'ls')

def column(p, x, vals, t0, t, a=1.0, cell_w=CELL_W):
    """16 cells filling top-down, 12 ms stagger, no overshoot."""
    for j, v in enumerate(vals):
        if t < t0 + 0.012 * j: break
        y = L.COL_Y0 + j * (CELL_H + CELL_G)
        p.rect(x - cell_w / 2, y, x + cell_w / 2, y + CELL_H, fill=vcol(v, a))

PROBS = STEP['probs']
def bar_rows():
    """9:16 tray: top 7 by probability, plus the chosen letter if it is not among them, plus 'other'."""
    order = sorted(range(27), key=lambda c: -PROBS[c])
    rows = order[:7]
    if CHOSEN not in rows: rows = order[:6] + [CHOSEN]
    rows = sorted(rows, key=lambda c: -PROBS[c])
    other = sum(PROBS[c] for c in range(27) if c not in rows)
    return rows, other
ROWS9, OTHER9 = bar_rows()
def row9_y(r): return 880 + r * 108

# ------------------------------------------------------------------ the frame function
def render(tr, fmt='16x9', S=2):
    """tr is real time. Everything is drawn at film time t = film_t(tr), except the camera,
    which runs on real time so it keeps gliding through the holds instead of stopping."""
    global L
    L = LAYOUTS[fmt]
    W, H, TX = L.W, L.H, L.TX
    t = film_t(tr)
    if 16.0 <= t < 20.5:  # the film's one camera move: slow push into the probability tray
        z = 1.0 + L.zoom * ease_out(ramp(tr, real_t(16.0), real_t(20.5)))
        fx, fy = L.focus
        cam = (fx - (fx - W / 2) / z, fy - (fy - H / 2) / z, z)  # the focus point stays put on screen
    else:
        cam = None
    p = Painter(W, H, S, cam)

    # ---- shot 1: the name spells itself; each letter is preceded by its 27-way choice
    if t < 4.4:
        for i, step in enumerate(SAMPLE['positions'][:len(NAME)]):
            ti = LETTER_T[i]
            if i == 0 and HOOK_T0 <= t < ti + 0.12:  # the hook: the first choice, full size, real probs
                g = ease_out(ramp(t, HOOK_T0, HOOK_T0 + 0.35))
                lit = t >= ti - 0.12
                for c, q in enumerate(step['probs']):
                    bx = L.HOOK_CX - 27 * 22 / 2 + c * 22
                    hh = (4 + 700 * q) * g
                    on = c == step['sampled'] and lit
                    p.rect(bx, L.NAME1_Y + 90 - hh, bx + 16, L.NAME1_Y + 90, fill=GOLD if on else dim(INK2, 0.8))
            elif ti - 0.15 <= t < ti + 0.1 and t < 3.0:  # later letters: the strip flickers, 150 ms
                for c, q in enumerate(step['probs']):
                    bx = L.NAME1_X[i] - 148 + c * 11
                    hh = 6 + 120 * q
                    p.rect(bx, L.NAME1_Y + 80 - hh, bx + 8, L.NAME1_Y + 80,
                           fill=dim(INK if c == step['sampled'] else INK3, 0.55))
            if t < ti: continue
            s = spring(t, ti)
            x, y, px = L.NAME1_X[i], L.NAME1_Y - 60 * (1 - s), L.NAME1_PX
            col = GOLD if (t < ti + 0.35 and t < 3.0) else INK
            if i >= K and t >= 3.0:  # shot 2: rewind, later letters fall away (reverse order)
                fall = ramp(t, 3.0 + 0.18 * (len(NAME) - 1 - i), 3.35 + 0.18 * (len(NAME) - 1 - i))
                if fall >= 1: continue
                y += 220 * fall ** 2; col = dim(INK, 1 - fall)
            elif i < K and t >= 3.0:  # the prefix rises into the top row: same objects, new role
                m = ease_out(ramp(t, 3.6, 4.4))
                x = L.NAME1_X[i] + (TX[i + 1] - L.NAME1_X[i]) * m
                y = L.NAME1_Y + (L.ROW_Y - L.NAME1_Y) * m
                px = L.NAME1_PX + (L.ROW_PX - L.NAME1_PX) * m
            p.text(x, y, NAME[i], 'serif', round(px), col)

    # ---- persistent prefix row (from 4.4): start ring, k, a, and the slot being decided
    if 4.4 <= t < 20.5:
        for i, step in enumerate(PREFIX_STEPS):
            glyph(p, step['input'], TX[i], L.ROW_Y, L.ROW_PX, INK3 if step['input'] == BOS else INK)
        p.text(TX[0], L.ROW_Y + 44, 'start', 'mono', 36, INK3)
    if 4.2 <= t < 20.5:
        if t < LAND_T:
            p.rect(L.SLOT_X - 40, L.ROW_Y + 14, L.SLOT_X + 40, L.ROW_Y + 20, fill=GOLD)
        else:  # the chosen letter flies from where it sits in the tray into the slot
            s = spring(t, LAND_T, dur=0.32)
            sx, sy, spx = (150, row9_y(ROWS9.index(CHOSEN)), 64) if L.vertical else (*L.cand(CHOSEN), L.CAND_PX)
            x = sx + (L.SLOT_X - sx) * s
            y = sy + (L.ROW_Y - sy) * s
            p.text(x, y, V[CHOSEN], 'serif', round(spx + (L.ROW_PX - spx) * min(1, s)), GOLD)

    # ---- candidates (shot 2 on): 27 options. In 9:16 the tray rows carry the letters in shot 6.
    if 4.4 <= t < 9.0 or (16.0 <= t < 20.5 and not L.vertical):
        for c in range(27):
            if t < 4.4 + 0.01 * c: break
            col = dim(INK3, 0.9)
            if t >= LAND_T and c == CHOSEN: col = dim(INK3, 0.35)
            glyph(p, c, *L.cand(c), L.CAND_PX, col)
        if t < 5.5: label(p, t, 4.6, 5.5, '27 options · which one?', 'opts')

    # ---- shot 3: each input becomes 16 numbers (token + position embedding, rmsnorm)
    if 5.5 <= t < 13.5:
        a = 1.0 if t < 9.0 else 0.55
        for i, step in enumerate(PREFIX_STEPS):
            column(p, TX[i], step['x_in'], 5.7 + 0.5 * i, t, a)
        label(p, t, 5.8, 9.0, 'each letter becomes 16 numbers', 'vec')

    # ---- shot 4: attention, one head at a time; weights accumulate in a matrix
    if 9.0 <= t < 13.5:
        label(p, t, 9.1, 13.5, 'attention · 4 heads', 'attn')
        h_now = max(h for h in range(4) if t >= HEAD_T[h]) if t >= HEAD_T[0] else -1
        y_b = L.COL_Y0 + 16 * (CELL_H + CELL_G) + 8
        if h_now >= 0:
            grow = ease_out(ramp(t, HEAD_T[h_now], HEAD_T[h_now] + 0.3))
            for j, w in enumerate(STEP['attn'][h_now]):
                wd = (2 + 26 * w) * grow
                if j == K:  # attention to itself: a small loop under its own column
                    pts = [(TX[K] + 44 * math.sin(2 * math.pi * u), y_b + 44 - 44 * math.cos(2 * math.pi * u))
                           for u in [i / 40 for i in range(41)]]
                else:
                    depth = 70 + 70 * abs(K - j)
                    pts = [(TX[K] + (TX[j] - TX[K]) * (i / 40), y_b + depth * math.sin(math.pi * i / 40)) for i in range(41)]
                if wd >= 0.5: p.line(pts, dim(CYAN, (0.35 + 0.65 * w) * (0.4 + 0.6 * grow)), wd)
        mx0, my0 = L.MX; cw, ch = 160, 78
        for i, step in enumerate(PREFIX_STEPS):
            glyph(p, step['input'], mx0 + cw * (i + 0.5), my0 - 24, 48, INK3 if step['input'] == BOS else INK2)
        for h in range(4):
            p.text(mx0 - 24, my0 + ch * h + ch / 2 + 10, f'h{h + 1}', 'mono', 36, INK3, 'rs')
            for j in range(K + 1):
                x0, y0 = mx0 + cw * j + 3, my0 + ch * h + 3
                p.rect(x0, y0, x0 + cw - 6, y0 + ch - 6, outline=RULE, width=2)
                if t >= HEAD_T[h] + 0.3:
                    w = STEP['attn'][h][j]
                    p.rect(x0, y0, x0 + cw - 6, y0 + ch - 6, fill=mix(GROUND2, CYAN, 0.12 + 0.6 * w))
                    p.text(x0 + (cw - 6) / 2, y0 + ch / 2 + 8, f'{w:.2f}', 'mono', 40, INK if w < 0.6 else GROUND)

    # ---- shot 5: the mixed vector goes through 64 units; only some fire
    if 13.5 <= t < 16.0:
        label(p, t, 13.6, 16.0, 'then 64 units · relu', 'mlp')
        column(p, L.RESID_X, STEP['resid_attn'], 13.55, t)
        if L.vertical: p.text(110, L.CAP_Y, 'after attention', 'mono', 36, INK3, 'ls')
        else: p.text(L.RESID_X, L.CAP_Y, 'after attention', 'mono', 36, INK3)
        (gx0, gy0), gc = L.GRID, 50
        for u, (pre, post) in enumerate(zip(STEP['mlp_pre'], STEP['mlp_post'])):
            r, c = divmod(u, 8)
            x0, y0 = gx0 + c * gc, gy0 + r * gc
            if t < 13.9 + 0.008 * u: continue
            p.rect(x0, y0, x0 + gc - 4, y0 + gc - 4, outline=RULE, width=2)
            if post > 0 and t >= 14.5:
                p.rect(x0, y0, x0 + gc - 4, y0 + gc - 4, fill=vcol(post))
            elif t < 14.5:  # before relu: everything shows, negatives included
                p.rect(x0 + 2, y0 + 2, x0 + gc - 6, y0 + gc - 6, fill=vcol(pre, 0.8))
        if t >= 14.6:
            p.text(gx0, gy0 + 8 * gc + 44, f"{FEAT['mlp_active']} / 64 active", 'mono', 44, INK, 'ls')
        if t >= 15.2:
            column(p, L.OUT_X, STEP['x_out'], 15.2, t)
            p.text(L.OUT_X, L.CAP_Y, 'output', 'mono', 36, INK3)

    # ---- shot 6: the probabilities, the weighted die, and where it really landed
    if 16.0 <= t < 20.5:
        label(p, t, 16.1, 17.4, '27 probabilities', 'probs')
        label(p, t, 17.4, 20.5, 'a weighted die', 'probs')
        full = 0.40
        if not L.vertical:
            BAR_BASE = 945; BAR_H = BAR_BASE - 500
            top = sorted(range(27), key=lambda c: -PROBS[c])[:5]
            for c, q in enumerate(PROBS):
                g = ease_out(ramp(t, 16.2 + 0.015 * c, 16.6 + 0.015 * c))  # linear-out, 400 ms
                hh = BAR_H * q / full * g
                x = L.cand(c)[0]
                chosen = (c == CHOSEN and t >= LAND_T)
                p.rect(x - 20, BAR_BASE - hh, x + 20, BAR_BASE, fill=GOLD if chosen else dim(INK2, 0.75))
                if g >= 1 and c in top:  # the chosen value is carried by its own label
                    p.text(x, BAR_BASE - hh - 14, f'{q:.2f}', 'mono', 40, INK2)
            if t >= LAND_T:
                xa, xc = L.cand(ARGMAX)[0], L.cand(CHOSEN)[0]
                ya = BAR_BASE - BAR_H * PROBS[ARGMAX] / full
                p.text(xa, ya - 70, 'most likely', 'sans', 44, INK2)
                yc = BAR_BASE - BAR_H * PROBS[CHOSEN] / full - 50
                ly = 700
                p.line([(xc, yc + 30), (xc, ly - 14), (xc - 16, ly - 14)], GOLD, 2)
                p.text(xc - 24, ly, f'chosen · {PROBS[CHOSEN]:.2f}', 'sans', 44, GOLD, 'rs')
        else:  # 9:16: horizontal bars, top letters + chosen + 'other' (all 27 do not fit legibly)
            BX, BL = 210, 440
            for r, c in enumerate(ROWS9 + ['other']):
                y = row9_y(r)
                q = OTHER9 if c == 'other' else PROBS[c]
                g = ease_out(ramp(t, 16.2 + 0.04 * r, 16.6 + 0.04 * r))
                chosen = (c == CHOSEN and t >= LAND_T)
                if c == 'other': p.text(150, y, 'other', 'sans', 34, INK3, 'ms')
                elif c == CHOSEN and t >= LAND_T: p.text(150, y, V[c], 'serif', 64, dim(INK3, 0.35))
                else: glyph(p, c, 150, y, 64, INK2)
                ln = BL * min(q, full) / full * g
                p.rect(BX, y - 40, BX + max(ln, 2), y - 6, fill=GOLD if chosen else dim(INK2, 0.75 if c != 'other' else 0.4))
                if g >= 1:
                    tcol = GOLD if chosen else INK2
                    p.text(BX + ln + 18, y - 8, f'{q:.2f}', 'mono', 40, tcol, 'ls')
                    tag = 'most likely' if (t >= LAND_T and c == ARGMAX) else 'chosen' if (t >= LAND_T and c == CHOSEN) else ''
                    if tag: p.text(BX + ln + 18 + font('mono', 40).getlength('0.00') + 22, y - 8, tag, 'sans', 40, tcol, 'ls')
        # the die: cumulative strip, segment width = probability; marker stops at the recorded u
        if t >= 17.4:
            sx0, sx1, sy0, sy1 = L.STRIP
            cw = [0.0] + list(accumulate(PROBS)); tot = cw[-1]
            for c in range(27):
                a, b = sx0 + (sx1 - sx0) * cw[c] / tot, sx0 + (sx1 - sx0) * cw[c + 1] / tot
                chosen = (c == CHOSEN and t >= LAND_T)
                p.rect(a, sy0, b, sy1, fill=GOLD if chosen else GROUND2, outline=RULE, width=2)
                if b - a > 34 and c != BOS:
                    p.text((a + b) / 2, sy1 - 14, V[c], 'serif', 38, GROUND if chosen else INK2)
            if t >= ROLL_T0:
                u = STEP['u'] * STEP['u_total'] / tot
                m = ease_out(ramp(t, ROLL_T0, ROLL_T1))
                mx = sx0 + (sx1 - sx0) * u * m
                p.rect(mx - 2, sy0 - 18, mx + 2, sy1 + 18, fill=INK)

    # ---- shot 7: every name from the run; dots mark letters that were not the favourite
    if t >= 20.5:
        for si, s in enumerate(TRACE['samples']):
            if L.vertical: x0, y0 = 170 + (si // 10) * 440, 560 + (si % 10) * 92
            else: x0, y0 = 250 + (si // 5) * 380, 250 + (si % 5) * 112
            if t < 20.7 + 0.04 * si: continue
            col = GOLD if si == FEAT['sample'] else INK
            xx = x0
            for p_ in s['positions']:
                if p_['sampled'] == BOS: break
                ch = V[p_['sampled']]
                wch = font('serif', 64).getlength(ch)
                p.text(xx, y0, ch, 'serif', 64, col, 'ls')
                if not is_fav(p_):
                    p.ring(xx + wch / 2, y0 + 22, 5, fill=INK3)
                xx += wch
        params = f"{TRACE['meta']['num_params']:,} numbers"
        if not L.vertical:
            if 21.2 <= t < 22.6:
                p.ring(250, 898, 8, fill=INK3)
                p.text(274, 916, f'{OFF} of {TOTAL} letters were not its favourite', 'sans', 56, INK, 'ls')
            elif t >= 22.6:
                p.text(250, 916, f'{params} · pure Python', 'sans', 56, INK, 'ls')
                p.ring(1290, 902, 8, fill=INK3)
                p.text(1314, 914, 'not its favourite', 'sans', 40, INK3, 'ls')
        else:
            if 21.2 <= t < 22.6:
                p.ring(170, 1542, 8, fill=INK3)
                p.text(194, 1560, f'{OFF} of {TOTAL} letters', 'sans', 56, INK, 'ls')
                p.text(170, 1640, 'were not its favourite', 'sans', 56, INK, 'ls')
            elif t >= 22.6:
                p.text(170, 1560, params, 'sans', 56, INK, 'ls')
                p.text(170, 1640, 'pure Python', 'sans', 56, INK, 'ls')
                p.ring(170, 1720, 8, fill=INK3)
                p.text(194, 1734, 'not its favourite', 'sans', 40, INK3, 'ls')
    return p.done()

# ------------------------------------------------------------------ stills + contact sheets
STILLS = [('1-hook', 0.6), ('1b-name', 2.6), ('2-problem', 5.3), ('3-vectors', 8.6), ('4-attention', 13.2),
          ('5-mlp', 15.8), ('6-proof', 20.3), ('7-close-poster', 23.9)]
STRIP = [18.6, 19.4, 19.65, 19.8, 20.0]  # film times; fastest transition: the die lands, the letter flies
POSTER_T = 23.9  # film time

def contact(frames, cols, path, fmt, tw=None):
    W, H = LAYOUTS[fmt].W, LAYOUTS[fmt].H
    tw = tw or (640 if W > H else 300)
    th = tw * H // W; pad = 36
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (tw + 12) + 12, rows * (th + pad + 12) + 12), hx('#000000'))
    d = ImageDraw.Draw(sheet)
    for i, (lab, im) in enumerate(frames):
        r, c = divmod(i, cols)
        x, y = 12 + c * (tw + 12), 12 + r * (th + pad + 12)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + pad))
        d.text((x, y + 6), lab, font=font('mono', 22), fill=INK2)
    sheet.save(path)

def _frame_job(job):
    i, t, out, fmt = job
    render(t, fmt).save(os.path.join(out, f'{i:05d}.png'), compress_level=1)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'stills'
    R = os.path.join(STUDIO, 'reviews')
    if cmd == 'still':      # still FMT T OUT
        render(float(sys.argv[3]), sys.argv[2]).save(sys.argv[4])
    elif cmd == 'frames':   # frames FMT OUTDIR FPS WORKERS: every frame independently, any order
        from multiprocessing import Pool
        fmt, out, fps, nw = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
        os.makedirs(out, exist_ok=True)
        jobs = [(i, i / fps, out, fmt) for i in range(round(DUR * fps))]
        with Pool(nw) as pool:
            for _ in pool.imap_unordered(_frame_job, jobs, chunksize=4): pass
        print('frames', fmt, len(jobs))
    elif cmd == 'sheet':    # sheet FMT FRAMEDIR FPS: contact sheets + poster from the frames that get encoded
        fmt, d, fps = sys.argv[2], sys.argv[3], int(sys.argv[4])
        cols = 4 if fmt == '16x9' else 8
        fr = lambda tf: Image.open(os.path.join(d, f'{round(real_t(tf) * fps):05d}.png'))
        contact([(f'{n} {real_t(t):.1f}s', fr(t)) for n, t in STILLS], cols, os.path.join(R, f'contact-final-{fmt}-beats.png'), fmt)
        contact([(f't={real_t(t):.2f}s', fr(t)) for t in STRIP], 5, os.path.join(R, f'contact-final-{fmt}-die-strip.png'), fmt,
                tw=480 if fmt == '16x9' else 260)
        fr(POSTER_T).convert('RGB').save(os.path.join(STUDIO, 'out', f'one-letter-{fmt}-poster.jpg'), quality=92)
    elif cmd == 'stills':   # stills FMT: quick local check (Mac fonts)
        fmt = sys.argv[2] if len(sys.argv) > 2 else '16x9'
        out = os.path.join(R, f'stills-{fmt}'); os.makedirs(out, exist_ok=True)
        frames = []
        for name, t in STILLS:
            tr = real_t(t); im = render(tr, fmt); im.save(os.path.join(out, f'{name}-t{tr:05.2f}.png')); frames.append((f'{name} {tr:.1f}s', im))
        contact(frames, 4 if fmt == '16x9' else 8, os.path.join(R, f'contact-{fmt}-beats.png'), fmt)
        print('wrote', out)
