"""MEASUREMENT A — the x-cross exit's delay from the target pivot, per rider TF, across 12 days.

JOE 1007: *"leg 8 exit shows us that the higher x-crosses carry unacceptable delay (from the target
pivot)"* -> *"the delay, per rider TF"*.

THE POPULATION: chains seeded on the 53 sanctioned `with-trend` octo-sigs, run with the CURRENT mech
so every leg comes from one build:
  one-time KICKSTART, established lineage walk, baton on an oob crossing within LIN_HOP
  Joe's ws12r ceiling rule, PER LEG: ws12r crossing into oob extends the ceiling to ws23
  exits: x-cross | final stalled | target-dr sanctioned octo-sig | MAE breach (chain stops)
  THE STASH IS OFF - Joe put it in limbo.

NO DAY BOUND. The tape is CONTIGUOUS - 1,632,960 bars x 5 s from 07-02 12:00:00 to 10-04 23:59:55 -
so the day-end bound in _chain_os.py was an invented truncation. Removed. A chain now ends only on
the MAE breach or at the tape end, which means a chain may run past midnight and swallow seeds that
previously started their own chain.

THE TARGET PIVOT: swing_detect find_pivots at the BANKED `swing` 1.25 - the first FAVOURABLE pivot
after the leg's open (an H for a LONG leg, an L for a SHORT one). Joe 1006 flagged swing_detect as
*"a BACKTEST RULER, not a causal tool"*, so it measures the delay and cannot sit inside a mech.
The leg's own MFE bar is printed beside it - unambiguous, and independent of the swing size.
"""
import os, io, contextlib, sys, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window
from optimus9.compute.swing_detect import find_pivots
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

MAE_STOP = float(os.environ.get('MAE_STOP', '1.1'))
CEIL_TRIG_TF, CEIL_HI = 12, 23
KNOB = ('lazy_g_config.v1|gcws30Mage|flip-towards+norblock|stamp-resolved|'
        'routing-banked|lineage-ws1|mtdwalk-drguard')
GRADES = ('with-trend',)
LIN_HOP = int(SC.LG['lin_hop']); BASE_HI = SC.TF[-1]
SWING = float(SC.LG['swing'])
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
N = len(SC.ts)
ALL_TF = list(range(SC.TF[0], CEIL_HI + 1))
RL = {t: SC.LD(t * 60, 'r') for t in range(SC.TF[0], CEIL_HI + 3)}
R = {t: RL[t][:N] for t in RL}
X = {t: SC.LD(t * 60, 'x')[:N] for t in ALL_TF}
M2 = SC.Mg[2][:N]; PX = SC.PX[:N]
PIV = find_pivots(PX, SWING)
HS = np.array([p for p, kk in PIV if kk == 'H']); LS = np.array([p for p, kk in PIV if kk == 'L'])
_P('tape %d bars, swing %.2f -> %d H and %d L pivots' % (N, SWING, HS.size, LS.size))

db = DatabaseManager(**get_db_config()); db.connect()
SIG = db.execute("SELECT os_day, os_ts, os_dr FROM octosig_rulings WHERE os_knob_key=%s "
                 "AND os_grade IN (" + ','.join(['%s'] * len(GRADES)) + ") ORDER BY os_day, os_ts",
                 (KNOB,) + GRADES, fetch=True)
BANK = {t: momo_bank(db, t) for t in ALL_TF}
db.disconnect()
SANC = {}; SEEDS = []
for r in SIG:
    k = SC.K('%s %s' % (r['os_day'], r['os_ts']))
    if k is None or k >= N: continue
    SANC[k] = int(r['os_dr']); SEEDS.append((k, int(r['os_dr']), str(r['os_day']), r['os_ts']))
SEEDS.sort()
ST = {}
for t in ALL_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for dd in (-1, +1):
        ST[(t, dd)] = stall_mask(RL[t], dd, int(SC.LG['stall_n']), s_, n_)
