"""tide_gate_ab.py — A/B the exit target-side gate (Joe 0708 catch: exits were firing on wrong-side curls).
Runs the scalp with exit_gate OFF (old: any turn) vs OOB (turn must reach the favourable extreme) vs MID
(turn past mid), over the 7-day windows tiling the sanitised tape. Reports realised r_ret/MAE/MFE/win per window.
Run:  python3 tide_gate_ab.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import run_config

SANITISE = dtm.datetime(2026, 5, 18, tzinfo=timezone.utc)
NOW = dtm.datetime.now(timezone.utc)
WARMUP_D, LOOK_D = 2, 7
S1 = {'s1m': (60, ('bb', 6, 0.56, 'close'), 'emerging'), 's1M': (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging'),
      's1r': (60, ('k', 6, 6, 5, 'close'), 'emerging')}
OVR = {'s10r': (600, ('k', 6, 6, 5, 'close'), 'emerging'), **S1}
SCALP = dict(fin_sets=('s1', 's15', 's30'), rev_sets=(), N=6, tol=24, wait_breach=False, seam=150000, stall_floor=0.0)


def window_ends():
    e = SANITISE + dtm.timedelta(days=WARMUP_D + LOOK_D); out = []
    while e <= NOW:
        out.append(e); e += dtm.timedelta(days=LOOK_D)
    if not out or (NOW - out[-1]).days >= 3:
        out.append(NOW)
    return out


def main():
    ends = window_ends()
    variants = [('OFF', 'off'), ('OOB', 'oob'), ('MID', 'mid')]
    print("=== exit target-side gate A/B — scalp over %d windows x 7d — HONEST COMPASS: mean + MAE-tail (CVaR10) ===" % len(ends))
    print("(mean = tail-sensitive center; tail = mean of worst-decile realized MAE = what the account actually eats)")
    print("%-11s | " % "win_end" + " | ".join("%-3s  n  mean  med  tail  win" % v[0] for v in variants))
    acc = {v[0]: [] for v in variants}
    for end in ends:
        J = Jig(int(end.timestamp() * 1000), hours=LOOK_D * 24, warmup=WARMUP_D * 24, overrides=OVR)
        row = "%-11s | " % end.strftime("%Y-%m-%d"); cells = []
        for name, g in variants:
            m = run_config(J, dict(SCALP, exit_gate=g)); acc[name].append(m)
            cells.append("%3d %+5.2f %+5.2f %5.1f %4.2f" % (m['n'], m['r_mean'], m['r_ret'], m['mae_tail'], m['win']))
        J.close()
        print(row + " | ".join(cells))
    md = lambda rows, k: np.median([r[k] for r in rows])
    print("\n%-6s %7s %7s %7s %7s %6s" % ("GATE", "MEANmed", "MEDmed", "TAILmed", "TAILwrst", "winmed"))
    for v in variants:
        r = acc[v[0]]
        print("%-6s %+7.3f %+7.3f %+7.2f %+7.2f %6.2f"
              % (v[0], md(r, 'r_mean'), md(r, 'r_ret'), md(r, 'mae_tail'), min(x['mae_tail'] for x in r), md(r, 'win')))
    print("\nread on the honest compass: MEAN (not median) is the center that feels the tail; TAIL is the worst-decile MAE the")
    print("account eats. A gate that lifts mean by DEEPENING tail hasn't found edge — it's borrowed it from the tail.")


if __name__ == "__main__":
    main()
