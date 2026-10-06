"""JOE 1005: "let's test these. if we can't pick a common thread then I'll let the hypothesis go"

THE HYPOTHESIS UNDER TEST (Joe's, from the 10-04 afternoon diff table):
  at a ws1Mage extrema -> ib cross, the per-line Mage diff carries a signature that marks the
  leg's turn. Two terms were separable on the first two legs:
    MAGNITUDE  — absolute diff on the tail lines ws8..ws12 (and on ws1), ranked within the leg
    ENGAGEMENT — tail/ws5: does the tail decay above ws5, or move as much as ws5 does
  12:16 (Joe's named pivot) was rank 1 of 19 on EVERY absolute measure and tail/ws5 = 0.94.
  The afternoon leg reproduced the magnitude term (15:04, 15:18) but NOT the engagement term
  (every afternoon event 0.19..0.57). The 0.8 engagement threshold is MINE, fitted to one event.

SIX LEGS, ONE RIG LOAD. The two already seen, plus Joe's four new ones, built by the SAME
producer so every comparison column comes from one run of one piece of code.

EVENT DEFINITION (unchanged from the 10-04 run, magediff2):
  one row per ws1Mage oob->ib cross whose cross bar lies inside the leg window; the row is
  anchored to the most extreme ws1Mage of the run since the previous cross. rev_wob 2 fires on
  any 2-bar run so it marks every micro-wiggle (171 revs in 75 min on 10-04 pm) -- the cross is
  the dedup key, the extrema is "the value inside ws1mage-rev" at the turn.

NO pxs. Raw Mage data and ws1Mage oob/ib crosses only, per Joe's standing constraint on this
line of work. Nothing here measures distance to a pivot.

JOE'S EYES ON THE FOUR PICKS (1005) -- this is the ground truth in this file:
    10-03 10:47  "is on pivot"
    10-03 08:19  "is only 10 minutes late"
    10-04 03:35  "was also 10 minutes late"
    10-04 06:11  "was not close, BUT 10 minutes earlier would have looked like a reversal because
                  market went sideways for the previous 20 minutes. observation: 06:11 might have
                  been overruled if the 13-23 Mages were employed"

AND THE LADDER WAS TRUNCATED. rig.tfs is 1..23 and ws13..ws23 all carry a fully populated Mage
(1,622,940 finite bars on ws23, to 10-04 23:59). The first run read ws1..ws12 only -- `range(1,13)`
was mine, not Joe's. The ladder now runs to ws23 and the ws13..ws23 band is reported as its own
term, which is what Joe's 06:11 observation asks for.
"""
import sys, datetime as dt
import numpy as np
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')
import sweep as W, upstream as UP

LEGS = [
    ('10-04 morning  (seen: Joe names 12:16 the pivot)', '2026-10-04 09:46:00', '2026-10-04 13:00:00'),
    ('10-04 afternoon (seen: Joe flagged 15:04, 15:18)', '2026-10-04 14:10:00', '2026-10-04 15:25:00'),
    ('10-04 05:16 -> 08:30',                             '2026-10-04 05:16:00', '2026-10-04 08:30:00'),
    ('10-04 00:35 -> 04:00',                             '2026-10-04 00:35:00', '2026-10-04 04:00:00'),
    ('10-03 09:35 -> 11:30',                             '2026-10-03 09:35:00', '2026-10-03 11:30:00'),
    ('10-03 05:33 -> 09:00',                             '2026-10-03 05:33:00', '2026-10-03 09:00:00'),
]

ms = int(dt.datetime(2026, 10, 4, tzinfo=dt.timezone.utc).timestamp() * 1000)
UP._cached_rig((ms, ms + 86400000)); R = UP._RIG
from optimus9.analysis.jig import oob_ib_cross

HI = float(R.C['oob_hi']); LO = float(R.C['oob_lo']); XW = int(R.C['boundary_xwob'])
g1 = np.asarray(R.lines['ws1']['Mage'], float); ts = np.asarray(R.ts, np.int64)
K = lambda s: int(np.searchsorted(ts, int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                   .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)))
U = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, dt.timezone.utc).strftime('%H:%M:%S')

NAMES = []
for n, key in (('g5', 'gcws5'), ('g15', 'gcws15'), ('g30', 'gcws30')):
    if key in R.lines: NAMES.append((n, np.asarray(R.lines[key]['Mage'], float)))
