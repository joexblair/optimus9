"""THE ONE REPORT. One build, every table. 1013.

Joe 1013: *"the time to produce outputs like this has increased exponentially. can you optimise the
flow?"* - I was running two or three separate scripts per report and paying `machine.build()` in
each one. This is one process: build once, walk the chain once, emit every table from that one pass.

    python3 1013_report.py                      the chain, the loop counts, the per-leg walks
    W_EVENTS='2026-07-19 11:00:00' python3 1013_report.py    also every event at or after that bar

NOTHING IS BUILT HERE. Every bar comes from `machine.chain`, `_ibmech` and `_htfgate`.
"""
import os
import re
import sys

os.environ.setdefault('W_TRACE_LIN', '1')
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import machine as M
import _chain10 as C
import _htfgate as HG

SC, U, N = M.SC, M.U, M.N
# THE WALK'S END. Joe 1013: *"continue walking to the first END in 07-20"*. The walk keeps opening
# legs while the last one ended before this bar, and stops after the first leg that ends on or
# after it. No cap on how many legs that takes.
UNTIL = SC.K(os.environ.get('W_UNTIL', '2026-07-20 00:00:00'))
EVENTS = os.environ.get('W_EVENTS', '')

ib, em, rows, gate, restart = M.build()

print()
print('| knob | live value |')
print('|---|---|')
print('| TAPE | %d bars |' % N)
print('| LOOP_TF / LOOP_END | ws%s / %s |' % (C.LOOP_TF, C.LOOP_END))
print('| the jumpstart cap, last-mile mode | ws%d |' % C.LASTMILE_KICK_TFCAP)
print('| W_PASS | %s |' % C.PASS)
print('| the chain restart | armed on ws%sr into oob, ws1Mage in-fence > %d bars, ws%s away |'
      % (C.LOOP_TF, __import__('_restart').MAGE_DWELL,
         ', ws'.join(str(t) for t in __import__('_restart').AWAY_TFS)))
print('| the HTF gate | ws%d / release %d bars / re-enable %d bars |'
      % (gate.x_tf, gate.wob, gate.ren_wob))
print('| the walk runs until | the first leg that ends on or after %s |' % U(UNTIL))

# ---- the chain: the declared legs, then the HTF-gated walk
L = []
for lbl, ets, cts, dr in M.TRADES:
    e = SC.K(ets)
    L.append((lbl, e, dr, M.chain(e, dr, ib, em, rows, gate=gate), 'declared', None))
k = L[-1][3]['end']
while k < N - 1 and k < UNTIL:
    side, tf, endl, val = gate.oob_side(k)
    he = 0 if endl is None else (+1 if endl == 'HIGH' else -1)
    # OPENING 1: the next permitted ws1cp-ib, either side.
    best = None
    for cps in (+1, -1):
        frm = k
        while True:
            cp, dec, via = ib.next_cp_ib(frm, cps)
            if dec is None:
                break
            if gate.permits_live(cps, side, dec, k, he):
                if best is None or dec < best[1]:
                    best = (cp, dec, via, cps)
                break
            frm = dec
    # OPENING 2: Joe 1013's chain restart. FIRST TO FIRE WINS - he set no precedence and the
    # earlier bar is the only reading that does not invent one. STATED.
    rk, rdr, rarm, rboard = (restart.next(k) if __import__('_restart').ON
                             else (None, None, None, None))
    use_restart = rk is not None and (best is None or rk < best[1])
    if use_restart:
        dec, dr, src = rk, rdr, 'restart'
        note = ('armed %s on ws%dr into %s oob; opens %s'
                % (U(rarm), C.LOOP_TF, 'LOW' if rboard < 0 else 'HIGH',
                   'LONG' if rdr < 0 else 'SHORT'))
        # THE GATE STILL DECIDES WHAT MAY OPEN. A HIGH-oob HTF line permits a LONG, a LOW-oob one a
        # SHORT - his 1013 rule. The restart is an opening, so it is tested like any other.
        want_cp = -dr
        if not gate.permits_live(want_cp, side, dec, k, he):
            note += ' | BLOCKED by the HTF gate'
            use_restart = False
    if not use_restart:
        if best is None:
            break
        cp, dec, via, cps = best
        dr = HG.trade_side(cps)
        src, note = 'ws1cp-ib', 'cp %s via %s on the %s side' % (U(cp), via,
                                                                'HIGH' if cps > 0 else 'LOW')
    if dec >= N - 1:
        break
    r = M.chain(dec, dr, ib, em, rows, gate=gate)
    if r['close'] is None:
        break
    L.append((U(dec), dec, dr, r, src, note))
    k = r['end']

