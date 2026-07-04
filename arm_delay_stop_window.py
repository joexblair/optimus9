"""
arm_delay_stop_window.py (Joe 0704) — arm-delay (wob-2 s5Mage), finisher runs BOTH windows (7x30s LOOKBACK
from gate-open + FORWARD from arm), tags each trade lb/fw/both, sweeps the STOP, reports net-of-cost per
segment (which window earns / is detrimental + the stop that rescues most). finisher_v2(gcs5M), 4 windows.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, datetime as dtm; from datetime import timezone
from dataclasses import replace
import bias_machine as bm
from optimus9.analysis.lr import lr_config, lr_walk
from optimus9.analysis import lr_v2 as L
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import BASE_BIAS

def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
db = DatabaseManager(**get_db_config()); db.connect(); cfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(db)
HI, LO, WOB = lr.hi, lr.lo, 2
STOPS = (0.3, 0.4, 0.5, 0.6, 0.7)

def travelled_direct(line):
    n = len(line); dh = dl = False; last = 0; DH = np.zeros(n, bool); DL = np.zeros(n, bool)
    for k in range(n):
        if line[k] >= HI:
            if last == -1: dh = True
            last = 1; dl = False
        elif line[k] <= LO:
            if last == 1: dl = True
            last = -1; dh = False
        DH[k] = dh; DL[k] = dl
    return DH, DL

def finish_both(W, opens, trigrev, q15h, q15l, q30h, q30l):
    lb, fw = {}, {}
    for (i, es, bd, ok, rsn, cap) in opens:
        qA, qB = (q15h, q30h) if es == 1 else (q15l, q30l)
        q = L.q1_gate(qA, qB, max(0, ok - lr.fin_lb), min(cap, ok + lr.fin_fwd))
        if q is not None:
            tk = L.fin_trigger(trigrev, bd, q, cap)
            if tk is not None: lb[tk] = (es, bd)
        qf = L.q1_gate(qA, qB, i, min(cap, i + lr.fin_lb + lr.fin_fwd))
        if qf is not None:
            tk = L.fin_trigger(trigrev, bd, qf, cap)
            if tk is not None: fw[tk] = (es, bd)
    return lb, fw

# collect per-window: entries + per-tk tag, across the 4 windows
WD = []
for end in [ms('2026-06-16 13:00'), ms('2026-06-18 00:00'), ms('2026-06-21 00:00'), ms('2026-06-22 00:00')]:
    W = bm.BiasWindow(db, end, lookback=72, warmup=80, cfg=cfg, lean=True); W._line = W._line_emerging; ts = W.ts
    setups = L.v2_arm(W, lr); sig = L.gate_signals(W, lr)
    q15h, q15l = L.s_qualify(W, lr, 's15m', 's15M', 's15r', lr.s15r_lb)
    q30h, q30l = L.s_qualify(W, lr, 's30m', 's30M', 's30r', lr.s30r_lb)
    trigrev = L._mage_rev(W.line('gcs5M'), lr.fin_mage_wob)
    s5M, s7M, s7mL, s7r = (W._line_emerging(n) for n in ('s5M', 's7M', 's7m', 's7r'))
    d5h, d5l = travelled_direct(s5M); d7h, d7l = travelled_direct(s7M)
    pred7 = L.predict_breach(s7r, s7mL, s7M, HI, LO, L.FENCE_HI, L.FENCE_LO); rev5M = L._mage_rev(s5M, WOB)
    retimed = []
    for (i, es, bd, cap, src) in setups:
        dir5 = d5l if es == -1 else d5h; dir7 = d7l if es == -1 else d7h
        s7r_es = (s7r <= LO) if es == -1 else (s7r >= HI)
        cond = dir5 & dir7 & (s7r_es | (pred7 == es))
        kc = next((k for k in range(i + 1, cap) if cond[k]), None)
        arm = next((k for k in range(kc, cap) if rev5M[k] == bd), None) if kc is not None else i
        if arm is not None: retimed.append((arm, es, bd, cap, src))
    lb, fw = finish_both(W, L.gate_open(W, lr, retimed, sig), trigrev, q15h, q15l, q30h, q30l)
    union = {**lb, **fw}
    ents = [(int(ts[tk]), es, bd, tk) for tk, (es, bd) in union.items()]
    tag = {int(ts[tk]): ('both' if tk in lb and tk in fw else 'lb' if tk in lb else 'fw') for tk in union}
    WD.append((W, ents, tag))

print('arm-delay (wob-2) — net-of-cost per finisher window, by STOP  [lb=lookback fw=forward both=both]:')
print(' stop | combined n net win%% | lb  n net | fw  n net | both n net')
for stop in STOPS:
    cfg2 = replace(lr, sl=stop)
    seg = {'lb': [0, 0.0], 'fw': [0, 0.0], 'both': [0, 0.0]}; cn = 0; cnet = 0.0; cw = 0
    for (W, ents, tag) in WD:
        resc = L.strand_rescue(W, cfg2, ents, L.lr_exit_v2(W, cfg2, ents, predict=False))
        for (tms, xms, bd, epx, xpx, ret, rsn) in resc:
            net = ret - 0.20; t = tag.get(tms, 'lb')
            seg[t][0] += 1; seg[t][1] += net; cn += 1; cnet += net; cw += 1 if net > 0 else 0
    print(' %.1f  | n=%-4d %+6.1f %2.0f    | %-4d %+6.1f | %-4d %+6.1f | %-4d %+6.1f' % (
        stop, cn, cnet, 100.0 * cw / max(1, cn), seg['lb'][0], seg['lb'][1], seg['fw'][0], seg['fw'][1], seg['both'][0], seg['both'][1]))
db.disconnect()
