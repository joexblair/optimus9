"""His 1104 step-1 measurement: the two `towards` readings, side by side, at every cadence event.

HIS PLAN, his words, step 2: *"report the disagreement rate and which way it goes, and collect the
maemfe difference, retaining the per cadence data for further analysis if requested"*.

NOTHING IS CHANGED. v4_fdm2.step1 keeps reading v4_fdm2.towards. This file computes the SECOND
count beside it and reports the difference, so the ruling is his to make on numbers.

THE TWO READINGS
    v4_fdm2.towards       what step 1 runs today. The travel from the block's opposed extreme to
                          the bar, so a line between its block's high and low satisfies BOTH sides
    jig.towards_away      the producer he asked for on the Jig, 1103 - *"a trade's direction sets towards and away"* - one
                          anchor per side, the rolling target-side extremum, so a line cannot be
                          both. `towards` is the gap from that extremum being exactly 0

WHAT STEP 1 DOES WITH IT: counts the ws4..ws30 lines that are ex-20/80 on the target side AND
travelling toward it, at the cadence event bar. A count of 0 fires a rev-trade; 1 or more walks on.
So the VERDICT is binary, and only a flip between 0 and non-0 changes what the machine does.

THE ANCHOR FOR towards_away is the trade's own open, which is what the rolling extremum needs and
what the fdm2-conf table uses. The cadence event is read on the trade that is open at it.

CAUSALITY. Both counts read the event bar and nothing after it. The MAE/MFE is SCORING on
sweep-pivots' leg, hindsight by its own ruling, and no count here touches it.

THE PER-CADENCE ROWS ARE KEPT in the .md this writes, every event one row, for whatever he asks
next.
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
    import v4_sweep_pivots as SP
    import ln
    from optimus9.analysis.jig import towards_away as TA
    from optimus9.analysis import jig as JIG
finally:
    sys.stderr = _e

OUT = os.environ.get('W_FDM2_S1_OUT', 'step1_repaired_94d.md')
#   WHICH SECOND READING. 'repaired' is jig.fdm2_cad_mom_detector as he repaired it on 1104 - the
#   reversal gate first, the side-owned extremum, closed-prev values and the lift-off on emerging.
#   'towards_away' is the earlier arm, kept runnable because the 297-event figure came off it and
#   that figure is now stale. HIS 1104: *"that hasn't been reviewed since the jig producer's
#   repair. now the jig producer does not print rev-trade at 1611"*.
READ = os.environ.get('W_FDM2_S1_READ', 'repaired')
assert READ in ('repaired', 'towards_away'), 'W_FDM2_S1_READ is %r' % READ
LN = F2.load()
B = len(LN['close']) - 1
CL = np.asarray(LN['close'], float)
LO = int(K.FDM_STEP1_ABOVE_TF) + 1
HI = int(LN['HI'])
W = io.open(OUT, 'w', encoding='utf-8')


def say(l=''):
    W.write(l + '\n')
    W.flush()


def counts(side, bar, anchor):
    """step 1's count under each reading at `bar`. -> (as it runs now, on the Jig).

    NEITHER IS BANKED OVER THE OTHER. His 1104: *"that conversation was never converted to
    a banked mech as far as I'm concerned"*. He asked for the rolling-extremum producer on
    the Jig so it would not be lost; he never ruled it into step 1, and no default moved.
    """
    k_old = k_new = 0
    for tf in range(LO, HI + 1):
        if not F2.ex2080(float(LN['CPR'][tf][bar]), side):
            continue
        if F2.towards(LN['CPR'][tf], tf, bar, side):
            k_old += 1
        #   THE SECOND READING. At 'repaired' every VALUE is closed-prev and only the lift-off
        #   reads emerging, his 1104 standard, and `away` needs a lift-off reversal in the span.
        #   The anchor is the trade's own open at either setting.
        if READ == 'repaired':
            st = JIG.fdm2_cad_mom_detector(np.asarray(LN['CPR'][tf], float),
                                       np.asarray(LN['EMR'][tf], float), bar, side, anchor,
                                       int(K.LIFT_PTS), K.gap_for(tf), float(K.LIFT_TOL),
                                       int(K.LIFT_WOB))['state']
        else:
            st = TA(LN['EMR'][tf], bar, side, anchor)['state']
        if st == 'towards':
            k_new += 1
    return k_old, k_new


say('# his 1104 step-1 measurement | the two `towards` readings at every cadence event | 94 days')
say('# NOTHING IS CHANGED: step 1 still reads v4_fdm2.towards. This is the difference, measured.')
say('# the count is the ws%d..ws%d lines ex-%g/%g on the target side AND travelling toward it'
    % (LO, HI, *K.fnc_pair(K.FDM_FNC_2080)))
say('# the verdict is binary: 0 fires a rev-trade, 1 or more walks on. Only a 0/non-0 flip matters.')
say('# MAE/MFE is the event bar to the bar sweep-pivots ends the leg on - scoring, hindsight, and')
say('# no count here reads it. The counts read the event bar and nothing after it.')
say("# the anchor for the Jig's producer is the trade the cadence event lands inside")
say('# the second reading is W_FDM2_S1_READ %s' % READ)
say('# repaired = jig.fdm2_cad_mom_detector: a lift-off reversal must exist in the span, the extremum')
say('# belongs to the side, values are closed-prev and only the lift-off reads emerging')
say('# the lift-off: LIFT_PTS %d samples, LIFT_TOL %g r-points, LIFT_WOB %d bars = %d s,'
    ' GAP_PER_TF %g bars per TF-minute'
    % (int(K.LIFT_PTS), float(K.LIFT_TOL), int(K.LIFT_WOB), int(K.LIFT_WOB) * 5,
       float(K.GAP_PER_TF)))
say()
say('| the cadence event | the oob side | the trade | its open | its exit | how it ended |'
    ' what it realised %% | what it had in hand here %% | the count now |'
    ' the count on the Jig | the verdict now | on the Jig | they |'
    ' rev-trading here realises %% | the difference %% | MAE %% | MFE %% |')
say('|' + '---|' * 17)

SIGS = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'])
assert SIGS, 'no re-entry signals on the tape'
ROWS = []
g = SIGS[0]
opn = SG.fire_bar(g)
side = SG.target_side(SG.direction(int(g['side'])))
src = 'fdm re-entry %s' % ln.U(int(g['bar']))
LEGS = F2.legs(LN, (opn, side, src), B, resig=SIGS)
for L in LEGS:
    sd, o, ex = int(L['side']), int(L['opn']), int(L['exit'])
    for evb, s0, why in F2.cadence_events(LN, sd, o + 1, ex):
        k_old, k_new = counts(sd, int(evb), o)
        v_old = 'rev-trade' if k_old == 0 else 'walk'
        v_new = 'rev-trade' if k_new == 0 else 'walk'
        sw = SP.swing(int(evb), -sd, CL)
        mae = mfe = None
        z = None
        if sw and sw.get('close') is not None:
            z = int(sw['close'])
            a, b2 = min(int(evb), z), max(int(evb), z)
            seg = CL[a:b2 + 1]
            pb = float(CL[int(evb)])
            if np.isfinite(seg).any():
                up = (float(np.nanmax(seg)) - pb) / pb * 100.0
                dn = (float(np.nanmin(seg)) - pb) / pb * 100.0
                mfe, mae = (up, dn) if sd > 0 else (-dn, -up)
        #   ── THE TRADING DECISION, his 1104: *"the 2 tables are missing the most important
        #      part - the trading decision. isn't that what we're working to resolve?"* ──────────
        #   WHAT THE MACHINE DID: it walked on at this event and the leg exited where it exited.
        #   WHAT THE OTHER READING WOULD DO: rev-trade HERE, which closes the leg at the router's
        #   own close bar, the event bar + 1. Both are priced off the leg's own open, signed by
        #   the leg's side, so the two are the same measurement on the same leg.
        #   THIS IS LEG-LEVEL ONLY. A rev-trade also OPENS the opposite trade and every leg after
        #   it moves, which no column can carry - it is a different run.
        po = float(CL[int(o)])
        here = sd * (float(CL[min(int(evb) + 1, B)]) - po) / po * 100.0
        ROWS.append(dict(ev=int(evb), sd=sd, opn=o, k_old=k_old, k_new=k_new,
                         v_old=v_old, v_new=v_new, mae=mae, mfe=mfe, z=z,
                         exit=int(L['exit']), ctype=str(L['ctype']), rel=float(L['rel']),
                         here=here, diff=here - float(L['rel'])))
        say('| %s | %s | %s | %s | %s | %s | %+.3f | %+.3f | %d of %d | %d of %d | %s | %s |'
            ' %s | %+.3f | %+.3f | %s | %s |'
            % (ln.U(int(evb)), 'HIGH' if sd > 0 else 'LOW',
               'LONG' if sd > 0 else 'SHORT', ln.U(o), ln.U(int(L['exit'])), str(L['ctype']),
               float(L['rel']), here, k_old, HI - LO + 1, k_new, HI - LO + 1,
               v_old, v_new, 'agree' if v_old == v_new else 'DISAGREE',
               here, here - float(L['rel']),
               '-' if mae is None else '%+.3f' % mae,
               '-' if mfe is None else '%+.3f' % mfe))

med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
say()
say('| the disagreement rate | value |')
say('|---|---|')
say('| cadence events | %d |' % len(ROWS))
say('| the two readings agree on the verdict | %d |' % sum(1 for r in ROWS if r['v_old'] == r['v_new']))
say('| they DISAGREE | %d |' % sum(1 for r in ROWS if r['v_old'] != r['v_new']))
say("| it runs rev-trade where the Jig's producer walks | %d |"
    % sum(1 for r in ROWS if r['v_old'] == 'rev-trade' and r['v_new'] == 'walk'))
say("| it walks where the Jig's producer rev-trades | %d |"
    % sum(1 for r in ROWS if r['v_old'] == 'walk' and r['v_new'] == 'rev-trade'))
say('| rev-trade verdicts, as it runs now | %d |' % sum(1 for r in ROWS if r['v_old'] == 'rev-trade'))
say("| rev-trade verdicts, on the Jig's producer | %d |" % sum(1 for r in ROWS if r['v_new'] == 'rev-trade'))
say('| median count now | %s |' % med([r['k_old'] for r in ROWS]))
say("| median count on the Jig's producer | %s |" % med([r['k_new'] for r in ROWS]))
say()
#   ── THE TRADING DECISION, aggregated over the events where the two readings differ ───────────
_d = [r for r in ROWS if r['v_old'] != r['v_new']]
say('| the trading decision on the %d events where they differ | value |' % len(_d))
say('|---|---|')
if _d:
    say('| what those legs actually realised, summed %% | %+.3f |' % sum(r['rel'] for r in _d))
    say('| what rev-trading at the event realises, summed %% | %+.3f |' % sum(r['here'] for r in _d))
    say('| the difference, summed %% | %+.3f |' % sum(r['diff'] for r in _d))
    say('| the difference, median %% | %+.3f |' % med([r['diff'] for r in _d]))
    say('| events where rev-trading here is BETTER | %d of %d |'
        % (sum(1 for r in _d if r['diff'] > 0), len(_d)))
    say('| events where rev-trading here is WORSE | %d of %d |'
        % (sum(1 for r in _d if r['diff'] < 0), len(_d)))
    say('| the best single difference %% | %+.3f |' % max(r['diff'] for r in _d))
    say('| the worst single difference %% | %+.3f |' % min(r['diff'] for r in _d))
    say('| of those legs, how many the stop ended | %d of %d |'
        % (sum(1 for r in _d if 'STOP' in r['ctype']), len(_d)))
say('| what this leaves out | a rev-trade also OPENS the opposite trade, so every leg after it'
    ' moves. That is a different run, not a column |')
say()
say('| the MAE/MFE difference, by what the two readings do | events | median MAE % |'
    ' median MFE % | sum MAE % | sum MFE % | MFE > abs(MAE) |')
say('|---|---|---|---|---|---|---|')
GRP = (('both rev-trade', lambda r: r['v_old'] == 'rev-trade' and r['v_new'] == 'rev-trade'),
       ('both walk', lambda r: r['v_old'] == 'walk' and r['v_new'] == 'walk'),
       ('only it rev-trades', lambda r: r['v_old'] == 'rev-trade' and r['v_new'] == 'walk'),
       ("only the Jig's producer rev-trades", lambda r: r['v_old'] == 'walk' and r['v_new'] == 'rev-trade'),
       ('every rev-trade it fires', lambda r: r['v_old'] == 'rev-trade'),
       ("every rev-trade the Jig's producer fires", lambda r: r['v_new'] == 'rev-trade'))
for nm, f in GRP:
    rs = [r for r in ROWS if f(r) and r['mae'] is not None]
    if not rs:
        say('| %s | 0 | - | - | - | - | - |' % nm)
        continue
    m = [r['mae'] for r in rs]
    x = [r['mfe'] for r in rs]
    say('| %s | %d | %+.3f | %+.3f | %+.3f | %+.3f | %d of %d |'
        % (nm, len(rs), med(m), med(x), sum(m), sum(x),
           sum(1 for a, b in zip(m, x) if b > abs(a)), len(rs)))
say()
say('| what this does NOT measure | the chain consequence of a flipped verdict. A rev-trade opens'
    ' the opposite trade and every leg after it moves, which is a different run, not a column |')
W.close()
print('wrote %s, %d cadence events' % (OUT, len(ROWS)))
