"""
bias_pk_tpsl_roll.py — rolling-window test of a TAKE-MONEY exit (TP 0.8 / SL sweep).

Same machine + same entries as bias_pk_rollsweep (pk update → next aligned s30a+s30M wob,
s14M OOB gate) — only the EXIT changes: TP +0.8% or SL -stop% (whichever the px path hits
first), else timeout at data end. Sweeps trigger TF 4..12 x stop {0.25,0.30,0.40,0.45}, OOB
gate, over 7-day windows (5-day step) back as far as klines exist. 33K lots, fees in.
Writes db table bias_pk_tpsl_roll; prints a robustness leaderboard + the winner's per-window trace.
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
COINS, START, FEE_RT, TP = 33_000, 1000.0, 0.11, 0.8
TFS = list(range(4, 13)); STOPS = [0.25, 0.30, 0.40, 0.45]; H = 3600_000
def sgn(v): return 1 if v >= OOB_HI else (-1 if v <= OOB_LO else 0)
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()
print(f'klines {dts(earliest)} → {dts(latest)}  ·  {len(ends)} windows')


def analyze(end):
    base, ts, ws, _, px = det._setup(end)
    W1 = min(int(ts[-1]), end); W0 = W1 - 168 * H
    def BB(fr, s, L, m): return IC.f_bb(IC.build_source(fr, s), L, m)
    def KK(fr, s, r, st, k): return IC.f_k(IC.build_source(fr, s), r, st, k)
    def AL(v, fr): return IC.align_to_base(v, fr, base)
    at = lambda t: int(np.searchsorted(ts, t, side='right')) - 1
    f7 = IC.resample(base, 420); s14M = AL(BB(f7, 'ohlc4', 74, 0.72), f7)
    f30 = IC.resample(base, 30); t30 = f30['timestamp'].to_numpy() + 30_000
    s30m_b = BB(f30, 'hlc3', 10, 0.40); s30M_b = BB(f30, 'ohlc4', 37, 0.72); s30r_b = KK(f30, 'close', 6, 6, 5)
    hw, lw = [], []
    for i in range(2, len(s30M_b)):
        a, b, c = s30M_b[i-2], s30M_b[i-1], s30M_b[i]
        if a != a or b != b or c != c: continue
        if a >= OOB_HI and c < b < a and s30m_b[i-2] >= OOB_HI and s30r_b[i-2] >= OOB_HI: sd = 1
        elif a <= OOB_LO and c > b > a and s30m_b[i-2] <= OOB_LO and s30r_b[i-2] <= OOB_LO: sd = -1
        else: continue
        tw = int(t30[i]); j = at(tw)
        if j >= 0: (hw if sd == 1 else lw).append((tw, j))
    hw.sort(); lw.sort()
    HT = np.array([t for t, j in hw]); HJ = np.array([j for t, j in hw])
    LT = np.array([t for t, j in lw]); LJ = np.array([j for t, j in lw])
    s6r = AL(KK(IC.resample(base, 360), 'close', 6, 6, 5), IC.resample(base, 360))
    sNmb, tNc = {}, {}
    for N in TFS:
        fr = IC.resample(base, N * 60); sNmb[N] = BB(fr, 'hlc3', 10, 0.4); tNc[N] = fr['timestamp'].to_numpy() + N * 60_000

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

    def ups_for(tf):
        mb, tc = sNmb[tf], tNc[tf]; trigs = []
        for k in range(2, len(mb)):
            a, b, c = mb[k-2], mb[k-1], mb[k]
            if a != a or b != b or c != c: continue
            S = -1 if (b <= OOB_LO and b < a and b < c) else (1 if (b >= OOB_HI and b > a and b > c) else 0)
            if S == 0: continue
            rt = int(tc[k-1]); j = at(rt)
            if j >= 0: trigs.append(dict(t=rt, j=j, s=S, s6r=s6r[j]))
        g = {1: None, -1: None}
        for w in trigs:
            sd = w['s']; ok = (sd == 1 and w['s6r'] > 50) or (sd == -1 and w['s6r'] < 50)
            w['res'] = w['s6r'] if ok else g[sd]
            if ok: g[sd] = w['s6r']
        ups, last = [], {1: None, -1: None}
        for W in trigs:
            S = W['s']; flt = last[S]; last[S] = W
            if sgn(s14M[W['j']]) != S or W['res'] is None or flt is None or not (W0 <= W['t'] <= W1): continue
            fv = s6rext(flt['j'], S)
            call = 0 if abs(W['res'] - fv) <= NEUTRAL_BAND else (1 if W['res'] > fv else -1)
            if call: ups.append((W['j'], call))
        return ups

    def run_tpsl(ups, stop):
        bal = START; n = wins = to = 0; seen = set()
        for (tj, bd) in ups:                              # tj = trigger bar; entry = next aligned wob
            ET, EJ = (HT, HJ) if -bd == 1 else (LT, LJ)
            ei = int(np.searchsorted(ET, int(ts[tj]), side='right'))
            if ei >= len(EJ): continue
            ej = int(EJ[ei])
            if ej in seen: continue
            seen.add(ej); ep = float(px[ej]); fwd = px[ej + 1:]
            tpx = ep * (1 + bd * TP / 100); spx = ep * (1 - bd * stop / 100)
            if bd == 1: tph, slh = np.where(fwd >= tpx)[0], np.where(fwd <= spx)[0]
            else:       tph, slh = np.where(fwd <= tpx)[0], np.where(fwd >= spx)[0]
            ti = tph[0] if len(tph) else None; si = slh[0] if len(slh) else None
            if si is not None and (ti is None or si <= ti): move = -stop
            elif ti is not None: move = TP
            else: move = bd * (float(px[-1]) - ep) / ep * 100; to += 1
            pnl = COINS * ep * (move - FEE_RT) / 100.0
            bal += pnl; n += 1; wins += (pnl > 0)
        return n, wins, round(bal - START, 2), to

    rows = []; wk = dts(W1)
    for tf in TFS:
        ups = ups_for(tf)
        for stop in STOPS:
            rows.append([wk, tf, stop, *run_tpsl(ups, stop)])
    return rows, W1


allrows = []
for end in ends:
    r, w1 = analyze(end); allrows += r
    print(f'  window → {dts(w1)[5:10]} done')
db.execute('DROP TABLE IF EXISTS bias_pk_tpsl_roll')
db.execute('''CREATE TABLE bias_pk_tpsl_roll (pk BIGINT AUTO_INCREMENT PRIMARY KEY, window_end DATETIME,
    trig_tf INT, stop_pct DECIMAL(4,2), trades INT, wins INT, net_usd FLOAT, timeouts INT)''')
db.executemany('INSERT INTO bias_pk_tpsl_roll (window_end,trig_tf,stop_pct,trades,wins,net_usd,timeouts) '
               'VALUES (%s,%s,%s,%s,%s,%s,%s)', allrows)
db.disconnect()

wkeys = sorted({r[0] for r in allrows})
def netv(tf, stop, wk): return next((r[5] for r in allrows if r[0]==wk and r[1]==tf and r[2]==stop), None)
combos = sorted({(r[1], r[2]) for r in allrows})
lb = []
for (tf, stop) in combos:
    vals = [r[5] for r in allrows if r[1] == tf and r[2] == stop]
    lb.append((sum(vals), sum(v > 0 for v in vals), len(vals), tf, stop))
print('\nLEADERBOARD — TP/SL exit, by total net across all windows (TP 0.8, OOB gate)')
print(f'  {"tf":>2} {"stop":>4} | {"total$":>8} {"+wins":>6} {"avg/win":>8}')
best = sorted(lb, reverse=True)[0]
for total, pos, ntot, tf, stop in sorted(lb, reverse=True)[:8]:
    print(f'  {tf:>2} {stop:>4} | {total:>+8.0f} {pos:>3}/{ntot} {total/ntot:>+8.0f}')
bt, bp, bn, btf, bstop = best
print(f'\nWINNER tf{btf}/stop{bstop} — net$ per window:')
print('  ends: ' + ''.join(f'{wk[5:10]:>8}' for wk in wkeys))
print('  net : ' + ''.join(f'{(netv(btf,bstop,wk) or 0):>+8.0f}' for wk in wkeys))
print(f'\n(confluence-exit best was TF6+r = -1423 total, 3/8 windows)')
print(f'→ db table bias_pk_tpsl_roll ({len(allrows)} rows)')
