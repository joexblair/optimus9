"""His 1114 sideways trigger and its pxs-retest, run over a span. A PROBE, not the mech.

GOAL: match his sideways-true and sideways-false examples, and show what the divergence step adds
on top of the raw trigger. HIS ASK: *"what result do you get if the divergence test is applied?"*

EVERY VALUE IS HIS, and the three that are MINE are named in the printed legend rather than buried:
the read for ws1r's under-50 cross, the read for the r lines fed to the divergence, and the anchor
being the excursion's own ib cross.

usage: sideways_probe.py '<from>' '<to>'
"""
import datetime as dt
import io
import os
import sys

import numpy as np

V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, V4)
os.environ.setdefault('LG_TAPE_END', '2026-10-05')

import ln
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_closed_prev as CP
    import v4_backstop_trades as BT
    from optimus9.analysis import jig as J
    from optimus9.config import get_db_config
    from optimus9 import DatabaseManager
    from optimus9.orchestration.rpl_cache import TAPE_DIR
finally:
    sys.stderr = _e

TRIG_TF = int(os.environ.get('W_FDM3_SIDEWAYS_TRIGGER', 5))      # his fdm3-sideways-trigger
SCAN_S = float(os.environ.get('W_FDM3_SCAN_WINDOW', 12.5)) * 60  # his fdm3-sideways-retest-scan-window
DIFF_PCT = float(os.environ.get('W_FDM3_DIFF_PCT', 0.88))        # his fdm3-sideways-retest-diff-pct
HI, LO, MID = 85.0, 15.0, 50.0
A, Z = ln.K(sys.argv[1]), ln.K(sys.argv[2])

cp = lambda nm, sec: np.asarray(CP.series(np.asarray(ln.line(nm), float), sec), float)
B1 = cp('ws1b', 60)
BT_ = cp('ws%db' % TRIG_TF, TRIG_TF * 60)
RT = cp('ws%dr' % TRIG_TF, TRIG_TF * 60)
R1 = cp('ws1r', 60)
RD = {t: cp('ws%dr' % t, t * 60) for t in (3, 4, 5)}
close = BT.prices()[0]
#   the pxs series sits beside __ts__ in the tape npz the lines were built on
import glob
PXS = None
for p in sorted(glob.glob(os.path.join(TAPE_DIR, '*.npz'))):
    z = np.load(p)
    if '__pxs__' in z.files and len(z['__ts__']) >= ln.N:
        PXS = np.asarray(z['__pxs__'], float)[:ln.N]
        break
assert PXS is not None, 'no tape npz carries __pxs__'

#   THE REAL 5 s OPENS, straight from kline_collection. The cached arrays hold t/h/l/c only, and a
#   bar's open is NOT derivable from them - using the previous close instead would be my number,
#   not the exchange's.
_s = sys.stderr; sys.stderr = io.StringIO()
db = DatabaseManager(**get_db_config()); db.connect()
rows = db.execute('SELECT kc_timestamp t, kc_open o FROM kline_collection '
                  'WHERE kc_timestamp BETWEEN %s AND %s ORDER BY kc_timestamp',
                  (int(ln.ts[max(0, A - 20000)]), int(ln.ts[min(ln.N - 1, Z + 20000)])), fetch=True)
db.disconnect(); sys.stderr = _s
OT = np.asarray([int(r['t']) for r in rows], np.int64)
OV = np.asarray([float(r['o']) for r in rows], float)


def opens_in(bar, half_s):
    """Every 5 s OPEN inside +/-half_s of `bar`, and the ws5 bar opens among them. -> (ts, vals)."""
    lo_ms = int(ln.ts[bar]) - int(half_s * 1000)
    hi_ms = int(ln.ts[bar]) + int(half_s * 1000)
    m = (OT >= lo_ms) & (OT <= hi_ms)
    #   a ws{TRIG_TF} bar OPENS on the epoch lattice, so its open is the 5 s open whose timestamp
    #   floors onto that lattice
    step = TRIG_TF * 60 * 1000
    first = (OT % step) == 0
    return OT[m & first], OV[m & first]


