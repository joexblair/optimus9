"""`no r block` at the episode level, with Joe's 75% MFE capture.

JOE 1006: *"re the exit: now that we have the skill to walk a signal forward, I'm going to assume we
can achieve at least 75% of MFE. let's bake that in to your workings"*.

MFE_CAPTURE IS AN ASSUMPTION, NOT A MEASUREMENT. No exit mech exists in this project; score39.score
runs to the next favourable PIVOT with NO STOP. 0.75 is Joe's stated floor for what a forward walk
should reach, and every number below that uses it is labelled as his assumption.

IT IS NOT IN lazy_g_config. It changes no banked column - nothing in octosig_rulings reads it - and
adding a knob bumps the config version and therefore the knob key. It moves into the config the
moment an exit mech makes it touch a row.

MAE IS NOT SUBTRACTED. There is no stop, so MAE is the drawdown the fire endured on the way, not a
realised cost. Capture is 0.75 * MFE and MAE is reported beside it as the risk that was carried.

THE EPISODE, NOT THE ROW. Two octo-sigs can resolve to the same g5extrema bar; they are one event
with identical MAE and MFE, and counting both doubles it. The episode key is (day, g5extrema bar).
"""
import os, io, contextlib, re
import numpy as np
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

MFE_CAPTURE = 0.75
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
        fv, av, _ = SC.score(kk, -d, H, L)                 # counter-dr, the baked side
        if av is None or fv is None: continue
        rows.append(dict(day=day, sig=f[2], ex=SC.U(ex), exk=ex, dr=d, mae=av, mfe=fv))

# ---- episodes
ep = {}
for r in rows: ep.setdefault((r['day'], r['exk']), []).append(r)
dupes = {k: v for k, v in ep.items() if len(v) > 1}
episodes = []
for k in sorted(ep):
    g = ep[k]
    episodes.append(dict(day=g[0]['day'], ex=g[0]['ex'], dr=g[0]['dr'], n=len(g),
                         sigs=', '.join(x['sig'] for x in g),
                         mae=g[0]['mae'], mfe=g[0]['mfe'],
                         same=all(abs(x['mae'] - g[0]['mae']) < 1e-9 and abs(x['mfe'] - g[0]['mfe']) < 1e-9 for x in g)))

print('# `no r block`, EPISODE LEVEL, counter-dr side   swing %.2f   capture %.0f%% of MFE (Joe 1006)'
      % (float(SC.LG['swing']), MFE_CAPTURE * 100))
print('\n| | rows | episodes | days |'); print('|---|---|---|---|')
print('| population | %d | %d | %d |' % (len(rows), len(episodes), len({r['day'] for r in rows})))
print('| g5extrema bars carrying more than one octo-sig | | %d | |' % len(dupes))
bad = [k for k, v in dupes.items() if not all(abs(x['mae'] - v[0]['mae']) < 1e-9 for x in v)]
print('| of those, rows DISAGREEING on MAE/MFE | | %d | |' % len(bad))

if dupes:
    print('\n# THE SHARED BARS — what got counted twice')
    print('| day | g5extrema | octo-sigs | MAE | MFE |'); print('|---|---|---|---|---|')
    for k in sorted(dupes):
        v = dupes[k]
        print('| %s | %s | %s | %.4f | %.4f |' % (v[0]['day'], v[0]['ex'],
              ', '.join(x['sig'] for x in v), v[0]['mae'], v[0]['mfe']))

def block(sub, lbl):
    if not sub: return None
    mae = sorted(x['mae'] for x in sub); mfe = sorted(x['mfe'] for x in sub)
    cap = [MFE_CAPTURE * x['mfe'] for x in sub]
    return (lbl, len(sub), len({x['day'] for x in sub}),
            mae[len(mae)//2], mfe[len(mfe)//2],
            sum(1 for x in sub if x['mfe'] > x['mae']),
            sum(1 for x in sub if x['mae'] > BLOCK),
            sum(cap), sum(cap) / len(cap), sum(x['mfe'] for x in sub))

print('\n# THE NUMBERS — row level vs episode level, in-sample (all 12 days)')
print('| unit | n | days | median MAE | median MFE | MFE>MAE | MAE>%.2f | sum MFE | sum CAPTURE @75%% | mean capture |' % BLOCK)
print('|---|---|---|---|---|---|---|---|---|---|')
for sub, lbl in ((rows, 'row'), (episodes, 'EPISODE')):
    b = block(sub, lbl)
    print('| %s | %d | %d | %.4f | %.4f | %d of %d | %d | %+.3f | %+.3f | %+.4f |'
          % (b[0], b[1], b[2], b[3], b[4], b[5], b[1], b[6], b[9], b[7], b[8]))

ds = sorted({r['day'] for r in rows}); fitd, oosd = set(ds[:8]), set(ds[8:])
print('\n# HELD OUT — FIT the first 8 days, OOS the last 4, EPISODE level')
print('- FIT %s' % ', '.join(sorted(fitd)))
print('- OOS %s' % ', '.join(sorted(oosd)))
print('\n| window | episodes | days | median MAE | median MFE | MFE>MAE | MAE>%.2f | sum MFE | sum CAPTURE @75%% | mean capture |' % BLOCK)
print('|---|---|---|---|---|---|---|---|---|---|')
for lbl, dd in (('FIT 8 days', fitd), ('OOS 4 days', oosd)):
    b = block([e for e in episodes if e['day'] in dd], lbl)
    if not b: continue
    print('| %s | %d | %d | %.4f | %.4f | %d of %d | %d | %+.3f | %+.3f | %+.4f |'
          % (b[0], b[1], b[2], b[3], b[4], b[5], b[1], b[6], b[9], b[7], b[8]))

print('\n# PER DAY, EPISODE LEVEL')
print('| day | episodes | sum MFE | sum CAPTURE @75%% | median MAE | worst MAE |')
print('|---|---|---|---|---|---|')
for d in ds:
    sub = [e for e in episodes if e['day'] == d]
    if not sub: continue
    print('| %s | %d | %+.3f | %+.3f | %.4f | %.4f |'
          % (d, len(sub), sum(x['mfe'] for x in sub), sum(MFE_CAPTURE * x['mfe'] for x in sub),
             sorted(x['mae'] for x in sub)[len(sub)//2], max(x['mae'] for x in sub)))
