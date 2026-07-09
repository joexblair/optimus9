"""pivot_entry_ceiling.py — give the exit a PERFECT entry and see what it does with it. (Joe 0709)

Every entry-side lever has failed to move the book: 4 arm samplings, 9 stop widths, 6 entry-state filters, the
hb33 bias filter. avgW sits at +1.03% throughout. The open question is whether the deficit is entry TIMING or
the EXIT.

Joe: use swing_detect instead of the v2 entry event.

`find_pivots` confirms a high only after price falls `pct%` from it, and a low only after it rises `pct%`. A
pivot at bar j is knowable only at some bar > j. **This is a hindsight entry. It is a CEILING, never a
strategy** -- the same class as the no-stop row in the stop sweep.

Design: enter at every swing pivot, long at a Low, short at a High, and hand it to the SAME exit machine
(lr_exit_v2, same stop, same cost). Compare against the v2 book.

  If the pivot book is strongly positive -> the deficit is entry timing. The exit works.
  If the pivot book is still negative   -> the exit gives back more than a perfect entry can supply.

This also supplies the control the previous run lacked. `capture` and post-exit excursion measured at a KNOWN
turn tell us what those statistics look like when the entry is exactly right.

Read-only. Run:  python3 pivot_entry_ceiling.py
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
PCTS = (0.5, 0.9, 1.5)          # pivot confirmation thresholds
BAR_S = 5


def stats(name, W, lr, ent):
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    n = len(px)
    net, sl, mfe, cap, hold = [], [], [], [], []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= n:
            continue
        seg = px[e:x + 1]
        best = seg.max() if bd == 1 else seg.min()
        rz = bd * (xpx - epx) / epx * 100.0 - COST
        mf = abs(bd * (best - epx) / epx * 100.0)
        net.append(rz); sl.append(1 if reason == 'SL' else 0); mfe.append(mf); hold.append((x - e) * BAR_S / 60.0)
        if mf > 0.05:
            cap.append(rz / mf)
    a = np.asarray(net)
    if a.size < 30:
        print("  %-22s n=%d (too few)" % (name, a.size)); return
    w, l = a[a > 0], a[a <= 0]
    be = 100.0 * abs(l.mean()) / (w.mean() + abs(l.mean())) if w.size and l.size else float('nan')
    print("  %-22s n=%-5d net=%+9.2f%%  mean=%+.4f%%  win=%4.1f%%  be=%4.1f%%  stop=%4.1f%%  avgW=%+.3f%%  avgL=%+.3f%%"
          % (name, a.size, a.sum(), a.mean(), 100 * (a > 0).mean(), be, 100 * np.mean(sl),
             w.mean() if w.size else 0, l.mean() if l.size else 0))
    print("  %-22s MFE_in p50=%.3f%%  capture p50=%.3f  hold p50=%.1f min"
          % ("", np.percentile(mfe, 50), np.percentile(cap, 50) if cap else float('nan'), np.percentile(hold, 50)))


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    print("42d · breach arm · cost %.2f%% · stop %.2f%%\n" % (COST, lr.sl))

    print("=== the real book (v2_walk_ad entries) ===")
    stats("v2 entries", W, lr, v2_walk_ad(W, lr))

    print("\n=== HINDSIGHT CEILING: entries at swing pivots (never a strategy) ===")
    for pct in PCTS:
        piv = find_pivots(px, pct=pct)
        ent = []
        for (i, kind) in piv:
            if i <= 0 or i >= len(ts) - 1:
                continue
            bd = 1 if kind == 'L' else -1        # buy the low, sell the high
            es = -bd
            ent.append((int(ts[i]), es, bd, int(i)))
        stats("pivots pct=%.1f%%" % pct, W, lr, ent)
    dev.disconnect()


if __name__ == "__main__":
    main()
