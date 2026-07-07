"""causal_pnl.py — re-test the v2 PnL with look-ahead REMOVED (Joe 0707, milestone: real-world viability).

The 45x backtest carried two look-aheads: ARM-DELAY (arm pushed to a future s5Mage reversal — window-end-bounded
forward scan) and STRAND_RESCUE (exit keyed off the future SL bar). Both inflate; neither is realizable by a causal
engine. This runs the 2x2 attribution over one window so we can see how much each look-ahead was worth:

    arm_delay(on=look-ahead / off=causal-breach-arm)  x  strand(on=look-ahead / off=causal-exit)
      on/on   = the inflated 45x (both look-aheads)
      on/off  = arm-delay's inflated entry contribution
      off/on  = strand's exit contribution
      off/off = the REALIZABLE floor (no look-ahead) — the honest number, sans arm-delay

NOTE: arm-delay CAN be causal per-bar (delay to the reversal as it happens) — that needs a walk-forward and is NOT in
this 2x2 (a batch arm_delay=on is look-ahead). off/off is the floor; the per-bar causal-arm-delay is the next build.

Run:  python3 causal_pnl.py [days]   (default 10.3)
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
START, LEV, MAX_LOT, RT = 500.0, 5.0, 66000, 0.20


def run(W, lr, arm_delay, strand):
    lr.arm_bigleg = arm_delay                         # ON = look-ahead forward scan · OFF = breach arm (causal)
    ent = v2_walk_ad(W, lr)
    ex = lr_exit_v2(W, lr, ent, predict=False)
    if strand:
        ex = strand_rescue(W, lr, ent, ex)            # ON = future-SL rescue (look-ahead) · OFF = causal base exit
    resc = sorted(ex, key=lambda x: x[0])
    n = len(resc)
    nets = [r - RT for (_, _, _, _, _, r, _) in resc]
    wins = sum(1 for x in nets if x > 0)
    acct = START
    for (_, _, _, epx, _, r, _) in resc:
        acct += min(MAX_LOT, acct * LEV / float(epx)) * float(epx) * (r - RT) / 100.0
    return n, acct, acct / START, 100.0 * wins / n if n else 0, sum(nets) / n if n else 0


def main():
    days = float(sys.argv[1]) if len(sys.argv) > 1 else 10.3
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    W = bm.BiasWindow(dev, now, lookback=days * 24 + 1, warmup=12, cfg=bm.BiasConfig(**BASE_BIAS))
    span_d = (int(W.ts[-1]) - int(W.ts[0])) / 8.64e7
    print("v2 PnL look-ahead attribution — %.1fd window (%d bars)  cost=%g%% RT  L=%gx compounding\n" % (
        span_d, len(W.ts), RT, LEV))
    print("  %-34s  n     $final    x      win%%   avgNet%%" % "variant")
    rows = [("on/on   INFLATED (both look-aheads)", True, True),
            ("on/off  arm-delay look-ahead only", True, False),
            ("off/on  strand look-ahead only", False, True),
            ("off/off CAUSAL FLOOR (no look-ahead)", False, False)]
    for label, ad, st in rows:
        lr = lr_config(dev)
        n, final, x, win, avgnet = run(W, lr, ad, st)
        print("  %-34s  %-4d  $%-7.0f  %5.1fx  %4.0f%%  %+6.3f" % (label, n, final, x, win, avgnet))


if __name__ == "__main__":
    main()
