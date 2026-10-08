"""THE OVERNIGHT RUN — edges, centroid, then the two reports Joe asked for. 1008.

Joe 1008: *"when you have a centroid, make very granular steps (eg 1, 0.05) around each knob to lock
it in. in the morning I'll want to see the day with the most stops, and the five day window which
holds the trades that need such a large stop loss and hopefully we'll be ready for a fresh sweep
tomorrow night"*.

FOUR PARTS, in order, each printed as it finishes:

  PART 1   THE EDGES. `mae_stop_pct` 2.5 and `reent_xwob` 18 were the TOP of their grids and both
           won, so the curve may still be rising past where it was measured. Extended first,
           because a centroid built on a grid edge is not a centroid.
  PART 2   THE CENTROID, granular. Every knob stepped finely around the best value found: 0.05 on
           `mae_stop_pct`, 1 on every integer and r-point knob.
  PART 3   THE DAY WITH THE MOST STOPS at the locked config, with every stop as a timestamped
           event table.
  PART 4   THE FIVE-DAY WINDOW HOLDING THE TRADES THAT NEED THE LARGE STOP. A leg "needs" it when
           its own MAE went past 1.1 - the old stop - and it still came home. Those are the legs a
           1.1 stop kills and a 2.5 stop keeps. The window is the 5 CONSECUTIVE days holding the
           most of their realised.

THE SCORE IS NET AFTER DRAG at 0.11 per leg. Slippage is still unset.
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
N = len(SC.ts); FEE = 0.11; OLD_STOP = 1.1
U = SC.U
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
SEED, LAST = 1, N - 1
R1, X1 = T.R1, T.X1
_fin = np.isfinite(X1) & np.isfinite(R1); _idx = np.arange(N)
_STEPS = {}
for t in C.ALL_TF:
    with momo_config(C.BANK[t]):
        with momo_window(int(C.BANK[t]['k_window']) * t):
            _STEPS[t] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))

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

def rebuild_stall(n):
    st = {}
    for t in C.ALL_TF:
        s_, n_ = _STEPS[t]
        for dd in (-1, +1):
            st[(t, dd)] = stall_mask(C.RL[t], dd, int(n), s_, n_)
    C.ST = st

BEST = dict(mae_stop_pct=2.5, reent_xwob=18, lin_hop=2, stall_n=4, momo_fence_r=20.0,
            dip_fence=53.0, dip_dwell_bars=6, oob_gate_bars=72, ceil_hi=23, ceil_trig_tf=8,
            rrev_wob=1, div_lines=(1, 2, 3), oob_gate_fence=15.0)
_NOW = {}

def setcfg(cfg):
    global _NOW
    C.MAE_STOP = float(cfg['mae_stop_pct']); C.LIN_HOP = int(cfg['lin_hop'])
    C.CEIL_HI = int(cfg['ceil_hi']); C.TRIG_TF = int(cfg['ceil_trig_tf'])
    C.GATE_BARS = int(cfg['oob_gate_bars']); C.DIP_DWELL = int(cfg['dip_dwell_bars'])
    C.DIP_FENCE = float(cfg['dip_fence']); C.DIP_HI = float(cfg['dip_fence'])
    C.DIP_LO = 100.0 - float(cfg['dip_fence'])
    C.EXF_LO = float(cfg['momo_fence_r']); C.EXF_HI = 100.0 - float(cfg['momo_fence_r'])
    T.EXF_LO = C.EXF_LO; T.EXF_HI = C.EXF_HI
    C.G_LO = float(cfg['oob_gate_fence']); C.G_HI = 100.0 - C.G_LO
    if _NOW.get('reent_xwob') != int(cfg['reent_xwob']): rebuild_returns(int(cfg['reent_xwob']))
    if _NOW.get('stall_n') != int(cfg['stall_n']): rebuild_stall(int(cfg['stall_n']))
    if (_NOW.get('div_lines') != tuple(cfg['div_lines'])
            or _NOW.get('rrev_wob') != int(cfg['rrev_wob'])):
        C.DIV_TFS = list(cfg['div_lines']); C.RREV = int(cfg['rrev_wob'])
        C.REV = {t: _mage_rev(C.R[t], C.RREV) for t in C.DIV_TFS}
    _NOW = {k: (tuple(v) if k == 'div_lines' else v) for k, v in cfg.items()}

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

def run(keep=False):
    legs = []; k, d = SEED, +1; guard = 0
    while True:
        guard += 1
        if guard > 20000: break
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        legs.append(dict(open=k, exit=xk, d=d, why=why, mae_meas=mae, hand=hand,
                         side='LONG' if d > 0 else 'SHORT',
                         real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn,
                         tr=(tr if keep else None)))
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
                npl=((real - drag) / n) if n else 0.0,
                sr=(100.0 * st / n) if n else 0.0, mm=(mfe / mae) if mae else float('inf'))

def line(knob, v, t, ref):
    lbl = ('ws' + ',ws'.join(str(x) + 'r' for x in v)) if knob == 'div_lines' else str(v)
    w = sum(1 for d_ in t['per'] if d_ in ref['per'] and t['per'][d_] > ref['per'][d_])
    l = sum(1 for d_ in t['per'] if d_ in ref['per'] and t['per'][d_] < ref['per'][d_])
    return (lbl + ('   <- BEST' if str(v) == str(BEST[knob]) else ''),
            str(t['n']), str(t['st']), '%.1f%%' % t['sr'], '%.2f' % t['mm'],
            '%+.4f' % t['real'], '-%.4f' % t['drag'], '%+.4f' % t['net'], '%+.6f' % t['npl'],
            '%+.4f' % (t['net'] - ref['net']), '%d / %d' % (w, l))
HDR = ('value', 'legs', 'stops', 'stop rate', 'MFE/MAE', 'gross', 'drag', 'NET', 'net per leg',
       'vs the reference', 'days won / lost')

setcfg(BEST); REF = tally(run())
print('# THE REFERENCE CONFIG — the best found by the staged sweep', flush=True)
box(('knob', 'value'), [(k, str(BEST[k])) for k in sorted(BEST)])
print('# reference: %d legs, %d stops (%.1f%%), MFE/MAE %.2f, gross %+.4f, drag -%.4f, NET %+.4f'
      % (REF['n'], REF['st'], REF['sr'], REF['mm'], REF['real'], REF['drag'], REF['net']),
      flush=True)

# ================= PART 1 — THE EDGES
print('\n\n# PART 1 — THE GRID EDGES EXTENDED', flush=True)
print('# mae_stop_pct 2.5 and reent_xwob 18 were both the TOP of their grid AND the winner, so the')
print('# curve may still be rising past where it was measured.', flush=True)
for knob, vals in (('mae_stop_pct', [2.5, 2.75, 3.0, 3.25, 3.5, 4.0, 5.0]),
                   ('reent_xwob', [18, 22, 26, 32, 40, 60])):
    rows = []
    for v in vals:
        cfg = dict(BEST); cfg[knob] = v
        setcfg(cfg); t = tally(run())
        rows.append(line(knob, v, t, REF))
        print('#   %s=%s -> net %+.4f (%d legs)' % (knob, v, t['net'], t['n']), flush=True)
    print('\n# %s — THE UPPER EDGE' % knob.upper())
    box(HDR, rows); sys.stdout.flush()

# ================= PART 2 — THE CENTROID, GRANULAR
print('\n\n# PART 2 — GRANULAR STEPS AROUND EACH KNOB', flush=True)
FINE = [('mae_stop_pct', [round(2.20 + 0.05 * i, 2) for i in range(17)]),
        ('oob_gate_fence', [11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0]),
        ('momo_fence_r', [17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0]),
        ('ceil_trig_tf', [5, 6, 7, 8, 9, 10]),
        ('dip_fence', [51.0, 52.0, 53.0, 54.0, 55.0]),
        ('dip_dwell_bars', [4, 5, 6, 7, 8]),
        ('stall_n', [3, 4, 5, 6]),
        ('rrev_wob', [1, 2]),
        ('lin_hop', [1, 2, 3]),
        ('oob_gate_bars', [48, 60, 72, 84, 96]),
        ('ceil_hi', [18, 20, 21, 22, 23]),
        ('div_lines', [(1,), (1, 2), (1, 2, 3), (1, 2, 3, 4)])]
WINNER = dict(BEST)
for knob, vals in FINE:
    rows = []; best = (None, None)
    for v in vals:
        cfg = dict(BEST); cfg[knob] = v
        setcfg(cfg); t = tally(run())
        rows.append(line(knob, v, t, REF))
        if best[1] is None or t['net'] > best[1]['net']: best = (v, t)
        print('#   %s=%s -> net %+.4f (%d legs)' % (knob, v, t['net'], t['n']), flush=True)
    WINNER[knob] = best[0]
    print('\n# %s — GRANULAR, BEST %s AT NET %+.4f' % (knob.upper(), best[0], best[1]['net']))
    box(HDR, rows); sys.stdout.flush()

print('\n\n# THE CENTROID — every knob at its own granular best')
box(('knob', 'the staged best', 'the granular best'),
    [(k, str(BEST[k]), str(WINNER[k])) for k in sorted(BEST)])
setcfg(WINNER); CEN = tally(run())
print('# the centroid composed: %d legs, %d stops (%.1f%%), MFE/MAE %.2f, gross %+.4f, '
      'drag -%.4f, NET %+.4f' % (CEN['n'], CEN['st'], CEN['sr'], CEN['mm'], CEN['real'],
                                 CEN['drag'], CEN['net']), flush=True)
print('# NOTE: each granular best was found ONE AT A TIME, so the composed centroid is NOT the')
print('# sum of them. Its net above is the only number that counts.', flush=True)
LOCK = WINNER if CEN['net'] > REF['net'] else BEST
setcfg(LOCK); L = tally(run(keep=True))
LEGS = run(keep=True)
print('\n# LOCKED FOR THE TWO REPORTS: %s' % {k: LOCK[k] for k in sorted(LOCK)}, flush=True)
print('# %d legs, %d stops (%.1f%%), NET %+.4f'
      % (L['n'], L['st'], L['sr'], L['net']), flush=True)

# ================= PART 3 — THE DAY WITH THE MOST STOPS
byday = collections.Counter(DAYOF(r['open']) for r in LEGS if r['why'] == 'mae breach')
legday = collections.Counter(DAYOF(r['open']) for r in LEGS)
worst = byday.most_common(1)[0][0]
print('\n\n# PART 3 — THE DAY WITH THE MOST STOPS: %s' % worst, flush=True)
box(('day', 'legs', 'stops', 'stop rate', 'realised'),
    [(d, str(legday[d]), str(byday[d]), '%.1f%%' % (100.0 * byday[d] / legday[d]),
      '%+.4f' % sum(r['real'] for r in LEGS if DAYOF(r['open']) == d))
     for d, _ in byday.most_common(8)])
dl = [r for r in LEGS if DAYOF(r['open']) == worst]
print('\n# %s — EVERY LEG' % worst)
box(('side', 'open', 'exit', 'hold min', 'why', 'handover', 'measured MAE', 'realised'),
    [(r['side'], U(r['open']),
      U(r['exit']) if DAYOF(r['exit']) == worst else '%s %s' % (DAYOF(r['exit'])[5:], U(r['exit'])),
      '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0), r['why'],
      U(r['hand']) if r['hand'] else '—', '%.4f' % r['mae_meas'], '%+.4f' % r['real'])
     for r in dl])
for r in [x for x in dl if x['why'] == 'mae breach']:
    p0 = float(PX[r['open']]); sgn = r['d']
    pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
    mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[r['open']])) / 60000.0)
    print('\n## %s %s   %s   pxs %.6f' % (DAYOF(r['open'])[5:], U(r['open']), r['side'], p0))
    box(('ts', '+min', 'event', 'pxs', 'pct'),
        [(U(r['open']), '+0.0', 'OPEN %s' % r['side'], '%.6f' % p0, '+0.0000')]
        + [(U(j), mn(j), lab, '%.6f' % float(PX[j]), pct(j)) for j, lab in (r['tr'] or [])]
        + [(U(r['exit']), mn(r['exit']), 'EXIT — mae breach', '%.6f' % float(PX[r['exit']]),
            pct(r['exit']))])
sys.stdout.flush()

# ================= PART 4 — THE FIVE-DAY WINDOW THAT NEEDS THE BIG STOP
need = [r for r in LEGS if r['why'] != 'mae breach' and r['mae_meas'] > OLD_STOP]
print('\n\n# PART 4 — THE LEGS THAT NEED THE LARGE STOP', flush=True)
print('# a leg NEEDS it when its own measured MAE went past the old %.2f and it still came home,'
      % OLD_STOP)
print('# so a %.2f stop would have killed it and the %.2f stop kept it.'
      % (OLD_STOP, C.MAE_STOP), flush=True)
box(('the measure', 'value'),
    [('legs that need the large stop', str(len(need))),
     ('their share of all legs', '%.1f%% of %d' % (100.0 * len(need) / len(LEGS), len(LEGS))),
     ('their summed realised', '%+.4f' % sum(r['real'] for r in need)),
     ('the whole chain\'s realised', '%+.4f' % L['real']),
     ('their share of the gross', '%.1f%%' % (100.0 * sum(r['real'] for r in need) / L['real'])),
     ('their largest measured MAE', '%.4f' % max(r['mae_meas'] for r in need)),
     ('their median measured MAE', '%.4f' % sorted(r['mae_meas'] for r in need)[len(need) // 2])])
pd = collections.defaultdict(float); pn = collections.Counter()
for r in need:
    pd[DAYOF(r['open'])] += r['real']; pn[DAYOF(r['open'])] += 1
days = sorted({DAYOF(r['open']) for r in LEGS})
wins = []
for i in range(len(days) - 4):
    w = days[i:i + 5]
    wins.append((sum(pd.get(d, 0.0) for d in w), sum(pn.get(d, 0) for d in w), w))
wins.sort(key=lambda z: -z[0])
print('\n# THE FIVE-DAY WINDOWS, RANKED BY THE REALISED THAT NEEDED THE LARGE STOP')
box(('the window', 'legs needing it', 'their realised', 'the window\'s whole realised',
     'their share'),
    [('%s to %s' % (w[0], w[-1]), str(n), '%+.4f' % v,
      '%+.4f' % sum(L['per'].get(d, 0.0) for d in w),
      '%.1f%%' % (100.0 * v / sum(L['per'].get(d, 0.0) for d in w))
      if sum(L['per'].get(d, 0.0) for d in w) else '—')
     for v, n, w in wins[:8]])
TOP = wins[0][2]
print('\n# %s TO %s — EVERY LEG THAT NEEDED THE LARGE STOP' % (TOP[0], TOP[-1]))
box(('day', 'side', 'open', 'exit', 'hold min', 'why', 'measured MAE', 'MFE', 'realised'),
    [(DAYOF(r['open']), r['side'], U(r['open']), U(r['exit']),
      '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0), r['why'],
      '%.4f' % r['mae_meas'], '%.4f' % mm(r['open'], r['exit'], r['d'])[1], '%+.4f' % r['real'])
     for r in need if DAYOF(r['open']) in TOP])
print('\n# OVERNIGHT RUN COMPLETE', flush=True)
