"""build_confluence_sweep — UNIFIED bi-directional AND-confluence, EXHAUSTIVE step=1 (Joe 0724). SAVED.

No sampling — every integer TF in [TF_MIN,TF_MAX] and every integer threshold in [THR_MIN,THR_MAX] is scanned (🪖).
ONE config, mirror-applied to both directions (separate short/long = overfit). Rolled-s4 + strength_slow>=ts AND
strength_fast>=tf. Scored swing-to-pivot @1% MAE/MFE, NO stops. Each config must fire >=FLOOR_D on BOTH sides;
ranked by COMBINED median net, short/long split shown so lopsided (overfit) configs are visible. Vectorized.
Usage: build_confluence_sweep.py <YYYY-MM-DD> <ndays>   (default 06-22 +7d)
"""
import sys
import numpy as np
from datetime import datetime, timezone, timedelta
import linelab as LL
import siglab

TF_MIN, TF_MAX = 6, 30          # every integer TF, step=1
THR_MIN, THR_MAX = 3, 26        # every integer threshold, step=1
TFS = list(range(TF_MIN, TF_MAX + 1))
THRS = list(range(THR_MIN, THR_MAX + 1))
CADENCE = 's5'
FLOOR_D = 8
STOP = 1.0

_day = next((a for a in sys.argv[1:] if a[:1].isdigit() and '-' in a), '2026-06-22')
_ndays = next((int(a) for a in sys.argv[1:] if a.isdigit()), 7)
_d0 = datetime.strptime(_day, '%Y-%m-%d').replace(tzinfo=timezone.utc)
S = int(_d0.timestamp() * 1000); E = int((_d0 + timedelta(days=_ndays)).timestamp() * 1000)

for tf in TFS:
    LL.register('s%dx' % tf, kind='bb', tf=tf, length=5, mult=0.37)
    LL.register('s%dm' % tf, kind='bb', tf=tf, length=6, mult=0.45)
cache, ets, epx, names = LL.warm(rebuild=False)
lab = siglab.Lab(cache, ets, epx)

# precompute per direction: strength matrix [n_markers, n_tf] + net vector
DAT = {}
for d in (-1, 1):
    M = siglab.markers(cache, lab, CADENCE, S, E, TFS, d)
    STR = np.array([[m['strn'][tf] for tf in TFS] for m in M]) if M else np.zeros((0, len(TFS)))
    NET = np.array([m['mfe'] - m['mae'] for m in M])
    MAE = np.array([m['mae'] for m in M]); MFE = np.array([m['mfe'] for m in M])
    DAT[d] = dict(STR=STR, NET=NET, MAE=MAE, MFE=MFE, n=len(M))
print('=== unified confluence EXHAUSTIVE step=1 | %s +%dd | cadence=%s | %d short + %d long markers ===' % (
    _day, _ndays, CADENCE, DAT[-1]['n'], DAT[1]['n']))
print('    swept: TF %d..%d (%d) x TF (fast<slow) x thr %d..%d (%d)^2  = %d configs' % (
    TF_MIN, TF_MAX, len(TFS), THR_MIN, THR_MAX, len(THRS),
    (len(TFS) * (len(TFS) - 1) // 2) * len(THRS) * len(THRS)))

ti = {tf: i for i, tf in enumerate(TFS)}
best = []
for si, slow in enumerate(TFS):
    for fast in TFS[:si]:                                   # fast < slow
        cs, cf = ti[slow], ti[fast]
        for ts_ in THRS:
            ms_s0 = DAT[-1]['STR'][:, cs] >= ts_; ml_s0 = DAT[1]['STR'][:, cs] >= ts_
            for tf_ in THRS:
                ms = ms_s0 & (DAT[-1]['STR'][:, cf] >= tf_)
                ml = ml_s0 & (DAT[1]['STR'][:, cf] >= tf_)
                ns, nl = int(ms.sum()), int(ml.sum())
                if ns < FLOOR_D or nl < FLOOR_D:
                    continue
                cn = np.concatenate([DAT[-1]['NET'][ms], DAT[1]['NET'][ml]])
                netmed = float(np.median(cn))
                bank = 100 * (np.sum(DAT[-1]['MAE'][ms] < STOP) + np.sum(DAT[1]['MAE'][ml] < STOP)) / (ns + nl)
                snet = float(np.median(DAT[-1]['NET'][ms])); lnet = float(np.median(DAT[1]['NET'][ml]))
                sbank = 100 * np.sum(DAT[-1]['MAE'][ms] < STOP) / ns; lbank = 100 * np.sum(DAT[1]['MAE'][ml] < STOP) / nl
                mfe = float(np.median(np.concatenate([DAT[-1]['MFE'][ms], DAT[1]['MFE'][ml]])))
                mae = float(np.median(np.concatenate([DAT[-1]['MAE'][ms], DAT[1]['MAE'][ml]])))
                best.append((netmed, slow, fast, ts_, tf_, ns, nl, mfe, mae, bank, snet, sbank, lnet, lbank))
best.sort(reverse=True)
print('\n-- TOP 15 UNIFIED configs by COMBINED median net (both sides >=%d fires), of %d qualifying --' % (
    FLOOR_D, len(best)))
print(' slow>=t & fast>=t | S+L fires | MFE/MAE/net | bank | SHORT net/bank | LONG net/bank')
for r in best[:15]:
    netmed, slow, fast, ts_, tf_, ns, nl, mfe, mae, bank, snet, sbank, lnet, lbank = r
    print('  s%d>=%-2d & s%d>=%-2d | %2d+%-2d=%2d | %4.2f/%4.2f/%+5.2f | %3d%% | %+5.2f/%3d%% | %+5.2f/%3d%%' % (
        slow, ts_, fast, tf_, ns, nl, ns + nl, mfe, mae, netmed, round(bank), snet, round(sbank), lnet, round(lbank)))
