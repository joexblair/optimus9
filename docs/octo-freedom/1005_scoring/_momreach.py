"""HOW FAR ABOVE THE RIDER CAN MOMENTUM BE SEEN? 1009.

Joe 1009: *"the question to ask: how far above the exit line can momentum be seen? maybe we are
limited by lin_hop 2"*, and his correction *"stall is the end of momentum"*.

At each stall, every line above the rider is checked for mom-true, and the GAP in TF numbers from
the rider to each one is recorded. lin_hop 2 can only reach a gap of 1 or 2. Anything beyond that
is momentum the baton cannot take, no matter how strong.

BOUND: masks exist for ws1-ws%d so far, so a gap is only counted where the mask exists. Gaps beyond
that are UNKNOWN, not absent, and are reported as such.
"""
import os, sys, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
from _momtrue import momtrue_mask, CACHE
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
MOMT = {}
for t in C.ALL_TF:
    kw = int(C.BANK[t]['k_window'])
    from _momtrue import _key
    p = os.path.join(CACHE, 'momt_%s.npz' % _key(SC.EM, HOURS, WARMUP, t, kw, 'gated'))
    if not os.path.exists(p): continue
    z = np.load(p)
    if len(z['p']) != N: continue
    MOMT[t] = {+1: z['p'].astype(bool), -1: z['m'].astype(bool)}
HAVE = sorted(MOMT)
print(__doc__ % (HAVE[-1] if HAVE else 0))
print('# momentum masks available for: %s' % ', '.join('ws%d' % t for t in HAVE), flush=True)
_i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])
legs = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    rider = None; aceil = C.BASE_HI
    for j, t in tr:
        if t.startswith('KICKSTART'): rider = int(t.split('rider ws')[1].split(' ')[0])
        elif t.startswith('baton -> ws'): rider = int(t.split('baton -> ws')[1].split(' ')[0])
        elif 'CEILING' in t: aceil = C.CEIL_HI
    legs.append(dict(k=k, xk=xk, d=d, why=why, rider=rider, aceil=aceil))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
for i, L in enumerate(legs):
    L['nb'] = bool(i + 1 < len(legs) and legs[i + 1]['why'] == 'mae breach'
                   and legs[i + 1]['k'] == L['xk'])
fs = [L for L in legs if L['why'] == 'final stalled' and L['rider'] is not None]
print('\n# %d stalls with a known rider, %d hand into a breach\n' % (len(fs), sum(1 for L in fs if L['nb'])),
      flush=True)
for nm, sel in (('EVERY STALL', fs), ('THE ONES THAT HAND INTO A BREACH', [L for L in fs if L['nb']])):
    if not sel: continue
    n = len(sel)
    gap = collections.Counter(); near = collections.Counter(); unk = 0
    for L in sel:
        j, d_, r_, ac = L['xk'], L['d'], L['rider'], L['aceil']
        found = None
        for t in HAVE:
            if t <= r_ or t > ac: continue
            if MOMT[t][d_][j]:
                found = t - r_; break
        top = max([t for t in HAVE if t <= ac] or [0])
        if found is None:
            if top < ac: unk += 1
            gap['none in ws1-ws%d' % top] += 1
        else:
            gap['gap %d' % found] += 1
            near['reachable by lin_hop %d' % C.LIN_HOP if found <= C.LIN_HOP
                 else 'BEYOND lin_hop %d' % C.LIN_HOP] += 1
    print('\n# %s — %d stalls. the NEAREST line above the rider with momentum' % (nm, n))
    box(('the gap in TF numbers', 'stalls', '% of them'),
        [(kk, str(v), '%.1f%%' % (100.0 * v / n)) for kk, v in sorted(gap.items())])
    if near:
        box(('could the baton take it?', 'stalls', '% of them'),
            [(kk, str(v), '%.1f%%' % (100.0 * v / n)) for kk, v in sorted(near.items())])
    if unk:
        print('- %d stalls had no momentum inside the masks built so far, but the ceiling reached' % unk)
        print('  higher than the masks do, so those are UNKNOWN rather than none.')
