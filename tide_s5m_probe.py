"""tide_s5m_probe.py — (1) s5m breach moments over the last 24h (the event Stage-1 keys on), (2) s15a & s30a events
over the last 2h via the jig's finishers() endpoint, (3) whether 's30a+s15a' is a single event or a conjunction.
Reads live tape. Run:  python3 tide_s5m_probe.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import _sgn

NOW = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
hm = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')


def edges(sig):                                   # rising edges of a boolean signal = discrete events
    return [k for k in range(1, len(sig)) if sig[k] and not sig[k - 1]]


def main():
    J = Jig(NOW, hours=24, warmup=24)             # s5m / s15 / s30 all from DB (no overrides needed)
    n = J.n; ts = J.ts; HI, LO = J.hi, J.lo
    print("tape last bar =", hm(ts[-1]), " HI/LO =", HI, LO)
    s5m = J.causal.line('s5m'); s5s = _sgn(s5m, HI, LO)
    q15h, q15l = J.causal.finishers('s15'); q30h, q30l = J.causal.finishers('s30')
    lb = J.cfg.fin_lb

    print("\n=== (1) s5m BREACHES — last 24h (fresh flip into OOB) ===")
    br = [(k, 'HI' if s5s[k] == 1 else 'LO') for k in range(1, n)
          if (s5s[k] == 1 and s5s[k - 1] != 1) or (s5s[k] == -1 and s5s[k - 1] != -1)]
    print("count = %d  (%d HI, %d LO)" % (len(br), sum(s == 'HI' for _, s in br), sum(s == 'LO' for _, s in br)))
    for k, s in br:
        print("  %s  s5m %s  (%.0f)" % (hm(ts[k]), s, s5m[k]))

    two = NOW - 2 * 3600 * 1000
    def in2h(ks): return [k for k in ks if ts[k] >= two]
    e15h, e15l = in2h(edges(q15h)), in2h(edges(q15l))
    e30h, e30l = in2h(edges(q30h)), in2h(edges(q30l))
    print("\n=== (2) s15a & s30a EVENTS — last 2h (rising edges, per side) ===")
    print("s15a: %d hi, %d lo   s30a: %d hi, %d lo" % (len(e15h), len(e15l), len(e30h), len(e30l)))
    for tag, ks in [('s15a-HI', e15h), ('s15a-LO', e15l), ('s30a-HI', e30h), ('s30a-LO', e30l)]:
        print("  %s: %s" % (tag, ", ".join(hm(ts[k])[6:] for k in ks) or "(none)"))

    print("\n=== (3) is 's30a+s15a' a single event? — co-occurrence within exit_fin_lb=%d bars, last 2h ===" % lb)
    for side, q15, q30 in [('HI', q15h, q30h), ('LO', q15l, q30l)]:
        pairs = []
        for k in in2h(edges(q15)):                # for each s15a, is there an s30a within +/- lb?
            if np.flatnonzero(q30[max(0, k - lb):min(n, k + lb + 1)]).size:
                pairs.append(k)
        print("  %s side: %d of %d s15a events had an s30a within %d bars" % (side, len(pairs), len(in2h(edges(q15))), lb))
    print("  -> s15a and s30a are SEPARATE jig signals (finishers('s15') vs finishers('s30')); 's30a+s15a' is a CONJUNCTION the")
    print("     machine builds in a window, not a native event. There is no finishers-combined endpoint.")
    J.close()


if __name__ == "__main__":
    main()
