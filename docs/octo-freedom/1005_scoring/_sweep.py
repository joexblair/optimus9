"""THE 95-DAY KNOB SWEEP, chain 0, one knob at a time. 1008.

Joe 1008: *"sweep all of the knobs we have"* / *"you're good to sweep"*.

ONE AT A TIME. A full grid over 13 knobs is 5^13 and impossible; every run here moves ONE knob and
holds the rest at their banked value. The curves show each knob's own shape and any knee.

HOW A KNOB IS APPLIED: the live values are module globals in `_chain10` and `_chain_2day`, read at
CALL time by `run_leg` and `gate_A`. The sweep rebinds those globals and rebuilds whatever derives
from them - `stall_n` rebuilds every stall mask, `rrev_wob` and `div_lines` rebuild the reversal
arrays, `reent_xwob` rebuilds the router's hold list. MONKEY-PATCHING MODULE STATE IS UGLY and it is
contained to this script; the banked config is never written to.

RANKED ON realised per leg, because the leg COUNT changes between settings and a total would reward
a knob for simply trading more. MFE/MAE, the stop rate, the leg count, the minutes naked and the
per-day win/loss against the banked config sit beside it.

ceil_hi's grid stops at 23 because `_chain10` builds its r / x / stall arrays to CEIL_HI at import;
going above 23 needs those producers rebuilt and is not a knob move.
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
N = len(SC.ts)
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
SEED, LAST = 1, N - 1
R1, X1, MGv = T.R1, T.X1, T.MG
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


def rebuild_stall(stall_n):
    st = {}
    for t in C.ALL_TF:
        with momo_config(C.BANK[t]):
            with momo_window(int(C.BANK[t]['k_window']) * t):
                s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
        for dd in (-1, +1):
            st[(t, dd)] = stall_mask(C.RL[t], dd, int(stall_n), s_, n_)
    C.ST = st


def rebuild_rev(tfs, wob):
    C.DIV_TFS = list(tfs)
    C.RREV = int(wob)
    C.REV = {t: _mage_rev(C.R[t], int(wob)) for t in C.DIV_TFS}


BASE = dict(mae_stop_pct=C.MAE_STOP, reent_xwob=T.XWOB, lin_hop=C.LIN_HOP,
            stall_n=int(SC.LG['stall_n']), momo_fence_r=C.EXF_LO, dip_fence=C.DIP_FENCE,
            dip_dwell_bars=C.DIP_DWELL, dip_mid=C.DIP_MID, oob_gate_bars=C.GATE_BARS,
            ceil_hi=C.CEIL_HI, ceil_trig_tf=C.TRIG_TF, rrev_wob=C.RREV,
            div_lines=tuple(C.DIV_TFS))


def apply(knob, v):
    if knob == 'mae_stop_pct': C.MAE_STOP = float(v)
    elif knob == 'lin_hop': C.LIN_HOP = int(v)
    elif knob == 'ceil_hi': C.CEIL_HI = int(v)
    elif knob == 'ceil_trig_tf': C.TRIG_TF = int(v)
    elif knob == 'oob_gate_bars': C.GATE_BARS = int(v)
    elif knob == 'dip_mid': C.DIP_MID = float(v)
    elif knob == 'dip_dwell_bars': C.DIP_DWELL = int(v)
    elif knob == 'dip_fence':
        C.DIP_FENCE = float(v); C.DIP_HI = float(v); C.DIP_LO = 100.0 - float(v)
    elif knob == 'momo_fence_r':
        C.EXF_LO = float(v); C.EXF_HI = 100.0 - float(v)
        T.EXF_LO = float(v); T.EXF_HI = 100.0 - float(v)
    elif knob == 'reent_xwob': rebuild_returns(int(v))
    elif knob == 'stall_n': rebuild_stall(int(v))
    elif knob == 'rrev_wob': rebuild_rev(BASE['div_lines'], int(v))
    elif knob == 'div_lines': rebuild_rev(v, BASE['rrev_wob'])
    else: raise KeyError(knob)


def reset():
    C.MAE_STOP = BASE['mae_stop_pct']; C.LIN_HOP = BASE['lin_hop']
    C.CEIL_HI = BASE['ceil_hi']; C.TRIG_TF = BASE['ceil_trig_tf']
    C.GATE_BARS = BASE['oob_gate_bars']; C.DIP_MID = BASE['dip_mid']
    C.DIP_DWELL = BASE['dip_dwell_bars']
    C.DIP_FENCE = BASE['dip_fence']; C.DIP_HI = BASE['dip_fence']
    C.DIP_LO = 100.0 - BASE['dip_fence']
    C.EXF_LO = BASE['momo_fence_r']; C.EXF_HI = 100.0 - BASE['momo_fence_r']
    T.EXF_LO = BASE['momo_fence_r']; T.EXF_HI = 100.0 - BASE['momo_fence_r']
    if T.XWOB != BASE['reent_xwob']: rebuild_returns(BASE['reent_xwob'])
    if _STALL_NOW[0] != BASE['stall_n']:
        rebuild_stall(BASE['stall_n']); _STALL_NOW[0] = BASE['stall_n']
    if tuple(C.DIV_TFS) != BASE['div_lines'] or C.RREV != BASE['rrev_wob']:
        rebuild_rev(BASE['div_lines'], BASE['rrev_wob'])


_STALL_NOW = [BASE['stall_n']]


def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)


def run():
    """chain 0 over the whole tape at whatever the globals currently say."""
    legs = []; k, d = SEED, +1
    guard = 0
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
        mae += a_; mfe += f_; real += r['real']
        per[DAYOF(r['open'])] += r['real']
    st = sum(1 for r in legs if r['why'] == 'mae breach')
    return dict(n=len(legs), pos=sum(1 for r in legs if r['real'] > 0), st=st, mae=mae, mfe=mfe,
                real=real, per=dict(per),
                rpl=(real / len(legs)) if legs else 0.0,
                sr=(100.0 * st / len(legs)) if legs else 0.0,
                mm=(mfe / mae) if mae else float('inf'))


GRID = [
 ('mae_stop_pct', [0.6, 0.8, 1.1, 1.4, 1.8, 2.5]),
 ('reent_xwob', [2, 4, 6, 8, 12, 18]),
 ('lin_hop', [1, 2, 3, 4, 6]),
 ('stall_n', [3, 4, 6, 8, 12]),
 ('momo_fence_r', [10.0, 14.0, 17.0, 20.0, 25.0]),
 ('dip_fence', [50.5, 52.0, 53.0, 55.0, 58.0, 65.0]),
 ('dip_dwell_bars', [2, 4, 6, 9, 12, 24]),
 ('dip_mid', [45.0, 48.0, 50.0, 52.0, 55.0]),
 ('oob_gate_bars', [24, 48, 72, 120, 240]),
 ('ceil_hi', [12, 16, 20, 23]),
 ('ceil_trig_tf', [8, 10, 12, 15, 20]),
 ('rrev_wob', [1, 2, 3, 5, 8]),
 ('div_lines', [(1,), (2,), (1, 2), (1, 2, 3)]),
]

print('# THE BANKED CONFIG, for the baseline row', flush=True)
box(('knob', 'banked value'),
    [(k, str(v)) for k, v in BASE.items()])
print('# tape %d bars, %s -> %s' % (N, DAYOF(0), DAYOF(N - 1)), flush=True)
print('\n# baseline running ...', flush=True)
reset()
B = tally(run())
print('# baseline: %d legs, %d stops (%.1f%%), MFE/MAE %.2f, realised %+.4f, per leg %+.6f'
      % (B['n'], B['st'], B['sr'], B['mm'], B['real'], B['rpl']), flush=True)

for knob, vals in GRID:
    rows = []
    for v in vals:
        reset(); apply(knob, v)
        if knob == 'stall_n': _STALL_NOW[0] = int(v)
        t = tally(run())
        win = sum(1 for dd in t['per'] if dd in B['per'] and t['per'][dd] > B['per'][dd])
        los = sum(1 for dd in t['per'] if dd in B['per'] and t['per'][dd] < B['per'][dd])
        lbl = ('ws' + ',ws'.join(str(x) + 'r' for x in v)) if knob == 'div_lines' else str(v)
        rows.append((lbl + ('   <- BANKED' if (str(v) == str(BASE[knob])
                                               or (knob == 'div_lines' and tuple(v) == BASE[knob]))
                            else ''),
                     str(t['n']), str(t['pos']), str(t['st']), '%.1f%%' % t['sr'],
                     '%.4f' % t['mae'], '%.4f' % t['mfe'], '%.2f' % t['mm'],
                     '%+.4f' % t['real'], '%+.6f' % t['rpl'],
                     '%+.6f' % (t['rpl'] - B['rpl']), '%d / %d' % (win, los)))
    print('\n# %s — BANKED %s' % (knob.upper(), BASE[knob]), flush=True)
    box(('value', 'legs', 'positive', 'stops', 'stop rate', 'MAE', 'MFE', 'MFE/MAE', 'realised',
         'realised per leg', 'vs banked per leg', 'days won / lost'), rows)
    sys.stdout.flush()
reset()
print('\n# SWEEP COMPLETE', flush=True)
