"""STAGE 1 of the r-pred-cancel A/B (Joe 0730). Banks causal timestamps to disk. NO scoring here.

Hypothesis (Joe): r-pred is not cancelled when x crosses through r, so a stale r-pred keeps a TF
"participating" in the ladder long after the cross. If true, rp_matrix -> seeded_ladder -> current_tf are
all carrying it, and the wrong markers APPLY.

  ARM A  rp[t] = (P[t] == CS) | oob_climb(E[t]['r'])                     <- live
  ARM B  rp[t] = latch(set=P rising edge, reset=x/r cross) | oob_climb(E[t]['r'])
         cancel = the polarity-matched debounced x/r cross already built in rpl_walk.build_lines:
           bull  fx_bull = _wx(x-r, -1)   x crosses UNDER r
           bear  fx_bear = _wx(x-r, +1)   x crosses OVER  r
         set-wins-on-ties (_latch_with_reset uses last_set >= last_reset).
         oob_climb is NOT cancelled -- only the predict term.

Both arms run the unmodified build_rplwalk2.applied() with rp_matrix swapped, so the ladder, the
contiguous rule, the 40s-lag check and the marker race are identical between arms.

    python3 ab_rpred_s1.py            -> writes ab_rpred_stage1.json
"""
import json, os, sys
import numpy as np
import build_exhaust as X
import build_rplwalk2 as W
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import _latch_with_reset

OUT = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'ab_rpred_stage1.json')


def rp_matrix_B(bias, ceiling):
    """ARM B — the predict term is a latch cancelled by the x/r cross on the same line."""
    E = R.L0['E']; P = R.L0['P']; p = R._polar(bias)
    fx = R.L0['fx_bull'] if p['BULL'] else R.L0['fx_bear']
    tfs = list(range(X.RPL_FLOOR, ceiling + 1))
    rp = np.zeros((len(tfs), R.L0['n']), dtype=bool)
    for i, t in enumerate(tfs):
        pr = (P[t] == p['CS'])
        edge = pr & ~np.r_[False, pr[:-1]]
        rp[i] = _latch_with_reset(edge, np.asarray(fx[t], bool)) | p['oob_climb'](E[t]['r'])
    return rp, tfs


def run(label, fn):
    orig = W.rp_matrix
    W.rp_matrix = fn
    try:
        rows = W.applied(ceiling=120, persist=False)
    finally:
        W.rp_matrix = orig
    seen, out = set(), []
    for r in rows:
        k = (r['conf'], r['cur'], r['bias'])
        if k in seen:
            continue
        seen.add(k)
        out.append(dict(setup=int(r['setup']), raw=int(r['raw']), conf=int(r['conf']), bias=r['bias'],
                        start_tf=int(r['start']), cur_tf=int(r['cur']), climbs=int(r['climbs']),
                        leg=r['leg'], wait_s=int(r['wait'])))
    print('%s: %d applied rows -> %d distinct events' % (label, len(rows), len(out)))
    return out


def main():
    X.rebuild_cache(120)
    A = run('ARM A (live)', W.rp_matrix)
    B = run('ARM B (x/r cross cancels r-pred)', rp_matrix_B)
    ts = np.asarray(R.L0['ts'], np.int64)
    with open(OUT, 'w') as f:
        json.dump(dict(A=A, B=B, ts0=int(ts[0]), ts1=int(ts[-1]), n=int(len(ts))), f)
    print('\nbanked -> %s' % OUT)
    ka = {(e['conf'], e['cur_tf'], e['bias']) for e in A}
    kb = {(e['conf'], e['cur_tf'], e['bias']) for e in B}
    print('  A only %d | shared %d | B only %d' % (len(ka - kb), len(ka & kb), len(kb - ka)))
    for lbl, S in (('A', A), ('B', B)):
        tf = [e['cur_tf'] for e in S]
        print('  %s: cur_tf med %d min %d max %d | climbs med %d | leg %s'
              % (lbl, int(np.median(tf)), min(tf), max(tf),
                 int(np.median([e['climbs'] for e in S])),
                 {k: sum(1 for e in S if e['leg'] == k) for k in sorted({e['leg'] for e in S})}))


if __name__ == '__main__':
    main()
