"""stop_sweep_causal.py — sweep the stop width on the causal book. (Joe 0709)

lr.sl = 0.90% was swept against the LOOK-AHEAD book. On the causal book (breach arm, lp_arm_bigleg=0):
  3309 entries · mean -0.1740%/trade · win 42.1% vs 50.4% breakeven · 49.9% stop out
  avg winner +1.038%   avg loser -1.055%   MAE p50 0.895%  p90 1.015%

PREDICTION (stated before the run): the stops sit hard against the boundary (MAE p90 = 1.015% vs a 0.90%
stop). Widening to 1.1-1.3% should convert a slice of stops into signal exits and lift the mean, then degrade
once the converted losers cost more than the recovered winners. If the mean is FLAT across all widths, the loss
is not the stop's placement and no width saves this book.

The arm and the entries do not depend on sl -- only the exit does. Entries are computed once.
`sl=None` runs with the stop effectively disabled (a diagnostic ceiling, never a valid config).

Read-only. Run:  python3 stop_sweep_causal.py
"""
import copy
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
SLS = (0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 2.0, 3.0, 99.0)   # 99 = stop effectively off (ceiling, not a config)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    ent = v2_walk_ad(W, lr)
    print("42d · breach arm (arm_bigleg=%s) · %d entries · cost %.2f%%\n" % (lr.arm_bigleg, len(ent), COST))

    half = np.median([e[3] for e in ent])
    print("%-7s %6s %10s %10s %7s %8s %7s %8s   %s"
          % ("stop%", "n", "net", "mean", "win%", "be%", "stop%", "avgW", "halves (mean)"))
    for sl in SLS:
        lc = copy.copy(lr); lc.sl = sl
        net, isSL, bars = [], [], []
        for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lc, ent, predict=False):
            k = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
            if x <= k or x >= len(px):
                continue
            net.append(bd * (xpx - epx) / epx * 100.0 - COST)
            isSL.append(1 if reason == 'SL' else 0)
            bars.append(k)
        a = np.asarray(net); b = np.asarray(bars)
        w, l = a[a > 0], a[a <= 0]
        be = 100.0 * abs(l.mean()) / (w.mean() + abs(l.mean())) if w.size and l.size else float('nan')
        m1, m2 = a[b < half], a[b >= half]
        tag = "  <- stop OFF (ceiling)" if sl > 90 else ""
        print("%-7s %6d %+9.2f%% %+9.4f%% %6.1f%% %7.1f%% %6.1f%% %+7.3f%%   %+.4f%% / %+.4f%%%s"
              % ("%.2f" % sl if sl < 90 else "off", a.size, a.sum(), a.mean(), 100.0 * (a > 0).mean(), be,
                 100.0 * np.mean(isSL), w.mean() if w.size else 0,
                 m1.mean() if m1.size else 0, m2.mean() if m2.size else 0, tag))
    dev.disconnect()


if __name__ == "__main__":
    main()
