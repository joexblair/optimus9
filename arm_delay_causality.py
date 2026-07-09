"""arm_delay_causality.py — is arm_delay look-ahead? (Joe 0709)

arm_delay re-times each arm by forward-scanning [i+1, cap) for the big-leg gate (kc), then [kc, cap) for the
s5Mage reversal (da). The suspicion (from the code): when a scan returns None it had to read ALL of [.., cap) —
and `cap = min(next opposite breach, i+horizon)` can extend well PAST the eventual trade bar tk. If the scan end
exceeds tk, the entry at tk was decided using bars AFTER tk = look-ahead (in the full-window backtest).

Per entry we compute scan_end (the furthest bar arm_delay had to read for that setup's verdict) and compare to
the trade bar tk. Reports the fraction of entries whose verdict required future bars. Read-only.
Run:  python3 arm_delay_causality.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_arm, v2_cascade, bigleg_gate, _mage_rev

SPAN_D = 42


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    print("arm_bigleg =", lr.arm_bigleg, "(1 => arm_delay ACTIVE in the producer)")

    setups0 = v2_arm(W, lr)                                  # arms BEFORE arm_delay
    ch, cl = bigleg_gate(W, lr)
    rev5M = _mage_rev(np.asarray(W.line('s5M'), float), lr.arm_wob)

    # replicate arm_delay, recording how far each verdict had to scan
    recs = []
    for (i, es, bd, cap, src) in setups0:
        cond = ch if es == 1 else cl
        kc = next((k for k in range(i + 1, cap) if cond[k]), None)
        da = None
        if kc is not None:
            da = next((k for k in range(kc, cap) if rev5M[k] == bd), None)
        if kc is None:
            arm, scan_end, why = i, cap - 1, 'no-bigleg (scanned to cap)'      # needed ALL of [i+1,cap)
        elif da is None:
            arm, scan_end, why = i, cap - 1, 'no-reversal (scanned to cap)'    # needed ALL of [kc,cap)
        else:
            arm, scan_end, why = da, da, 'found (scan stopped at da)'
        recs.append((arm, scan_end, why, i, cap))

    tk_by_arm = {c[0]: c[7] for c in v2_cascade(W, lr)}      # final arm bar -> trade bar (None if no trade)
    tot = ahead = 0
    by_why = {}
    for (arm, scan_end, why, i, cap) in recs:
        tk = tk_by_arm.get(arm)
        if tk is None:
            continue                                          # no trade from this setup
        tot += 1
        la = scan_end > tk                                    # verdict needed bars AFTER the trade bar
        ahead += 1 if la else 0
        d = by_why.setdefault(why, [0, 0]); d[0] += 1; d[1] += 1 if la else 0

    print("\n=== arm_delay verdict vs trade bar (%d entries, %dd) ===" % (tot, SPAN_D))
    print("%-32s %8s %10s %8s" % ("verdict path", "entries", "look-ahead", "pct"))
    for why, (n, la) in sorted(by_why.items(), key=lambda x: -x[1][0]):
        print("%-32s %8d %10d %7.1f%%" % (why, n, la, 100.0 * la / max(n, 1)))
    print("\nTOTAL: %d/%d entries (%.1f%%) had their arm decided using bars AFTER the trade bar" %
          (ahead, tot, 100.0 * ahead / max(tot, 1)))
    print("VERDICT: %s" % ("LOOK-AHEAD CONFIRMED in the full-window backtest" if ahead else
                           "causal (no verdict read past its trade bar)"))
    dev.disconnect()


if __name__ == "__main__":
    main()
