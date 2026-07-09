"""arm_delay_sweep.py — the v2 arm fires 24 min early. Does a fixed delay recover the edge? (Joe 0709)

Bounds on one axis, all measured, 42d, breach arm, same exit:
  enter at the v2 arm            24 min early   mean -0.1745%
  enter at pivot confirmation    pct% late      mean -0.2229% / -0.2246% / -0.2166%  (0.5 / 0.9 / 1.5)
  enter at the pivot (hindsight) exact          mean +0.7071%  (pct=0.9)

The v2 entries sit 286 bars (24.0 min, long) and 297 bars (24.8 min, short) before the nearest 0.9% pivot, at
a price 0.7% worse. The reachable zone lies between the two legal bounds.

Simplest possible probe: shift every v2 entry forward by a fixed delay D and re-score. No new signal, no new
mechanism -- just the question "is the arm early, and by how much?"

PREDICTION (before the run): the mean improves as D approaches ~24 min and degrades after. A delay is a blunt
instrument -- it moves good and bad entries alike -- so I expect the peak to be well short of the +0.71%
ceiling, and possibly still negative. If the curve is FLAT, the 24-minute gap is a median with no per-trade
information in it, and delay is not the repair.

D is a fixed number of bars. Entries whose delayed bar runs past the window end are dropped.
Read-only. Run:  python3 arm_delay_sweep.py
"""
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import lr_exit_v2, v2_walk_ad
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS

SPAN_D = 42
COST = 0.20
BAR_S = 5
DELAYS_MIN = (0, 2, 5, 10, 15, 20, 24, 30, 40, 60)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    n = len(px)
    base = v2_walk_ad(W, lr)
    print("42d · breach arm · %d entries · cost %.2f%% · stop %.2f%%\n" % (len(base), COST, lr.sl))
    print("%-8s %6s %10s %10s %7s %7s %9s %9s   %s"
          % ("delay", "n", "net", "mean", "win%", "stop%", "avgW", "avgL", "halves (mean)"))

    for D in DELAYS_MIN:
        shift = D * 60 // BAR_S
        ent = [(int(ts[k + shift]), es, bd, k + shift) for (t, es, bd, k) in base if k + shift < n - 1]
        seen, ded = set(), []
        for e in ent:                                   # a delay can collide two arms onto one bar
            if e[3] not in seen:
                seen.add(e[3]); ded.append(e)
        net, sl, bars = [], [], []
        for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ded, predict=False):
            e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
            if x <= e or x >= n:
                continue
            net.append(bd * (xpx - epx) / epx * 100.0 - COST)
            sl.append(1 if reason == 'SL' else 0); bars.append(e)
        a = np.asarray(net); b = np.asarray(bars)
        if a.size < 30:
            print("%-8s n=%d (too few)" % ("%dmin" % D, a.size)); continue
        w, l = a[a > 0], a[a <= 0]
        half = np.median(b)
        m1, m2 = a[b < half], a[b >= half]
        print("%-8s %6d %+9.2f%% %+9.4f%% %6.1f%% %6.1f%% %+8.3f%% %+8.3f%%   %+.4f%% / %+.4f%%"
              % ("%dmin" % D, a.size, a.sum(), a.mean(), 100 * (a > 0).mean(), 100 * np.mean(sl),
                 w.mean() if w.size else 0, l.mean() if l.size else 0,
                 m1.mean() if m1.size else 0, m2.mean() if m2.size else 0))
    dev.disconnect()


if __name__ == "__main__":
    main()
