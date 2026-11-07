"""fdm2-momo at the first bar of every cad walk on the tape. HIS NAME, HIS WIRING, HIS GO.

HIS 1106 RULINGS, verbatim:
  the latch's scope   *"per cad walk is my answer to 3"*
  what ends it        *"the revtrade.  I'm basing this on our 085x example"* - so the latch overrules
                      truncations inside ITS OWN cad walk, the cad walk ends, and the next rev-trade
                      closes the leg. That resolves the circularity: a latch that blocked every
                      rev-trade would have nothing left to end it.
  the run             *"agreed - your clear for takeoff"*

WHAT IT MEASURES, over the whole 94.5-day tape, one continuous chain through v4_fdm2.legs:
  1  every director truncation, and whether it had a CAD WALK at all - some fire on the ws1 seam+15s
     bar itself, with no walk and so no room for an early latch
  2  the three signals at the cad walk's FIRST bar, and the medians over that population
  3  the vote there, and whether fdm2-momo would fire
  4  the carrier outcome from the truncation bar, so a fire can be scored against what followed
  5  HIS ADDED TEST: what the leg's own exit was, and how far the truncation sat from the leg's end

WHAT IT CANNOT MEASURE. Where an OVERRULED leg would end instead needs the latch wired into
v4_fdm2.walk and the chain re-run. That is a change to the live machine, so it is proposed and not
applied here.
"""
import io
import os
import re
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
XE = {t: np.asarray(ln.line('ws%dx' % t), float) for t in CARRIERS}
ME = {t: np.asarray(ln.line('ws%dm' % t), float) for t in CARRIERS}
XC = {t: np.asarray(CP.series(XE[t], t * 60), float) for t in CARRIERS}
MM = {t: np.asarray(CP.series(ME[t], t * 60), float) for t in CARRIERS}
RP = {}
for read in ('closed-prev', 'emerging'):
    kk = LN['CPR'] if read == 'closed-prev' else LN['EMR']
    mm = MM if read == 'closed-prev' else ME
    gg = LN['CPM'] if read == 'closed-prev' else LN['MGE']
    for t in CARRIERS:
        RP[(read, t)] = predict_breach(np.asarray(kk[t], float), mm[t], np.asarray(gg[t], float))
PIN = {(t, sd): JIG.at_extreme_mask(LN['EMR'][t], sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL)
       for t in CARRIERS for sd in (+1, -1)}

CACHE = '/home/joe/.claude/jobs/7c82535c/tmp/latch_cache.json'
t0 = time.time()
SIGS = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'], CPM=LN['CPM'])
g = SIGS[0]
LG = F2.legs(LN, (SG.fire_bar(g), SG.target_side(SG.direction(int(g['side']))), 'fdm re-entry'),
             B, resig=SIGS)
sys.stderr.write('chain: %d legs, %.0f s\n' % (len(LG), time.time() - t0))
sys.stderr.flush()

WALK = re.compile(r'min walk from (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d), truncated at')
SEAM = re.compile(r'seam\+\d+s bar (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)')
EV = []
for L in LG:
    for r in L['rows']:
        w = str(r.get('why', ''))
        if str(r['stage']) != 'REV-TRADE' or not w.startswith('the director - '):
            continue
        m = WALK.search(w)
        s = SEAM.search(w)
        EV.append(dict(trunc=int(r['bar']), side=int(L['side']), leg=L,
                       walk0=ln.K(m.group(1)) if m else (ln.K(s.group(1)) if s else None),
                       has_walk=bool(m), why=w))

#   THE CHAIN IS 36 MINUTES. Its harvest is cached so the next question costs seconds, not a re-run.
import json
json.dump([dict(trunc=e['trunc'], side=e['side'], walk0=e['walk0'], has_walk=e['has_walk'],
                leg_open=int(e['leg']['opn']), leg_exit=int(e['leg']['exit']),
                rel=float(e['leg']['rel']), mae=float(e['leg']['mae']),
                mfe=float(e['leg']['mfe']), stopped=bool(e['leg']['stopped']),
                ctype=str(e['leg']['ctype']), why=e['why']) for e in EV],
          open(CACHE, 'w'))
sys.stderr.write('cached %d events to %s\n' % (len(EV), CACHE))

print('| the population | value |')
print('|---|---|')
print('| legs on the tape | %d |' % len(LG))
print('| director truncations | %d |' % len(EV))
print('| of those, WITH a cad walk | %d |' % sum(1 for e in EV if e['has_walk']))
print('| of those, firing on the seam bar with NO walk | %d |' % sum(1 for e in EV if not e['has_walk']))
print('| the chain | %.0f s |' % (time.time() - t0))
print()


def sig(bar, sd, read):
    mg = LN['CPM'] if read == 'closed-prev' else LN['MGE']
    xs = XC if read == 'closed-prev' else XE
    nr = nx = npn = 0
    for t in CARRIERS:
        if int(RP[(read, t)][bar]) == sd:
            nr += 1
        if (float(np.asarray(mg[t], float)[bar]) - float(np.asarray(xs[t], float)[bar])) * sd > 0:
            nx += 1
        if PIN[(t, sd)][bar]:
            npn += 1
    return nr, nx, npn


