"""seq_sweep — test the SETUP families: reductions of the Mage arrival ordering. Joe 0803 03:40.

THE SPARSITY PROBLEM, MEASURED FIRST. rpl_tape_seq banks the full arrival ordering of 10 Mages, and the
tape shows 22,973-25,338 DISTINCT orderings. As a raw key that is useless — the same trap the 9-line momo
vector fell into, where full agreement was too rare to carry an episode count. So the ordering must be
REDUCED, and the reductions are where Joe's own notes live:

  BOBBING  "if a Mage is bobbing on a boundary line, a higher TF Mage is making it's way to the same
           boundary" -> htf_closing: are the HTF arrival ages SMALLER than s4's, i.e. did the slower
           Mages reach this boundary more recently than the mid one
  GATHER   "their lines will gather to a boundary before they push away from it" -> gather_span: the
           spread between the most recent and the 5th most recent arrival. A tight span IS the gather
  DOMINOES rpl_dominoes dm_dom_strict/loose/reverse -> mono: does the arrival order run fastest-first
           (the ladder falling in sequence), slowest-first, or neither

EVERY FEATURE IS SIDE-RELATIVE. An armed bar reads the ordering at the boundary its Mage breached, so a
hi-armed bar uses the HI arrivals and a lo-armed bar the LO ones. Comparing a hi setup against a lo setup
would be comparing two different events.

THE INSTRUMENT IS UNCHANGED, and it is the one that survived the night:
  - lifts measured INSIDE the arm-side stratum, so arm-side cannot leak in (rpl_learn ln_pk 54)
  - contiguous armed bars sharing a cell collapse to ONE episode (the effective-n gate)
  - in-sample 05-18 -> 07-27 03:21, holdout after; the holdout chooses nothing
  - families scored by sign-agreement over ALL qualifying cells, never by their best cell

    python3 seq_sweep.py
"""
import sys, logging
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
logging.disable(logging.INFO)
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

SPLIT = '07-27 03:21:00'
MIN_IN, MIN_HD = 300, 60
LAD = ['g5', 'g15', 's30', 's1', 's2', 's4', 'h30', 'h45', 'h60', 'h90']
BIG = 10 ** 9


def bucket(v, edges):
    """index of the first edge v is <= ; len(edges) if beyond. NaN/none -> -1."""
    out = np.full(len(v), len(edges), np.int8)
    for i, e in enumerate(reversed(edges)):
        out[v <= e] = len(edges) - 1 - i
    out[~np.isfinite(v)] = -1
    return out


