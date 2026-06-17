"""
bias_pk_backtest.py — trade the bias machine over the last 7 days.

ENTRY: at each pk print (s12m reversal → s6r anchor-vs-floater call, gated), wait for the next
       s30a + s30M wobslay ALIGNED to the bias (BEAR→hi-peak reversal, BULL→lo-trough reversal); enter there.
EXIT : the next OPPOSITE confluence — s6m OOB + s30a + s30M wobslay (BEAR→lo, BULL→hi), else data end.
Two gate modes: 'oob' (s14M OOB on side S) and 'vs50' (debug: s14M > / < 50).
33K lots · Bybit taker fee 0.11% rt · 50x · 1000 USDT start.  Writes db table bias_pk_trades.
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
COINS, START, LEV, FEE_RT = 33_000, 1000.0, 50.0, 0.11
def sgn(v): return 1 if v >= OOB_HI else (-1 if v <= OOB_LO else 0)
def fmt(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d %H:%M')
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80)
base, ts, ws, _, px = det._setup(int(dtm.datetime.now(timezone.utc).timestamp() * 1000))
db.disconnect()
W1 = int(ts[-1]); W0 = W1 - 168 * 3600_000

def bb(fr, s, L, m): return IC.f_bb(IC.build_source(fr, s), L, m)
def kk(fr, s, r, st, k): return IC.f_k(IC.build_source(fr, s), r, st, k)
def al(v, fr): return IC.align_to_base(v, fr, base)
tf7 = IC.resample(base, 420);  s14M = al(bb(tf7, 'ohlc4', 74, 0.72), tf7)
tf6 = IC.resample(base, 360);  s6r = al(kk(tf6, 'close', 6, 6, 5), tf6); s6m = al(bb(tf6, 'hlc3', 10, 0.40), tf6)
tf12 = IC.resample(base, 720); s12m_b = bb(tf12, 'hlc3', 10, 0.4); t12c = tf12['timestamp'].to_numpy() + 720_000
tf30 = IC.resample(base, 30)
s30m_b = bb(tf30, 'hlc3', 10, 0.40); s30M_b = bb(tf30, 'ohlc4', 37, 0.72); s30r_b = kk(tf30, 'close', 6, 6, 5)
t30 = tf30['timestamp'].to_numpy() + 30_000
def at(t): return int(np.searchsorted(ts, t, side='right')) - 1

# ── s30a + s30M wobslays (both sides): s30M 2-bar turn off its extreme + s30a (all 3 s30 OOB) at the extreme ──
wobs = []
for i in range(2, len(s30M_b)):
    a, b, c = s30M_b[i-2], s30M_b[i-1], s30M_b[i]
    if a != a or b != b or c != c: continue
    if a >= OOB_HI and c < b < a and s30m_b[i-2] >= OOB_HI and s30r_b[i-2] >= OOB_HI: sd = 1
    elif a <= OOB_LO and c > b > a and s30m_b[i-2] <= OOB_LO and s30r_b[i-2] <= OOB_LO: sd = -1
    else: continue
    tw = int(t30[i]); j = at(tw)
    if j >= 0: wobs.append((tw, j, sd))

# ── s12m reversals → pk triggers (call via s6r anchor vs floater-trough/peak) ──
trigs = []
for k in range(2, len(s12m_b)):
    a, b, c = s12m_b[k-2], s12m_b[k-1], s12m_b[k]
    if a != a or b != b or c != c: continue
    S = -1 if (b <= OOB_LO and b < a and b < c) else (1 if (b >= OOB_HI and b > a and b > c) else 0)
    if S == 0: continue
    rt = int(t12c[k-1]); j = at(rt)
    if j < 0: continue
    trigs.append(dict(t=rt, j=j, s=S, s6r=s6r[j]))
good = {1: None, -1: None}
for w in trigs:
    sd = w['s']; ok = (sd == 1 and w['s6r'] > 50.0) or (sd == -1 and w['s6r'] < 50.0)
    w['res'] = w['s6r'] if ok else good[sd]
    if ok: good[sd] = w['s6r']

def s6r_extreme(jr, S):                                  # floater = s6r trough/peak extreme, unbounded to the 50-cross
    bv = s6r[jr]
    for step in (-1, +1):
        k2 = jr
        while 0 <= k2 + step < len(s6r):
            v = s6r[k2 + step]
            if v != v: break
            if (S == -1 and v >= 50.0) or (S == 1 and v <= 50.0): break
            k2 += step
            if (S == 1 and v > bv) or (S == -1 and v < bv): bv = v
    return bv

def pk_prints(mode):                                     # gated bias prints (t, bd) for a gate mode
    ups, last_rev = [], {1: None, -1: None}
    for W in trigs:
        S = W['s']; flt = last_rev[S]; last_rev[S] = W
        gate = (sgn(s14M[W['j']]) == S) if mode == 'oob' else ((s14M[W['j']] > 50.0) == (S == 1))
        if not gate or W['res'] is None or flt is None: continue
        if not (W0 <= W['t'] <= W1): continue
        fv = s6r_extreme(flt['j'], S)
        call = 'NEUT' if abs(W['res'] - fv) <= NEUTRAL_BAND else ('BULL' if W['res'] > fv else 'BEAR')
        bd = 1 if call == 'BULL' else (-1 if call == 'BEAR' else 0)
        if bd != 0: ups.append((W['t'], bd))
    return ups

def trade(t_up, bd):                                     # entry = next aligned wob; exit = next opposite confluence
    ent = next(((tw, j) for (tw, j, s) in wobs if s == -bd and tw > t_up), None)
    if ent is None: return None
    et, ej = ent
    ex = next(((tw, j) for (tw, j, s) in wobs if s == bd and tw > et and sgn(s6m[j]) == bd), None)
    if ex is None: xt, xj, why = int(ts[-1]), len(px) - 1, 'eod'
    else: xt, xj, why = ex[0], ex[1], 'wob'
    ep, xp = float(px[ej]), float(px[xj])
    return dict(up=t_up, et=et, xt=xt, ej=ej, xj=xj, bd=bd, ep=ep, xp=xp, why=why,
                move=bd * (xp - ep) / ep * 100)

# ── run both modes, collect rows, print summaries ──
db.connect()
db.execute('DROP TABLE IF EXISTS bias_pk_trades')
db.execute('''CREATE TABLE bias_pk_trades (
    pk BIGINT AUTO_INCREMENT PRIMARY KEY, gate_mode VARCHAR(6), print_time DATETIME, entry_time DATETIME,
    exit_time DATETIME, direction VARCHAR(8), exit_reason VARCHAR(4), entry_px FLOAT, exit_px FLOAT,
    lot_coins INT, notional_usd FLOAT, leverage INT, margin_usd FLOAT, fee_usd FLOAT,
    pnl_usd FLOAT, pnl_margin_pct FLOAT, balance_usd FLOAT)''')
cols = ['gate_mode', 'print_time', 'entry_time', 'exit_time', 'direction', 'exit_reason', 'entry_px', 'exit_px',
        'lot_coins', 'notional_usd', 'leverage', 'margin_usd', 'fee_usd', 'pnl_usd', 'pnl_margin_pct', 'balance_usd']
rows, summary = [], {}
for mode in ('oob', 'vs50'):
    bal = START; seen = set(); trs = []
    for (t_up, bd) in pk_prints(mode):
        tr = trade(t_up, bd)
        if tr is None or tr['ej'] in seen: continue       # dedupe trades sharing an entry wob
        seen.add(tr['ej']); trs.append(tr)
    for tr in trs:
        notional = COINS * tr['ep']; fee = notional * FEE_RT / 100.0
        pnl = notional * (tr['move'] - FEE_RT) / 100.0; bal += pnl
        rows.append([mode, dts(tr['up']), dts(tr['et']), dts(tr['xt']),
                     'LONG' if tr['bd'] == 1 else 'SHORT', tr['why'], round(tr['ep'], 5), round(tr['xp'], 5),
                     COINS, round(notional, 2), int(LEV), round(notional / LEV, 2), round(fee, 2),
                     round(pnl, 2), round(LEV * (tr['move'] - FEE_RT), 2), round(bal, 2)])
    pnls = np.array([r[13] for r in rows if r[0] == mode])
    summary[mode] = dict(n=len(trs), wins=int((pnls > 0).sum()), net=float(pnls.sum()), final=bal,
                         wob=sum(t['why'] == 'wob' for t in trs))
ph = ','.join(['%s'] * len(cols))
db.executemany(f"INSERT INTO bias_pk_trades ({','.join(cols)}) VALUES ({ph})", rows)
db.disconnect()

print(f'\nBACKTEST  {fmt(W0)} → {fmt(W1)} (7d) · entry=aligned s30a+s30M wob · exit=opposite s6m+s30a+s30M wob')
print(f'{"mode":>10} {"trades":>7} {"win%":>6} {"net$":>9} {"final$":>9} {"wob-exit":>9}')
for mode in ('oob', 'vs50'):
    s = summary[mode]
    lbl = 's14M-OOB' if mode == 'oob' else 's14M-vs50'
    print(f'{lbl:>10} {s["n"]:>7} {(100*s["wins"]/s["n"] if s["n"] else 0):>5.0f}% '
          f'{s["net"]:>+8.2f} {s["final"]:>9.2f} {s["wob"]:>4}/{s["n"]}')

# validation vs Joe's example (vs50: BEAR @0611 11:36 → entry 11:52 → exit 12:26)
ex = next((r for r in rows if r[0] == 'vs50' and r[1].endswith('11:36:00')), None)
if ex: print(f'\nexample check (vs50, print 0611 11:36): entry {ex[2][-8:-3]}  exit {ex[3][-8:-3]}  {ex[4]}')
print(f'→ db table bias_pk_trades ({len(rows)} rows)')