W1 = SP.legs('ws1Mage')
ROWS = []
for e in EV:
    if e['walk0'] is None:
        continue
    w1 = [z for o, z, _ in W1 if o <= e['trunc'] <= z]
    upto = min(w1) if w1 else int(e['leg']['exit'])
    for read in ('closed-prev', 'emerging'):
        nr, nx, npn = sig(e['walk0'], e['side'], read)
        src = LN['CPR'] if read == 'closed-prev' else LN['EMR']
        n = 0
        for t in CARRIERS:
            a = np.asarray(src[t], float)
            if (a[e['trunc']] >= 85.0) if e['side'] > 0 else (a[e['trunc']] <= 15.0):
                continue
            seg = a[e['trunc']:upto + 1]
            if seg.size and np.isfinite(seg).any():
                if (np.nanmax(seg) >= 85.0) if e['side'] > 0 else (np.nanmin(seg) <= 15.0):
                    n += 1
        ROWS.append(dict(read=read, trunc=e['trunc'], walk0=e['walk0'], side=e['side'],
                         has_walk=e['has_walk'], rpred=nr, mx=nx, pin=npn, n_w1=n,
                         lead=(e['trunc'] - e['walk0']) * 5, rel=float(e['leg']['rel']),
                         mae=float(e['leg']['mae']), mfe=float(e['leg']['mfe']),
                         leg_exit=int(e['leg']['exit']), leg_open=int(e['leg']['opn'])))

print('## the medians at the cad walk\'s FIRST bar - fdm2-momo\'s own population')
print()
print('| the read | the signal | median | p25 | p75 | bars |')
print('|---|---|---|---|---|---|')
MED = {}
for read in ('closed-prev', 'emerging'):
    sub = [r for r in ROWS if r['read'] == read]
    for ft in ('rpred', 'mx', 'pin'):
        v = np.array([r[ft] for r in sub], float)
        MED[(read, ft)] = float(np.median(v))
        print('| %s | %s | %.1f | %.0f | %.0f | %d |'
              % (read, ft, MED[(read, ft)], np.percentile(v, 25), np.percentile(v, 75), len(v)))
print()

print('## fdm2-momo\'s vote at the cad walk\'s first bar, scored against what followed the truncation')
print()
print('SPLIT BY WHETHER THE TRUNCATION HAD A CAD WALK AT ALL. The ones that fire on the ws1')
print('seam+15s bar have no walk, so fdm2-momo reads the truncation bar itself and its lead is 0 s.')
print('His wiring only covers the WITH-WALK rows.')
print()
print('| had a cad walk | the read | votes | cases | fdm2-momo fires | carriers reaching 15/85 after the truncation, median | zero-carrier | p90 | median lead, s |')
print('|---|---|---|---|---|---|---|---|---|')
for hw in (True, False):
  for read in ('closed-prev', 'emerging'):
    sub = [r for r in ROWS if r['read'] == read and r['has_walk'] == hw]
    for nv in (0, 1, 2, 3):
        m = [r for r in sub
             if ((1 if r['rpred'] >= MED[(read, 'rpred')] else 0)
                 + (1 if r['mx'] < MED[(read, 'mx')] else 0)
                 + (1 if r['pin'] >= MED[(read, 'pin')] else 0)) == nv]
        if not m:
            print('| %s | %s | %d | 0 | - | - | - | - | - |' % ('yes' if hw else 'no', read, nv)); continue
        c = np.array([r['n_w1'] for r in m], float)
        ld = np.array([r['lead'] for r in m], float)
        print('| %s | %s | %d | %d | %s | %.1f | %.1f%% | %.0f | %.0f |'
              % ('yes' if hw else 'no', read, nv, len(m), 'yes' if nv >= 3 else 'no',
                 float(np.median(c)), 100.0 * (c == 0).mean(),
                 float(np.percentile(c, 90)), float(np.median(ld))))
print()

print('## HIS ADDED TEST - how far the truncation sat from the leg\'s own end')
print()
print('| had a cad walk | the read | votes | cases | the truncation IS the leg\'s exit | median seconds to the leg exit | the leg\'s realised %, median | its MAE %, median | its MFE %, median |')
print('|---|---|---|---|---|---|---|---|---|')
for hw in (True, False):
  for read in ('closed-prev', 'emerging'):
    sub = [r for r in ROWS if r['read'] == read and r['has_walk'] == hw]
    for nv in (0, 1, 2, 3):
        m = [r for r in sub
             if ((1 if r['rpred'] >= MED[(read, 'rpred')] else 0)
                 + (1 if r['mx'] < MED[(read, 'mx')] else 0)
                 + (1 if r['pin'] >= MED[(read, 'pin')] else 0)) == nv]
        if not m:
            print('| %s | %s | %d | 0 | - | - | - | - | - |' % ('yes' if hw else 'no', read, nv)); continue
        gap = np.array([(r['leg_exit'] - r['trunc']) * 5 for r in m], float)
        rel = np.array([r['rel'] for r in m], float)
        mae = np.array([r['mae'] for r in m], float)
        mfe = np.array([r['mfe'] for r in m], float)
        print('| %s | %s | %d | %d | %.1f%% | %.0f | %+.3f | %.3f | %+.3f |'
              % ('yes' if hw else 'no', read, nv, len(m), 100.0 * (gap <= 5).mean(),
                 float(np.median(gap)), float(np.median(rel)), float(np.median(mae)),
                 float(np.median(mfe))))
