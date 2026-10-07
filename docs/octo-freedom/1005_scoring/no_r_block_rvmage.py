"""Joe's route for `no r block`: r vs Mage positioning across the wsf lines.

JOE 1006, verbatim:
  *"test the r vs Mage postioning (ie is r above or below Mage?) across all wsf lines"*
  *"if r is 'mostly' underneath Mage, then Mage is leading upward. for 19:49 +1dr, this makes it a
   `with-trend` moment, and a LONG position is opened"*
  *"the held out data will need to define 'mostly'"*
  *"inverse for -1dr"*

WHAT `no r block` IS. score39.branchD:151 builds `blk` = every TF in ws1..ws12 whose r is oob on the
dr side at the g5extrema bar. Empty blk -> empty keep -> :162 returns why='no r block'. It is not a
rejection; branch D has no wall to test a claim against, so it says nothing. 19:49:55's r ladder is
twelve dots - not one line oob, not one even in the 83..85 band.

THE STATISTIC. `under` = how many of ws1..ws12 have r BELOW Mage at the g5extrema bar. Both arrays
are score39's own Rl and Mg, read at the same bar branch D read.

  dr +1 : Mage leading UP  (under high)  -> LONG
  dr -1 : Mage leading DOWN (under low)  -> SHORT

"MOSTLY" IS NOT PICKED HERE. Every threshold from 7..12 of 12 is reported with its own population
and episode count. Joe picks it from the held-out data; this file measures, it does not choose.

SCORED AT THE STAMPED BAR, the same bar os_mae_traded uses, so the numbers are comparable to what is
already banked. `no r block` rows have no rider, so the lineage walk produces no walked bar for them.
"""
import os, sys, io, contextlib, re
import numpy as np
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

