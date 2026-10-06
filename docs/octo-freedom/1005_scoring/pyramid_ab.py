"""A/B: does Joe's two-condition gate apply to a PYRAMID ADD, or only to a fresh entry?
Joe 1005: "I can't decide on the pyramid call. A/B it".

THE GATE, his words: BLOCK when (sub-wsf cascade FACING dr) AND (higher wsf lines mom-true).
  cond1  net g15Mage -> ws1Mage faces dr.  Span settled by measurement: g5->ws1 disagrees with his
         own 02:12 call, g15->ws1 matches it, and it is the span his mtd.r2 wording uses.
  cond2  any wsf line ABOVE the branch-D ex-fence block top is mom-true. "higher" read as higher
         than the block - MINE, flagged; "any" rather than a count - MINE, flagged.
  Both read AT THE SIGNAL BAR, per his nimble ruling.

A PYRAMID ADD, defined causally: a signal firing while a position opened by an EARLIER signal on
the SAME side is still open. Known at the bar, no lookahead.

  ARM P-GATED   the gate applies to every signal, adds included
  ARM P-EXEMPT  the gate applies only to a fresh entry; an add is exempt
  ARM NO-GATE   the gate is off entirely - the current build, for reference
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, datetime as dt
import numpy as np
sys.path.insert(0, _HERE)
import sweep as W, upstream as UP
S = W.S
ms = int(dt.datetime(2026, 10, 4, tzinfo=dt.timezone.utc).timestamp() * 1000)
UP._cached_rig((ms, ms + 86400000)); R = UP._RIG; WM = UP.RLW.W
from optimus9.compute.momo_seam import seam_mask
rts = np.asarray(R.ts, np.int64)
mfr = float(R.C['momo_fence_r']); FENCE = (mfr, 100.0 - mfr); WCFG = WM.WS1_CFG
SMc = {t: seam_mask(R.ts, t) for t in range(1, 13)}
RLc = {t: np.asarray(R.lines['ws%d' % t]['r'], float) for t in range(1, 13)}
_mt = {}
def momtrue(t, k, d):
    ck = (t, k, d)
    if ck not in _mt:
        _mt[ck] = bool(WM.momentum_true(RLc[t], R.BK[t], WCFG, d, k, SMc[t], t,
                                        strip_mom_at_fence=FENCE)[0])
    return _mt[ck]

def gate(k, d, blocktop):
    """-> (block?, cond1, cond2). Joe's AND, read at bar k."""
    net3 = S.MTD['ws1'][k] - S.MTD['g15'][k]
    c1 = (net3 > 0) if d > 0 else (net3 < 0)
    above = [t for t in range(1, 13) if t > blocktop and momtrue(t, k, d)] if blocktop else \
            [t for t in range(1, 13) if momtrue(t, k, d)]
    return (c1 and bool(above)), c1, above

def leg(k, d):
    Hs, Ls = W.piv(W.CUR['swing']); stop = W.CUR['stop']
    tgt = Ls if d > 0 else Hs
    nx = tgt[tgt > k]
    if nx.size == 0: return None
    j = int(nx[0]); e = float(S.PX[k]); seg = S.PX[k:j + 1]
    adv = (seg - e) / e * 100.0 if d > 0 else (e - seg) / e * 100.0
    fav = (e - seg) / e * 100.0 if d > 0 else (seg - e) / e * 100.0
    hit = np.flatnonzero(np.isfinite(adv) & (adv >= stop))
    if hit.size: return (-stop - W.COST, k + int(hit[0]))
    return (float(np.nanmax(fav)) - W.COST, j)

def run(days, SIG, arm):
    out = []
    for day in days:
        live = []                          # [(close_bar, side)] still open
        for k, lbl in sorted(SIG[day]):
            st, gr, d = W.route(k, W.CUR)
            if st != 'CONFLUENCE': continue
            side = 'SHORT' if d > 0 else 'LONG'
            live = [x for x in live if x[0] > k]
            is_add = any(x[1] == side for x in live)
            m = S.mtd(k); top = 0
            if m.get('ex') is not None:
                b = S.branchD(d, m['ex'])
                if b.get('keep'): top = max(b['keep'])
            blocked, c1, above = gate(k, d, top)
            if arm == 'P-GATED'  and blocked: continue
            if arm == 'P-EXEMPT' and blocked and not is_add: continue
            L = leg(k, d)
            if not L: continue
            live.append((L[1], side))
            out.append(dict(day=day, lbl=lbl, net=L[0], add=is_add, grade=gr,
                            blocked=blocked, c1=c1, nabove=len(above)))
    return out

if __name__ == '__main__':
    SIG = W.signal_bars(W.FIT + W.TEST)
    print('# gate: (g15->ws1 faces dr) AND (any wsf above the D block top is mom-true), read at the signal bar')
    print('# stop %.2f | risk %.1f %% | swing %.2f' % (W.CUR['stop'], W.CUR['risk'], W.CUR['swing']))
    print()
    print('## THE A/B — does the gate apply to a pyramid add?')
    print('| arm | set | trades | adds taken | total net % | mean net % | winners |')
    print('|' + '---|' * 7)
    res = {}
    for arm in ('NO-GATE', 'P-GATED', 'P-EXEMPT'):
        for tag, days in (('FIT', W.FIT), ('TEST', W.TEST)):
            o = run(days, SIG, arm); res[(arm, tag)] = o
            n = np.array([x['net'] for x in o]) if o else np.array([0.0])
            print('| **%s** | %s | %d | %d | **%+.3f** | **%+.4f** | %d |'
                  % (arm, tag, len(o), sum(1 for x in o if x['add']), n.sum(), n.mean(), int((n > 0).sum())))
    print()
    print('## THE ADDS THEMSELVES — the population the question is about')
    print('| arm | set | adds | their total net % | their mean |')
    print('|' + '---|' * 5)
    for arm in ('NO-GATE', 'P-GATED', 'P-EXEMPT'):
        for tag in ('FIT', 'TEST'):
            a = [x for x in res[(arm, tag)] if x['add']]
            v = np.array([x['net'] for x in a]) if a else np.array([0.0])
            print('| %s | %s | %d | %+.3f | %+.4f |' % (arm, tag, len(a), v.sum(), v.mean()))
    print()
    base = res[('NO-GATE', 'TEST')]
    bv = np.array([x['net'] for x in base])
    print('## HELD-OUT HEAD TO HEAD, vs the current no-gate build')
    print('| arm | TEST trades | TEST total % | TEST mean % | trades vs no-gate | total vs no-gate |')
    print('|' + '---|' * 6)
    for arm in ('NO-GATE', 'P-GATED', 'P-EXEMPT'):
        v = np.array([x['net'] for x in res[(arm, 'TEST')]]) if res[(arm, 'TEST')] else np.array([0.0])
        print('| **%s** | %d | %+.3f | **%+.4f** | %+d | %+.3f |'
              % (arm, len(v), v.sum(), v.mean(), len(v) - len(bv), v.sum() - bv.sum()))
