"""THE CHAIN, corrected. Joe 1007: *"I meant for ws2Mage momentum detection as a one-time thing to
kickstart the established lineage walk"*.

TWO CORRECTIONS from _chain2.py:
  1. ONE-TIME KICKSTART. The momentum read picks the STARTING rider at the arm. After that the
     ESTABLISHED lineage walk owns the rider: the baton moves only on an oob crossing within
     LIN_HOP. _chain2 re-read momentum on every bar while ws2Mage was oob and walked the rider up
     on mom-true alone - on leg 1 that moved the tag ws1 -> ws3 FIVE SECONDS after ws1 became
     rider, so ws1's stall at 04:41:00 never fired and +0.9501 became +0.5186.
  2. THE STALL IS NOT SUPPRESSED. Joe said to stash the X-CROSS. _chain2 also withheld the stall
     until the first ib confirmation, which he never asked for. The stall now fires whenever it
     prints, as it does in the established walk.

THE STASH IS UNCHANGED: an x-cross while ws2Mage is oob is recorded, not acted on; at the ib bar
(confirmed over IB_WOB bars) it fires only if there is no momentum at or above the rider.
"""
import os, io, contextlib, sys
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

D, START, FIRST = '2026-09-25', '02:48:50', 1
SHOW = tuple(range(1, 8))
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
NEED = sorted(set(LIN_TF) | {13, 14})
R = {t: SC.LD(t * 60, 'r') for t in NEED}
X = {t: SC.LD(t * 60, 'x') for t in LIN_TF}
M2 = SC.Mg[2]; PX = SC.PX
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
def mt(t, k, d):
    key = (t, k, d)
    if key in _mt: return _mt[key]
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            v = momo_g_why(SC.Rl[t], int(d), int(k))[0] in ('momo', 'curl')
    _mt[key] = v; return v