def main():
    d = DatabaseManager(**get_db_config()); d.connect()
    acols = ','.join('q.sq_a_h_%s ah_%s' % (l, l) for l in LAD)
    lcols = ','.join('q.sq_a_l_%s al_%s' % (l, l) for l in LAD)
    dcols = ','.join('q.sq_d_h_%s dh_%s' % (l, l) for l in LAD)
    ecols = ','.join('q.sq_d_l_%s dl_%s' % (l, l) for l in LAD)
    rows = d.execute(
        "SELECT m.tm_ms,m.tm_utc,m.tm_arm_side sd,m.tm_clean_up cu,m.tm_clean_dn cd,"
        + acols + ',' + lcols + ',' + dcols + ',' + ecols +
        " FROM rpl_tape_momo m JOIN rpl_tape_seq q ON q.sq_ms=m.tm_ms "
        "WHERE m.tm_armed=1 ORDER BY m.tm_ms", fetch=True)
    d.disconnect()
    n = len(rows)
    ms = np.array([r['tm_ms'] for r in rows], np.int64)
    utc = np.array([r['tm_utc'] for r in rows]); ins = utc < SPLIT
    side = np.array([(r['sd'] or '') for r in rows])
    cl = {'LONG': np.array([r['cu'] for r in rows], np.int8),
          'SHORT': np.array([r['cd'] for r in rows], np.int8)}
    hi = side == 'hi'

    def pick(pfx_h, pfx_l):
        """side-relative matrix (n,10): hi-armed bars take the HI column, lo-armed the LO one."""
        H = np.column_stack([[(r['%s_%s' % (pfx_h, l)] if r['%s_%s' % (pfx_h, l)] is not None else BIG)
                              for l in LAD] for r in rows][0:0]) if False else None
        A = np.empty((n, len(LAD)), np.int64)
        for k, l in enumerate(LAD):
            a = np.array([(r['%s_%s' % (pfx_h, l)] if r['%s_%s' % (pfx_h, l)] is not None else BIG) for r in rows],
                         np.int64)
            b = np.array([(r['%s_%s' % (pfx_l, l)] if r['%s_%s' % (pfx_l, l)] is not None else BIG) for r in rows],
                         np.int64)
            A[:, k] = np.where(hi, a, b)
        return A

    ARR = pick('ah', 'al')          # bars since arrival at the ARMED boundary
    DEP = pick('dh', 'dl')          # bars since departure from it
    print('armed bars %d   in-sample %d   holdout %d' % (n, ins.sum(), (~ins).sum()), flush=True)
    print('arrival ages, median bars by line:  %s'
          % '  '.join('%s=%d' % (l, int(np.median(ARR[:, k][ARR[:, k] < BIG]))) for k, l in enumerate(LAD)),
          flush=True)

    order = np.argsort(ARR, axis=1, kind='stable')
    rankpos = np.empty_like(order)
    np.put_along_axis(rankpos, order, np.arange(len(LAD))[None, :].repeat(n, 0), axis=1)
    srt = np.sort(ARR, axis=1)

    F = {}
    F['first arrival, which line'] = np.array(LAD, dtype='U4')[order[:, 0]]
    F['first TWO arrivals, ordered'] = np.char.add(np.array(LAD, dtype='U5')[order[:, 0]],
                                                   np.array(LAD, dtype='U5')[order[:, 1]])
    blk = np.array(['L', 'L', 'L', 'M', 'M', 'M', 'H', 'H', 'H', 'H'])
    F['first arrival, which BLOCK'] = blk[order[:, 0]]
    F['first THREE blocks, ordered'] = np.char.add(np.char.add(blk[order[:, 0]], blk[order[:, 1]]),
                                                   blk[order[:, 2]])
    lad_idx = np.arange(len(LAD))
    cov = ((rankpos - rankpos.mean(1, keepdims=True)) * (lad_idx - lad_idx.mean())).sum(1)
    F['DOMINOES monotone A/D/M'] = np.where(cov > 12, 'A', np.where(cov < -12, 'D', 'M'))
    span = np.where(srt[:, 4] >= BIG, np.nan, (srt[:, 4] - srt[:, 0]).astype(float))
    F['GATHER span, 5 fastest arrivals'] = bucket(span, [12, 36, 120, 360, 1080]).astype('U3')
    s4a = ARR[:, LAD.index('s4')].astype(float); s4a[s4a >= BIG] = np.nan
    hmin = ARR[:, 6:].min(1).astype(float); hmin[hmin >= BIG] = np.nan
    F['BOBBING htf-vs-s4 age gap'] = bucket(hmin - s4a, [-1080, -360, -60, 60, 360, 1080]).astype('U3')
    F['BOBBING htf arrived before s4'] = np.where(np.isfinite(hmin - s4a), (hmin < s4a).astype('U2'), '-')
    g5a = ARR[:, 0].astype(float); g5a[g5a >= BIG] = np.nan
    g5d = DEP[:, 0].astype(float); g5d[g5d >= BIG] = np.nan
    F['g5 currently OOB at this boundary'] = np.where(np.isfinite(g5a - g5d), (g5a < g5d).astype('U2'), '-')
    F['s4 arrival age, bucketed'] = bucket(s4a, [60, 180, 600, 1800, 7200]).astype('U3')
    F['GATHER span x DOMINOES'] = np.char.add(F['GATHER span, 5 fastest arrivals'],
                                              F['DOMINOES monotone A/D/M'])
    F['first block x DOMINOES'] = np.char.add(F['first arrival, which BLOCK'],
                                              F['DOMINOES monotone A/D/M'])
    F['BOBBING gap x GATHER span'] = np.char.add(F['BOBBING htf-vs-s4 age gap'],
                                                 F['GATHER span, 5 fastest arrivals'])

    OUT = []
    for lab, key in F.items():
        for dtag in ('LONG', 'SHORT'):
            c = cl[dtag]
            same = np.r_[False, (key[1:] == key[:-1]) & (ms[1:] == ms[:-1] + 5000)]
            st = ~same
            agree = tot = 0; best = None
            for s in ('hi', 'lo'):
                sm = st & (side == s)
                bi = c[sm & ins].mean(); bh = c[sm & ~ins].mean()
                for k in np.unique(key[sm]):
                    m = sm & (key == k)
                    mi = m & ins; mh = m & ~ins
                    ni, nh = int(mi.sum()), int(mh.sum())
                    if ni < MIN_IN or nh < MIN_HD:
                        continue
                    li = 100 * (c[mi].mean() - bi); lh = 100 * (c[mh].mean() - bh)
                    tot += 1; agree += int((li > 0) == (lh > 0))
                    if best is None or abs(li) > abs(best[2]):
                        best = ('%s|%s' % (s, k), ni, li, nh, lh)
            if tot < 4:
                continue
            p = agree / tot
            OUT.append((lab, dtag, tot, 100 * p, (p - 0.5) / np.sqrt(0.25 / tot), best))
    OUT.sort(key=lambda r: -r[4])
    print('\n== SETUP FAMILIES, lift inside arm-side, episodes, in-sample -> holdout ==')
    print('%-34s %-6s %5s %7s %7s  %s' % ('family', 'dir', 'cells', 'agree%', 'z', 'best cell (in | hold)'))
    for lab, dtag, tot, pct, z, best in OUT:
        print('%-34s %-6s %5d %6.1f%% %+7.2f  %-14s in %+6.2f | hd %+6.2f  (n %d|%d)'
              % (lab, dtag, tot, pct, z, best[0], best[2], best[4], best[1], best[3]))
    zs = np.array([r[4] for r in OUT])
    print('\n%d family-direction tests   mean z %+.3f   sd %.3f   z>0 %d   z<0 %d'
          % (len(zs), zs.mean(), zs.std(ddof=1), int((zs > 0).sum()), int((zs < 0).sum())))
    print('Bonferroni for %d tests needs z ~ %.2f' % (len(zs), abs(np.percentile(np.random.randn(200000), 100 * (1 - 0.025 / len(zs))))))


if __name__ == '__main__':
    main()
