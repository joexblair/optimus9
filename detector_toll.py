"""detector_toll.py — what do the existing causal turn-detectors cost? (Joe 0709)

Established on 42d, breach arm, same exit, cost 0.20%:
  enter at a 0.9% swing pivot (hindsight)     mean +0.7071%
  enter at that pivot's confirmation (legal)  mean -0.2246%   toll = the 0.930% price penalty
  enter at the v2 arm                         mean -0.1745%   24 min early, 0.7% worse price
  enter at v2 arm + fixed delay D             flat, best at D=0. A constant cannot find the turn.

Every causal turn-detector waits for the turn to prove itself, and pays a toll in price. This measures the toll
of the detectors already in the codebase, two ways:

  (1) BOOK    -- build entries from each detector's fires and score them through lr_exit_v2.
  (2) TOLL    -- for each 0.9% pivot, the first fire of that detector at/after the pivot: lag, price penalty.

PREDICTION (before the run): every detector lands near -0.2%, the same fixed toll as pivot confirmation,
because they all require the turn to prove itself. If one is clearly positive it is finding the turn before the
price has to pay for it.

Detectors (all causal, all already in lr_v2):
  s5m rev wob{2,7}   s5M rev wob{1,2,7}   s2M rev wob1   s5r coarse-curl 40s   s7r coarse-curl 105s

Read-only. Run:  python3 detector_toll.py
"""
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import _mage_rev, coarse_curl, lr_exit_v2
from optimus9.compute.swing_detect import find_pivots
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS

SPAN_D = 42
COST = 0.20
BAR_S = 5
PIVOT_PCT = 0.9


def fires_from_rev(rev):
    """rev: +1 up-turn / -1 down-turn per bar -> [(bar, bd)] with bd = the direction of the new leg."""
    k = np.flatnonzero(rev != 0)
    return [(int(i), int(rev[i])) for i in k]


def fires_from_curl(ts, line, seam_ms):
    """coarse_curl fires one seam after a turn. Trough(+1) -> long; peak(-1) -> short."""
    out = []
    for direction, bd in ((1, 1), (-1, -1)):
        hits = coarse_curl(ts, line, seam_ms, direction)
        out += [(int(np.searchsorted(ts, t)), bd) for t in hits]
    return sorted(out)


def score(name, W, lr, fires, ts, px):
    n = len(px)
    ent, seen = [], set()
    for (k, bd) in fires:
        if 0 < k < n - 1 and k not in seen:
            seen.add(k); ent.append((int(ts[k]), -bd, bd, k))
    net, sl = [], []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= n:
            continue
        net.append(bd * (xpx - epx) / epx * 100.0 - COST); sl.append(1 if reason == 'SL' else 0)
    a = np.asarray(net)
    if a.size < 30:
        print("  %-22s n=%-5d (too few)" % (name, a.size)); return
    w, l = a[a > 0], a[a <= 0]
    print("  %-22s n=%-5d net=%+9.2f%%  mean=%+.4f%%  win=%4.1f%%  stop=%4.1f%%  avgW=%+.3f%%  avgL=%+.3f%%"
          % (name, a.size, a.sum(), a.mean(), 100 * (a > 0).mean(), 100 * np.mean(sl),
             w.mean() if w.size else 0, l.mean() if l.size else 0))


def toll(name, fires, piv, px):
    """For each pivot, the first same-direction fire at/after it: lag (min) and price penalty (%)."""
    by = {1: np.array(sorted(k for k, bd in fires if bd == 1)),
          -1: np.array(sorted(k for k, bd in fires if bd == -1))}
    lag, pen = [], []
    for (i, kind) in piv:
        bd = 1 if kind == 'L' else -1
        arr = by.get(bd)
        if arr is None or not arr.size:
            continue
        j = int(np.searchsorted(arr, i))
        if j >= arr.size:
            continue
        k = int(arr[j])
        if (k - i) * BAR_S > 3600:            # no fire within an hour of the pivot
            continue
        lag.append((k - i) * BAR_S / 60.0)
        pen.append(bd * (px[k] - px[i]) / px[i] * 100.0)   # + = worse than the pivot price
    if len(lag) < 20:
        print("  %-22s matched %d pivots (too few)" % (name, len(lag))); return
    print("  %-22s matched %4d/%d pivots   lag p50=%5.1f min  p90=%5.1f min   penalty p50=%+.3f%%  p90=%+.3f%%"
          % (name, len(lag), len(piv), np.percentile(lag, 50), np.percentile(lag, 90),
             np.percentile(pen, 50), np.percentile(pen, 90)))


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    s5m, s5M, s2M = (np.asarray(W.line(x), float) for x in ('s5m', 's5M', 's2M'))
    s5r, s7r = (np.asarray(W.line(x), float) for x in ('s5r', 's7r'))
    piv = [(i, k) for (i, k) in find_pivots(px, pct=PIVOT_PCT)]
    print("42d · %d pivots at %.1f%% · cost %.2f%% · stop %.2f%%\n" % (len(piv), PIVOT_PCT, COST, lr.sl))

    dets = [("s5m rev wob2", fires_from_rev(_mage_rev(s5m, 2))),
            ("s5m rev wob7", fires_from_rev(_mage_rev(s5m, 7))),
            ("s5M rev wob1", fires_from_rev(_mage_rev(s5M, 1))),
            ("s5M rev wob2", fires_from_rev(_mage_rev(s5M, 2))),
            ("s5M rev wob7", fires_from_rev(_mage_rev(s5M, 7))),
            ("s2M rev wob1", fires_from_rev(_mage_rev(s2M, 1))),
            ("s5r curl 40s", fires_from_curl(ts, s5r, 40_000)),
            ("s7r curl 105s", fires_from_curl(ts, s7r, 105_000))]

    print("=== BOOK: enter at every fire ===")
    for (nm, f) in dets:
        score(nm, W, lr, f, ts, px)
    print("\n=== TOLL vs the 0.9%% pivots (reference: confirmation lag 7.4 min, penalty +0.930%%) ===")
    for (nm, f) in dets:
        toll(nm, f, piv, px)
    dev.disconnect()


if __name__ == "__main__":
    main()
