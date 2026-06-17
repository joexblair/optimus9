"""
bias_pk_validate.py — 96h validation of the s12m-reversal PK machine WITH the s14M OOB gate.

Same machine as bias_pk_pentest.py (s12m reversal = anchor, floater = prev same-side
reversal's s6r trough/peak extreme, neutral band 2.2, side-of-50 s6r) EXCEPT the gate:
a bias state update fires only when s14M is OOB on the anchor's side (the s14M OOB gate,
replacing the debug s14M-vs-50). Floater chain stays UNGATED (s14M disregarded, per spec).

Per gated bias update (long/short/neut), reports:
  - run-up to the adversarial swing  : favourable excursion (bias dir) to the first
                                       counter-bias ZigZag pivot (long→H, short→L) on px_smooth.
  - profit to the next s14M OOB reversal : bias-dir move to when s14M next flips OOB to -S.

configs: s14M BB74|0.72|ohlc4 TF7 · s6r K5|6|6|close TF6 · s12m BB10|0.4|hlc3 TF12 · OOB 85/15.
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
from optimus9.compute.swing_detect import find_pivots

OOB_HI, OOB_LO, NEUTRAL_BAND = 85.0, 15.0, 2.2
def sgn(v): return 1 if v >= OOB_HI else (-1 if v <= OOB_LO else 0)
def fmt(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d %H:%M')

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=96, warmup_hours=80)
base, ts, ws, _, px = det._setup(int(dtm.datetime.now(timezone.utc).timestamp() * 1000))
db.disconnect()
W1 = int(ts[-1]); W0 = W1 - 96 * 3600_000

def bb(fr, src, L, m): return IC.f_bb(IC.build_source(fr, src), L, m)
def kk(fr, src, r, s, k): return IC.f_k(IC.build_source(fr, src), r, s, k)
def al(v, fr): return IC.align_to_base(v, fr, base)

tf7 = IC.resample(base, 420);  s14M = al(bb(tf7, 'ohlc4', 74, 0.72), tf7)
tf6 = IC.resample(base, 360);  s6r = al(kk(tf6, 'close', 6, 6, 5), tf6)
tf12 = IC.resample(base, 720); s12m_b = bb(tf12, 'hlc3', 10, 0.4); t12c = tf12['timestamp'].to_numpy() + 720_000
side14 = np.where(s14M >= OOB_HI, 1, np.where(s14M <= OOB_LO, -1, 0)).astype(np.int8)
bclose = base['close'].to_numpy()
def at(t): return int(np.searchsorted(ts, t, side='right')) - 1

# ── s12m reversals = triggers (double-spikes on); gate = s14M OOB on side S ──
trigs = []
for k in range(2, len(s12m_b)):
    a, b, c = s12m_b[k-2], s12m_b[k-1], s12m_b[k]
    if a != a or b != b or c != c: continue
    S = -1 if (b <= OOB_LO and b < a and b < c) else (1 if (b >= OOB_HI and b > a and b > c) else 0)
    if S == 0: continue
    rt = int(t12c[k-1]); j = at(rt)
    if j < 0: continue
    trigs.append(dict(t=rt, j=j, s=S, s6r=s6r[j], gate=(sgn(s14M[j]) == S)))

good = {1: None, -1: None}                               # side-of-50 s6r resolution
for w in trigs:
    sd = w['s']; ok = (sd == 1 and w['s6r'] > 50.0) or (sd == -1 and w['s6r'] < 50.0)
    w['res'] = w['s6r'] if ok else good[sd]
    if ok: good[sd] = w['s6r']

def s6r_extreme(jr, S):                                  # floater: trough/peak extreme, unbounded to the 50-cross
    bv, bk = s6r[jr], jr
    for step in (-1, +1):
        kk2 = jr
        while 0 <= kk2 + step < len(s6r):
            v = s6r[kk2 + step]
            if v != v: break
            if (S == -1 and v >= 50.0) or (S == 1 and v <= 50.0): break
            kk2 += step
            if (S == 1 and v > bv) or (S == -1 and v < bv): bv, bk = v, kk2
    return bv, bk

v0 = int(np.argmax(~np.isnan(px)))                       # first non-NaN px (skip warmup NaNs)
pivots = sorted((i + v0, k) for i, k in find_pivots(px[v0:], 0.9))
def first_pivot(i0, kind): return next((x for x, kk3 in pivots if x > i0 and kk3 == kind), None)

# ── gated bias updates + metrics (floater = prev same-side reversal, UNGATED) ──
updates = []
last_rev = {1: None, -1: None}
for W in trigs:
    S = W['s']; flt = last_rev[S]; last_rev[S] = W       # chain updates on EVERY reversal (ungated floater)
    if not W['gate'] or W['res'] is None or flt is None: continue
    if not (W0 <= W['t'] <= W1): continue
    anc = W['res']; fv, fk = s6r_extreme(flt['j'], S)
    call = 'NEUT' if abs(anc - fv) <= NEUTRAL_BAND else ('BULL' if anc > fv else 'BEAR')
    bd = 1 if call == 'BULL' else (-1 if call == 'BEAR' else 0)
    je = W['j']; p0 = px[je]
    runup = profit = None
    if bd != 0:
        pk = first_pivot(je, 'H' if bd == 1 else 'L')
        if pk is not None: runup = bd * (px[pk] - p0) / p0 * 100
        opp = np.where(side14[je+1:] == -S)[0]
        jr = je + 1 + int(opp[0]) if len(opp) else len(px) - 1
        profit = bd * (px[jr] - p0) / p0 * 100
    updates.append(dict(t=W['t'], S=S, call=call, bd=bd, runup=runup, profit=profit))

# ── report ──
print(f'96h VALIDATION  window {fmt(W0)} → {fmt(W1)}   (s14M OOB gate)')
print(f'gated bias updates: {len(updates)}  '
      f"(long {sum(u['call']=='BULL' for u in updates)}, "
      f"short {sum(u['call']=='BEAR' for u in updates)}, "
      f"neut {sum(u['call']=='NEUT' for u in updates)})\n")
print(f'  {"time":11} {"side":4} {"call":5} {"run-up":>8} {"profit→s14Mrev":>14}')
for u in updates:
    ru = f'{u["runup"]:+.2f}%' if u['runup'] is not None else '  —'
    pf = f'{u["profit"]:+.2f}%' if u['profit'] is not None else '  —'
    print(f'  {fmt(u["t"]):11} {("HI" if u["S"]==1 else "LO"):4} {u["call"]:5} {ru:>8} {pf:>14}')

def stats(rows, key):
    v = np.array([r[key] for r in rows if r[key] is not None])
    return ('n=0' if not len(v) else
            f'n={len(v):2d}  median {np.median(v):+5.2f}%  mean {v.mean():+5.2f}%  hit {(v>0).mean()*100:3.0f}%')
print()
for label, sel in (('LONG ', 'BULL'), ('SHORT', 'BEAR')):
    rows = [u for u in updates if u['call'] == sel]
    print(f'  {label}  run-up: {stats(rows,"runup")}')
    print(f'         profit: {stats(rows,"profit")}')
dirn = [u for u in updates if u['bd'] != 0]
print(f'  ALL-DIR run-up: {stats(dirn,"runup")}')
print(f'          profit: {stats(dirn,"profit")}')
