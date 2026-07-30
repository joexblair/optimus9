"""build_feature_hunt — which gap-report column actually predicts a good trade? (Joe 0725). SAVED.

Open hunt, NOT assuming the fitted rolled-s4 + dtf_now + s10 rule. For every s5 cadence marker (both dirs) it
computes each candidate feature per TF and correlates it (rank/Spearman, threshold-free so it can't overfit a cut)
with the trade's net = MFE-MAE (swing-to-pivot @2%). Ranks features by how well they separate winners from losers.
A feature that beats dtf_now_s10 is a DIFFERENT rule worth chasing.
Features per TF: dtf_now (favourable strength vs s4) · gapval (raw x-m) · dtime (gap change since last marker) ·
                 dtf_prev (last marker's strength). Plus gap_s4 itself.
Usage: build_feature_hunt.py <YYYY-MM-DD start> <ndays>   (default: whole tape)
"""
import sys
import numpy as np
import linelab as LL
import siglab

TFS = list(range(4, 31)); CADENCE = 's5'


def spearman(x, y):
    """rank correlation, NaN-safe, threshold-free."""
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 12:
        return np.nan, int(m.sum())
    xr = np.argsort(np.argsort(x[m])).astype(float); yr = np.argsort(np.argsort(y[m])).astype(float)
    xr -= xr.mean(); yr -= yr.mean()
    denom = np.sqrt((xr * xr).sum() * (yr * yr).sum())
    return (float((xr * yr).sum() / denom) if denom else np.nan), int(m.sum())


for tf in TFS:
    LL.register('s%dx' % tf, kind='bb', tf=tf, length=5, mult=0.37)
    LL.register('s%dm' % tf, kind='bb', tf=tf, length=6, mult=0.45)
cache, ets, epx, names = LL.warm(rebuild=False)
lab = siglab.Lab(cache, ets, epx)
import time as _t
S = None; E = None
if len(sys.argv) > 1 and sys.argv[1][:1].isdigit():
    from datetime import datetime, timezone, timedelta
    d0 = datetime.strptime(sys.argv[1], '%Y-%m-%d').replace(tzinfo=timezone.utc)
    nd = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    S = int(d0.timestamp() * 1000); E = int((d0 + timedelta(days=nd)).timestamp() * 1000)
else:
    S, E = int(ets[0]), int(ets[-1])

# markers both dirs, merged chronologically for the temporal (dtime / dtf_prev) features
M = []
for d in (-1, 1):
    for m in siglab.markers(cache, lab, CADENCE, S, E, TFS, d):
        M.append(m)
M.sort(key=lambda m: m['tms'])
print('=== feature hunt | %s..%s | %d markers (both dirs) | swing 2%% ===' % (
    _t.strftime('%m-%d', _t.gmtime(S / 1000)), _t.strftime('%m-%d', _t.gmtime(E / 1000)), len(M)))

# per-marker features
gapval = {m['tms']: {tf: m['gap_s4'] - m['d'] * m['strn'][tf] for tf in TFS} for m in M}  # x-m recovered
for i, m in enumerate(M):
    m['gv'] = gapval[m['tms']]
    m['dtime'] = {tf: (m['gv'][tf] - M[i - 1]['gv'][tf]) if i else np.nan for tf in TFS}
    m['prevstrn'] = {tf: (M[i - 1]['strn'][tf]) if i else np.nan for tf in TFS}
    m['net'] = m['mfe'] - m['mae']

FEATS = {'dtf_now': lambda m, tf: m['strn'][tf], 'gapval': lambda m, tf: m['gv'][tf],
         'dtime': lambda m, tf: m['dtime'][tf], 'dtf_prev': lambda m, tf: m['prevstrn'][tf]}

for dname, dsel in (('SHORT', -1), ('LONG', 1)):
    sub = [m for m in M if m['d'] == dsel]
    net = np.array([m['net'] for m in sub])
    rows = []
    for fname, ff in FEATS.items():
        for tf in TFS:
            fv = np.array([ff(m, tf) for m in sub], float)
            rho, n = spearman(fv, net)
            if np.isfinite(rho):
                rows.append((abs(rho), rho, fname, tf, n))
    rows.sort(reverse=True)
    print('\n-- %s (%d) | top 12 features by |rank-corr with net| --' % (dname, len(sub)))
    print('  |rho|  rho    feature      TF')
    for a, rho, fname, tf, n in rows[:12]:
        star = '  <- dtf_now_s10 (the fitted rule)' if (fname == 'dtf_now' and tf == 10) else ''
        print('  %.2f  %+.2f  %-9s   s%d%s' % (a, rho, fname, tf, star))
    # where does the fitted rule rank?
    for k, (a, rho, fname, tf, n) in enumerate(rows):
        if fname == 'dtf_now' and tf == 10:
            print('  ...dtf_now_s10 ranks #%d of %d (|rho|=%.2f)' % (k + 1, len(rows), a)); break
