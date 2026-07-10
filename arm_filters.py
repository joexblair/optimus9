"""arm_filters.py — post-hoc filters on the 9-day gate book, scored per day. (Joe 0710)

Every filter is causal at the bar it acts on.  Reported with the WORST day, because a filter that only
works on the pool is a filter fitted to the pool.

  python3 arm_filters.py --days 2026-07-01..2026-07-09
"""
import argparse, datetime as dtm
import numpy as np
import arm_trade as AT

COST = 0.20


def daterange(spec):
    a, b = spec.split('..'); d0, d1 = dtm.date.fromisoformat(a), dtm.date.fromisoformat(b)
    out = []
    while d0 <= d1:
        out.append(d0.isoformat()); d0 += dtm.timedelta(days=1)
    return out


ap = argparse.ArgumentParser()
ap.add_argument('--days', default='2026-07-01..2026-07-09')
ap.add_argument('--producer', default='gate')
cli = ap.parse_args()

base = AT.build_args()
by_day = {}
for day in daterange(cli.days):
    by_day[day] = AT.run_day(base.parse_args(['--day', day, '--producer', cli.producer]), quiet=True)
allr = [r for v in by_day.values() for r in v]
print(f"\n{len(allr)} trades over {len(by_day)} days   producer={cli.producer}   cost {COST}%\n")


def score(name, keep, xform=None):
    """keep(r) -> bool (take the trade).  xform(r) -> net (default r['net'])."""
    per, pooled = [], []
    for day, rows in by_day.items():
        sel = [r for r in rows if keep(r)]
        if not sel:
            per.append(np.nan); continue
        v = [(xform(r) if xform else r['net']) for r in sel]
        per.append(float(np.mean(v))); pooled += v
    if not pooled:
        print(f"  {name:<34} (none)"); return
    a = np.array(pooled); pd_ = np.array([x for x in per if np.isfinite(x)])
    print(f"  {name:<34} n={a.size:<4} mean {a.mean():+8.4f}%  total {a.sum():+7.2f}%  win {100*(a>0).mean():5.1f}%"
          f"  worst day {pd_.min():+8.4f}%  days+ {int((pd_>0).sum())}/{pd_.size}")


print("BASELINE")
score("all trades", lambda r: True)

print("\nENTRY FILTERS (skip the trade)")
for t in (6, 7, 8):
    score(f"apex TF >= {t}", lambda r, t=t: r['tf'] >= t)
score("tpTF > apex (ladder awake above)", lambda r: r['xt'] > r['tf'])
score("delay <= 10 min", lambda r: r['delay'] <= 10)
score("delay >= 10 min", lambda r: r['delay'] >= 10)

print("\nTIME-AND-EXCURSION EXITS (bail at minute N if MFE@N < X)")
for N in (5, 10, 15):
    for X in (0.10, 0.20, 0.30):
        def xf(r, N=N, X=X):
            return (r[f'exit{N}'] - COST) if r[f'mfe{N}'] < X else r['net']
        score(f"N={N:>2}m  X={X:.2f}%", lambda r: True, xf)

print("\nCOMBINED")
def combo(r):
    if r['mfe10'] < 0.20:
        return r['exit10'] - COST
    return r['net']
score("bail@10m if MFE<0.20", lambda r: True, combo)
score("...and apex >= 6", lambda r: r['tf'] >= 6, combo)
score("...and apex >= 7", lambda r: r['tf'] >= 7, combo)
