"""STAGE 2 of the r-pred-cancel A/B (Joe 0730). Loads the banked timestamps and scores them.
swing_detect is imported HERE and nowhere in stage 1, so scoring cannot feed back into generation.

Trade dir = -side (bull bias = hi OOB = short). MFE/MAE from the confirmed exhaustion bar to the next
favourable pivot. No cap, no horizon.

    python3 ab_rpred_s2.py [--pct 2.22 4.00]
"""
import json, os, random, sys, statistics as st
import numpy as np
import build_exhaust as X
import optimus9.orchestration.rpl_walk as R
from optimus9.compute.swing_detect import find_pivots

IN = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'ab_rpred_stage1.json')
random.seed(907)


def scorer(px, pct):
    P = find_pivots(px, pct); pv = [p[0] for p in P]; kd = [p[1] for p in P]

    def one(i, side):
        want = 'L' if side > 0 else 'H'
        nb = next((b for b, k in zip(pv, kd) if b > i and k == want), None)
        if nb is None:
            return None
        seg = px[i:nb + 1]
        if side > 0:
            return (px[i] - np.nanmin(seg)) / px[i] * 100, (np.nanmax(seg) - px[i]) / px[i] * 100
        return (np.nanmax(seg) - px[i]) / px[i] * 100, (px[i] - np.nanmin(seg)) / px[i] * 100
    return one, pv


def main(argv):
    pcts = [2.22, 4.00]
    if '--pct' in argv:
        pcts = [float(a) for a in argv[argv.index('--pct') + 1:] if a.replace('.', '').isdigit()]
    D = json.load(open(IN))
    X.rebuild_cache(120)
    ts = np.asarray(R.L0['ts'], np.int64); px = np.asarray(R.L0['src'].pxs, float)
    q = lambda a, f: sorted(a)[int(f * (len(a) - 1))]
    print('banked  A %d events | B %d events\n' % (len(D['A']), len(D['B'])))
    for pct in pcts:
        one, pv = scorer(px, pct)
        print('=== swing_detect %.2f%%  (%d pivots) ===' % (pct, len(pv)))
        print('  %-28s %5s | %6s %6s %6s %6s | %6s %6s'
              % ('arm', 'n', 'MFE', 'MAE', 'MAEp90', 'ratio', 'MFEp10', 'medTF'))
        res = {}
        for lbl in ('A', 'B'):
            ev = [(int(np.searchsorted(ts, e['conf'])), 1 if e['bias'] == 'bull' else -1, e['cur_tf'])
                  for e in D[lbl]]
            r_ = [(x, tf) for i, s, tf in ev if (x := one(i, s))]
            mf = [x[0] for x, _ in r_]; ma = [x[1] for x, _ in r_]
            res[lbl] = (mf, ma)
            print('  %-28s %5d | %6.2f %6.2f %6.2f %6.2f | %6.2f %6d'
                  % ({'A': 'A  live', 'B': 'B  x/r cross cancels'}[lbl], len(r_), st.median(mf),
                     st.median(ma), q(ma, .90), st.median(mf) / max(1e-9, st.median(ma)),
                     q(mf, .10), int(st.median([tf for _, tf in r_]))))
        lo = min(int(np.searchsorted(ts, e['conf'])) for e in D['A'] + D['B'])
        hi = max(int(np.searchsorted(ts, e['conf'])) for e in D['A'] + D['B'])
        rnd = [x for _ in range(8000) if (x := one(random.randint(lo, hi), random.choice([1, -1])))]
        rm = [r[0] for r in rnd]; ra = [r[1] for r in rnd]
        print('  %-28s %5d | %6.2f %6.2f %6.2f %6.2f | %6.2f %6s   <- RANDOM'
              % ('random', len(rnd), st.median(rm), st.median(ra), q(ra, .90),
                 st.median(rm) / max(1e-9, st.median(ra)), q(rm, .10), ''))
        a_mf, a_ma = res['A']; b_mf, b_ma = res['B']
        print('  delta B-A: MFE %+.2f  MAE %+.2f  ratio %+.2f\n'
              % (st.median(b_mf) - st.median(a_mf), st.median(b_ma) - st.median(a_ma),
                 st.median(b_mf) / max(1e-9, st.median(b_ma)) - st.median(a_mf) / max(1e-9, st.median(a_ma))))
    ka = {(e['conf'], e['cur_tf'], e['bias']) for e in D['A']}
    kb = {(e['conf'], e['cur_tf'], e['bias']) for e in D['B']}
    one4, _ = scorer(px, 4.00)
    for lbl, S in (('A only', ka - kb), ('B only', kb - ka)):
        if not S:
            print('%s: none' % lbl); continue
        r_ = [x for c, tf, bs in S if (x := one4(int(np.searchsorted(ts, c)), 1 if bs == 'bull' else -1))]
        if r_:
            print('%-8s n=%-4d MFE %6.2f  MAE %6.2f  ratio %5.2f  (4.00%%)'
                  % (lbl, len(r_), st.median([x[0] for x in r_]), st.median([x[1] for x in r_]),
                     st.median([x[0] for x in r_]) / max(1e-9, st.median([x[1] for x in r_]))))


if __name__ == '__main__':
    main(sys.argv[1:])
