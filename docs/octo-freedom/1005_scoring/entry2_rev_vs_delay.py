"""THE POTENTIAL DIFF for MVP2 task #26 — trade 2 on a g5Mage same-side reversal vs a fixed delay.

JOE 1006: *"we could do better than a simple 1 minute delay between positions - if we fire on g5Mage
same-side reversing (2 bars to confirm) then we're guaranteed to optimise the entry"* and
*"not for now - we'll stash it for MVP2, but I'd be curious about the potential diff"*.

THREE PLACEMENTS FOR TRADE 2, every cluster, same side, same scoring:
  A  +SPACING_S after trade 1            - Joe's current rule, 60 s = 12 bars
  B  the next g5Mage same-side reversal  - the MVP2 proposal. LONG wants REV +1 (turning UP),
                                           SHORT wants REV -1. REV_WOB = 2 bars confirms the turn.
  C  the cluster's own 2nd octo-sig      - what the mech emits today

MEASURED, NOT BUILT. Nothing here changes a mech or a table.

THE CLUSTERS ARE RECOMPUTED WITH THE dr GUARD ON, so 09-30 15:24:55 is gone - it was a +1 LONG and a
-1 SHORT sharing an extrema only because the mtd walk crossed a dr flip.

NO REACH LIMIT on the reversal search, on purpose. Joe has not named one, and capping it would
manufacture the answer. The lag is reported so he can see how far it actually had to look.
"""
import os, io, contextlib, re
import numpy as np
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

CAP, SPACING_S, GRID_S = 0.75, 60, 5
SPACING_BARS = SPACING_S // GRID_S
DAYS = os.environ.get('LG_DAYS',
    '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
    '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
H, L = SC.pivots(float(SC.LG['swing']))

rows = []
for day in DAYS:
    p = os.path.join('octosig', '%s.out' % day)
    if not os.path.exists(p): continue
    for ln in open(p):
        if not ln.startswith('R|'): continue
        f = ln.rstrip('\n').split('|')
        if len(f) < 7 or not re.match(r'^\d\d:\d\d:\d\d$', f[2]): continue
        k = SC.K('%s %s' % (day, f[2])); r = SC.classify(k, f[2])
        if (r.get('D') or {}).get('why') != 'no r block': continue
        ex = int(r['m']['ex']) if r['m'].get('ex') is not None else k
        d = int(SC.DRv[k])
        if d == 0: continue
        rows.append(dict(day=day, sig=f[2], exts=SC.U(ex), exk=ex, k=k,
                         scork=(ex if ex > k else k), dr=d,
                         side=('LONG' if d > 0 else 'SHORT')))      # counter-dr, the baked flip

cl = {}
for r in rows: cl.setdefault((r['day'], r['exk']), []).append(r)
for v in cl.values(): v.sort(key=lambda x: x['k'])
pairs = [v for v in cl.values() if len(v) > 1]

sc = lambda bar, side: SC.score(bar, (-1 if side == 'LONG' else +1), H, L)
want = lambda side: (+1 if side == 'LONG' else -1)

print('# TRADE 2 PLACEMENT — the potential diff, MVP2 task #26   capture %.0f%% of MFE' % (CAP*100))
print('# clusters recomputed WITH the mtd-walk dr guard   %s' % SC.LG_KEY)
print('\n- `no r block` rows: %d   g5extrema bars: %d   clusters (2+ signals on one bar): %d'
      % (len(rows), len(cl), len(pairs)))
if not pairs:
    print('\n- no clusters survive the dr guard. Nothing to compare.'); raise SystemExit

print('\n# EACH CLUSTER')
print('| day | g5extrema | side | trade 1 | A +%ds | A MAE/MFE | B g5Mage rev | B lag s | B MAE/MFE | C own 2nd sig | C lag s | C MAE/MFE |' % SPACING_S)
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
agg = {'A': [], 'B': [], 'C': [], '1': []}
for v in pairs:
    a, b = v[0], v[1]
    side = a['side']
    k1 = a['scork']
    f1, m1, _ = sc(k1, side)
    kA = k1 + SPACING_BARS
    w = want(side)
    kB = next((i for i in range(k1 + 1, SC.TAPE_LAST + 1) if int(SC.REV[i]) == w), None)
    kC = b['scork']
    row = ['| %s | %s | %s | %s |' % (a['day'], a['exts'], side, SC.U(k1))]
    cells = {}
    for tag, kx in (('A', kA), ('B', kB), ('C', kC)):
        if kx is None or kx > SC.TAPE_LAST: cells[tag] = (None, None, None, None); continue
        fx, mx, _ = sc(kx, side)
        cells[tag] = (kx, mx, fx, (int(SC.ts[kx]) - int(SC.ts[k1])) / 1000.0)
    fmt = lambda t: ('%.4f / %.4f' % (cells[t][1], cells[t][2])) if cells[t][1] is not None else '—'
    bar = lambda t: SC.U(cells[t][0]) if cells[t][0] is not None else '—'
    lag = lambda t: ('%.0f' % cells[t][3]) if cells[t][0] is not None else '—'
    print('%s %s | %s | %s | %s | %s | %s | %s | %s |'
          % (row[0], bar('A'), fmt('A'), bar('B'), lag('B'), fmt('B'), bar('C'), lag('C'), fmt('C')))
    if m1 is not None: agg['1'].append((m1, f1))
    for t in ('A', 'B', 'C'):
        if cells[t][1] is not None: agg[t].append((cells[t][1], cells[t][2]))

print('\n# THE THREE PLACEMENTS, SUMMED OVER %d CLUSTERS' % len(pairs))
print('| trade 2 placement | n | median MAE | worst MAE | sum MFE | sum CAPTURE @75%% | MFE>MAE |')
print('|---|---|---|---|---|---|---|')
for tag, lbl in (('1', 'trade 1 alone, reference'),
                 ('A', 'A  +%d s fixed delay (today)' % SPACING_S),
                 ('B', 'B  g5Mage same-side reversal (MVP2)'),
                 ('C', 'C  the cluster\'s own 2nd octo-sig')):
    g = agg[tag]
    if not g: print('| %s | 0 | — | — | — | — | — |' % lbl); continue
    mm = sorted(x[0] for x in g); ff = [x[1] for x in g]
    print('| %s | %d | %.4f | %.4f | %+.3f | %+.3f | %d of %d |'
          % (lbl, len(g), mm[len(mm)//2], max(mm), sum(ff), CAP*sum(ff),
             sum(1 for x in g if x[1] > x[0]), len(g)))

print('\n# TWO TRADES TOTAL — trade 1 plus each trade 2')
print('| pairing | sum MFE | sum CAPTURE @75%% | diff vs A |'); print('|---|---|---|---|')
base = sum(x[1] for x in agg['1']) + sum(x[1] for x in agg['A'])
for tag, lbl in (('A', 'trade 1 + A (today)'), ('B', 'trade 1 + B (MVP2)'), ('C', 'trade 1 + C')):
    t = sum(x[1] for x in agg['1']) + sum(x[1] for x in agg[tag])
    print('| %s | %+.3f | %+.3f | %+.3f |' % (lbl, t, CAP*t, CAP*(t - base)))
