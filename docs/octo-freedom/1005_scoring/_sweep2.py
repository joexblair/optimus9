"""THE COMBINED SWEEP, 95 days, chain 0, ranked on NET AFTER DRAG. 1008.

Joe 1008: *"reducing legs is important too - the bybit fess and slippage need to be contained if we
can"* / *"agreed - combined sweep"*.

WHY COMBINED: the one-at-a-time sweep cannot be added up. `mae_stop_pct` 2.5 is +103.30 of net on
its own and `dip_dwell_bars` 12 is +57.29, but they move the SAME legs, so the pair is not +160.59.

THE DESIGN, in two stages because a full grid over 13 knobs is 2304 runs:

  STAGE 1   a FULL GRID on the four knobs that moved the net most, 3 x 3 x 2 x 2 = 36 runs:
              mae_stop_pct     1.1 / 1.8 / 2.5
              dip_dwell_bars   6 / 12 / 24
              reent_xwob       6 / 18
              lin_hop          1 / 2
  STAGE 2   from stage 1's best NET, every remaining knob one at a time, holding stage 1's winner:
              stall_n 4, rrev_wob 1 / 8, ceil_hi 12, momo_fence_r 10 / 14,
              dip_fence 50.5 / 52, oob_gate_bars 240, ceil_trig_tf 8, div_lines ws2r
            `dip_mid` is excluded: all five of its values gave IDENTICAL results, so the band has
            replaced it and it is read by nothing that changes an outcome.

THE SCORE IS NET AFTER DRAG.
  fee_per_leg 0.11 %, Joe 1007 *"0.11 is bybit's fees"*, a round trip.
  drag        legs * 0.11, its own column and its own total.
  SLIPPAGE IS NOT IN IT and has no measured value yet.
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
N = len(SC.ts)
FEE = 0.11
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
SEED, LAST = 1, N - 1
R1, X1 = T.R1, T.X1
_fin = np.isfinite(X1) & np.isfinite(R1)
_idx = np.arange(N)

def rebuild_returns(xwob):
    def holds(mask):
        run = (_idx + 1) - np.maximum.accumulate(np.where(mask, 0, _idx + 1))
        held = run >= xwob
        conf = held & ~np.r_[False, held[:-1]]
        return [(int(c) - (xwob - 1), int(c)) for c in np.flatnonzero(conf)
                if int(c) - (xwob - 1) >= 1]
    L = [(rb, cf, +1) for rb, cf in holds((X1 >= R1) & _fin)]
    S = [(rb, cf, -1) for rb, cf in holds((X1 <= R1) & _fin)]
    T.XWOB = xwob
    T.RETURNS = sorted(L + S, key=lambda z: z[1])

_STEPS = {}
for t in C.ALL_TF:
    with momo_config(C.BANK[t]):
        with momo_window(int(C.BANK[t]['k_window']) * t):
            _STEPS[t] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))

def rebuild_stall(stall_n):
    st = {}
    for t in C.ALL_TF:
        s_, n_ = _STEPS[t]
        for dd in (-1, +1):
            st[(t, dd)] = stall_mask(C.RL[t], dd, int(stall_n), s_, n_)
    C.ST = st

def rebuild_rev(tfs, wob):
    C.DIV_TFS = list(tfs); C.RREV = int(wob)
    C.REV = {t: _mage_rev(C.R[t], int(wob)) for t in C.DIV_TFS}

BASE = dict(mae_stop_pct=1.1, reent_xwob=6, lin_hop=2, stall_n=6, momo_fence_r=17.0,
            dip_fence=53.0, dip_dwell_bars=6, oob_gate_bars=72, ceil_hi=23, ceil_trig_tf=12,
            rrev_wob=2, div_lines=(1, 2))
_NOW = dict(BASE)

def setcfg(cfg):
    """apply a full config dict, rebuilding only what changed."""
    global _NOW
    C.MAE_STOP = float(cfg['mae_stop_pct']); C.LIN_HOP = int(cfg['lin_hop'])
    C.CEIL_HI = int(cfg['ceil_hi']); C.TRIG_TF = int(cfg['ceil_trig_tf'])
    C.GATE_BARS = int(cfg['oob_gate_bars']); C.DIP_DWELL = int(cfg['dip_dwell_bars'])
    C.DIP_FENCE = float(cfg['dip_fence']); C.DIP_HI = float(cfg['dip_fence'])
    C.DIP_LO = 100.0 - float(cfg['dip_fence'])
    C.EXF_LO = float(cfg['momo_fence_r']); C.EXF_HI = 100.0 - float(cfg['momo_fence_r'])
    T.EXF_LO = C.EXF_LO; T.EXF_HI = C.EXF_HI
    if int(cfg['reent_xwob']) != T.XWOB: rebuild_returns(int(cfg['reent_xwob']))
    if int(cfg['stall_n']) != _NOW['stall_n']: rebuild_stall(int(cfg['stall_n']))
    if tuple(cfg['div_lines']) != tuple(C.DIV_TFS) or int(cfg['rrev_wob']) != C.RREV:
        rebuild_rev(cfg['div_lines'], cfg['rrev_wob'])
    _NOW = dict(cfg)

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
    mae = mfe = real = 0.0
    per = collections.defaultdict(float)
    for r in legs:
        a_, f_ = (C.MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
        mae += a_; mfe += f_; real += r['real']; per[DAYOF(r['open'])] += r['real']
    n = len(legs); st = sum(1 for r in legs if r['why'] == 'mae breach')
    drag = n * FEE
    return dict(n=n, pos=sum(1 for r in legs if r['real'] > 0), st=st, mae=mae, mfe=mfe,
                real=real, drag=drag, net=real - drag, per=dict(per),
                rpl=(real / n) if n else 0.0, npl=((real - drag) / n) if n else 0.0,
                sr=(100.0 * st / n) if n else 0.0, mm=(mfe / mae) if mae else float('inf'))

def daycmp(a, b):
    w = sum(1 for dd in a['per'] if dd in b['per'] and a['per'][dd] > b['per'][dd])
    l = sum(1 for dd in a['per'] if dd in b['per'] and a['per'][dd] < b['per'][dd])
    return w, l

print('# fee %.2f%% per leg, slippage UNSET. Score = NET AFTER DRAG.' % FEE, flush=True)
setcfg(BASE); B = tally(run())
print('# banked: %d legs, %d stops (%.1f%%), MFE/MAE %.2f, gross %+.4f, drag -%.4f, NET %+.4f'
      % (B['n'], B['st'], B['sr'], B['mm'], B['real'], B['drag'], B['net']), flush=True)

G1 = dict(mae_stop_pct=[1.1, 1.8, 2.5], dip_dwell_bars=[6, 12, 24],
          reent_xwob=[6, 18], lin_hop=[1, 2])
keys = list(G1)
print('\n# STAGE 1 — THE FULL GRID ON FOUR KNOBS, %d runs'
      % np.prod([len(G1[k]) for k in keys]), flush=True)
res = []
for i, combo in enumerate(itertools.product(*[G1[k] for k in keys])):
    cfg = dict(BASE); cfg.update(dict(zip(keys, combo)))
    setcfg(cfg); t = tally(run()); w, l = daycmp(t, B)
    res.append((combo, t, w, l))
    print('#   %2d/36  %s -> net %+.4f (%d legs)'
          % (i + 1, dict(zip(keys, combo)), t['net'], t['n']), flush=True)
res.sort(key=lambda z: -z[1]['net'])
print('\n# STAGE 1 RESULT, RANKED BY NET')
box(('mae_stop_pct', 'dip_dwell_bars', 'reent_xwob', 'lin_hop', 'legs', 'positive', 'stops',
     'stop rate', 'MFE/MAE', 'gross', 'drag', 'NET', 'net per leg', 'days won / lost'),
    [(str(c[keys.index('mae_stop_pct')]), str(c[keys.index('dip_dwell_bars')]),
      str(c[keys.index('reent_xwob')]), str(c[keys.index('lin_hop')]),
      str(t['n']), str(t['pos']), str(t['st']), '%.1f%%' % t['sr'], '%.2f' % t['mm'],
      '%+.4f' % t['real'], '-%.4f' % t['drag'], '%+.4f' % t['net'], '%+.6f' % t['npl'],
      '%d / %d' % (w, l)) for c, t, w, l in res])

WIN = dict(BASE); WIN.update(dict(zip(keys, res[0][0])))
print('\n# STAGE 1 WINNER: %s   NET %+.4f'
      % ({k: WIN[k] for k in keys}, res[0][1]['net']), flush=True)
W = res[0][1]

STAGE3 = True
S2 = [('stall_n', [3, 4, 8]), ('rrev_wob', [1, 3, 8]), ('ceil_hi', [12, 16]),
      ('momo_fence_r', [10.0, 14.0, 20.0]), ('dip_fence', [50.5, 52.0, 55.0]),
      ('oob_gate_bars', [120, 240]), ('ceil_trig_tf', [8, 10, 15]),
      ('div_lines', [(1,), (2,), (1, 2, 3)])]
print('\n# STAGE 2 — EVERY REMAINING KNOB, HELD AGAINST THE STAGE 1 WINNER', flush=True)
rows = []
for knob, vals in S2:
    for v in vals:
        cfg = dict(WIN); cfg[knob] = v
        setcfg(cfg); t = tally(run()); w, l = daycmp(t, W)
        lbl = ('ws' + ',ws'.join(str(x) + 'r' for x in v)) if knob == 'div_lines' else str(v)
        rows.append((knob, lbl, str(t['n']), str(t['st']), '%.1f%%' % t['sr'], '%.2f' % t['mm'],
                     '%+.4f' % t['real'], '-%.4f' % t['drag'], '%+.4f' % t['net'],
                     '%+.4f' % (t['net'] - W['net']), '%d / %d' % (w, l)))
        print('#   %s=%s -> net %+.4f (%+.4f vs the winner)'
              % (knob, lbl, t['net'], t['net'] - W['net']), flush=True)
box(('knob', 'value', 'legs', 'stops', 'stop rate', 'MFE/MAE', 'gross', 'drag', 'NET',
     'vs the stage 1 winner', 'days won / lost'), rows)
print('\n# COMBINED SWEEP COMPLETE', flush=True)


# ---- STAGE 3: compose the stage-2 knobs that IMPROVED on the stage-1 winner. 1008.
#
# Stage 2 is also one-at-a-time, so its improvers do not add up either. This composes the five that
# beat the stage-1 winner, 2 x 2 x 2 x 2 x 2 = 32 runs.
G3 = dict(ceil_trig_tf=[12, 8], momo_fence_r=[17.0, 20.0], rrev_wob=[2, 1],
          stall_n=[6, 4], div_lines=[(1, 2), (1, 2, 3)])
k3 = list(G3)
print('\n# STAGE 3 — COMPOSING THE STAGE 2 IMPROVERS, %d runs'
      % int(np.prod([len(G3[k]) for k in k3])), flush=True)
r3 = []
for i, combo in enumerate(itertools.product(*[G3[k] for k in k3])):
    cfg = dict(WIN); cfg.update(dict(zip(k3, combo)))
    setcfg(cfg); t = tally(run()); w, l = daycmp(t, B)
    r3.append((combo, t, w, l))
    print('#   %2d/32  %s -> net %+.4f (%d legs)'
          % (i + 1, dict(zip(k3, combo)), t['net'], t['n']), flush=True)
r3.sort(key=lambda z: -z[1]['net'])
print('\n# STAGE 3 RESULT, RANKED BY NET — all held on the stage 1 winner')
box(tuple(k3) + ('legs', 'positive', 'stops', 'stop rate', 'MFE/MAE', 'gross', 'drag', 'NET',
                 'net per leg', 'days won / lost vs BANKED'),
    [tuple(('ws' + ',ws'.join(str(x) + 'r' for x in c[j]) if k3[j] == 'div_lines' else str(c[j]))
           for j in range(len(k3)))
     + (str(t['n']), str(t['pos']), str(t['st']), '%.1f%%' % t['sr'], '%.2f' % t['mm'],
        '%+.4f' % t['real'], '-%.4f' % t['drag'], '%+.4f' % t['net'], '%+.6f' % t['npl'],
        '%d / %d' % (w, l)) for c, t, w, l in r3])
best = dict(WIN); best.update(dict(zip(k3, r3[0][0])))
print('\n# THE BEST CONFIG FOUND')
box(('knob', 'banked', 'best'),
    [(k, str(BASE[k]), str(best[k])) for k in sorted(BASE)])
print('\n# banked NET %+.4f  ->  best NET %+.4f   (%+.4f)'
      % (B['net'], r3[0][1]['net'], r3[0][1]['net'] - B['net']), flush=True)
print('# STAGE 3 COMPLETE', flush=True)
