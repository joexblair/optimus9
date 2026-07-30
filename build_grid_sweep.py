"""build_grid_sweep — HTF confluence-TF x threshold grid for the short locator (Joe 0724). SAVED.

Foundation locked: cadence=s5, s4 episode line, swing_detect-1% swing-to-pivot MAE/MFE, 18-min lookback.
Sweeps the ENGAGED confluence line's TF (the HTF whose dtf_now gates the short) and the threshold knob.
Precomputes per marker ONCE (T*, gap_s4, dtf_now for every candidate HTF, entry offset/MFE/MAE), then the grid
is pure filtering. Rule per cell: short + gapval_s4<=0 + dtf_now_{HTF} >= thr. Ranked by median net (MFE-MAE),
fires>=FLOOR. Also reports the current max(s15,s22)>=10 multi-dim combo + the best TF PAIR as a max() combo.
Usage: build_grid_sweep.py <YYYY-MM-DD start> <ndays>   (default 06-22 +7d)
"""
import sys
import numpy as np
from datetime import datetime, timezone, timedelta
import linelab as LL
import optimus9.orchestration.rpl_walk as R
from optimus9.compute.swing_detect import find_pivots

HTF_TFS = [10, 12, 14, 15, 16, 18, 20, 22, 26, 30]
THRS = [5, 6, 8, 10, 12, 15, 20]
CADENCE = 's5'
LOOKBACK = int(18 * 60 / 5)
FLOOR = 15                      # min fires over the window to rank a cell (avoid rare-setup cherry-picking)
STOP = 1.0

_day = next((a for a in sys.argv[1:] if a[:1].isdigit() and '-' in a), '2026-06-22')
_ndays = next((int(a) for a in sys.argv[1:] if a.isdigit()), 7)
_d0 = datetime.strptime(_day, '%Y-%m-%d').replace(tzinfo=timezone.utc)
S = int(_d0.timestamp() * 1000); E = int((_d0 + timedelta(days=_ndays)).timestamp() * 1000)

# register any missing HTF candidate lines, then warm (per-line cache -> only new ones compute)
for tf in HTF_TFS:
    LL.register('s%dx' % tf, kind='bb', tf=tf, length=5, mult=0.37)
    LL.register('s%dm' % tf, kind='bb', tf=tf, length=6, mult=0.45)
cache, ets, epx, names = LL.warm(rebuild=False)
ts = cache.ts
s4x = LL.line(cache, 's4x'); s4m = LL.line(cache, 's4m')
HX = {tf: LL.line(cache, 's%dx' % tf) for tf in HTF_TFS}
HM = {tf: LL.line(cache, 's%dm' % tf) for tf in HTF_TFS}
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


def score_entry(t):
    j = min(int(np.searchsorted(ets, t)), len(epx) - 1); entry = float(epx[j])
    lowi = min([p for p in Ls if p > j], default=len(epx) - 1)
    seg = epx[j:lowi + 1]
    mfe = (entry - float(seg.min())) / entry * 100
    mae = max(0.0, (float(seg.max()) - entry) / entry * 100)
    topi = max([p for p in Hs if p <= j], default=None)
    off = ((float(epx[topi]) - entry) / float(epx[topi]) * 100) if topi is not None else None
    return off, mfe, mae


# ---- precompute markers once ----
cad = LL.xm_cross(cache, CADENCE, wob=6, lookback_tf=3, min_dwell_s=180, align_line=None, start=S, end=E)
seen, M = set(), []
for tms, bd in cad:
    if bd != -1:
        continue
    star = s4_hi_extreme(tms)
    if star is None or star in seen:
        continue
    seen.add(star)
    gap_s4 = float(s4x[star] - s4m[star])
    if gap_s4 > 0:                                    # s4 must have rolled
        continue
    dtf = {tf: float(HX[tf][star] - HM[tf][star]) - gap_s4 for tf in HTF_TFS}
    off, mfe, mae = score_entry(tms)
    M.append(dict(dtf=dtf, off=off, mfe=mfe, mae=mae))
print('=== grid | %s +%dd | cadence=%s | %d rolled-s4 short markers ===' % (_day, _ndays, CADENCE, len(M)))


def agg(rows):
    if not rows:
        return None
    off = [r['off'] for r in rows if r['off'] is not None]; mfe = [r['mfe'] for r in rows]; mae = [r['mae'] for r in rows]
    net = [r['mfe'] - r['mae'] for r in rows]; bank = sum(1 for r in rows if r['mae'] < STOP)
    return dict(n=len(rows), off=float(np.median(off)) if off else float('nan'),
                mfe=float(np.median(mfe)), mae=float(np.median(mae)), net=float(np.median(net)),
                bank=bank, bankpct=100 * bank / len(rows))


cells = []
for tf in HTF_TFS:
    for thr in THRS:
        rows = [r for r in M if r['dtf'][tf] >= thr]
        a = agg(rows)
        if a and a['n'] >= FLOOR:
            cells.append((tf, thr, a))
cells.sort(key=lambda c: c[2]['net'], reverse=True)
print('\n-- TOP 12 cells by median net (MFE-MAE), fires>=%d --' % FLOOR)
print(' HTF thr | fires | offset | MFE   | MAE   | net    | bank')
for tf, thr, a in cells[:12]:
    print('  s%-3d %2d | %5d | %+5.2f%% | %5.2f | %5.2f | %+5.2f | %d%%' % (
        tf, thr, a['n'], a['off'], a['mfe'], a['mae'], a['net'], round(a['bankpct'])))

# reference: current multi-dim max(s15,s22)>=10, and the best single TF's pair as a max()
def combo(tfs, thr):
    rows = [r for r in M if max(r['dtf'][t] for t in tfs) >= thr]
    return agg(rows)
print('\n-- reference combos --')
for label, tfs, thr in [('max(s15,s22)>=10 [current]', [15, 22], 10),
                        ('single best cell', [cells[0][0]], cells[0][1])]:
    a = combo(tfs, thr)
    if a:
        print('  %-28s | fires %d | off %+.2f%% | MFE %.2f | MAE %.2f | net %+.2f | bank %d%%' % (
            label, a['n'], a['off'], a['mfe'], a['mae'], a['net'], round(a['bankpct'])))
# best pair max() among top TFs
top_tfs = sorted({tf for tf, _, _ in cells[:8]})
best_pair = None
for i in range(len(top_tfs)):
    for jx in range(i + 1, len(top_tfs)):
        for thr in THRS:
            a = combo([top_tfs[i], top_tfs[jx]], thr)
            if a and a['n'] >= FLOOR and (best_pair is None or a['net'] > best_pair[3]['net']):
                best_pair = (top_tfs[i], top_tfs[jx], thr, a)
if best_pair:
    t1, t2, thr, a = best_pair
    print('  best pair max(s%d,s%d)>=%d       | fires %d | off %+.2f%% | MFE %.2f | MAE %.2f | net %+.2f | bank %d%%' % (
        t1, t2, thr, a['n'], a['off'], a['mfe'], a['mae'], a['net'], round(a['bankpct'])))
