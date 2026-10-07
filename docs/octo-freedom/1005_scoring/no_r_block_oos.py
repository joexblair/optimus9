"""`no r block` — Joe's r-vs-Mage rule, held out. Joe 1006: *"the only path to the truth is OOS.
using MAEMFE, find the best solution"*.

THE MECH IS JOE'S, UNCHANGED. `under` = how many of ws1..ws12 have r BELOW Mage at the g5extrema
bar. dr +1 fires LONG when `under` >= T; dr -1 fires SHORT when (lines - under) >= T. The ONLY free
knob is T, "mostly".

THE PROTOCOL. 46 rows over 12 days is too small for one split to mean anything, so T is chosen
LEAVE-ONE-DAY-OUT: for each day, T is picked on the other 11 days and applied to the held-out day,
and every held-out row is pooled. Each day is OOS exactly once and no row ever helps choose the T
that scores it. A straight chronological split is reported beside it as the cruder check.

THE DAY IS THE BLOCK UNIT, not the row - rows cluster on a g5extrema bar, so episode counts are
printed next to every row count and no rate appears without one.

TWO OBJECTIVES, both reported, because they pull opposite ways and the honest answer is whether they
agree: SUM(MFE - MAE) rewards firing more, MEAN(MFE - MAE) per row rewards firing better.
"""
import os, io, contextlib, re
import numpy as np
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

DAYS = os.environ.get('LG_DAYS',
    '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
    '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
SWING = float(SC.LG['swing']); BLOCK = float(SC.LG['mae_block'])
H, L = SC.pivots(SWING)
TF = SC.TF
TS = list(range(0, 13))                       # T 0 = no filter at all, the baseline

rows = []
for day in DAYS:
    p = os.path.join('octosig', '%s.out' % day)
    if not os.path.exists(p): continue
    for ln in open(p):
        if not ln.startswith('R|'): continue
        f = ln.rstrip('\n').split('|')
        if len(f) < 7 or not re.match(r'^\d\d:\d\d:\d\d$', f[2]): continue
        k = SC.K('%s %s' % (day, f[2]))
        r = SC.classify(k, f[2])
        if (r.get('D') or {}).get('why') != 'no r block': continue
        ex = int(r['m']['ex']) if r['m'].get('ex') is not None else k
        d = int(SC.DRv[k])
        if d == 0: continue
        under = sum(1 for t in TF if np.isfinite(SC.Rl[t][ex]) and np.isfinite(SC.Mg[t][ex])
                    and float(SC.Rl[t][ex]) < float(SC.Mg[t][ex]))
        fin = sum(1 for t in TF if np.isfinite(SC.Rl[t][ex]) and np.isfinite(SC.Mg[t][ex]))
        kk = ex if ex > k else k
        fv, av, _ = SC.score(kk, -d, H, L)                 # the counter-dr side, Joe's rule
        if av is None or fv is None: continue
        rows.append(dict(day=day, sig=f[2], ex=SC.U(ex), dr=d, under=under, fin=fin,
                         lead=(under if d > 0 else fin - under), mae=av, mfe=fv))

fires = lambda r, T: r['lead'] >= T
def stat(sub):
    if not sub: return None
    mae = sorted(x['mae'] for x in sub); mfe = sorted(x['mfe'] for x in sub)
    return dict(n=len(sub), days=len({x['day'] for x in sub}),
                ep=len({(x['day'], x['ex']) for x in sub}),
                mae=mae[len(mae)//2], mfe=mfe[len(mfe)//2],
                gt=sum(1 for x in sub if x['mfe'] > x['mae']),
                blk=sum(1 for x in sub if x['mae'] > BLOCK),
                tot=sum(x['mfe'] - x['mae'] for x in sub),
                avg=sum(x['mfe'] - x['mae'] for x in sub) / len(sub))

print('# `no r block`, JOE\'S r-vs-Mage RULE, HELD OUT   swing %.2f   block %.2f   %s'
      % (SWING, BLOCK, SC.LG_KEY))
print('# %d rows, %d days, %d distinct g5extrema bars. T 0 = no filter.'
      % (len(rows), len({r['day'] for r in rows}), len({(r['day'], r['ex']) for r in rows})))

print('\n# IN-SAMPLE, every T — all 12 days, for reference only')
print('| T | rows | episodes | days | median MAE | median MFE | MFE>MAE | MAE>%.2f | sum(MFE-MAE) | mean per row |' % BLOCK)
print('|---|---|---|---|---|---|---|---|---|---|')
for T in TS:
    s = stat([r for r in rows if fires(r, T)])
    if not s: continue
    print('| %d | %d | %d | %d | %.4f | %.4f | %d of %d | %d | %+.3f | %+.4f |'
          % (T, s['n'], s['ep'], s['days'], s['mae'], s['mfe'], s['gt'], s['n'], s['blk'], s['tot'], s['avg']))

print('\n# LEAVE-ONE-DAY-OUT — T chosen on 11 days, applied to the 12th, every held-out row pooled')
for oname, okey in (('SUM(MFE-MAE)', 'tot'), ('MEAN(MFE-MAE) per row', 'avg')):
    held, chosen = [], {}
    for d in sorted({r['day'] for r in rows}):
        fit = [r for r in rows if r['day'] != d]
        best, bestv = None, None
        for T in TS:
            s = stat([r for r in fit if fires(r, T)])
            if not s: continue
            if bestv is None or s[okey] > bestv: best, bestv = T, s[okey]
        chosen[d] = best
        held += [r for r in rows if r['day'] == d and fires(r, best)]
    s = stat(held)
    print('\n## objective on the FIT days: %s' % oname)
    print('| OOS pooled | rows | episodes | days | median MAE | median MFE | MFE>MAE | MAE>%.2f | sum(MFE-MAE) | mean per row |' % BLOCK)
    print('|---|---|---|---|---|---|---|---|---|---|')
    if s:
        print('| held-out | %d | %d | %d | %.4f | %.4f | %d of %d | %d | %+.3f | %+.4f |'
              % (s['n'], s['ep'], s['days'], s['mae'], s['mfe'], s['gt'], s['n'], s['blk'], s['tot'], s['avg']))
    print('\n| held-out day | T picked on the other 11 |'); print('|---|---|')
    for d in sorted(chosen): print('| %s | %s |' % (d, chosen[d]))

print('\n# CHRONOLOGICAL SPLIT — FIT the first 8 days, OOS the last 4')
ds = sorted({r['day'] for r in rows}); fitd, oosd = set(ds[:8]), set(ds[8:])
print('- FIT %s' % ', '.join(sorted(fitd)))
print('- OOS %s' % ', '.join(sorted(oosd)))
print('\n| T | FIT rows | FIT mean per row | OOS rows | OOS episodes | OOS median MAE | OOS median MFE | OOS MFE>MAE | OOS MAE>%.2f | OOS mean per row |' % BLOCK)
print('|---|---|---|---|---|---|---|---|---|---|')
for T in TS:
    sf = stat([r for r in rows if r['day'] in fitd and fires(r, T)])
    so = stat([r for r in rows if r['day'] in oosd and fires(r, T)])
    if not sf or not so: continue
    print('| %d | %d | %+.4f | %d | %d | %.4f | %.4f | %d of %d | %d | %+.4f |'
          % (T, sf['n'], sf['avg'], so['n'], so['ep'], so['mae'], so['mfe'],
             so['gt'], so['n'], so['blk'], so['avg']))