NAMES += [('ws%d' % t, np.asarray(R.lines['ws%d' % t]['Mage'], float)) for t in range(1, 24)]
WS = {n: v for n, v in NAMES}
LAD = ['ws%d' % t for t in range(1, 24)]          # the full 23-rung ladder
TAIL = slice(7, 12)    # ws8..ws12  -- the band the original signature read
UPPER = slice(12, 23)  # ws13..ws23 -- the band Joe asks about at 06:11

ALLX = oob_ib_cross(g1, HI, LO, XW)
print('# oob fence %.1f / %.1f | boundary_xwob %d | lines in the Rig: %s'
      % (HI, LO, XW, ', '.join(n for n, _ in NAMES)))
print('# NOTE gcws5 / gcws15 are absent from the Rig line set, so the ladder starts at ws1.')
print()

SUM = []
for title, t0, t1 in LEGS:
    A, B = K(t0), K(t1)
    cr = [c for c in ALLX if A <= c[0] <= B]
    print('=' * 100)
    print('## LEG  %s' % title)
    print('#  %s -> %s   bars %d -> %d   (%.0f min)   ib crosses in window: %d'
          % (t0, t1, A, B, (ts[B] - ts[A]) / 60000.0, len(cr)))
    print()
    if not cr:
        print('no ws1Mage oob->ib cross inside this window.'); print(); continue
    rows = []; prev = A
    for c in cr:
        ib, side = c[0], c[2]
        seg = g1[prev:ib]
        if not len(seg) or not np.isfinite(seg).any(): prev = ib; continue
        ex = prev + (int(np.nanargmax(seg)) if side > 0 else int(np.nanargmin(seg)))
        rows.append((ex, ib, side)); prev = ib
    print('| # | ws1Mage extrema | value | side | first ib cross | ib value | bars | mins |')
    print('|' + '---|' * 8)
    for i, (ex, ib, side) in enumerate(rows, 1):
        print('| %d | **%s** | **%.2f** | %s | **%s** | %.2f | %d | %.1f |'
              % (i, U(ex), g1[ex], 'hi' if side > 0 else 'lo', U(ib), g1[ib], ib - ex,
                 (ts[ib] - ts[ex]) / 60000.0))
    print()
    E = [U(ex)[:5] for ex, ib, s in rows]
    G = np.array([[WS[n][ib] - WS[n][ex] for ex, ib, s in rows] for n in LAD])   # 23 x nEvents
    AG = np.abs(G)
    print('## DIFF PER LINE — Mage at the ib cross MINUS Mage at the ws1Mage extrema')
    print('| line | ' + ' | '.join('%s->%s' % (U(ex)[:5], U(ib)[:5]) for ex, ib, s in rows) + ' |')
    print('|' + '---|' * (len(rows) + 1))
    for n, v in NAMES:
        print('| **%s** | ' % n + ' | '.join(
            ('—' if not (np.isfinite(v[ex]) and np.isfinite(v[ib])) else '%+.2f' % (v[ib] - v[ex]))
            for ex, ib, s in rows) + ' |')
    print()
    tail = AG[TAIL].mean(0); head = AG[0:3].mean(0); whole = AG[0:12].mean(0); rel = tail / AG[4]
    ws1 = AG[0]; ratio = AG[11] / AG[0]
    up = AG[UPPER].mean(0); upr = up / AG[0]; uptail = up / tail
    print('## THE SIGNATURE, RANKED BY ABSOLUTE TAIL MOVEMENT (mean |diff| ws8..ws12)')
    print('| rank | event | **tail ws8-12** | **upper ws13-23** | **upper/tail** | upper/ws1 | tail/ws5 | ws1 | ws12/ws1 |')
    print('|' + '---|' * 9)
    order = np.argsort(-tail)
    for r, j in enumerate(order, 1):
        print('| %d | **%s** | **%.2f** | **%.2f** | **%.2f** | %.3f | %.2f | %.2f | %.3f |'
              % (r, E[j], tail[j], up[j], uptail[j], upr[j], rel[j], ws1[j], ratio[j]))
    print()
    print('## RANKED BY THE UPPER BAND ws13..ws23 — the band the first run never read')
    print('| rank | event | **upper ws13-23** | tail ws8-12 | upper/tail | ws1 |')
    print('|' + '---|' * 6)
    for r, j in enumerate(np.argsort(-up), 1):
        print('| %d | **%s** | **%.2f** | %.2f | %.2f | %.2f |' % (r, E[j], up[j], tail[j], uptail[j], ws1[j]))
    print()
    j0 = int(order[0]); j1 = int(order[1]) if len(order) > 1 else j0
    sep = tail[j0] / tail[j1] if len(order) > 1 and tail[j1] > 0 else float('nan')
    agree = (int(np.argmax(ws1)) == j0) and (int(np.argmax(whole)) == j0)
    print('## THE TOP PICK\'S LADDER, rung by rung, all 23')
    print('| line | |diff| at %s | as a share of ws1 |' % E[j0])
    print('|---|---|---|')
    for t in range(23):
        print('| %s | **%.2f** | %.3f |' % (LAD[t], AG[t, j0], AG[t, j0] / AG[0, j0]))
    print()
    print('| the pick | value |')
    print('|---|---|')
    print('| top by tail | **%s** (tail %.2f) |' % (E[j0], tail[j0]))
    print('| 2nd by tail | %s (tail %.2f) |' % (E[j1], tail[j1]))
    print('| separation top/2nd | **%.2f x** |' % sep)
    print('| ws1 rank-1 event | %s |' % E[int(np.argmax(ws1))])
    print('| whole-ladder rank-1 event | %s |' % E[int(np.argmax(whole))])
    print('| all three absolute measures agree? | **%s** |' % ('YES' if agree else 'NO'))
    print('| top pick tail/ws5 | **%.2f** |' % rel[j0])
    print('| max tail/ws5 anywhere in leg | %.2f (at %s) |' % (rel.max(), E[int(np.argmax(rel))]))
    print('| any event ENGAGED (tail/ws5 > 0.8) | **%s** |' % ('YES' if (rel > 0.8).any() else 'NO'))
    print()
    print('| the upper band at the pick | value |')
    print('|---|---|')
    print('| upper ws13-23 at %s | **%.2f** |' % (E[j0], up[j0]))
    print('| upper/tail at %s | **%.2f** |' % (E[j0], uptail[j0]))
    print('| rank of %s on the upper band | **%d of %d** |'
          % (E[j0], 1 + int((up > up[j0]).sum()), len(rows)))
    print('| top by upper band | **%s** (upper %.2f) |' % (E[int(np.argmax(up))], up.max()))
    print()
    SUM.append(dict(leg=title, n=len(rows), top=E[j0], tail=tail[j0], tail2=tail[j1], sep=sep,
                    agree=agree, rel=rel[j0], relmax=rel.max(),
                    relmax_at=E[int(np.argmax(rel))], eng=bool((rel > 0.8).any()),
                    ws1top=E[int(np.argmax(ws1))], ws1=ws1[j0],
                    up=up[j0], uptail=uptail[j0], uprank=1 + int((up > up[j0]).sum()),
                    uptop=E[int(np.argmax(up))], upmax=up.max()))

