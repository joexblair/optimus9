"""Does the lineage CLIMB on the winners and stay on ws1 on the losers? All 45 trades.

Both failures walked so far (09-26 12:18:00, 09-28 09:52:00) ended with holder ws1 and ZERO baton
passes - nothing ever crossed oob. This measures that across the whole population instead of
inferring it from two cases, and walks 09-30 15:28:35 (realised -2.6631) as the third example.
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
_P('ready')

OPEN_GRADES = ('with-trend', 'no r block'); TRADE = 'no r block'
DAYS = ('2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
        '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
R = {t: SC.Rl[t] for t in LIN_TF}; PX = SC.PX
db = DatabaseManager(**get_db_config()); db.connect()
BANK = {t: momo_bank(db, t) for t in LIN_TF}; db.disconnect()
ST = {}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for dd in (-1, +1):
        ST[(t, dd)] = stall_mask(SC.Rl[t], dd, int(SC.LG['stall_n']), s_, n_)
_mt = {}
def mt1(k, d):
    key = (k, d)
    if key in _mt: return _mt[key]
    with momo_config(BANK[1]):
        with momo_window(int(BANK[1]['k_window']) * 1):
            v = momo_g_why(SC.Rl[1], int(d), int(k))[0] in ('momo', 'curl')
    _mt[key] = v; return v
_P('producers ready')
oobf = lambda t, k, d: (float(R[t][k]) >= SC.HI) if d > 0 else (float(R[t][k]) <= SC.LO)

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
_P('%d trades' % len(trades))

out = []
for t in trades:
    side = 'LONG' if t['dr'] > 0 else 'SHORT'
    arm = next((s for s in arms if s['k'] > t['open_k']), None)
    if arm is None: continue
    back = -1 if side == 'LONG' else +1
    prev = int(SC.DRv[arm['k']]); holder = None; chain = []; xk = None; why = None
    for k in range(arm['k'], SC.TAPE_LAST + 1):
        dk = int(SC.DRv[k])
        if dk == back and prev != back: xk, why = k, 'dr backstop'; break
        prev = dk
        if holder is None:
            if mt1(k, t['dr']): holder = LIN_TF[0]; chain = [(k, holder)]
            continue
        cand = [tt for tt in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1)
                if oobf(tt, k, t['dr'])]
        if cand:
            holder = max(cand); chain.append((k, holder)); continue
        if ST[(holder, t['dr'])][k]: xk, why = k, 'final stalled'; break
    if xk is None: continue
    p0 = float(PX[t['open_k']])
    real = (float(PX[xk]) - p0) / p0 * 100.0 * (1 if side == 'LONG' else -1)
    out.append(dict(day=t['day'], sig=t['sig'], side=side, passes=max(0, len(chain) - 1),
                    top=(chain[-1][1] if chain else None), real=real, why=why,
                    hold=(int(SC.ts[xk]) - int(SC.ts[t['open_k']])) / 60000.0))

print('\n# DOES THE LINEAGE CLIMB? %d trades' % len(out))
print('| baton passes | trades | sum realised | mean per trade | positive | median hold min |')
print('|---|---|---|---|---|---|')
for lo, hi, lbl in ((0, 0, '0 - never left ws1'), (1, 2, '1-2'), (3, 5, '3-5'), (6, 99, '6+')):
    g = [x for x in out if lo <= x['passes'] <= hi]
    if not g: print('| %s | 0 | — | — | — | — |' % lbl); continue
    h = sorted(x['hold'] for x in g)
    print('| %s | %d | %+.3f | %+.4f | %d of %d | %.1f |'
          % (lbl, len(g), sum(x['real'] for x in g), sum(x['real'] for x in g) / len(g),
             sum(1 for x in g if x['real'] > 0), len(g), h[len(h) // 2]))

print('\n# BY THE TOP TF THE LINEAGE REACHED')
print('| top TF | trades | sum realised | mean per trade | positive |')
print('|---|---|---|---|---|')
for tf in sorted({x['top'] for x in out if x['top']}):
    g = [x for x in out if x['top'] == tf]
    print('| ws%d | %d | %+.3f | %+.4f | %d of %d |'
          % (tf, len(g), sum(x['real'] for x in g), sum(x['real'] for x in g) / len(g),
             sum(1 for x in g if x['real'] > 0), len(g)))

print('\n# EVERY TRADE, sorted by realised')
print('| day | open | side | baton passes | top TF | hold min | why | realised |')
print('|---|---|---|---|---|---|---|---|')
for x in sorted(out, key=lambda z: z['real']):
    print('| %s | %s | %s | %d | %s | %.1f | %s | %+.4f |'
          % (x['day'], x['sig'], x['side'], x['passes'],
             ('ws%d' % x['top']) if x['top'] else '—', x['hold'], x['why'], x['real']))
