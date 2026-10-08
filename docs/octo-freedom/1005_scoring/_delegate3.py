"""WHERE ws60r's SIGNAL LIVES — the reading bar DECOUPLED from the handover bar. 1008.

Joe 1008: *"you'll recall that swing detect is strictly a backtest tool"*, correcting my
*"reading ws60r at crossing+20 min to decide a handover at crossing+6 min is information past the
decision"*.

WHICH HALF OF THAT CLAIM STANDS, stated precisely:

  STANDS   a GATE that reads ws60r at crossing + 20 min cannot decide a handover that fires at
           crossing + 6 min. That is information after the decision bar and it is not buildable.
  DOES NOT the MEASUREMENT does not inherit that constraint. swing_detect is the SCORER, never an
           input to the mech, so the scoring bar is allowed to sit in the future - that is what a
           scoring bar is. I tied the reading bar to the handover bar for the whole study and that
           cost the one thing the study was for: WHERE ws60r's signal actually lives.

SO THIS RUN DECOUPLES THEM. The handover stays at the banked oob_gate_bars 72 (6 min). ws60r's
trajectory is read at crossing + 0 / 72 / 108 / 144 / 192 / 240 bars. Every row says whether it is
BUILDABLE as a gate - reading bar at or before the handover bar - or MEASUREMENT ONLY.

TWO SCORING BARS, because Joe's sentence and the gate's job are not the same question:
  next pivot after the READING bar    Joe's words: *"the next pivot will be matching ws60r's
                                      trajectory"*. Asks whether ws60r predicts the next turn.
  next pivot after the HANDOVER bar   asks whether that reading predicts the move the chain is
                                      about to take by delegating. This is the gate-relevant one.

POPULATION: every ws12r oob crossing whose run exceeds 73 bars, i.e. every one that DOES delegate
at the banked width. 'oob still alive at the reading bar' is a column, not a filter.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute.swing_detect import find_pivots
import _chain10 as C

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
R12 = C.R[C.TRIG_TF]
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
HI, LO = SC.HI, SC.LO
HAND = 72                      # the banked oob_gate_bars; the handover bar is crossing + 73
OFFS = [(0, 'at the crossing'), (72, '6 min — THE HANDOVER BAR'), (108, '9 min'),
        (144, '12 min'), (192, '16 min'), (240, '20 min')]
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
print('# tape %d bars; handover fixed at crossing + %d bars' % (N, HAND + 1), flush=True)

TRAJ60 = np.zeros(N, np.int8)
_cur = _prev = np.nan
for k in range(N):
    v = float(R60[k])
    if np.isfinite(v):
        if not np.isfinite(_cur): _cur = v
        elif v != _cur: _prev, _cur = _cur, v
    TRAJ60[k] = 0 if not np.isfinite(_prev) else (1 if _cur > _prev else (-1 if _cur < _prev else 0))

EV = []
k = 1
while k < N:
    for side in (+1, -1):
        now = (float(R12[k]) >= HI) if side > 0 else (float(R12[k]) <= LO)
        was = (float(R12[k - 1]) >= HI) if side > 0 else (float(R12[k - 1]) <= LO)
        if now and not was:
            j = k
            while j < N and (((float(R12[j]) >= HI) if side > 0 else (float(R12[j]) <= LO))): j += 1
            if j - k > HAND + 1: EV.append(dict(k=k, side=side, run=j - k))
            break
    k += 1
print('# %d crossings reach the %d-bar handover' % (len(EV), HAND), flush=True)

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
_days = sorted({DAYOF(k) for k in range(0, N, 2000)})
BLK = {'all': set(_days), 'fit': set(_days[:47]), 'hold': set(_days[47:])}

def run(pct, off, scorebar, blk):
    ni, nk = PIV[pct]
    o = [0, 0, 0.0]; c = [0, 0, 0.0]; z = 0; alive = 0
    for e in EV:
        rb = e['k'] + off + (1 if off else 0)
        sb = rb if scorebar == 'read' else e['k'] + HAND + 1
        if rb >= N or sb >= N: continue
        if blk != 'all' and DAYOF(sb) not in BLK[blk]: continue
        if e['run'] > off: alive += 1
        tj = int(TRAJ60[rb])
        if tj == 0: z += 1; continue
        if int(ni[sb]) < 0: continue
        hit = 1 if (tj > 0 and nk[sb] > 0) or (tj < 0 and nk[sb] < 0) else 0
        p0 = float(PX[sb]); p1 = float(PX[int(ni[sb])])
        mv = (p1 - p0) / p0 * 100.0 * tj
        t = o if tj == e['side'] else c
        t[0] += 1; t[1] += hit; t[2] += mv
    return o, c, z, alive

for scorebar, slab in (('hand', 'SCORED AT THE HANDOVER BAR — the gate-relevant question'),
                       ('read', "SCORED AT THE READING BAR — Joe's sentence")):
    for pct in (1.0, 0.9):
        print('\n# %s, swing_detect %.1f%%' % (slab, pct))
        rows = []
        for off, lab in OFFS:
            for blk in ('all', 'fit', 'hold'):
                o, c, z, alive = run(pct, off, scorebar, blk)
                rows.append((lab, 'BUILDABLE' if off <= HAND else 'measurement only', blk,
                             str(o[0] + c[0]), str(o[0]),
                             '%.1f%%' % (100.0 * o[1] / o[0]) if o[0] else '—',
                             str(c[0]),
                             '%.1f%%' % (100.0 * c[1] / c[0]) if c[0] else '—',
                             '%+.1f' % ((100.0 * o[1] / o[0]) - (100.0 * c[1] / c[0]))
                             if o[0] and c[0] else '—',
                             '%+.4f' % (o[2] / o[0]) if o[0] else '—',
                             '%+.4f' % (c[2] / c[0]) if c[0] else '—',
                             str(alive), str(z)))
        box(('where ws60r is read', 'can it gate?', 'block', 'events', 'gate OPEN',
             'OPEN hit rate', 'gate closed', 'closed hit rate', 'spread, pts',
             'OPEN mean pxs move', 'closed mean pxs move', 'ws12r still oob there', 'traj 0'), rows)
print('\n- the handover is FIXED at crossing + %d bars on every row. Only the bar ws60r is read on' % (HAND + 1))
print('  moves, so this isolates WHERE the signal lives from WHEN the chain delegates.')
print('- "can it gate?" is BUILDABLE only when the reading bar is at or before the handover bar.')
print('  The measurement-only rows are evidence about ws60r, never a mech.')
print('- swing_detect is the SCORER on every row and is never an input. Joe 1008: "swing detect is')
print('  strictly a backtest tool".')
