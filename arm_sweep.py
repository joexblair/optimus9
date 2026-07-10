"""arm_sweep.py — sweep the arm-delay knobs over N days. (Joe 0710)

Scores every config on the FULL flow (latch arm -> s3s4 gate -> finishers -> TP), per day, then reports
  pooled mean/win  AND  the WORST DAY's mean.
The worst-day column is the one to read: a config that only works on one day is not a config.

  python3 arm_sweep.py --days 2026-07-06..2026-07-09 --knob m_mult
  python3 arm_sweep.py --days 2026-07-06..2026-07-09 --knob bands
"""
import argparse
import datetime as dtm

import numpy as np

import arm_trade as AT

GRIDS = {
    'm_mult': [('--m-mult', v) for v in ('0.44', '0.50', '0.56', '0.62')],
    'm_len': [('--m-len', v) for v in ('6', '7', '8')],
    'tol': [('--tol', v) for v in ('0', '2', '4', '6')],
    'cap': [('--cap', v) for v in ('30', '60', '120', '240')],
    'bands': [('--bands', v) for v in ('7:2,14:4,999:6', '999:2', '999:4', '5:2,999:4', '7:2,999:4', '7:4,999:6')],
}


def daterange(spec):
    a, b = spec.split('..')
    d0, d1 = dtm.date.fromisoformat(a), dtm.date.fromisoformat(b)
    out = []
    while d0 <= d1:
        out.append(d0.isoformat()); d0 += dtm.timedelta(days=1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', default='2026-07-06..2026-07-09')
    ap.add_argument('--knob', required=True, choices=sorted(GRIDS))
    ap.add_argument('--producer', default='gate')
    ap.add_argument('--fixed', default='', help='extra argv, e.g. "--m-mult 0.56 --cap 60"')
    cli = ap.parse_args()

    days = daterange(cli.days)
    base = AT.build_args()
    fixed = cli.fixed.split() if cli.fixed else []
    print(f"\nknob={cli.knob}  producer={cli.producer}  days={days[0]}..{days[-1]} ({len(days)})  fixed={cli.fixed or '-'}")
    print(f"{'value':<18} {'n':>4} {'net mean':>10} {'win':>6} {'gross':>9} {'MAE p50':>8} "
          f"{'worst day':>10} {'best day':>9} {'days +ve':>9}")
    for (flag, val) in GRIDS[cli.knob]:
        per_day, pooled = [], []
        for day in days:
            argv = ['--day', day, '--producer', cli.producer] + fixed + [flag, val]
            try:
                rows = AT.run_day(base.parse_args(argv), quiet=True)
            except Exception as e:
                print(f"{val:<18}  ERROR {e}"); rows = None; break
            if not rows:
                per_day.append(np.nan); continue
            per_day.append(float(np.mean([r['net'] for r in rows]))); pooled += rows
        if not pooled:
            continue
        n = np.array([r['net'] for r in pooled]); g = np.array([r['gross'] for r in pooled])
        pd_ = np.array([x for x in per_day if np.isfinite(x)])
        print(f"{val:<18} {n.size:>4} {n.mean():+9.4f}% {100*(n>0).mean():5.1f}% {g.mean():+8.4f}%"
              f" {np.median([r['mae'] for r in pooled]):7.2f}% {pd_.min():+9.4f}% {pd_.max():+8.4f}%"
              f" {int((pd_>0).sum())}/{pd_.size:>3}")


if __name__ == '__main__':
    main()
