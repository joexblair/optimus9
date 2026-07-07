"""mae_mfe_armline.py — arm-line MAE/MFE A/B for the spec redesign (Joe 0707).

NO pnl, NO arm-delay. Just: breach-arm on a chosen line → score each arm's MAE/MFE (d-signed) to the NEXT >=0.9%
swing pivot (swing_detect.find_pivots), median across arms, over the 14d window. A/B the ARM LINE: s5m vs s7m vs s10m.
Adapts s5Mage_wob_sweep.py's scorer; the only change is the arm generator is a parameterized line-breach.

MAE = worst adverse excursion (against the trade dir bd=-es) before the next swing · MFE = best favourable · lower
|MAE| = the arm lands closer to the turn · MFE/|MAE| = entry quality. Run:  python3 mae_mfe_armline.py [line ...]
"""
import sys, time, bisect
import numpy as np

import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.live.strategy import StrategyLoop
from optimus9.compute.swing_detect import find_pivots

SWING_PCT = 0.9


def line_arm(W, line_name, hi, lo):
    """Breach-arm on ANY line: OOB cross → arm; bd = -es (trade = the reversal). [(bar_i, es, bd)]. Emerging/causal."""
    L = np.asarray(W.line(line_name), float)
    sign = np.where(L >= hi, 1, np.where(L <= lo, -1, 0))
    return [(i, int(sign[i]), -int(sign[i])) for i in range(1, len(L)) if sign[i] != 0 and sign[i] != sign[i - 1]]


def main():
    lines = sys.argv[1:] or ["s5m", "s7m"]
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
    strat = StrategyLoop(dev, bm.BiasConfig(**BASE_BIAS), cfg, "FARTCOINUSDT", buffer_hours=336, warmup_hours=48)
    W = strat.window(int(time.time() * 1000)); ts = W.ts
    px = np.asarray(W.px, float)
    dev.disconnect()
    days = (int(ts[-1]) - int(ts[0])) / 86400000.0
    v0 = int(np.argmax(~np.isnan(px)))
    piv = [p[0] + v0 for p in find_pivots(px[v0:], SWING_PCT)]

    print("arm-line MAE/MFE to next >=%.1f%% swing — %dd, %d real swings (no pnl / no arm-delay)\n" % (
        SWING_PCT, round(days), len(piv)))
    print("%-6s %6s %6s %9s %9s %10s" % ("line", "n", "n/day", "MAE", "MFE", "MFE/|MAE|"))
    for ln in lines:
        try:
            arms = line_arm(W, ln, HI, LO)
        except Exception as e:
            print("%-6s  ERR (not seeded? %s)" % (ln, str(e)[:50])); continue
        maes, mfes = [], []
        for i, es, bd in arms:
            j = bisect.bisect_right(piv, int(i))
            if j >= len(piv):
                continue
            fav = bd * (px[i:piv[j] + 1] - px[i]) / px[i] * 100.0
            if fav.size:
                mfes.append(float(np.nanmax(fav))); maes.append(float(np.nanmin(fav)))
        if not maes:
            print("%-6s %6d" % (ln, len(arms))); continue
        maes, mfes = np.array(maes), np.array(mfes)
        print("%-6s %6d %6.1f %+9.3f %+9.3f %10.2f" % (
            ln, len(maes), len(maes) / days, np.median(maes), np.median(mfes),
            np.median(mfes / np.maximum(np.abs(maes), 1e-9))))


if __name__ == "__main__":
    main()
