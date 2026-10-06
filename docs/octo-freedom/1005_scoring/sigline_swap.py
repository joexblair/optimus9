"""Joe's 1005 overnight idea, scored: swap the line that carries the ws1mage-rev CROSS.

The g1 swap he described is inert (section 11 of 1005_knobs.md - the walk discards the g1 legs).
The live leg is `sig_mage`. This scores each candidate across all 17 days at the BAKED config
(stop 0.95, risk 1.5 %, swing 0.70, dr-bias, no pyramid cap, $888) under his objective:
best PnL with minimal loss of trades.
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, datetime as dt
import numpy as np
sys.path.insert(0, _HERE)
import upstream as UP
import sweep as W

FIT  = ['2026-09-%02d' % d for d in (25,26,27,28,29,30)] + ['2026-10-%02d' % d for d in (1,2,3,4)]
TEST = ['2026-07-23','2026-07-25','2026-08-06','2026-08-20','2026-08-30','2026-09-14','2026-09-17']
ms = int(dt.datetime(2026,10,4,tzinfo=dt.timezone.utc).timestamp()*1000)
UP._cached_rig((ms, ms+86400000)); R = UP._RIG
_real = UP.RLW.ws1mage_rev
SUB = {'sig': None}
def wrap(g1, sig_mage, hi, lo, **kw):
    return _real(g1, SUB['sig'] if SUB['sig'] is not None else sig_mage, hi, lo, **kw)
UP.RLW.ws1mage_rev = wrap

def score(days, sigmap):
    Hs, Ls = W.piv(W.CUR['swing']); stop = W.CUR['stop']
    o, cl, nt = [], [], []
    for day in days:
        for lbl in sigmap[day]:
            try: k = W.S.K(day + ' ' + lbl)
            except Exception: continue
            st, gr, d = W.route(k, W.CUR)
            if st != 'CONFLUENCE': continue
            tgt = Ls if d > 0 else Hs
            nx = tgt[tgt > k]
            if nx.size == 0: continue
            j = int(nx[0]); e = float(W.S.PX[k]); seg = W.S.PX[k:j+1]
            adv = (seg-e)/e*100.0 if d > 0 else (e-seg)/e*100.0
            fav = (e-seg)/e*100.0 if d > 0 else (seg-e)/e*100.0
            hit = np.flatnonzero(np.isfinite(adv) & (adv >= stop))
            ex, g = (k+int(hit[0]), -stop) if hit.size else (j, float(np.nanmax(fav)))
            o.append(k); cl.append(ex); nt.append(g - W.COST)
    if not o: return 0, 0.0, 0.0, 1.0, 0.0
    o, cl, nt = np.array(o), np.array(cl), np.array(nt)
    fin, dd, n = W.grid_block(o, cl, nt, W.CUR['pyr'], [W.CUR['risk']], stop + W.COST)
    return len(nt), float(nt.sum()), float(nt.mean()), float(fin[0]), float(dd[0])

print('# BAKED config: stop %.2f | risk %.1f %% | swing %.2f | $888' % (W.CUR['stop'], W.CUR['risk'], W.CUR['swing']))
print()
print('## `sig_mage` SWAP, scored on 10 FIT + 7 TEST days')
print('| sig_mage | FIT sig | FIT n | FIT total % | FIT mean | FIT $ | FIT DD % | TEST sig | TEST n | TEST total % | TEST mean | TEST $ | TEST DD % | retention | robust /day |')
print('|' + '---|' * 15)
base = None
for name, key in (('gcws30Mage', None), ('ws1Mage','ws1'), ('ws2Mage','ws2'), ('ws3Mage','ws3')):
    try: SUB['sig'] = None if key is None else np.asarray(R.lines[key]['Mage'], float)
    except KeyError: print('| %s | NOT IN CACHE |' % name); continue
    sm = {}
    for day in FIT + TEST: sm[day] = UP.walk_day(day)
    fs = sum(len(sm[d]) for d in FIT); ts = sum(len(sm[d]) for d in TEST)
    fn, ft, fm, ffin, fdd = score(FIT, sm)
    tn, tt, tm, tfin, tdd = score(TEST, sm)
    if base is None: base = (fn, tn)
    rob = min(ffin**(1/10.0) if ffin>0 else 0.0, tfin**(1/7.0) if tfin>0 else 0.0)
    ret = min(fn/max(1,base[0]), tn/max(1,base[1]))
    print('| **%s** | %d | %d | %+.3f | %+.4f | %.2f | %.2f | %d | %d | %+.3f | %+.4f | %.2f | %.2f | **%.3f** | **%.6f** |'
          % (name, fs, fn, ft, fm, 888*ffin, fdd*100, ts, tn, tt, tm, 888*tfin, tdd*100, ret, rob))
SUB['sig'] = None