_P('producers ready')
def band(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'O' if v >= SC.HI else ('x' if v >= EXF_HI else '.')
    return 'O' if v <= SC.LO else ('x' if v <= EXF_LO else '.')
oobf = lambda t, k, d: (float(R[t][k]) >= SC.HI) if d > 0 else (float(R[t][k]) <= SC.LO)
m2oob = lambda k, d: (float(M2[k]) >= SC.HI) if d > 0 else (float(M2[k]) <= SC.LO)
def xcond(h, k, d):
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return False
    xv = float(X[h][k])
    c = (xv < float(R[t1][k]) and xv < float(R[t2][k])) if d > 0 else \
        (xv > float(R[t1][k]) and xv > float(R[t2][k]))
    return c and band(t1, k, d) == '.' and band(t2, k, d) == '.'
def arm_bar(k_from, d):
    for k in range(k_from + 1, SC.TAPE_LAST + 1):
        if d > 0 and float(M2[k]) >= SC.HI and float(M2[k - 1]) < SC.HI: return k
        if d < 0 and float(M2[k]) <= SC.LO and float(M2[k - 1]) > SC.LO: return k
    return None

def run_leg(k, d, ib_wob, stash_on):
    tr = []; a = arm_bar(k, d)
    if a is None: return None, 'no arm', tr
    tr.append((a, 'exit-armed — ws2Mage %s %.0f (%.2f)'
               % ('over' if d > 0 else 'under', SC.HI if d > 0 else SC.LO, float(M2[a]))))
    rider = None; stash = None; ib_run = 0
    for j in range(a, SC.TAPE_LAST + 1):
        if rider is None:
            # ONE-TIME KICKSTART: the highest oob line. After this the established walk owns it.
            c = [t for t in LIN_TF if oobf(t, j, d)]
            if c:
                rider = max(c)
                tr.append((j, 'KICKSTART — rider ws%d (r %.2f oob). Established walk takes over.'
                           % (rider, float(R[rider][j]))))
            continue
        cand = [t for t in range(rider + 1, min(rider + LIN_HOP, LIN_TF[-1]) + 1) if oobf(t, j, d)]
        if cand:
            rider = max(cand); stash = None
            tr.append((j, 'baton -> ws%d oob (r %.2f)' % (rider, float(R[rider][j])))); continue
        if ST[(rider, d)][j]:
            tr.append((j, 'final stalled on ws%d (r %.2f %s)'
                       % (rider, float(R[rider][j]), band(rider, j, d))))
            return j, 'final stalled', tr
        xc = xcond(rider, j, d)
        if not stash_on:
            if xc: return j, 'x-cross', tr
            continue
        if m2oob(j, d):
            ib_run = 0
            if xc and stash is None:
                stash = j
                tr.append((j, 'x-cross STASHED on ws%d (ws2Mage %.2f oob)' % (rider, float(M2[j]))))
            continue
        ib_run += 1
        if ib_run == ib_wob:
            live = any(mt(t, j, d) for t in LIN_TF if t >= rider)
            tr.append((j, 'ws2Mage ib confirmed (%d bars) — momentum at/above ws%d: %s'
                       % (ib_wob, rider, 'YES' if live else 'NO')))
            if stash is not None and not live:
                tr.append((j, 'stashed x-cross (from %s) FIRES' % SC.U(stash)))
                return j, 'stashed x-cross', tr
        if ib_run >= ib_wob and xc:
            return j, 'x-cross', tr
    return None, 'tape end', tr

def box(hdr, rows):
    """Joe's boxed report: one record per row, columns centred in the header."""
    w = [max(len(hdr[i]), max((len(str(r[i])) for r in rows), default=0)) for i in range(len(hdr))]
    L = lambda l, m, r: l + m.join('─' * (x + 2) for x in w) + r
    print(L('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('├', '┼', '┤'))
    for r in rows:
        print('│' + '│'.join(' ' + str(r[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('└', '┴', '┘'))

def chain(ib_wob, stash_on, show=()):
    k = SC.K('%s %s' % (D, START)); d = FIRST; out = []
    for leg in range(1, 41):
        xk, why, tr = run_leg(k, d, ib_wob, stash_on)
        if xk is None: break
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        real = (float(PX[xk]) - p0) / p0 * 100.0 * sgn
        pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
        mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
        if leg in show:
            print('\n## LEG %d — %s   open %s   pxs %.6f'
                  % (leg, 'LONG' if d > 0 else 'SHORT', SC.U(k), p0))
            rows = [(SC.U(k), '+0.0', 'OPEN %s' % ('LONG' if d > 0 else 'SHORT'),
                     '%.6f' % p0, '+0.0000')]
            rows += [(SC.U(j), mn(j), lbl, '%.6f' % float(PX[j]), pct(j)) for j, lbl in tr]
            rows += [(SC.U(xk), mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]), pct(xk))]
            box(('ts', '+min', 'event', 'pxs', 'pct'), rows)
        out.append(dict(leg=leg, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk,
                        real=real, why=why))
        k = xk; d = -d
    return out

print('\n# A/B — one-time kickstart, stall never suppressed')
ab = []
for lbl, wob, son in (('no stash (x-cross fires at once)', 6, False),
                      ('stash, ib wob 6', 6, True),
                      ('stash, ib wob 12', 12, True)):
    L = chain(wob, son)
    ab.append((lbl, str(len(L)), str(sum(1 for x in L if x['real'] > 0)),
               '%+.4f' % sum(x['real'] for x in L[:6]),
               '%+.4f' % sum(x['real'] for x in L[:7]),
               '%+.4f' % sum(x['real'] for x in L)))
box(('variant', 'legs', 'positive', 'legs 1-6', 'legs 1-7', 'total realised'), ab)

print('\n# THE 7 LEGS — stash, ib wob 6')
L = chain(6, True, show=SHOW)
print()
box(('leg', 'side', 'open', 'exit', 'hold min', 'realised', 'why'),
    [(str(r['leg']), r['side'], SC.U(r['open']), SC.U(r['exit']),
      '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0),
      '%+.4f' % r['real'], r['why']) for r in L[:7]]
    + [('all 7', '', SC.U(L[0]['open']), SC.U(L[6]['exit']),
        '%.1f' % sum((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0 for r in L[:7]),
        '%+.4f' % sum(r['real'] for r in L[:7]), '')])
print('\n# THE WHOLE CHAIN (%d legs)' % len(L))
box(('legs', 'positive', 'total realised'),
    [(str(len(L)), str(sum(1 for r in L if r['real'] > 0)),
      '%+.4f' % sum(r['real'] for r in L))])