print('=' * 100)
print('## CROSS-LEG: IS THERE A COMMON THREAD?')
print('| leg | events | top by tail | tail | sep x | **upper ws13-23** | **upper/tail** | upper rank of the pick | top by upper | upper max |')
print('|' + '---|' * 10)
for s in SUM:
    print('| %s | %d | **%s** | %.2f | %.2f | **%.2f** | **%.2f** | **%d of %d** | **%s** | %.2f |'
          % (s['leg'], s['n'], s['top'], s['tail'], s['sep'], s['up'], s['uptail'],
             s['uprank'], s['n'], s['uptop'], s['upmax']))
print()
print('| term | legs where it holds | legs tested |')
print('|---|---|---|')
print('| magnitude picks ONE event (3 absolute measures agree) | **%d** | %d |'
      % (sum(1 for s in SUM if s['agree']), len(SUM)))
print('| that pick is separated >= 2x from the 2nd | **%d** | %d |'
      % (sum(1 for s in SUM if s['sep'] >= 2.0), len(SUM)))
print('| engagement: some event reaches tail/ws5 > 0.8 | **%d** | %d |'
      % (sum(1 for s in SUM if s['eng']), len(SUM)))
print('| engagement: the TOP PICK reaches tail/ws5 > 0.8 | **%d** | %d |'
      % (sum(1 for s in SUM if s['rel'] > 0.8), len(SUM)))
print('| the tail pick is ALSO rank 1 on the upper band ws13-23 | **%d** | %d |'
      % (sum(1 for s in SUM if s['uprank'] == 1), len(SUM)))