_P('producers ready; %d seeds, riders ws%d..ws%d' % (len(SEEDS), ALL_TF[0], ALL_TF[-1]))

def bnd(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'O' if v >= SC.HI else ('x' if v >= EXF_HI else '.')
    return 'O' if v <= SC.LO else ('x' if v <= EXF_LO else '.')
oobf = lambda t, k, d: (float(R[t][k]) >= SC.HI) if d > 0 else (float(R[t][k]) <= SC.LO)
def xcond(h, k, d):
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return False
    xv = float(X[h][k])
    c = (xv < float(R[t1][k]) and xv < float(R[t2][k])) if d > 0 else \
        (xv > float(R[t1][k]) and xv > float(R[t2][k]))
    return c and bnd(t1, k, d) == '.' and bnd(t2, k, d) == '.'

def run_leg(k0, d):
    """-> dict for one leg."""
    p0 = float(PX[k0]); sgn = 1 if d > 0 else -1
    armed = False; rider = None; mae = 0.0; ceil = BASE_HI; ceil_bar = None
    for j in range(k0 + 1, N):
        px = float(PX[j])
        if np.isfinite(px) and px > 0:
            adv = -((px - p0) / p0 * 100.0 * sgn)
            if adv > mae: mae = adv
            if adv > MAE_STOP:
                return dict(exit=j, why='mae breach', mae=mae, rider=rider, ceil=ceil_bar)
        if SANC.get(j) == -d:
            return dict(exit=j, why='octo-sig flip', mae=mae, rider=rider, ceil=ceil_bar)
        if ceil == BASE_HI and oobf(CEIL_TRIG_TF, j, d) and not oobf(CEIL_TRIG_TF, j - 1, d):
            ceil = CEIL_HI; ceil_bar = j
        if not armed:
            if (d > 0 and float(M2[j]) >= SC.HI and float(M2[j - 1]) < SC.HI) or \
               (d < 0 and float(M2[j]) <= SC.LO and float(M2[j - 1]) > SC.LO):
                armed = True
            else:
                continue
        if rider is None:
            c = [t for t in ALL_TF if t <= ceil and oobf(t, j, d)]
            if c: rider = max(c)
            continue
        cand = [t for t in range(rider + 1, min(rider + LIN_HOP, ceil) + 1) if oobf(t, j, d)]
        if cand:
            rider = max(cand); continue
        if ST[(rider, d)][j]:
            return dict(exit=j, why='final stalled', mae=mae, rider=rider, ceil=ceil_bar)
        if xcond(rider, j, d):
            return dict(exit=j, why='x-cross', mae=mae, rider=rider, ceil=ceil_bar)
    return dict(exit=None, why='tape end', mae=mae, rider=rider, ceil=ceil_bar)

LEGS = []; stop_bar = -1; nch = 0
for k0, dr, day, ts in SEEDS:
    if k0 <= stop_bar: continue
    nch += 1; k, d, ln = k0, dr, 0
    while True:
        L = run_leg(k, d)
        if L['exit'] is None: break
        ln += 1; xk = L['exit']
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        pc = lambda j: (float(PX[j]) - p0) / p0 * 100.0 * sgn
        tgt = HS if d > 0 else LS
        nxt = tgt[tgt > k]
        pbar = int(nxt[0]) if nxt.size else None
        seg = PX[k:xk + 1]; idx = np.arange(k, xk + 1)
        ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
        mbar = int(idx[int(seg.argmax()) if d > 0 else int(seg.argmin())]) if seg.size else None
        LEGS.append(dict(chain='%s %s' % (day, ts), leg=ln, side='LONG' if d > 0 else 'SHORT',
                         open=k, exit=xk, why=L['why'], rider=L['rider'], ceil=L['ceil'],
                         real=pc(xk), mae=L['mae'], pivot=pbar, mfe_bar=mbar,
                         pivot_pct=(pc(pbar) if pbar is not None and pbar < N else None),
                         mfe_pct=(pc(mbar) if mbar is not None else None)))
        if L['why'] == 'mae breach': break
        k = xk; d = -d
    stop_bar = LEGS[-1]['exit'] if LEGS else stop_bar
    _P('chain %s %s: %d legs' % (day, ts, ln))

def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    L = lambda s, m, e: s + m.join('─' * (x + 2) for x in w) + e
    print(L('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('└', '┴', '┘'))
md = lambda v: (sorted(v)[len(v) // 2] if v else float('nan'))
MIN = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0

XL = [L for L in LEGS if L['why'] == 'x-cross' and L['rider'] and L['pivot'] is not None
      and L['pivot'] < N]
print('\n# THE x-CROSS DELAY FROM THE TARGET PIVOT, PER RIDER TF  (swing %.2f)' % SWING)
g = collections.defaultdict(list)
for L in XL: g[L['rider']].append(L)
rows = []
for t in sorted(g):
    v = g[t]
    dmin = [MIN(L['pivot'], L['exit']) for L in v]
    gb = [(L['pivot_pct'] - L['real']) for L in v]
    dmfe = [MIN(L['mfe_bar'], L['exit']) for L in v]
    rows.append(('ws%d' % t, str(len(v)), '%+.1f' % md(dmin), '%+.1f' % (sum(dmin) / len(v)),
                 '%+.1f' % max(dmin), '%+.4f' % md(gb), '%+.4f' % sum(gb),
                 '%+.1f' % md(dmfe), '%+.4f' % md([L['real'] for L in v])))
box(('rider TF', 'x-cross legs', 'delay med min', 'delay mean min', 'delay max min',
     'give-back med', 'give-back total', 'delay from MFE bar med', 'realised med'), rows)

print('\n# THE SAME, GROUPED ws1-ws12 vs ws13-ws23')
rows = []
for lbl, lo, hi in (('ws1-ws12 (resting ceiling)', 1, 12), ('ws13-ws23 (extended)', 13, 23)):
    v = [L for L in XL if lo <= L['rider'] <= hi]
    if not v: continue
    dmin = [MIN(L['pivot'], L['exit']) for L in v]
    gb = [(L['pivot_pct'] - L['real']) for L in v]
    rows.append((lbl, str(len(v)), '%+.1f' % md(dmin), '%+.1f' % (sum(dmin) / len(v)),
                 '%+.4f' % md(gb), '%+.4f' % sum(gb),
                 '%+.4f' % (sum(L['real'] for L in v) / len(v))))
box(('rider band', 'x-cross legs', 'delay med min', 'delay mean min', 'give-back med',
     'give-back total', 'realised mean'), rows)

print('\n# DELAY FROM THE LEG\'S OWN MFE BAR, GROUPED  (independent of the swing size)')
rows = []
for lbl, lo, hi in (('ws1-ws2', 1, 2), ('ws3-ws6', 3, 6), ('ws7-ws12', 7, 12),
                    ('ws13-ws23', 13, 23)):
    v = [L for L in LEGS if L['why'] == 'x-cross' and L['rider'] and lo <= L['rider'] <= hi
         and L['mfe_bar'] is not None]
    if not v: continue
    dd2 = [MIN(L['mfe_bar'], L['exit']) for L in v]
    gb2 = [L['mfe_pct'] - L['real'] for L in v]
    rows.append((lbl, str(len(v)), '%+.1f' % md(dd2), '%+.1f' % (sum(dd2) / len(v)),
                 '%+.1f' % max(dd2), '%+.4f' % md(gb2), '%+.4f' % (sum(gb2) / len(v)),
                 '%+.4f' % sum(gb2)))
box(('rider band', 'x-cross legs', 'delay med min', 'delay mean min', 'delay max min',
     'give-back med', 'give-back mean', 'give-back total'), rows)

print('\n# THE SAME FOR final stalled, FOR COMPARISON')
rows = []
for lbl, lo, hi in (('ws1-ws2', 1, 2), ('ws3-ws6', 3, 6), ('ws7-ws12', 7, 12),
                    ('ws13-ws23', 13, 23)):
    v = [L for L in LEGS if L['why'] == 'final stalled' and L['rider'] and lo <= L['rider'] <= hi
         and L['mfe_bar'] is not None]
    if not v: continue
    dd2 = [MIN(L['mfe_bar'], L['exit']) for L in v]
    gb2 = [L['mfe_pct'] - L['real'] for L in v]
    rows.append((lbl, str(len(v)), '%+.1f' % md(dd2), '%+.1f' % (sum(dd2) / len(v)),
                 '%+.4f' % md(gb2), '%+.4f' % (sum(gb2) / len(v))))
box(('rider band', 'stalled legs', 'delay med min', 'delay mean min', 'give-back med',
     'give-back mean'), rows)

with open(os.environ.get('LEGS_FILE', '/home/joe/.claude/jobs/6eb9931e/tmp/chainos2_legs.txt'),
          'w') as fh:
    print('| chain | leg | side | open | exit | why | rider | ceiling | MFE bar | MFE pct | '
          'realised | delay from MFE min | give-back | leg MAE |', file=fh)
    for L in LEGS:
        print('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %+.4f | %s | %s | %.4f |'
              % (L['chain'], L['leg'], L['side'], SC.U(L['open']), SC.U(L['exit']), L['why'],
                 ('ws%d' % L['rider']) if L['rider'] else '-',
                 (SC.U(L['ceil']) if L['ceil'] is not None else '-'),
                 (SC.U(L['mfe_bar']) if L['mfe_bar'] is not None else '-'),
                 ('%+.4f' % L['mfe_pct']) if L['mfe_pct'] is not None else '-', L['real'],
                 ('%+.1f' % MIN(L['mfe_bar'], L['exit'])) if L['mfe_bar'] is not None else '-',
                 ('%+.4f' % (L['mfe_pct'] - L['real'])) if L['mfe_pct'] is not None else '-',
                 L['mae']), file=fh)

print('\n# EVERY x-CROSS LEG WITH A RIDER ABOVE ws12')
hi = [L for L in XL if L['rider'] > 12]
box(('chain', 'leg', 'side', 'open', 'target pivot', 'MFE bar', 'exit', 'rider', 'delay min',
     'pivot pct', 'realised', 'give-back'),
    [(L['chain'], str(L['leg']), L['side'], SC.U(L['open']), SC.U(L['pivot']),
      SC.U(L['mfe_bar']), SC.U(L['exit']), 'ws%d' % L['rider'],
      '%+.1f' % MIN(L['pivot'], L['exit']), '%+.4f' % L['pivot_pct'], '%+.4f' % L['real'],
      '%+.4f' % (L['pivot_pct'] - L['real'])) for L in hi]
    or [('—',) * 12])

print('\n# EVERY LEG, EVERY EXIT KIND')
w = collections.Counter(); wr = collections.Counter()
for L in LEGS: w[L['why']] += 1; wr[L['why']] += L['real']
box(('why', 'legs', 'realised', 'per leg'),
    [(kk, str(w[kk]), '%+.4f' % wr[kk], '%+.4f' % (wr[kk] / w[kk]))
     for kk in sorted(w, key=lambda z: -w[z])]
    + [('all', str(sum(w.values())), '%+.4f' % sum(wr.values()),
        '%+.4f' % (sum(wr.values()) / max(1, sum(w.values()))))])
print('\n- %d chains from %d sanctioned seeds, %d legs' % (nch, len(SEEDS), len(LEGS)))
print('- legs whose ceiling latched: %d of %d'
      % (sum(1 for L in LEGS if L['ceil'] is not None), len(LEGS)))