print()
def why_gap(prev_end, prev_dr, open_bar):
    """Why is the last leg's end not this leg's open? -> AT MOST THREE WORDS.

    Joe 1013: *"a new column that uses max 3 words to describe why a leg's end is not the same
    timestamp as the next leg's OPEN"*.
    """
    if prev_end is None:
        return 'first leg'
    if open_bar == prev_end:
        return 'no gap'
    if open_bar < prev_end:
        return 'opens before end'
    flip = -prev_dr                                   # the side the chain would take at that bar
    side, tf, endl, val = gate.oob_side(prev_end)
    he = 0 if endl is None else (+1 if endl == 'HIGH' else -1)
    want_cp = HG.cp_side_for(flip)                    # ONE place for this sign, asserted there
    if side is not None and not gate.permits_live(want_cp, side, prev_end, prev_end, he):
        return 'hack blocked %s' % ('SHORT' if flip > 0 else 'LONG')
    return 'walk skipped bar'


print('| # | opens | side | how it opened | close event | the chain ends | why it ends | '
      'gap between legs reason | gross |')
print('|---|---|---|---|---|---|---|---|---|')
tot = 0.0
_pe, _pd = None, None
for i, (lbl, e, dr, r, src, note) in enumerate(L, 1):
    tot += r['gross_end']
    print('| %d | %s | %s | %s | %s | %s | %s | %s | %+.4f%% |'
          % (i, U(e), 'SHORT' if dr > 0 else 'LONG', src, U(r['close']),
             U(r['end']), str(r['why_end']).replace('|', '·')[:60],
             why_gap(_pe, _pd, e), r['gross_end']))
    _pe, _pd = r['end'], dr
print('| **TOTAL** | — | — | — | — | %s | — | — | **%+.4f%%** |' % (U(L[-1][3]['end']), tot))

# ---- the frozen reference
bad = []
for lbl, ets, cts, dr in M.TRADES:
    r = [x for x in L if x[0] == lbl][0][3]
    f = M.FROZEN.get(lbl)
    if f and abs(r['gross_end'] - f[1]) > M.TOL:
        bad.append('%s end %+.4f%% vs frozen %+.4f%%' % (lbl, r['gross_end'], f[1]))
print()
print('| check | result |')
print('|---|---|')
print('| the 6 declared legs vs the frozen reference | %s |'
      % ('all match' if not bad else ' / '.join(bad)))

# ---- the event counts, from the accumulated traces
print()
print('| per leg | how it opened | W_LOOP | JUMPSTART | EXHAUSTION after a loop | events | note |')
print('|---|---|---|---|---|---|---|')
for lbl, e, dr, r, src, note in L:
    ev = r.get('tr_all') or [(b, t) for b, t in r['tr']]
    print('| %s | %s | %d | %d | %d | %d | %s |'
          % (U(e), src,
             sum(1 for b, t in ev if 'W_LOOP' in str(t)),
             sum(1 for b, t in ev if 'JUMPSTART —' in str(t)),
             sum(1 for b, t in ev if 'LOOP CLOSE —' in str(t)), len(ev),
             (note or '')[:90]))

if EVENTS:
    A = SC.K(EVENTS)
    print()
    print('# EVERY EVENT AT OR AFTER %s' % EVENTS)
    print('| leg opens | bar | event |')
    print('|---|---|---|')
    for lbl, e, dr, r, src, note in L:
        for b, t in (r.get('tr_all') or r['tr']):
            if b >= A:
                print('| %s | %s | %s |' % (U(e), U(b), str(t).replace('|', '·')))
