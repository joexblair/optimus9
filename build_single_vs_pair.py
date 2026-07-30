"""build_single_vs_pair — does the 2nd confluence line earn its degrees of freedom? (Joe 0725). SAVED.

Neutral, DOF-charged instrument. NO verdict — prints the numbers; the spec call is Joe's.
  SINGLE : strength_s10 >= thr                    (1 free knob: thr)
  PAIR   : strength_slow >= ts AND strength_s10 >= tf   (3 free knobs: slow TF, ts, tf -- s10 fixed as fast)
Both pick their BEST config on IS (max combined median net, min fires/dir/half), then are scored on the held-out
OOS half. Run BOTH split orderings (first->last AND last->first) so neither side rides a lucky split. The pair's
extra DOF lets it win IS by construction; the honest number is OOS, and the IS->OOS drop is the overfit tax.
Usage: build_single_vs_pair.py <YYYY-MM-DD> <ndays>   (default 06-22 +14d)
"""
import sys
import numpy as np
from datetime import datetime, timezone, timedelta
import linelab as LL
import siglab

TFS = list(range(4, 31))       # Joe 0725: TF4 added (step=1). Inert as its own confluence (strength vs s4 ≡ 0) — swept, not assumed.
THRS = list(range(3, 27))
FAST = 10                      # s10 fixed as the confirmer both methods share
CADENCE = 's5'
MINF = 5

_day = next((a for a in sys.argv[1:] if a[:1].isdigit() and '-' in a), '2026-06-22')
_ndays = next((int(a) for a in sys.argv[1:] if a.isdigit()), 14)
_d0 = datetime.strptime(_day, '%Y-%m-%d').replace(tzinfo=timezone.utc)
S = int(_d0.timestamp() * 1000)
MID = int((_d0 + timedelta(days=_ndays // 2)).timestamp() * 1000)
E = int((_d0 + timedelta(days=_ndays)).timestamp() * 1000)

for tf in TFS:
    LL.register('s%dx' % tf, kind='bb', tf=tf, length=5, mult=0.37)
    LL.register('s%dm' % tf, kind='bb', tf=tf, length=6, mult=0.45)
cache, ets, epx, names = LL.warm(rebuild=False)
lab = siglab.Lab(cache, ets, epx)
ti = {tf: i for i, tf in enumerate(TFS)}


def blk(a, b):
    D = {}
    for d in (-1, 1):
        M = siglab.markers(cache, lab, CADENCE, a, b, TFS, d)
        STR = np.array([[m['strn'][tf] for tf in TFS] for m in M]) if M else np.zeros((0, len(TFS)))
        D[d] = dict(STR=STR, NET=np.array([m['mfe'] - m['mae'] for m in M]),
                    MAE=np.array([m['mae'] for m in M]))
    return D


A = blk(S, MID); B = blk(MID, E)


def net_bank(D, mask_by_d):
    nets, maes = [], []
    for d in (-1, 1):
        m = mask_by_d[d]
        if m.sum() < MINF:
            return None
        nets.append(D[d]['NET'][m]); maes.append(D[d]['MAE'][m])
    alln = np.concatenate(nets); allm = np.concatenate(maes)
    return dict(n=len(alln), net=float(np.median(alln)), bank=100 * np.sum(allm < 1.0) / len(allm),
                snet=float(np.median(nets[0])), lnet=float(np.median(nets[1])))


def single_mask(D, thr):
    return {d: D[d]['STR'][:, ti[FAST]] >= thr for d in (-1, 1)}


def pair_mask(D, slow, ts, tf):
    return {d: (D[d]['STR'][:, ti[slow]] >= ts) & (D[d]['STR'][:, ti[FAST]] >= tf) for d in (-1, 1)}


def best_on(ISD, mkmask, grid):
    """Select the config that maximizes ROBUST-on-IS = min(IS short net, IS long net) — balanced, the fairest
    shot for the pair (Joe 0725: no longer best-IS-net, which handed the pair its most-overfit config)."""
    best = None; bestkey = None
    for params in grid:
        r = net_bank(ISD, mkmask(ISD, *params))
        if not r:
            continue
        key = min(r['snet'], r['lnet'])
        if bestkey is None or key > bestkey:
            best = (params, r); bestkey = key
    return best


single_grid = [(t,) for t in THRS]
pair_grid = [(slow, ts, tf) for slow in TFS if slow != FAST for ts in THRS for tf in THRS]

for label, ISD, OOSD in (('IS=first7 -> OOS=last7', A, B), ('IS=last7 -> OOS=first7', B, A)):
    print('\n==== %s | s10=fixed confirmer | MINF=%d/dir/half ====' % (label, MINF))
    sb = best_on(ISD, single_mask, single_grid)
    pb = best_on(ISD, pair_mask, pair_grid)
    print(' method | best-IS config      | IS net/bank         | OOS net/bank         | IS->OOS drop | OOS S/L')
    for name, b, mk in (('SINGLE', sb, single_mask), ('PAIR  ', pb, pair_mask)):
        if not b:
            print('  %s | (no config met MINF)' % name); continue
        params, fitr = b
        tr = net_bank(OOSD, mk(OOSD, *params))
        cfg = ('s10>=%d' % params[0]) if name.startswith('SINGLE') else ('s%d>=%d & s10>=%d' % params)
        if tr:
            print('  %s | %-19s | %+.2f/%3d%% (n%2d) | %+.2f/%3d%% (n%2d) | %+.2f | %+.2f/%+.2f' % (
                name, cfg, fitr['net'], round(fitr['bank']), fitr['n'], tr['net'], round(tr['bank']), tr['n'],
                tr['net'] - fitr['net'], tr['snet'], tr['lnet']))
        else:
            print('  %s | %-19s | %+.2f/%3d%% (n%2d) | best-IS config fired <MINF on OOS' % (
                name, cfg, fitr['net'], round(fitr['bank']), fitr['n']))
