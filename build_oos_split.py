"""build_oos_split — unified confluence with an OOS TRAIN/TEST split (Joe 0725). SAVED.

The plain exhaustive sweep gets gamed: ranking by median net rewards high thresholds that filter to 8-9 lucky
fires. Fix = fit on the FIRST half of the window, TEST on the SECOND half (mirrors the RPL evo's IS/OOS).
A config that only fits the first half collapses on the second -> its test-net exposes the overfit.
Rule: rolled-s4 + strength_slow>=ts AND strength_fast>=tf, ONE config both directions (siglab). Swing-to-pivot @1%.
Ranked by TEST combined median net, among configs firing >=MINF per half per direction. Shows fit->test drop.
Usage: build_oos_split.py <YYYY-MM-DD> <ndays>   (default 06-22 +14d -> fit 7d / test 7d)
"""
import sys
import numpy as np
from datetime import datetime, timezone, timedelta
import linelab as LL
import siglab

TFS = list(range(6, 31))
THRS = list(range(3, 27))
CADENCE = 's5'
MINF = 5             # min fires per HALF per DIRECTION (must survive in both halves, both ways)
STOP = 1.0

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


def block(a, b):
    D = {}
    for d in (-1, 1):
        M = siglab.markers(cache, lab, CADENCE, a, b, TFS, d)
        STR = np.array([[m['strn'][tf] for tf in TFS] for m in M]) if M else np.zeros((0, len(TFS)))
        D[d] = dict(STR=STR, NET=np.array([m['mfe'] - m['mae'] for m in M]),
                    MAE=np.array([m['mae'] for m in M]), n=len(M))
    return D


FIT, TEST = block(S, MID), block(MID, E)
print('=== OOS split | %s | FIT %dd (S %d/L %d) -> TEST %dd (S %d/L %d) | cadence=%s ===' % (
    _day, _ndays // 2, FIT[-1]['n'], FIT[1]['n'], _ndays - _ndays // 2, TEST[-1]['n'], TEST[1]['n'], CADENCE))


def stats(B, cs, cf, ts_, tf_):
    out = {}
    for d in (-1, 1):
        m = (B[d]['STR'][:, cs] >= ts_) & (B[d]['STR'][:, cf] >= tf_)
        out[d] = (int(m.sum()), B[d]['NET'][m], B[d]['MAE'][m])
    return out


rows = []
for si, slow in enumerate(TFS):
    for fast in TFS[:si]:
        cs, cf = ti[slow], ti[fast]
        for ts_ in THRS:
            for tf_ in THRS:
                f = stats(FIT, cs, cf, ts_, tf_); t = stats(TEST, cs, cf, ts_, tf_)
                if min(f[-1][0], f[1][0], t[-1][0], t[1][0]) < MINF:
                    continue
                fsnet = float(np.median(f[-1][1])); flnet = float(np.median(f[1][1]))
                tsnet = float(np.median(t[-1][1])); tlnet = float(np.median(t[1][1]))
                fnet = float(np.median(np.concatenate([f[-1][1], f[1][1]])))
                tnet = float(np.median(np.concatenate([t[-1][1], t[1][1]])))
                tn = np.concatenate([t[-1][2], t[1][2]]); tbank = 100 * np.sum(tn < STOP) / len(tn)
                # ROBUST score: worst of {fit, test} AND worst of {short, long} across both halves -> nothing hides
                robust = min(fnet, tnet, fsnet, flnet, tsnet, tlnet)
                rows.append((robust, fnet, tnet, slow, fast, ts_, tf_, t[-1][0] + t[1][0],
                             tbank, fsnet, flnet, tsnet, tlnet))
rows.sort(reverse=True)
print('-- TOP 15 by ROBUST = min(fitNet, testNet, each dir each half), of %d survivors --' % len(rows))
print(' slow>=t & fast>=t | ROBUST | fit->test | test bank | fit S/L | test S/L')
for r in rows[:15]:
    robust, fnet, tnet, slow, fast, ts_, tf_, tn_, tbank, fsnet, flnet, tsnet, tlnet = r
    print('  s%d>=%-2d & s%d>=%-2d | %+5.2f | %+.2f->%+.2f | %3d%% | %+.2f/%+.2f | %+.2f/%+.2f' % (
        slow, ts_, fast, tf_, robust, fnet, tnet, round(tbank), fsnet, flnet, tsnet, tlnet))
if not rows:
    print('  (no config fired >=%d in BOTH halves BOTH directions)' % MINF)
