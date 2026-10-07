"""THE EXIT A/B — `final stalled` vs Joe's x-cross, across every `no r block` trade.

JOE'S RULINGS, 1007:
  the gate     *"run the simpler fix - it's sound logic"* -> the x-cross condition applies ONLY to a
               tag holder that ACTUALLY CROSSED oob. ws1 takes the tag on momentum and never reached
               oob, so it is not eligible. Measured on 09-25: without the gate the condition fired on
               ws1 at 19:49:00, 56.8 min before ws11 held the tag and before the trade even opened.
  the cross    *"my view is literal: ws{oob tag holder tf}x crossing ws{tf+1 and tf+2}r"* - ONE x
               line, TWO r targets. dr +1 crosses UNDER, dr -1 crosses OVER.
  in-fence     both targets must be in-fence (r below the 83/17 ex-fence on the dr side).
  `oob`        means the TAG HOLDER. It need not still be oob at the cross - on 09-25 ws11r was
               95.48 at 20:45:45 and 81.19 at 20:46:00, so r-still-oob and x-under-r never overlap.
  the wob      *"that's up for decision - an AB across the 44 trades is needed"* -> the conjunction
               is tested at wob 1, 2 and 3 CONSECUTIVE bars, reported, not chosen.

ws13 AND ws14 ARE OUTSIDE THE LINEAGE BAND (ws1..ws12) and are loaded anyway: holder+2 from ws11
reaches ws13 and from ws12 reaches ws14, and the condition is literal about holder+1 and holder+2.
Joe 1007 parked the question of what ws13 does to the mech until after this A/B. The BATON still
clamps at ws12 - only the x-cross targets look higher.

MOMENTUM IS READ ON dr, NEVER ON trade_side. The backstop is the only thing that reads the side.
"""
import os, io, contextlib, re, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window, momo_g_why
from optimus9.analysis.jig import stall_mask
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%6.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('score39 ready')

OPEN_GRADES = ('with-trend', 'no r block')
TRADE = 'no r block'
MFE_CAPTURE, MAE_CAP = 0.75, 0.95
WOBS = (1, 2, 3)
DAYS = os.environ.get('LG_DAYS',
    '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
    '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
LIN_TF = SC.TF
LIN_HOP = int(SC.LG['lin_hop'])
EXF_HI = 100.0 - float(SC.LG['momo_fence_r'])     # 83.0
EXF_LO = float(SC.LG['momo_fence_r'])             # 17.0
NEED_R = sorted(set(LIN_TF) | {LIN_TF[-1] + 1, LIN_TF[-1] + 2})
R = {t: SC.LD(t * 60, 'r') for t in NEED_R}
X = {t: SC.LD(t * 60, 'x') for t in LIN_TF}
PX = SC.PX
_P('r ws1..ws%d, x ws1..ws%d' % (NEED_R[-1], LIN_TF[-1]))

db = DatabaseManager(**get_db_config()); db.connect()
BANK = {t: momo_bank(db, t) for t in LIN_TF}; db.disconnect()
ST = {}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            step, samples = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for dd in (-1, +1):
        ST[(t, dd)] = stall_mask(SC.Rl[t], dd, int(SC.LG['stall_n']), step, samples)
_P('stall masks built')
_mt = {}
def mt1(k, d):
    key = (k, d)
    if key in _mt: return _mt[key]
    with momo_config(BANK[1]):
        with momo_window(int(BANK[1]['k_window']) * 1):
            v = momo_g_why(SC.Rl[1], int(d), int(k))[0] in ('momo', 'curl')
    _mt[key] = v; return v

def oob(t, k, d):
    v = float(R[t][k])
    return (v >= SC.HI) if d > 0 else (v <= SC.LO)
def infence(t, k, d):
    v = float(R[t][k])
    return (v < EXF_HI) if d > 0 else (v > EXF_LO)
def xcond(h, k, d):
    """ws{h}x crosses UNDER ws{h+1}r and ws{h+2}r (dr +1), both in-fence."""
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return False
    xv = float(X[h][k])
    if d > 0:
        c = xv < float(R[t1][k]) and xv < float(R[t2][k])
    else:
        c = xv > float(R[t1][k]) and xv > float(R[t2][k])
    return c and infence(t1, k, d) and infence(t2, k, d)

def walk(k_start, d, side, mode, wob):
    """mode 'stall' or 'xcross'. -> (exit_k, why, holder, chain)"""
    back = -1 if side == 'LONG' else +1
    prev = int(SC.DRv[k_start]); holder = None; chain = []; qual = False; run = 0
    for k in range(k_start, SC.TAPE_LAST + 1):
        dk = int(SC.DRv[k])
        if dk == back and prev != back: return k, 'dr backstop', holder, chain
        prev = dk
        if holder is None:
            if mt1(k, d): holder, qual = LIN_TF[0], False; chain = [(k, holder)]
            continue
        cand = [t for t in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1) if oob(t, k, d)]
        if cand:
            holder, qual, run = max(cand), True, 0      # arrived BY crossing oob -> eligible
            chain.append((k, holder)); continue
        if mode == 'xcross':
            if qual and xcond(holder, k, d):
                run += 1
                if run >= wob: return k, 'x-cross', holder, chain
            else: run = 0
        if ST[(holder, d)][k]: return k, 'final stalled', holder, chain
    return None, 'tape end', holder, chain

