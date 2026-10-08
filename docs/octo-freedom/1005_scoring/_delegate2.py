"""THE DELEGATION GATE, SWEPT OVER THE GATE WIDTH — definition 1, the pivot likelihood. 1008.

Joe 1008: *"does it improve if we sweep 6/9/12/16/20 minutes? 'improve' carries two definitions:
1) likelihoodd of a correctly gated delegation, and 2) impact on our maemfe baseline"*.

THIS SCRIPT IS DEFINITION 1 ONLY. Definition 2 needs the gate inside `run_leg` and is `_gatearm.py`.

THE CAUSALITY CONSTRAINT, and it decides the whole shape of this sweep. The delegation happens AT
the handover bar. Reading ws60r's trajectory at crossing + 20 min to decide a handover that fires at
crossing + 6 min is LOOKAHEAD - information after the entry bar. So the only causal reading is:

    the trajectory is read AT the handover bar, and the handover bar MOVES WITH oob_gate_bars.

Sweeping 6/9/12/16/20 minutes therefore means sweeping `oob_gate_bars` itself to 72/108/144/192/240
bars at the 5 s grid, and reading ws60r there. That is one sweep serving both of Joe's definitions,
not two.

CONSEQUENCE, reported and not hidden: the event population SHRINKS as the width grows, because
fewer ws12r oob runs last that long. The counts are a column.

THE GATE TESTED HERE is the variant that separated best in `_delegate.py` - ws60r's trajectory
against THE oob SIDE, dr ignored (71.3% / 37.5% against the three-way's 71.0% / 39.3%). Joe's dr
clause cost 56 events and bought nothing. The three-way is still printed beside it.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute.swing_detect import find_pivots
import _chain10 as C

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
R12 = C.R[C.TRIG_TF]
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
HI, LO = SC.HI, SC.LO
WIDTHS = [(6, 72), (9, 108), (12, 144), (16, 192), (20, 240)]
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
print('# tape %d bars; ws%dr trigger, oob %.0f/%.0f' % (N, C.TRIG_TF, LO, HI), flush=True)

TRAJ60 = np.zeros(N, np.int8)
_cur = _prev = np.nan
for k in range(N):
    v = float(R60[k])
    if np.isfinite(v):
        if not np.isfinite(_cur): _cur = v
        elif v != _cur: _prev, _cur = _cur, v
    TRAJ60[k] = 0 if not np.isfinite(_prev) else (1 if _cur > _prev else (-1 if _cur < _prev else 0))

# every ws12r crossing into oob, with the full length of its oob run
EV = []
k = 1
while k < N:
    for side in (+1, -1):
        now = (float(R12[k]) >= HI) if side > 0 else (float(R12[k]) <= LO)
        was = (float(R12[k - 1]) >= HI) if side > 0 else (float(R12[k - 1]) <= LO)
        if now and not was:
            j = k
            while j < N and (((float(R12[j]) >= HI) if side > 0 else (float(R12[j]) <= LO))): j += 1
            EV.append(dict(k=k, side=side, dr=int(DRv[k]), run=j - k))
            break
    k += 1
print('# %d crossings' % len(EV), flush=True)

PIV = {}
for pct in (0.9, 1.0):
    pv = find_pivots(PX, pct)
    ni = np.full(N, -1, np.int64); nk = np.zeros(N, np.int8)
    s_ = 0
    for b_, kd_ in pv:
        if b_ > s_:
            ni[s_:b_] = b_; nk[s_:b_] = 1 if kd_ == 'H' else -1
        s_ = b_
    PIV[pct] = (ni, nk)
    print('# swing_detect %.1f%% -> %d pivots' % (pct, len(pv)), flush=True)

_days = sorted({DAYOF(k) for k in range(0, N, 2000)})
BLK = {'all': set(_days), 'fit': set(_days[:47]), 'hold': set(_days[47:])}

def run(pct, gb, rule, blk):
    ni, nk = PIV[pct]
    o = [0, 0, 0.0]; c = [0, 0, 0.0]; z = 0; adr = 0
    for e in EV:
        if e['run'] <= gb + 1: continue
        b = e['k'] + gb + 1
        if b >= N: continue
        if blk != 'all' and DAYOF(b) not in BLK[blk]: continue
        tj = int(TRAJ60[b])
        if rule == 'joe':
            if e['dr'] == 0: continue
            if e['side'] != e['dr']: adr += 1; continue
            want = e['dr']
        else:
            want = e['side']
        if tj == 0: z += 1; continue
        if int(ni[b]) < 0: continue
        hit = 1 if (tj > 0 and nk[b] > 0) or (tj < 0 and nk[b] < 0) else 0
        p0 = float(PX[b]); p1 = float(PX[int(ni[b])])
        mv = (p1 - p0) / p0 * 100.0 * tj
        t = o if tj == want else c
        t[0] += 1; t[1] += hit; t[2] += mv
    return o, c, z, adr

for rule, rlab in (('side', 'ws60r traj vs THE oob SIDE, dr ignored'),
                   ('joe', "JOE'S THREE-WAY — dr, the oob side and ws60r traj all agree")):
    for pct in (0.9, 1.0):
        print('\n# %s, swing_detect %.1f%%' % (rlab, pct))
        rows = []
        for mins, gb in WIDTHS:
            for blk in ('all', 'fit', 'hold'):
                o, c, z, adr = run(pct, gb, rule, blk)
                rows.append(('%d min / %d bars' % (mins, gb), blk,
                             str(o[0] + c[0]), str(o[0]),
                             '%.1f%%' % (100.0 * o[1] / o[0]) if o[0] else '—',
                             str(c[0]),
                             '%.1f%%' % (100.0 * c[1] / c[0]) if c[0] else '—',
                             '%+.1f' % ((100.0 * o[1] / o[0]) - (100.0 * c[1] / c[0]))
                             if o[0] and c[0] else '—',
                             '%+.4f' % (o[2] / o[0]) if o[0] else '—',
                             '%+.4f' % (c[2] / c[0]) if c[0] else '—',
                             str(z), str(adr) if rule == 'joe' else '—'))
        box(('the gate width', 'block', 'events', 'gate OPEN', 'OPEN hit rate', 'gate closed',
             'closed hit rate', 'spread, pts', 'OPEN mean pxs move', 'closed mean pxs move',
             'traj 0', 'oob side against dr'), rows)
print('\n- the trajectory is read AT the handover bar, which is crossing + the width + 1. Reading it')
print('  later than the bar the handover fires on would be lookahead, so the width and the reading')
print('  bar cannot be swept separately.')
print('- "spread, pts" is the OPEN hit rate minus the closed one. That is the number to compare.')
print('- "traj 0" and "oob side against dr" are the events each rule DROPS at that width.')
