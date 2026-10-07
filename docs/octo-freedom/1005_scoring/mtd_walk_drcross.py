"""How many rows had their routing read at a bar whose dr differs from the octo-sig's dr.

THE DEFECT, found 1006 from Joe's challenge on 09-30 15:24:55. score39.classify walks forward up to
MTD_WALK_BARS when mtd(k) returns neither r1 nor r2:

    for j in range(k + 1, min(TAPE_LAST, k + MTD_WALK_BARS) + 1):
        m2 = mtd(j)
        if m2['route'] in ('mtd.r1', 'mtd.r2'):
            m, kw = m2, j; break

There is NO dr GUARD. mtd(j) reads DRv[j], so if dr flips inside the walk window the whole branch-D
read - blk, keep, the r ladder, the mage net, the grade - is taken on the OPPOSITE fence from the
signal's own dr, while os_dr still records the signal's dr. The row looks self-consistent and is not.

Measured: 09-30 15:25:45 is dr +1, mtd(15:25:45) is `neither` with ex 15:22:10, the walk moves ONE
bar to 15:25:50 where dr is -1, and the row takes that bar's mtd.r1 and its ex 15:24:55.

THIS FILE ONLY COUNTS. It changes nothing.
"""
import os, io, contextlib, re
import numpy as np
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

DAYS = os.environ.get('LG_DAYS',
    '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
    '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
H, L = SC.pivots(float(SC.LG['swing'])); BLOCK = float(SC.LG['mae_block'])

rows = []
for day in DAYS:
    p = os.path.join('octosig', '%s.out' % day)
    if not os.path.exists(p): continue
    for ln in open(p):
        if not ln.startswith('R|'): continue
        f = ln.rstrip('\n').split('|')
        if len(f) < 7 or not re.match(r'^\d\d:\d\d:\d\d$', f[2]): continue
        k = SC.K('%s %s' % (day, f[2]))
        d0 = int(SC.DRv[k])
        m0 = SC.mtd(k)
        kw, dw = k, d0
        if m0['route'] not in ('mtd.r1', 'mtd.r2') and SC.MTD_WALK_BARS > 0:
            for j in range(k + 1, min(SC.TAPE_LAST, k + SC.MTD_WALK_BARS) + 1):
                m2 = SC.mtd(j)
                if m2['route'] in ('mtd.r1', 'mtd.r2'):
                    kw, dw = j, int(SC.DRv[j]); break
        r = SC.classify(k, f[2])
        D = r.get('D') or {}
        wt = (r['status'] == 'CONFLUENCE' and not D.get('away', True))
        side = ('LONG' if d0 > 0 else 'SHORT') if wt or D.get('why') == 'no r block' \
               else ('SHORT' if d0 > 0 else 'LONG')
        fv, av, _ = SC.score(kw if kw > k else k, (-d0 if (wt or D.get('why') == 'no r block') else d0), H, L)
        rows.append(dict(day=day, sig=f[2], dr=d0, drw=dw, walked=(kw != k),
                         crossed=(kw != k and dw != d0), bars=(kw - k),
                         status=r['status'], grade=r['grade'], route=r['m'].get('route'),
                         why=D.get('why'), wt=wt, side=side, mae=av, mfe=fv))

n = len(rows)
cr = [r for r in rows if r['crossed']]
print('# THE mtd WALK CROSSING A dr FLIP   MTD_WALK_BARS %d bars = %d s   %s'
      % (SC.MTD_WALK_BARS, SC.MTD_WALK_BARS * 5, SC.LG_KEY))
print('\n| | rows | of %d | days |' % n); print('|---|---|---|---|')
w = [r for r in rows if r['walked']]
print('| total octo-sigs | %d | 100%% | %d |' % (n, len({r['day'] for r in rows})))
print('| the mtd walk ran | %d | %.1f%% | %d |' % (len(w), 100.0*len(w)/n, len({r['day'] for r in w})))
print('| **the walk CROSSED a dr flip** | **%d** | **%.1f%%** | %d |'
      % (len(cr), 100.0*len(cr)/n, len({r['day'] for r in cr})))

print('\n# THE CROSSED ROWS, BY GRADE')
print('| status | grade | crossed rows | of all crossed |'); print('|---|---|---|---|')
g = {}
for r in cr: g[(r['status'], r['grade'])] = g.get((r['status'], r['grade']), 0) + 1
for k2 in sorted(g, key=lambda x: -g[x]):
    print('| %s | %s | %d | %.1f%% |' % (k2[0], k2[1], g[k2], 100.0*g[k2]/len(cr) if cr else 0))

wt_all = [r for r in rows if r['wt']]
wt_cr = [r for r in cr if r['wt']]
print('\n# with-trend SPECIFICALLY')
print('| | rows | days |'); print('|---|---|---|')
print('| with-trend, all | %d | %d |' % (len(wt_all), len({r['day'] for r in wt_all})))
print('| **with-trend that CROSSED a dr flip** | **%d** | %d |'
      % (len(wt_cr), len({r['day'] for r in wt_cr})))
print('| with-trend crossed, as %% of with-trend | %.1f%% | |'
      % (100.0*len(wt_cr)/len(wt_all) if wt_all else 0))

if cr:
    print('\n# EVERY CROSSED ROW')
    print('| day | octo-sig | sig dr | walked dr | bars walked | status | grade | side | MAE | MFE |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    fm = lambda v: ('%.4f' % v) if v is not None else '—'
    for r in sorted(cr, key=lambda x: (x['day'], x['sig'])):
        print('| %s | %s | %+d | %+d | %d | %s | %s | %s | %s | %s |'
              % (r['day'], r['sig'], r['dr'], r['drw'], r['bars'], r['status'], r['grade'],
                 r['side'], fm(r['mae']), fm(r['mfe'])))

print('\n# BARS WALKED, WHERE THE WALK RAN')
b = {}
for r in w: b[r['bars']] = b.get(r['bars'], 0) + 1
print('| bars walked | rows | of which crossed a flip |'); print('|---|---|---|')
for k2 in sorted(b):
    print('| %d | %d | %d |' % (k2, b[k2], sum(1 for r in cr if r['bars'] == k2)))
