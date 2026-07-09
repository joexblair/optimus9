"""tide_report.py — MAE/MFE report for the machine with the strict s30a+s15a entry (1,1 box, via jig finisher_pair)
+ full exit online. Per-week over the live tape. Also reconciles the entry event vs the inline conjunction.
Run:  python3 tide_report.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from optimus9.analysis.lr_v2 import _rolling_any
from tide_machine import run_config

OVR = {'s10r': (600, ('k', 6, 6, 5, 'close'), 'emerging')}
CFG = dict(wait_breach=False, seam=150000, exit_gate='oob')      # strict entry + 1,1 box are the machine defaults now
WARMUP_D, LOOK_D = 2, 7


def main():
    now = dtm.datetime.now(timezone.utc)
    # ---- entry reconcile: finisher_pair(box=12) == inline q15&q30 co-occurrence over the 1,1 box ----
    J = Jig(int(now.timestamp() * 1000), hours=LOOK_D * 24, warmup=WARMUP_D * 24, overrides=OVR)
    q15h, q15l = J.causal.finishers('s15'); q30h, q30l = J.causal.finishers('s30')
    ep_h, ep_l = J.causal.finisher_pair(box=12)
    ih = _rolling_any(q15h, 12) & _rolling_any(q30h, 12); il = _rolling_any(q15l, 12) & _rolling_any(q30l, 12)
    print("ENTRY reconcile finisher_pair==inline: hi %s  lo %s" % (bool((ep_h == ih).all()), bool((ep_l == il).all())))
    J.close()

    ends = []
    e = now - dtm.timedelta(days=28)
    while e <= now:
        ends.append(e); e += dtm.timedelta(days=LOOK_D)
    if (now - ends[-1]).total_seconds() > 2 * 86400:
        ends.append(now)
    print("\n=== strict s30a+s15a entry (1,1) + full exit — MAE/MFE per week (live tape) ===")
    print("%-16s %4s | %6s %6s %5s | %7s %7s %6s %6s %6s %4s" %
          ("win_end", "n", "eMAE", "eMFE", "mfeS", "mean", "med", "rMAE", "rMFE", "tail", "win"))
    rows = []
    for end in ends:
        J = Jig(int(end.timestamp() * 1000), hours=LOOK_D * 24, warmup=WARMUP_D * 24, overrides=OVR)
        m = run_config(J, CFG); J.close(); rows.append(m)
        print("%-16s %4d | %6.2f %6.2f %5d | %+7.3f %+7.3f %6.2f %6.2f %6.2f %4.2f" %
              (end.strftime("%m-%d %H:%M"), m['n'], m['e_mae'], m['e_mfe'], m['mfeside'],
               m['r_mean'], m['r_ret'], m['r_mae'], m['r_mfe'], m['mae_tail'], m['win']))
    md = lambda k: np.median([r[k] for r in rows])
    print("\nMEDIAN  eMAE %.2f eMFE %.2f | mean %+.3f med %+.3f rMAE %.2f rMFE %.2f tail %.2f win %.2f" %
          (md('e_mae'), md('e_mfe'), md('r_mean'), md('r_ret'), md('r_mae'), md('r_mfe'), md('mae_tail'), md('win')))


if __name__ == "__main__":
    main()
