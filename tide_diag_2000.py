"""tide_diag_2000.py — diagnose the 07-07 ~20:00 short OUTs Joe flagged as wrong-side s5r curls.
Window ends 22:00 (data past 20:00 visible), prints shorts exiting 19:50-20:40 with exit route, then the
coarse-sampled s5r around each so we can see which side the curl fired on. Run:  python3 tide_diag_2000.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import run_config

END = int(dtm.datetime(2026, 7, 7, 22, 0, tzinfo=timezone.utc).timestamp() * 1000)
OVR = {'s10r': (600, ('k', 6, 6, 5, 'close'), 'emerging'),
       's1m': (60, ('bb', 6, 0.56, 'close'), 'emerging'), 's1M': (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging'),
       's1r': (60, ('k', 6, 6, 5, 'close'), 'emerging')}
SCALP = dict(fin_sets=('s1', 's15', 's30'), rev_sets=(), N=6, tol=24, wait_breach=False, seam=150000, stall_floor=0.0)
hm = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')
LO, HI = 15, 85


def main():
    J = Jig(END, hours=6, warmup=24, overrides=OVR)
    m = run_config(J, SCALP)
    ts = J.ts; s5r = J.causal.line('s5r')
    lo = dtm.datetime(2026, 7, 7, 19, 50, tzinfo=timezone.utc).timestamp() * 1000
    hi = dtm.datetime(2026, 7, 7, 21, 45, tzinfo=timezone.utc).timestamp() * 1000
    print("=== short trades with exit in 19:50-20:45 ===")
    for e, x, side, ret, mae, route in m['trades']:
        if side == 'short' and lo <= ts[x] <= hi:
            print("  IN %s  OUT %s  route=%-6s ret%+.2f MAE%.2f  s5r@in=%.0f s5r@out=%.0f"
                  % (hm(ts[e]), hm(ts[x]), route, ret, mae, s5r[e], s5r[x]))
    print("\n=== s5r (coarse 150s samples) 19:50 -> 20:45 : side of each turn ===")
    tsc, s5rc = J.causal.coarse('s5r', 150000)
    for k in range(len(tsc)):
        if lo <= tsc[k] <= hi:
            turn = ''
            if k >= 2:
                if s5rc[k - 1] < s5rc[k] and s5rc[k - 1] <= s5rc[k - 2]:
                    turn = 'TROUGH(up-curl) side=%s' % ('LO-ok' if s5rc[k - 1] <= LO else 'MID/HI-WRONG')
                if s5rc[k - 1] > s5rc[k] and s5rc[k - 1] >= s5rc[k - 2]:
                    turn = 'PEAK(dn-curl)'
            print("  %s  s5r=%5.1f  %s" % (hm(tsc[k]), s5rc[k], turn))
    J.close()


if __name__ == "__main__":
    main()
