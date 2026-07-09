"""risk_stack_dist.py — derive the total-exposure cap from the SHIPPING stack's pyramid distribution (Joe 0708).

Replays v2_walk_ad entries + strand_rescue exits through the one-way open/add/close model (mirrors
MatchingEngine's arithmetic, but writes NOTHING — SAFE against the live o9_live.fx_* tables), tracking the
peak net-exposure as a MULTIPLE of live equity per pyramid episode. Reports the distribution so the cap clips
the runaway tail (the ~40x peak) without clipping the productive body. One-way here → a FLOOR for hedge mode
(hedge adds the currently-skipped opposite legs); re-derive from a hedge replay once built. Run: python3 risk_stack_dist.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue

SPAN_D = 30
START, LEV, MAX_LOT, COST = 500.0, 5.0, 66000, 0.20   # match v2walk_ad_pnl (the shipping compounding model)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ent = v2_walk_ad(W, lr)
    exd = {x[0]: x for x in strand_rescue(W, lr, ent, lr_exit_v2(W, lr, ent, predict=False))}

    events = []                                        # (t, kind, bd, price) — mirrors replay.py's event build
    for e in ent:
        tms, bd = int(e[0]), int(e[2])
        x = exd.get(tms)
        if x is None:
            continue
        events.append((tms, "open", bd, float(x[3])))
        events.append((int(x[1]), "close", bd, float(x[4])))
    events.sort(key=lambda e: e[0])

    equity = START
    net_sz = net_avg = 0.0; net_side = 0; peak_mult = 0.0; adds = 0
    peaks, add_counts = [], []
    for (t, kind, bd, price) in events:
        if kind == "open":
            if net_sz > 0 and bd != net_side:
                continue                               # opposite side while holding — one-way skip (hedge will NOT)
            lot = min(MAX_LOT, equity * LEV / price)
            if net_sz == 0:
                net_side, net_avg, net_sz, adds = bd, price, lot, 1
            else:
                net_avg = (net_avg * net_sz + price * lot) / (net_sz + lot); net_sz += lot; adds += 1
            peak_mult = max(peak_mult, net_sz * price / equity)
        elif net_sz > 0:                               # close the net on first exit while holding
            ret = (price - net_avg) / net_avg * 100.0 * net_side
            equity = max(equity + net_sz * net_avg * (ret - COST) / 100.0, 1e-6)
            peaks.append(peak_mult); add_counts.append(adds)
            net_sz = net_avg = 0.0; net_side = 0; peak_mult = 0.0; adds = 0

    peaks, ac = np.array(peaks), np.array(add_counts)
    print("=== v2_walk_ad pyramid stack distribution (%d episodes, %dd, $%d @ %gx, MAX_LOT %d) ===" %
          (len(peaks), SPAN_D, START, LEV, MAX_LOT))
    print("peak GROSS exposure (x equity):")
    for p in (50, 75, 90, 95, 99):
        print("  p%-3d = %6.1fx" % (p, np.percentile(peaks, p)))
    print("  max  = %6.1fx    mean = %.1fx" % (peaks.max(), peaks.mean()))
    print("pyramid depth (adds/episode):")
    for p in (50, 90, 95, 99):
        print("  p%-3d = %4.1f" % (p, np.percentile(ac, p)))
    print("  max  = %d    single-leg episodes = %.0f%%" % (ac.max(), 100 * np.mean(ac == 1)))
    print("\nCAP CANDIDATES: p95 = %.1fx  p99 = %.1fx  (body up to p90 = %.1fx; tail max = %.1fx)" %
          (np.percentile(peaks, 95), np.percentile(peaks, 99), np.percentile(peaks, 90), peaks.max()))
    dev.disconnect()


if __name__ == "__main__":
    main()
