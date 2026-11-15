#!/usr/bin/env python3
"""Record assets/trace.json from an instrumented run of third_party/microgpt.py.

The model source is not copied. It is read, patched at a few exact anchors with
record-only calls (they read .data and never touch `random`), then exec'd. Each
patch must match exactly once, so if microgpt.py changes the recorder fails
instead of drifting.

microgpt.py is Karpathy's gist, downloaded by scripts/fetch_microgpt.sh (not
redistributed here). Run it via scripts/record.sh, or from the repo root:
    python3 src/record_trace.py
"""
import hashlib, json, os, sys
from bisect import bisect as _bisect
from itertools import accumulate as _acc

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'third_party', 'microgpt.py')
OUT = os.path.join(ROOT, 'assets', 'trace.json')

# (anchor, replacement). Each anchor must appear exactly once.
PATCHES = [
    ("    x = [t + p for t, p in zip(tok_emb, pos_emb)] # joint token and position embedding\n"
     "    x = rmsnorm(x) # note: not redundant due to backward pass via the residual connection\n",
     "    x = [t + p for t, p in zip(tok_emb, pos_emb)]\n    x = rmsnorm(x)\n"
     "    _T('tok_emb', tok_emb); _T('pos_emb', pos_emb); _T('x_in', x)\n"),
    ("            attn_weights = softmax(attn_logits)\n",
     "            attn_weights = softmax(attn_logits)\n"
     "            _T('attn', attn_weights, append=True)\n"),
    ("        x = [a + b for a, b in zip(x, x_residual)]\n        # 2) MLP block\n        x_residual = x\n",
     "        x = [a + b for a, b in zip(x, x_residual)]\n        x_residual = x\n"
     "        _T('resid_attn', x)\n"),
    ("        x = [xi.relu() for xi in x]\n",
     "        _T('mlp_pre', x)\n        x = [xi.relu() for xi in x]\n        _T('mlp_post', x)\n"),
    ("    logits = linear(x, state_dict['lm_head'])\n",
     "    _T('x_out', x)\n    logits = linear(x, state_dict['lm_head'])\n    _T('logits', logits)\n"),
    ("        logits = gpt(token_id, pos_id, keys, values)\n        probs = softmax([l / temperature",
     "        _begin(sample_idx, pos_id, token_id)\n"
     "        logits = gpt(token_id, pos_id, keys, values)\n        probs = softmax([l / temperature"),
    ("        token_id = random.choices(range(vocab_size), weights=[p.data for p in probs])[0]\n",
     # Same draw as CPython 3.11 random.choices(k=1): one random() call, bisect on
     # cumulative weights. Restated so the uniform u can be recorded. The 20-name
     # check against the unmodified run proves the RNG stream is unchanged.
     "        _w = [p.data for p in probs]; _cw = list(_acc(_w)); _tot = _cw[-1] + 0.0\n"
     "        _u = random.random()\n"
     "        token_id = range(vocab_size)[_bisect(_cw, _u * _tot, 0, vocab_size - 1)]\n"
     "        _T('probs', probs); CUR[0]['u'] = _u; CUR[0]['u_total'] = _tot; _end(token_id)\n"),
]

REC = {'samples': []}
CUR = [None]  # dict for the position being recorded, or None (training)


def _T(key, vals, append=False):
    if CUR[0] is None:
        return
    row = [v.data for v in vals]
    if append:
        CUR[0].setdefault(key, []).append(row)
    else:
        CUR[0][key] = row


def _begin(sample_idx, pos_id, token_id):
    while len(REC['samples']) <= sample_idx:
        REC['samples'].append({'positions': []})
    CUR[0] = {'pos': pos_id, 'input': token_id}
    REC['samples'][sample_idx]['positions'].append(CUR[0])


def _end(token_id):
    CUR[0]['sampled'] = token_id
    CUR[0] = None


def main():
    src = open(SRC).read()
    patched = src
    for anchor, repl in PATCHES:
        n = patched.count(anchor)
        if n != 1:
            sys.exit(f'patch anchor matched {n} times, expected 1:\n{anchor}')
        patched = patched.replace(anchor, repl)
    g = {'__name__': '__microgpt__', '_T': _T, '_begin': _begin, '_end': _end,
         '_bisect': _bisect, '_acc': _acc, 'CUR': CUR}
    os.chdir(os.path.dirname(SRC))  # microgpt.py reads input.txt from its working directory
    exec(compile(patched, SRC, 'exec'), g)

    uchars, BOS = g['uchars'], g['BOS']
    for s in REC['samples']:
        s['name'] = ''.join(uchars[p['sampled']] for p in s['positions'] if p['sampled'] != BOS)
    REC['meta'] = {
        'source': 'microgpt.py (gist karpathy/8627fe009c40f57531cb18360106ce95, revision 14fb038)',
        'source_sha256': hashlib.sha256(src.encode()).hexdigest(),
        'python': sys.version.split()[0],
        'vocab': uchars + ['<BOS>'],
        'BOS': BOS,
        'num_params': len(g['params']),
        'n_embd': g['n_embd'], 'n_head': g['n_head'], 'n_layer': g['n_layer'],
        'block_size': g['block_size'], 'temperature': g['temperature'],
        'num_steps': g['num_steps'],
        'note': 'probs are the temperature-scaled softmax used for sampling; logits are pre-temperature',
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(REC, f, separators=(',', ':'))
    print('trace names:', ' '.join(s['name'] for s in REC['samples']), file=sys.stderr)


if __name__ == '__main__':
    main()
