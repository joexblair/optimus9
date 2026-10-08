"""THE >ws12 oob FENCE SWEPT, against the best config found so far. 1008.

Joe 1008: *"we should have a knob for >12 oob"*.

`oob_gate_fence` is now the >ws12 mech's own oob, replacing the global 15/85 it was borrowing for
the 72-bar gate, the branch-1 window and the ceiling trigger. 15.0 reproduces today exactly.

HELD AT THE BEST CONFIG FOUND SO FAR, which is the stage-1 winner plus stage 2's biggest improver:
  mae_stop_pct 2.5, dip_dwell_bars 6, reent_xwob 18, lin_hop 2, ceil_trig_tf 8  -> NET -9.5687

A LOWER fence is STRICTER - ws12r must go further out before the mech arms. A HIGHER fence arms it
sooner. 50 is the degenerate end where every bar counts as oob.
"""
import os, sys, datetime, collections, itertools
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_config
from optimus9.compute.momo_gated import momo_window
from optimus9.analysis.jig import stall_mask
from optimus9.analysis.lr_v2 import _mage_rev
import _chain10 as C
import _chain_2day as T

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); FEE = 0.11
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
SEED, LAST = 1, N - 1
R1, X1 = T.R1, T.X1
_fin = np.isfinite(X1) & np.isfinite(R1); _idx = np.arange(N)

def rebuild_returns(xwob):
    def holds(mask):
        run = (_idx + 1) - np.maximum.accumulate(np.where(mask, 0, _idx + 1))
        held = run >= xwob
        conf = held & ~np.r_[False, held[:-1]]
        return [(int(c) - (xwob - 1), int(c)) for c in np.flatnonzero(conf)
                if int(c) - (xwob - 1) >= 1]
    T.XWOB = xwob
    T.RETURNS = sorted([(rb, cf, +1) for rb, cf in holds((X1 >= R1) & _fin)]
                       + [(rb, cf, -1) for rb, cf in holds((X1 <= R1) & _fin)],
                       key=lambda z: z[1])

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

def run():
    legs = []; k, d = SEED, +1; guard = 0
    while True:
        guard += 1
        if guard > 20000: break
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        legs.append(dict(open=k, exit=xk, d=d, why=why,
                         real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn))
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, T.gate_A, LAST)
            if cf is None: break
            k, d = cf, sd; continue
        if xk >= LAST: break
        k = xk; d = -d
    return legs

def tally(legs):
    mae = mfe = real = 0.0; per = collections.defaultdict(float)
    for r in legs:
        a_, f_ = (C.MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
        mae += a_; mfe += f_; real += r['real']; per[DAYOF(r['open'])] += r['real']
    n = len(legs); st = sum(1 for r in legs if r['why'] == 'mae breach'); drag = n * FEE
    return dict(n=n, pos=sum(1 for r in legs if r['real'] > 0), st=st, mae=mae, mfe=mfe,
                real=real, drag=drag, net=real - drag, per=dict(per),
                npl=((real - drag) / n) if n else 0.0,
                sr=(100.0 * st / n) if n else 0.0, mm=(mfe / mae) if mae else float('inf'))

# ---- the best config found so far
C.MAE_STOP = 2.5; C.DIP_DWELL = 6; C.LIN_HOP = 2; C.TRIG_TF = 8
rebuild_returns(18)
print('# held at mae_stop_pct 2.5, dip_dwell_bars 6, reent_xwob 18, lin_hop 2, ceil_trig_tf 8',
      flush=True)
REF = None
rows = []
for v in [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0]:
    C.G_LO = float(v); C.G_HI = 100.0 - float(v)
    t = tally(run())
    if v == 15.0: REF = t
    rows.append((v, t))
    print('#   oob_gate_fence=%.0f -> net %+.4f (%d legs)' % (v, t['net'], t['n']), flush=True)
print('\n# OOB_GATE_FENCE — BANKED 15.0, held at the best config')
box(('value', 'the ws12r test', 'legs', 'positive', 'stops', 'stop rate', 'MFE/MAE', 'gross',
     'drag', 'NET', 'net per leg', 'vs fence 15', 'days won / lost vs fence 15'),
    [('%.0f' % v + ('   <- BANKED' if v == 15.0 else ''),
      'r <= %.0f or r >= %.0f' % (v, 100.0 - v),
      str(t['n']), str(t['pos']), str(t['st']), '%.1f%%' % t['sr'], '%.2f' % t['mm'],
      '%+.4f' % t['real'], '-%.4f' % t['drag'], '%+.4f' % t['net'], '%+.6f' % t['npl'],
      '%+.4f' % (t['net'] - REF['net']),
      '%d / %d' % (sum(1 for dd in t['per'] if dd in REF['per'] and t['per'][dd] > REF['per'][dd]),
                   sum(1 for dd in t['per'] if dd in REF['per'] and t['per'][dd] < REF['per'][dd])))
     for v, t in rows])
print('\n# COMPLETE', flush=True)
