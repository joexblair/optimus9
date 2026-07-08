"""ab_filler_entries.py — does filler_invisible change the ENTRIES? A/B OFF vs ON, on BOTH paths separately
(Joe 0708): the BACKTEST config (full 30d window) and the o9/LIVE config (8h buffer / 6h warmup — the loop's
actual params). filler_invisible is a BiasWindow param, so the only thing that varies is the fix. If the entry
sets are identical, the 2.7% synthetic filler doesn't reach the entries → park it; if they diverge, the premium
math wants re-running on the clean tape. Read-only. Run:  python3 ab_filler_entries.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_walk_ad

_SIDE = {1: "Buy", -1: "Sell"}


def entries(dev, lr, now, lookback, warmup, filler):
    W = bm.BiasWindow(dev, now, lookback=lookback, warmup=warmup, cfg=bm.BiasConfig(**BASE_BIAS),
                      lean=True, filler_invisible=filler)
    return {(int(e[0]), _SIDE[int(e[2])]) for e in v2_walk_ad(W, lr)}, int(W.ts[0])


def ab(dev, lr, now, lookback, warmup, label):
    off, lo = entries(dev, lr, now, lookback, warmup, False)
    on, _ = entries(dev, lr, now, lookback, warmup, True)
    lo = max(lo, min((t for t, _ in off | on), default=lo))
    added = on - off                                       # entries the fix INTRODUCED
    removed = off - on                                     # entries the fix REMOVED
    off_ms = {t: s for t, s in off}; on_ms = {t: s for t, s in on}
    flips = {t for t in (off_ms.keys() & on_ms.keys()) if off_ms[t] != on_ms[t]}   # same bar, side flipped
    span_h = (now - lo) / 3600000.0
    print("=== %s  (%.0fh, filler OFF vs ON) ===" % (label, span_h))
    print("  entries OFF=%d  ON=%d   added=%d  removed=%d  side-flips=%d" %
          (len(off), len(on), len(added), len(removed), len(flips)))
    same = not added and not removed and not flips
    print("  VERDICT: %s" % ("IDENTICAL — filler does not reach entries" if same
                             else "DIVERGES — %.1f%% of OFF entries changed" % (100.0 * (len(added) + len(removed) + len(flips)) / max(len(off), 1))))
    return same


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    lr = lr_config(dev)
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    bt = ab(dev, lr, now, 30 * 24, 48, "BACKTEST path (30d full window)")
    o9 = ab(dev, lr, now, 8, 6, "o9/LIVE path (8h buffer / 6h warmup)")
    print("\nSUMMARY: backtest %s | o9 %s" %
          ("clean-invariant" if bt else "AFFECTED", "clean-invariant" if o9 else "AFFECTED"))
    dev.disconnect()


if __name__ == "__main__":
    main()
