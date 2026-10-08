"""WHAT ACTUALLY CANCELS THE DELEGATION BEFORE THE WINDOW EXPIRES. 1008.

Joe 1008: *"if ws12r `stalled` or `x-crossed` before the 192 bars expire, we accept that as a
reversal and there is no delegation. confirm"*.

I CANNOT CONFIRM IT AS WRITTEN, so this measures what the code does instead of asserting it.

THREE THINGS CANCEL A DELEGATION TODAY, read off `run_leg`:
  1  ws12r LEAVES oob      `oob_a = None` resets the timer, so the window restarts from the next
                           crossing. This is an oob EXIT, not a stall or an x-cross.
  2  the MAE stop          outranks everything; the leg closes and nothing delegates.
  3  THE RIDER stalls or x-crosses, where the rider is whatever TF holds the baton. If the rider
                           happens to BE ws12 then Joe's sentence is satisfied by accident. If the
                           rider is ws5, ws12's own stall is never tested.

SO WHAT IS NOT BUILT is Joe's sentence itself: ws12r's OWN stall, and ws12x crossing ws12r, as
cancels in their own right, independent of which TF holds the baton.

MEASURED HERE, over 95 days at oob_gate_bars 192 and at the banked 72, on the banked build:
  how many ws12r oob runs reach the window
  how many of those had ws12r ITSELF stall inside the window
  how many had ws12x cross ws12r inside the window (the branch-1 condition, counter-dr)
  which TF held the baton when the handover fired - i.e. how often ws12 was the rider anyway
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts); TF = C.TRIG_TF
R12, X12, ST = C.R[TF], C.X[TF], C.ST
HI, LO = SC.HI, SC.LO
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
print('# tape %d bars; ws%dr trigger, oob %.0f/%.0f, stop %.2f'
      % (N, TF, LO, HI, C.MAE_STOP), flush=True)

# ---- every ws12r oob run, and what ws12 itself did inside each candidate window
RUNS = []
k = 1
while k < N:
    for side in (+1, -1):
        now = (float(R12[k]) >= HI) if side > 0 else (float(R12[k]) <= LO)
        was = (float(R12[k - 1]) >= HI) if side > 0 else (float(R12[k - 1]) <= LO)
        if now and not was:
            j = k
            while j < N and (((float(R12[j]) >= HI) if side > 0 else (float(R12[j]) <= LO))): j += 1
            RUNS.append((k, side, j - k))
            break
    k += 1
print('# %d ws12r oob runs' % len(RUNS), flush=True)

u = lambda z: float(X12[z]) < float(R12[z])
rows = []
for gb in (72, 192):
    reach = [(k, s, r) for k, s, r in RUNS if r > gb + 1]
    st_in = xc_in = both = 0
    for k, s, r in reach:
        w = range(k, min(N - 1, k + gb + 1) + 1)
        sm = any(bool(ST[(TF, s)][q]) for q in w)
        xm = any(((u(q) and not u(q - 1)) if s > 0 else ((not u(q)) and u(q - 1)))
                 for q in w if q >= 1)
        st_in += sm; xc_in += xm; both += (sm or xm)
    rows.append(('%d bars / %g min' % (gb, gb * 5 / 60.0), str(len(RUNS)), str(len(reach)),
                 str(st_in), '%.1f%%' % (100.0 * st_in / len(reach)) if reach else '—',
                 str(xc_in), '%.1f%%' % (100.0 * xc_in / len(reach)) if reach else '—',
                 str(both), '%.1f%%' % (100.0 * both / len(reach)) if reach else '—'))
print('\n# ws12r\'s OWN stall and x-cross INSIDE the window, on runs that reach it')
box(('the window', 'all ws12r oob runs', 'runs reaching the window',
     'ws12r stalled inside', 'as %', 'ws12x crossed ws12r inside', 'as %',
     'either happened', 'as %'), rows)

# ---- what the CHAIN does: which TF is the rider at the handover, and what cancels in practice
for gb in (72, 192):
    C.GATE_BARS = gb
    legs = []; k, d, g = 1, +1, 0
    riders = collections.Counter(); whyn = collections.Counter(); nhand = 0
    pre = collections.Counter()
    while True:
        g += 1
        if g > 20000: break
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        if hand is not None:
            nhand += 1
            rid = None
            for b_, lbl in tr:
                if b_ > hand: break
                if lbl.startswith('KICKSTART'): rid = int(lbl.split('rider ws')[1].split(' ')[0])
                elif lbl.startswith('baton -> ws'): rid = int(lbl.split('baton -> ws')[1].split(' ')[0])
            riders[rid if rid is not None else 0] += 1
        else:
            # no handover: did a ws12r oob run even reach the window in this leg?
            got = any(lbl.startswith('CEILING') for _, lbl in tr)
            pre['ws12r went oob, no handover' if got else 'ws12r never went oob'] += 1
        whyn[why] += 1
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        legs.append(1)
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
            if cf is None: break
            k, d = cf, sd; continue
        if xk >= N - 1: break
        k = xk; d = -d
    print('\n# THE CHAIN AT oob_gate_bars %d — %d legs, %d handovers' % (gb, len(legs), nhand))
    box(('the TF holding the baton when the handover fired', 'handovers', 'as % of handovers'),
        [(('ws%d' % t) if t else 'no rider yet — the walk had not kickstarted', str(c),
          '%.1f%%' % (100.0 * c / nhand)) for t, c in sorted(riders.items())])
    box(('legs with NO handover', 'legs'), [(k_, str(v)) for k_, v in pre.most_common()])
    box(('the leg exit', 'legs'), [(w, str(c)) for w, c in whyn.most_common()])
