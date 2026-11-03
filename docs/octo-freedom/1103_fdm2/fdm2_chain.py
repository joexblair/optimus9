"""fdm2's driver - his 1103 pen-test: walk the first leg from the 08-03 re-entry.

HIS ASK, standing from 1102: *"we'll walk from the 08-03 reentry / pre-chain check: walk the first
leg manually to pen-test the mech"*. The default here is ONE leg because that is what he asked
for, not because a leg count is a cap of mine. W_FDM2_LEGS=all walks to the tape end.

THE MECH IS v4_fdm2. Nothing is computed in this file - it loads, walks, and prints.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_fdm_reentry as RE
    import v4_signal as SG
    import ln
finally:
    sys.stderr = _e

RE_AT = os.environ.get('W_FDM2_OPEN', '2026-08-03 00:41:30')
ALL = os.environ.get('W_FDM2_LEGS', '1') == 'all'

LN = F2.load()
B = len(LN['close']) - 1
print('# fdm2 | TAPE %d bars, ends %s | RULED_OK %s | the walk runs to %s'
      % (len(LN['close']), ln.U(B), K.RULED_OK, ln.U(B)))
print('# THE STOP IS ON: FDM_MAE_CAP %.2f%% adverse from the open, his "yes, move it to default"'
      % float(K.FDM_MAE_CAP))
print()
print('| the knob | value | what it is |')
print('|---|---|---|')
for nm, what in (('FDM_FNC_2080', 'his "fdm-20-80-fnc" - step 1 AND the population. "ex" includes oob'),
                 ('FDM_STEP1_ABOVE_TF', 'step 1 scans STRICTLY above this TF, so ws4..ws30 = 27 lines'),
                 ('FDM_POP_LO', 'the reversal population floor, so ws3..ws30 = 28 before the filter'),
                 ('FDM_M3_FNC', 'ws3Mage\'s fence in the preamble, 25 -> 25/75'),
                 ('FDM_X10_WOB', 'the ws10x race hold, bars. His 1103 "use 24"'),
                 ('FDM_X10_GRACE_PCT', 'his "fdm-ws10x-cad-grace" - the grace walk\'s floor, %'),
                 ('FDM_X10_TRADE_PCT', 'the grace walk\'s rev-trade threshold, %'),
                 ('FDM_X10_GRACE_MIN', 'the grace walk\'s length, minutes'),
                 ('FDM_MAE_CAP', 'the stop, % adverse from the open'),
                 ('FDM_X10_FRM', 'must the race CROSS follow the cadence event, or only its CONFIRM'),
                 ('LIFT_WOB', 'the lift-off hold; the reversal STAMP is lift + 7 bars = 35 s')):
    v = getattr(K, nm)
    print('| %s | %s | %s |' % (nm, ('%g' % v) if not isinstance(v, str) else v, what))
print()

#   ── the open: his banked re-entry ─────────────────────────────────────────────────────────────
SIGS = RE.signals(LN['G30B'], LN['EMR'])
k0 = ln.K(RE_AT)
HIT = [g for g in SIGS if int(g['bar']) == k0]
assert len(HIT) == 1, ('the %s re-entry signal is not in the list - %d matches'
                       % (RE_AT, len(HIT)))
g = HIT[0]
D = SG.direction(int(g['side']))
OPN = SG.fire_bar(g)
TS = SG.target_side(D)
print('| the open | value |')
print('|---|---|')
print('| the re-entry signal bar | %s |' % ln.U(int(g['bar'])))
print('| the gcws30b window side | %s oob |' % ('HIGH' if int(g['side']) > 0 else 'LOW'))
print('| the trade | %s |' % D)
print('| its target side | %s |' % ('HIGH' if TS > 0 else 'LOW'))
print('| the open price bar | %s - the router\'s "just OPEN", 1 bar |' % ln.U(OPN))
print('| why | %s |' % g['why'])
print()

LG = F2.legs(LN, (OPN, TS, 'fdm re-entry %s' % ln.U(int(g['bar']))), B, resig=SIGS)
if not ALL:
    LG = LG[:1]

#   ── the decision rows, chronological ──────────────────────────────────────────────────────────
for i, L in enumerate(LG):
    print('## leg %s | %s | target side %s | %s'
          % (ln.U(L['opn']), 'LONG' if L['side'] > 0 else 'SHORT',
             'HIGH' if L['side'] > 0 else 'LOW', L['src']))
    print()
    print('| the bar | the stage | why |')
    print('|---|---|---|')
    for r in L['rows']:
        print('| %s | %s | %s |' % (ln.U(int(r['bar'])), r['stage'], r['why']))
    if not L['rows']:
        print('| %s | NO CADENCE EVENT | no cadence event on the %s side from the open to %s |'
              % (ln.U(L['opn']), 'HIGH' if L['side'] > 0 else 'LOW', ln.U(B)))
    print()

#   ── the legs ──────────────────────────────────────────────────────────────────────────────────
print('## the legs | every number carries the FDM_MAE_CAP %.2f%% stop' % float(K.FDM_MAE_CAP))
print()
print('| the open | the trade | the rev-trade signal | the exit | the exit kind | held min |'
      ' MAE% | MFE% | realised% |')
print('|---|---|---|---|---|---|---|---|---|')
for L in LG:
    print('| %s | %s | %s | %s | %s | %.1f | %.3f | %.3f | %+.3f |'
          % (ln.U(L['opn']), 'LONG' if L['side'] > 0 else 'SHORT',
             '-' if L['sig'] is None else ln.U(int(L['sig'])), ln.U(L['exit']), L['ctype'],
             L['held_min'], L['mae'], L['mfe'], L['rel']))
print()
S = F2.score(LG)
print('| the aggregate | value |')
print('|---|---|')
print('| legs | %d |' % S['n'])
print('| stopped | %d |' % S['stops'])
print('| gross %% | %+.3f |' % S['gross'])
print('| drag %% | -%.3f (%.4f%% round trip x %d legs) |' % (S['drag'], F2.DRAG_PCT, S['n']))
print('| net %% | %+.3f |' % S['net'])
print('| MAE %% total | %.3f |' % S['mae'])
print('| MFE %% total | %.3f |' % S['mfe'])
print('| MFE captured | %.1f%% of MFE |'
      % ((S['gross'] / S['mfe'] * 100.0) if S['mfe'] else float('nan')))
print('| held min, shortest .. longest | %.1f .. %.1f |' % (S['min_held'], S['max_held']))


#   ── W_FDM2_VERIFY=on: the machine's own numbers at his six 08-03 trades ───────────────────────
#   HIS SIX 08-03 TRADES and the side of the trade being CLOSED at each cadence. The span of the
#   last one, 1841, ENDS AT MIDNIGHT AND THAT BOUND IS MINE - there is no seventh trade to close
#   it. Every other span ends at the next trade.
#
#   THE WALK IS F2.walk, NOT A LOOP OVER THE EVENTS. A hand-rolled loop printed every cadence
#   event in a span, which for 1841 was three - but the mech CLOSES the trade at its first
#   rev-trade, so the 21:03 and 23:01 rows were decision points for a trade that ended at 18:51:55,
#   with populations measured from an open that no longer existed. F2.walk stops where the mech
#   stops, so the table cannot drift from the machine again.
#
#   THE RAW-BAR COLUMNS ARE A DIAGNOSTIC OF THE SUPERSEDED CENSUS, NOT A MACHINE ARM. They count
#   the lift-off bar itself, which is 35 s of lookahead at LIFT_WOB 8, over the row's OWN frozen
#   population - so the only difference between the two pcts is the stamp.
if os.environ.get('W_FDM2_VERIFY') == 'on':
    from optimus9.analysis.jig import lift_off as _lo

    def _raw(sd, pop, a, b):
        n = 0
        for tf in pop:
            bars = _lo(LN['EMR'][tf], sd, K.LIFT_PTS, K.gap_for(tf), K.LIFT_TOL, K.LIFT_WOB)
            if any(int(a) < int(x) <= int(b) for x in bars):
                n += 1
        return n

    HIS = [('0702', '2026-08-03 07:02:00', '2026-08-03 10:08:00', None),
           ('1008', '2026-08-03 10:08:00', '2026-08-03 13:15:00', +1),
           ('1315', '2026-08-03 13:15:00', '2026-08-03 14:06:00', -1),
           ('1406', '2026-08-03 14:06:00', '2026-08-03 16:44:00', +1),
           ('1644', '2026-08-03 16:44:00', '2026-08-03 18:41:00', -1),
           ('1841', '2026-08-03 18:41:00', '2026-08-04 00:00:00', +1)]
    print()
    print('## his 08-03 trades through v4_fdm2 | ws10x hold FDM_X10_WOB %d bars = %d s |'
          ' each walk STOPS at its first rev-trade, as the mech does'
          % (int(K.FDM_X10_WOB), int(K.FDM_X10_WOB) * 5))
    print()
    print('| the trade | target side | the bar | the stage | step 1 | the ws10x-cadence | which |'
          ' reversed, STAMP | pct, STAMP | reversed, RAW lift bar | pct, RAW |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    for nm, t0, t1, psd in HIS:
        a, b = ln.K(t0), ln.K(t1)
        for sd in ((psd,) if psd is not None else (-1, +1)):
            sn = 'HIGH' if sd > 0 else 'LOW'
            sig, rows = F2.walk(LN, sd, a, b)
            if not rows:
                print('| %s | %s | - | NO CADENCE EVENT | - | - | - | - | - | - | - |' % (nm, sn))
                continue
            for r in rows:
                st = str(r['stage'])
                k = '%d of %d' % (int(r['k']), int(r['n'])) if 'k' in r else '-'
                if 'pop' in r:
                    pop = list(r['pop'])
                    rw = _raw(sd, pop, int(r['ev']), int(r['bar']))
                    pr = (rw / len(pop) * 100.0) if pop else 0.0
                    print('| %s | %s | %s | %s | %s | %s | %s | %d of %d | %.1f%% | %d of %d |'
                          ' %.1f%% |'
                          % (nm, sn, ln.U(int(r['bar'])), st, k, ln.U(int(r['bar'])),
                             r['which'], int(r['rv']), len(pop), float(r['pct']),
                             rw, len(pop), pr))
                else:
                    print('| %s | %s | %s | %s | %s | - | - | - | - | - | - |'
                          % (nm, sn, ln.U(int(r['bar'])), st, k))
            if sig is not None:
                print('| %s | %s | %s | TRADE CLOSES | - | - | - | - | - | - | - |'
                      % (nm, sn, ln.U(int(sig) + 1)))
