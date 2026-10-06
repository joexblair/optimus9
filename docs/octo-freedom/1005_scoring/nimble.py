"""THE NIMBLE WALK. Joe 1005: "we need to be nimble - at any time a walk can move to another branch
if the conditions (like the sub-wsf cascade) change".

WHY: measured 1005, mtd.r1's anchor is STALE at the signal bar on 262 of 276 confluences (95 %) —
all 4 mtd Mages are oob at the step-1 extrema but not at the bar the signal actually fires. The
route condition (cascade towards/away from dr) flips between the two bars on 108 of 276 (39 %).

THREE VARIANTS, scored side by side on FIT (10 days) and TEST (7 random held-out days):
  A  EXTREMA   as built. mtd step 2 reads the 4 Mages at the step-1 extrema. Route decided once.
  B  AT-BAR    mtd step 2 reads the 4 Mages at the SIGNAL bar. This is the version Joe tried on
               1004 and rolled back ("you're absolutely right. rollback") when I pointed out the
               extrema is where the Mages are most extreme. His nimble ruling reopens it with the
               95 % staleness number that was not known then.
  C  NIMBLE    the route is re-read at EVERY bar from the signal forward. The trade is taken at the
               first bar whose route says CONFLUENCE. If the route says BLOCKED or OPEN the walk
               keeps walking - "the walk walks", Joe 1004.

MY ONE CHOSEN VALUE, NAMED: variant C needs a terminator or it walks to the end of the tape. I
terminate at the NEXT octo-sig of the same day, or the day's last bar if there is none. That is a
mechanism already in the data, not a new knob - but it IS a choice and Joe has not ruled it.
Alternatives he may prefer: the next dr flip, or a bar count (which would be a knob).
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys
import numpy as np
sys.path.insert(0, _HERE)
import sweep as W
S = W.S
HI0 = W.CUR['fence']

def route_at(k, anchor, c):
    """mtd + branch D at bar k, reading step 2 at `anchor` ('ex' or 'bar')."""
    d = int(S.DRv[k])
    if d == 0: return (None, None, 0)
    HI, LO = c['fence'], 100.0 - c['fence']
    same = (lambda v: v >= HI) if d > 0 else (lambda v: v <= LO)
    g5 = S.MTD['g5']
    a = max(0, k - c['g5extrema_lookback'])
    hits = [i for i in range(a, k + 1) if np.isfinite(g5[i]) and same(g5[i])]
    if hits:
        ex = max(hits, key=lambda i: g5[i]) if d > 0 else min(hits, key=lambda i: g5[i])
    else:
        j = k
        while j < S.TAPE_LAST and not (np.isfinite(g5[j]) and same(g5[j])): j += 1
        if not (np.isfinite(g5[j]) and same(g5[j])): return (None, None, d)
        want = -1 if d > 0 else +1
        nxt = [i for i in range(j, S.TAPE_LAST + 1) if S.REV[i] == want]
        if not nxt: return (None, None, d)
        ex = nxt[0]
    base = ex if anchor == 'ex' else k            # <- THE ONLY DIFFERENCE between A and B
    TOL = {'g5': 0, 'g15': c['tol15'], 'g30': c['tol30'], 'ws1': 0}
    v = {}
    for n in ('g5', 'g15', 'g30', 'ws1'):
        w = TOL[n]
        if w == 0: v[n] = S.MTD[n][base]; continue
        lo_, hi_ = max(0, base - w), min(S.TAPE_LAST, base + w)
        seg = S.MTD[n][lo_:hi_ + 1]
        v[n] = (float(np.nanmax(seg)) if d > 0 else float(np.nanmin(seg))) if np.isfinite(seg).any() else np.nan
    r1 = all(np.isfinite(v[n]) and same(v[n]) for n in v)
    net = v['ws1'] - v['g15']
    towards = (net > 0) if d > 0 else (net < 0)
    if not r1:
        return (('BLOCKED', 'mtd.r2', d) if towards else ('OPEN', 'neither', d))
    exf = (lambda x: x >= HI) if d > 0 else (lambda x: x <= LO)
    blk = [t for t in S.TF if np.isfinite(S.Rl[t][ex]) and exf(S.Rl[t][ex])]
    af = S.anchor_floater(S.Rl[1], S.PX, d, ex, block=c['af_block'])
    div = bool(af.get('fired')) if isinstance(af, dict) else False
    w1 = float(af['floater'][1]) if div else float(S.Rl[1][ex])
    keep = []
    if blk:
        keep = [blk[0]]
        for t in blk[1:]:
            if t - keep[-1] - 1 <= c['gap_max']: keep.append(t)
    if not keep: return ('OPEN', 'no r block', d)
    weak = min(keep, key=lambda t: S.Rl[t][ex]) if d > 0 else max(keep, key=lambda t: S.Rl[t][ex])
    band = (min(w1, S.Rl[weak][ex]), max(w1, S.Rl[weak][ex]))
    claim = [t for t in S.TF if t > max(keep) and np.isfinite(S.Rl[t][ex]) and band[0] <= S.Rl[t][ex] <= band[1]]
    if claim: return ('OPEN', 'band claimed', d)
    mnet = S.Mg[12][ex] - S.Mg[1][ex]
    away = (mnet < 0) if d > 0 else (mnet > 0)
    # GRADE CORRECTED 1006. Joe: *"`with-trend` would be SHORT because dr is -1. the truth is
    # what the MAE and MFE are reporting - the only change to make is `against-trend`"*. The
    # mapping was recorded in 1005_knobs.md:22 as his 1004 ruling, AWAY = with-trend, and it is
    # inverted. AWAY from dr is now **against-trend**; TOWARDS is **with-trend**, which matches
    # 1003_lazy_g_spec.md:403 - *"present = with-trend, absent = against-trend"*.
    # THE STAGE-2 FLIP POPULATION DOES NOT MOVE. Every selector is pinned to `away` itself, not
    # to the label, so the rows Joe flipped on 1005 are the same rows. Only their NAME changed.
    return ('CONFLUENCE', 'against-trend' if away else 'with-trend', d)

def leg(k, d, c):
    """-> (net, open_bar, close_bar) at the baked stop, or None if unresolved."""
    Hs, Ls = W.piv(c['swing']); stop = c['stop']
    tgt = Ls if d > 0 else Hs
    nx = tgt[tgt > k]
    if nx.size == 0: return None
    j = int(nx[0]); e = float(S.PX[k]); seg = S.PX[k:j + 1]
    adv = (seg - e) / e * 100.0 if d > 0 else (e - seg) / e * 100.0
    fav = (e - seg) / e * 100.0 if d > 0 else (seg - e) / e * 100.0
    hit = np.flatnonzero(np.isfinite(adv) & (adv >= stop))
    if hit.size: return (-stop - W.COST, k, k + int(hit[0]))
    return (float(np.nanmax(fav)) - W.COST, k, j)

def run(days, SIG, variant, c):
    out = []
    for day in days:
        sigs = sorted(SIG[day])
        for i, (k, lbl) in enumerate(sigs):
            stop_bar = sigs[i + 1][0] if i + 1 < len(sigs) else None
            if variant in ('A', 'B'):
                st, gr, d = route_at(k, 'ex' if variant == 'A' else 'bar', c)
                if st != 'CONFLUENCE': continue
                L = leg(k, d, c)
                if L: out.append(dict(day=day, lbl=lbl, bar=k, grade=gr, net=L[0], waited=0))
            else:
                end = stop_bar if stop_bar is not None else min(k + 17280, S.TAPE_LAST)
                took = None
                for b in range(k, end):
                    st, gr, d = route_at(b, 'bar', c)
                    if st == 'CONFLUENCE': took = (b, gr, d); break
                if took is None: continue
                b, gr, d = took
                L = leg(b, d, c)
                if L: out.append(dict(day=day, lbl=lbl, bar=b, grade=gr, net=L[0],
                                      waited=(S.ts[b] - S.ts[k]) / 60000.0))
    return out

if __name__ == '__main__':
    SIG = W.signal_bars(W.FIT + W.TEST)
    print('# baked config: stop %.2f | risk %.1f %% | swing %.2f' % (W.CUR['stop'], W.CUR['risk'], W.CUR['swing']))
    print()
    print('## THE NIMBLE WALK — three variants, FIT 10 days vs TEST 7 held-out days')
    print('| variant | what it reads | set | trades | total net % | mean net % | winners | mean wait min |')
    print('|' + '---|' * 8)
    res = {}
    for v, desc in (('A', 'step 2 at the EXTREMA (as built)'),
                    ('B', 'step 2 at the SIGNAL bar'),
                    ('C', 'route re-read EVERY bar, first CONFLUENCE taken')):
        for tag, days in (('FIT', W.FIT), ('TEST', W.TEST)):
            o = run(days, SIG, v, W.CUR); res[(v, tag)] = o
            n = np.array([x['net'] for x in o]) if o else np.array([0.0])
            wt = np.mean([x['waited'] for x in o]) if o else 0.0
            print('| **%s** | %s | %s | %d | **%+.3f** | **%+.4f** | %d | %.1f |'
                  % (v, desc, tag, len(o), n.sum(), n.mean(), int((n > 0).sum()), wt))
    print()
    print('## HEAD TO HEAD on the held-out set')
    print('| variant | TEST trades | TEST total % | TEST mean % | vs A trades | vs A total |')
    print('|' + '---|' * 6)
    a = np.array([x['net'] for x in res[('A', 'TEST')]])
    for v in ('A', 'B', 'C'):
        n = np.array([x['net'] for x in res[(v, 'TEST')]]) if res[(v, 'TEST')] else np.array([0.0])
        print('| %s | %d | %+.3f | %+.4f | %+d | %+.3f |'
              % (v, len(n), n.sum(), n.mean(), len(n) - len(a), n.sum() - a.sum()))
