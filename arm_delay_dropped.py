"""
arm_delay_dropped.py (Joe 0704) — the setups the arm-delay LOSES: big-leg setups that traded on the ORIG arm
but not after the delay (no s5Mage reversal in-window, or the delayed cascade no longer finishes). → table
arm_delay_dropped. Probe config: finisher_v2(gcs5M), wob=2 on s5m/s5Mage, DB working configs (emerging).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, datetime as dtm; from datetime import timezone
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis import lr_v2 as L
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import BASE_BIAS

def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
db = DatabaseManager(**get_db_config()); db.connect(); cfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(db)
HI, LO, WOB = lr.hi, lr.lo, 2

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

def eval_setup(W, setup, sig, q15h, q15l, q30h, q30l, revg):
    opens = L.gate_open(W, lr, [setup], sig)
    if not opens: return None
    (oi, es, bd, ok, rsn, ocap) = opens[0]
    qA, qB = (q15h, q30h) if es == 1 else (q15l, q30l)
    q1 = L.q1_gate(qA, qB, max(0, ok - lr.fin_lb), min(ocap, ok + lr.fin_fwd))
    if q1 is None: return None
    return L.fin_trigger(revg, bd, q1, ocap)

rows = []
for lbl, end in [('06-16', ms('2026-06-16 13:00')), ('06-18', ms('2026-06-18 00:00')),
                 ('06-21', ms('2026-06-21 00:00')), ('06-22', ms('2026-06-22 00:00'))]:
    W = bm.BiasWindow(db, end, lookback=72, warmup=80, cfg=cfg, lean=True); W._line = W._line_emerging
    ts = W.ts
    setups = L.v2_arm(W, lr); sig = L.gate_signals(W, lr)
    q15h, q15l = L.s_qualify(W, lr, 's15m', 's15M', 's15r', lr.s15r_lb)
    q30h, q30l = L.s_qualify(W, lr, 's30m', 's30M', 's30r', lr.s30r_lb)
    revg = L._mage_rev(W.line('gcs5M'), lr.fin_mage_wob)
    s5M, s7M, s7m, s7r = (W._line_emerging(n) for n in ('s5M', 's7M', 's7m', 's7r'))
    d5h, d5l = travelled_direct(s5M); d7h, d7l = travelled_direct(s7M)
    pred7 = L.predict_breach(s7r, s7m, s7M, HI, LO, L.FENCE_HI, L.FENCE_LO)
    rev5M = L._mage_rev(s5M, WOB)
    for (i, es, bd, cap, src) in setups:
        dir5 = d5l if es == -1 else d5h; dir7 = d7l if es == -1 else d7h
        s7r_es = (s7r <= LO) if es == -1 else (s7r >= HI)
        cond = dir5 & dir7 & (s7r_es | (pred7 == es))
        kc = next((k for k in range(i + 1, cap) if cond[k]), None)
        if kc is None: continue                                          # not big-leg
        da = next((k for k in range(kc, cap) if rev5M[k] == bd), None)
        orig_e = eval_setup(W, (i, es, bd, cap, src), sig, q15h, q15l, q30h, q30l, revg)
        del_setup = (da if da is not None else i, es, bd, cap, src)
        del_e = eval_setup(W, del_setup, sig, q15h, q15l, q30h, q30l, revg)
        if orig_e is not None and del_e is None:                         # DROPPED by the delay
            reason = 'no_s5Mage_reversal' if da is None else 'delayed_no_finish'
            rows.append((lbl, int(ts[i]), es, bd, int(ts[kc]), int(ts[da]) if da is not None else None,
                         int(ts[cap - 1]), int(ts[orig_e]), reason, int((cap - (da if da else i)))))

db.execute('DROP TABLE IF EXISTS arm_delay_dropped')
db.execute('''CREATE TABLE arm_delay_dropped (win VARCHAR(8), arm_ms BIGINT, es INT, bd INT, bigleg_ms BIGINT,
              delayed_arm_ms BIGINT, cap_ms BIGINT, orig_entry_ms BIGINT, drop_reason VARCHAR(32), delayed_window_bars INT)''')
db.executemany('INSERT INTO arm_delay_dropped VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
from collections import Counter
print('dropped by the delay: %d setups' % len(rows))
print('by reason:', dict(Counter(r[8] for r in rows)))
print('by window:', dict(Counter(r[0] for r in rows)))
print('-> table arm_delay_dropped (window, arm_ms, es, bd, bigleg_ms, delayed_arm_ms, cap_ms, orig_entry_ms, drop_reason, delayed_window_bars)')
db.disconnect()
