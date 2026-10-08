"""JOE'S SELF-TEST ON THE REVERSED WALK. 1008.

Joe 1008: *"before you show it to me, test yourself first. the test is simple: is the pxs of the
open signal located at or near a pivot that supports my trade (eg low pxs pivot for a LONG trade)?
if yes, no lineage walk is needed, if no walk the lineage path that takes me to a better pxs (ie go
lower in pxs if the open is a LONG trade). if the lineage walk takes you to a higher pxs (ie with
the LONG trade), the lineage walk is facing the wrong direction"*.

THE TEST, run on every arm-5 leg. No pivot knob is invented; the pivot question is asked in the
only knob-free form there is:

  does the open bar already hold the best pxs?   the best pxs in the span the walk traversed -
                                                 the LOWEST for a LONG, the HIGHEST for a SHORT.
                                                 If the open bar holds it, no walk can improve on
                                                 it and every walk must land worse.
  did the walk land on a better pxs?             the sign of the entry improvement. NEGATIVE means
                                                 the walk faced the WRONG DIRECTION, by Joe's test.
  what would the other frame have given?         the same walk on the opposite frame, so the test
                                                 can say which way round is right per leg.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
import _nakedchain as NK

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); U = SC.U
DAYOF = lambda k: datetime.datetime.utcfromtimestamp(int(SC.ts[k]) / 1000).strftime('%Y-%m-%d')

rows_ = NK.run_chain_naked(T.gate_A, 'end', 'rev_inv')
legs = [r for r in rows_ if not r['brk']]
print('# arm 5 — %d legs' % len(legs))

def best_in(a, b, d):
    seg = PX[a:b + 1]
    ok = np.isfinite(seg) & (seg > 0)
    if not ok.any(): return None, None
    idx = np.flatnonzero(ok)
    vals = seg[idx]
    i = idx[int(np.argmin(vals))] if d > 0 else idx[int(np.argmax(vals))]
    return a + int(i), float(seg[int(i)])

print('\n# THE TEST, LEG BY LEG — arm 5, reversed lineage + ws2 override')
rows = []
nb = nw = nz = 0
for r in legs:
    k, lb, d, fr = r['walkfrom'], r['land'], r['d'], r['frame']
    p0 = float(PX[k]); pe = float(PX[lb])
    imp = (p0 - pe) / p0 * 100.0 * d
    ob, bp = best_in(k, lb, d) if lb > k else (k, p0)
    oth, othw, _ = NK.rev_walk(k, -fr)
    oimp = ((p0 - float(PX[oth])) / p0 * 100.0 * d) if oth else float('nan')
    if lb == k:
        v = 'no walk — zero bars'; nz += 1
    elif imp > 0:
        v = 'moved BETTER'; nb += 1
    else:
        v = 'moved WORSE — WRONG DIRECTION'; nw += 1
    rows.append((str(r['leg']), r['side'], '%s %s' % (DAYOF(k)[5:], U(k)), '%+d' % fr,
                 '%.6f' % p0, U(lb), '%.1f' % r['naked'], '%.6f' % pe, '%+.4f' % imp,
                 U(ob) if ob else '—', '%.6f' % bp if bp else '—',
                 'YES' if ob == k else 'no',
                 U(oth) if oth else 'never', '%+.4f' % oimp if oth else '—', v))
box(('leg', 'side', 'the walk starts', 'frame', 'open pxs', 'landing bar', 'naked min',
     'landing pxs', 'entry better by %', 'best pxs bar in the span', 'that best pxs',
     'open bar already best?', 'the OTHER frame lands', 'its entry better by %',
     'JOE\'S TEST'), rows)

print('\n# THE VERDICT')
box(('the outcome', 'legs', 'what it means'),
    [('no walk — zero bars', str(nz), 'the open signal was left alone. Cannot help or hurt.'),
     ('moved BETTER', str(nb), 'the walk found a better pxs. The direction was right.'),
     ('moved WORSE — WRONG DIRECTION', str(nw),
      'the walk landed on a pxs that is worse for the trade. FAILS Joe\'s test.')])
mv = [r for r in legs if r['land'] > r['walkfrom']]
print('- %d of the %d legs relocated at all; %d of those %d landed WORSE.'
      % (len(mv), len(legs), nw, len(mv)))
print('- summed entry improvement over the relocating legs: %+.4f'
      % sum((float(PX[r['walkfrom']]) - float(PX[r['land']])) / float(PX[r['walkfrom']])
            * 100.0 * r['d'] for r in mv))

print('\n# WOULD THE OPPOSITE FRAME HAVE FACED THE RIGHT WAY?')
rows = []
bb = bo = be = 0
for r in legs:
    k, lb, d, fr = r['walkfrom'], r['land'], r['d'], r['frame']
    if lb == k: continue
    p0 = float(PX[k])
    imp = (p0 - float(PX[lb])) / p0 * 100.0 * d
    oth, _, _ = NK.rev_walk(k, -fr)
    if oth is None: continue
    oimp = (p0 - float(PX[oth])) / p0 * 100.0 * d
    if oimp > imp: bo += 1
    elif oimp < imp: bb += 1
    else: be += 1
    rows.append((str(r['leg']), r['side'], U(k), '%+d' % fr, U(lb), '%+.4f' % imp,
                 '%+d' % -fr, U(oth), '%+.4f' % oimp, '%+.4f' % (oimp - imp),
                 'the OTHER frame' if oimp > imp else ('this frame' if oimp < imp else 'equal')))
box(('leg', 'side', 'the walk starts', 'frame used', 'its landing', 'its entry better by %',
     'the other frame', 'its landing', 'its entry better by %', 'the gap',
     'which faced the right way'), rows)
print('- the frame in use won %d, the opposite frame won %d, equal %d.' % (bb, bo, be))
