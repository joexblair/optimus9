"""causal_arm_hold.py — SANDBOX test of a CAUSAL arm-delay (Joe 0707, milestone: real-world viability).

The current arm_delay falls back to the BREACH arm when no s5Mage reversal is found yet (`da if da is not None else i`).
That fallback is the look-ahead's twin: in a long batch window a future reversal IS found (arm delayed); in the live
short window it's NOT (arm fires early at the breach). Joe's INTENT = the Elder tide-screen: HOLD until s5Mage actually
reverses. The one change: **drop the breach-fallback** — a big-leg arm with no reversal yet produces NO trade (holds),
never fires early. That makes it causal (window-invariant) AND implements the intent.

Monkeypatch only — does NOT modify lr_v2 (sandbox the spec; integrate as a config toggle only if it earns it).
Run:  python3 causal_arm_hold.py
"""
import time
import datetime as dtm
from datetime import timezone

import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
import optimus9.analysis.lr_v2 as lr2

START, LEV, MAX_LOT, RT = 500.0, 5.0, 66000, 0.20


def arm_delay_hold(W, cfg, setups):
    """CAUSAL arm-delay: big-leg arm HOLDS until s5Mage reverses toward bd; NO breach-fallback (drop if none yet)."""
    if getattr(cfg, "arm_mode", "s5m") == "s5Mage":
        return setups
    ch, cl = lr2.bigleg_gate(W, cfg)
    rev5M = lr2._mage_rev(W.line("s5M"), cfg.arm_wob)
    out = []
    for (i, es, bd, cap, src) in setups:
        cond = ch if es == 1 else cl
        kc = next((k for k in range(i + 1, cap) if cond[k]), None)
        if kc is None:
            out.append((i, es, bd, cap, src)); continue          # not a big leg → breach arm (unchanged)
        da = next((k for k in range(kc, cap) if rev5M[k] == bd), None)
        if da is None:
            continue                                             # big leg, no reversal yet → HOLD, no trade
        out.append((da, es, bd, cap, src))                       # delay to the (real, past-at-fire) reversal


    return out


def h(ms):
    return time.strftime("%H:%M:%S", time.gmtime(int(ms) / 1000))


def entries_at(dev, lr, bcfg, end, days=None):
    lb = (days * 24 + 1) if days else 8
    W = bm.BiasWindow(dev, end, lookback=lb, warmup=(12 if days else 6), cfg=bcfg)
    lr.arm_bigleg = True
    return W, {int(e[0]) for e in lr2.v2_walk_ad(W, lr)}


def main():
    lr2.arm_delay = arm_delay_hold                               # <-- the swap (module global; v2_cascade picks it up)
    dev = DatabaseManager(**get_db_config()); dev.connect()
    bcfg = bm.BiasConfig(**BASE_BIAS)
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)

    # 1) window-invariance: the 20:42 bar that VANISHED under the old fallback — is the causal-hold set stable?
    tk = 1783370530000
    _, e_short = entries_at(dev, lr_config(dev), bcfg, tk + 5301 + 120000)
    _, e_long = entries_at(dev, lr_config(dev), bcfg, tk + 3600000)
    print("WINDOW-INVARIANCE (causal hold):")
    print("  20:42:10 in short-window? %s | in long-window? %s  (want: SAME)" % (tk in e_short, tk in e_long))

    # 2) Joe's target: does a hold-arm open near 21:10 (a s5Mage reversal)?
    W, _ = entries_at(dev, lr_config(dev), bcfg, now)
    ts = list(W.ts)
    lr = lr_config(dev); lr.arm_bigleg = True
    arms = lr2.arm_delay(W, lr, lr2.v2_arm(W, lr))               # the held/delayed arm bars
    near = [(int(ts[a[0]]), a[1], a[4]) for a in arms if abs(int(ts[a[0]]) - 1783372200000) < 300000]  # ±5min of 21:10
    print("HOLD-ARMS near 21:10:", [(h(m), es, src) for (m, es, src) in near] or "none")

    # 3) PnL: causal hold + no strand, vs the floor (arm-delay off) and the inflated (both look-aheads)
    print("PnL (10.3d):")
    def pnl(W, lr, use_hold, strand):
        lr.arm_bigleg = use_hold
        ent = lr2.v2_walk_ad(W, lr)
        ex = lr2.lr_exit_v2(W, lr, ent, predict=False)
        if strand:
            ex = lr2.strand_rescue(W, lr, ent, ex)
        resc = sorted(ex, key=lambda x: x[0]); n = len(resc)
        nets = [r - RT for (_, _, _, _, _, r, _) in resc]; wins = sum(1 for x in nets if x > 0)
        acct = START
        for (_, _, _, epx, _, r, _) in resc:
            acct += min(MAX_LOT, acct * LEV / float(epx)) * float(epx) * (r - RT) / 100.0
        return n, acct, acct / START, 100.0 * wins / n if n else 0, sum(nets) / n if n else 0
    Wp = bm.BiasWindow(dev, now, lookback=10.3 * 24 + 1, warmup=12, cfg=bcfg)
    for label, hold, st in [("CAUSAL HOLD + no strand", True, False), ("floor: breach-arm + no strand (off/off)", False, False)]:
        n, final, x, win, an = pnl(Wp, lr_config(dev), hold, st)
        print("  %-40s n=%-4d $%-7.0f %5.1fx  win %2.0f%%  avgNet %+.3f" % (label, n, final, x, win, an))


if __name__ == "__main__":
    main()
