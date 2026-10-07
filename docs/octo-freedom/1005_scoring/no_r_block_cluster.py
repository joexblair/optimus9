"""Joe's cluster read and his 2-trades-at-1-minute rule, on the `no r block` population.

JOE 1006: *"if there's multiple signals wrapping up, that means they've built over a large leg (ie,
we've seen the early reversals and carried them) - more early reversal in a leg = larger leg =
larger reversal - my call, based on this idea, is that we place 2 trades at 1 minute intervals"*.

TWO SEPARATE THINGS ARE MEASURED.
  1. THE IDEA. Do signals that share a g5extrema bar carry a LARGER MFE than solo ones? That is
     Joe's claim and it stands or falls on its own, independent of what we then do about it.
  2. THE RULE. Trade 1 at the first octo-sig of the cluster, trade 2 exactly SPACING_S later,
     scored against what the cluster's own second octo-sig bar gave.

SPACING IS JOE'S, 60 s = 12 bars at the 5 s grid. It is not swept.

NO DEDUP. Joe ruled two signals on one extrema are two trades, so the row is the unit and the
earlier episode-level figures are withdrawn.
"""
import os, io, contextlib, re
import numpy as np
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

MFE_CAPTURE = 0.75
SPACING_S = 60
GRID_S = 5
SPACING_BARS = SPACING_S // GRID_S
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
        k = SC.K('%s %s' % (day, f[2])); r = SC.classify(k, f[2])
        if (r.get('D') or {}).get('why') != 'no r block': continue
        ex = int(r['m']['ex']) if r['m'].get('ex') is not None else k
        d = int(SC.DRv[k])
        if d == 0: continue
        kk = ex if ex > k else k
        fv, av, _ = SC.score(kk, -d, H, L)
        if av is None or fv is None: continue
        rows.append(dict(day=day, sig=f[2], ex=SC.U(ex), exk=ex, sigk=k, scork=kk, dr=d, mae=av, mfe=fv))

cl = {}
for r in rows: cl.setdefault((r['day'], r['exk']), []).append(r)
for v in cl.values(): v.sort(key=lambda x: x['sigk'])
for r in rows: r['clustered'] = len(cl[(r['day'], r['exk'])]) > 1

print('# `no r block` — JOE\'S CLUSTER READ   swing %.2f   capture %.0f%%   spacing %d s = %d bars'
      % (float(SC.LG['swing']), MFE_CAPTURE * 100, SPACING_S, SPACING_BARS))
print('# NO DEDUP - Joe ruled two signals on one g5extrema are two trades.')

print('\n# 1. THE IDEA — do clustered signals carry a larger MFE than solo ones?')
print('| group | rows | g5extrema bars | days | median MFE | mean MFE | max MFE | median MAE | MFE>MAE |')
print('|---|---|---|---|---|---|---|---|---|')
for lbl, sub in (('CLUSTERED (share a g5extrema)', [r for r in rows if r['clustered']]),
                 ('solo', [r for r in rows if not r['clustered']])):
    if not sub: continue
    mfe = sorted(x['mfe'] for x in sub); mae = sorted(x['mae'] for x in sub)
    print('| %s | %d | %d | %d | %.4f | %.4f | %.4f | %.4f | %d of %d |'
          % (lbl, len(sub), len({(x['day'], x['exk']) for x in sub}), len({x['day'] for x in sub}),
             mfe[len(mfe)//2], sum(mfe)/len(mfe), max(mfe), mae[len(mae)//2],
             sum(1 for x in sub if x['mfe'] > x['mae']), len(sub)))

print('\n# 2. THE RULE — trade 1 at the first octo-sig, trade 2 at +%d s' % SPACING_S)
print('| day | g5extrema | trade 1 bar | MAE1 | MFE1 | trade 2 bar (+%ds) | MAE2 | MFE2 | the cluster\'s own 2nd sig | its MAE | its MFE |' % SPACING_S)
print('|---|---|---|---|---|---|---|---|---|---|---|')
pair = []
for key in sorted(cl):
    v = cl[key]
    if len(v) < 2: continue
    a = v[0]
    k2 = a['scork'] + SPACING_BARS
    if k2 > SC.TAPE_LAST: continue
    f2, a2, _ = SC.score(k2, -a['dr'], H, L)
    b = v[1]
    print('| %s | %s | %s | %.4f | %.4f | %s | %s | %s | %s | %.4f | %.4f |'
          % (a['day'], a['ex'], SC.U(a['scork']), a['mae'], a['mfe'], SC.U(k2),
             ('%.4f' % a2) if a2 is not None else '—', ('%.4f' % f2) if f2 is not None else '—',
             b['sig'], b['mae'], b['mfe']))
    if a2 is not None and f2 is not None:
        pair.append(dict(day=a['day'], m1=a['mae'], f1=a['mfe'], m2=a2, f2=f2,
                         mb=b['mae'], fb=b['mfe']))

if pair:
    print('\n# THE RULE vs WHAT THE SIGNALS ACTUALLY GAVE, %d clusters' % len(pair))
    print('| trade 2 sourced from | sum MFE | sum CAPTURE @75%% | median MAE | worst MAE | MFE>MAE |')
    print('|---|---|---|---|---|---|')
    for lbl, mk, fk in (('+%d s after trade 1 (Joe\'s rule)' % SPACING_S, 'm2', 'f2'),
                        ('the cluster\'s own 2nd octo-sig', 'mb', 'fb')):
        mm = sorted(p[mk] for p in pair); ff = [p[fk] for p in pair]
        print('| %s | %+.3f | %+.3f | %.4f | %.4f | %d of %d |'
              % (lbl, sum(ff), MFE_CAPTURE * sum(ff), mm[len(mm)//2], max(mm),
                 sum(1 for p in pair if p[fk] > p[mk]), len(pair)))
    f1 = [p['f1'] for p in pair]; m1 = sorted(p['m1'] for p in pair)
    print('| trade 1 alone, for reference | %+.3f | %+.3f | %.4f | %.4f | %d of %d |'
          % (sum(f1), MFE_CAPTURE * sum(f1), m1[len(m1)//2], max(m1),
             sum(1 for p in pair if p['f1'] > p['m1']), len(pair)))

print('\n# THE WHOLE POPULATION, ROW LEVEL, NO DEDUP')
mfe = sorted(x['mfe'] for x in rows); mae = sorted(x['mae'] for x in rows)
cap = [MFE_CAPTURE * x['mfe'] for x in rows]
print('| rows | g5extrema bars | days | median MAE | median MFE | MFE>MAE | MAE>%.2f | sum MFE | sum CAPTURE @75%% | mean capture |' % BLOCK)
print('|---|---|---|---|---|---|---|---|---|---|')
print('| %d | %d | %d | %.4f | %.4f | %d of %d | %d | %+.3f | %+.3f | %+.4f |'
      % (len(rows), len(cl), len({x['day'] for x in rows}), mae[len(mae)//2], mfe[len(mfe)//2],
         sum(1 for x in rows if x['mfe'] > x['mae']), len(rows),
         sum(1 for x in rows if x['mae'] > BLOCK), sum(mfe), sum(cap), sum(cap)/len(cap)))
