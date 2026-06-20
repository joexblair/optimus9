"""
bias_pk_walk_0612.py — self-walk the bias/pk logic with REAL line values, 0636 → 0824 s12m revs
(Joe 0619), to validate the "floater = last anchor in g[], any side" rule BEFORE refactoring.

Prints every s12m reversal in the band: time · bar · side · s12m · mo12m · px_smooth · on-side?(valid)
Then at the 0824 reversal, computes the pk verdict two ways:
  • NEW floater  = last valid anchor in a single g slot (any side)
  • OLD floater  = g[S] (last SAME-side anchor)
for osc ∈ {s12m, mo12m}, via _pk_state_from_slopes(osc_slope, px_slope, floor).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.compute.pk5s_gate_computer import Pk5sGateComputer as PKG

R0, R1 = 1781150400000, 1781753040000
def hm(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m-%d %H:%M')

db = DatabaseManager(**get_db_config()); db.connect()
W = bm.BiasWindow(db, R1); db.disconnect()
s12 = W._aligned(720, bm.GEN_M); mo12 = W._aligned(720, bm.MO12m); px = W.px

revs = W.trigs(12)                                   # reversal bars (detected on GEN_M@TF12 = s12m)
band = [r for r in revs if R0 <= r['t'] <= R1 and 6 * 3600 <= (r['t'] // 1000) % 86400 <= 9 * 3600]
print(f"window {hm(R0)} → {hm(R1)}  ·  s12m reversals in 06:00–09:00 band:\n")
print(f"  {'time':>11} {'bar':>6} {'S':>2} {'s12m':>7} {'mo12m':>7} {'px_sm':>9} {'valid':>6}")
for r in band:
    j = r['j']; S = r['s']; v = s12[j]
    valid = (S == 1 and v > 50) or (S == -1 and v < 50)
    print(f"  {hm(r['t']):>11} {j:>6} {S:>+2} {v:>7.1f} {mo12[j]:>7.1f} {px[j]:>9.5f} {'yes' if valid else 'WRONG':>6}")

# locate the 06-12 06:36 anchor, then 0824 = the NEXT s12m reversal after it
r36 = next(r for r in band if hm(r['t']) == '06-12 06:36')
r24 = min((r for r in revs if r['t'] > r36['t']), key=lambda r: r['t'])
print(f"\nanchor   0636 rev → bar {r36['j']}  S{r36['s']:+d}  s12m {s12[r36['j']]:.1f}  mo12m {mo12[r36['j']]:.1f}  px {px[r36['j']]:.5f}")
print(f"current  0824 rev → bar {r24['j']}  S{r24['s']:+d}  s12m {s12[r24['j']]:.1f}  mo12m {mo12[r24['j']]:.1f}  px {px[r24['j']]:.5f}")

# walk g forward through ALL valid revs up to (not incl) 0824 to find each floater
def valid(r, line):
    v = line[r['j']]; return (r['s'] == 1 and v > 50) or (r['s'] == -1 and v < 50)
ordered = sorted([r for r in revs if r['t'] < r24['t']], key=lambda r: r['t'])
g_single = None; g_side = {1: None, -1: None}
for r in ordered:
    if not valid(r, s12):                            # wrong-side-of-50 → g NOT updated
        continue
    g_single = r; g_side[r['s']] = r
new_flt = g_single; old_flt = g_side[r24['s']]
print(f"\nNEW floater (last anchor any side) → {hm(new_flt['t'])} bar {new_flt['j']} S{new_flt['s']:+d}")
print(f"OLD floater (last SAME-side g[S])  → {hm(old_flt['t'])} bar {old_flt['j']} S{old_flt['s']:+d}" if old_flt else "OLD floater: none")

ST = {2.0: 'PM_LONG(+2)', -2.0: 'PM_SHORT(-2)', 1.0: 'DIV(+1)', -1.0: 'DIV(-1)', 0.0: 'NOISE(0)'}
def verdict(osc, flt):
    aj, fj = r24['j'], flt['j']
    ls = float(osc[aj] - osc[fj]); ps = float(px[aj] - px[fj])
    st = float(PKG._pk_state_from_slopes(ls, ps, 0.0))
    same = 'SAME-sign→PM' if np.sign(ls) == np.sign(ps) else 'OPP-sign→DIV'
    return ls, ps, same, ST.get(st, st)
print("\n0824 verdict (slope_floor=0, sign-dominated):")
for nm, osc in (('s12m', s12), ('mo12m', mo12)):
    for fl, flt in (('NEW', new_flt), ('OLD', old_flt) if old_flt else (None, None)):
        if flt is None: continue
        ls, ps, same, st = verdict(osc, flt)
        print(f"  {nm:>6} {fl:>4}flt | osc_slope {ls:>+7.2f}  px_slope {ps:>+9.5f}  {same:>13}  → {st}")
