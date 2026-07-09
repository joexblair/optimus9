"""seam_arm_ab.py — arm on the s5m breach measured AT THE 5-MINUTE SEAM, not the first 5s bar. (Joe 0709)

s5m_arm currently fires on any 5s bar where the emerging s5m crosses the boundary (`sign[i] != sign[i-1]`).
A crossing that happens mid-bar and retreats before the 5-minute bar closes still arms.

Joe: measure the breach at the 5-minute emerging bar seam. Only a crossing that is still OOB when the 5m bar
turns over becomes an arm.

PREDICTION (before the run): fewer entries; median adverse excursion falls; average winner stays pinned near
+1.03% (the exit caps it); mean per trade improves but stays negative.

Baseline: 3308 entries, mean -0.1731%, win 42.1%, avgW +1.038%, stop 49.8%, MAE p50 0.895%.

Only the s5m arm is re-sampled. The s5r divergence arm is untouched. `arm_bigleg=0` (breach arm, no delay).
Monkeypatches `lr_v2.s5m_arm` for the duration — analysis only, no production change.

Read-only. Run:  python3 seam_arm_ab.py
"""
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.analysis import lr_v2
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import lr_exit_v2, v2_walk_ad
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS

SPAN_D = 42
COST = 0.20
SEAMS_MS = (None, 60_000, 150_000, 300_000)   # None = current (every 5s bar); 300000 = the 5-minute seam


def make_seam_arm(seam_ms):
    """s5m_arm evaluated only on bars that sit on a `seam_ms` boundary. seam_ms=None -> the original."""
    def s5m_arm_seam(W, cfg):
        ts = np.asarray(W.ts); hi, lo = cfg.hi, cfg.lo
        s5m = np.asarray(W.line('s5m'), float)
        sign = np.where(s5m >= hi, 1, np.where(s5m <= lo, -1, 0))
        if seam_ms is None:
            return [(i, int(sign[i]), -int(sign[i])) for i in range(1, len(ts)) if sign[i] != 0 and sign[i] != sign[i - 1]]
        k = np.flatnonzero((ts % seam_ms) == 0)               # the seam bars, in order
        out = []
        for j in range(1, len(k)):
            i, p = k[j], k[j - 1]
            if sign[i] != 0 and sign[i] != sign[p]:            # OOB at this seam, not at the previous one
                out.append((int(i), int(sign[i]), -int(sign[i])))
        return out
    return s5m_arm_seam


def score(name, W, lr, ent):
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    net, sl, mae = [], [], []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= len(px):
            continue
        seg = px[e:x + 1]
        adverse = seg.min() if bd == 1 else seg.max()
        net.append(bd * (xpx - epx) / epx * 100.0 - COST)
        sl.append(1 if reason == 'SL' else 0)
        mae.append(abs(bd * (adverse - epx) / epx * 100.0))
    a = np.asarray(net); m = np.asarray(mae)
    if a.size < 30:
        print("  %-16s n=%d (too few)" % (name, a.size)); return
    w, l = a[a > 0], a[a <= 0]
    be = 100.0 * abs(l.mean()) / (w.mean() + abs(l.mean()))
    print("  %-16s n=%-5d net=%+8.2f%%  mean=%+.4f%%  win=%4.1f%%  be=%4.1f%%  stop=%4.1f%%  avgW=%+.3f%%  avgL=%+.3f%%  MAE p50=%.3f%%"
          % (name, a.size, a.sum(), a.mean(), 100 * (a > 0).mean(), be, 100 * np.mean(sl),
             w.mean(), l.mean(), np.percentile(m, 50)))


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    print("42d · arm_bigleg=%s · cost %.2f%%\n" % (lr.arm_bigleg, COST))

    orig = lr_v2.s5m_arm
    try:
        for seam in SEAMS_MS:
            lr_v2.s5m_arm = make_seam_arm(seam)
            ent = v2_walk_ad(W, lr)
            label = "every 5s bar" if seam is None else "%d-min seam" % (seam // 60_000)
            score(label, W, lr, ent)
    finally:
        lr_v2.s5m_arm = orig
    dev.disconnect()


if __name__ == "__main__":
    main()
