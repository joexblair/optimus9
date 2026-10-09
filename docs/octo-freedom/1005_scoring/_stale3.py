"""C4 AS A MEASURABLE — "READY TO CROSS". 1009.

Joe 1009: *"this could indicate that the line is ready to cross - it's got close enough because it
was travelled from a distant value (further from 50) towards the lines that its bouncing on"*.

Three things in that clause, each printed per TF. NO THRESHOLD IS APPLIED.

  WHERE IT CAME FROM   x's furthest-from-50 value in the lookback, and its bar.
  HOW FAR IT TRAVELLED  |x_extreme - 50| minus |x_now - 50|: the distance it closed BACK towards
                        mid-board. Positive means it came in from a more distant value.
  HOW CLOSE IT IS NOW   |x - r| at the bar, beside the count of downward crosses - the bounces.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, box, U = C.SC, C.box, C.SC.U
N = len(SC.ts)
TS = os.environ.get('X_TS', '2026-08-23 01:28:15'); D = int(os.environ.get('X_DR', 1))
k = SC.K(TS); TFS = list(C.ALL_TF)
R = {t: np.asarray(C.R[t], float)[:N] for t in TFS}
X = {t: np.asarray(C.X[t], float)[:N] for t in TFS}
print('# %s   leg dr %+d   "ready to cross", per TF' % (TS, D), flush=True)
for w in (int(z) for z in os.environ.get('X_WINS', '20,40,60').split(',')):
    nb = int(round(w * 60 / 5.0)); a = max(1, k - nb + 1)
    rows = []
    for t in TFS:
        x, r = X[t], R[t]
        seg = x[a:k + 1]
        ok = np.isfinite(seg)
        if not ok.any(): continue
        dist = np.where(ok, np.abs(seg - 50.0), -np.inf)
        iex = int(np.argmax(dist))
        xe = float(seg[iex]); xn = float(x[k]); rn = float(r[k])
        xu = x < r
        nc = int(np.sum(xu[a:k + 1] & ~xu[a - 1:k]))
        rows.append(('ws%d' % t, '%.2f' % xn, '%.2f' % rn, '%+.2f' % (xn - rn),
                     '%.2f' % abs(xn - rn), '%.2f' % xe, U(a + iex),
                     '%.2f' % abs(xe - 50.0), '%.2f' % abs(xn - 50.0),
                     '%+.2f' % (abs(xe - 50.0) - abs(xn - 50.0)), str(nc),
                     'BELOW r' if xn < rn else 'above r'))
    print('\n# lookback %d min = %d bars' % (w, nb))
    box(('the line', 'x now', 'r now', 'x - r', '|x - r| the gap', 'x furthest from 50',
         'at that bar', '|that x - 50|', '|x now - 50|', 'distance it closed back',
         'downward crosses', 'x sits'), rows)
    cl = [float(abs(float(X[t][k]) - float(R[t][k]))) for t in TFS if np.isfinite(X[t][k])]
    tr = []
    for t in TFS:
        seg = X[t][a:k + 1]; ok = np.isfinite(seg)
        if not ok.any(): continue
        dist = np.where(ok, np.abs(seg - 50.0), -np.inf)
        xe = float(seg[int(np.argmax(dist))])
        tr.append(abs(xe - 50.0) - abs(float(X[t][k]) - 50.0))
    box(('across the %d TFs, %d min' % (len(rows), w), 'value'),
        [('|x - r| — min / median / max', '%.2f / %.2f / %.2f'
          % (min(cl), float(np.median(cl)), max(cl))),
         ('how many have |x - r| under 5', str(sum(1 for z in cl if z < 5))),
         ('how many have |x - r| under 10', str(sum(1 for z in cl if z < 10))),
         ('distance closed back — min / median / max', '%.2f / %.2f / %.2f'
          % (min(tr), float(np.median(tr)), max(tr))),
         ('how many closed back more than 20', str(sum(1 for z in tr if z > 20))),
         ('how many have x BELOW r right now',
          str(sum(1 for t in TFS if np.isfinite(X[t][k]) and float(X[t][k]) < float(R[t][k]))))])
