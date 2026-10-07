"""THE LAZY-G PORT — every `no r block` trade, opened towards dr, exited by Joe's lineage walk.

JOE 1007: *"because we are dynamically and surgically selecting the exit bar, we need a further row
that captures the actual open to close, as a comparison to '75% of MFE'"*.

  open        every `no r block` octo-sig, AT that bar, TOWARDS dr (dr +1 = LONG). Pyramiding is
              accepted - Joe 1007: *"I think I accidentally introduced pyramiding ... I'm good with that"*.
  exit-armed  the first later octo-sig graded neither `with-trend` nor `no r block`.
  exit        the lineage walk from exit-armed: step forward to ws1 momentum, hop up on an oob
              crossing within +2 TF numbers, exit on the rider's final `stalled`.

THREE RESULT COLUMNS, side by side:
  REALISED      (px_exit - px_open)/px_open, signed by the side. The actual open-to-close. NEW.
  MFE@75        0.75 * the pivot-stretch MFE - Joe's capture assumption, what we have been quoting.
  MFE@75 capped the same with Joe's 0.95 MAE cap zeroing it.

MOMENTUM IS READ ON dr, NEVER ON trade_side - Joe 1006. `stalled` comes from jig.stall_mask, the same
producer baton.py uses, computed ONCE over the whole tape per TF per dr (vectorised). ws1 mom-true
comes from momo_g_why and is computed LAZILY, one bar at a time as the walk reaches it - it is the
expensive call and the walk must not read ahead of itself.

NO HOLDING LIMIT. Joe has never named one. A trade runs until its walk ends.
"""
import os, io, contextlib, re, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')      # score39.py:25 - optimus9 is not on the path from here

# STDERR IS NOT SWALLOWED AROUND THE IMPORTS. The earlier version did
#     _e = sys.stderr; sys.stderr = io.StringIO()
#     ...imports...
#     sys.stderr = _e
# and a failing import then raised into a discarded buffer: the process exited 1 with ZERO output and
# looked identical to a job that had been killed. Joe 1007: *"missing the shell outputs has been
# plaguing you for a few days now. diagnose and repair"*. That swallow WAS the repair target - the
# real error here was ModuleNotFoundError: optimus9, invisible for two launches.
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
import lineage_walk as LW

