"""build_past50_finish — does the gcs5 finisher tighten the past-50 MAE? (Joe 0726). SAVED.
Compares RAW provisional entries vs gcs5-FINISHED entries (same finisher the RC/RPL sweep uses): MAE/MFE distribution
+ path-based joint stop×TP bracket (stop 0.50..1.00, drag 0.36). MEAN-primary. 21 random days, dedup, swing 2%.
"""
import numpy as np
import build_past50 as P
from optimus9.compute.swing_detect import find_pivots

CFG = dict(wob=5, oob=87, dev=48, a='x')
DRAG = 0.11 + 0.25
SG = np.round(np.arange(0.50, 1.001, 0.05), 2); TG = np.round(np.arange(0.25, 5.001, 0.25), 2); INF = 10**9
DAY = 86400 * 1000
te, epx = P.te, P.epx
piv = find_pivots(epx, 2.0)
Hidx = np.array([p for p, k in piv if k == 'H']); Lidx = np.array([p for p, k in piv if k == 'L'])


def days(seed=21, k=21):
    lo, hi = int(te[0]), int(te[-1]) - DAY; nd = int((hi - lo) / DAY)
    offs = np.random.default_rng(seed).choice(np.arange(nd), min(k, nd), replace=False)
    return [(int(lo + o * DAY), int(lo + o * DAY + DAY)) for o in sorted(offs)]


def trades(D, fin, gate=False):
    tr = {}
    for S, E in D:
        for i, de in P.qualify_in(S, E):
            if not (S <= te[i] < E):
                continue
            for ti, tf, br in P.trigger(i, de, CFG['wob'], CFG['a'], fin=fin, gate=gate):
                tr[(int(te[ti]), tf)] = -de
    return tr


def mfe_mae_paths(tr):
    mfe, mae, paths = [], [], []
    for (ts, tf), d in tr.items():
        _, mf, ma = P.lab.score(ts, d); mfe.append(mf); mae.append(ma)
        j = int(np.searchsorted(te, ts)); arr = Hidx if d > 0 else Lidx
        kk = np.searchsorted(arr, j + 1); e = int(arr[kk]) if kk < len(arr) else min(j + 3000, len(epx) - 1)
        seg = epx[j:e + 1]
        if len(seg) >= 2 and seg[0] > 0:
            paths.append(d * (seg - seg[0]) / seg[0] * 100.0)
    return np.array(mfe), np.array(mae), paths


def bracket(paths):
    N = len(paths); stopI = np.full((N, len(SG)), INF); tpI = np.full((N, len(TG)), INF); term = np.zeros(N)
    for t, r in enumerate(paths):
        rmin = np.minimum.accumulate(r); rmax = np.maximum.accumulate(r); term[t] = r[-1]
        for si, s in enumerate(SG):
            h = np.flatnonzero(rmin <= -s)
            if len(h): stopI[t, si] = h[0]
        for ti, tp in enumerate(TG):
            h = np.flatnonzero(rmax >= tp)
            if len(h): tpI[t, ti] = h[0]
    best = None
    for si, s in enumerate(SG):
        for ti, tp in enumerate(TG):
            st, tt = stopI[:, si], tpI[:, ti]
            p = np.where(st < tt, -s, np.where(tt < st, tp, term))
            p = np.where((st == tt) & (st < INF), -s, p) - DRAG
            if best is None or p.mean() > best[2]:
                best = (s, tp, p.mean(), np.median(p), 100 * np.mean(p > 0), p.std())
    return best


if __name__ == '__main__':
    D = days()
    COMBOS = [('RAW', 0, False), ('gcs5', 1, False), ('2-stage', 2, False),
              ('gate+gcs5', 1, True), ('gate+2-stage', 2, True)]
    print('past-50 finisher knobs | 21 random days | dedup | swing 2%% | drag %.2f | MEAN-primary\n' % DRAG)
    for label, fin, gate in COMBOS:
        tr = trades(D, fin, gate); mfe, mae, paths = mfe_mae_paths(tr)
        if not len(mae):
            print('%-14s | 0 trades'); continue
        b = bracket(paths)
        print('%-14s | %3d tr | MAE mean %.2f med %.2f | JOINT stop %.2f/TP %.2f -> MEAN %+.3f  med %+.3f  win %2.0f%%  R:R %.1f' % (
            label, len(mae), mae.mean(), np.median(mae), b[0], b[1], b[2], b[3], b[4], b[1] / b[0]))
