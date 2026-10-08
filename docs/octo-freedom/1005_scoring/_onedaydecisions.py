"""THE THREE DECISIONS THAT REST ON ONE DAY, RE-MEASURED OVER 95. 1008.

Each of these was chosen on a single episode and has been banked ever since:

  1  GATE A vs GATE B, the re-entry gate. §12 chose A on 09-25 + 09-26: 43 legs +13.3928 against
     B's 40 legs +9.2482. Two days.
  2  THE BATON PASS, `oob` vs `stalled`. §15 swap 2 measured -4.6905 for `stalled` on the 08:10
     chain. ONE day, and Joe's tag ruling put `oob` in.
  3  THE WALK'S EXIT, `x-cross` live vs stall-only (`W_NOX=1`). §15 swap 1 measured +0.6115 for
     stall-only on the 08:10 chain, and §14 measured the OPPOSITE on 15:41 by 1.2550. One leg each.

`W_PASS` and `W_NOX` are read at `_chain10` IMPORT time, so each arm is its own process with its own
env - there is no way to flip them in-process.

Held at the TWO SURVIVING knobs from §29: mae_stop_pct 2.5 and reent_xwob 18, everything else
banked. That is the config I would actually defend, so it is the one the decisions are tested on.

NET AFTER DRAG at 0.11 per leg; slippage unset.
"""
import os, sys, json, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.lr_v2 import _mage_rev
import _chain10 as C
import _chain_2day as T

GATE = os.environ.get('W_GATE', 'A')
SC, PX = C.SC, C.PX
N = len(SC.ts); FEE = 0.11
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
C.MAE_STOP = 2.5
_idx = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_idx + 1) - np.maximum.accumulate(np.where(m, 0, _idx + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])
gate = T.gate_A if GATE == 'A' else T.gate_B

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

legs = []; k, d = 1, +1; g = 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    legs.append(dict(day=DAYOF(k), why=why, open=k, exit=xk, dd=d,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, gate, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

per = collections.defaultdict(lambda: [0.0, 0, 0, 0.0, 0.0])
whys = collections.Counter()
for r in legs:
    a_, f_ = (C.MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['dd'])
    e = per[r['day']]
    e[0] += r['real']; e[1] += 1; e[2] += 1 if r['why'] == 'mae breach' else 0
    e[3] += a_; e[4] += f_
    whys[r['why']] += 1
print(json.dumps(dict(arm='gate=%s pass=%s nox=%s' % (GATE, C.PASS, int(C.NOX)),
                      gate=GATE, pas=C.PASS, nox=int(C.NOX), legs=len(legs),
                      whys=dict(whys),
                      per={k_: [round(v[0], 4), v[1], v[2], round(v[3], 4), round(v[4], 4)]
                           for k_, v in sorted(per.items())})), flush=True)