OPEN_GRADES = ('with-trend', 'no r block')
TRADE_GRADE = 'no r block'
MFE_CAPTURE, MAE_CAP = 0.75, 0.95
DAYS = os.environ.get('LG_DAYS',
    '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
    '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
STALL_N = int(SC.LG['stall_n'])
H, L = SC.pivots(float(SC.LG['swing']))
PX = SC.PX

# ---- the momentum producers, read on dr
_P('stall_mask over %d TFs x 2 dr ...' % len(SC.TF))
db = DatabaseManager(**get_db_config()); db.connect()
BANK = {t: momo_bank(db, t) for t in LIN_TF}; db.disconnect()
ST = {}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            step, samples = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for dd in (-1, +1):
        ST[(t, dd)] = stall_mask(SC.Rl[t], dd, STALL_N, step, samples)
_P('stall masks built')
_mtc = {}
def mom_true_at(t, k, d):
    key = (t, k, d)
    if key in _mtc: return _mtc[key]
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            v = momo_g_why(SC.Rl[t], int(d), int(k))[0] in ('momo', 'curl')
    _mtc[key] = v
    return v

# ---- every octo-sig, one list, no day boundary
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
        sigs.append(dict(day=day, sig=f[2], k=k, open_k=max(k, int(r['kw']), ex), ex=ex, dr=d,
                         grade=g, openable=(g in OPEN_GRADES)))
sigs.sort(key=lambda x: x['k'])
_P('%d octo-sigs classified' % len(sigs))
arms = [s for s in sigs if not s['openable']]
trades = [s for s in sigs if s['grade'] == TRADE_GRADE]

out = []
_P('walking %d trades ...' % len(trades))
for _i, t in enumerate(trades):
    side = 'LONG' if t['dr'] > 0 else 'SHORT'                 # towards dr, Joe 1007
    arm = next((s for s in arms if s['k'] > t['open_k']), None)
    rec = dict(day=t['day'], sig=t['sig'], side=side, dr=t['dr'], open_k=t['open_k'],
               arm=arm, w=None)
    if arm:
        rec['w'] = LW.walk(SC.Rl, SC.DRv,
                           lambda tt, kk, d=t['dr']: mom_true_at(tt, kk, d),
                           lambda tt, kk, d=t['dr']: bool(ST[(tt, d)][kk]),
                           arm['k'], t['dr'], SC.HI, SC.LO, SC.TAPE_LAST,
                           LIN_TF, LIN_HOP, side)
    mfe, mae, _ = SC.score(t['open_k'], (-1 if side == 'LONG' else +1), H, L)
    rec['mfe'], rec['mae'] = mfe, mae
    xk = rec['w']['exit_k'] if rec['w'] else None
    if xk is not None:
        p0, p1 = float(PX[t['open_k']]), float(PX[xk])
        rec['real'] = (p1 - p0) / p0 * 100.0 * (1.0 if side == 'LONG' else -1.0)
        rec['hold'] = (int(SC.ts[xk]) - int(SC.ts[t['open_k']])) / 60000.0
        seg = PX[t['open_k']:xk + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
        if side == 'LONG':
            rec['mae_win'] = max(0.0, (p0 - float(seg.min())) / p0 * 100.0)
        else:
            rec['mae_win'] = max(0.0, (float(seg.max()) - p0) / p0 * 100.0)
    else:
        rec['real'] = rec['hold'] = rec['mae_win'] = None
    out.append(rec)
    _P('  trade %2d/%d  %s %s -> %s' % (_i + 1, len(trades), t['day'], t['sig'],
       (SC.U(rec['w']['exit_k']) if rec['w'] and rec['w']['exit_k'] is not None else '—')))

U = SC.U
fm = lambda v, n=4: ('%.*f' % (n, v)) if v is not None else '—'
print('# THE LAZY-G PORT — %d `no r block` TRADES, opened towards dr, exited by the lineage walk'
      % len(out))
print('# %s   capture %.0f%% of MFE   MAE cap %.2f' % (SC.LG_KEY, MFE_CAPTURE*100, MAE_CAP))
print('\n| day | open | side | exit-armed | ws1 mom @ | exit | why | hold min | MAE in window | REALISED | MFE@75 | MFE@75 capped |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in out:
    w = r['w']
    c75 = (0.0 if (r['mae'] is not None and r['mae'] >= MAE_CAP) else
           (MFE_CAPTURE * r['mfe'] if r['mfe'] is not None else None))
    print('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |'
          % (r['day'], r['sig'], r['side'],
             r['arm']['sig'] if r['arm'] else '—',
             U(w['start_k']) if w and w['start_k'] is not None else '—',
             U(w['exit_k']) if w and w['exit_k'] is not None else '—',
             (w['why'] if w else 'no exit-armed'),
             fm(r['hold'], 1), fm(r['mae_win']), fm(r['real']),
             fm(MFE_CAPTURE * r['mfe'] if r['mfe'] is not None else None), fm(c75)))

ok = [r for r in out if r['real'] is not None]
print('\n# THE THREE RESULT COLUMNS, SUMMED OVER %d TRADES' % len(ok))
print('| measure | sum | mean per trade | positive | days |'); print('|---|---|---|---|---|')
def tot(vals, lbl):
    v = [x for x in vals if x is not None]
    if not v: print('| %s | — | — | — | — |' % lbl); return
    print('| %s | %+.3f | %+.4f | %d of %d | %d |'
          % (lbl, sum(v), sum(v)/len(v), sum(1 for x in v if x > 0), len(v),
             len({r['day'] for r in ok})))
tot([r['real'] for r in ok], '**REALISED open to close**')
tot([MFE_CAPTURE * r['mfe'] for r in ok if r['mfe'] is not None], 'MFE@75')
tot([(0.0 if (r['mae'] is not None and r['mae'] >= MAE_CAP) else MFE_CAPTURE*r['mfe'])
     for r in ok if r['mfe'] is not None], 'MFE@75 capped at %.2f' % MAE_CAP)

print('\n# WHY EACH WALK ENDED')
wy = {}
for r in out:
    k2 = r['w']['why'] if r['w'] else 'no exit-armed'
    wy[k2] = wy.get(k2, 0) + 1
print('| why | trades |'); print('|---|---|')
for k2 in sorted(wy, key=lambda x: -wy[x]): print('| %s | %d |' % (k2, wy[k2]))

print('\n# PER DAY')
print('| day | trades | REALISED | MFE@75 | MFE@75 capped | median hold min |')
print('|---|---|---|---|---|---|')
for d in sorted({r['day'] for r in out}):
    s = [r for r in out if r['day'] == d and r['real'] is not None]
    if not s: continue
    hd = sorted(x['hold'] for x in s)
    print('| %s | %d | %+.3f | %+.3f | %+.3f | %.1f |'
          % (d, len(s), sum(x['real'] for x in s),
             sum(MFE_CAPTURE*x['mfe'] for x in s if x['mfe'] is not None),
             sum((0.0 if x['mae'] >= MAE_CAP else MFE_CAPTURE*x['mfe']) for x in s if x['mfe'] is not None),
             hd[len(hd)//2]))
