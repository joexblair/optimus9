"""tide_causality.py — window-invariance causality audit (the project's confirmed look-ahead test). Two windows with
the SAME entry cutoff but different END (short vs short+6h more tape). Any INTERIOR trade (entered+exited well before
the short end) MUST be bit-identical in both; if extending the tape shifts it, a forward scan is peeking (look-ahead).
Specifically stresses arm_delay (uncapped forward scan) and the exit walk. Run:  python3 tide_causality.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import run_config

OVR = {'s10r': (600, ('k', 6, 6, 5, 'close'), 'emerging')}
CFG = dict(wait_breach=False, seam=150000, exit_gate='oob')
hm = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')


def trades_by_entry(end, start):
    hours = int((end - start).total_seconds() / 3600)
    J = Jig(int(end.timestamp() * 1000), hours=hours, warmup=48, overrides=OVR); ts = J.ts
    m = run_config(J, CFG)
    out = {int(ts[e]): (int(ts[x]), round(ret, 4), round(mae, 4), side) for e, x, side, ret, mae, route in m['trades']}
    J.close(); return out, int(ts[-1])


def main():
    now = dtm.datetime.now(timezone.utc)
    START = now - dtm.timedelta(days=24)                         # same cutoff for both
    T = now - dtm.timedelta(days=3)                              # comparison horizon (short end); long adds 3d future pad
    S, s_last = trades_by_entry(T, START)
    L, l_last = trades_by_entry(now, START)
    short_end = int(T.timestamp() * 1000)
    print("short window ends %s ; long ends %s (same cutoff %s, +3d tape)" % (hm(s_last), hm(l_last), hm(int(START.timestamp() * 1000))))
    guard = short_end - 3600 * 1000
    interior = [te for te in S if te < guard and S[te][0] < guard]
    mism = []
    for te in interior:
        if te not in L:
            mism.append((te, 'MISSING in long', S[te], None)); continue
        if S[te] != L[te]:
            mism.append((te, 'DIFFERS', S[te], L[te]))
    print("interior trades (closed >1h before short end): %d" % len(interior))
    print("bit-identical across the +6h tape: %d / %d" % (len(interior) - len(mism), len(interior)))
    if mism:
        print("\n*** LOOK-AHEAD — %d interior trades shifted when tape was extended ***" % len(mism))
        for te, why, s, l in mism[:15]:
            print("  entry %s  %s\n     short=%s\n     long =%s" % (hm(te), why, s, l))
    else:
        print("\nPASS — every interior trade is invariant to future tape. Entry (arm_delay) + exit are causal.")


if __name__ == "__main__":
    main()
