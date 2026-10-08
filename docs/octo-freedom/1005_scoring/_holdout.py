"""THE HOLD-OUT TEST — is the +156 spread across the tape, or fitted to it? 1008.

Joe gave me the con for 9 hours. This is the first thing I owe him, because every knob in SS25 was
fitted to the same 95 days that scored it, and I said so.

THREE SPLITS, because one split is a choice and three is a measurement:
  halves      days 1-47 (FIT) against days 48-95 (HOLD). The honest forward test.
  interleave  odd-numbered days against even-numbered. Immune to a regime that sits in one half.
  thirds      the first, middle and last 31-32 days, each scored on its own.

TWO CONFIGS, scored on every block:
  banked    mae_stop_pct 1.1 and the rest as seeded
  best      the SS25 staged winner: mae_stop_pct 2.5, reent_xwob 18, ceil_trig_tf 8,
            momo_fence_r 20.0, rrev_wob 1, stall_n 4, div_lines ws1r,ws2r,ws3r

THE CHAIN IS NOT RESTARTED PER BLOCK. It runs once over the whole tape and each leg is attributed to
the block its OPEN bar falls in - Joe's *"day is the block unit"*. Restarting per block would seed a
different chain in each one and the two would not be comparable.

NET AFTER DRAG at 0.11 per leg. Slippage unset.
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
_ST = {}
for t in C.ALL_TF:
    with momo_config(C.BANK[t]):
        with momo_window(int(C.BANK[t]['k_window']) * t):
            _ST[t] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))

def rebuild_returns(w):
    def holds(m):
        run = (_idx + 1) - np.maximum.accumulate(np.where(m, 0, _idx + 1))
        h = run >= w; cf = h & ~np.r_[False, h[:-1]]
        return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
    T.XWOB = w
    T.RETURNS = sorted([(a, b, +1) for a, b in holds((X1 >= R1) & _fin)]
                       + [(a, b, -1) for a, b in holds((X1 <= R1) & _fin)], key=lambda z: z[1])

def rebuild_stall(n):
    C.ST = {(t, dd): stall_mask(C.RL[t], dd, int(n), *_ST[t])
            for t in C.ALL_TF for dd in (-1, +1)}

def setcfg(c):
    C.MAE_STOP = float(c['mae_stop_pct']); C.LIN_HOP = int(c['lin_hop'])
    C.CEIL_HI = int(c['ceil_hi']); C.TRIG_TF = int(c['ceil_trig_tf'])
    C.GATE_BARS = int(c['oob_gate_bars']); C.DIP_DWELL = int(c['dip_dwell_bars'])
    C.DIP_FENCE = float(c['dip_fence']); C.DIP_HI = C.DIP_FENCE
    C.DIP_LO = 100.0 - C.DIP_FENCE
    C.EXF_LO = float(c['momo_fence_r']); C.EXF_HI = 100.0 - C.EXF_LO
    T.EXF_LO = C.EXF_LO; T.EXF_HI = C.EXF_HI
    C.G_LO = float(c['oob_gate_fence']); C.G_HI = 100.0 - C.G_LO
    rebuild_returns(int(c['reent_xwob'])); rebuild_stall(int(c['stall_n']))
    C.DIV_TFS = list(c['div_lines']); C.RREV = int(c['rrev_wob'])
    C.REV = {t: _mage_rev(C.R[t], C.RREV) for t in C.DIV_TFS}

BANKED = dict(mae_stop_pct=1.1, reent_xwob=6, lin_hop=2, stall_n=6, momo_fence_r=17.0,
              dip_fence=53.0, dip_dwell_bars=6, oob_gate_bars=72, ceil_hi=23, ceil_trig_tf=12,
              rrev_wob=2, div_lines=(1, 2), oob_gate_fence=15.0)
BEST = dict(BANKED, mae_stop_pct=2.5, reent_xwob=18, ceil_trig_tf=8, momo_fence_r=20.0,
            rrev_wob=1, stall_n=4, div_lines=(1, 2, 3))

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
                         real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn,
                         day=DAYOF(k)))
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, T.gate_A, LAST)
            if cf is None: break
            k, d = cf, sd; continue
        if xk >= LAST: break
        k = xk; d = -d
    return legs

def score(legs, days):
    sub = [r for r in legs if r['day'] in days]
    mae = mfe = real = 0.0
    for r in sub:
        a_, f_ = (C.MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
        mae += a_; mfe += f_; real += r['real']
    n = len(sub); st = sum(1 for r in sub if r['why'] == 'mae breach'); drag = n * FEE
    pd = collections.defaultdict(float)
    for r in sub: pd[r['day']] += r['real']
    return dict(n=n, st=st, real=real, drag=drag, net=real - drag, per=dict(pd),
                npl=((real - drag) / n) if n else 0.0,
                sr=(100.0 * st / n) if n else 0.0, mm=(mfe / mae) if mae else float('inf'))

print('# scoring both configs over the whole tape, then splitting by the leg\'s OPEN day',
      flush=True)
OUT = {}
for lbl, cfg in (('banked', BANKED), ('best', BEST)):
    setcfg(cfg); OUT[lbl] = run()
    print('#   %s -> %d legs' % (lbl, len(OUT[lbl])), flush=True)
    OUT[lbl + '_stop'] = cfg['mae_stop_pct']
DAYS = sorted({r['day'] for r in OUT['banked']} | {r['day'] for r in OUT['best']})
print('# %d days, %s to %s' % (len(DAYS), DAYS[0], DAYS[-1]), flush=True)

BLOCKS = [('ALL 95 DAYS', DAYS),
          ('HALVES — fit, days 1-%d' % (len(DAYS) // 2), DAYS[:len(DAYS) // 2]),
          ('HALVES — hold, days %d-%d' % (len(DAYS) // 2 + 1, len(DAYS)), DAYS[len(DAYS) // 2:]),
          ('INTERLEAVE — fit, odd-numbered days', DAYS[0::2]),
          ('INTERLEAVE — hold, even-numbered days', DAYS[1::2]),
          ('THIRDS — first', DAYS[:len(DAYS) // 3]),
          ('THIRDS — middle', DAYS[len(DAYS) // 3:2 * len(DAYS) // 3]),
          ('THIRDS — last', DAYS[2 * len(DAYS) // 3:])]
rows = []
for name, dd in BLOCKS:
    for lbl in ('banked', 'best'):
        C.MAE_STOP = OUT[lbl + '_stop']
        s = score(OUT[lbl], set(dd))
        rows.append((name, lbl, str(len(dd)), str(s['n']), str(s['st']), '%.1f%%' % s['sr'],
                     '%.2f' % s['mm'], '%+.4f' % s['real'], '-%.4f' % s['drag'],
                     '%+.4f' % s['net'], '%+.6f' % s['npl']))
print('\n# EVERY BLOCK, BOTH CONFIGS')
box(('the block', 'config', 'days', 'legs', 'stops', 'stop rate', 'MFE/MAE', 'gross', 'drag',
     'NET', 'net per leg'), rows)

print('\n# THE DELTA, BLOCK BY BLOCK — does `best` beat `banked` everywhere?')
rows = []
for name, dd in BLOCKS:
    C.MAE_STOP = OUT['banked_stop']; a = score(OUT['banked'], set(dd))
    C.MAE_STOP = OUT['best_stop']; b = score(OUT['best'], set(dd))
    w = sum(1 for d_ in b['per'] if d_ in a['per'] and b['per'][d_] > a['per'][d_])
    l = sum(1 for d_ in b['per'] if d_ in a['per'] and b['per'][d_] < a['per'][d_])
    rows.append((name, str(len(dd)), '%+.4f' % a['net'], '%+.4f' % b['net'],
                 '%+.4f' % (b['net'] - a['net']),
                 '%+.6f' % (b['npl'] - a['npl']), '%d / %d' % (w, l),
                 'best wins' if b['net'] > a['net'] else 'BANKED WINS'))
box(('the block', 'days', 'banked NET', 'best NET', 'the delta', 'delta per leg',
     'days best won / lost', 'verdict'), rows)
print('\n# HOLD-OUT COMPLETE', flush=True)
