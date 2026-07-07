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
SCALP = dict(fin_sets=('s1', 's15', 's30'), rev_sets=(), N=6, tol=24, wait_breach=False, seam=150000, stall_floor=0.0)
BEST = dict(SCALP, use_gate=False)                          # scalp, NO s3s4 gate
LEAKY = dict(SCALP, use_gate=True)                          # scalp, WITH s3s4 gate (arm->gate->finisher)


def window_ends():
    e = SANITISE + dtm.timedelta(days=WARMUP_D + LOOK_D); out = []
    while e <= NOW:
        out.append(e); e += dtm.timedelta(days=LOOK_D)
    if not out or (NOW - out[-1]).days >= 3:
        out.append(NOW)
    return out


def main():
    ends = window_ends()
    print("=== multi-window: realized per week — GATE-off vs GATE-on (scalp) — %d windows x 7d ===" % len(ends))
    print("%-11s %4s | %7s %6s %6s %4s | %7s %6s %6s %4s" %
          ("win_end", "n", "NOGret", "NOGmae", "NOGmfe", "win", "GATret", "GATmae", "GATmfe", "win"))
    bests = []; leaks = []
    for end in ends:
        J = Jig(int(end.timestamp() * 1000), hours=LOOK_D * 24, warmup=WARMUP_D * 24, overrides=OVR)
        b = run_config(J, BEST); l = run_config(J, LEAKY); J.close()
        bests.append(b); leaks.append(l)
        print("%-11s %4d | %+7.3f %6.2f %6.2f %4.2f | %+7.3f %6.2f %6.2f %4.2f" %
              (end.strftime("%Y-%m-%d"), b['n'], b['r_ret'], b['r_mae'], b['r_mfe'], b['win'],
               l['r_ret'], l['r_mae'], l['r_mfe'], l['win']))
    md = lambda rows, k: np.median([r[k] for r in rows])
    print("\nMEDIAN  GATEoff: ret %+.3f  MAE %.2f  MFE %.2f  win %.2f  | GATEon: ret %+.3f  MAE %.2f  MFE %.2f  win %.2f"
          % (md(bests, 'r_ret'), md(bests, 'r_mae'), md(bests, 'r_mfe'), md(bests, 'win'),
             md(leaks, 'r_ret'), md(leaks, 'r_mae'), md(leaks, 'r_mfe'), md(leaks, 'win')))
    print("WORST-window ret  GATEoff %+.3f  GATEon %+.3f" % (min(r['r_ret'] for r in bests), min(r['r_ret'] for r in leaks)))


if __name__ == "__main__":
    main()
