"""
bias_pk_backtest.py — sweep the bias-machine trade over the last 7 days.

ENTRY: at each pk UPDATE (s{TF}m reversal → s6r anchor-vs-floater call, gated), enter on the next
       s30a+s30M wobslay aligned to the bias (BEAR→hi, BULL→lo).
EXIT : opposite-side s30a+s30M wobslay with s6m [+ s6r if exit_has_r] OOB on that side, else data end.
SWEEP: trigger TF 4..12 min  x  exit {without r / with r}  x  gate {s14M OOB / s14M vs50}.
33K lots · 50x · Bybit taker 0.11% rt · 1000 USDT start.  Writes db table bias_pk_sweep.
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
TFS = list(range(4, 13))                                 # trigger TFs 4..12 min
def sgn(v): return 1 if v >= OOB_HI else (-1 if v <= OOB_LO else 0)
def fmt(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d %H:%M')

END = int(dtm.datetime(2026, 6, 17, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)  # PINNED for reproducible runs
db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80)
base, ts, ws, _, px = det._setup(END)
db.disconnect()
W1 = min(int(ts[-1]), END); W0 = W1 - 168 * 3600_000

def bb(fr, s, L, m): return IC.f_bb(IC.build_source(fr, s), L, m)
def kk(fr, s, r, st, k): return IC.f_k(IC.build_source(fr, s), r, st, k)
def al(v, fr): return IC.align_to_base(v, fr, base)
tf7 = IC.resample(base, 420); s14M = al(bb(tf7, 'ohlc4', 74, 0.72), tf7)
tf6 = IC.resample(base, 360); s6r = al(kk(tf6, 'close', 6, 6, 5), tf6); s6m = al(bb(tf6, 'hlc3', 10, 0.40), tf6)
tf30 = IC.resample(base, 30)
s30m_b = bb(tf30, 'hlc3', 10, 0.40); s30M_b = bb(tf30, 'ohlc4', 37, 0.72); s30r_b = kk(tf30, 'close', 6, 6, 5)
t30 = tf30['timestamp'].to_numpy() + 30_000
def at(t): return int(np.searchsorted(ts, t, side='right')) - 1

# ── entry/exit s30a+s30M wobslays (both sides), fixed ──
wobs = []
for i in range(2, len(s30M_b)):
    a, b, c = s30M_b[i-2], s30M_b[i-1], s30M_b[i]
    if a != a or b != b or c != c: continue
    if a >= OOB_HI and c < b < a and s30m_b[i-2] >= OOB_HI and s30r_b[i-2] >= OOB_HI: sd = 1
    elif a <= OOB_LO and c > b > a and s30m_b[i-2] <= OOB_LO and s30r_b[i-2] <= OOB_LO: sd = -1
    else: continue
    tw = int(t30[i]); j = at(tw)
    if j >= 0: wobs.append((tw, j, sd))

def s6r_extreme(jr, S):
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

def build_trigs(tf_min):                                 # s{tf}m reversals (double-spikes) → trigs with side-of-50 res
    secs = tf_min * 60
    fr = IC.resample(base, secs); sNm = bb(fr, 'hlc3', 10, 0.4); tNc = fr['timestamp'].to_numpy() + secs * 1000
    trigs = []
    for k in range(2, len(sNm)):
        a, b, c = sNm[k-2], sNm[k-1], sNm[k]
        if a != a or b != b or c != c: continue
        S = -1 if (b <= OOB_LO and b < a and b < c) else (1 if (b >= OOB_HI and b > a and b > c) else 0)
        if S == 0: continue
        rt = int(tNc[k-1]); j = at(rt)
        if j >= 0: trigs.append(dict(t=rt, j=j, s=S, s6r=s6r[j]))
    good = {1: None, -1: None}
    for w in trigs:
        sd = w['s']; ok = (sd == 1 and w['s6r'] > 50.0) or (sd == -1 and w['s6r'] < 50.0)
        w['res'] = w['s6r'] if ok else good[sd]
        if ok: good[sd] = w['s6r']
    return trigs

def pk_updates(trigs, gate):
    ups, last = [], {1: None, -1: None}
    for W in trigs:
        S = W['s']; flt = last[S]; last[S] = W
        g = (sgn(s14M[W['j']]) == S) if gate == 'oob' else ((s14M[W['j']] > 50.0) == (S == 1))
        if not g or W['res'] is None or flt is None: continue
        if not (W0 <= W['t'] <= W1): continue
        fv = s6r_extreme(flt['j'], S)
        call = 'NEUT' if abs(W['res'] - fv) <= NEUTRAL_BAND else ('BULL' if W['res'] > fv else 'BEAR')
        bd = 1 if call == 'BULL' else (-1 if call == 'BEAR' else 0)
        if bd != 0: ups.append((W['t'], bd))
    return ups

def run_config(trigs, gate, exit_r, em, er):            # em/er = the exit's aligned m & r lines
    bal = START; trades = 0; wins = 0; eod = 0; seen = set()
    for (t_up, bd) in pk_updates(trigs, gate):
        ent = next(((tw, j) for (tw, j, s) in wobs if s == -bd and tw > t_up), None)
        if ent is None or ent[1] in seen: continue
        seen.add(ent[1]); ej = ent[1]
        ex = next((j for (tw, j, s) in wobs if s == bd and tw > ent[0]
                   and sgn(em[j]) == bd and (not exit_r or sgn(er[j]) == bd)), None)
        if ex is None: eod += 1                          # never exited → rode to data end (artifact tell)
        xj = ex if ex is not None else len(px) - 1
        ep, xp = float(px[ej]), float(px[xj])
        pnl = COINS * ep * (bd * (xp - ep) / ep * 100 - FEE_RT) / 100.0
        bal += pnl; trades += 1; wins += (pnl > 0)
    return trades, wins, bal - START, eod

sNm_al, sNr_al = {}, {}                                  # aligned m/r lines per TF (for the exit sweep)
for tf in TFS:
    fr = IC.resample(base, tf * 60); sNm_al[tf] = al(bb(fr, 'hlc3', 10, 0.4), fr); sNr_al[tf] = al(kk(fr, 'close', 6, 6, 5), fr)

# ── two sweeps ──
rows = []
for tf in TFS:                                          # (1) trigger TF varies, exit FIXED (s6m+s6r, 6min)
    trigs = build_trigs(tf)
    for gate in ('oob', 'vs50'):
        for er in (False, True):
            n, w, net, eod = run_config(trigs, gate, er, s6m, s6r)
            rows.append(['trigger', tf, int(er), gate, n, w, round(net, 2), eod])
trigs12 = build_trigs(12)                               # (2) trigger FIXED s12m, exit TF varies
for tf in TFS:
    for gate in ('oob', 'vs50'):
        for er in (False, True):
            n, w, net, eod = run_config(trigs12, gate, er, sNm_al[tf], sNr_al[tf])
            rows.append(['exit', tf, int(er), gate, n, w, round(net, 2), eod])

db.connect()
db.execute('DROP TABLE IF EXISTS bias_pk_sweep')
db.execute('''CREATE TABLE bias_pk_sweep (pk BIGINT AUTO_INCREMENT PRIMARY KEY, sweep VARCHAR(8), tf_min INT,
    exit_has_r TINYINT, gate_mode VARCHAR(6), trades INT, wins INT, net_usd FLOAT, eod_exits INT)''')
db.executemany('INSERT INTO bias_pk_sweep (sweep,tf_min,exit_has_r,gate_mode,trades,wins,net_usd,eod_exits) '
               'VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', rows)
db.disconnect()

def cell(sw, tf, gate, er): return next(r[6] for r in rows if r[0] == sw and r[1] == tf and r[3] == gate and r[2] == er)
def eodc(sw, tf, gate, er): return next((r[7], r[4]) for r in rows if r[0] == sw and r[1] == tf and r[3] == gate and r[2] == er)
for sw, title in (('trigger', '(1) TRIGGER sweep (exit fixed s6m+s6r)'), ('exit', '(2) EXIT sweep (trigger fixed s12m)')):
    print(f'\n{title}  {fmt(W0)}→{fmt(W1)}  net$ 7d   [OOB+r: eod/trades]')
    print(f'{"TF":>3} | {"OOB no-r":>9} {"OOB +r":>8} | {"vs50 no-r":>10} {"vs50 +r":>9}   eod/n')
    for tf in TFS:
        e, n = eodc(sw, tf, 'oob', 1)
        print(f'{tf:>3} | {cell(sw,tf,"oob",0):>+9.0f} {cell(sw,tf,"oob",1):>+8.0f} | '
              f'{cell(sw,tf,"vs50",0):>+10.0f} {cell(sw,tf,"vs50",1):>+9.0f}   {e}/{n}')
print(f'\n→ db table bias_pk_sweep ({len(rows)} rows)')
