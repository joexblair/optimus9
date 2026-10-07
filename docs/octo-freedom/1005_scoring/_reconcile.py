"""From +97.619 sum MFE to -8.059 realised. Where every step of the gap goes.

Joe 1007: *"I'm less convinced about our original summary"*. This reconciles the banked
capture @75% against the realised open-to-close, step by step, on the same 45 trades.
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
CAP = 0.75
DAYS = ('2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
        '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
H, L = SC.pivots(float(SC.LG['swing'])); PX = SC.PX
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
    if (k, d) in _mt: return _mt[(k, d)]
    with momo_config(BANK[1]):
        with momo_window(int(BANK[1]['k_window']) * 1):
            v = momo_g_why(SC.Rl[1], int(d), int(k))[0] in ('momo', 'curl')
    _mt[(k, d)] = v; return v
oobf = lambda t, k, d: (float(SC.Rl[t][k]) >= SC.HI) if d > 0 else (float(SC.Rl[t][k]) <= SC.LO)
_P('producers ready')

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

rows = []
for t in trades:
    side = 'LONG' if t['dr'] > 0 else 'SHORT'; sgn = 1 if side == 'LONG' else -1
    dt = -1 if side == 'LONG' else +1
    mfe_p, mae_p, piv = SC.score(t['open_k'], dt, H, L)       # the PIVOT STRETCH, what is banked
    arm = next((s for s in arms if s['k'] > t['open_k']), None)
    if arm is None or mfe_p is None: continue
    back = -1 if side == 'LONG' else +1
    prev = int(SC.DRv[arm['k']]); holder = None; xk = None
    for k in range(arm['k'], SC.TAPE_LAST + 1):
        dk = int(SC.DRv[k])
        if dk == back and prev != back: xk = k; break
        prev = dk
        if holder is None:
            if mt1(k, t['dr']): holder = LIN_TF[0]
            continue
        cand = [tt for tt in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1)
                if oobf(tt, k, t['dr'])]
        if cand: holder = max(cand); continue
        if ST[(holder, t['dr'])][k]: xk = k; break
    if xk is None: continue
    p0 = float(PX[t['open_k']])
    seg = PX[t['open_k']:xk + 1]; idx = np.arange(t['open_k'], xk + 1)
    ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
    jf = int(seg.argmax()) if side == 'LONG' else int(seg.argmin())
    mfe_w = (float(seg[jf]) - p0) / p0 * 100.0 * sgn
    rows.append(dict(day=t['day'], sig=t['sig'], mfe_p=mfe_p, mfe_w=mfe_w,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn,
                     piv_min=(int(SC.ts[piv]) - int(SC.ts[t['open_k']])) / 60000.0,
                     hold=(int(SC.ts[xk]) - int(SC.ts[t['open_k']])) / 60000.0,
                     mfe_at=(int(SC.ts[int(idx[jf])]) - int(SC.ts[t['open_k']])) / 60000.0,
                     arm=(int(SC.ts[arm['k']]) - int(SC.ts[t['open_k']])) / 60000.0))

n = len(rows)
sp = sum(r['mfe_p'] for r in rows); sw = sum(r['mfe_w'] for r in rows); sr = sum(r['real'] for r in rows)
print('\n# THE CHAIN, %d trades' % n)
print('| step | sum | per trade | what it assumes |'); print('|---|---|---|---|')
print('| sum MFE over the PIVOT STRETCH | %+.3f | %+.4f | the stretch to the next favourable pivot |' % (sp, sp / n))
print('| x %.0f%% capture | **%+.3f** | %+.4f | Joe 1006 - a forward walk reaches 75%% of it |' % (CAP * 100, CAP * sp, CAP * sp / n))
print('| sum MFE over the ACTUAL HOLDING WINDOW | %+.3f | %+.4f | open -> the lineage walk exit |' % (sw, sw / n))
print('| x %.0f%% capture on THAT | %+.3f | %+.4f | same assumption, honest window |' % (CAP * 100, CAP * sw, CAP * sw / n))
print('| **REALISED open to close** | **%+.3f** | **%+.4f** | nothing - it is the price difference |' % (sr, sr / n))

print('\n# WHY THE TWO MFE NUMBERS DIFFER')
print('| | min | median | max |'); print('|---|---|---|---|')
for lbl, key in (('pivot stretch length, min', 'piv_min'), ('actual hold, min', 'hold'),
                 ('MFE bar, min after open', 'mfe_at'), ('exit-armed, min after open', 'arm')):
    v = sorted(r[key] for r in rows)
    print('| %s | %.1f | %.1f | %.1f |' % (lbl, v[0], v[len(v) // 2], v[-1]))
longer = sum(1 for r in rows if r['hold'] > r['piv_min'])
print('\n- trades whose HOLD outlasts the pivot stretch: **%d of %d**' % (longer, n))
print('- trades whose MFE bar lands AFTER exit-armed: %d of %d'
      % (sum(1 for r in rows if r['mfe_at'] > r['arm']), n))
print('- trades whose window MFE is SMALLER than the pivot-stretch MFE: %d of %d'
      % (sum(1 for r in rows if r['mfe_w'] < r['mfe_p'] - 1e-9), n))
