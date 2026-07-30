"""build_walkforward — single vs pair, walked across the weeks (Joe 0725). SAVED. The evolving-loop version of
the single/OOS check: slide IS(7d)->OOS(next 7d) across the tape; at EACH step re-tune both rules on that step's
IS and score on the next-week OOS. No verdict — prints each week's OOS for both; the spec call is Joe's.
  SINGLE : strength_s10 >= thr                       (1 knob)
  PAIR   : strength_slow >= ts AND strength_s10 >= tf (3 knobs: slow TF, ts, tf)
Both selected by ROBUST-on-IS = min(IS short net, IS long net). Scored swing-to-pivot @2% (siglab default), no stops.
Usage: build_walkforward.py <IS_days> <OOS_days> <step_days>   (default 7 7 3)
"""
import sys
import numpy as np
from datetime import timezone
import linelab as LL
import siglab

TFS = list(range(4, 31)); THRS = list(range(3, 27)); FAST = 10; CADENCE = 's5'; MINF = 5
DAY = 86400 * 1000
IS_D = int(sys.argv[1]) if len(sys.argv) > 1 else 7
OOS_D = int(sys.argv[2]) if len(sys.argv) > 2 else 7
STEP = int(sys.argv[3]) if len(sys.argv) > 3 else 3

for tf in TFS:
    LL.register('s%dx' % tf, kind='bb', tf=tf, length=5, mult=0.37)
    LL.register('s%dm' % tf, kind='bb', tf=tf, length=6, mult=0.45)
cache, ets, epx, names = LL.warm(rebuild=False)
lab = siglab.Lab(cache, ets, epx)
ti = {tf: i for i, tf in enumerate(TFS)}
t0, t1 = int(ets[0]), int(ets[-1])
import time as _t
F = lambda ms: _t.strftime('%m-%d', _t.gmtime(ms / 1000))


def blk(a, b):
    D = {}
    for d in (-1, 1):
        M = siglab.markers(cache, lab, CADENCE, a, b, TFS, d)
        STR = np.array([[m['strn'][tf] for tf in TFS] for m in M]) if M else np.zeros((0, len(TFS)))
        D[d] = dict(STR=STR, NET=np.array([m['mfe'] - m['mae'] for m in M]), MAE=np.array([m['mae'] for m in M]))
    return D


def nb(D, masks):
    ns, ms_ = [], []
    for d in (-1, 1):
        m = masks[d]
        if m.sum() < MINF:
            return None
        ns.append(D[d]['NET'][m]); ms_.append(D[d]['MAE'][m])
    alln = np.concatenate(ns); allm = np.concatenate(ms_)
    return dict(net=float(np.median(alln)), bank=100 * np.sum(allm < 1.0) / len(allm),
                snet=float(np.median(ns[0])), lnet=float(np.median(ns[1])), n=len(alln))


smask = lambda D, thr: {d: D[d]['STR'][:, ti[FAST]] >= thr for d in (-1, 1)}
pmask = lambda D, slow, ts, tf: {d: (D[d]['STR'][:, ti[slow]] >= ts) & (D[d]['STR'][:, ti[FAST]] >= tf) for d in (-1, 1)}
sgrid = [(t,) for t in THRS]
pgrid = [(s, ts, tf) for s in TFS if s != FAST for ts in THRS for tf in THRS]


def pick(ISD, mk, grid):
    best = None; bk = None
    for p in grid:
        r = nb(ISD, mk(ISD, *p))
        if not r:
            continue
        k = min(r['snet'], r['lnet'])
        if bk is None or k > bk:
            best = (p, r); bk = k
    return best


starts = []
s = t0
while s + (IS_D + OOS_D) * DAY <= t1 + DAY:
    starts.append(s); s += STEP * DAY
print('=== WALK-FORWARD | IS %dd -> OOS %dd, step %dd | swing 2%% | %d steps over %s..%s ===' % (
    IS_D, OOS_D, STEP, len(starts), F(t0), F(t1)))
print(' IS window   -> OOS window  | SINGLE cfg  OOSnet/bank | PAIR cfg           OOSnet/bank')
srec, prec = [], []
for st in starts:
    ISd = blk(st, st + IS_D * DAY); OOSd = blk(st + IS_D * DAY, st + (IS_D + OOS_D) * DAY)
    sb = pick(ISd, smask, sgrid); pb = pick(ISd, pmask, pgrid)
    so = nb(OOSd, smask(OOSd, *sb[0])) if sb else None
    po = nb(OOSd, pmask(OOSd, *pb[0])) if pb else None
    sc = ('s10>=%d' % sb[0][0]) if sb else '-'
    pc = ('s%d>=%d&s10>=%d' % pb[0]) if pb else '-'
    print('  %s..%s -> %s..%s | %-9s %s | %-16s %s' % (
        F(st), F(st + IS_D * DAY), F(st + IS_D * DAY), F(st + (IS_D + OOS_D) * DAY),
        sc, ('%+.2f/%3d%%' % (so['net'], round(so['bank']))) if so else 'OOS<MINF ',
        pc, ('%+.2f/%3d%%' % (po['net'], round(po['bank']))) if po else 'OOS<MINF'))
    if so:
        srec.append(so['net'])
    if po:
        prec.append(po['net'])
print('--- OOS net across walk: SINGLE mean %+.2f (n=%d steps) | PAIR mean %+.2f (n=%d) | pair-better %d/%d ---' % (
    (np.mean(srec) if srec else float('nan')), len(srec), (np.mean(prec) if prec else float('nan')), len(prec),
    sum(1 for a, b in zip(srec, prec) if b > a), min(len(srec), len(prec))))
