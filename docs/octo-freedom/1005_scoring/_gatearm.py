"""THE DELEGATION GATE IN THE CHAIN — definition 2, the MAE/MFE and net impact. 1008.

Joe 1008: *"does it improve if we sweep 6/9/12/16/20 minutes? 'improve' carries two definitions:
1) likelihoodd of a correctly gated delegation, and 2) impact on our maemfe baseline"*.

ONE ARM = one (W_DGATE, oob_gate_bars) pair, run over the full 95 days on the banked build.
15 arms: off / once / retest x 72 / 108 / 144 / 192 / 240 bars (6 / 9 / 12 / 16 / 20 min).

`off` at each width is THE CONTROL FOR THAT WIDTH - moving oob_gate_bars changes the chain whether
or not the gate exists, so the gate's own effect is only readable against the same width.

`off` at 72 bars is the BANKED BUILD and must return fit +0.7511 / hold +4.0801 / all +4.8312 on
1623 legs. If it does not, nothing else in the sweep is trusted.

MFE/MAE uses Joe's 1007 scoring rule: a stopped leg scores MAE = mae_stop_pct 2.50 and MFE 0.0000.
It is comparable ACROSS these arms because the stop is fixed at 2.5 on every one of them.
"""
import os, sys, json, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

GB = int(os.environ['X_GB'])
C.GATE_BARS = GB                   # run_leg reads it as a module global
SC, PX = C.SC, C.PX
N = len(SC.ts); FEE = 0.11
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
assert abs(C.MAE_STOP - 2.5) < 1e-9, 'mae_stop_pct is %s, the arm needs 2.5' % C.MAE_STOP
assert T.XWOB == 18, 'reent_xwob is %d, the arm needs 18' % T.XWOB
assert C.XT_ROLE == 'b' and C.XT_TFS == 'next' and C.XT_FENCE == 0, 'not the banked B x-cross target'

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

legs = []; k, d, g = 1, +1, 0
nhand = nref = 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    if hand is not None: nhand += 1
    nref += sum(1 for _, lbl in tr if lbl.startswith('DELEGATION REFUSED'))
    legs.append(dict(day=DAYOF(k), why=why, open=k, exit=xk, dd=d,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

per = collections.defaultdict(lambda: [0.0, 0, 0, 0.0, 0.0]); whys = collections.Counter()
for r in legs:
    a_, f_ = (C.MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['dd'])
    e = per[r['day']]
    e[0] += r['real']; e[1] += 1; e[2] += 1 if r['why'] == 'mae breach' else 0
    e[3] += a_; e[4] += f_
    whys[r['why']] += 1
print(json.dumps(dict(dgate=C.DGATE, gb=GB, mins=round(GB * 5 / 60.0, 1), legs=len(legs),
                      handovers=nhand, refusals=nref, whys=dict(whys),
                      per={k_: [round(v[0], 4), v[1], v[2], round(v[3], 4), round(v[4], 4)]
                           for k_, v in sorted(per.items())})), flush=True)
