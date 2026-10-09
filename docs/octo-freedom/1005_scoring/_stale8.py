"""THE NEXT 8 TIES, EVERY MODEL CLAUSE AS A RANGE. 1009.

Joe 1009: *"using ranges and clusters, instead of fixed values (eg TFs >8 could just as easily be
TFs >7 or >11, ws1-ws3 could be ws1-ws4), scan the next 8 ties and see if you can pick any of your
model clauses"*.

A TIE is a ws12r dwell-ending where the 40-min UP/DOWN vote on ws60r splits evenly.

Every clause is printed at SEVERAL cuts so the cut is not a hidden choice:
  C1  Mage below r, for every cut TF > 6,7,8,9,10,11
  C2  ws1-ws3, ws1-ws4, ws1-ws5: how many oob now, and the minutes since each side's last oob
  C3  traj DOWN vs UP, for the bands ws4-ws10, ws5-ws11, ws6-ws12
  C4  x below r, across all TFs and the two halves, with the distance x closed back toward 50
  TB  the tie-breaker: ws60r latest - earliest over 3 x TF = 36 samples

NO CLAUSE IS SCORED AGAINST TRUTH. Joe has not read these bars and no outcome is measured here, so
the only thing the table can show is what each clause says and whether the clauses agree.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from _trajmech import traj, sample_series

SC, box, U = C.SC, C.box, C.SC.U
N = len(SC.ts); HI, LO = SC.HI, SC.LO; TF = C.TRIG_TF
R12 = np.asarray(C.R[TF], float)[:N]
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
TFS = list(C.ALL_TF)
R = {t: np.asarray(C.R[t], float)[:N] for t in TFS}
X = {t: np.asarray(C.X[t], float)[:N] for t in TFS}
MG = {t: np.asarray(SC.LD(t * 60, 'Mage'), float)[:N] for t in TFS}
BL = C.TRAJ_BLOCK * 5 / 60.0; LOOK = 3 * TF
ND = int(round(40.0 / BL))
sg = lambda z: 0 if z == 0 else (1 if z > 0 else -1)
NM = {0: 'tied', 1: 'UP', -1: 'DOWN'}
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
START = SC.K(os.environ.get('X_AFTER', '2026-08-24 00:00:00'))
WANT = int(os.environ.get('X_N', 8))

# ---- find the ties
ends = []
for d in (+1, -1):
    ob = ((R12 >= C.G_HI) if d > 0 else (R12 <= C.G_LO)) & np.isfinite(R12)
    st = np.flatnonzero(ob & ~np.r_[False, ob[:-1]]); en = np.flatnonzero(ob & ~np.r_[ob[1:], False])
    for a, b in zip(st, en):
        if b < a + C.GATE_BARS + 1: continue
        k = a + C.GATE_BARS + 1
        if k < START: continue
        ends.append((k, d, a, b))
ends.sort()
ties = []
for k, d, a, b in ends:
    s = traj(R60, k, C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND, d)['samples']
    if len(s) < ND + 1: continue
    u = dn = 0
    for i in range(ND):
        z = sg(float(R60[s[i][0]]) - float(R60[s[i + 1][0]])); u += z > 0; dn += z < 0
    if u == dn:
        ties.append((k, d, a, b, u, dn))
    if len(ties) >= WANT: break
print('# %d TIES from %s forward. the vote window is 40 min = %d diffs'
      % (len(ties), U(START), ND), flush=True)

def c1(k):
    out = {}
    for cut in (6, 7, 8, 9, 10, 11):
        sel = [t for t in TFS if t > cut]
        g = [float(MG[t][k]) - float(R[t][k]) for t in sel]
        bel = sum(1 for z in g if z < 0)
        out[cut] = (bel, len(sel), float(np.median(g)))
    return out
def c2(k):
    out = {}
    for hi_ in (3, 4, 5):
        sel = list(range(1, hi_ + 1)); oo = 0; mh = []; ml = []
        for t in sel:
            r = R[t]
            if float(r[k]) >= HI or float(r[k]) <= LO: oo += 1
            wh = np.flatnonzero(r[:k + 1] >= HI); wl = np.flatnonzero(r[:k + 1] <= LO)
            mh.append((k - int(wh[-1])) * 5 / 60.0 if len(wh) else 9e9)
            ml.append((k - int(wl[-1])) * 5 / 60.0 if len(wl) else 9e9)
        out[hi_] = (oo, len(sel), float(np.median(mh)), float(np.median(ml)))
    return out
def c3(k, d):
    out = {}
    for lo_, hi_ in ((4, 10), (5, 11), (6, 12)):
        u = dn = fl = 0
        for t in range(lo_, hi_ + 1):
            r = traj(R[t], k, C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND, d)
            u += r['dir'] > 0; dn += r['dir'] < 0; fl += r['dir'] == 0
        out[(lo_, hi_)] = (dn, u, fl)
    return out
def c4(k, w=20):
    nb = int(round(w * 60 / 5.0)); a = max(1, k - nb + 1)
    bel = 0; closed = []
    for t in TFS:
        xn, rn = float(X[t][k]), float(R[t][k])
        if not (np.isfinite(xn) and np.isfinite(rn)): continue
        bel += xn < rn
        seg = X[t][a:k + 1]; ok = np.isfinite(seg)
        if ok.any():
            dist = np.where(ok, np.abs(seg - 50.0), -np.inf)
            xe = float(seg[int(np.argmax(dist))])
            closed.append(abs(xe - 50.0) - abs(xn - 50.0))
    return bel, len(TFS), float(np.median(closed)) if closed else float('nan')
def tb(k, d):
    s = sample_series(R60, k, C.TRAJ_BLOCK, LOOK, C.TRAJ_KIND, d)
    if len(s) < 2: return None, 0
    return s[0][1] - s[-1][1], len(s)

print('\n# C1 — Mage BELOW r, at every cut. "DOWN" is read as the Mages sitting below')
rows = []
for k, d, a, b, u, dn in ties:
    o = c1(k)
    rows.append((DAY(k), U(k), '%+d' % d)
                + tuple('%d/%d  %.0f%%' % (o[c][0], o[c][1], 100.0 * o[c][0] / o[c][1])
                        for c in (6, 7, 8, 9, 10, 11))
                + ('%+.1f' % o[8][2],))
box(('day', 'the dwell-ending', 'dr', 'TF>6', 'TF>7', 'TF>8', 'TF>9', 'TF>10', 'TF>11',
     'median Mage-r above ws8'), rows)

print('\n# C2 — the lower wsf lines: how many oob NOW, and minutes since each side\'s last oob')
rows = []
for k, d, a, b, u, dn in ties:
    o = c2(k)
    rows.append((DAY(k), U(k), '%+d' % d)
                + tuple('%d/%d' % (o[h][0], o[h][1]) for h in (3, 4, 5))
                + tuple('%.0f' % o[h][2] for h in (3, 4, 5))
                + tuple('%.0f' % o[h][3] for h in (3, 4, 5)))
box(('day', 'the dwell-ending', 'dr', 'oob now ws1-3', 'ws1-4', 'ws1-5',
     'min since HI oob ws1-3', 'ws1-4', 'ws1-5',
     'min since LOW oob ws1-3', 'ws1-4', 'ws1-5'), rows)

print('\n# C3 — traj across the mid bands, DOWN vs UP vs FLAT')
rows = []
for k, d, a, b, u, dn in ties:
    o = c3(k, d)
    rows.append((DAY(k), U(k), '%+d' % d)
                + tuple('%dD %dU %dF' % o[bd] for bd in ((4, 10), (5, 11), (6, 12)))
                + (NM[sg(o[(5, 11)][1] - o[(5, 11)][0])],))
box(('day', 'the dwell-ending', 'dr', 'ws4-ws10', 'ws5-ws11', 'ws6-ws12',
     'ws5-ws11 majority'), rows)

print('\n# C4 — x below its own r, and how far x closed back toward 50 over 20 min')
rows = []
for k, d, a, b, u, dn in ties:
    bel, tot, cl = c4(k)
    rows.append((DAY(k), U(k), '%+d' % d, '%d/%d' % (bel, tot),
                 '%.0f%%' % (100.0 * bel / tot), '%d/%d' % (tot - bel, tot),
                 '%.1f' % cl, 'DOWN' if bel > tot - bel else ('UP' if bel < tot - bel else 'tied')))
box(('day', 'the dwell-ending', 'dr', 'x BELOW r', '% below', 'x above r',
     'median distance closed back', 'what the count leans'), rows)

print('\n# THE TIE-BREAKER vs EVERY CLAUSE — one row per tie')
rows = []
agree = collections.Counter()
for k, d, a, b, u, dn in ties:
    df, ns = tb(k, d)
    t = sg(df) if df is not None else 0
    o1 = c1(k); o3 = c3(k, d); bel, tot, cl = c4(k)
    v1 = -1 if o1[8][0] > o1[8][1] - o1[8][0] else (1 if o1[8][0] < o1[8][1] - o1[8][0] else 0)
    v3 = sg(o3[(5, 11)][1] - o3[(5, 11)][0])
    v4 = -1 if bel > tot - bel else (1 if bel < tot - bel else 0)
    for nm, v in (('C1', v1), ('C3', v3), ('C4', v4)):
        agree[(nm, 'agrees with the tie-breaker' if v == t and t != 0
               else ('disagrees' if t != 0 and v != 0 else 'no verdict'))] += 1
    rows.append((DAY(k), U(k), '%+d' % d, '%+.4f' % df if df is not None else 'n/a', NM[t],
                 NM[v1], NM[v3], NM[v4],
                 'HANDOVER' if t == d else ('REFUSED' if t == -d else 'tied')))
box(('day', 'the dwell-ending', 'dr', 'ws60r latest-earliest over %d samples' % LOOK,
     'the tie-breaker', 'C1 Mage', 'C3 traj', 'C4 x-below-r', 'the gate it gives'), rows)
box(('clause vs the tie-breaker', 'count'), [('%s %s' % kk, str(v)) for kk, v in sorted(agree.items())])
