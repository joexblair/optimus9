"""THE WHOLE CHAIN WITH A NAKED LINEAGE WALK AT EVERY OPEN. 09-25 + 09-26. 1008.

Joe 1008: *"now we need to test the entire chain for 'lineage walking towards dr to optimise the
trade entry'"*, then his three rulings:
  1  *"every open"*
  2  *"native, ie we don't mangle the side"*
  3  *"the walk runs from the re-entry's conf bar - no lineage walk for an optimised opening"*

THE MECH, as those rulings fix it:
  at EVERY open bar the chain would have entered on, nothing is opened. The LINEAGE WALK runs from
  that bar carrying NO POSITION, on the frame `dr` gives at that bar. When the walk terminates, the
  trade is entered THERE, on the chain's OWN NATIVE SIDE - the walk never changes the side.

  the walk's frame     int(DRv[k]) - the tape dr at the open bar. Joe's "towards dr".
  the trade's side     untouched: the alternation for an alternation open, +1 for a re-entry open.
  the re-entry router  untouched. The ws1x hold / reent_xwob 6 conf bar is found exactly
                       as the baseline finds it, and the walk starts FROM that conf bar.
  while naked          NO MAE, NO 1.10 stop. Nothing is open, so nothing can be stopped.
  the entered leg      the unchanged composed mech, C.run_leg(landing, native side) - lineage walk
                       + the >ws12 oob mech + the 1.10 stop.

THE NAKED WALK IS THE LINEAGE WALK ONLY - arm, KICKSTART, baton, then `final stalled` or `x-cross`,
with the ws12r ceiling rule live. It does NOT carry the >ws12 handover: that mech exists to exit an
open position and there is no position while the walk walks. MY STRUCTURAL CALL, stated so it can
be flipped; it is the walk that produced 15:55:05 in SS14b.

THE ONE GAP THE RULINGS DO NOT CLOSE is what happens when the walk never terminates. Both answers
are run as separate arms rather than decided:
  ARM 1  'end'   - no landing, the chain ends there.
  ARM 2  'open'  - no landing, the trade is entered at the open bar, i.e. the baseline for that leg.

Arm 0 is the committed baseline: T.run_chain(T.gate_A), 43 legs, +13.3928.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.lr_v2 import _mage_rev
import _chain10 as C
import _chain_2day as T

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); U = SC.U
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
M2, ST = C.M2, C.ST
MAE_STOP = C.MAE_STOP
DAYOF = lambda k: datetime.datetime.utcfromtimestamp(int(SC.ts[k]) / 1000).strftime('%Y-%m-%d')
print('# tape %d bars, last %s %s' % (N, DAYOF(N - 1), U(N - 1)), flush=True)


def naked_walk(k0, d):
    """THE LINEAGE WALK ONLY, carrying no position. Returns (landing_bar, why, trace).

    No MAE stop and no >ws12 handover - nothing is open. The ws12r ceiling rule is live because Joe
    ruled it part of the walk, per leg.
    """
    armed = False; rider = None; ceil = C.BASE_HI; tr = []
    for j in range(k0 + 1, N):
        if ceil == C.BASE_HI and C.oobf(C.TRIG_TF, j, d) and not C.oobf(C.TRIG_TF, j - 1, d):
            ceil = C.CEIL_HI
            tr.append((j, 'CEILING ws%d -> ws%d' % (C.BASE_HI, C.CEIL_HI)))
        if not armed:
            if (d > 0 and float(M2[j]) >= SC.HI and float(M2[j - 1]) < SC.HI) or \
               (d < 0 and float(M2[j]) <= SC.LO and float(M2[j - 1]) > SC.LO):
                armed = True
                tr.append((j, 'armed — ws2Mage %s %.0f (%.2f)'
                           % ('over' if d > 0 else 'under', SC.HI if d > 0 else SC.LO,
                              float(M2[j]))))
            else:
                continue
        if rider is None:
            c = [t for t in C.ALL_TF if t <= ceil and C.oobf(t, j, d)]
            if c:
                rider = max(c)
                tr.append((j, 'KICKSTART — rider ws%d (r %.2f)' % (rider, float(C.R[rider][j]))))
            continue
        cand = [t for t in range(rider + 1, min(rider + C.LIN_HOP, ceil) + 1)
                if C.oobf(t, j, d)]
        if cand:
            rider = max(cand)
            tr.append((j, 'baton -> ws%d oob (r %.2f)' % (rider, float(C.R[rider][j]))))
            continue
        if ST[(rider, d)][j]:
            return j, 'final stalled on ws%d' % rider, tr
        if C.xcond(rider, j, d):
            return j, 'x-cross on ws%d' % rider, tr
    return None, 'the walk never terminated', tr


try:
    TURN_WOB = int(C.W['ent_rev_wob'])
except Exception:
    TURN_WOB = 5
REV1T = _mage_rev(C.R[1], TURN_WOB)
WANT_TURN = lambda d: (-1 if d > 0 else +1)
_EXF_LO = float(SC.LG['momo_fence_r']); _EXF_HI = 100.0 - _EXF_LO


def _fen1(v, d):
    if d > 0:
        return 'hi oob' if v >= SC.HI else ('hi ex-f' if v >= _EXF_HI else 'in-fence')
    return 'lo oob' if v <= SC.LO else ('lo ex-f' if v <= _EXF_LO else 'in-fence')


def _traj1(k):
    """ws1r's TRAJECTORY: the sign of (ws1r now - ws1r at its last step change at or before k).

    The higher-TF r lines are step functions, so the last step is well defined and this needs no
    lookback window. Same reading as _joereads.py's step_dir.
    """
    v = C.R[1]
    cur = float(v[k]); j = k
    while j > 0 and (not np.isfinite(v[j - 1]) or float(v[j - 1]) == cur):
        j -= 1
    if j <= 0:
        return 0
    prev = float(v[j - 1])
    return 1 if cur > prev else (-1 if cur < prev else 0)


def _noop_confluence(k, d):
    """JOE'S CONFLUENCE — when the walk is an immediate no-op. 1008.

    Joe 1008, on arm-8 leg 1 (02:48:50, LONG, frame -1, ws1r 54.33 in-fence and rising):
    *"we could confluence that further by looking at ws1r's trajectory + infence. in this case it's
    upward so the walk is immediately a no-op"*.

    THE WALK'S TRAVEL IS THE FRAME'S SIGN: on frame -1 the travel is DOWN toward the low fence and
    the terminal turn is UP; on frame +1 the travel is UP and the terminal turn is DOWN.

      no-op when   ws1r's trajectory is AGAINST the travel  AND  ws1r is IN-FENCE on the frame.

    Both halves are needed. Against-the-travel alone is just a wiggle; in-fence is what says there is
    no extension in progress to ride. Zero knobs - the fences are oob 15/85 and the ex-fence
    momo_fence_r 17/83, both already settled.

    IT DOES NOT COVER LEG 2's SHAPE (04:41:00, ws1r pinned at 100.00 hi oob). That leg is at the
    extreme, not in-fence, so this test does not fire on it.
    """
    v = float(C.R[1][k])
    infence = not (v >= SC.HI or v >= _EXF_HI) if d > 0 else not (v <= SC.LO or v <= _EXF_LO)
    return _traj1(k) != d and infence


def turn_walk(k0, d, confluence=False):
    """THE TURN WALK — the entry-optimising walk, landing on ws1r's TURN. 1008.

    Joe 1008: *"10:17 walked down to the reversl of ws1r at 10:21. at 10:21 it was infence - that's
    the end of the walk"* / *"a r line that doesn't reach the bottom is weak, and weak lets pxs
    climb"* / and his ruling on the detector: *"rrev_wob 5"*.

      THE ws2 OVERRIDE  stands. No ws2Mage gate.
      THE LINE          ws1r, which §18 proved is where the downward lineage always terminates.
      THE LANDING       the first ws1r TURN AGAINST the walk's travel, by
                        `_mage_rev(ws1r, ent_rev_wob 5)`. On frame -1 the downward travel ends on a
                        turn UP; on frame +1 the upward travel ends on a turn DOWN. `WANT_TURN(d)`
                        is _chain10's own convention, reused not reinvented.
      WHY THE TURN      not the oob arrival. At 10:17 ws1r bottomed at 19.95, 4.95 above the 15
                        fence, and turned without ever reaching oob - the §18 rule then waited
                        19.0 min for an unrelated oob visit and gave up 0.5702% of entry. A line
                        that turns while in-fence has no extension left, and that weakness is what
                        lets pxs climb back.

    `ent_rev_wob` 5 is a SECOND knob for a SECOND mech. `rrev_wob` 2 is untouched and still serves
    the >ws12 divergence.
    """
    if confluence and _noop_confluence(k0, d):
        v = float(C.R[1][k0])
        return k0, ('NO-OP — ws1r %.2f is %s on frame %+d and its trajectory is %+d, against the '
                    'travel' % (v, _fen1(v, d), d, _traj1(k0))), []
    want = WANT_TURN(d)
    for j in range(k0, N):
        if int(REV1T[j]) == want:
            v = float(C.R[1][j])
            return j, ('ws1r turns %s (rrev_wob %d) at r %.2f, %s'
                       % ('UP' if want > 0 else 'DOWN', TURN_WOB, v, _fen1(v, d))), \
                   [(j, 'ws1r turn %s, r %.2f %s' % ('UP' if want > 0 else 'DOWN', v, _fen1(v, d)))]
    return None, 'ws1r never turned before the tape end', []


def rev_walk(k0, d):
    """THE REVERSED LINEAGE WALK — Joe's entry-optimising walk. 1008.

    Joe 1008: *"we'll create a ws2 override, because `walking to a better opening` uses lineage walk
    in a different way, for a different purpose / -walking to a better entry does not need ws2: ws2
    was introduced to get the trade started, to collect the big MFE / -optimising an entry carries
    no aspirations for a big trade - it just needs to move an open signal that is misplaced on the
    board / -waiting for ws2Mage will almost always ride over the optimal position, for 2 reasons:
    --1, the signal relocations are small --2, the very purpose of `walking the lineage walk to a
    more optimised location` requires the lineage to operate in reverse"*.

      THE ws2 OVERRIDE   `exit-armed` is GONE. No ws2Mage gate at all.
      THE RIDER          the TOP OF THE UNBROKEN oob RUN FROM ws1 on the walk's frame. Not
                         max(oob): at 04:41 max(oob) is ws10 while Joe read ws1.
      THE BATON          DOWNWARD - an oob TF within lin_hop BELOW the rider, taken as far as it
                         goes on the same bar. ws1 is the floor; no line exists below it.
      THE LANDING        the bar the downward lineage runs out on. Joe's *"zero bars"*.

    THE THREE READS THIS REPRODUCES, which is why this is the reading taken:
      04:41:00 frame +1   ws1r 100.00 oob, ws2r 70.97 in-fence -> run is [ws1] -> rider ws1 ->
                          nothing below -> ZERO BARS. Joe: *"the lineage stops at ws1 ... it walks
                          zero bars"*.
      17:31:55 frame -1   ws1r 12.80 and ws2r 3.19 oob, ws3r 39.57 in-fence -> run is [ws1, ws2] ->
                          rider ws2 -> baton down to ws1 -> ZERO BARS. Joe: *"my view is zero bars,
                          because there is no DOWNWARD lineage after ws2r"*.
      15:41:00 frame -1   ws1r 26.71 in-fence -> the run is EMPTY -> no rider -> the walk WAITS.
                          This is the only shape that relocates at all.

    NOTE THE REDUCTION, stated because it is a consequence and not a choice: because the run is
    contiguous FROM ws1, ws1 is always in it, so the downward baton always reaches ws1 and the
    lineage always runs out there. The mech therefore lands on THE FIRST BAR WHERE ws1r IS oob ON
    THE WALK'S FRAME. `final stalled` and `x-cross` are never reached, because exhaustion fires on
    the KICKSTART bar itself.
    """
    for j in range(k0, N):
        run = []
        for t in C.ALL_TF:
            if t > C.BASE_HI: break
            if C.oobf(t, j, d): run.append(t)
            else: break
        if not run:
            continue
        rider = run[-1]
        tr = [(j, 'KICKSTART — rider ws%d, the top of the oob run ws1-ws%d (r %.2f)'
               % (rider, rider, float(C.R[rider][j])))]
        while True:
            cand = [t for t in range(max(1, rider - C.LIN_HOP), rider) if C.oobf(t, j, d)]
            if not cand: break
            rider = min(cand)
            tr.append((j, 'baton DOWN -> ws%d oob (r %.2f)' % (rider, float(C.R[rider][j]))))
        return j, 'lineage exhausted below ws%d' % rider, tr
    return None, 'the walk never terminated', tr


def run_chain_naked(gate, noland, frame='dr', seed=None, last_open=None, confluence=False):
    """THE WALK'S FRAME.

      'dr'   int(DRv[k]), the tape dr at the open bar, the native side when dr is 0. Arms 1 and 2.
      'inv'  -d, THE INVERSE OF THE TRADE SIDE. Joe 1008: *"the direction of the x cross is defined
             by the trade - it's a SHORT trade, so the cross is downward"*. A downward cross is
             `d > 0` in the code, so a SHORT trade (side -1) walks on frame +1. Arms 3 and 4.
    """
    rows = []; n = 0
    LAST = T.LAST_OPEN if last_open is None else last_open
    k, d, seg_n = (T.K(T.START_D, '02:48:50') if seed is None else seed), +1, 0
    while True:
        fr = (int(DRv[k]) or d) if frame in ('dr', 'rev_dr', 'turn_dr') else -d
        lb, lw, ltr = (turn_walk(k, fr, confluence) if frame.startswith('turn')
                       else rev_walk(k, fr) if frame.startswith('rev')
                       else naked_walk(k, fr))
        if lb is None or lb > LAST:
            if noland == 'end':
                rows.append(dict(brk=True, noland=k, nw=lw)); break
            lb, lw = k, 'no landing — entered at the open bar'
        p_open = float(PX[k]); p_ent = float(PX[lb]); sgn = 1 if d > 0 else -1
        xk, why, mae, cb, hand, tr = C.run_leg(lb, d)
        if xk is None: break
        n += 1; seg_n += 1
        rows.append(dict(brk=False, leg=n, side='LONG' if d > 0 else 'SHORT', d=d,
                         walkfrom=k, frame=fr, land=lb, lw=lw, dr0=(int(DRv[k]) == 0),
                         naked=(int(SC.ts[lb]) - int(SC.ts[k])) / 60000.0,
                         imp=(p_open - p_ent) / p_open * 100.0 * sgn,
                         open=lb, exit=xk, real=(float(PX[xk]) - p_ent) / p_ent * 100.0 * sgn,
                         why=why, hand=hand, mae_meas=mae,
                         tr=(tr if why == 'mae breach' else None)))
        if why == 'mae breach' or (seg_n == 7 and n == 7):
            rb, cf, sd = T.find_reentry(xk, gate, LAST)
            if cf is None:
                rows.append(dict(brk=True, a=xk, b=None)); break
            rows.append(dict(brk=True, a=xk, b=cf, rb=rb, sd=sd))
            k, d, seg_n = cf, sd, 0
            continue
        if xk >= LAST: break
        k = xk; d = -d
    return rows


def main():
    print('# arm 0 — the committed baseline, no naked walk ...', flush=True)
    A0 = T.run_chain(T.gate_A)
    print('# arm 1 — naked walk, no landing ends the chain ...', flush=True)
    A1 = run_chain_naked(T.gate_A, 'end')
    print('# arm 2 — naked walk, no landing enters at the open ...', flush=True)
    A2 = run_chain_naked(T.gate_A, 'open')
    print('# arm 3 — frame = INVERSE OF THE TRADE SIDE, no landing ends it ...', flush=True)
    A3 = run_chain_naked(T.gate_A, 'end', 'inv')
    print('# arm 4 — frame = INVERSE OF THE TRADE SIDE, no landing enters at the open ...',
          flush=True)
    A4 = run_chain_naked(T.gate_A, 'open', 'inv')
    print('# arm 5 — REVERSED lineage, ws2 override, frame = inverse of the side ...', flush=True)
    A5 = run_chain_naked(T.gate_A, 'end', 'rev_inv')
    print('# arm 6 — REVERSED lineage, ws2 override, frame = dr ...', flush=True)
    A6 = run_chain_naked(T.gate_A, 'end', 'rev_dr')
    print('# arm 7 — the TURN walk, ent_rev_wob %d, frame = inverse of the side ...' % TURN_WOB,
          flush=True)
    A7 = run_chain_naked(T.gate_A, 'end', 'turn_inv')
    print('# arm 8 — the TURN walk, ent_rev_wob %d, frame = dr ...' % TURN_WOB, flush=True)
    A8 = run_chain_naked(T.gate_A, 'end', 'turn_dr')
    ARMS = [('arm 0 — baseline, no walk', A0),
            ('arm 1 — frame dr, no landing ends it', A1),
            ('arm 2 — frame dr, no landing enters at the open', A2),
            ('arm 3 — frame = inverse of the side, no landing ends it', A3),
            ('arm 4 — frame = inverse of the side, no landing enters at the open', A4),
            ('arm 5 — REVERSED lineage + ws2 override, frame = inverse of the side', A5),
            ('arm 6 — REVERSED lineage + ws2 override, frame = dr', A6),
            ('arm 7 — the TURN walk, ent_rev_wob %d, frame = inverse of the side' % TURN_WOB, A7),
            ('arm 8 — the TURN walk, ent_rev_wob %d, frame = dr' % TURN_WOB, A8)]

    print('\n# THE THREE ARMS, 09-25 02:48:50 TO THE END OF 09-26')
    rows = []
    for lbl, rr in ARMS:
        t = T.tally(rr)
        nk = sum(r.get('naked', 0.0) for r in rr if not r['brk'])
        im = sum(r.get('imp', 0.0) for r in rr if not r['brk'])
        rows.append((lbl, str(t['legs']), str(t['pos']), str(t['stops']), str(t['reent']),
                     '%s %s' % (DAYOF(t['last'])[5:], U(t['last'])) if t['last'] else '—',
                     '%.4f' % t['mae'], '%.4f' % t['mfe'],
                     '%.2f' % (t['mfe'] / t['mae']) if t['mae'] else 'inf',
                     '%+.4f' % t['real'], '%+.4f' % t['conv'], '%.1f' % nk, '%+.4f' % im))
    box(('arm', 'legs', 'positive', 'stops', 're-entries', 'last exit', 'running MAE', 'running MFE',
         'MFE/MAE', 'realised as scored', 'realised at -1.10', 'minutes naked', 'entry improvement'),
        rows)
    print('- "minutes naked" is time with NOTHING OPEN while a walk walks. It is its own column and')
    print('  its own total; it is not folded into any other number.')
    print('- "entry improvement" sums (open bar price -> landing bar price) in the native side\'s')
    print('  favour. It is an entry, not P&L, and it is already inside realised.')
    print('- a stopped leg scores MAE %.4f and MFE 0.0000, Joe 1007.' % MAE_STOP)

    print('\n# PER DAY, BY THE LEG\'S ENTRY BAR')
    rows = []
    for lbl, rr in ARMS:
        pd = collections.OrderedDict()
        for r in rr:
            if r['brk']: continue
            e = pd.setdefault(DAYOF(r['open']), dict(n=0, pos=0, st=0, mae=0.0, mfe=0.0, real=0.0,
                                                     nk=0.0))
            a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else T.mm(r['open'], r['exit'], r['d'])
            e['n'] += 1; e['pos'] += 1 if r['real'] > 0 else 0
            e['st'] += 1 if r['why'] == 'mae breach' else 0
            e['mae'] += a_; e['mfe'] += f_; e['real'] += r['real']; e['nk'] += r.get('naked', 0.0)
        for dd, e in pd.items():
            rows.append((lbl, dd, str(e['n']), str(e['pos']), str(e['st']), '%.4f' % e['mae'],
                         '%.4f' % e['mfe'], '%.2f' % (e['mfe'] / e['mae']) if e['mae'] else 'inf',
                         '%+.4f' % e['real'], '%.1f' % e['nk']))
    box(('arm', 'day', 'legs', 'positive', 'stops', 'MAE', 'MFE', 'MFE/MAE', 'realised',
         'minutes naked'), rows)

    for lbl, rr in ARMS[1:]:
        print('\n\n# %s — EVERY LEG, ONE PER ROW' % lbl.upper())
        rows = []; rr_ = 0.0
        for r in rr:
            if r['brk']:
                if r.get('noland') is not None:
                    rows.append(('—', 'NO LANDING', '%s %s' % (DAYOF(r['noland'])[5:], U(r['noland'])),
                                 '—', '—', '—', '—', '—', '—', '—', '—', '—', r['nw'], '—'))
                else:
                    rows.append(('—', 'STOP — re-entry router', '%s %s' % (DAYOF(r['a'])[5:], U(r['a'])),
                                 '—', ('%s %s' % (DAYOF(r['b'])[5:], U(r['b']))) if r.get('b')
                                 else 'NONE', '—', '—', '—', '—', '—', '—', '—',
                                 'the walk restarts from the conf bar' if r.get('b') else
                                 'no re-entry found', '—'))
                continue
            a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else T.mm(r['open'], r['exit'], r['d'])
            rr_ += r['real']
            rows.append((str(r['leg']), r['side'], '%s %s' % (DAYOF(r['walkfrom'])[5:], U(r['walkfrom'])),
                         '%+d' % r['frame'], U(r['land']), '%.1f' % r['naked'], '%+.4f' % r['imp'],
                         U(r['exit']), '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0),
                         r['why'], '%.4f' % a_, '%.4f' % f_, r['lw'], '%+.4f' % rr_))
        box(('leg', 'side', 'the walk starts', 'frame dr', 'entry bar', 'naked min',
             'entry better by %', 'exit', 'hold min', 'why', 'leg MAE', 'leg MFE',
             'what landed the walk', 'running realised'), rows)

    print('\n# EVERY STOP, ALL THREE ARMS')
    rows = []
    for lbl, rr in ARMS:
        for r in rr:
            if r['brk'] or r['why'] != 'mae breach': continue
            rows.append((lbl, DAYOF(r['open'])[5:], r['side'],
                         U(r.get('walkfrom', r['open'])), U(r['open']), U(r['exit']),
                         '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0),
                         '%+.4f' % r['real'], '%.4f' % (abs(r['real']) - MAE_STOP)))
    box(('arm', 'day', 'side', 'the walk started', 'entry bar', 'exit', 'hold min', 'realised',
         'overshoot past %.2f' % MAE_STOP), rows)

    print('\n# WHERE dr WAS 0 AT AN OPEN BAR, AND WHERE THE WALK NEVER TERMINATED')
    rows = []
    for lbl, rr in ARMS[1:]:
        z = [r for r in rr if not r['brk'] and r.get('dr0')]
        nl = [r for r in rr if r['brk'] and r.get('noland') is not None]
        nlo = [r for r in rr if not r['brk'] and 'no landing' in r.get('lw', '')]
        rows.append((lbl, str(len(z)), ', '.join(U(r['walkfrom']) for r in z) or 'none',
                     str(len(nl) + len(nlo)),
                     ', '.join(U(r.get('noland', r.get('walkfrom'))) for r in nl + nlo) or 'none'))
    box(('arm', 'opens with dr 0', 'which', 'opens the walk never landed', 'which'), rows)



if __name__ == '__main__':
    main()
