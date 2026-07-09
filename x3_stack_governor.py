"""x3_stack_governor.py — X3: stack-close x first-leg governor, 2x2, tol swept. (register Part 3)

Thesis is pre-registered in docs/causal_lookahead_register.md. Do not read the outcome back into it.

  per-leg    each entry gets its OWN exit bar        <- what v2_walk prices today (fiction: E1)
  stack-close one reversal exit closes the side's    <- what live does, because Bybit hedge mode holds
              whole averaged position                   ONE position per positionIdx

  governor   a pyramid leg is allowed only FURTHER ALONG THE LEG than the side's FIRST entry (Joe),
             tol% tolerance for retests. tol swept; winner -> risk_config.pyramid_tol_pct.

Unit notional per leg (=1.0), equal qty, so realized PnL reads as leg-return units and the averaging
arithmetic is exact. Fees 5.5bps/side (taker), matching replay.py. NOT a live-realizable PnL: no slippage,
no order-book walk, no compounding. It measures STACK SEMANTICS and the GOVERNOR, one variable at a time.

strand_rescue excluded: it is gated on the completed SL (it IS on the live path, register B3-corrected, but it
is hindsight and would confound the stack question).

Run:  python3 x3_stack_governor.py
"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.live.risk import leg_further_along
from optimus9.live.stack_model import PositionStack
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2

SPAN_D = 42
FEE_BPS = 5.5
TOLS = (0.0, 0.05, 0.10, 0.20, 0.30)


def run(trades, stack_close: bool, tol: float | None):
    """trades: [(e_bar, x_bar, bd, e_px, x_px)] sorted by e_bar. tol=None -> governor off."""
    ev = []
    for (eb, xb, bd, epx, xpx) in trades:
        ev.append((eb, 0, bd, epx))          # 0 = open  (opens before closes on the same bar)
        ev.append((xb, 1, bd, xpx))          # 1 = close
    ev.sort(key=lambda e: (e[0], e[1]))

    st = PositionStack(fee_bps=FEE_BPS)
    live = {1: 0, -1: 0}                     # per-side count of entries not yet closed (per-leg mode)
    blocked = opens = closes = 0
    depth_max = 0
    for (bar, kind, bd, px) in ev:
        if kind == 0:
            p = st.get(bd)
            if p is not None:                                     # this is a pyramid ADD
                if tol is not None and not leg_further_along(bd, p.first_px, px, tol):
                    blocked += 1
                    continue
            st.add(bd, px, 1.0)
            live[bd] += 1
            opens += 1
            depth_max = max(depth_max, st.get(bd).n_adds)
        else:
            p = st.get(bd)
            if p is None:
                continue                                          # its open was governor-blocked
            if stack_close:
                st.close(bd, px)                                  # ONE signal closes the whole side
                live[bd] = 0
                closes += 1
            else:
                st.close(bd, px, qty=1.0)                         # per-leg: retire one unit at its own exit
                live[bd] = max(0, live[bd] - 1)
                closes += 1
    return dict(net=st.realized, opens=opens, closes=closes, blocked=blocked, depth_max=depth_max)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts = np.asarray(W.ts)
    ent = v2_walk_ad(W, lr)
    trades = []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        eb, xb = int(np.searchsorted(ts, int(tms))), int(np.searchsorted(ts, int(exms)))
        if xb > eb:
            trades.append((eb, xb, int(bd), float(epx), float(xpx)))
    trades.sort()
    print("X3 · %dd · %d trades · fee %.1fbps/side · unit notional (NOT a live PnL)\n" % (SPAN_D, len(trades), FEE_BPS))

    print("%-14s %-8s %10s %8s %8s %8s %7s" % ("exit model", "tol%", "net(units)", "opens", "closes", "blocked", "depth"))
    base = {}
    for sc in (False, True):
        label = "stack-close" if sc else "per-leg"
        for tol in (None,) + TOLS:
            r = run(trades, sc, tol)
            if tol is None:
                base[sc] = r['net']
            d = "" if tol is None else "  (%+.2f vs no-gov)" % (r['net'] - base[sc])
            print("%-14s %-8s %10.3f %8d %8d %8d %7d%s"
                  % (label, "off" if tol is None else "%.2f" % tol, r['net'], r['opens'], r['closes'],
                     r['blocked'], r['depth_max'], d))
        print()

    print("stack-close COST vs per-leg (governor off): %+.3f units (%.1f%%)"
          % (base[True] - base[False], 100.0 * (base[True] - base[False]) / abs(base[False]) if base[False] else 0))
    dev.disconnect()


if __name__ == "__main__":
    main()
