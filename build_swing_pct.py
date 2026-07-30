"""build_swing_pct — is the edge yardstick-dependent? (Joe 0725). SAVED. TEST ONLY — 1% stays operating.

Same entries (cadence s5, s4 episode, rule s10>=16), re-scored at swing_detect 0.5 / 1 / 2%. Entry selection does
NOT depend on swing_pct (only MFE/MAE does), so this isolates the yardstick. If the edge holds at 1% but craters at
0.5% and balloons at 2%, the 1% swing is the mechanic. NO verdict — prints the numbers.
Usage: build_swing_pct.py <YYYY-MM-DD> <ndays>   (default 06-22 +14d)
"""
import sys
import numpy as np
from datetime import datetime, timezone, timedelta
import linelab as LL
import siglab

TFS = list(range(6, 31))
FAST, THR = 10, 16              # the robust single-s10 rule
CADENCE = 's5'

_day = next((a for a in sys.argv[1:] if a[:1].isdigit() and '-' in a), '2026-06-22')
_ndays = next((int(a) for a in sys.argv[1:] if a.isdigit()), 14)
_d0 = datetime.strptime(_day, '%Y-%m-%d').replace(tzinfo=timezone.utc)
S = int(_d0.timestamp() * 1000); E = int((_d0 + timedelta(days=_ndays)).timestamp() * 1000)

for tf in TFS:
    LL.register('s%dx' % tf, kind='bb', tf=tf, length=5, mult=0.37)
    LL.register('s%dm' % tf, kind='bb', tf=tf, length=6, mult=0.45)
cache, ets, epx, names = LL.warm(rebuild=False)

print('=== swing-%% sensitivity | %s +%dd | rule s10>=%d | cadence=%s | TEST ONLY (1%% stays operating) ===' % (
    _day, _ndays, THR, CADENCE))
print(' swing | dir   | fires | MFE  | MAE  | net   | bank')
for sp in (0.5, 1.0, 2.0):
    lab = siglab.Lab(cache, ets, epx, swing_pct=sp)
    for d, name in ((-1, 'SHORT'), (1, 'LONG')):
        M = siglab.markers(cache, lab, CADENCE, S, E, [FAST], d)
        rows = [m for m in M if m['strn'][FAST] >= THR]
        if not rows:
            print('  %4.1f%% | %-5s | 0' % (sp, name)); continue
        mfe = np.array([r['mfe'] for r in rows]); mae = np.array([r['mae'] for r in rows])
        net = mfe - mae; bank = 100 * np.sum(mae < 1.0) / len(rows)
        print('  %4.1f%% | %-5s | %5d | %4.2f | %4.2f | %+5.2f | %3d%%' % (
            sp, name, len(rows), float(np.median(mfe)), float(np.median(mae)), float(np.median(net)), round(bank)))
