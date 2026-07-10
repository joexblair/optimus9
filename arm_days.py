"""arm_days.py — the full arm-delay flow over N days, pooled. (Joe 0710)

  python3 arm_days.py --days 2026-07-03..2026-07-09 --producer gate
"""
import argparse, datetime as dtm
import numpy as np
import arm_trade as AT


def daterange(spec):
    a, b = spec.split('..')
    d0 = dtm.date.fromisoformat(a); d1 = dtm.date.fromisoformat(b)
    out = []
    while d0 <= d1:
        out.append(d0.isoformat()); d0 += dtm.timedelta(days=1)
    return out


ap = argparse.ArgumentParser()
ap.add_argument('--days', default='2026-07-03..2026-07-09')
ap.add_argument('--producers', default='arm,gate')
ap.add_argument('--cap', type=int, default=240)
ap.add_argument('--m-len', type=int, default=7)
ap.add_argument('--m-mult', type=float, default=0.50)
ap.add_argument('--tol', type=float, default=0.0)
ap.add_argument('--bands', default=None)
cli = ap.parse_args()

base = AT.build_args()
for prod in cli.producers.split(','):
    pooled = []
    print(f"\n===== producer={prod} =====")
    print(f"{'day':<12} {'n':>4} {'net mean':>10} {'total':>8} {'win':>6} {'gross':>9} {'MAE p50':>8} {'delay':>6}")
    for day in daterange(cli.days):
        argv = ['--day', day, '--producer', prod, '--cap', str(cli.cap),
                '--m-len', str(cli.m_len), '--m-mult', str(cli.m_mult), '--tol', str(cli.tol)]
        if cli.bands:
            argv += ['--bands', cli.bands]
        a = base.parse_args(argv)
        try:
            rows = AT.run_day(a, quiet=True)
        except Exception as e:
            print(f"{day:<12}  ERROR {e}"); continue
        if not rows:
            print(f"{day:<12}    0"); continue
        n = np.array([r['net'] for r in rows]); g = np.array([r['gross'] for r in rows])
        print(f"{day:<12} {n.size:>4} {n.mean():+9.4f}% {n.sum():+7.2f}% {100*(n>0).mean():5.1f}%"
              f" {g.mean():+8.4f}% {np.median([r['mae'] for r in rows]):7.2f}%"
              f" {np.median([r['delay'] for r in rows]):5.0f}m")
        pooled += rows
    if pooled:
        n = np.array([r['net'] for r in pooled]); g = np.array([r['gross'] for r in pooled])
        print(f"{'POOLED':<12} {n.size:>4} {n.mean():+9.4f}% {n.sum():+7.2f}% {100*(n>0).mean():5.1f}%"
              f" {g.mean():+8.4f}% {np.median([r['mae'] for r in pooled]):7.2f}%"
              f" {np.median([r['delay'] for r in pooled]):5.0f}m")
        from collections import Counter
        print("  apex TFs: " + "  ".join(f"TF{t}x{c}" for t, c in sorted(Counter(r['tf'] for r in pooled).items())))
