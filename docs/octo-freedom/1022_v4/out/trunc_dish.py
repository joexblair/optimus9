"""The dish re-pointed at the bars the gate would actually read.

HIS 1105 GO on my own recommendation: *"re-point the dish first. Choosing between 2 and 3 on
leg-open medians is choosing on the wrong population, and that is how a build learns one bar"*.

THE PROBLEM THIS FIXES. momo_dish.py scores the LEG'S OPEN bar. The gate would sit at the
fdm2-wsxcad-director's truncation test - the clause that ended the 2026-08-07 08:26:10 LONG at
08:57:55 on *"ws5, ws6 away and no ex-20/80 line towards"*. Those are different bar populations, so
a median measured at leg opens may not transfer to a truncation bar.

HOW THE POPULATION IS BUILT. ONE continuous chain over the whole tape through v4_fdm2.legs - the
driver that owns the state - from the first fdm re-entry signal to the tape's end, harvesting every
SEAM and REV-TRADE row the director printed, each paired with ITS OWN leg's target side. No bar is
synthesised and no trade context is invented: the side and the `since` anchor are the leg's own.

WHAT IT PRINTS
  1  the truncation bars found, with the leg each belongs to
  2  the three signals at every one of them, and their medians over that population
  3  those medians BESIDE the leg-open medians from momo_dish, so the shift is visible
  4  the vote at each bar, and what the carriers reached from it - bounded by the leg's own exit
     and by the ws1Mage leg that was open there, never by the day's end

NOTHING IS WIRED AND NO KNOB MOVES. The run reads.
"""
import io
import os
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_signal as SG
    import v4_fdm_reentry as RE
    import v4_sweep_pivots as SP
    import v4_closed_prev as CP
    import ln
    from optimus9.analysis import jig as JIG
    from optimus9.compute.breaching_line import predict_breach
finally:
    sys.stderr = _e

LN = F2.load()
HI = int(LN['HI'])
NB = len(LN['close'])
CARRIERS = list(range(int(K.FDM_STEP1_ABOVE_TF) + 1, HI + 1))
B = NB - 1

#   the x and m lines, both reads, for the fast-versus-slow pair and for r-pred
XE = {t: np.asarray(ln.line('ws%dx' % t), float) for t in CARRIERS}
ME = {t: np.asarray(ln.line('ws%dm' % t), float) for t in CARRIERS}
XC = {t: np.asarray(CP.series(XE[t], t * 60), float) for t in CARRIERS}
MM = {t: np.asarray(CP.series(ME[t], t * 60), float) for t in CARRIERS}
RPRED = {}
for read in ('closed-prev', 'emerging'):
    kk = LN['CPR'] if read == 'closed-prev' else LN['EMR']
    mm = MM if read == 'closed-prev' else ME
    gg = LN['CPM'] if read == 'closed-prev' else LN['MGE']
    for t in CARRIERS:
        RPRED[(read, t)] = predict_breach(np.asarray(kk[t], float), mm[t],
                                          np.asarray(gg[t], float))
PIN = {(t, sd): JIG.at_extreme_mask(LN['EMR'][t], sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL)
       for t in CARRIERS for sd in (+1, -1)}

t0 = time.time()
SIGS = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'], CPM=LN['CPM'])
assert SIGS, 'no fdm re-entry signals on the tape'
g = SIGS[0]
D = SG.direction(int(g['side']))
LG = F2.legs(LN, (SG.fire_bar(g), SG.target_side(D), 'fdm re-entry %s' % ln.U(int(g['bar']))),
             B, resig=SIGS)
sys.stderr.write('the chain: %d legs, %.0f s\n' % (len(LG), time.time() - t0))
sys.stderr.flush()

#   every director truncation bar, paired with its own leg
TR = []
for L in LG:
    for r in L['rows']:
        w = str(r.get('why', ''))
        if str(r['stage']) == 'REV-TRADE' and w.startswith('the director - '):
            TR.append((int(r['bar']), int(L['side']), L, w))

print('| the population | value |')
print('|---|---|')
print('| the chain | ONE continuous run, %s to %s |' % (ln.U(int(LG[0]['opn'])), ln.U(B)))
print('| legs | %d |' % len(LG))
print('| director truncation bars | %d |' % len(TR))
print('| the carrier set | ws%dr to ws%dr |' % (CARRIERS[0], CARRIERS[-1]))
print('| the chain run time | %.0f s |' % (time.time() - t0))
print()

#   the three signals at each truncation bar, both reads
ROWS = []
for bar, sd, L, why in TR:
    for read in ('closed-prev', 'emerging'):
        src = LN['CPR'] if read == 'closed-prev' else LN['EMR']
        mg = LN['CPM'] if read == 'closed-prev' else LN['MGE']
        xs = XC if read == 'closed-prev' else XE
        nr = nx = np_ = 0
        for t in CARRIERS:
            if int(RPRED[(read, t)][bar]) == sd:
                nr += 1
            if (float(np.asarray(mg[t], float)[bar]) - float(np.asarray(xs[t], float)[bar])) * sd > 0:
                nx += 1
            if PIN[(t, sd)][bar]:
                np_ += 1
        ROWS.append(dict(bar=bar, side=sd, read=read, n_rpred=nr, n_mage_above_x=nx,
                         n_pinned=np_, leg_open=int(L['opn']), leg_exit=int(L['exit']),
                         rel=float(L['rel'])))