def excursions(a, z):
    out, run = [], None
    for k in range(a, z + 1):
        s = +1 if B1[k] >= HI else (-1 if B1[k] <= LO else 0)
        if s and run is None:
            run = (k, s)
        elif run and s != run[1]:
            out.append((run[0], k - 1, run[1]))
            run = (k, s) if s else None
    if run:
        out.append((run[0], z, run[1]))
    return out


def pivot_of(s0, s1, sd):
    seg = PXS[s0:s1 + 1]
    if not np.isfinite(seg).any():
        return None
    v = np.nanmin(seg) if sd < 0 else np.nanmax(seg)
    idx = np.flatnonzero(np.isclose(seg, v))
    return s0 + int(idx[-1])            # HIS N5: the LAST bar of a flat extreme


def oob(v, sd):
    return (v >= HI) if sd > 0 else (v <= LO)


ALLEX = excursions(max(0, A - 60000), Z)       # back far enough to find a floater
print('| the legend | value |')
print('|---|---|')
print('| the trigger lines | ws%db and ws%dr, closed-prev at %d s. his fdm3-sideways-trigger %d |'
      % (TRIG_TF, TRIG_TF, TRIG_TF * 60, TRIG_TF))
print('| oob | at or past %g / %g |' % (LO, HI))
print('| the pivot | the LAST bar of the most extreme pxs inside the ws1b oob excursion |')
print('| the anchor | the excursion\'s own ws1b oob->ib cross bar. MINE, from his "walk forward '
      'until ws1b is ib" |')
print('| the floater | the last same-side ws1b oob->ib cross before it with a ws1r cross under %g '
      'between. Keep walking back, no bound |' % MID)
print('| ws1r\'s read for that cross | closed-prev at 60 s. MINE - he named no read |')
print('| the scan window | +/-%.1f min, centred. his fdm3-sideways-retest-scan-window |' % (SCAN_S / 60))
print('| the diff | abs(floater open - anchor open) / the EARLIER of the two x 100, <= %g%%. his '
      'fdm3-sideways-retest-diff-pct |' % DIFF_PCT)
print('| the bars fed to the divergence | the two ws%d OHLC "open" extremum bars, HIS 1114 - so '
      'both land on a %d minute multiple. The ws1b cross bars only CENTRE the windows |'
      % (TRIG_TF, TRIG_TF))
print('| the divergence | jig.anchor_floater_given on ws3r, ws4r, ws5r closed-prev against the raw '
      'close at those two bars, dr = the excursion side. The r read is MINE |')
print('| a divergence verdict | abs(state) == 1 and state == the excursion side. +/-2 is a price '
      'match and is IGNORED, his 1114 |')
print()
print('| the ws1b excursion | side | the pxs pivot | ws%db | oob | ws%dr | oob | the RAW verdict '
      '| the anchor cross | the floater cross | ws%db/r oob at the floater | the floater extremum '
      'bar | its open | the anchor extremum bar | its open | the diff %% | within %g%% | ws3r '
      '| ws4r | ws5r | the FINAL verdict |'
      % (TRIG_TF, TRIG_TF, TRIG_TF, DIFF_PCT))
