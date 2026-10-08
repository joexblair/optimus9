"""THE GLOBAL oob FENCE SWEPT — oob_hi / oob_lo. 1008.

`oob_hi` 85 / `oob_lo` 15 in `lazy_g_config` is the fence Joe calls oob, and my own memory says it
ALWAYS means 15/85. It was never swept, and chain 0 reads it in three places:

  the arm        ws2Mage >= oob_hi for a LONG leg, <= oob_lo for a SHORT
  the KICKSTART  the rider is the highest TF whose r is past the fence
  the baton      a candidate TF must be past the fence

It does NOT drive the >ws12 mech any more - that has `oob_gate_fence` since 1008 - nor the
ex-fence, which is `momo_fence_r`.

SWEPT SYMMETRICALLY, lo = 100 - hi, because that is what the fence is. Held at the §25 staged
winner. NET AFTER DRAG at 0.11 per leg; slippage unset.
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
_ST = {}
for t in C.ALL_TF:
    with momo_config(C.BANK[t]):
        with momo_window(int(C.BANK[t]['k_window']) * t):
            _ST[t] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))
_idx = np.arange(N); _fin = np.isfinite(T.X1) & np.isfinite(T.R1)

WIN = dict(mae_stop_pct=2.5, reent_xwob=18, lin_hop=2, stall_n=4, momo_fence_r=20.0,
           dip_fence=53.0, dip_dwell_bars=6, oob_gate_bars=72, ceil_hi=23, ceil_trig_tf=8,
           rrev_wob=1, div_lines=(1, 2, 3), oob_gate_fence=15.0)
C.MAE_STOP = WIN['mae_stop_pct']; C.LIN_HOP = WIN['lin_hop']
C.CEIL_HI = WIN['ceil_hi']; C.TRIG_TF = WIN['ceil_trig_tf']
C.GATE_BARS = WIN['oob_gate_bars']; C.DIP_DWELL = WIN['dip_dwell_bars']
C.DIP_FENCE = WIN['dip_fence']; C.DIP_HI = C.DIP_FENCE; C.DIP_LO = 100.0 - C.DIP_FENCE
C.EXF_LO = WIN['momo_fence_r']; C.EXF_HI = 100.0 - C.EXF_LO
T.EXF_LO = C.EXF_LO; T.EXF_HI = C.EXF_HI
C.G_LO = WIN['oob_gate_fence']; C.G_HI = 100.0 - C.G_LO
C.DIV_TFS = list(WIN['div_lines']); C.RREV = WIN['rrev_wob']
C.REV = {t: _mage_rev(C.R[t], C.RREV) for t in C.DIV_TFS}
C.ST = {(t, dd): stall_mask(C.RL[t], dd, int(WIN['stall_n']), *_ST[t])
        for t in C.ALL_TF for dd in (-1, +1)}
w = int(WIN['reent_xwob'])
def holds(m):
    run = (_idx + 1) - np.maximum.accumulate(np.where(m, 0, _idx + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = w
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & _fin)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & _fin)], key=lambda z: z[1])

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
                         real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, day=DAYOF(k)))
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
        mae += a_; mfe += f_; real += r['real']; per[r['day']] += r['real']
    n = len(legs); st = sum(1 for r in legs if r['why'] == 'mae breach'); drag = n * FEE
    days = sorted(per)
    return dict(n=n, st=st, real=real, drag=drag, net=real - drag, per=dict(per),
                npl=((real - drag) / n) if n else 0.0,
                sr=(100.0 * st / n) if n else 0.0, mm=(mfe / mae) if mae else float('inf'),
                t1=sum(per[x] for x in days[:len(days)//3]),
                t2=sum(per[x] for x in days[len(days)//3:2*len(days)//3]),
                t3=sum(per[x] for x in days[2*len(days)//3:]))

print('# the global oob fence, held at the §25 staged winner', flush=True)
rows = []; ref = None
for hi in (75.0, 78.0, 80.0, 82.0, 85.0, 88.0, 90.0, 92.0, 95.0):
    SC.HI = hi; SC.LO = 100.0 - hi
    t = tally(run())
    if hi == 85.0: ref = t
    rows.append((hi, t))
    print('#   oob %.0f/%.0f -> net %+.4f (%d legs, %d stops)'
          % (100.0 - hi, hi, t['net'], t['n'], t['st']), flush=True)
print('\n# OOB_HI / OOB_LO — BANKED 85 / 15')
box(('the fence', 'legs', 'stops', 'stop rate', 'MFE/MAE', 'gross', 'drag', 'NET', 'net per leg',
     'vs 85/15', 'third 1', 'third 2', 'third 3', 'days won / lost vs 85/15'),
    [('%.0f / %.0f' % (100.0 - hi, hi) + ('   <- BANKED' if hi == 85.0 else ''),
      str(t['n']), str(t['st']), '%.1f%%' % t['sr'], '%.2f' % t['mm'],
      '%+.4f' % t['real'], '-%.4f' % t['drag'], '%+.4f' % t['net'], '%+.6f' % t['npl'],
      '%+.4f' % (t['net'] - ref['net']), '%+.2f' % t['t1'], '%+.2f' % t['t2'], '%+.2f' % t['t3'],
      '%d / %d' % (sum(1 for d_ in t['per'] if d_ in ref['per'] and t['per'][d_] > ref['per'][d_]),
                   sum(1 for d_ in t['per'] if d_ in ref['per'] and t['per'][d_] < ref['per'][d_])))
     for hi, t in rows])
print('\n# COMPLETE', flush=True)
