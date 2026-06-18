"""
bias_pk_worst.py — per-trade detail for the WORST window of the most-promising config.

Config: trigger s8m · s14M OOB gate · exit = opposite s30a+s30M wob with s6m AND s6r OOB (with-r).
Window: ending 2026-05-18 01:24 (the -2542 USDT window). 33K lots, fees in.
Emits per-trade ledger (incl max adverse excursion + duration) to db table bias_pk_worst.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.compute.indicator_computer import IndicatorComputer as IC

OOB_HI, OOB_LO, NEUTRAL_BAND = 85.0, 15.0, 2.2
COINS, START, FEE_RT, TRIG_TF, H = 33_000, 1000.0, 0.11, 8, 3600_000
def sgn(v): return 1 if v >= OOB_HI else (-1 if v <= OOB_LO else 0)
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')

END = int(dtm.datetime(2026, 5, 18, 1, 24, tzinfo=timezone.utc).timestamp() * 1000)
db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80)
base, ts, ws, _, px = det._setup(END)
W1 = min(int(ts[-1]), END); W0 = W1 - 168 * H

def BB(fr, s, L, m): return IC.f_bb(IC.build_source(fr, s), L, m)
def KK(fr, s, r, st, k): return IC.f_k(IC.build_source(fr, s), r, st, k)
def AL(v, fr): return IC.align_to_base(v, fr, base)
at = lambda t: int(np.searchsorted(ts, t, side='right')) - 1
f7 = IC.resample(base, 420); s14M = AL(BB(f7, 'ohlc4', 74, 0.72), f7)
f6 = IC.resample(base, 360); s6m = AL(BB(f6, 'hlc3', 10, 0.40), f6); s6r = AL(KK(f6, 'close', 6, 6, 5), f6)
f30 = IC.resample(base, 30); t30 = f30['timestamp'].to_numpy() + 30_000
s30m_b = BB(f30, 'hlc3', 10, 0.40); s30M_b = BB(f30, 'ohlc4', 37, 0.72); s30r_b = KK(f30, 'close', 6, 6, 5)
f8 = IC.resample(base, TRIG_TF * 60); s8m_b = BB(f8, 'hlc3', 10, 0.4); t8c = f8['timestamp'].to_numpy() + TRIG_TF * 60_000

wobs = []
for i in range(2, len(s30M_b)):
    a, b, c = s30M_b[i-2], s30M_b[i-1], s30M_b[i]
    if a != a or b != b or c != c: continue
    if a >= OOB_HI and c < b < a and s30m_b[i-2] >= OOB_HI and s30r_b[i-2] >= OOB_HI: sd = 1
    elif a <= OOB_LO and c > b > a and s30m_b[i-2] <= OOB_LO and s30r_b[i-2] <= OOB_LO: sd = -1
    else: continue
    tw = int(t30[i]); j = at(tw)
    if j >= 0: wobs.append((tw, j, sd))

def s6rext(jr, S):
    bv = s6r[jr]
    for step in (-1, 1):
        k2 = jr
        while 0 <= k2 + step < len(s6r):
            v = s6r[k2 + step]
            if v != v: break
            if (S == -1 and v >= 50) or (S == 1 and v <= 50): break
            k2 += step
            if (S == 1 and v > bv) or (S == -1 and v < bv): bv = v
    return bv

trigs = []
for k in range(2, len(s8m_b)):
    a, b, c = s8m_b[k-2], s8m_b[k-1], s8m_b[k]
    if a != a or b != b or c != c: continue
    S = -1 if (b <= OOB_LO and b < a and b < c) else (1 if (b >= OOB_HI and b > a and b > c) else 0)
    if S == 0: continue
    rt = int(t8c[k-1]); j = at(rt)
    if j >= 0: trigs.append(dict(t=rt, j=j, s=S, s6r=s6r[j]))
g = {1: None, -1: None}
for w in trigs:
    sd = w['s']; ok = (sd == 1 and w['s6r'] > 50) or (sd == -1 and w['s6r'] < 50)
    w['res'] = w['s6r'] if ok else g[sd]
    if ok: g[sd] = w['s6r']

rows = []; bal = START; last = {1: None, -1: None}; seen = set()
for W in trigs:
    S = W['s']; flt = last[S]; last[S] = W
    if sgn(s14M[W['j']]) != S or W['res'] is None or flt is None or not (W0 <= W['t'] <= W1): continue
    fv = s6rext(flt['j'], S)
    call = 0 if abs(W['res'] - fv) <= NEUTRAL_BAND else (1 if W['res'] > fv else -1)
    if call == 0: continue
    bd = call
    ent = next(((tw, j) for (tw, j, s) in wobs if s == -bd and tw > W['t']), None)
    if ent is None or ent[1] in seen: continue
    seen.add(ent[1]); et, ej = ent
    ex = next(((tw, j) for (tw, j, s) in wobs if s == bd and tw > et and sgn(s6m[j]) == bd and sgn(s6r[j]) == bd), None)
    if ex is None: xt, xj, why = int(ts[-1]), len(px) - 1, 'eod'
    else: xt, xj, why = ex[0], ex[1], 's6mr'
    ep, xp = float(px[ej]), float(px[xj])
    seg = (px[ej:xj + 1] - ep) / ep * 100 * bd                # signed in bias dir
    move = float(seg[-1]); adverse = float(seg.min())          # max adverse excursion (worst against)
    pnl = COINS * ep * (move - FEE_RT) / 100.0; bal += pnl
    rows.append([dts(W['t']), dts(et), dts(xt), 'LONG' if bd == 1 else 'SHORT', why,
                 round(ep, 5), round(xp, 5), round(move, 3), round(adverse, 3),
                 round((xt - et) / 60000), round(pnl, 2), round(bal, 2)])
db.execute('DROP TABLE IF EXISTS bias_pk_worst')
db.execute('''CREATE TABLE bias_pk_worst (pk BIGINT AUTO_INCREMENT PRIMARY KEY, print_time DATETIME,
    entry_time DATETIME, exit_time DATETIME, direction VARCHAR(8), exit_reason VARCHAR(4),
    entry_px FLOAT, exit_px FLOAT, move_pct FLOAT, max_adverse_pct FLOAT, dur_min INT,
    pnl_usd FLOAT, balance_usd FLOAT)''')
db.executemany('''INSERT INTO bias_pk_worst (print_time,entry_time,exit_time,direction,exit_reason,entry_px,
    exit_px,move_pct,max_adverse_pct,dur_min,pnl_usd,balance_usd) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows)
db.disconnect()

pn = np.array([r[10] for r in rows])
print(f'WORST WINDOW {dts(W0)} → {dts(W1)}  ·  trig s8m · OOB · exit s6m+s6r')
print(f'  {len(rows)} trades · {int((pn>0).sum())} wins ({100*(pn>0).mean():.0f}%) · net ${pn.sum():+.0f} · '
      f'avg win ${pn[pn>0].mean():+.0f} · avg loss ${pn[pn<=0].mean():+.0f}')
adv = np.array([r[8] for r in rows]); dur = np.array([r[9] for r in rows])
print(f'  losers: median adverse {np.median(adv[pn<=0]):.2f}% · median dur {int(np.median(dur[pn<=0]))}m   '
      f'winners: median dur {int(np.median(dur[pn>0]))}m')
print('  worst 5 trades:')
for r in sorted(rows, key=lambda x: x[10])[:5]:
    print(f'    {r[1][5:]} {r[3]:5} {r[5]}→{r[6]}  move{r[7]:+.2f}% adv{r[8]:+.2f}% {r[9]}m  ${r[10]:+.0f}')
print(f'→ db table bias_pk_worst ({len(rows)} rows)')
