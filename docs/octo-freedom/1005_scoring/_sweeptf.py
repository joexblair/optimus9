"""ceil_trig_tf SWEPT ACROSS ws8..ws20, INCLUDING ws13 AND ws14. 1008.

Joe 1008: *"ceil_trig_tf: sweep 13 and 14 as well"*.

HELD AT THE STAGE 3 WINNER, and run at BOTH live values of the new `oob_gate_fence`:
  mae_stop_pct 2.5, reent_xwob 18, lin_hop 2, dip_dwell_bars 6, dip_fence 53.0,
  momo_fence_r 20.0, rrev_wob 1, stall_n 4, div_lines ws1r,ws2r,ws3r, ceil_hi 23,
  oob_gate_bars 72
  oob_gate_fence 15.0 (banked) and 10.0 (its own sweep's peak)

ceil_trig_tf drives BOTH ws{TF}r tests in the >ws12 mech - the 72-bar handover gate, the branch-1
window, and the ceiling trigger that extends ws12 -> ws23. The base ceiling stays ws12 and the
extended one stays ws23; only the trigger LINE moves.

ws13 and ws14 are available: `_chain10` builds r to CEIL_HI + 3 = ws26 and x over ws1..ws23.
"""
import os, sys, datetime, collections
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
        legs.append(dict(open=k, exit=xk, d=d, why=why, hand=hand,
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
    return dict(n=n, st=st, mae=mae, mfe=mfe, real=real, drag=drag, net=real - drag, per=dict(per),
                hand=sum(1 for r in legs if r['hand']),
                div=sum(1 for r in legs if r['why'].startswith('>ws12')),
                npl=((real - drag) / n) if n else 0.0,
                sr=(100.0 * st / n) if n else 0.0, mm=(mfe / mae) if mae else float('inf'))

# ---- the stage 3 winner
C.MAE_STOP = 2.5; C.DIP_DWELL = 6; C.LIN_HOP = 2
C.DIP_FENCE = 53.0; C.DIP_HI = 53.0; C.DIP_LO = 47.0
C.EXF_LO = 20.0; C.EXF_HI = 80.0; T.EXF_LO = 20.0; T.EXF_HI = 80.0
C.CEIL_HI = 23; C.GATE_BARS = 72
rebuild_returns(18)
_STEPS = {}
for t in C.ALL_TF:
    with momo_config(C.BANK[t]):
        with momo_window(int(C.BANK[t]['k_window']) * t):
            _STEPS[t] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))
st = {}
for t in C.ALL_TF:
    s_, n_ = _STEPS[t]
    for dd in (-1, +1):
        st[(t, dd)] = stall_mask(C.RL[t], dd, 4, s_, n_)
C.ST = st
C.DIV_TFS = [1, 2, 3]; C.RREV = 1
C.REV = {t: _mage_rev(C.R[t], 1) for t in C.DIV_TFS}
print('# held at the stage 3 winner: mae_stop 2.5, reent_xwob 18, momo_fence_r 20, rrev_wob 1,',
      flush=True)
print('# stall_n 4, div_lines ws1r,ws2r,ws3r, lin_hop 2, dip 47-53 dwell 6, ceil_hi 23, gate 72',
      flush=True)

TFS = [8, 10, 11, 12, 13, 14, 15, 16, 18, 20]
for fence in (15.0, 10.0):
    C.G_LO = fence; C.G_HI = 100.0 - fence
    rows = []; ref = None
    for tf in TFS:
        C.TRIG_TF = tf
        t = tally(run())
        if tf == 12: ref = t
        rows.append((tf, t))
        print('#   fence %.0f  ws%dr -> net %+.4f (%d legs, %d handovers)'
              % (fence, tf, t['net'], t['n'], t['hand']), flush=True)
    print('\n# CEIL_TRIG_TF AT oob_gate_fence %.0f' % fence)
    box(('the trigger line', 'legs', 'stops', 'stop rate', 'handovers', '>ws12 exits', 'MFE/MAE',
         'gross', 'drag', 'NET', 'net per leg', 'vs ws12', 'days won / lost vs ws12'),
        [('ws%dr' % tf + ('   <- BANKED' if tf == 12 else ''),
          str(t['n']), str(t['st']), '%.1f%%' % t['sr'], str(t['hand']), str(t['div']),
          '%.2f' % t['mm'], '%+.4f' % t['real'], '-%.4f' % t['drag'], '%+.4f' % t['net'],
          '%+.6f' % t['npl'], '%+.4f' % (t['net'] - ref['net']),
          '%d / %d' % (sum(1 for d_ in t['per']
                           if d_ in ref['per'] and t['per'][d_] > ref['per'][d_]),
                       sum(1 for d_ in t['per']
                           if d_ in ref['per'] and t['per'][d_] < ref['per'][d_])))
         for tf, t in rows])
    sys.stdout.flush()
print('\n# COMPLETE', flush=True)
