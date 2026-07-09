"""tide_timeline.py — chronological table over the span of the last 10 s5m breaches, interleaving where s15a and s30a
trigger (rising edges, both sides). Shows how tightly (or not) the three Stage-1 ingredients actually cluster.
Run:  python3 tide_timeline.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import _sgn

NOW = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
hm = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%H:%M:%S')


def edges(sig):
    return [k for k in range(1, len(sig)) if sig[k] and not sig[k - 1]]


def main():
    J = Jig(NOW, hours=24, warmup=24)
    n = J.n; ts = J.ts; HI, LO = J.hi, J.lo
    s5m = J.causal.line('s5m'); s5s = _sgn(s5m, HI, LO)
    q15h, q15l = J.causal.finishers('s15'); q30h, q30l = J.causal.finishers('s30')
    br = [k for k in range(1, n) if (s5s[k] == 1 and s5s[k - 1] != 1) or (s5s[k] == -1 and s5s[k - 1] != -1)]
    start = br[-10]                                            # span = from 10th-last s5m breach to the last bar
    rows = []
    for k in br:
        if k >= start:
            rows.append((ts[k], 's5m BREACH', 'HI' if s5s[k] == 1 else 'LO', '%.0f' % s5m[k]))
    for tag, sig, side in [('s15a', q15h, 'HI'), ('s15a', q15l, 'LO'), ('s30a', q30h, 'HI'), ('s30a', q30l, 'LO')]:
        for k in edges(sig):
            if k >= start:
                rows.append((ts[k], tag, side, ''))
    rows.sort()
    print("=== last 10 s5m breaches + s15a/s30a triggers interleaved (%s .. %s) ===" % (hm(ts[start]), hm(ts[-1])))
    print("%-10s  %-11s  %-4s  %s" % ("time", "event", "side", "s5m"))
    for t, ev, sd, val in rows:
        mark = '  <<' if ev == 's5m BREACH' else ''
        print("%-10s  %-11s  %-4s  %-4s%s" % (hm(t), ev, sd, val, mark))
    J.close()


if __name__ == "__main__":
    main()
