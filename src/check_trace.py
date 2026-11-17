#!/usr/bin/env python3
"""Gate 3 check: accept or reject assets/trace.json, then pick the featured name.

1. The 20 names in the trace must equal the names printed by unmodified microgpt.py
   (assets/reference-run.log). On any mismatch, reject and exit nonzero.
2. Featured name (rule v2, brief.md): the first sample of length >= 4 with a
   position >= 2 whose sampled token is not the argmax of probs. (v1 lacked
   pos >= 2 and picked an empty-prefix step.) Fallback: the
   highest-entropy step among samples of length >= 4, flagged as such.
Writes assets/featured.json.
"""
import json, math, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
A = os.path.join(ROOT, 'assets')

trace = json.load(open(os.path.join(A, 'trace.json')))
ref = re.findall(r'^sample\s+\d+: (.*)$', open(os.path.join(A, 'reference-run.log')).read(), re.M)
got = [s['name'] for s in trace['samples']]
if ref != got or len(ref) != 20:
    sys.exit(f'REJECT trace: names differ\n ref={ref}\n got={got}')
print('ACCEPT: 20/20 names match the unmodified run')

vocab = trace['meta']['vocab']
H = lambda p: -sum(x * math.log(x) for x in p if x > 0)
feat = None
for si, s in enumerate(trace['samples']):
    if len(s['name']) < 4:
        continue
    for p in s['positions']:
        am = max(range(len(p['probs'])), key=p['probs'].__getitem__)
        if p['pos'] >= 2 and p['sampled'] != am:
            feat = dict(rule='v2: first non-argmax step with pos >= 2', sample=si, name=s['name'], pos=p['pos'],
                        sampled=vocab[p['sampled']], argmax=vocab[am],
                        p_sampled=p['probs'][p['sampled']], p_argmax=p['probs'][am])
            break
    if feat:
        break
if not feat:
    best = max(((H(p['probs']), si, p) for si, s in enumerate(trace['samples']) if len(s['name']) >= 4
                for p in s['positions'] if p['pos'] >= 2), key=lambda r: r[0])
    _, si, p = best
    feat = dict(rule='fallback: highest entropy (sampled == argmax)', sample=si,
                name=trace['samples'][si]['name'], pos=p['pos'], sampled=vocab[p['sampled']],
                argmax=vocab[p['sampled']], p_sampled=p['probs'][p['sampled']], p_argmax=p['probs'][p['sampled']])

p = trace['samples'][feat['sample']]['positions'][feat['pos']]
feat['prefix'] = feat['name'][:feat['pos']]
feat['entropy_nats'] = H(p['probs'])
feat['mlp_active'] = sum(v > 0 for v in p['mlp_post'])
steps = [q for s in trace['samples'] for q in s['positions']]
feat['run_off_argmax'] = [sum(q['sampled'] != max(range(len(q['probs'])), key=q['probs'].__getitem__) for q in steps), len(steps)]
feat['attn'] = p['attn']
feat['top5'] = sorted(((vocab[i], q) for i, q in enumerate(p['probs'])), key=lambda r: -r[1])[:5]
json.dump(feat, open(os.path.join(A, 'featured.json'), 'w'), indent=2)
print(json.dumps(feat, indent=2))

# 3. Control step for the viewer study's arm B (paper/viewer-study.md), stated before looking:
#    the first other sample of length >= 4 that reaches the SAME prefix at the same position and
#    wrote the argmax there. Same prefix => identical inputs, attention, MLP and probabilities
#    (the model is deterministic given the prefix); only the outcome differs. No match: no arm B.
ctrl = None
for si, s in enumerate(trace['samples']):
    if si == feat['sample'] or len(s['name']) < 4 or not s['name'].startswith(feat['prefix']) or len(s['positions']) <= feat['pos']:
        continue
    q = s['positions'][feat['pos']]
    am = max(range(len(q['probs'])), key=q['probs'].__getitem__)
    if q['sampled'] == am:
        ctrl = dict(feat, rule='arm B: first other sample with the same prefix whose step took the argmax', sample=si,
                    name=s['name'], sampled=vocab[am], p_sampled=q['probs'][am])
        same = all(q[k] == p[k] for k in ('x_in', 'attn', 'resid_attn', 'mlp_post', 'x_out', 'probs'))
        if not same:
            sys.exit('arm B: same prefix but different values; rule assumption broken')
        break
if ctrl:
    json.dump(ctrl, open(os.path.join(A, 'featured-B.json'), 'w'), indent=2)
    print('arm B:', ctrl['name'], 'pos', ctrl['pos'], '->', ctrl['sampled'], round(ctrl['p_sampled'], 4))
else:
    print('arm B: no same-prefix argmax step in this run')