LEGOPEN = {('closed-prev', 'n_rpred'): 1.0, ('closed-prev', 'n_mage_above_x'): 13.0,
           ('closed-prev', 'n_pinned'): 10.0, ('emerging', 'n_rpred'): 0.0,
           ('emerging', 'n_mage_above_x'): 13.0, ('emerging', 'n_pinned'): 10.0}
print('## the medians at the truncation bars, BESIDE the leg-open medians')
print()
print('| the read | the signal | median at the truncation bars | median at the leg opens, ws1Mage | the shift | p25 | p75 | bars |')
print('|---|---|---|---|---|---|---|---|')
MED = {}
for read in ('closed-prev', 'emerging'):
    sub = [r for r in ROWS if r['read'] == read]
    for ft in ('n_rpred', 'n_mage_above_x', 'n_pinned'):
        v = np.array([r[ft] for r in sub], float)
        m = float(np.median(v)) if len(v) else float('nan')
        MED[(read, ft)] = m
        lo = LEGOPEN[(read, ft)]
        print('| %s | %s | %.1f | %.1f | %+.1f | %.0f | %.0f | %d |'
              % (read, ft, m, lo, m - lo,
                 np.percentile(v, 25) if len(v) else float('nan'),
                 np.percentile(v, 75) if len(v) else float('nan'), len(v)))
print()

#   the vote at each truncation bar, on the truncation population's OWN medians, and the outcome
W1 = SP.legs('ws1Mage')
print('## every truncation bar: the vote on its own medians, and what the carriers reached')
print()
print('| the bar | the leg it ended | side | the read | r-pred | fast-vs-slow | pinned | votes | carriers reaching 15/85 by the ws1Mage leg close | by the leg\'s own exit | the leg realised |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
VOTES = {}
for r in sorted(ROWS, key=lambda r: (r['bar'], r['read'])):
    bar, sd, read = r['bar'], r['side'], r['read']
    v = ((1 if r['n_rpred'] >= MED[(read, 'n_rpred')] else 0)
         + (1 if r['n_mage_above_x'] < MED[(read, 'n_mage_above_x')] else 0)
         + (1 if r['n_pinned'] >= MED[(read, 'n_pinned')] else 0))
    src = LN['CPR'] if read == 'closed-prev' else LN['EMR']
    w1 = [z for o, z, _ in W1 if o <= bar <= z]
    upto = min(w1) if w1 else r['leg_exit']
    n = 0
    for t in CARRIERS:
        a = np.asarray(src[t], float)
        if (a[bar] >= 85.0) if sd > 0 else (a[bar] <= 15.0):
            continue
        seg = a[bar:upto + 1]
        if seg.size and np.isfinite(seg).any():
            if (np.nanmax(seg) >= 85.0) if sd > 0 else (np.nanmin(seg) <= 15.0):
                n += 1
    n2 = 0
    for t in CARRIERS:
        a = np.asarray(src[t], float)
        if (a[bar] >= 85.0) if sd > 0 else (a[bar] <= 15.0):
            continue
        seg = a[bar:r['leg_exit'] + 1]
        if seg.size and np.isfinite(seg).any():
            if (np.nanmax(seg) >= 85.0) if sd > 0 else (np.nanmin(seg) <= 15.0):
                n2 += 1
    VOTES.setdefault((read,), []).append((v, n, n2))
    print('| %s | %s | %s | %s | %d | %d | %d | %d | %d | %d | %+.3f |'
          % (ln.U(bar), ln.U(r['leg_open']), 'HIGH' if sd > 0 else 'LOW', read,
             r['n_rpred'], r['n_mage_above_x'], r['n_pinned'], v, n, n2, r['rel']))
print()

print('## the vote scored at the truncation bars - the gate\'s own population')
print()
print('| the read | votes | bars | carriers reaching 15/85 by the ws1Mage leg close, median | zero-carrier bars | p90 |')
print('|---|---|---|---|---|---|')
for read in ('closed-prev', 'emerging'):
    rows = VOTES.get((read,), [])
    for nv in (0, 1, 2, 3):
        m = [x for x in rows if x[0] == nv]
        if not m:
            print('| %s | %d | 0 | - | - | - |' % (read, nv)); continue
        c = np.array([x[1] for x in m], float)
        print('| %s | %d | %d | %.1f | %.1f%% | %.0f |'
              % (read, nv, len(m), float(np.median(c)), 100.0 * (c == 0).mean(),
                 float(np.percentile(c, 90))))
