"""HIS ws1b FIRING MECH, READ AGAINST THE 2026-08-29 23:50 SHORT. Nothing is decided here.

Joe 1029, the flow verbatim:

    -there is no trade open  (either because of a STOP, or because the machine is cold-starting)
    -walk
    -if ws1b crosses from oob to ib (candidate-side)
    --if ws5Mage is oob or has been oob in the last 5 minutes on the candidate-side
    ---anchor on the ws5Mage extremum.  the anchor is for the next step to align with
    ---if at least 2 ws{>5}Mage wsf lines are printing a value that is away from the candidate
       side, at the anchor bar (ie: high candidate-side and line values are less than ws5Mage, low
       candidate-side and lines are printing values higher than ws5Mage)
    ----open the trade, direction: away from candidate-side

    does that mech match the already formed 2350 SHORT?  the ws1b firing should move 2350 forward
    to 2353

SO FOUR READS, in his order, over 2026-08-29 23:00 .. 2026-08-30 00:30:

    1  every ws1b oob->ib cross, raw bar AND the LIN2_CROSS_WOB 12 confirm bar, both sides.
    2  the ws5Mage oob runs on each side, with the bar and value of the extremum.
    3  for each cross: was ws5Mage oob at it, or oob inside the trailing 5 min.
    4  the ws6Mage..ws12Mage ladder AT THE ANCHOR BAR against ws5Mage at that same bar.

wsf is ws1..ws12 - his 1017 band names - so "ws{>5}Mage wsf lines" is ws6..ws12.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
from optimus9.analysis.jig import oob_ib_cross
sys.stderr = _e

A, B = ln.K('2026-08-29 23:00:00'), ln.K('2026-08-30 00:30:00')
BAND = list(range(6, int(K.L2_MOM_MAXTF) + 1))
LOOKBACK_S = 300                      # his "last 5 minutes"
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = CP.arm_lines(E)
B1 = np.asarray(CL['b'], float)                                  # ws1b, CLOSED
MG = {t: np.asarray(CP.line('ws%dMage' % t, t * 60), float) for t in range(1, 13)}
M5 = MG[5]
W = max(1, int(K.LIN2_CROSS_WOB))

print('# HIS ws1b FIRING MECH, READ AGAINST THE 2026-08-29 23:50 SHORT')
print('# SPAN %s .. %s | RULED_OK %s' % (ln.U(A), ln.U(B), K.RULED_OK))
print('# oob is %.0f/%.0f. ws1b and the Mage ladder are the CLOSED reads.' % (K.OOB_LO, K.OOB_HI))
print('# LIN2_CROSS_WOB %d bars = %d s - his 1027 "add the wob12 to all crosses".' % (W, W * 5))
print('# the trailing oob lookback is %d s - his "last 5 minutes".' % LOOKBACK_S)
print('# the band is ws6..ws%d - wsf is ws1..ws12, his 1017 names.' % K.L2_MOM_MAXTF)
print('')

# ---- 1. every ws1b oob -> ib cross -----------------------------------------------------------
print('## 1 - every ws1b oob->ib cross in the span')
print('')
print('| the raw cross bar | the wob %d confirm bar | the candidate side | ws1b at raw |'
      ' ws1b at confirm |' % W)
print('|---|---|---|---|---|')
crosses = []
for c, cf, sd in oob_ib_cross(B1, K.OOB_HI, K.OOB_LO, W):
    c, cf, sd = int(c), int(cf), int(sd)
    if not (A <= c <= B):
        continue
    crosses.append((c, cf, sd))
    print('| %s | %s | %s | %.2f | %.2f |'
          % (ln.U(c), ln.U(cf), 'HIGH' if sd > 0 else 'LOW', float(B1[c]), float(B1[cf])))
print('')

# ---- 2. the ws5Mage oob runs ------------------------------------------------------------------
print('## 2 - every ws5Mage oob RUN in the span, with its extremum')
print('')
print('| the side | the run enters | the run leaves | bars | the extremum bar |'
      ' ws5Mage at the extremum |')
print('|---|---|---|---|---|---|')
runs = {}
for sd, nm in ((+1, 'HIGH'), (-1, 'LOW')):
    m = K.oob_mask(M5, sd)
    i = A
    out = []
    while i <= B:
        if m[i] and not m[i - 1]:
            j = i
            while j + 1 < len(m) and m[j + 1]:
                j += 1
            seg = M5[i:j + 1]
            k = i + (int(np.nanargmax(seg)) if sd > 0 else int(np.nanargmin(seg)))
            out.append((i, j, k))
            print('| %s | %s | %s | %d | %s | %.2f |'
                  % (nm, ln.U(i), ln.U(j), j - i + 1, ln.U(k), float(M5[k])))
            i = j + 1
            continue
        i += 1
    runs[sd] = out
print('')

# ---- 3 and 4. the gate and the ladder test, per cross ----------------------------------------
print('## 3 - the ws5Mage gate at each cross, and the anchor it selects')
print('')
print('| the raw cross bar | the confirm bar | candidate side | ws5Mage oob AT the cross? |'
      ' oob inside the trailing %d s? | the anchor bar | ws5Mage at the anchor |' % LOOKBACK_S)
print('|---|---|---|---|---|---|---|')
fires = []
for c, cf, sd in crosses:
    m = K.oob_mask(M5, sd)
    at = bool(m[c])
    lb = c - LOOKBACK_S // 5
    recent = bool(m[max(0, lb):c + 1].any())
    anchor = None
    for i0, j0, k0 in runs[sd]:
        if i0 <= c or (i0 <= c + 0 and j0 >= lb) or (j0 >= lb and i0 <= c):
            if j0 >= lb and i0 <= c:
                anchor = k0
    print('| %s | %s | %s | %s | %s | %s | %s |'
          % (ln.U(c), ln.U(cf), 'HIGH' if sd > 0 else 'LOW', 'YES' if at else 'no',
             'YES' if recent else 'no', ln.U(anchor) if anchor is not None else '-',
             '%.2f' % float(M5[anchor]) if anchor is not None else '-'))
    if (at or recent) and anchor is not None:
        fires.append((c, cf, sd, anchor))
print('')

print('## 4 - the ws6..ws%d Mage ladder AT THE ANCHOR BAR, per candidate cross' % K.L2_MOM_MAXTF)
print('')
print('| the cross bar | candidate side | the anchor bar | the line | value at the anchor |'
      ' ws5Mage at the anchor | away from the candidate side? |')
print('|---|---|---|---|---|---|---|')
for c, cf, sd, anchor in fires:
    v5 = float(M5[anchor])
    for t in BAND:
        v = float(MG[t][anchor])
        away = (v < v5) if sd > 0 else (v > v5)
        print('| %s | %s | %s | ws%dMage | %.2f | %.2f | %s |'
              % (ln.U(c), 'HIGH' if sd > 0 else 'LOW', ln.U(anchor), t, v, v5,
                 'YES' if away else 'no'))
print('')

print('## the verdict per cross')
print('')
print('| the raw cross bar | the confirm bar | candidate side | the anchor bar |'
      ' lines away at the anchor | required | FIRES? | the trade side |')
print('|---|---|---|---|---|---|---|---|')
need = int(K.LIN2_CHAIN_OPEN_LINES)
for c, cf, sd, anchor in fires:
    v5 = float(M5[anchor])
    got = [t for t in BAND
           if np.isfinite(MG[t][anchor])
           and ((float(MG[t][anchor]) < v5) if sd > 0 else (float(MG[t][anchor]) > v5))]
    ok = len(got) >= need
    print('| %s | %s | %s | %s | %d - %s | %d | %s | %s |'
          % (ln.U(c), ln.U(cf), 'HIGH' if sd > 0 else 'LOW', ln.U(anchor), len(got),
             ','.join('ws%d' % t for t in got) if got else 'none', need,
             'YES' if ok else 'no', ('SHORT' if sd > 0 else 'LONG') if ok else '-'))
print('')
print('| the read | value |')
print('|---|---|')
print('| his prediction | the 23:50 open moves forward to ~23:53 |')
print('| crosses in the span | %d |' % len(crosses))
print('| crosses passing the ws5Mage gate with an anchor | %d |' % len(fires))
