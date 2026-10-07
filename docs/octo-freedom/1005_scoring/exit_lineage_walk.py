"""THE EXIT — Joe's spec, 1006/1007.

JOE, verbatim:
  *"exit is simple:
    - walk forward with the already opened trade
    - at the first octo-sig that is NOT graded as `with-trend` or `no r block`
    -- follow the momentum using the exact same mech that walks octo-sig forward
    -- when the momentum reaches it's final `stalled`, exit the trade"*

`lineage walk` IS JOE'S TERM, adopted 1007.

THE OPEN TRADE is any octo-sig graded `with-trend` or `no r block` - the two that flip to the
counter-dr side. The EXIT TRIGGER is the first later octo-sig graded neither.

THE EXIT WALK IS THE SAME MECH, unchanged: lineage_walk.walk() from the trigger's g5extrema, rider =
the highest oob TF in ws1..ws12, baton passes on an oob crossing within +2 TF numbers, upward only.
Its terminal `rider stalled` is the exit bar.

NO DAY BOUNDARY. Every octo-sig across all 12 days is loaded into ONE list sorted by bar, so a trade
opened late in a day finds its trigger on the next one rather than being cut off by the file layout.
Joe has never named a holding limit and none is imposed.

THE ENTRY IS CAUSAL: max(octo-sig bar, the mtd walk's qualifying bar, the g5extrema). That is the fix
measured 1006 - the banked table still stamps max(octo-sig bar, g5extrema) and is 0.807 MFE richer
across 12 days because of it.

THREE THINGS JOE HAS NOT RULED, counted not assumed:
  1. whose SIDE sets the exit walk's backstop - the open trade's, or the trigger octo-sig's own.
     Both are computed. A is the open trade's side, B is the trigger's.
  2. the trigger has NO RIDER (an empty r ladder), so the exit walk cannot start.
  3. the exit walk ends on the dr BACKSTOP rather than a stall. Joe said exit on the final `stalled`.
"""
import os, io, contextlib, re
import numpy as np
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
import lineage_walk as LW

OPEN_GRADES = ('with-trend', 'no r block')
DAYS = os.environ.get('LG_DAYS',
    '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
    '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
H, L = SC.pivots(float(SC.LG['swing']))

sigs = []
for day in DAYS:
    p = os.path.join('octosig', '%s.out' % day)
    if not os.path.exists(p): continue
    for ln in open(p):
        if not ln.startswith('R|'): continue
        f = ln.rstrip('\n').split('|')
        if len(f) < 7 or not re.match(r'^\d\d:\d\d:\d\d$', f[2]): continue
        k = SC.K('%s %s' % (day, f[2]))
        d = int(SC.DRv[k])
        if d == 0: continue
        r = SC.classify(k, f[2]); D = r.get('D') or {}
        ex = int(r['m']['ex']) if r['m'].get('ex') is not None else k
        kw = int(r['kw'])
        entry = max(k, kw, ex)                      # the causal stamp
        g = D.get('why') if D.get('why') == 'no r block' else r['grade']
        sigs.append(dict(day=day, sig=f[2], k=k, entry=entry, ex=ex, dr=d, grade=g,
                         openable=(g in OPEN_GRADES),
                         side=('LONG' if d > 0 else 'SHORT')))   # both open grades flip counter-dr
sigs.sort(key=lambda x: x['k'])

def run(trig, side):
    return LW.walk(SC.Rl, SC.DRv, None, SC.ts and 0, 0, trig['ex'], trig['dr'],
                   SC.HI, SC.LO, SC.TAPE_LAST, LIN_TF, LIN_HOP, side)

print('# THE EXIT — Joe\'s lineage walk from the first non-tradeable octo-sig   %s' % SC.LG_KEY)
print('\n| | count |'); print('|---|---|')
print('| octo-sigs, all days | %d |' % len(sigs))
for g in sorted({s['grade'] for s in sigs}):
    print('| grade `%s` | %d |' % (g, sum(1 for s in sigs if s['grade'] == g)))
op = [s for s in sigs if s['openable']]
tr = [s for s in sigs if not s['openable']]
print('| **open trades** (with-trend + no r block) | **%d** |' % len(op))
print('| **possible exit triggers** | **%d** |' % len(tr))

print('\n# DOES EVERY OPEN TRADE FIND A TRIGGER?')
found = 0; gap = []
for t in op:
    nxt = next((s for s in tr if s['k'] > t['entry']), None)
    t['trig'] = nxt
    if nxt: found += 1; gap.append((int(SC.ts[nxt['k']]) - int(SC.ts[t['entry']])) / 60000.0)
print('| | count |'); print('|---|---|')
print('| open trades with a later trigger | %d of %d |' % (found, len(op)))
print('| open trades with NO trigger to the end of the tape | %d |' % (len(op) - found))
if gap:
    g = sorted(gap)
    print('\n| wait for the trigger, minutes | value |'); print('|---|---|')
    print('| min | %.1f |' % g[0]); print('| median | %.1f |' % g[len(g)//2]); print('| max | %.1f |' % g[-1])

print('\n# THE TRIGGERS, BY GRADE')
tg = {}
for t in op:
    if t.get('trig'): tg[t['trig']['grade']] = tg.get(t['trig']['grade'], 0) + 1
print('| trigger grade | open trades it would close |'); print('|---|---|')
for k2 in sorted(tg, key=lambda x: -tg[x]): print('| %s | %d |' % (k2, tg[k2]))

print('\n# CAN THE EXIT WALK START? (the trigger needs a rider at its g5extrema)')
nr = 0
for t in op:
    x = t.get('trig')
    if not x: continue
    if 'rider' not in x:
        x['rider'] = LW.rider_at(SC.Rl, x['ex'], x['dr'], SC.HI, SC.LO, LIN_TF)
    if x['rider'] is None: nr += 1
print('| | count |'); print('|---|---|')
print('| trigger HAS a rider - the exit walk starts | %d |' % (found - nr))
print('| **trigger has NO rider - the walk cannot start** | **%d** |' % nr)
