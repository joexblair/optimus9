"""s5Mage_wob_sweep.py (Joe 0705) — sweep the s5Mage arm wob under the CORRECTED wob_no_fire_latch.

wob_no_fire_latch (Joe's spec): latch OPENS on an OOB breach; CLOSES (arm fires) on the first wob signal =
`wob` sequential 5s bars that do NOT print a higher value than the prior bar (hi-breach → non-increasing) /
NOT lower (lo-breach → non-decreasing). Same value COUNTS; only a contrary print resets the count. One arm
per breach (the first wob signal). Fixes the unbounded-latch bleed (arm firing mid-board 16min post-breach).

Scores each arm MAE/MFE (d-signed) to the next >=0.9% swing pivot (swing_detect), last 14 days, EMERGING.
"""
import sys, time, bisect
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.live.strategy import StrategyLoop
from optimus9.compute.swing_detect import find_pivots
from optimus9.analysis.lr_v2 import s5Mage_arm

dev = DatabaseManager(**get_db_config()); dev.connect()
cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
strat = StrategyLoop(dev, bm.BiasConfig(**BASE_BIAS), cfg, 'FARTCOINUSDT', buffer_hours=336, warmup_hours=48)
W = strat.window(int(time.time() * 1000)); ts = W.ts
px = np.asarray(W.px, float)
dev.disconnect()
days = (int(ts[-1]) - int(ts[0])) / 86400000.0
v0 = int(np.argmax(~np.isnan(px)))
piv = [p[0] + v0 for p in find_pivots(px[v0:], 0.9)]


def arms_for(wob):
    """The ENGINE's s5Mage_arm (two-wob latch) at this wob — single source, sweep == engine."""
    cfg.arm_wob = wob
    return s5Mage_arm(W, cfg)


print('s5Mage arm — TWO-wob latch (breach-confirm + reversal), %dd, %d real swings\n' % (round(days), len(piv)))
print('%-4s %8s %7s %8s %8s %9s' % ('wob', 'n', 'n/day', 'MAE', 'MFE', 'MFE/|MAE|'))
for wob in range(0, 13):
    maes, mfes = [], []
    for i, es, bd in arms_for(wob):
        j = bisect.bisect_right(piv, int(i))
        if j >= len(piv):
            continue
        fav = bd * (px[i:piv[j] + 1] - px[i]) / px[i] * 100.0
        mfes.append(float(np.nanmax(fav))); maes.append(float(np.nanmin(fav)))
    if not maes:
        print('%-4d %8d' % (wob, 0)); continue
    maes, mfes = np.array(maes), np.array(mfes)
    print('%-4d %8d %7.1f %+8.3f %+8.3f %9.2f' % (
        wob, len(maes), len(maes) / days, np.median(maes), np.median(mfes),
        np.median(mfes / np.maximum(np.abs(maes), 1e-9))))
