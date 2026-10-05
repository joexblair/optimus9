"""7-day forward projection by DAY-BLOCK bootstrap over the 9 measured days. Joe 1005: "7 day forecast".

Blocks are whole DAYS, drawn with replacement, so within-day clustering and the day-to-day spread
are both preserved. 20,000 draws. This is a resample of measured results, not a model: it cannot
know about regimes the 9 days do not contain.
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, io, os, contextlib, json
import numpy as np
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
exec(open(_os.path.join(_HERE, 'ninedays.py')).read().split('ALL = {}')[0])
ALL = {}
for day in DAYS: ALL[day] = day_rows(day)
rng = np.random.default_rng(20261005)

def proj(key, label, Ls=(1, 2, 3, 5, 10)):
    blocks = [np.array([x[key] for x in sorted([y for y in ALL[d] if y['status'] == 'CONFLUENCE'],
                                               key=lambda y: y['open_ms'])]) for d in DAYS]
    blocks = [b for b in blocks if b.size]
    print()
    print('## %s — 7 days drawn from the 9, 20,000 paths' % label)
    print('| L | p5 equity x | p25 | median | p75 | p95 | mean | P(final < 1.0) | P(max DD > 50%) | P(wiped) |')
    print('|' + '---|' * 10)
    for Lv in Ls:
        fin = np.empty(20000); dds = np.empty(20000); wipe = 0
        for t in range(20000):
            idx = rng.integers(0, len(blocks), 7)
            eq = 1.0; pk = 1.0; dd = 0.0; dead = False
            for i in idx:
                for r in blocks[i]:
                    f = 1.0 + Lv * r / 100.0
                    if f <= 0: dead = True; break
                    eq *= f; pk = max(pk, eq); dd = max(dd, (pk - eq) / pk)
                if dead: break
            if dead: eq = 0.0; dd = 1.0; wipe += 1
            fin[t] = eq; dds[t] = dd
        q = np.percentile(fin, [5, 25, 50, 75, 95])
        print('| %dx | %.4f | %.4f | **%.4f** | %.4f | %.4f | %.4f | %.1f %% | %.1f %% | %.2f %% |'
              % (Lv, q[0], q[1], q[2], q[3], q[4], fin.mean(),
                 (fin < 1.0).mean() * 100, (dds > 0.5).mean() * 100, wipe / 200.0))

print('# 7-DAY FORWARD PROJECTION — day-block bootstrap of the 9 measured days (09-25 .. 10-03)')
print()
print('## THE PER-DAY INPUT — what is being resampled')
print('| day | conf trades | total net % | mean net % | total net % UNFLIPPED |')
print('|' + '---|' * 5)
for d in DAYS:
    g = [x for x in ALL[d] if x['status'] == 'CONFLUENCE']
    print('| %s | %d | %+.3f | %+.3f | %+.3f |' % (d[5:], len(g), sum(x['net'] for x in g),
          float(np.mean([x['net'] for x in g])), sum(x['net_asis'] for x in g)))
allc = [x for d in DAYS for x in ALL[d] if x['status'] == 'CONFLUENCE']
print('| **9 days** | %d | **%+.3f** | %+.3f | **%+.3f** |' % (len(allc), sum(x['net'] for x in allc),
      float(np.mean([x['net'] for x in allc])), sum(x['net_asis'] for x in allc)))
proj('net', 'A — with the stage 2 flip (what I built this session)')
proj('net_asis', 'B — WITHOUT the flip, dr-bias side throughout')
