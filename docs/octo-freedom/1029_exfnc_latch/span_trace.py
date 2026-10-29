"""Every 5 s bar of ws5Mage and ws1b across the span he named, with the mech marked per row.

Joe 1029: *"print a ~144 row table that shows the 5s data for ws5Mage line values and crosses, and
ws1b line values and crosses, between ws5Mage crossing to oob after 08-30 2345 and its cross to ib
near 2355 - add a column that you'll populate if you see that a row is matching any part of the
mech"*.

Both lines are the LIVE read. The last-completed-bar read is dropped.

The highest-so-far column is the running furthest point ws5Mage has reached since its own run
began, up to and including that bar. At a firing bar that value IS the anchor, and it uses no bar
after the firing bar.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K
sys.stderr = _e

HI, LO = K.OOB_HI, K.OOB_LO
M5 = np.asarray(ln.line('ws5Mage'), float)
B1 = np.asarray(ln.line('ws1b'), float)
MG = {t: np.asarray(ln.line('ws%dMage' % t), float) for t in range(1, 13)}
BAND = list(range(6, int(K.L2_MOM_MAXTF) + 1))
NEED = int(K.LIN2_CHAIN_OPEN_LINES)
LB = int(K.LIN2_CHAIN_OPEN_LOOKBACK_S) // 5

m5hi = K.oob_mask(M5, +1)
b1hi = K.oob_mask(B1, +1)

#   the span: from the ws5Mage crossing to beyond-85 after 2026-08-29 23:45, to 144 bars later.
S = ln.K('2026-08-29 23:45:00')
start = None
for i in range(S, S + 4000):
    if m5hi[i] and not m5hi[i - 1]:
        start = i
        break
assert start is not None, 'no ws5Mage crossing to beyond 85 after 2026-08-29 23:45'
A = start
B = A + 143

print('# EVERY 5 s BAR, ws5Mage AND ws1b, WITH THE MECH MARKED PER ROW')
print('# the span starts at the ws5Mage crossing to beyond %.0f after 2026-08-29 23:45:00,'
      ' and runs 144 bars = 12 minutes.' % HI)
print('# %s .. %s | both lines are the LIVE read | RULED_OK %s' % (ln.U(A), ln.U(B), K.RULED_OK))
print('# the mech: ws1b crosses in from beyond %.0f, then ws5Mage must be beyond %.0f now or'
      ' inside %d s,' % (HI, HI, K.LIN2_CHAIN_OPEN_LOOKBACK_S))
print('#   then at the furthest point ws5Mage reached, %d or more of ws6..ws%d Mage must print'
      ' below it, then open AWAY from the side ws1b came in from.'
      % (NEED, K.L2_MOM_MAXTF))
print('# highest so far = the furthest ws5Mage has reached since its own run began, up to this'
      ' bar. No later bar is read.')
print('')
print('| the bar | ws5Mage | ws5Mage beyond %.0f? | ws5Mage event | highest ws5Mage so far |'
      ' ws1b | ws1b beyond %.0f? | ws1b event | the mech at this row |' % (HI, HI))
print('|---|---|---|---|---|---|---|---|---|')

run_from = None
if m5hi[A]:
    j = A
    while j > 0 and m5hi[j - 1]:
        j -= 1
    run_from = j
best = None
opened = None
for i in range(A, B + 1):
    if m5hi[i] and not m5hi[i - 1]:
        run_from = i
        best = None
    if not m5hi[i]:
        pass
    if run_from is not None and m5hi[i]:
        seg = M5[run_from:i + 1]
        best = float(np.nanmax(seg)) if np.isfinite(seg).any() else None
        best_bar = run_from + int(np.nanargmax(seg)) if np.isfinite(seg).any() else None
    m5ev = ''
    if m5hi[i] and not m5hi[i - 1]:
        m5ev = 'crosses to beyond %.0f' % HI
    elif (not m5hi[i]) and m5hi[i - 1]:
        m5ev = 'crosses back inside'
    b1ev = ''
    mech = ''
    if b1hi[i] and not b1hi[i - 1]:
        b1ev = 'crosses to beyond %.0f' % HI
    elif (not b1hi[i]) and b1hi[i - 1]:
        b1ev = 'crosses IN from beyond %.0f' % HI
        if opened is not None:
            mech = ('step 1 FAILS - a trade is already open from %s, so this crossing is not'
                    ' taken' % ln.U(opened))
        else:
            gate_now = bool(m5hi[i])
            gate_rec = bool(m5hi[max(0, i - LB):i + 1].any())
            if not (gate_now or gate_rec):
                mech = ('step 2 ok - ws1b crosses in / step 3 FAILS - ws5Mage not beyond %.0f'
                        ' now nor inside %d s' % (HI, K.LIN2_CHAIN_OPEN_LOOKBACK_S))
            else:
                j = i if m5hi[i] else None
                if j is None:
                    for q in range(i, max(0, i - LB) - 1, -1):
                        if m5hi[q]:
                            j = q
                            break
                r0 = j
                while r0 > 0 and m5hi[r0 - 1]:
                    r0 -= 1
                seg = M5[r0:j + 1]
                k = r0 + int(np.nanargmax(seg))
                v0 = float(M5[k])
                got = [t for t in BAND
                       if np.isfinite(MG[t][k]) and float(MG[t][k]) < v0]
                if len(got) >= NEED:
                    opened = i
                    mech = ('step 2 ok / step 3 ok %s / step 4 anchor %s at %.2f / step 5 %d of 7'
                            ' below it - %s / step 6 OPEN SHORT'
                            % ('beyond now' if gate_now else 'inside %d s' % K.LIN2_CHAIN_OPEN_LOOKBACK_S,
                               ln.U(k), v0, len(got), ','.join('ws%d' % t for t in got)))
                else:
                    mech = ('step 2 ok / step 3 ok / step 4 anchor %s at %.2f / step 5 FAILS'
                            ' %d of 7 below it, %d needed' % (ln.U(k), v0, len(got), NEED))
    if not mech and run_from is not None and m5hi[i] and m5ev:
        mech = 'the ws5Mage gate run begins here'
    print('| %s | %.2f | %s | %s | %s | %.2f | %s | %s | %s |'
          % (ln.U(i), float(M5[i]), 'yes' if m5hi[i] else 'no', m5ev or '-',
             '%.2f' % best if best is not None else '-',
             float(B1[i]), 'yes' if b1hi[i] else 'no', b1ev or '-', mech or '-'))
