"""JOE'S 01:28 READ, CLAUSE BY CLAUSE, AS NUMBERS. 1009.

Joe 1009: *"would we be able to build this together if I share what I see on the charts and what I
would be monitoring if I was trading by hand, for each timestamp, so you can gather enough mechs to
build a model that you can apply to any stalemate? the mechs I share will be fuzzy - you'll need to
think in ranges or clusters, not specifics"*.

His four clauses for 2026-08-23 01:28:15, dr +1, and why he calls it DOWN:

  C1  *"practically every TF >8 has mage printing lower than r. this the Mages creating a strong
      downward lead"*
  C2  *"the lower wsf r's are all weak (ie have not been hi oob for ~1 hour) and are printing mid
      board"*
  C3  *"the r lines between ws5 and ws11 are collectively showing downward traj and momentum"*
  C4  *"there are multiple downward x-crosses bouncing in the lead up to 01:28"*

Each clause is printed as the number it would have to be. NO THRESHOLD IS APPLIED - the bands and
windows are Joe's to set, so every candidate window is shown side by side instead of one being
picked.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from _trajmech import traj

SC, box, U = C.SC, C.box, C.SC.U
N = len(SC.ts); HI, LO = SC.HI, SC.LO
TS = os.environ.get('X_TS', '2026-08-23 01:28:15'); D = int(os.environ.get('X_DR', 1))
k = SC.K(TS)
TFS = list(C.ALL_TF)
R = {t: np.asarray(C.R[t], float)[:N] for t in TFS}
X = {t: np.asarray(C.X[t], float)[:N] for t in TFS}
M = {t: np.asarray(SC.LD(t * 60, 'Mage'), float)[:N] for t in TFS}
print('# %s   leg dr %+d   ws%dr %.2f   THE VOTE TIES'
      % (TS, D, C.TRIG_TF, float(R[C.TRIG_TF][k])), flush=True)

print('\n# C1 — "practically every TF >8 has mage printing lower than r"')
rows = []
for lo, hi, lbl in ((1, 8, 'ws1-ws8'), (9, 23, 'ws9-ws23'), (1, 23, 'every TF')):
    sel = [t for t in TFS if lo <= t <= hi]
    g = [float(M[t][k]) - float(R[t][k]) for t in sel]
    bel = sum(1 for z in g if z < 0)
    rows.append((lbl, str(len(sel)), str(bel), '%.0f%%' % (100.0 * bel / len(sel)),
                 '%+.2f' % float(np.median(g)), '%+.2f' % min(g), '%+.2f' % max(g)))
box(('the band', 'TFs in it', 'Mage BELOW r', '% below', 'median Mage-r', 'most negative',
     'most positive'), rows)
print('- the cut Joe named is TF > 8. the row above it is printed so the contrast is visible.')

print('\n# C2 — "the lower wsf r\'s ... have not been hi oob for ~1 hour ... printing mid board"')
rows = []
for t in [z for z in TFS if z <= 8]:
    r = R[t]
    was = np.flatnonzero(r[:k + 1] >= HI)
    wlo = np.flatnonzero(r[:k + 1] <= LO)
    rows.append(('ws%dr' % t, '%.2f' % float(r[k]),
                 '%.1f' % ((k - int(was[-1])) * 5 / 60.0) if len(was) else 'never',
                 U(int(was[-1])) if len(was) else '—',
                 '%.1f' % ((k - int(wlo[-1])) * 5 / 60.0) if len(wlo) else 'never',
                 U(int(wlo[-1])) if len(wlo) else '—'))
box(('the line', 'r now', 'min since it was last HI oob (>=%.0f)' % HI, 'that bar',
     'min since LOW oob (<=%.0f)' % LO, 'that bar'), rows)
v = [float(R[t][k]) for t in TFS if t <= 8]
box(('"mid board" — where ws1-ws8 r actually sit', 'value'),
    [('min', '%.2f' % min(v)), ('median', '%.2f' % float(np.median(v))), ('max', '%.2f' % max(v)),
     ('how many in 40-60', str(sum(1 for z in v if 40 <= z <= 60))),
     ('how many in 30-70', str(sum(1 for z in v if 30 <= z <= 70))),
     ('how many in 25-75 - the named fence', str(sum(1 for z in v if 25 <= z <= 75))),
     ('how many oob either way (<=%.0f or >=%.0f)' % (LO, HI),
      str(sum(1 for z in v if z <= LO or z >= HI)))])

print('\n# C3 — "the r lines between ws5 and ws11 are collectively showing downward traj"')
rows = []; u = dn = fl = 0
for t in range(5, 12):
    r = traj(R[t], k, C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND, D)
    u += r['dir'] > 0; dn += r['dir'] < 0; fl += r['dir'] == 0
    rows.append(('ws%dr' % t, '%.2f' % float(R[t][k]),
                 {1: 'UP +1', -1: 'DOWN -1', 0: 'FLAT 0'}[int(r['dir'])],
                 '%+.4f' % r['travel'] if np.isfinite(r['travel']) else 'n/a',
                 '%d samples = %.1f min' % (r['tail_used'], r['tail_used'] * C.TRAJ_BLOCK * 5 / 60.0),
                 str(r['deferred']),
                 U(r['reversal_bar']) if r['reversal_bar'] is not None else '—'))
box(('the line', 'r now', 'its traj dir', 'travel', 'tail it used', 'deferred',
     'the reversal bar'), rows)
box(('the ws5-ws11 tally', 'count'), [('DOWN -1', str(dn)), ('UP +1', str(u)), ('FLAT 0', str(fl))])
print('- mom-true per TF is NOT here: `momtrue_mask` keys its cache on the TF, so ws5-ws11 needs')
print('  7 cache builds. Say the word and I run them.')

print('\n# C4 — "multiple downward x-crosses bouncing in the lead up to 01:28"')
rows = []
for w in (5, 10, 20, 40, 60):
    nb = int(round(w * 60 / 5.0)); a = max(1, k - nb + 1)
    tot = 0; per = []
    for t in TFS:
        xu = X[t] < R[t]
        c = int(np.sum(xu[a:k + 1] & ~xu[a - 1:k]))
        tot += c
        if c: per.append('ws%d x%d' % (t, c))
    rows.append(('%d min' % w, str(nb), str(tot), '%.2f' % (tot / float(len(TFS))),
                 ', '.join(per) if per else 'none'))
box(('the lookback', 'bars', 'downward x-crosses, all %d TFs' % len(TFS), 'per TF',
     'where they fired'), rows)
print('- a DOWNWARD x-cross is ws{t}x crossing from above to below ws{t}r - the dr +1 direction,')
print('  per the x-cross direction ruling. Counted per TF, every TF ws1-ws%d.' % max(TFS))
