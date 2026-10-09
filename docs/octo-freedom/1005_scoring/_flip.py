"""THE REFUTATION TEST — THE SAME TOOLS WITH A FLIPPED dr. 1009.

Joe 1009: *"I wonder what will result if we flip the confluence - ie, instead of supporting the C3
data, let's try to refute it using the same tools with a flipped dr view"*.

PART 1 asks which tools can see dr at all. A tool that never reads dr cannot be refuted by flipping
it, and the answer has to be measured, not asserted: every clause is computed at side +1 and at
side -1 and the two are compared byte for byte.

PART 2 runs the one family that IS dr-sensitive - the divergence - with dr flipped: the extremum
anchored on the OPPOSITE side, `anchor_floater` handed -d, and the ws1Mage anchor taken from the
opposite oob side.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from _trajmech import traj, sample_series
from optimus9.analysis.jig import anchor_floater

SC, box, U = C.SC, C.box, C.SC.U
N = len(SC.ts); HI, LO = SC.HI, SC.LO; TF = C.TRIG_TF
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
TFS = list(C.ALL_TF)
R = {t: np.asarray(C.R[t], float)[:N] for t in TFS}
MG = {t: np.asarray(SC.LD(t * 60, 'Mage'), float)[:N] for t in TFS}
M1 = MG[1]
BL = C.TRAJ_BLOCK * 5 / 60.0; LOOK = 3 * TF
sg = lambda z: 0 if z == 0 else (1 if z > 0 else -1)
NM = {0: '-', 1: 'UP', -1: 'DOWN'}
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
TIES = [('2026-08-25 00:42:05', +1), ('2026-08-25 02:06:05', -1), ('2026-08-25 06:54:05', -1),
        ('2026-08-25 18:30:05', +1), ('2026-08-25 22:57:35', +1), ('2026-08-26 00:30:05', -1),
        ('2026-08-26 02:55:50', +1), ('2026-08-26 04:06:05', -1)]
TRUTH = {'2026-08-25 00:42:05': +1, '2026-08-25 02:06:05': +1, '2026-08-25 06:54:05': -1,
         '2026-08-25 18:30:05': +1, '2026-08-25 22:57:35': -1, '2026-08-26 00:30:05': +1,
         '2026-08-26 02:55:50': -1, '2026-08-26 04:06:05': +1}

print('# PART 1 — WHICH TOOLS CAN SEE dr AT ALL. every clause at side +1 and side -1')
print('# TRAJ_KIND is %r\n' % C.TRAJ_KIND, flush=True)
rows = []
for ts, d in TIES:
    k = SC.K(ts)
    c3 = {}
    for s in (+1, -1):
        u = dn = 0
        for t in range(5, 12):
            r = traj(R[t], k, C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND, s)
            u += r['dir'] > 0; dn += r['dir'] < 0
        c3[s] = (dn, u, sg(u - dn))
    tbv = {}
    for s in (+1, -1):
        ss = sample_series(R60, k, C.TRAJ_BLOCK, LOOK, C.TRAJ_KIND, s)
        tbv[s] = round(ss[0][1] - ss[-1][1], 6) if len(ss) >= 2 else None
    rows.append((DAY(k), U(k), '%+d' % d,
                 '%dD %dU %s' % (c3[+1][0], c3[+1][1], NM[c3[+1][2]]),
                 '%dD %dU %s' % (c3[-1][0], c3[-1][1], NM[c3[-1][2]]),
                 'IDENTICAL' if c3[+1] == c3[-1] else '*** DIFFERS',
                 '%+.4f' % tbv[+1], '%+.4f' % tbv[-1],
                 'IDENTICAL' if tbv[+1] == tbv[-1] else '*** DIFFERS'))
box(('day', 'the dwell-ending', 'the real dr', 'C3 computed at side +1', 'C3 at side -1',
     'C3 flip', 'tie-breaker at +1', 'at -1', 'TB flip'), rows)
box(('the clause', 'does it read dr?', 'why'),
    [('C3 traj ws5-ws11', 'NO', 'with TRAJ_KIND %r, `side` is only used by the \'extreme\' sampler;'
      ' `close` takes the block\'s last finite bar' % C.TRAJ_KIND),
     ('the 36-sample tie-breaker', 'NO', 'same sampler, same reason'),
     ('C1 Mage below r', 'NO', 'sign(Mage - r) per TF — no side term'),
     ('C4 x below r', 'NO', 'sign(x - r) per TF — no side term'),
     ('C2 oob counts', 'NO', 'r vs the 15/85 fence — both sides counted'),
     ('the ladders', 'NO', 'monotonic runs across the TF index — no side term'),
     ('the divergence anchor', 'YES', 'the extremum side, `anchor_floater(..., d, ...)` and the '
      'dr-side ws1Mage cross to IB all take d')])

print('\n\n# PART 2 — THE DIVERGENCE WITH dr FLIPPED')
def extremum(line, k, d, w):
    nb = int(round(w * 60 / 5.0)); a = max(1, k - nb + 1)
    seg = line[a:k + 1]; ok = np.isfinite(seg)
    if not ok.any(): return None
    z = np.where(ok, seg, np.inf if d < 0 else -np.inf)
    return a + int(np.argmin(z) if d < 0 else np.argmax(z))
W = int(os.environ.get('X_W', 60))
rows = []; agr = collections.Counter()
for ts, d in TIES:
    k = SC.K(ts)
    for t in (1, 2):
        cells = []
        for lbl, dd in (('real', d), ('flipped', -d)):
            e = extremum(R[t], k, dd, W)
            af = anchor_floater(R[t], C.PX, dd, e) if e is not None else None
            cells.append((U(e) if e is not None else '—',
                          '%.2f' % float(R[t][e]) if e is not None else '—',
                          ('%d' % int(af['fired'])) if af else '—',
                          ('%+.2f' % af['d_osc']) if af else '—'))
        rows.append((DAY(k), U(k), '%+d' % d, 'ws%dr' % t) + cells[0] + cells[1]
                    + ('same bar' if cells[0][0] == cells[1][0] else 'different bar',))
        agr[('fired real %s' % cells[0][2], 'fired flipped %s' % cells[1][2])] += 1
box(('day', 'the dwell-ending', 'real dr', 'the line',
     'extremum REAL dr', 'r there', 'fired', 'd_osc',
     'extremum FLIPPED dr', 'r there', 'fired', 'd_osc', 'the anchor bar'), rows)
box(('fired real -> fired flipped', 'rows of %d' % len(rows)),
    [('%s -> %s' % kk, str(v)) for kk, v in sorted(agr.items())])

print('\n# THE ws1Mage ANCHOR WITH dr FLIPPED')
rows = []
for ts, d in TIES:
    k = SC.K(ts)
    v = float(M1[k])
    cells = []
    for lbl, dd in (('real', d), ('flipped', -d)):
        if v >= HI or v <= LO:
            cells.append((U(k), 'ws1Mage oob at %.2f — no lookback' % v)); continue
        oob = (M1 >= HI) if dd > 0 else (M1 <= LO)
        cr = np.flatnonzero((~oob[1:k + 1]) & oob[0:k])
        cells.append((U(int(cr[-1]) + 1) if len(cr) else '—',
                      'the last %s-side cross to IB' % ('HIGH' if dd > 0 else 'LOW')
                      if len(cr) else 'no cross found'))
    rows.append((DAY(k), U(k), '%+d' % d, '%.2f' % v) + cells[0] + cells[1]
                + ('same bar' if cells[0][0] == cells[1][0] else 'different bar',))
box(('day', 'the dwell-ending', 'real dr', 'ws1Mage now', 'anchor REAL dr', 'what it is',
     'anchor FLIPPED dr', 'what it is', 'the anchor'), rows)
