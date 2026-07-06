"""backtest_pnl.py — the v2_walk_ad PnL summary, to confirm o9-live and the backtest read the SAME data (Joe 0707).

Runs the shipping stack (v2_walk_ad · s5m arm · lr_exit_v2 predict=False · strand_rescue) over a WINDOW ending now,
with o9-live's EXACT config (BASE_BIAS + lr_config). Reports Joe's format: FULL (compounding dynamic-5x) + wins +
avgNet%/trade, SINGLE-POSITION (one-at-a-time), and same-side/opposite overlap counts. Also asserts px == bar close
(the causal hinge: entries/exits taken at px[bar]; a non-close px would be look-ahead). NO 5301 here — that offset is
only in o9-live's state_log labeling; the backtest steps bar-by-bar on closes.

Run:  python3 backtest_pnl.py [days]     (default 10.3)
"""
import sys
import datetime as dtm
from datetime import timezone

import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue

SYM = "FARTCOINUSDT"
START = 500.0
LEV = 5.0
MAX_LOT = 66000
RT_COST = 0.20          # % round-trip est (fees+slip); real comes from o9-live


def main():
    days = float(sys.argv[1]) if len(sys.argv) > 1 else 10.3
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    cfg = bm.BiasConfig(**BASE_BIAS)
    lookback_h = days * 24 + 1
    W = bm.BiasWindow(dev, now, lookback=lookback_h, warmup=12, cfg=cfg)
    lrcfg = lr_config(dev)

    # --- purity hinge: px must be the bar close ---
    tp = dev.execute("SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s", (SYM,), fetch=True)[0]["tp_pk"]
    last_close = dev.execute("SELECT kc_close c FROM kline_collection WHERE kc_tp_pk=%s AND kc_timestamp=%s",
                             (tp, int(W.ts[-1])), fetch=True)
    if last_close:
        d = abs(float(W.px[-1]) - float(last_close[0]["c"]))
        print("px==close check: |W.px[-1]-kc_close|=%.8f  -> %s" % (d, "CLOSE (causal)" if d < 1e-6 else "NOT close!"))

    ent = v2_walk_ad(W, lrcfg)
    resc = sorted(strand_rescue(W, lrcfg, ent, lr_exit_v2(W, lrcfg, ent, predict=False)), key=lambda x: x[0])

    span_d = (int(W.ts[-1]) - int(W.ts[0])) / 8.64e7
    n = len(resc)
    nets = [r - RT_COST for (_, _, _, _, _, r, _) in resc]
    wins = sum(1 for x in nets if x > 0)

    # FULL — compounding dynamic-5x (survival sizing: losses shrink the next lot)
    acct = START
    for (tms, exms, bd, epx, xpx, r, reason) in resc:
        lot = min(MAX_LOT, acct * LEV / float(epx))
        acct += lot * float(epx) * (r - RT_COST) / 100.0
    full_x = acct / START

    # SINGLE-POSITION — one position at a time (skip any entry while a position is open); classify the rest
    single = same_side = opp_side = 0
    open_until = -1; open_bd = 0; sacct = START
    for (tms, exms, bd, epx, xpx, r, reason) in resc:
        if int(tms) > open_until:                         # flat -> take it (single-position trade)
            single += 1
            lot = min(MAX_LOT, sacct * LEV / float(epx)); sacct += lot * float(epx) * (r - RT_COST) / 100.0
            open_until = int(exms); open_bd = bd
        elif bd == open_bd:
            same_side += 1                                 # same-side add = Bybit auto-pyramid
        else:
            opp_side += 1                                  # opposite-side overlap (needs hedge mode)
    single_x = sacct / START

    print("v2_walk_ad · s5m arm · %.1fd window ending now  (actual span %.1fd, %d bars)" % (days, span_d, len(W.ts)))
    print("  FULL:            n=%d   $%.0f -> $%.0f  (%.1fx)  win %.0f%%  avgNet %+.3f%%/trade" % (
        n, START, acct, full_x, 100.0 * wins / n, sum(nets) / n))
    print("  SINGLE-POSITION: n=%d            (%.1fx)  win --   [no overlap/pyramid]" % (single, single_x))
    print("  same-side overlaps (Bybit auto-pyramid adds): %d of %d   (opposite-side overlaps: %d)" % (
        same_side, n, opp_side))


if __name__ == "__main__":
    main()
