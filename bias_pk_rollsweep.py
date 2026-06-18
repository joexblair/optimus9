"""
bias_pk_rollsweep.py — rolling-window robustness of the bias-machine sweeps.

7-day windows, overlapping by 2 days (5-day step), back as far as klines exist. Per window
runs BOTH sweeps: (1) trigger TF 4..12 (exit fixed s6m+s6r), (2) exit TF 4..12 (trigger fixed
s12m). x exit {no-r / +r} x gate {s14M OOB / vs50}. 33K lots · fees · tracks eod (un-exited).
Writes db table bias_pk_rollsweep; prints per-window TF6 trace + a robustness leaderboard.
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
COINS, START, FEE_RT = 33_000, 1000.0, 0.11
TFS = list(range(4, 13))
H = 3600_000
def sgn(v): return 1 if v >= OOB_HI else (-1 if v <= OOB_LO else 0)
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')
def dd(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d')

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80)
tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
db.disconnect()

ends = []; e = latest
while e - (168 + 80) * H >= earliest:                    # need 7d window + 80h warmup of klines
    ends.append(e); e -= 120 * H                         # step back 5 days
ends.reverse()
print(f'klines {dts(earliest)} → {dts(latest)}  ·  {len(ends)} windows (7d, 5d step)')


def analyze(end):
    det2 = BLDetect(db2, lookback_hours=168, warmup_hours=80)
    base, ts, ws, _, px = det2._setup(end)
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
    sNmb, tNc, MS, RS = {}, {}, {}, {}
    for N in TFS:
        fr = IC.resample(base, N * 60)
        mb = BB(fr, 'hlc3', 10, 0.4); sNmb[N] = mb; tNc[N] = fr['timestamp'].to_numpy() + N * 60_000
        ma = AL(mb, fr); ra = AL(KK(fr, 'close', 6, 6, 5), fr)
        MS[N] = np.where(ma >= OOB_HI, 1, np.where(ma <= OOB_LO, -1, 0))
        RS[N] = np.where(ra >= OOB_HI, 1, np.where(ra <= OOB_LO, -1, 0))
    s6r = AL(KK(IC.resample(base, 360), 'close', 6, 6, 5), IC.resample(base, 360))

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

    def trigs_for(tf):
        mb, tc = sNmb[tf], tNc[tf]; out = []
        for k in range(2, len(mb)):
            a, b, c = mb[k-2], mb[k-1], mb[k]
            if a != a or b != b or c != c: continue
            S = -1 if (b <= OOB_LO and b < a and b < c) else (1 if (b >= OOB_HI and b > a and b > c) else 0)
            if S == 0: continue
            rt = int(tc[k-1]); j = at(rt)
            if j >= 0: out.append(dict(t=rt, j=j, s=S, s6r=s6r[j]))
        g = {1: None, -1: None}
        for w in out:
            sd = w['s']; ok = (sd == 1 and w['s6r'] > 50) or (sd == -1 and w['s6r'] < 50)
            w['res'] = w['s6r'] if ok else g[sd]
            if ok: g[sd] = w['s6r']
        return out

    def ups_for(trigs, gate):
        ups, last = [], {1: None, -1: None}
        for W in trigs:
            S = W['s']; flt = last[S]; last[S] = W
            ok = (sgn(s14M[W['j']]) == S) if gate == 'oob' else ((s14M[W['j']] > 50) == (S == 1))
            if not ok or W['res'] is None or flt is None or not (W0 <= W['t'] <= W1): continue
            fv = s6rext(flt['j'], S)
            call = 0 if abs(W['res'] - fv) <= NEUTRAL_BAND else (1 if W['res'] > fv else -1)
            if call: ups.append((W['t'], call))
        return ups

    def run(ups, er, ms, rs):
        bal = START; n = wins = eod = 0; seen = set()
        for (t_up, bd) in ups:
            ET, EJ = (HT, HJ) if -bd == 1 else (LT, LJ)
            ei = int(np.searchsorted(ET, t_up, side='right'))
            if ei >= len(EJ): continue
            ej = int(EJ[ei]); et = int(ET[ei])
            if ej in seen: continue
            seen.add(ej)
            XT, XJ = (HT, HJ) if bd == 1 else (LT, LJ)
            xi = int(np.searchsorted(XT, et, side='right')); xj = None
            while xi < len(XJ):
                jj = int(XJ[xi])
                if ms[jj] == bd and (not er or rs[jj] == bd): xj = jj; break
                xi += 1
            if xj is None: eod += 1; xj = len(px) - 1
            ep, xp = float(px[ej]), float(px[xj])
            pnl = COINS * ep * (bd * (xp - ep) / ep * 100 - FEE_RT) / 100.0
            bal += pnl; n += 1; wins += (pnl > 0)
        return n, wins, round(bal - START, 2), eod

    rows = []; wk = dts(W1)
    for tf in TFS:
        tg = trigs_for(tf)
        for gate in ('oob', 'vs50'):
            up = ups_for(tg, gate)
            for er in (0, 1):
                rows.append([wk, 'trigger', tf, er, gate, *run(up, er, MS[6], RS[6])])
    tg6 = trigs_for(6)                                   # exit sweep: trigger FIXED at TF6 (the structural pick)
    for gate in ('oob', 'vs50'):
        up = ups_for(tg6, gate)
        for tf in TFS:
            for er in (0, 1):
                rows.append([wk, 'exit', tf, er, gate, *run(up, er, MS[tf], RS[tf])])
    return rows, W1


db2 = DatabaseManager(**get_db_config()); db2.connect()
allrows = []
for end in ends:
    r, w1 = analyze(end)
    allrows += r
    print(f'  window → {dd(w1)}  done ({len(r)} configs)')
db2.execute('DROP TABLE IF EXISTS bias_pk_rollsweep')
db2.execute('''CREATE TABLE bias_pk_rollsweep (pk BIGINT AUTO_INCREMENT PRIMARY KEY, window_end DATETIME,
    sweep VARCHAR(8), tf_min INT, exit_has_r TINYINT, gate_mode VARCHAR(6),
    trades INT, wins INT, net_usd FLOAT, eod_exits INT)''')
db2.executemany('INSERT INTO bias_pk_rollsweep (window_end,sweep,tf_min,exit_has_r,gate_mode,trades,wins,net_usd,eod_exits) '
                'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', allrows)
db2.disconnect()

wins_cols = sorted({r[0] for r in allrows})
def net(sweep, tf, er, gate, wk): return next((r[7] for r in allrows if r[0]==wk and r[1]==sweep and r[2]==tf and r[3]==er and r[4]==gate), None)

print(f'\nTRIGGER sweep · OOB gate · TF6 — net$ per window (window end mmdd):')
print('  ends:    ' + ''.join(f'{wk[5:10]:>8}' for wk in wins_cols))
print('  TF6 no-r:' + ''.join(f'{(net("trigger",6,0,"oob",wk) or 0):>+8.0f}' for wk in wins_cols))
print('  TF6  +r :' + ''.join(f'{(net("trigger",6,1,"oob",wk) or 0):>+8.0f}' for wk in wins_cols))

# robustness leaderboard: total net across windows + #positive windows (trigger sweep)
def leaderboard(sw, title):
    print(f'\nLEADERBOARD — {title}, total net across all windows')
    print(f'  {"tf":>2} {"r":>1} {"gate":>4} | {"total$":>8} {"+wins":>6} {"avg/win":>8}')
    combos = sorted({(r[2], r[3], r[4]) for r in allrows if r[1] == sw})
    lb = []
    for (tf, er, gate) in combos:
        vals = [r[7] for r in allrows if r[1] == sw and r[2] == tf and r[3] == er and r[4] == gate]
        lb.append((sum(vals), sum(v > 0 for v in vals), len(vals), tf, er, gate))
    top = sorted(lb, reverse=True)
    for total, pos, ntot, tf, er, gate in top[:8]:
        print(f'  {tf:>2} {er:>1} {gate:>4} | {total:>+8.0f} {pos:>3}/{ntot} {total/ntot:>+8.0f}')
    return top[0]
leaderboard('trigger', 'TRIGGER sweep (exit fixed s6m+s6r)')
best = leaderboard('exit', 'EXIT sweep (trigger fixed TF6)')
bt, bp, bn, btf, ber, bg = best
print(f'\nEXIT-sweep winner  exitTF{btf} r{ber} {bg} — net$ per window:')
print('  ends: ' + ''.join(f'{wk[5:10]:>8}' for wk in wins_cols))
print('  net : ' + ''.join(f'{(net("exit",btf,ber,bg,wk) or 0):>+8.0f}' for wk in wins_cols))
print(f'\n→ db table bias_pk_rollsweep ({len(allrows)} rows, {len(ends)} windows)')
