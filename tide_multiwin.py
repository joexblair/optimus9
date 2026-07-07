"""tide_multiwin.py — multi-window validation of the sweep winner (Joe 0707). Runs the BEST config
(wait_breach=OFF, s10r 600/close, seam 150s, fl0, finisher breach-N6-tol4) vs the LEAKY one (wait_breach=ON) over
7-day windows tiling the sanitised tape (05-18+ -> 07-07 20:00). Reports per-window realised r_ret + win + entries and
the median/worst across windows — does the +0.45 hold, or was it one lucky window? Run:  python3 tide_multiwin.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import run_config

SANITISE = dtm.datetime(2026, 5, 18, tzinfo=timezone.utc)
NOW = dtm.datetime(2026, 7, 7, 20, 0, tzinfo=timezone.utc)
WARMUP_D, LOOK_D = 2, 7
S1 = {'s1m': (60, ('bb', 6, 0.56, 'close'), 'emerging'), 's1M': (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging'),
      's1r': (60, ('k', 6, 6, 5, 'close'), 'emerging')}
OVR = {'s10r': (600, ('k', 6, 6, 5, 'close'), 'emerging'), **S1}
BEST = dict(fin_sets=('s1', 's15', 's30'), rev_sets=(), N=6, tol=24, wait_breach=False, seam=150000, stall_floor=0.0)
LEAKY = dict(BEST); LEAKY['wait_breach'] = True


def window_ends():
    e = SANITISE + dtm.timedelta(days=WARMUP_D + LOOK_D); out = []
    while e <= NOW:
        out.append(e); e += dtm.timedelta(days=LOOK_D)
    if not out or (NOW - out[-1]).days >= 3:
        out.append(NOW)
    return out


def main():
    ends = window_ends()
    print("=== multi-window: BEST (wb=off) vs LEAKY (wb=on) — %d windows x 7d ===" % len(ends))
    print("%-12s %4s | %8s %5s | %8s %5s" % ("win_end", "n", "BEST_ret", "win", "LEAK_ret", "win"))
    bests = []; leaks = []
    for end in ends:
        J = Jig(int(end.timestamp() * 1000), hours=LOOK_D * 24, warmup=WARMUP_D * 24, overrides=OVR)
        b = run_config(J, BEST); l = run_config(J, LEAKY); J.close()
        bests.append((b['r_ret'], b['win'], b['n'])); leaks.append((l['r_ret'], l['win']))
        print("%-12s %4d | %+8.3f %5.2f | %+8.3f %5.2f" % (end.strftime("%Y-%m-%d"), b['n'], b['r_ret'], b['win'], l['r_ret'], l['win']))
    br = np.array([x[0] for x in bests]); bw = np.array([x[1] for x in bests]); lr = np.array([x[0] for x in leaks])
    print("\nBEST  r_ret: median %+.3f  worst %+.3f  | win median %.2f  | %d/%d windows positive"
          % (np.median(br), br.min(), np.median(bw), int((br > 0).sum()), len(br)))
    print("LEAKY r_ret: median %+.3f  worst %+.3f" % (np.median(lr), lr.min()))
    print("lift (BEST - LEAKY) median: %+.3f" % np.median(br - lr))


if __name__ == "__main__":
    main()
