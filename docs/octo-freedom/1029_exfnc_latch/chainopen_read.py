"""WHAT THE Mage LADDER DID AROUND 2026-08-29 23:45 - the read behind his chain-open spec.

Joe 1029: *"the chain open should be on the ws5Mage oob with at least one higher TF Mage printing
closer to 50. that moment is 08-29 ~2345, and it's a SHORT"*.

HIS TIME IS AN ESTIMATE, so this prints the whole 23:00..2026-08-30 00:30 span and lets the bars
say where the condition sits. NOTHING IS DECIDED HERE - it is the read the gate is built on.

"closer to 50" is printed as |value - 50| per line so the comparison against ws5Mage is on the page
rather than assumed.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_closed_prev as CP
sys.stderr = _e

A, B = ln.K('2026-08-29 23:00:00'), ln.K('2026-08-30 00:30:00')
TFS = list(range(1, 13))
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in TFS}     # CLOSED
MGE = {t: ln.line('ws%dMage' % t) for t in TFS}             # EMERGING

print('# THE Mage LADDER, 2026-08-29 23:00:00 .. 2026-08-30 00:30:00')
print('# oob is %.0f/%.0f - K.oob, the same test arm_race already applies to a Mage.'
      % (K.OOB_LO, K.OOB_HI))
print('# RULED_OK %s' % K.RULED_OK)
print('')

# ---- 1. every ws5Mage oob entry in the span, both reads and both sides ----------------------
print('## every bar ws5Mage ENTERS oob in the span')
print('')
print('| the bar | read | side | ws5Mage | ws5Mage dist from 50 |')
print('|---|---|---|---|---|')
hits = []
for nm, D in (('closed', MGL), ('emerging', MGE)):
    v = np.asarray(D[5], float)
    for sd, sn in ((+1, 'HIGH'), (-1, 'LOW')):
        m = K.oob_mask(v, sd)
        for i in range(A, B + 1):
            if m[i] and not m[i - 1]:
                hits.append((i, nm, sn, float(v[i])))
for i, nm, sn, x in sorted(hits):
    print('| %s | %s | %s | %.2f | %.2f |' % (ln.U(i), nm, sn, x, abs(x - 50.0)))
print('')

# ---- 2. the whole ladder at each of those bars, one record per row -------------------------
print('## the full Mage ladder at each ws5Mage oob entry')
print('')
print('| the bar | read | the ws5Mage side | the line | value | dist from 50 |'
      ' closer to 50 than ws5Mage? | higher TF than ws5? |')
print('|---|---|---|---|---|---|---|---|')
for i, nm, sn, x in sorted(hits):
    D = MGL if nm == 'closed' else MGE
    d5 = abs(x - 50.0)
    for t in TFS:
        val = float(np.asarray(D[t], float)[i])
        d = abs(val - 50.0)
        print('| %s | %s | %s | ws%dMage | %.2f | %.2f | %s | %s |'
              % (ln.U(i), nm, sn, t, val, d, 'YES' if d < d5 else 'no',
                 'YES' if t > 5 else 'no'))
print('')

# ---- 3. his 2345 bar exactly, both reads ---------------------------------------------------
for stamp in ('2026-08-29 23:45:00',):
    k = ln.K(stamp)
    print('## the ladder at %s - his quoted moment' % stamp)
    print('')
    print('| the line | closed | closed dist from 50 | emerging | emerging dist from 50 |'
          ' closed oob? |')
    print('|---|---|---|---|---|---|')
    for t in TFS:
        c = float(np.asarray(MGL[t], float)[k]); e = float(np.asarray(MGE[t], float)[k])
        ob = ('HIGH' if K.oob(c, +1) else ('LOW' if K.oob(c, -1) else 'no'))
        print('| ws%dMage | %.2f | %.2f | %.2f | %.2f | %s |'
              % (t, c, abs(c - 50.0), e, abs(e - 50.0), ob))
    print('')
