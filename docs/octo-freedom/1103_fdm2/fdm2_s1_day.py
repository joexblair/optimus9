"""His 1104 ask: one day where the step-1 towards difference is visible, line by line.

*"find a day where I can see this issue, and show me the timestamped rows. add whatever columns you
think I'll need."*

THE ISSUE: at a cadence event, step 1 counts the ws4..ws30 lines that are ex-20/80 on the target
side AND travelling toward it. Two readings of "travelling toward it" disagree on 297 of 753 events
across the tape, and always the same way - the banked rolling-extremum reading counts FEWER.

WHAT THIS PRINTS, per cadence event on the day:
    both counts, the two verdicts, and for EVERY line the current reading counted, that line's own
    numbers under both readings - so the disagreement is readable per line rather than per event.

THE COLUMNS I ADDED and why he will want them:
    its value           the line's chart-matched value at the event bar. It is what ex-20/80 tested
    the block extreme   the current reading's anchor: the opposed extreme of its own block
    travel              value minus that extreme. The current reading calls the line `towards` when
                        this is positive on a HIGH target, negative on a LOW one
    the rolling extreme the banked reading's anchor: the most extreme value on the TARGET side since
                        the trade opened, up to this bar
    the gap             how far the line sits from that rolling extreme. The banked reading calls
                        the line `towards` only when this is exactly 0
    at which bar        the bar the rolling extreme was set on, so the age of the anchor is visible

NOTHING IS CHANGED. Both readings are computed side by side; step 1 still runs the current one.
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
    from optimus9.compute.rule2_trajectory import opposed_extrema as OPX
finally:
    sys.stderr = _e

DAY = os.environ['W_FDM2_S1_DAY']
LN = F2.load()
A, B = ln.K(DAY + ' 00:00:00'), min(ln.K(DAY + ' 23:59:55'), len(LN['close']) - 1)
CL = np.asarray(LN['close'], float)
LO, HI = int(K.FDM_STEP1_ABOVE_TF) + 1, int(LN['HI'])
N = HI - LO + 1
print('## step 1\'s two towards readings, line by line | %s' % DAY)
print('# the count is the ws%d..ws%d lines ex-%g/%g on the target side AND travelling toward it'
      % (LO, HI, *K.fnc_pair(K.FDM_FNC_2080)))
print('# 0 fires a rev-trade, 1 or more walks on. Only a 0 / non-0 flip changes what the machine does')
print('# the current reading anchors on the line\'s own block extreme; the banked one on the rolling')
print('# target-side extremum since the trade opened, and calls a line towards only at a gap of 0')
print('# every value is read AT the event bar. The MAE/MFE is sweep-pivots\' scoring scale')
print()

SIGS = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'])
g = SIGS[0]
LEGS = F2.legs(LN, (SG.fire_bar(g), SG.target_side(SG.direction(int(g['side']))),
                    'fdm re-entry %s' % ln.U(int(g['bar']))), len(LN['close']) - 1, resig=SIGS)
EV = []
for L in LEGS:
    sd, o, ex = int(L['side']), int(L['opn']), int(L['exit'])
    for evb, s0, why in F2.cadence_events(LN, sd, o + 1, ex):
        if A <= int(evb) <= B:
            EV.append((int(evb), sd, o, ex, L['src'], L['ctype'], float(L['rel'])))
print('| the cadence event | the oob side | the trade it decides | its open | its exit | how it'
      " ended | the trade realised %% | the count now | the count on the Jig's producer | the verdict"
      " now | on the Jig's producer | they | MAE %% | MFE %% |")
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
ROWS = []
for evb, sd, o, ex, src, ctype, rel in EV:
    k_old, k_new, det = 0, 0, []
    for tf in range(LO, HI + 1):
        v = float(LN['CPR'][tf][evb])
        if not F2.ex2080(v, sd):
            continue
        t_old = F2.towards(LN['CPR'][tf], tf, evb, sd)
        r = TA(LN['EMR'][tf], evb, sd, o)
        t_new = r['state'] == 'towards'
        k_old += 1 if t_old else 0
        k_new += 1 if t_new else 0
        if t_old or t_new:
            det.append((tf, v, t_old, t_new, r))
    v_old = 'rev-trade' if k_old == 0 else 'walk'
    v_new = 'rev-trade' if k_new == 0 else 'walk'
    sw = SP.swing(int(evb), -sd, CL)
    mae = mfe = None
    if sw and sw.get('close') is not None:
        z = int(sw['close'])
        a2, b2 = min(int(evb), z), max(int(evb), z)
        seg = CL[a2:b2 + 1]
        pb = float(CL[int(evb)])
        if np.isfinite(seg).any():
            up = (float(np.nanmax(seg)) - pb) / pb * 100.0
            dn = (float(np.nanmin(seg)) - pb) / pb * 100.0
            mfe, mae = (up, dn) if sd > 0 else (-dn, -up)
    ROWS.append((evb, sd, o, det, k_old, k_new, v_old, v_new))
    print('| %s | %s | %s | %s | %s | %s | %+.3f | %d of %d | %d of %d | %s | %s | %s | %s | %s |'
          % (ln.U(evb), 'HIGH' if sd > 0 else 'LOW', 'LONG' if sd > 0 else 'SHORT',
             ln.U(o), ln.U(ex), ctype, rel, k_old, N, k_new, N, v_old, v_new,
             'agree' if v_old == v_new else 'DISAGREE',
             '-' if mae is None else '%+.3f' % mae, '-' if mfe is None else '%+.3f' % mfe))

print()
print('## the lines behind each DISAGREE, one row per line')
print('# only the lines at least one reading counted are listed. A line neither counted is not here')
print()
print("| the cadence event | the line | its value | counted now | counted on the Jig's producer |"
      ' the block extreme | travel | the rolling extreme | at which bar | the gap |')
print('|---|---|---|---|---|---|---|---|---|---|')
for evb, sd, o, det, k_old, k_new, v_old, v_new in ROWS:
    if v_old == v_new:
        continue
    for tf, v, t_old, t_new, r in det:
        bi, best, _ = OPX(LN['CPR'][tf], sd, evb, K.traj_block(tf))
        trav = (v - best) if best is not None and np.isfinite(best) else float('nan')
        print('| %s | ws%dr | %.2f | %s | %s | %s | %s | %.2f | %s | %+.2f |'
              % (ln.U(evb), tf, v, 'yes' if t_old else '-', 'yes' if t_new else '-',
                 '%.2f' % best if best is not None and np.isfinite(best) else '-',
                 '%+.2f' % trav if np.isfinite(trav) else '-',
                 r['extremum'], ln.U(int(r['at'])), r['gap']))
print()
print('| the day | value |')
print('|---|---|')
print('| cadence events | %d |' % len(ROWS))
print('| they DISAGREE | %d |' % sum(1 for r in ROWS if r[6] != r[7]))
print('| rev-trades now | %d |' % sum(1 for r in ROWS if r[6] == 'rev-trade'))
print("| rev-trades on the Jig's producer | %d |" % sum(1 for r in ROWS if r[7] == 'rev-trade'))
