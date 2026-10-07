"""THE TWO SWAPS, A/B'd across the full chain. 09-25. 1007.

Joe 1007: *"there's 2 changes to test: 1) the test your about to build: swapping the x-cross with
stall, and 2) keeping the x-cross and swapping oob with stalled"*.

  BASELINE    pass `oob`, exit x-cross OR final stalled. As built, and as ruled.
  SWAP 1      pass `oob`, exit FINAL STALLED ONLY - the x-cross removed.
  SWAP 2      pass `stalled`, exit x-cross OR final stalled - the x-cross kept.

The baton's pass and the walk's exit are the only things that move. The >ws12 oob mech, the ceiling
rule, the mae 1.1 stop and the arm are identical in all three.

TWO FRAMINGS, because a swap changes every exit and therefore every downstream open:
  Joe's chain    two segments - legs from 02:48:50, then Joe's hand-picked 08:10:00 reopen held
                 FIXED at 7 legs in the first segment. Keeps his intervention in place.
  one chain      a single run from 02:48:50 to its first mae stop. No intervention, so it is the
                 pure mech comparison - but the as-built version stops early and the leg counts
                 differ, which is the point rather than a flaw.

SCORING: a leg that hit the stop scores MFE 0.0000 and MAE 1.1000, the knob value - Joe's rule.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box, MAE_STOP = C.SC, C.PX, C.box, C.MAE_STOP
D = C.D
VARIANTS = [('baseline  pass oob, exit x-cross+stall', 'oob', False),
            ('swap 1    pass oob, exit stall only', 'oob', True),
            ('swap 2    pass stalled, exit x-cross+stall', 'stalled', False)]

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]
    seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

def run(segs):
    """-> [row dicts]. `segs` is [(start, side, maxlegs)], maxlegs 0 = until the stop."""
    rows = []; n = 0; prev = None
    for si, (st, sd, ml) in enumerate(segs):
        k = SC.K('%s %s' % (D, st)); d = sd; seg_n = 0
        if prev is not None:
            rows.append(dict(brk=True, a=prev, b=k))
        while True:
            xk, why, mae, cb, hand, tr = C.run_leg(k, d)
            if xk is None: break
            n += 1; seg_n += 1
            p0 = float(PX[k]); sgn = 1 if d > 0 else -1
            rows.append(dict(brk=False, leg=n, side='LONG' if d > 0 else 'SHORT', open=k,
                             exit=xk, real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn,
                             why=why, hand=hand, d=d))
            prev = xk
            if why == 'mae breach': break
            if ml and seg_n >= ml: break
            k = xk; d = -d
    return rows

def tally(rows):
    rA = rF = rR = 0.0
    for r in rows:
        if r['brk']: continue
        a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
        rA += a_; rF += f_; rR += r['real']
    L = [r for r in rows if not r['brk']]
    return dict(legs=len(L), pos=sum(1 for r in L if r['real'] > 0), mae=rA, mfe=rF, real=rR,
                stops=sum(1 for r in L if r['why'] == 'mae breach'),
                last=L[-1]['exit'] if L else None,
                hand=sum(1 for r in L if r['hand']))

def leg_table(lbl, rows):
    print('\n## %s' % lbl)
    out = []; rA = rF = rR = 0.0
    for r in rows:
        if r['brk']:
            out.append(('—', 'BREAK', SC.U(r['a']), SC.U(r['b']),
                        '%.1f' % ((int(SC.ts[r['b']]) - int(SC.ts[r['a']])) / 60000.0),
                        'chain broken — reopen on Joe\'s mech', '—', '—', '—',
                        '%.4f' % rA, '%.4f' % rF, '%+.4f' % rR))
            continue
        a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
        rA += a_; rF += f_; rR += r['real']
        out.append((str(r['leg']), r['side'], SC.U(r['open']), SC.U(r['exit']),
                    '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0),
                    r['why'], '%.4f' % a_, '%.4f' % f_, '%+.4f' % r['real'],
                    '%.4f' % rA, '%.4f' % rF, '%+.4f' % rR))
    box(('leg', 'side', 'open', 'exit', 'hold min', 'why', 'leg MAE', 'leg MFE', 'realised',
         'running MAE', 'running MFE', 'running realised'), out)

# JOE'S REOPEN MECH. 1007: *"08:10 was created on a solid mech - I shared the spec at the time I
# placed it. in fact I was going to deploy it again at 11:21, after the mae1.1 @ 10:56"*. The spec
# he shared at 08:10: *"ws1r is low oob reversing and there is an upward Mage cascade"*. Both bars
# are his reads, both upward, so both reopen LONG.
#
# I CANNOT BUILD THE MECH: the cascade half has no ruled producer and task #22 is parked. These are
# its OUTPUTS, given by Joe, used as given. The driver reopens at the first named bar STRICTLY
# AFTER a stop, so a variant that runs past a bar never uses it.
SEED = ('02:48:50', +1, 7)          # 7 legs - Joe called 07:51 "stopped", his call, not a stop rule
REOPENS = ['08:10:00', '11:21:00']

def run_chain():
    rows = []; n = 0; prev = None
    st, sd, ml = SEED
    pending = list(REOPENS)
    while True:
        k = SC.K('%s %s' % (D, st)); d = sd; seg_n = 0
        if prev is not None:
            rows.append(dict(brk=True, a=prev, b=k))
        stopped = False
        while True:
            xk, why, mae, cb, hand, tr = C.run_leg(k, d)
            if xk is None: break
            n += 1; seg_n += 1
            p0 = float(PX[k]); sgn = 1 if d > 0 else -1
            rows.append(dict(brk=False, leg=n, side='LONG' if d > 0 else 'SHORT', open=k,
                             exit=xk, real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn,
                             why=why, hand=hand, d=d))
            prev = xk
            if why == 'mae breach':
                stopped = True; break
            if ml and seg_n >= ml: break
            k = xk; d = -d
        nxt = [t for t in pending if SC.K('%s %s' % (D, t)) > prev]
        if not nxt: break
        st, sd, ml = nxt[0], +1, 0
        pending = [t for t in pending if t != nxt[0]]
    return rows

RES = {}
for lbl, pass_, nox in VARIANTS:
    C.PASS, C.NOX = pass_, nox
    RES[lbl] = run_chain()

print('\n# THE TWO SWAPS, SIDE BY SIDE')
box(('variant', 'legs', 'positive', 'stops', 'handovers', 'last exit',
     'running MAE', 'running MFE', 'MFE/MAE', 'running realised'),
    [(lbl, str(t['legs']), str(t['pos']), str(t['stops']), str(t['hand']),
      SC.U(t['last']) if t['last'] else '—', '%.4f' % t['mae'], '%.4f' % t['mfe'],
      '%.2f' % (t['mfe'] / t['mae']) if t['mae'] else 'inf', '%+.4f' % t['real'])
     for lbl, rows in RES.items() for t in [tally(rows)]])

print('\n# EVERY LEG')
for lbl, pass_, nox in VARIANTS:
    leg_table(lbl, RES[lbl])

print('\n- the baton pass and the walk exit are the only differences. The >ws12 mech, the ceiling')
print('  rule, the arm and the mae %.2f stop are identical in all three.' % MAE_STOP)