DAYS = os.environ.get('LG_DAYS',
    '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
    '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
SWING = float(SC.LG['swing'])
H, L = SC.pivots(SWING)
TF = SC.TF

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
        D = r.get('D') or {}
        if D.get('why') != 'no r block': continue
        ex = int(r['m']['ex']) if r['m'].get('ex') is not None else k
        d = int(SC.DRv[k])
        if d == 0: continue
        under = sum(1 for t in TF if np.isfinite(SC.Rl[t][ex]) and np.isfinite(SC.Mg[t][ex])
                    and float(SC.Rl[t][ex]) < float(SC.Mg[t][ex]))
        fin = sum(1 for t in TF if np.isfinite(SC.Rl[t][ex]) and np.isfinite(SC.Mg[t][ex]))
        kk = ex if ex > k else k                       # the stamped bar, as octosig_db stamps it
        fs, as_, _ = SC.score(kk, +1, H, L)            # SHORT
        fl, al, _ = SC.score(kk, -1, H, L)             # LONG
        rows.append(dict(day=day, sig=f[2], ex=SC.U(ex), stamp=SC.U(kk), dr=d, under=under, fin=fin,
                         mae_s=as_, mfe_s=fs, mae_l=al, mfe_l=fl))

print('# `no r block` ROWS — r vs Mage at the g5extrema   swing %.2f   %s' % (SWING, SC.LG_KEY))
print('# under = how many of ws1..ws12 have r BELOW Mage. dr +1 wants it HIGH, dr -1 wants it LOW.')
print('\n| day | octo-sig | g5extrema | stamped | dr | under of 12 | MAE LONG | MFE LONG | MAE SHORT | MFE SHORT |')
print('|---|---|---|---|---|---|---|---|---|---|')
fm = lambda v: ('%.4f' % v) if v is not None else '—'
for r in rows:
    print('| %s | %s | %s | %s | %+d | %d of %d | %s | %s | %s | %s |'
          % (r['day'], r['sig'], r['ex'], r['stamp'], r['dr'], r['under'], r['fin'],
             fm(r['mae_l']), fm(r['mfe_l']), fm(r['mae_s']), fm(r['mfe_s'])))
print('\n- %d `no r block` rows across %d days' % (len(rows), len({r['day'] for r in rows})))
print('- dr +1: %d   dr -1: %d' % (sum(1 for r in rows if r['dr'] > 0), sum(1 for r in rows if r['dr'] < 0)))

print('\n# THE `under` DISTRIBUTION')
print('| under of 12 | dr +1 rows | dr -1 rows |'); print('|---|---|---|')
for u in range(0, 13):
    a = sum(1 for r in rows if r['under'] == u and r['dr'] > 0)
    b = sum(1 for r in rows if r['under'] == u and r['dr'] < 0)
    if a or b: print('| %d | %d | %d |' % (u, a, b))

print('\n# EVERY "MOSTLY" THRESHOLD — what Joe\'s rule takes, and what it scores')
print('# dr +1 fires LONG when under >= T. dr -1 fires SHORT when (12 - under) >= T.')
print('\n| T of 12 | rows fired | days | distinct g5extrema bars | median MAE | median MFE | MFE>MAE | MAE>0.70 |')
print('|---|---|---|---|---|---|---|---|')
for T in range(7, 13):
    fired = []
    for r in rows:
        lead = r['under'] if r['dr'] > 0 else (r['fin'] - r['under'])
        if lead < T: continue
        mae, mfe = (r['mae_l'], r['mfe_l']) if r['dr'] > 0 else (r['mae_s'], r['mfe_s'])
        if mae is None or mfe is None: continue
        fired.append((r, mae, mfe))
    if not fired:
        print('| %d | 0 | 0 | 0 | — | — | — | — |' % T); continue
    maes = sorted(x[1] for x in fired); mfes = sorted(x[2] for x in fired)
    print('| %d | %d | %d | %d | %.4f | %.4f | %d of %d | %d |'
          % (T, len(fired), len({x[0]['day'] for x in fired}), len({(x[0]['day'], x[0]['ex']) for x in fired}),
             maes[len(maes)//2], mfes[len(mfes)//2],
             sum(1 for x in fired if x[2] > x[1]), len(fired),
             sum(1 for x in fired if x[1] > float(SC.LG['mae_block']))))

print('\n# THE OPPOSITE SIDE, same rows — the control')
print('| T of 12 | rows | median MAE | median MFE | MFE>MAE |'); print('|---|---|---|---|---|')
for T in range(7, 13):
    fired = []
    for r in rows:
        lead = r['under'] if r['dr'] > 0 else (r['fin'] - r['under'])
        if lead < T: continue
        mae, mfe = (r['mae_s'], r['mfe_s']) if r['dr'] > 0 else (r['mae_l'], r['mfe_l'])
        if mae is None or mfe is None: continue
        fired.append((mae, mfe))
    if not fired: print('| %d | 0 | — | — | — |' % T); continue
    maes = sorted(x[0] for x in fired); mfes = sorted(x[1] for x in fired)
    print('| %d | %d | %.4f | %.4f | %d of %d |'
          % (T, len(fired), maes[len(maes)//2], mfes[len(mfes)//2],
             sum(1 for x in fired if x[1] > x[0]), len(fired)))

# ---- THE BASELINE. `under` is near-determined by dr (dr -1 rows all sit at under <= 3, dr +1 rows
# mostly at 12), so the rule fires on almost the whole population. This is what "always take the
# counter-dr side on every `no r block` row, no filter at all" scores - the thing the `under`
# threshold has to beat to be earning anything.
print('\n# THE BASELINE — no `under` filter, every `no r block` row, counter-dr side')
print('| population | rows | days | distinct g5extrema bars | median MAE | median MFE | MFE>MAE | MAE>0.70 |')
print('|---|---|---|---|---|---|---|---|')
for lbl, pick in (('counter-dr (what the rule takes)', 'flip'), ('dr-bias side', 'bias')):
    f = []
    for r in rows:
        if pick == 'flip':
            mae, mfe = (r['mae_l'], r['mfe_l']) if r['dr'] > 0 else (r['mae_s'], r['mfe_s'])
        else:
            mae, mfe = (r['mae_s'], r['mfe_s']) if r['dr'] > 0 else (r['mae_l'], r['mfe_l'])
        if mae is None or mfe is None: continue
        f.append((r, mae, mfe))
    maes = sorted(x[1] for x in f); mfes = sorted(x[2] for x in f)
    print('| %s | %d | %d | %d | %.4f | %.4f | %d of %d | %d |'
          % (lbl, len(f), len({x[0]['day'] for x in f}), len({(x[0]['day'], x[0]['ex']) for x in f}),
             maes[len(maes)//2], mfes[len(mfes)//2],
             sum(1 for x in f if x[2] > x[1]), len(f),
             sum(1 for x in f if x[1] > float(SC.LG['mae_block']))))

print('\n# HOW MUCH OF THE POPULATION EACH THRESHOLD KEEPS')
print('| T of 12 | dr +1 kept of 24 | dr -1 kept of 22 | total kept of 46 |')
print('|---|---|---|---|')
for T in range(7, 13):
    a = sum(1 for r in rows if r['dr'] > 0 and r['under'] >= T)
    b = sum(1 for r in rows if r['dr'] < 0 and (r['fin'] - r['under']) >= T)
    print('| %d | %d | %d | %d |' % (T, a, b, a + b))
