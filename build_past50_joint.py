"""build_past50_joint — PATH-BASED joint stop×TP bracket for the past-50 mechanic (Joe 0726). SAVED.
Walks the actual px_smooth EVENT-tape price from each entry to the next favourable 2% pivot; first bar that touches
-stop or +TP wins (EXACT first-touch — no MFE/MAE ambiguity guess). Joint grid: stop 0.50..1.00 (Joe's constraint),
TP 0.25..5.0. Drag = 0.36% round-trip (0.11 Bybit fee + 0.25 slippage, o9-live book) subtracted from EVERY trade.
MEAN-primary reporting (+median), win, reward:risk. In-sample bracket params on the 21-day set.
"""
import numpy as np
import build_past50_sweep as S
import build_past50 as P
from optimus9.compute.swing_detect import find_pivots

CFG = dict(wob=5, oob=87, dev=48, seam=2)      # x×Mage best
DRAG = 0.11 + 0.25
SG = np.round(np.arange(0.50, 1.001, 0.05), 2)
TG = np.round(np.arange(0.25, 5.001, 0.25), 2)
INF = 10**9
te, epx = P.te, P.epx
piv = find_pivots(epx, 2.0)
Hidx = np.array([p for p, k in piv if k == 'H']); Lidx = np.array([p for p, k in piv if k == 'L'])


def _end(j, d):
    arr = Hidx if d > 0 else Lidx
    k = np.searchsorted(arr, j + 1)
    return int(arr[k]) if k < len(arr) else min(j + 3000, len(epx) - 1)


def paths():
    days = S.random_days(21, 21)
    ons = [(i, de) for i, de in S.qualify(CFG['oob'], CFG['seam']) if any(a <= te[i] < b for a, b in days)]
    F = S.fires(CFG['wob'], CFG['dev'], CFG['oob'], 'x')
    tr = S.deduped(ons, F)
    P_ = []
    for (ts, tf), d in tr.items():
        j = int(np.searchsorted(te, ts)); e = _end(j, d)
        seg = epx[j:e + 1]
        if len(seg) < 2 or seg[0] <= 0:
            continue
        P_.append(d * (seg - seg[0]) / seg[0] * 100.0)      # favourable return path, %
    return P_


if __name__ == '__main__':
    paths = paths(); N = len(paths)
    stopI = np.full((N, len(SG)), INF); tpI = np.full((N, len(TG)), INF); term = np.zeros(N)
    for t, r in enumerate(paths):
        rmin = np.minimum.accumulate(r); rmax = np.maximum.accumulate(r); term[t] = r[-1]
        for si, s in enumerate(SG):
            h = np.flatnonzero(rmin <= -s)
            if len(h): stopI[t, si] = h[0]
        for ti, tp in enumerate(TG):
            h = np.flatnonzero(rmax >= tp)
            if len(h): tpI[t, ti] = h[0]

    def pnl_for(si, ti):
        st, tp = stopI[:, si], tpI[:, ti]
        out = np.where(st < tp, -SG[si], np.where(tp < st, TG[ti], term))
        out = np.where((st == tp) & (st < INF), -SG[si], out)          # simultaneous touch -> stop (conservative)
        return out - DRAG

    print('=== past-50 x×Mage | PATH-BASED joint stop×TP | %d trades / 21d | drag %.2f%% | MEAN-primary ===' % (N, DRAG))
    best = None
    for si, s in enumerate(SG):
        row_best = None
        for ti, tp in enumerate(TG):
            p = pnl_for(si, ti); m = p.mean()
            if row_best is None or m > row_best[1]:
                row_best = (tp, m, np.median(p), 100 * np.mean(p > 0), p)
            if best is None or m > best[2]:
                best = (s, tp, m, np.median(p), 100 * np.mean(p > 0), p)
        tp, m, md, w, p = row_best
        st = stopI[:, si]
        print('  stop %.2f | best TP %.2f -> MEAN %+.3f  median %+.3f  win %2.0f%%  R:R %.2f  stopped %2.0f%%' % (
            s, tp, m, md, w, tp / s, 100 * np.mean(st < INF)))
    s, tp, m, md, w, p = best
    print('\n=== JOINT BEST  stop %.2f / TP %.2f  (drag %.2f in) ===' % (s, tp, DRAG))
    print('  per-trade MEAN %+.3f%%  median %+.3f  win %.0f%%  std %.2f  R:R %.2f' % (m, md, w, p.std(), tp / s))
    gross = p + DRAG
    print('  gross (pre-drag) mean %+.3f -> drag knocks off %.2f/trade | %d tr / 21d = %.1f/day' % (
        gross.mean(), DRAG, N, N / 21))
    print('  ⚠ in-sample bracket params (21-day fit) + concurrency not modelled (40%% overlap) — confirm OOS')
