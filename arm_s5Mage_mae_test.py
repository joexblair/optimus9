"""arm_s5Mage_mae_test.py (Joe 0705) — quick MAE/MFE test: arm on s5Mage REVERSAL.

Question: is a non-delayed arm = s5Mage reversing a good entry? Config s5Mage = 37|0.70|ohlc4 (300s),
EMERGING/causal. For each s5Mage slope-reversal (dir = up→long / down→short) ride to the next real
≥0.9% swing pivot (swing_detect.find_pivots) and measure d-signed MAE/MFE. Last 14 days.
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.analysis.lr import lr_config
from optimus9.compute.swing_detect import find_pivots

dev = DatabaseManager(**get_db_config()); dev.connect()
_lc = lr_config(dev); HI, LO = _lc.hi, _lc.lo    # OOB boundary (85/15)
now = int(time.time() * 1000)
OV = {'s5M': (300, ('bb', 37, 0.70, 'ohlc4'), 'emerging')}   # override mult 0.83->0.70
W = bm.BiasWindow(dev, now, lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS),
                  line_overrides=OV, lean=True)
s5M = np.asarray(W.line('s5M'), float)
px = np.asarray(W.px, float)
ts = W.ts
print('window %s -> %s  (%d bars)' % (
    time.strftime('%m-%d %H:%M', time.gmtime(int(ts[0]) / 1000)),
    time.strftime('%m-%d %H:%M', time.gmtime(int(ts[-1]) / 1000)), len(ts)))

import bisect
v0 = int(np.argmax(~np.isnan(px)))           # first non-nan (find_pivots chokes on leading NaN)
piv = [p[0] + v0 for p in find_pivots(px[v0:], 0.9)]   # real >=0.9% swing pivots (full-array index)
print('\ns5Mage(37|0.70|ohlc4) reversal as ARM — OOB-GATED (rev only counts off an extreme, HI=%g/LO=%g)' % (HI, LO))
print('scored to next >=0.9%% pivot — 14d, %d real swings\n' % len(piv))
print('%-5s %8s %9s %9s %9s %9s %10s' % ('wob', 'n', 'MAE_med', 'MFE_med', 'MFE/|MAE|', 'clean%<.33', 'dist_med_s'))
for wob in (0, 2, 4, 6, 8, 10):
    rev = _mage_rev(s5M, wob)                 # +1 up(long) / -1 down(short); wob = confirm bars
    rev = np.where((rev == 1) & (s5M <= LO), 1,          # up-turn OFF an OOB-low  -> LONG
                   np.where((rev == -1) & (s5M >= HI), -1, 0))  # down-turn OFF an OOB-high -> SHORT
    maes, mfes, dists = [], [], []
    for i in np.flatnonzero(rev):
        d = int(rev[i]); entry = float(px[i])
        j = bisect.bisect_right(piv, int(i))
        if j >= len(piv):
            continue
        fav = d * (px[i:piv[j] + 1] - entry) / entry * 100.0
        mfes.append(float(np.nanmax(fav))); maes.append(float(np.nanmin(fav)))
        k = bisect.bisect_left(piv, int(i))
        dists.append(min([abs(int(i) - piv[x]) for x in (k - 1, k) if 0 <= x < len(piv)] or [0]) * 5)
    if not maes:
        print('%-5d %8d' % (wob, 0)); continue
    maes, mfes = np.array(maes), np.array(mfes)
    print('%-5d %8d %+8.3f %+8.3f %9.2f %9d%% %10d' % (
        wob, len(maes), np.median(maes), np.median(mfes),
        np.median(mfes / np.maximum(np.abs(maes), 1e-9)),
        round(100 * (maes > -0.33).mean()), int(np.median(dists))))
dev.disconnect()
