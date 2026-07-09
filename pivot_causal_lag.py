"""pivot_causal_lag.py — how much of the pivot edge survives being legal? (Joe 0709)

Entering AT a swing pivot is hindsight: the pivot is confirmed only once price has moved `pct%` away from it.
The ceiling run showed the exit is sound and the deficit is entry timing (+0.706%/trade at pct=0.9 vs
-0.174% for the v2 entries).

Two measurements:

(1) CAUSAL PIVOT ENTRY. Enter at the CONFIRMATION bar — the first bar where price has moved pct% from the
    extreme. That bar is knowable in real time. The entry price is worse by roughly pct%.

    PREDICTION (before the run): the lag costs about pct%, so all three books land at or below zero:
    0.5% -> ~-0.19%, 0.9% -> ~-0.19%, 1.5% -> ~-0.24%. If any is clearly positive, there is reachable edge.

(2) WHERE THE v2 ENTRIES SIT relative to the nearest pivot of the same direction: lag in bars, and the price
    penalty paid versus entering at that pivot.

`find_pivots` is re-implemented here so the confirmation bar can be recorded; the pivot indices are asserted
identical to the library's. Read-only. Run:  python3 pivot_causal_lag.py
"""
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import lr_exit_v2, v2_walk_ad
from optimus9.compute.swing_detect import find_pivots
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS

SPAN_D = 42
COST = 0.20
PCTS = (0.5, 0.9, 1.5)
BAR_S = 5


def pivots_with_confirm(price, pct):
    """(pivot_i, kind, confirm_i) — confirm_i is the bar at which the pivot became knowable."""
    price = np.asarray(price, float)
    n = len(price); thr = pct / 100.0
    fin = np.flatnonzero(np.isfinite(price) & (price > 0))
    if fin.size < 2:
        return []
    start = int(fin[0]); hi_i = lo_i = ext_i = start; trend = 0
    out = []
    for i in range(start + 1, n):
        p = price[i]
        if not np.isfinite(p) or p <= 0:
            continue
        if trend == 0:
            if p > price[hi_i]:
                hi_i = i
            if p < price[lo_i]:
                lo_i = i
            if (price[hi_i] - p) / price[hi_i] >= thr:
                out.append((int(hi_i), 'H', i)); trend = -1; ext_i = i
            elif (p - price[lo_i]) / price[lo_i] >= thr:
                out.append((int(lo_i), 'L', i)); trend = 1; ext_i = i
        elif trend == 1:
            if p >= price[ext_i]:
                ext_i = i
            elif (price[ext_i] - p) / price[ext_i] >= thr:
                out.append((int(ext_i), 'H', i)); trend = -1; ext_i = i
        else:
            if p <= price[ext_i]:
                ext_i = i
            elif (p - price[ext_i]) / price[ext_i] >= thr:
                out.append((int(ext_i), 'L', i)); trend = 1; ext_i = i
    return out


def stats(name, W, lr, ent):
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    n = len(px)
    net, sl = [], []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= n:
            continue
        net.append(bd * (xpx - epx) / epx * 100.0 - COST); sl.append(1 if reason == 'SL' else 0)
    a = np.asarray(net)
    if a.size < 30:
        print("  %-26s n=%d (too few)" % (name, a.size)); return
    w, l = a[a > 0], a[a <= 0]
    print("  %-26s n=%-5d net=%+9.2f%%  mean=%+.4f%%  win=%4.1f%%  stop=%4.1f%%  avgW=%+.3f%%  avgL=%+.3f%%"
          % (name, a.size, a.sum(), a.mean(), 100 * (a > 0).mean(), 100 * np.mean(sl),
             w.mean() if w.size else 0, l.mean() if l.size else 0))


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    print("42d · breach arm · cost %.2f%% · stop %.2f%%\n" % (COST, lr.sl))

    real = v2_walk_ad(W, lr)
    stats("v2 entries", W, lr, real)

    for pct in PCTS:
        pw = pivots_with_confirm(px, pct)
        lib = [(i, k) for (i, k) in find_pivots(px, pct=pct) if k in 'HL']
        mine = [(i, k) for (i, k, _) in pw]
        assert set(mine).issubset(set(lib)), "pivot mismatch vs library"

        print("\n--- pct=%.1f%%   pivots=%d ---" % (pct, len(pw)))
        ideal = [(int(ts[i]), -(1 if k == 'L' else -1), (1 if k == 'L' else -1), int(i))
                 for (i, k, c) in pw if 0 < i < len(ts) - 1]
        causal = [(int(ts[c]), -(1 if k == 'L' else -1), (1 if k == 'L' else -1), int(c))
                  for (i, k, c) in pw if 0 < c < len(ts) - 1]
        stats("at the pivot (hindsight)", W, lr, ideal)
        stats("at confirmation (legal)", W, lr, causal)
        lag = [(c - i) for (i, k, c) in pw]
        pen = [abs(px[c] - px[i]) / px[i] * 100.0 for (i, k, c) in pw]
        print("  confirmation lag: p50=%.1f min  p90=%.1f min   price penalty: p50=%.3f%%  p90=%.3f%%"
              % (np.percentile(lag, 50) * BAR_S / 60, np.percentile(lag, 90) * BAR_S / 60,
                 np.percentile(pen, 50), np.percentile(pen, 90)))

    # ── where do the v2 entries sit relative to the nearest same-direction pivot? ──
    pw = pivots_with_confirm(px, 0.9)
    for want in (1, -1):
        pv = np.array([i for (i, k, c) in pw if (1 if k == 'L' else -1) == want])
        ev = np.array([e[3] for e in real if e[2] == want])
        if not pv.size or not ev.size:
            continue
        j = np.clip(np.searchsorted(pv, ev), 0, pv.size - 1)
        near = pv[j]
        d_bars = ev - near
        pen = want * (px[ev] - px[near]) / px[near] * 100.0     # + = the v2 entry is WORSE than the pivot
        side = "long" if want == 1 else "short"
        print("\nv2 %-5s entries vs nearest 0.9%% pivot (n=%d): bars p50=%+.0f (%.1f min)  price penalty p50=%+.3f%%  p90=%+.3f%%"
              % (side, ev.size, np.percentile(d_bars, 50), np.percentile(np.abs(d_bars), 50) * BAR_S / 60,
                 np.percentile(pen, 50), np.percentile(pen, 90)))
    dev.disconnect()


if __name__ == "__main__":
    main()
