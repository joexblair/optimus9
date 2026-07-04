"""
build_armdelay_walk.py (Joe 0704) — sizing/compounding/maxDD report for the ARM-DELAY stack (provisional):
arm delayed to the s5Mage reversal (wob-2, big-leg), finisher runs BOTH windows (lookback + forward, union),
gcs5M trigger, exit = lr_exit_v2(predict=False)+strand_rescue with a 0.7% stop. Causal/emerging. ONE
continuous window (06-12→06-22, the validated span). Same 5x dynamic sizing + compounding as build_v2_walk.
HOLD LIGHTLY — one config, one window, un-OOS, cost=0.20% EST. → table armdelay_walk.
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
def dt(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc)
START, LEV, MAXLOT, RT, STOP, WOB = 500.0, 5.0, 66000, 0.20, 0.7, 2
db = DatabaseManager(**get_db_config()); db.connect(); cfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(db)
HI, LO = lr.hi, lr.lo

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

W = bm.BiasWindow(db, ms('2026-06-22 00:00'), lookback=240, warmup=80, cfg=cfg, lean=True); W._line = W._line_emerging
ts = W.ts
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
opens = L.gate_open(W, lr, retimed, sig)
union = {}                                                             # tk -> (es,bd)  (both windows, union)
for (i, es, bd, ok, rsn, cap) in opens:
    qA, qB = (q15h, q30h) if es == 1 else (q15l, q30l)
    for (w0, w1) in ((max(0, ok - lr.fin_lb), min(cap, ok + lr.fin_fwd)), (i, min(cap, i + lr.fin_lb + lr.fin_fwd))):
        q = L.q1_gate(qA, qB, w0, w1)
        if q is not None:
            tk = L.fin_trigger(trigrev, bd, q, cap)
            if tk is not None: union[tk] = (es, bd)
ents = sorted([(int(ts[tk]), es, bd, tk) for tk, (es, bd) in union.items()])
cfg07 = replace(lr, sl=STOP)
resc = sorted(L.strand_rescue(W, cfg07, ents, L.lr_exit_v2(W, cfg07, ents, predict=False)), key=lambda x: x[0])
walk = {w[0]: w for w in lr_walk(W, ents, lr)}

acct = START; peak = START; maxdd = 0.0; mineq = START; capped = None; rows = []; nsl = 0
for i, (tms, exms, bd, epx, xpx, r, reason) in enumerate(resc):
    lot = min(MAXLOT, acct * LEV / float(epx))
    if lot >= MAXLOT and capped is None: capped = i
    pnl = lot * float(epx) * (r - RT) / 100.0
    acct += pnl; peak = max(peak, acct); maxdd = max(maxdd, (peak - acct) / peak); mineq = min(mineq, acct)
    nsl += 1 if reason == 'SL' else 0
    rows.append((tms, dt(tms), bd, round(walk[tms][4], 3), round(walk[tms][5], 3), dt(exms), round(r, 3),
                 reason, round(float(epx), 8), int(lot), round(pnl, 2), round(acct, 2)))
db.execute('DROP TABLE IF EXISTS armdelay_walk')
db.execute('''CREATE TABLE armdelay_walk (trade_ms BIGINT, trade_dt DATETIME, trade_dir TINYINT, mae FLOAT,
    mfe FLOAT, exit_dt DATETIME, ret FLOAT, reason VARCHAR(8), entry_px DECIMAL(14,8), lot INT, pnl_usdt FLOAT, equity FLOAT)''')
db.executemany('INSERT INTO armdelay_walk VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
netsum = sum(r - RT for (_, _, _, _, _, r, _) in resc); wins = sum(1 for (*_, r, _rr) in resc if r - RT > 0)
print('ARM-DELAY walk (wob2, both-windows, %.1f%% stop, 06-12→06-22, 5x compounding):' % STOP)
print('  trades=%d  SL=%d (%.0f%%)  win=%.0f%%  sum-net/trade=%+.3f%%' % (len(rows), nsl, 100 * nsl / len(rows), 100 * wins / len(rows), netsum / len(rows)))
print('  $%.0f → $%.0f (%.1fx)  maxDD=%.0f%%  min-eq=$%.0f  cap66k@trade=%s' % (START, acct, acct / START, 100 * maxdd, mineq, capped))
db.disconnect()
