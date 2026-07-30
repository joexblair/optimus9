"""build_rpred_mode — the bespoke r-pred mode as a stateful signal (Joe 0725). SAVED.

Pipeline (grounded in lr_cascade qualify-vs-trigger + arm_s5Mage):
  1. MAGE LATCH   : s4M breaches OOB (slip 3 -> >=82 HI / <=18 LO) -> latch, dir from side (HI->short, LO->long).
  2. WEAKNESS ARM : while latched, wait for the HTFs to TURN -- an HTF on the fade side (d*gap<0) whose |gap| is now
                    shrinking vs M bars ago. ANY-TF or ALL-TF (toggle). This is the current rule (stretch) one step
                    later (turning). Latch RESETS here -> ARMED.
  3. TRIGGER      : s4r still OOB (>=85/<=15) -> x-cross-pred (predict s4x x s4r near bound, earlier entry);
                    s4r back to IB          -> plain s4x x s4m cross (favourable dir). Fire -> emit -> IDLE.
  r-divergence (s4M OOB & s4r IB) is implicit in the trigger split, left OPTIONAL. Runs ALONGSIDE the flat rule.
Scored swing-to-pivot @2%. Usage: build_rpred_mode.py <YYYY-MM-DD start> <ndays>   (default whole tape)
"""
import sys
import numpy as np
import linelab as LL
import siglab

SLIP = 3; M = 60; TIMEOUT = 360; HTFS = [10, 12, 15, 20, 30]
HI, LO = 85.0, 15.0

LL.register('s4r', kind='k',  tf=4, k_len=7, rsi=5, stc=11)
LL.register('s4M', kind='bb', tf=4, length=37, mult=0.83)
cache, ets, epx, names = LL.warm(rebuild=False)
lab = siglab.Lab(cache, ets, epx)
ts = cache.ts; n = len(ts)
s4M = LL.line(cache, 's4M'); s4r = LL.line(cache, 's4r'); s4x = LL.line(cache, 's4x'); s4m = LL.line(cache, 's4m')
GAP = {tf: LL.line(cache, 's%dx' % tf) - LL.line(cache, 's%dm' % tf) for tf in HTFS}
# trigger events (precomputed boolean arrays, indexed by dir)
diff = s4x - s4m
cross = {-1: (diff < 0) & (np.roll(diff, 1) >= 0),   # s4x crosses UNDER s4m -> short
         +1: (diff > 0) & (np.roll(diff, 1) <= 0)}    # s4x crosses OVER  s4m -> long
lp, sp = LL.xcross_pred(cache, base='s4', bnd_offset=4)
xcp = {-1: sp, +1: lp}
s4r_oob = (s4r >= HI) | (s4r <= LO)

if len(sys.argv) > 1 and sys.argv[1][:1].isdigit():
    from datetime import datetime, timezone, timedelta
    d0 = datetime.strptime(sys.argv[1], '%Y-%m-%d').replace(tzinfo=timezone.utc)
    nd = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    S = int(d0.timestamp()*1000); E = int((d0+timedelta(days=nd)).timestamp()*1000)
else:
    S, E = int(ets[0]), int(ets[-1])
i0 = int(np.searchsorted(ts, S)); i1 = int(np.searchsorted(ts, E))


def weak(i, d, mode):
    p = max(0, i - M)
    hits = [tf for tf in HTFS if (d * GAP[tf][i] < 0) and (abs(GAP[tf][i]) < abs(GAP[tf][p]))]
    return (len(hits) > 0) if mode == 'any' else (len(hits) == len(HTFS))


def run(mode):
    state = 'IDLE'; d = 0; ai = 0; out = []
    poh = pol = False                                            # prior-bar OOB-hi / OOB-lo (for the breach EDGE)
    for i in range(i0, i1):
        oh = s4M[i] >= HI - SLIP; ol = s4M[i] <= LO + SLIP
        if state == 'IDLE':                                      # latch ONCE on the breach edge (IB->OOB)
            if oh and not poh: state, d = 'LATCHED', -1
            elif ol and not pol: state, d = 'LATCHED', +1
        elif state == 'LATCHED':
            if weak(i, d, mode): state, ai = 'ARMED', i          # latch resets on weakness -> ARMED
        elif state == 'ARMED':
            trig = xcp[d][i] if s4r_oob[i] else cross[d][i]
            if trig: out.append((int(ts[i]), d)); state = 'IDLE'  # fire once; needs a fresh breach to re-arm
            elif i - ai > TIMEOUT: state = 'IDLE'
        poh, pol = oh, ol
    return out


def base_rate():
    """trade EVERY s4x x s4m cross in its direction -- the no-edge benchmark the mode must beat."""
    return [(int(ts[i]), d) for d in (-1, 1) for i in np.flatnonzero(cross[d][i0:i1]) + i0]


def score(sigs):
    rows = {-1: [], 1: []}
    for tms, d in sigs:
        _, mfe, mae = lab.score(tms, d); rows[d].append(mfe - mae)
    return rows


def report(name, sigs):
    r = score(sigs); allnet = r[-1] + r[1]
    if not allnet:
        print('  %-22s | (0 signals)' % name); return
    med = float(np.median(allnet)); win = 100 * np.mean([x > 0 for x in allnet])
    sm = ('%+.2f(%d)' % (float(np.median(r[-1])), len(r[-1]))) if r[-1] else 'nan(0)'
    lm = ('%+.2f(%d)' % (float(np.median(r[1])), len(r[1]))) if r[1] else 'nan(0)'
    print('  %-22s | n=%3d | net %+.2f | win %2.0f%% | SHORT %s LONG %s' % (name, len(allnet), med, win, sm, lm))


import time as _t
print('=== r-pred MODE vs flat rule | %s..%s | swing 2%% ===' % (
    _t.strftime('%m-%d', _t.gmtime(S/1000)), _t.strftime('%m-%d', _t.gmtime(E/1000))))
report('rpred-mode ANY-weak', run('any'))
report('rpred-mode ALL-weak', run('all'))
flat = [(m['tms'], d) for d in (-1, 1) for m in siglab.markers(cache, lab, 's5', S, E, [10], d) if m['strn'][10] >= 16]
report('flat rule (s10>=16)', flat)
report('BASE (every s4 cross)', base_rate())
