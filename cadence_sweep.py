"""cadence_sweep — does a SMALLER cadence TF pull the short entries earlier? (Joe 0724). SAVED.

Holds everything else fixed (s4 episode, s12/s15/s22 HTF confluence, rule) and sweeps ONLY the cadence line's TF.
Rule: short marker + gapval_s4<=0 + max(dtf_now_s15,dtf_now_s22)>=10, deduped by s4-episode T*.
Metric: median late-entry OFFSET (how far down the MFE side the entry fired) + swing_detect-1% MFE/MAE + bank rate.
Offset is frame-independent, so it answers the cadence question cleanly regardless of swing-vs-finisher MAE.
"""
import sys
import numpy as np
from datetime import datetime, timezone, timedelta
import linelab as LL
import optimus9.orchestration.rpl_walk as R
from optimus9.compute.swing_detect import find_pivots

_day = next((a for a in sys.argv[1:] if a[:1].isdigit() and '-' in a), '2026-06-26')   # start YYYY-MM-DD
_ndays = next((int(a) for a in sys.argv[1:] if a.isdigit()), 1)                        # window length in days
_d0 = datetime.strptime(_day, '%Y-%m-%d').replace(tzinfo=timezone.utc)
S = int(_d0.timestamp() * 1000)
E = int((_d0 + timedelta(days=_ndays)).timestamp() * 1000)
LOOKBACK = int(18 * 60 / 5)
cache, ets, epx, names = LL.warm(rebuild=False)
ts = cache.ts
L = {n: LL.line(cache, n) for n in ('s4x', 's4m', 's12x', 's12m', 's15x', 's15m', 's22x', 's22m')}
s4x = L['s4x']
piv = find_pivots(epx, 1.0)
Hs = [p for p, k in piv if k == 'H']; Ls = [p for p, k in piv if k == 'L']


def s4_hi_extreme(t):
    i = int(np.searchsorted(ts, t)); oob = s4x >= R.HI; j = i
    while j >= 0 and j > i - LOOKBACK and not oob[j]:
        j -= 1
    if j < 0 or j <= i - LOOKBACK or not oob[j]:
        return None
    lo = j
    while lo > 0 and oob[lo - 1]:
        lo -= 1
    hi = j
    while hi < len(oob) - 1 and oob[hi + 1]:
        hi += 1
    return lo + int(np.argmax(s4x[lo:hi + 1]))


def gaps_at(star):
    g = {}
    for tf in ('s4', 's12', 's15', 's22'):
        g[tf] = float(L[tf + 'x'][star] - L[tf + 'm'][star])
    return g


def score_entry(t):
    j = min(int(np.searchsorted(ets, t)), len(epx) - 1); entry = float(epx[j])
    topi = max([p for p in Hs if p <= j], default=None)
    lowi = min([p for p in Ls if p > j], default=len(epx) - 1)
    seg = epx[j:lowi + 1]
    mfe = (entry - float(seg.min())) / entry * 100
    mae = max(0.0, (float(seg.max()) - entry) / entry * 100)
    off = ((float(epx[topi]) - entry) / float(epx[topi]) * 100) if topi is not None else None
    return off, mfe, mae


print('=== cadence TF sweep | %s +%dd | rule: short + gapval_s4<=0 + max(dTFnow s15,s22)>=10 ===' % (_day, _ndays))
print('cadence | shorts | fires | med offset | med MFE | med MAE | bank')
for ctf in (4, 5, 6, 7, 8):
    cad = LL.xm_cross(cache, 's%d' % ctf, wob=6, lookback_tf=3, min_dwell_s=180, align_line=None, start=S, end=E)
    seen, fires = set(), []
    for tms, bd in cad:
        if bd != -1:
            continue
        star = s4_hi_extreme(tms)
        if star is None or star in seen:
            continue
        g = gaps_at(star)
        if not (g['s4'] <= 0 and max(g['s15'] - g['s4'], g['s22'] - g['s4']) >= 10):
            continue
        seen.add(star)
        off, mfe, mae = score_entry(tms)
        fires.append((off, mfe, mae))
    n_short = sum(1 for _, b in cad if b == -1)
    if fires:
        offs = [f[0] for f in fires if f[0] is not None]; mfes = [f[1] for f in fires]; maes = [f[2] for f in fires]
        bank = sum(1 for f in fires if f[2] < 1.0)
        print('  s%-5d | %6d | %5d | %+9.2f%% | %6.2f%% | %6.2f%% | %d/%d' % (
            ctf, n_short, len(fires), float(np.median(offs)), float(np.median(mfes)), float(np.median(maes)), bank, len(fires)))
    else:
        print('  s%-5d | %6d | %5d | (no fires)' % (ctf, n_short, len(fires)))
