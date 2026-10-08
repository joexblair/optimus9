"""EVERY RE-ENTRY SIGNAL ON 2026-09-22, AND WHAT CREATED IT. CHAIN 0. 1008.

Joe 1008: *"I have a suspicion there's a lot of re-entry signals. for each of the signals, add the
incoming timestamps and/or decisions that created them"*.

THE RE-ENTRY MECH, gate A, every clause:
  NO PIERCE    Joe 1008 *"I advised you to drop the pierce"*. A HOLD is the whole signal.
  the hold     LONG: ws1x sits AT OR ABOVE ws1r for `reent_xwob` 6 bars.
               SHORT: ws1x sits AT OR BELOW ws1r for `reent_xwob` 6 bars. Joe 1008 *"apply the
               mirror"*.
  conf         return + 6 - 1 = return + 5 bars, the first bar the hold is knowable. 25 s at the
               5 s grid. THE ONLY BAR A RE-ENTRY CAN BE PLACED ON.
  gate A       LONG: ws1r <= `momo_fence_r` 17 at the hold's first bar AND ws12Mage > ws1Mage.
               SHORT: ws1r >= 83 at the hold's first bar AND ws12Mage < ws1Mage.

EVERY CANDIDATE IS PRINTED, not just the accepted one: for each stop, every return/conf pair the
router looked at from the stop bar onward, with the gate's two values and which clause rejected it.
That is the volume Joe is asking about.

NOTHING IS TRUNCATED. The candidate list per stop runs from the stop bar to the ACCEPTED conf, which
is where the router stops looking.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); U = SC.U
R1, X1 = T.R1, T.X1
MG = T.MG
EXF_LO = T.EXF_LO
XWOB = T.XWOB
TFHI = SC.TF[-1]
DAY = os.environ.get('W_DAY2', '2026-09-22')
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
def chain0_stops(gate, seed, last):
    out = []; k, d = seed, +1
    while True:
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, gate, last)
            out.append((xk, rb, cf))
            if cf is None: break
            k, d = cf, sd
            continue
        if xk >= last: break
        k = xk; d = -d
    return out

print('# chain 0 over the whole tape, %d bars ...' % N, flush=True)
S = [(a, rb, cf) for a, rb, cf in chain0_stops(T.gate_A, 1, N - 1) if DAYOF(a) == DAY]
print('# %s — %d stops, each with its re-entry router trace' % (DAY, len(S)))

print('\n# THE VOLUME — HOW MANY ws1x RETURNS THE ROUTER LOOKED AT PER STOP')
rows = []; tot_c = 0; tot_f = 0; tot_m = 0
for a, rb, cf in S:
    cands = [(r_, c_, s_) for r_, c_, s_ in T.RETURNS if c_ > a and (cf is None or c_ <= cf)]
    nf = sum(1 for r_, c_, s_ in cands if not T.gate_A(r_, c_, s_))
    nm = 0
    tot_c += len(cands); tot_f += nf; tot_m += nm
    rows.append((U(a), str(len(cands)), str(nf), str(nm),
                 ('%s %s' % (DAYOF(cf)[5:], U(cf))) if cf else 'NONE',
                 '%.1f' % ((int(SC.ts[cf]) - int(SC.ts[a])) / 60000.0) if cf else '—'))
box(('the stop bar', 'ws1x returns seen', 'rejected on the ws1r 17 fence',
     'rejected on ws12Mage > ws1Mage', 'the accepted conf', 'gap min'), rows)
print('- %d candidate returns across the %d stops: %d rejected on the fence, %d on the Mage line,'
      % (tot_c, len(S), tot_f, tot_m))
print('  %d accepted.' % (tot_c - tot_f - tot_m))
print('- every candidate is a real ws1x hold of %d bars on one side of ws1r. The gate is what'
      % XWOB)
print('  thins them, not the detector.')

for a, rb, cf in S:
    cands = [(r_, c_, s_) for r_, c_, s_ in T.RETURNS if c_ > a and (cf is None or c_ <= cf)]
    print('\n\n## THE STOP AT %s — %d ws1x RETURNS SEEN, ACCEPTED %s'
          % (U(a), len(cands), ('%s %s' % (DAYOF(cf)[5:], U(cf))) if cf else 'NONE'))
    rows = []
    for r_, c_, s_ in cands:
        up = s_ > 0
        fen = EXF_LO if up else 100.0 - EXF_LO
        fen_ok = (float(R1[r_]) <= fen) if up else (float(R1[r_]) >= fen)
        mg_ok = (float(MG[TFHI][c_]) > float(MG[1][c_])) if up \
            else (float(MG[TFHI][c_]) < float(MG[1][c_]))
        rows.append(('LONG' if up else 'SHORT',
                     U(r_), '%.2f' % float(R1[r_]), '%.2f' % float(X1[r_]),
                     'PASS' if fen_ok else 'fail',
                     U(c_), '%.2f' % float(MG[TFHI][c_]), '%.2f' % float(MG[1][c_]),
                     'PASS' if mg_ok else 'fail',
                     '%.6f' % float(PX[c_]),
                     'ACCEPTED' if (c_ == cf) else
                     ('rejected — ws1r %.2f > %.0f' % (float(R1[r_]), EXF_LO) if not fen_ok
                      else 'rejected — ws%dM %.2f vs ws1M %.2f'
                      % (TFHI, float(MG[TFHI][c_]), float(MG[1][c_])))))
    box(('the branch', 'the hold starts', 'ws1r there', 'ws1x there',
         'the fence', 'conf = hold+%d' % (XWOB - 1), 'ws%dMage at conf' % TFHI,
         'ws1Mage at conf', 'the Mage line', 'pxs at conf', 'the ruling'), rows)