print('|' + '---|' * 21)
for s0, s1, sd in ALLEX:
    if s1 < A:
        continue
    p = pivot_of(s0, s1, sd)
    if p is None:
        continue
    bo, ro = oob(BT_[p], sd), oob(RT[p], sd)
    raw = 'FALSE' if (bo or ro) else 'true'
    row = ['%s .. %s' % (ln.U(s0), ln.U(s1)), 'HIGH' if sd > 0 else 'LOW', ln.U(p),
           '%.2f' % BT_[p], 'OOB' if bo else 'no', '%.2f' % RT[p], 'OOB' if ro else 'no', raw]
    if raw == 'FALSE':
        print('| ' + ' | '.join(row + ['-'] * 12 + ['sideways == FALSE on the raw trigger']) + ' |')
        continue
    ank = s1 + 1
    if ank > ln.N - 1:
        print('| ' + ' | '.join(row + ['past the tape'] + ['-'] * 11 + ['no retest']) + ' |')
        continue
    #   the floater: earlier same-side excursions, latest first, each tested for a ws1r under-50
    #   cross strictly between its ib bar and the anchor
    flo = None
    for q0, q1, qsd in sorted([e for e in ALLEX if e[1] + 1 < ank and e[2] == sd], reverse=True):
        c = q1 + 1
        seg = R1[c:ank + 1]
        ok = np.isfinite(seg)
        crossed = bool(np.any((seg[:-1] >= MID) & (seg[1:] < MID) & ok[:-1] & ok[1:]))
        if crossed:
            flo = c
            break
    if flo is None:
        print('| ' + ' | '.join(row + [ln.U(ank), 'none found'] + ['-'] * 10
                                + ['no retest - no floater']) + ' |')
        continue
    fbo, fro = oob(BT_[flo], sd), oob(RT[flo], sd)
    if not (fbo or fro):
        print('| ' + ' | '.join(row + [ln.U(ank), ln.U(flo), 'neither'] + ['-'] * 9
                                + ['do nothing - his ELSE IF']) + ' |')
        continue
    ft, fv = opens_in(flo, SCAN_S)
    at, av = opens_in(ank, SCAN_S)
    if not len(fv) or not len(av):
        print('| ' + ' | '.join(row + [ln.U(ank), ln.U(flo), 'yes', 'no ws%d open' % TRIG_TF]
                                + ['-'] * 8 + ['no retest']) + ' |')
        continue
    fi = int(np.argmax(fv) if sd > 0 else np.argmin(fv))
    ai = int(np.argmax(av) if sd > 0 else np.argmin(av))
    fo, ao = float(fv[fi]), float(av[ai])
    #   HIS 1114: *"the anchor and floater should be found at the same-side ws5 OHLC open extremum
    #   inside that 25min window, so the timestamps should be multiples of 5 minutes"*. THESE are
    #   the two bars the divergence reads; the ws1b crosses only centred the windows.
    fb = int(np.searchsorted(ln.ts, int(ft[fi])))
    ab = int(np.searchsorted(ln.ts, int(at[ai])))
    assert int(ln.ts[fb]) == int(ft[fi]) and int(ln.ts[ab]) == int(at[ai]), \
        'an extremum open bar is not on the 5 s grid'
    assert int(ft[fi]) % (TRIG_TF * 60 * 1000) == 0 and int(at[ai]) % (TRIG_TF * 60 * 1000) == 0, \
        'an extremum open is not on the ws%d lattice' % TRIG_TF
    earlier = fo if ft[fi] <= at[ai] else ao
    pct = abs(fo - ao) / earlier * 100.0
    within = pct <= DIFF_PCT
    row += [ln.U(ank), ln.U(flo), 'yes', ln.U(fb), '%.5f' % fo, ln.U(ab), '%.5f' % ao,
            '%.4f' % pct, 'yes' if within else 'NO']
    if not within:
        print('| ' + ' | '.join(row + ['-'] * 3 + ['sideways == true - the diff is too wide']) + ' |')
        continue
    sts = []
    for t in (3, 4, 5):
        d = J.anchor_floater_given(RD[t], close, sd, ab, fb)
        sts.append('none' if d is None else str(d['state']))
    hit = any(s == str(int(sd)) for s in sts)
    print('| ' + ' | '.join(row + sts
                            + ['sideways == FALSE - divergence' if hit
                               else 'sideways == true - no divergence']) + ' |')