sigs = []
for day in DAYS:
    p = os.path.join('octosig', '%s.out' % day)
    if not os.path.exists(p): continue
    for ln in open(p):
        if not ln.startswith('R|'): continue
        f = ln.rstrip('\n').split('|')
        if len(f) < 7 or not re.match(r'^\d\d:\d\d:\d\d$', f[2]): continue
        k = SC.K('%s %s' % (day, f[2])); d = int(SC.DRv[k])
        if d == 0: continue
        r = SC.classify(k, f[2]); D = r.get('D') or {}
        ex = int(r['m']['ex']) if r['m'].get('ex') is not None else k
        g = D.get('why') if D.get('why') == 'no r block' else r['grade']
        sigs.append(dict(day=day, sig=f[2], k=k, open_k=max(k, int(r['kw']), ex), dr=d, grade=g,
                         openable=(g in OPEN_GRADES)))
sigs.sort(key=lambda x: x['k'])
arms = [s for s in sigs if not s['openable']]
trades = [s for s in sigs if s['grade'] == TRADE]
_P('%d octo-sigs, %d trades' % (len(sigs), len(trades)))

VAR = [('stalled', 'stall', 0)] + [('x-cross wob%d' % w, 'xcross', w) for w in WOBS]
res = {v[0]: [] for v in VAR}
rows = []
for i, t in enumerate(trades):
    side = 'LONG' if t['dr'] > 0 else 'SHORT'
    arm = next((s for s in arms if s['k'] > t['open_k']), None)
    p0 = float(PX[t['open_k']])
    row = dict(day=t['day'], sig=t['sig'], side=side, arm=arm['sig'] if arm else None)
    for lbl, mode, wob in VAR:
        if arm is None: row[lbl] = (None, 'no exit-armed', None); continue
        xk, why, holder, chain = walk(arm['k'], t['dr'], side, mode, wob)
        real = None if xk is None else (float(PX[xk]) - p0) / p0 * 100.0 * (1 if side == 'LONG' else -1)
        row[lbl] = (xk, why, holder)
        if real is not None:
            res[lbl].append(dict(day=t['day'], sig=t['sig'], real=real, why=why, holder=holder,
                                 hold=(int(SC.ts[xk]) - int(SC.ts[t['open_k']])) / 60000.0))
    rows.append(row)
    _P('  %2d/%d %s %s' % (i + 1, len(trades), t['day'], t['sig']))

print('\n# THE EXIT A/B — %d `no r block` trades, opened towards dr   %s' % (len(trades), SC.LG_KEY))
print('# x-cross gated on the tag holder having CROSSED oob (Joe 1007)')
print('\n| variant | trades exited | sum REALISED | mean per trade | positive | median hold min |')
print('|---|---|---|---|---|---|')
for lbl, _m, _w in VAR:
    g = res[lbl]
    if not g: print('| %s | 0 | — | — | — | — |' % lbl); continue
    h = sorted(x['hold'] for x in g)
    print('| %s | %d | %+.3f | %+.4f | %d of %d | %.1f |'
          % (lbl, len(g), sum(x['real'] for x in g), sum(x['real'] for x in g) / len(g),
             sum(1 for x in g if x['real'] > 0), len(g), h[len(h) // 2]))

print('\n# WHY EACH VARIANT ENDED')
print('| variant | final stalled | x-cross | dr backstop | tape end |'); print('|---|---|---|---|---|')
for lbl, _m, _w in VAR:
    g = res[lbl]
    c = lambda w: sum(1 for x in g if x['why'] == w)
    print('| %s | %d | %d | %d | %d |' % (lbl, c('final stalled'), c('x-cross'),
                                          c('dr backstop'), c('tape end')))

print('\n# PER TRADE — exit bar and realised, every variant')
hdr = '| day | open | side | exit-armed |'
for lbl, _m, _w in VAR: hdr += ' %s bar | %s real |' % (lbl, lbl)
print(hdr); print('|---' * (4 + 2 * len(VAR)) + '|')
for r in rows:
    line = '| %s | %s | %s | %s |' % (r['day'], r['sig'], r['side'], r['arm'] or '—')
    for lbl, _m, _w in VAR:
        xk, why, holder = r[lbl]
        g = next((x for x in res[lbl] if x['day'] == r['day'] and x['sig'] == r['sig']), None)
        line += ' %s | %s |' % (SC.U(xk) if xk is not None else '—',
                                ('%+.4f' % g['real']) if g else '—')
    print(line)

print('\n# PER DAY, REALISED')
hd = '| day | trades |'
for lbl, _m, _w in VAR: hd += ' %s |' % lbl
print(hd); print('|---' * (2 + len(VAR)) + '|')
for d in sorted({r['day'] for r in rows}):
    line = '| %s | %d |' % (d, sum(1 for r in rows if r['day'] == d))
    for lbl, _m, _w in VAR:
        s = sum(x['real'] for x in res[lbl] if x['day'] == d)
        line += ' %+.3f |' % s
    print(line)
