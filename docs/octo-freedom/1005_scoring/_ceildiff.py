"""THE MESS OF CAPPING THE CEILING AT THE BANKED oob_gate_bars 72. 1008.

Joe 1008: *"we're not talking about 192 yet - that's a future task that hasn't been banked yet. I'm
interest in the potential mess of not following the banked and in-use `>ws12r oob` path"*.

ONE QUESTION ONLY: at the banked oob_gate_bars 72, what does `ceil_hi` 23 -> 12 actually disturb?

WHY THE NET DELTA UNDERSTATES IT. The chain is sequential - leg N+1 opens at leg N's exit bar - so a
single changed exit RE-PHASES every leg after it. "+2 legs" is not two extra trades; it is the whole
chain downstream of the first divergence being a different set of legs. This measures that directly:
the first bar where the two arms disagree, how many legs are bar-identical, and how far the drift
runs.

Both arms are run in ONE process so the lines, stalls and knobs are provably the same objects.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts); FEE = 0.11
assert C.GATE_BARS == 72, 'this run is the banked width only, got %d' % C.GATE_BARS
assert C.DGATE == 'off', 'the delegation gate must be off here'
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
print('# tape %d bars; oob_gate_bars %d, stop %.2f, x-cross target ws{h+1}%s'
      % (N, C.GATE_BARS, C.MAE_STOP, C.XT_ROLE), flush=True)

def chain(ceil):
    C.CEIL_HI = ceil
    out = []; k, d, g = 1, +1, 0
    while True:
        g += 1
        if g > 20000: break
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        seg = PX[k:xk + 1]; ok = np.isfinite(seg) & (seg > 0)
        rel = np.where(ok, (seg - p0) / p0 * 100.0 * sgn, 0.0)
        out.append(dict(open=k, exit=xk, d=d, why=why, hand=hand, ceil_bar=cb,
                        mae=(C.MAE_STOP if why == 'mae breach' else -float(rel.min())),
                        mfe=(0.0 if why == 'mae breach' else float(rel.max())),
                        real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn))
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
            if cf is None: break
            k, d = cf, sd; continue
        if xk >= N - 1: break
        k = xk; d = -d
    return out

A = chain(23); print('# ceil 23 -> %d legs' % len(A), flush=True)
B = chain(12); print('# ceil 12 -> %d legs' % len(B), flush=True)

# ---- where they part
same = 0
for a, b in zip(A, B):
    if a['open'] == b['open'] and a['exit'] == b['exit'] and a['why'] == b['why']: same += 1
    else: break
first = (A[same], B[same]) if same < min(len(A), len(B)) else None
print('\n# WHERE THE TWO CHAINS PART')
box(('the measure', 'ceil_hi 23 — banked', 'ceil_hi 12 — extension off'),
    [('legs', str(len(A)), str(len(B))),
     ('legs bar-identical from the seed', str(same), str(same)),
     ('as % of the shorter chain', '%.1f%%' % (100.0 * same / min(len(A), len(B))),
      '%.1f%%' % (100.0 * same / min(len(A), len(B)))),
     ('the first leg that differs', str(same + 1), str(same + 1)),
     ('its open bar', U(first[0]['open']) if first else '—', U(first[1]['open']) if first else '—'),
     ('its day', DAYOF(first[0]['open']) if first else '—',
      DAYOF(first[1]['open']) if first else '—'),
     ('its exit bar', U(first[0]['exit']) if first else '—', U(first[1]['exit']) if first else '—'),
     ('its exit reason', first[0]['why'] if first else '—', first[1]['why'] if first else '—'),
     ('its realised', '%+.4f' % first[0]['real'] if first else '—',
      '%+.4f' % first[1]['real'] if first else '—')])

# ---- how much of each chain shares an open bar with the other, in any position
oa = {r['open'] for r in A}; ob = {r['open'] for r in B}
shared = oa & ob
print('\n# HOW MUCH OF THE CHAIN SURVIVES, counting shared OPEN BARS in any position')
box(('the measure', 'value'),
    [('ceil 23 legs', str(len(A))), ('ceil 12 legs', str(len(B))),
     ('open bars present in BOTH chains', str(len(shared))),
     ('as % of ceil 23', '%.1f%%' % (100.0 * len(shared) / len(A))),
     ('open bars ONLY in ceil 23', str(len(oa - ob))),
     ('open bars ONLY in ceil 12', str(len(ob - oa)))])

# ---- the legs whose delegation itself changed
ha = {r['open']: (r['hand'] is not None) for r in A}
hb = {r['open']: (r['hand'] is not None) for r in B}
flip = [k for k in shared if ha[k] != hb[k]]
print('\n# THE LEGS WHOSE DELEGATION FLIPPED, among the legs both chains share')
box(('the measure', 'value'),
    [('shared legs', str(len(shared))),
     ('delegated under ceil 23, NOT under ceil 12', str(sum(1 for k in flip if ha[k]))),
     ('delegated under ceil 12, NOT under ceil 23', str(sum(1 for k in flip if hb[k]))),
     ('delegation identical', str(len(shared) - len(flip)))])
if flip:
    ra = {r['open']: r for r in A}; rb = {r['open']: r for r in B}
    print('\n# EVERY FLIPPED LEG, in time order')
    box(('day', 'open', 'side', 'ceil 23 exit', 'ceil 23 why', 'ceil 23 realised',
         'ceil 12 exit', 'ceil 12 why', 'ceil 12 realised', 'realised delta'),
        [(DAYOF(k), U(k), 'LONG' if ra[k]['d'] > 0 else 'SHORT',
          U(ra[k]['exit']), ra[k]['why'], '%+.4f' % ra[k]['real'],
          U(rb[k]['exit']), rb[k]['why'], '%+.4f' % rb[k]['real'],
          '%+.4f' % (rb[k]['real'] - ra[k]['real']))
         for k in sorted(flip)])

# ---- the score, both arms, same scoring rule
days = sorted({DAYOF(r['open']) for r in A} | {DAYOF(r['open']) for r in B})
BL = {'all': set(days), 'fit': set(days[:47]), 'hold': set(days[47:])}
def sc(rr, blk):
    g = n = s = 0; a_ = f_ = 0.0
    for r in rr:
        if DAYOF(r['open']) not in BL[blk]: continue
        g += r['real']; n += 1; s += 1 if r['why'] == 'mae breach' else 0
        a_ += r['mae']; f_ += r['mfe']
    return g - n * FEE, n, s, (f_ / a_ if a_ else 0.0)
print('\n# THE SCORE — same rule on both arms, a stopped leg scores MAE %.2f and MFE 0.0000'
      % C.MAE_STOP)
box(('block', 'ceil 23 NET', 'ceil 12 NET', 'NET delta', 'ceil 23 MFE/MAE', 'ceil 12 MFE/MAE',
     'MFE/MAE delta', 'ceil 23 legs', 'ceil 12 legs', 'ceil 23 stops', 'ceil 12 stops'),
    [(blk, '%+.4f' % x[0], '%+.4f' % y[0], '%+.4f' % (y[0] - x[0]),
      '%.4f' % x[3], '%.4f' % y[3], '%+.4f' % (y[3] - x[3]),
      str(x[1]), str(y[1]), str(x[2]), str(y[2]))
     for blk in ('fit', 'hold', 'all') for x in [sc(A, blk)] for y in [sc(B, blk)]])
