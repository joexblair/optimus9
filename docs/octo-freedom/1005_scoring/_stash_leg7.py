"""Joe's stash trick, tested on leg 7 (09-25 07:40:20 LONG) before rebuilding the chain on it.

JOE 1007: *"ws2Mage crossing oob is only the beginning of ws2's climb. if you think about the way a
Mage moves when it's oob, you'll see that pxs keeps pace with the Mage until the Mage crosses into
ib. my suggestion - stash the ws1x-cross until ws2Mage crosses into ib, then test for momentum again.
if there's no momentum, then let the stashed ws1x-cross fire"*.

MY READING, stated so it can be corrected:
  ib            ws2Mage crossing BACK INSIDE the oob fence - below 85 for a +dr leg.
  stash         the x-cross is recorded, not acted on.
  test again    at the ib bar, ask whether momentum is still there.
  no momentum   the stashed x-cross fires - exit at the ib bar.

WHAT "MOMENTUM" MEANS IS NOT RULED, so four candidates are printed at the ib bar rather than one
chosen: any line oob, the holder still oob, the holder not stalled, ws1 mom-true.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window, momo_g_why
from optimus9.analysis.jig import stall_mask
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%5.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D, DRS = '2026-09-25', +1
OPEN_TS, XC_TS, ARM_TS = '07:40:20', '07:51:05', '07:46:55'
LIN_TF = SC.TF
EXF_HI = 100.0 - float(SC.LG['momo_fence_r'])
R = {t: SC.Rl[t] for t in LIN_TF}
X1 = SC.LD(60, 'x'); M2 = SC.Mg[2]; PX = SC.PX
db = DatabaseManager(**get_db_config()); db.connect()
BANK = {t: momo_bank(db, t) for t in LIN_TF}; db.disconnect()
ST = {}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    ST[t] = stall_mask(SC.Rl[t], DRS, int(SC.LG['stall_n']), s_, n_)
def mt(t, k):
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            return momo_g_why(SC.Rl[t], DRS, int(k))[0] in ('momo', 'curl')
_P('producers ready')
band = lambda t, k: ('O' if float(R[t][k]) >= SC.HI else
                     ('x' if float(R[t][k]) >= EXF_HI else '.'))

k_open = SC.K('%s %s' % (D, OPEN_TS)); p0 = float(PX[k_open])
k_arm = SC.K('%s %s' % (D, ARM_TS)); k_xc = SC.K('%s %s' % (D, XC_TS))

print('\n## LEG 7 — LONG, open %s, x-cross fired %s (currently the exit)' % (OPEN_TS, XC_TS))
print('\n# ws2Mage FROM THE ARM TO THE ib CROSSING')
print('| ts | +min from open | ws2Mage | oob? | pxs | pct LONG |'); print('|---|---|---|---|---|---|')
ib = None
for k in range(k_arm, SC.TAPE_LAST + 1):
    v = float(M2[k])
    if v < SC.HI and float(M2[k - 1]) >= SC.HI: ib = k
    if k <= k_arm + 240 and (k - k_arm) % 12 == 0:
        print('| %s | %+.1f | %.2f | %s | %.6f | %+.4f |'
              % (SC.U(k), (int(SC.ts[k]) - int(SC.ts[k_open])) / 60000.0, v,
                 'Y' if v >= SC.HI else '-', float(PX[k]), (float(PX[k]) - p0) / p0 * 100.0))
    if ib is not None and k > ib: break

print('\n# THE KEY BARS')
print('| bar | ts | +min | ws2Mage | pxs | pct LONG |'); print('|---|---|---|---|---|---|')
for lbl, k in (('OPEN', k_open), ('exit-armed (ws2Mage over 85)', k_arm),
               ('x-cross fires — currently the EXIT', k_xc),
               ('ws2Mage crosses into ib', ib)):
    if k is None: print('| %s | — | | | | |' % lbl); continue
    print('| %s | %s | %+.1f | %.2f | %.6f | %+.4f |'
          % (lbl, SC.U(k), (int(SC.ts[k]) - int(SC.ts[k_open])) / 60000.0, float(M2[k]),
             float(PX[k]), (float(PX[k]) - p0) / p0 * 100.0))

if ib is not None:
    print('\n# AT THE ib BAR %s — IS THERE STILL MOMENTUM?' % SC.U(ib))
    oob_lines = [t for t in LIN_TF if float(R[t][ib]) >= SC.HI]
    print('| test | answer |'); print('|---|---|')
    print('| any line ws1..ws12 oob | %s |' % (', '.join('ws%d' % t for t in oob_lines) or '**NONE**'))
    print('| ws1 r | %.2f  %s |' % (float(R[1][ib]), band(1, ib)))
    print('| ws1 still oob | %s |' % ('Y' if float(R[1][ib]) >= SC.HI else '**no**'))
    print('| ws1 stalled | %s |' % ('Y' if ST[1][ib] else 'no'))
    print('| ws1 mom-true | %s |' % ('Y' if mt(1, ib) else '**no**'))
    print('\n# THE LADDER AT THE ib BAR')
    print('| TF | r | band |'); print('|---|---|---|')
    for t in LIN_TF:
        print('| ws%d | %.2f | %s |' % (t, float(R[t][ib]), band(t, ib)))
    print('\n# WHAT THE STASH IS WORTH ON THIS LEG')
    print('| exit rule | bar | pxs | realised |'); print('|---|---|---|---|')
    print('| x-cross fires immediately (today) | %s | %.6f | %+.4f |'
          % (SC.U(k_xc), float(PX[k_xc]), (float(PX[k_xc]) - p0) / p0 * 100.0))
    print('| **stashed until ws2Mage ib** | %s | %.6f | **%+.4f** |'
          % (SC.U(ib), float(PX[ib]), (float(PX[ib]) - p0) / p0 * 100.0))
    seg = PX[k_open:ib + 1]
    seg = seg[np.isfinite(seg) & (seg > 0)]
    print('| MFE over open -> ib | | %.6f | %+.4f |'
          % (float(seg.max()), (float(seg.max()) - p0) / p0 * 100.0))
