"""JOE'S TWO READS AS COLUMNS, APPLIED TO ALL 12 STOPPED TRADES. 1008.

Joe's 10:56:40 read, verbatim:
  *"-all TF's >7 are showing upward traj and momentum / -ws11 or ws12 are weak, supporting the
    upward momentum / -`x` and `m` print a clean upward ladder from ws3"*  -> flip the trade to LONG

Joe's 12:27:05 read, verbatim:
  *"-ws1r to ws12r is a -60 downward ladder, although it's not monotonic: the lower cluster is
    upward ... the higher wsf lines are facing down ... the higher wsf and the dtf Mages are coming
    off a high ex-fence pegging that started at ~08:14. at 12:27, all >ws5Mages (including DTF
    mages) are falling away from hi ex-fence and creating a down facing mage ladder/cascade ...
    ws{10,11,12}r have yet to cross to oob or ex-fence yet"*

WHAT IS MEASURED, and nothing is scored as a verdict:
  the r ladder        ws1r -> ws12r delta, monotonic or not, and the TF where the sign flips
  the cluster split   the lower cluster's direction against the higher cluster's, in TF order
  the pegging start   per TF, the FIRST bar of the current unbroken no-counter-visit run. Joe reads
                      ~08:14 for the 12:27 open, so this column must land near it there.
  de-pegging          per TF above ws5, the Mage's distance from the hi/lo ex-fence and whether its
                      last step moved away from it
  ws10/11/12 r        at oob, at ex-fence, or neither - Joe's "have yet to cross"
  the x and m ladders their ws3 -> ws12 delta, Joe's "clean upward ladder from ws3"

THE TIME DIRECTION of a line is the sign of (value now - value at its last step change). The higher
TFs are step functions, so the last step is well defined and needs no window. That is the only way
I could read "traj" without inventing a lookback.

DTF = ws13 and above, per task #14's wording. Lines exist to ws30 for r, m, x and Mage.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
L = {}
for role in ('r', 'm', 'x', 'Mage'):
    for t in range(1, 31):
        L[(t, role)] = SC.LD(t * 60, role)[:N]
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
HI, LO = SC.HI, SC.LO
DAYOF = lambda k: datetime.datetime.utcfromtimestamp(int(SC.ts[k]) / 1000).strftime('%Y-%m-%d')
K = lambda s: SC.K(s)

STOPS = [('2026-09-25 10:56:40', 'SHORT'), ('2026-09-25 12:27:05', 'LONG'),
         ('2026-09-25 15:41:00', 'LONG'), ('2026-09-25 18:59:10', 'SHORT'),
         ('2026-09-25 21:27:40', 'LONG'), ('2026-09-25 22:28:25', 'SHORT'),
         ('2026-09-26 04:30:55', 'LONG'), ('2026-09-26 09:06:00', 'LONG'),
         ('2026-09-26 11:46:35', 'LONG'), ('2026-09-26 14:17:35', 'SHORT'),
         ('2026-09-26 16:25:40', 'LONG'), ('2026-09-26 18:37:00', 'LONG')]

def step_dir(t, role, k):
    """Sign of (value at k) - (value at the line's last step change at or before k). Cap-free."""
    v = L[(t, role)]
    cur = float(v[k])
    j = k
    while j > 0 and (not np.isfinite(v[j - 1]) or float(v[j - 1]) == cur):
        j -= 1
    if j <= 0: return 0
    prev = float(v[j - 1])
    return 1 if cur > prev else (-1 if cur < prev else 0)

def peg_start(t, k, dr):
    """First bar of the current unbroken run with NO counter-dr ex-fence visit, for ws{t}Mage."""
    ctf = (lambda v: v <= EXF_LO) if dr > 0 else (lambda v: v >= EXF_HI)
    m = L[(t, 'Mage')]
    for j in range(k, max(0, k - 34560) - 1, -1):
        v = float(m[j])
        if np.isfinite(v) and ctf(v):
            return j + 1
    return None

def fence_state(t, k, dr):
    v = float(L[(t, 'r')][k])
    if dr > 0:
        return 'oob' if v >= HI else ('ex-fence' if v >= EXF_HI else 'neither')
    return 'oob' if v <= LO else ('ex-fence' if v <= EXF_LO else 'neither')

def ladder(role, k, lo, hi):
    v = [float(L[(t, role)][k]) for t in range(lo, hi + 1)]
    st = [v[i] - v[i - 1] for i in range(1, len(v))]
    mono = all(s > 0 for s in st) or all(s < 0 for s in st)
    flip = None
    for i, s in enumerate(st):
        if i and (s > 0) != (st[i - 1] > 0):
            flip = lo + i; break
    return v[-1] - v[0], mono, flip

# ---- the two legs Joe read, in full
for ts, side in STOPS[:2]:
    k = K(ts); dr = int(DRv[k])
    print('\n# %s   %s   dr %+d   pxs %.6f — THE FULL LADDERS' % (ts, side, dr, float(PX[k])))
    box(('TF', 'r', 'r fence', 'r dir', 'Mage', 'Mage dir', 'Mage to hi ex-fence',
         'pegged since', 'm', 'm dir', 'x', 'x dir'),
        [('ws%d' % t, '%.2f' % float(L[(t, 'r')][k]), fence_state(t, k, dr),
          '%+d' % step_dir(t, 'r', k), '%.2f' % float(L[(t, 'Mage')][k]),
          '%+d' % step_dir(t, 'Mage', k),
          '%+.1f' % (float(L[(t, 'Mage')][k]) - EXF_HI),
          (SC.U(peg_start(t, k, dr)) if peg_start(t, k, dr) else '—'),
          '%.2f' % float(L[(t, 'm')][k]), '%+d' % step_dir(t, 'm', k),
          '%.2f' % float(L[(t, 'x')][k]), '%+d' % step_dir(t, 'x', k))
         for t in range(1, 31)])

# ---- the 12-leg comparison
print('\n# ALL 12 STOPPED TRADES — JOE\'S READS AS COLUMNS')
rows = []
for ts, side in STOPS:
    k = K(ts); dr = int(DRv[k])
    d12, mono12, flip12 = ladder('r', k, 1, 12)
    dx, _, _ = ladder('x', k, 3, 12)
    dm, _, _ = ladder('m', k, 3, 12)
    up_hi = sum(1 for t in range(8, 13) if step_dir(t, 'r', k) > 0)
    dn_hi = sum(1 for t in range(8, 13) if step_dir(t, 'r', k) < 0)
    away = sum(1 for t in range(6, 31)
               if (step_dir(t, 'Mage', k) < 0 and float(L[(t, 'Mage')][k]) < EXF_HI + 10))
    ps = [peg_start(t, k, dr) for t in range(6, 13)]
    ps = [p for p in ps if p]
    f101112 = ', '.join(fence_state(t, k, dr)[:3] for t in (10, 11, 12))
    rows.append((DAYOF(k)[5:], side, SC.U(k), '%+d' % dr,
                 '%+.1f' % d12, 'Y' if mono12 else 'no',
                 ('ws%d' % flip12) if flip12 else '—',
                 '%d up / %d dn' % (up_hi, dn_hi),
                 '%+.1f' % dx, '%+.1f' % dm,
                 str(away),
                 SC.U(min(ps)) if ps else '—',
                 f101112))
box(('day', 'side', 'open', 'dr', 'ws1r->ws12r', 'monotonic', 'r sign flips at',
     'ws8..ws12 r dir', 'ws3x->ws12x', 'ws3m->ws12m', '>ws5 Mages falling off hi ex-fence',
     'earliest peg start ws6..ws12', 'ws10/11/12 r fence'), rows)
print('\n- "falling off hi ex-fence" counts ws6..ws30 Mages whose last step was DOWN and which sit')
print('  below the hi ex-fence + 10. The +10 band is MINE and the only threshold in the table.')
print('- "r sign flips at" is the lowest TF where the ws1->ws12 r ladder changes direction.')
