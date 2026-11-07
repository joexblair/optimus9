"""The per-line data behind ONE `MOMO VOTE` row, and the side-audit of every read in it.

HIS 1106 ASK: *"show me the data that produced this row, and confirm that the data is built on a
low side context"* / *"explain in simple terms how these 3 votes individually reached their
decisions"*.

THE VERDICT COMES FROM `v4_fdm2.momo_vote` ITSELF, not from a re-implementation here, so the dump
and the decision can never disagree. Everything else in here is the ARITHMETIC that produced the
three counts, printed line by line at the SAME bar.

  W_ROW_AT    the bar, 'YYYY-MM-DD HH:MM:SS'
  W_ROW_SIDE  the leg's target side: 'LOW' or 'HIGH'. v4_signal.target_side: a LONG hunts the HIGH
              oob (+1), a SHORT the LOW (-1). The side is an INPUT, never derived here.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.environ.setdefault('W_V4_EXPERIMENT', '1')      # the arm is OFF on the bank; this READS it
os.environ.setdefault('W_V4_FDM2_MOMO_ON', '1')
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import ln
    from optimus9.analysis import jig as JIG
    from optimus9.constants import BOUNDARY_HI, BOUNDARY_LO, FENCE_HI, FENCE_LO
finally:
    sys.stderr = _e

AT = os.environ.get('W_ROW_AT', '2026-08-23 07:55:10')
SIDE = -1 if os.environ.get('W_ROW_SIDE', 'LOW').upper() == 'LOW' else +1

LN = F2.load()
NB = len(LN['close'])
BAR = next(b for b in range(NB) if ln.U(b) == AT)
M = F2._momo_lines(LN)
TFS = list(M['tfs'])
V = F2.momo_vote(LN, BAR, SIDE)
assert V['bar'] == BAR
READ = V['read']

mg = LN['CPM'] if READ == 'closed_prev' else LN['MGE']      # ws{t}Mage, the 38-bar %B
xs = M['XCP'] if READ == 'closed_prev' else M['XEM']        # ws{t}x, the 5-bar %B
mm = M['MCP'] if READ == 'closed_prev' else M['MEM']        # ws{t}m, the 6-bar %B
kk = LN['CPR'] if READ == 'closed_prev' else LN['EMR']      # ws{t}r, the %K


def f(v, n=2):
    return 'nan' if not np.isfinite(v) else ('%.*f' % (n, v))


def row(*c):
    print('| ' + ' | '.join(str(x) for x in c) + ' |')


def head(*c):
    row(*c)
    row(*(['---'] * len(c)))


print('| the row | value |')
print('|---|---|')
row('the bar', '%s (index %d)' % (ln.U(BAR), BAR))
row('the leg', '2026-08-23 05:30:20 SHORT' if SIDE < 0 else 'the HIGH-side leg')
row("the leg's target side", '%s (side = %+d)' % ('LOW' if SIDE < 0 else 'HIGH', SIDE))
row('the read', READ + ' (FDM2_MOMO_READ)')
row('the carriers', 'ws%d..ws%d = %d lines (FDM_STEP1_ABOVE_TF %d, HI %d)'
    % (TFS[0], TFS[-1], len(TFS), int(K.FDM_STEP1_ABOVE_TF), int(LN['HI'])))
row('the boundaries', 'oob %g/%g, the no-engage fence %g/%g' % (BOUNDARY_LO, BOUNDARY_HI,
                                                                FENCE_LO, FENCE_HI))
row('r-pred count', '%d of %d, its median knob FDM2_MOMO_FLOOR_RPRED %d, vote if count >= floor'
    % (V['rpred'], len(TFS), int(K.FDM2_MOMO_FLOOR_RPRED)))
row('Mage-beyond-x count', '%d of %d, its median knob FDM2_MOMO_MED_MX %d, vote if count < median'
    % (V['mx'], len(TFS), int(K.FDM2_MOMO_MED_MX)))
row('pinned count', '%d of %d, its median knob FDM2_MOMO_MED_PIN %d, vote if count >= median'
    % (V['pin'], len(TFS), int(K.FDM2_MOMO_MED_PIN)))
row('the vote', '%d of 3, the floor FDM2_MOMO_VOTES %d' % (V['votes'], int(K.FDM2_MOMO_VOTES)))
row('fires', 'YES' if V['fires'] else 'no')

print()
print('# the side audit - every side-dependent read in the row, with side = %+d' % SIDE)
print()
head('the signal', 'the expression in the code', 'with side = %+d' % SIDE, 'so it asks')
row('r-pred', 'predict_breach(...)[bar] == side',
    '== %+d' % SIDE,
    'the %s-side flag only; the %s-side flag (%+d) is not counted'
    % ('low' if SIDE < 0 else 'high', 'high' if SIDE < 0 else 'low', -SIDE))
row('r-pred, inside predict_breach', 'k <= fence_lo and k > lo and anchor_lo <= lo and (lo - anchor_lo) + tol > (k - lo)'
    if SIDE < 0 else 'k >= fence_hi and k < hi and anchor_hi >= hi and (anchor_hi - hi) + tol > (hi - k)',
    'lo = %g, fence_lo = %g, anchor_lo = min(ws{t}m, ws{t}Mage)' % (BOUNDARY_LO, FENCE_LO)
    if SIDE < 0 else 'hi = %g, fence_hi = %g, anchor_hi = max(...)' % (BOUNDARY_HI, FENCE_HI),
    'the LOW branch of the flag' if SIDE < 0 else 'the HIGH branch of the flag')
row('Mage-beyond-x', '(ws{t}Mage - ws{t}x) * side > 0', '(Mage - x) * -1 > 0' if SIDE < 0
    else '(Mage - x) * +1 > 0', 'Mage BELOW x' if SIDE < 0 else 'Mage ABOVE x')
row('pinned', 'at_extreme_mask(ws{t}r emerging, side, ...)', 'side = %+d' % SIDE,
    'the distance is now - the window MINIMUM' if SIDE < 0
    else 'the distance is the window MAXIMUM - now')

print()
print('# signal 1 - r-pred, HIS OWN mech, read on %s' % READ)
print()
head('tf', 'ws{t}r (k)', 'ws{t}m', 'ws{t}Mage', 'anchor_%s = %s' % ('lo' if SIDE < 0 else 'hi',
                                                                    'min' if SIDE < 0 else 'max'),
     'k inside the engage band', 'the anchor is oob', 'the anchor overshoot',
     "k's undershoot", 'overshoot > undershoot', 'the flag', 'counted')
nr = 0
for t in TFS:
    k = float(np.asarray(kk[t], float)[BAR])
    m_ = float(np.asarray(mm[t], float)[BAR])
    g_ = float(np.asarray(mg[t], float)[BAR])
    fl = int(M[('RP', READ, t)][BAR])
    if SIDE < 0:
        anc = min(m_, g_)
        band = (k <= FENCE_LO) and (k > BOUNDARY_LO)
        ancoob = anc <= BOUNDARY_LO
        over, under = BOUNDARY_LO - anc, k - BOUNDARY_LO
        bandtxt = 'k %s %g and k %s %g' % (f(k), FENCE_LO, f(k), BOUNDARY_LO)
    else:
        anc = max(m_, g_)
        band = (k >= FENCE_HI) and (k < BOUNDARY_HI)
        ancoob = anc >= BOUNDARY_HI
        over, under = anc - BOUNDARY_HI, BOUNDARY_HI - k
        bandtxt = 'k %s %g and k %s %g' % (f(k), FENCE_HI, f(k), BOUNDARY_HI)
    hit = fl == SIDE
    nr += 1 if hit else 0
    row('ws%d' % t, f(k), f(m_), f(g_), f(anc),
        'yes' if band else 'NO', 'yes' if ancoob else 'NO', f(over), f(under),
        'yes' if (np.isfinite(over) and np.isfinite(under) and over > under) else 'NO',
        '%+d' % fl, 'YES' if hit else '.')
row('**the count**', '', '', '', '', '', '', '', '', '', '', '**%d of %d**' % (nr, len(TFS)))
assert nr == V['rpred'], 'the dump and momo_vote disagree on r-pred'

print()
print('# signal 2 - Mage beyond x, the 38-bar %%B against the 5-bar %%B, read on %s' % READ)
print()
head('tf', 'ws{t}Mage (38 bars, 0.93s)', 'ws{t}x (5 bars, 0.35s)', 'Mage - x',
     'x %s Mage' % ('above' if SIDE < 0 else 'below'), 'counted')
nx = 0
for t in TFS:
    g_ = float(np.asarray(mg[t], float)[BAR])
    x_ = float(np.asarray(xs[t], float)[BAR])
    d = g_ - x_
    hit = np.isfinite(d) and d * SIDE > 0
    nx += 1 if hit else 0
    row('ws%d' % t, f(g_), f(x_), f(d),
        'yes' if (np.isfinite(d) and d * SIDE > 0) else 'NO', 'YES' if hit else '.')
row('**the count**', '', '', '', '', '**%d of %d**' % (nx, len(TFS)))
assert nx == V['mx'], 'the dump and momo_vote disagree on Mage-beyond-x'

print()
print('# signal 3 - pinned, read on EMERGING whatever FDM2_MOMO_READ says (a pin is a lift-off read)')
print()
head('tf', 'the gap, bars', 'the span, bars', 'the span, s', 'the %d samples'
     % int(K.LIFT_PTS), 'the window %s' % ('minimum' if SIDE < 0 else 'maximum'),
     'now = ws{t}r emerging', 'now - the %s' % ('minimum' if SIDE < 0 else 'maximum'),
     'LIFT_TOL %g' % float(K.LIFT_TOL), 'pinned')
npn = 0
for t in TFS:
    gp = int(K.gap_for(t))
    pts = max(2, int(K.LIFT_PTS))
    span = (pts - 1) * gp
    r = np.asarray(LN['EMR'][t], float)
    idx = [BAR - (pts - 1 - i) * gp for i in range(pts)]
    w = [r[i] if 0 <= i < NB else np.nan for i in idx]
    now = float(w[-1])
    ext = (np.nanmin(w) if SIDE < 0 else np.nanmax(w)) if np.isfinite(w).any() else np.nan
    dist = (now - ext) if SIDE < 0 else (ext - now)
    hit = bool(M[('PIN', t, SIDE)][BAR])
    npn += 1 if hit else 0
    row('ws%d' % t, gp, span, span * 5, ' '.join(f(v, 1) for v in w), f(ext), f(now), f(dist),
        'yes' if (np.isfinite(dist) and dist <= float(K.LIFT_TOL)) else 'NO',
        'YES' if hit else '.')
row('**the count**', '', '', '', '', '', '', '', '', '**%d of %d**' % (npn, len(TFS)))
assert npn == V['pin'], 'the dump and momo_vote disagree on pinned'

print()
print('| the vote, signal by signal | the count | the median knob | the test | fired |')
print('|---|---|---|---|---|')
row('r-pred', '%d of %d' % (V['rpred'], len(TFS)), int(K.FDM2_MOMO_FLOOR_RPRED),
    '%d >= %d' % (V['rpred'], int(K.FDM2_MOMO_FLOOR_RPRED)),
    'YES' if V['rpred'] >= int(K.FDM2_MOMO_FLOOR_RPRED) else 'no')
row('Mage-beyond-x', '%d of %d' % (V['mx'], len(TFS)), int(K.FDM2_MOMO_MED_MX),
    '%d < %d' % (V['mx'], int(K.FDM2_MOMO_MED_MX)),
    'YES' if V['mx'] < int(K.FDM2_MOMO_MED_MX) else 'no')
row('pinned', '%d of %d' % (V['pin'], len(TFS)), int(K.FDM2_MOMO_MED_PIN),
    '%d >= %d' % (V['pin'], int(K.FDM2_MOMO_MED_PIN)),
    'YES' if V['pin'] >= int(K.FDM2_MOMO_MED_PIN) else 'no')
row('**the total**', '**%d of 3**' % V['votes'], '', 'the floor is %d' % int(K.FDM2_MOMO_VOTES),
    '**%s**' % ('LATCHED' if V['fires'] else 'no latch'))
print()
print(V['why'])


#   ── HIS 1106 SPEC UPDATE - THE READS THE UPDATE NEEDS, MEASURED AT THIS ONE BAR ───────────────
#   NOTHING BELOW IS WIRED INTO momo_vote. Every section is a diagnostic read at the SAME bar, put
#   here so his four open concretions can be settled against numbers instead of a preference:
#     1  r-pred gated by `towards` - BOTH reads, because fdm2-momo reads emerging while step1's own
#        precedent calls towards() on closed-prev. The gap is his to close; the numbers are mine.
#     2  the maxTF candidates he named, 10 and 12, on signal 1 and signal 2
#     3  his new internal signal-2 vote: has x crossed Mage inside the last minute, and which way
#     4  his third dimension, REPORTING ONLY: both lines' trajectory from the cadence event to this
#        bar, on emerging, and the bar their fitted paths cross
#   THE PROJECTION CARRIES NO HORIZON. `bars to cross` is derived from the two fitted slopes and is
#   unbounded - inventing a lookahead window to "plot the path" would be a cap he never set.
EVENT = os.environ.get('W_ROW_EVENT', '')
XW = max(1, int(os.environ.get('W_ROW_XWIN', '12')))      # his "last minute" = 12 bars = 60 s

print()
print('# his update 1 - r-pred gated by `towards`, and the maxTF candidates')
print()
head('tf', 'ws{t}r (k)', 'the r-pred flag', 'counted now',
     '`towards` on closed-prev', '`towards` on emerging',
     'counted with the closed-prev gate', 'counted with the emerging gate',
     'inside maxTF 10', 'inside maxTF 12')
G = {}
for t in TFS:
    fl = int(M[('RP', READ, t)][BAR])
    now = fl == SIDE
    tc = bool(F2.towards(LN['CPR'][t], t, BAR, SIDE))
    te = bool(F2.towards(LN['EMR'][t], t, BAR, SIDE))
    G[t] = (now, tc, te)
    row('ws%d' % t, f(float(np.asarray(kk[t], float)[BAR])), '%+d' % fl,
        'YES' if now else '.', 'yes' if tc else 'NO', 'yes' if te else 'NO',
        'YES' if (now and tc) else '.', 'YES' if (now and te) else '.',
        'yes' if t <= 10 else 'NO', 'yes' if t <= 12 else 'NO')
print()
head('the r-pred count under each combination', 'carriers', 'the count')
for lab, hi_ in (('ws4..ws30, no gate - WHAT THE ROW PRINTED', 30), ('ws4..ws10, no gate', 10),
                 ('ws4..ws12, no gate', 12)):
    c = [t for t in TFS if t <= hi_ and G[t][0]]
    row(lab, 'ws4..ws%d = %d' % (hi_, len([t for t in TFS if t <= hi_])),
        '%d (%s)' % (len(c), ', '.join('ws%d' % t for t in c) if c else 'none'))
for gi, gl in ((1, 'the closed-prev `towards` gate'), (2, 'the emerging `towards` gate')):
    for hi_ in (30, 10, 12):
        c = [t for t in TFS if t <= hi_ and G[t][0] and G[t][gi]]
        row('ws4..ws%d, %s' % (hi_, gl), 'ws4..ws%d = %d' % (hi_, len([t for t in TFS if t <= hi_])),
            '%d (%s)' % (len(c), ', '.join('ws%d' % t for t in c) if c else 'none'))

print()
print('# his update 2 - signal 2 under the maxTF candidates, and his new x-crosses-Mage vote')
print()
head('tf', 'ws{t}Mage', 'ws{t}x', 'Mage - x', 'counted by signal 2 now',
     'x crossed Mage inside %d bars = %d s' % (XW, XW * 5), 'the cross bar', 'the direction',
     'his vote', 'inside maxTF 10', 'inside maxTF 12')
C = {}
for t in TFS:
    g_ = float(np.asarray(mg[t], float)[BAR])
    x_ = float(np.asarray(xs[t], float)[BAR])
    d = g_ - x_
    now = bool(np.isfinite(d) and d * SIDE > 0)
    dif = np.asarray(xs[t], float) - np.asarray(mg[t], float)
    cb, dirn = None, '.'
    for i in range(BAR - XW + 1, BAR + 1):
        if i < 1:
            continue
        a, b = dif[i - 1], dif[i]
        if np.isfinite(a) and np.isfinite(b) and a != 0.0 and (a > 0) != (b > 0):
            cb, dirn = i, ('x crossed UNDER Mage' if a > 0 else 'x crossed OVER Mage')
    #   HIS FOUR CASES, verbatim. A SHORT's x crossing UNDER Mage is a `walk` vote; crossing OVER
    #   is a `rev-trade` vote. A LONG's are the mirror. side -1 is the SHORT, +1 the LONG.
    if cb is None:
        vote = '.'
    else:
        under = dirn.endswith('UNDER Mage')
        vote = 'walk' if (under == (SIDE < 0)) else 'rev-trade'
    C[t] = (now, cb, dirn, vote)
    row('ws%d' % t, f(g_), f(x_), f(d), 'YES' if now else '.',
        'yes' if cb is not None else 'NO', ln.U(cb) if cb is not None else '.', dirn, vote,
        'yes' if t <= 10 else 'NO', 'yes' if t <= 12 else 'NO')
print()
head('signal 2 under each carrier set', 'carriers', 'Mage-beyond-x count',
     'his median knob FDM2_MOMO_MED_MX 7', 'x-crossed-Mage lines', '`walk` votes',
     '`rev-trade` votes')
for hi_ in (30, 10, 12):
    sub = [t for t in TFS if t <= hi_]
    nxs = [t for t in sub if C[t][0]]
    crs = [t for t in sub if C[t][1] is not None]
    wk = [t for t in sub if C[t][3] == 'walk']
    rv = [t for t in sub if C[t][3] == 'rev-trade']
    row('ws4..ws%d' % hi_, len(sub), '%d (%s)' % (len(nxs), ', '.join('ws%d' % t for t in nxs) or 'none'),
        'the count is %s 7' % ('below' if len(nxs) < 7 else 'at or above'),
        '%d (%s)' % (len(crs), ', '.join('ws%d' % t for t in crs) or 'none'),
        '%d (%s)' % (len(wk), ', '.join('ws%d' % t for t in wk) or 'none'),
        '%d (%s)' % (len(rv), ', '.join('ws%d' % t for t in rv) or 'none'))

if EVENT:
    EB = next(b for b in range(NB) if ln.U(b) == EVENT)
    assert EB <= BAR, 'the cadence event is after the bar being read'
    print()
    print('# his update 3, REPORTING ONLY - both lines\' trajectory from the cadence event to this bar')
    print()
    print('| the span | value |')
    print('|---|---|')
    row('the cadence event', '%s (index %d)' % (ln.U(EB), EB))
    row('the bar', '%s (index %d)' % (ln.U(BAR), BAR))
    row('the span', '%d bars = %d s = %.1f min' % (BAR - EB + 1, (BAR - EB + 1) * 5,
                                                   (BAR - EB + 1) * 5 / 60.0))
    row('the fit', 'least squares on the emerging bars in the span, slope in r-points per minute')
    row('away from the target side', 'slope > 0 (the target side is LOW)' if SIDE < 0
        else 'slope < 0 (the target side is HIGH)')
    print()
    head('tf', 'ws{t}x slope, r-points/min', 'ws{t}Mage slope, r-points/min',
         'x away from the target side', 'Mage away from the target side', 'both away',
         'ws{t}x - ws{t}Mage at the bar, fitted', 'the gap closing', 'bars to the fitted cross',
         's to the fitted cross', 'the fitted cross travels away from the target side')
    bb = np.arange(EB, BAR + 1, dtype=float)
    for t in TFS:
        xv = np.asarray(xs[t], float)[EB:BAR + 1]
        gv = np.asarray(mg[t], float)[EB:BAR + 1]
        ok = np.isfinite(xv) & np.isfinite(gv)
        if ok.sum() < 2:
            row('ws%d' % t, *(['nan'] * 9))
            continue
        sx, ix = np.polyfit(bb[ok], xv[ok], 1)
        sm, im = np.polyfit(bb[ok], gv[ok], 1)
        fx, fm = sx * BAR + ix, sm * BAR + im
        d = fx - fm
        rel = sx - sm
        btc = (-d / rel) if rel != 0 else np.inf
        closing = (d > 0 and rel < 0) or (d < 0 and rel > 0)
        awx = (sx > 0) if SIDE < 0 else (sx < 0)
        awm = (sm > 0) if SIDE < 0 else (sm < 0)
        crossaway = bool(btc > 0 and np.isfinite(btc) and ((sx > 0) if SIDE < 0 else (sx < 0)))
        row('ws%d' % t, f(sx * 12.0, 3), f(sm * 12.0, 3), 'yes' if awx else 'NO',
            'yes' if awm else 'NO', 'YES' if (awx and awm) else '.', f(d),
            'yes' if closing else 'NO',
            f(btc, 1) if (btc > 0 and np.isfinite(btc)) else 'never on these slopes',
            f(btc * 5, 0) if (btc > 0 and np.isfinite(btc)) else '.',
            'yes' if crossaway else 'NO')
