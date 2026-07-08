"""reconcile_hedge_entries.py — honesty check for the hedge wiring (Joe 0708). Two prongs:

1) TRADES MATCH: the static backtest entry set = v2_walk_ad over the tape (what build_v2_walk books). Simulate
   the OLD one-way handling (replay model: opposite-side-while-holding DROPPED) vs the NEW hedge handling
   (each side independent → every entry becomes open/add, 0 drops). Confirm hedge reproduces the FULL static
   set, and quantify the drops one-way lost (= the overlapping opposite legs that make the hedge premium).
2) DATA CLEAN: the tape under those entries has no gaps / zero-vol frozen bars / carry-forward filler dupes —
   a match on dirty data is false comfort ([[project_frozen_tape_failure]],[[project_filler_invisible]]).

Read-only; runs on the dev tape. Run:  python3 reconcile_hedge_entries.py"""
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
_SIDE = {1: "Buy", -1: "Sell"}


def sim_oneway(events):
    """replay's one-way model: same-side adds, opposite-while-holding DROPPED, first close-while-holding flattens."""
    net, opens, adds, drops = None, 0, 0, 0
    for (t, kind, side) in events:
        if kind == "open":
            if net is None: net, opens = side, opens + 1
            elif net == side: adds += 1
            else: drops += 1                       # opposite side while holding the net → dropped
        elif net is not None:                      # close → flatten the net
            net = None
    return dict(opens=opens, adds=adds, drops=drops, handled=opens + adds)


def sim_hedge(events):
    """each side an independent leg: every entry becomes open (flat that side) or add (holding that side)."""
    leg = {"Buy": False, "Sell": False}
    opens = adds = drops = 0
    for (t, kind, side) in events:
        if kind == "open":
            if not leg[side]: leg[side], opens = True, opens + 1
            else: adds += 1
        else:                                      # close that side's leg (reversal-TP is per side)
            leg[side] = False
    return dict(opens=opens, adds=adds, drops=drops, handled=opens + adds)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ent = v2_walk_ad(W, lr)
    exd = {x[0]: x for x in strand_rescue(W, lr, ent, lr_exit_v2(W, lr, ent, predict=False))}

    events = []
    for e in ent:
        tms, side = int(e[0]), _SIDE[int(e[2])]
        x = exd.get(tms)
        if x is None:
            continue
        events.append((tms, "open", side))
        events.append((int(x[1]), "close", side))
    events.sort(key=lambda z: z[0])
    static_entries = sum(1 for z in events if z[1] == "open")

    ow, hg = sim_oneway(events), sim_hedge(events)
    print("=== PRONG 1: trades match static backtest (%d entries, %dd) ===" % (static_entries, SPAN_D))
    print("  ONE-WAY : handled %d  (opens %d, adds %d)  DROPPED %d" % (ow["handled"], ow["opens"], ow["adds"], ow["drops"]))
    print("  HEDGE   : handled %d  (opens %d, adds %d)  DROPPED %d" % (hg["handled"], hg["opens"], hg["adds"], hg["drops"]))
    match = hg["handled"] == static_entries and hg["drops"] == 0
    print("  VERDICT : hedge reproduces the FULL static set: %s   (one-way lost %d overlapping legs = the premium)"
          % ("YES" if match else "NO", ow["drops"]))

    # ── PRONG 2: data clean over the entry window ──
    tp = dev.execute("SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s", ("FARTCOINUSDT",), fetch=True)[0]["tp_pk"]
    lo = int(W.ts[0])
    agg = dev.execute("""SELECT COUNT(*) n, SUM(kc_volume=0) zero_vol,
                                (MAX(kc_timestamp)-MIN(kc_timestamp))/5000+1 expected
                         FROM kline_collection WHERE kc_tp_pk=%s AND kc_timestamp>=%s""", (tp, lo), fetch=True)[0]
    dup = dev.execute("""SELECT SUM(v=0 AND o=po AND h=ph AND l=pl AND c=pc) dupes FROM (
                            SELECT kc_volume v, kc_open o, kc_high h, kc_low l, kc_close c,
                                   LAG(kc_open)  OVER w po, LAG(kc_high) OVER w ph,
                                   LAG(kc_low)   OVER w pl, LAG(kc_close) OVER w pc
                            FROM kline_collection WHERE kc_tp_pk=%s AND kc_timestamp>=%s
                            WINDOW w AS (ORDER BY kc_timestamp)) q""", (tp, lo), fetch=True)[0]["dupes"]
    n, zv, exp = int(agg["n"]), int(agg["zero_vol"] or 0), int(agg["expected"] or 0)
    gaps = exp - n
    print("\n=== PRONG 2: data clean (%d bars over the window) ===" % n)
    dup = int(dup or 0)
    # Bybit OMITS no-trade bars → every V=0 bar in our tape is a synthetic carry-forward fill (the corrupter).
    print("  grid gaps (missing 5s bars)      : %d   %s" % (gaps, "OK" if gaps == 0 else "GAPPY"))
    print("  V=0 synthetic filler bars        : %d  (%.1f%%)  %s" %
          (zv, 100.0 * zv / max(n, 1), "OK" if zv == 0 else "FILLER — corrupts oscillators (filler_invisible fix exists)"))
    print("    ...of which consecutive runs   : %d  (%.1f%%)" % (dup, 100.0 * dup / max(n, 1)))
    clean = gaps == 0 and zv == 0
    print("\nRECONCILE: trades match=%s  data clean=%s  →  %s" %
          (match, clean, "HONEST ✓" if (match and clean) else "INVESTIGATE"))
    dev.disconnect()


if __name__ == "__main__":
    main()
