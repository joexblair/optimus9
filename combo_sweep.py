"""combo_sweep — rank FEATURE FAMILIES by how well they generalise, not by their best cell. Joe 0803 02:10.

    Joe: "do what you feel is the right next move. keep driving until you run out of combo ideas"

THE INSTRUMENT, AND WHY IT IS THIS ONE
Every individual cell measured tonight died on selection: the momo triple's best cells inverted on the
holdout, and the s4 r x Mage 3-way's best cell was 2.47 sigma out of 154 looked at. Picking a winner from
N cells and then quoting its significance is the error, and it has now happened twice.

So the unit of measurement here is the FAMILY, not the cell. For a family that partitions armed episodes
into cells, the statistic is:

    SIGN-AGREEMENT = of the cells with enough episodes both sides of the split, what fraction keep the
                     SIGN of their lift from in-sample to holdout.

Under the null that the family carries nothing, that is 50%. It cannot be gamed by choosing a cell,
because every qualifying cell counts. It is one number per family and it is reported for every family
tried, including the ones that fail.

PRE-REGISTERED, STATED BEFORE THE SWEEP RUNS
  H1: TF1 net cross direction > 0 AND TF2 net < 0 (the 1-min set crossing up while the 2-min set crosses
      down) marks a LONG-favourable episode. This came out of the s4 r x Mage 3-way as the best cell and
      is therefore NOT established by that run; it is tested here as ONE test with a fixed direction.

EPISODES, NOT BARS. Every family collapses contiguous armed bars sharing the same cell key to their first
bar (rpl_learn: the effective-n gate). Bar counts are not sample sizes.

SPLIT. in-sample 05-18 -> 07-27 03:21, holdout 07-27 03:21 -> now. The holdout was never used to choose
anything in this file.

    python3 combo_sweep.py
"""
import sys, logging, itertools
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
logging.disable(logging.INFO)
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from build_scn import CROSS, SETS

SPLIT = '07-27 03:21:00'
MIN_IN, MIN_HD = 300, 60          # episodes required per cell, each side of the split
TFSLICE = {s: slice(i * 6, i * 6 + 6) for i, (s, _) in enumerate(SETS)}


def load():
    d = DatabaseManager(**get_db_config()); d.connect()
    rows = d.execute(
        "SELECT m.tm_ms,m.tm_utc,m.tm_arm_side sd,m.tm_clean_up cu,m.tm_clean_dn cd,"
        "m.tm_vec_up vu,m.tm_vec_dn vd,c.tc_dir cr,c.tc_age ca,c.tc_n_cross cn,"
        "w.tw_dir wr,w.tw_age wa FROM rpl_tape_momo m "
        "JOIN rpl_tape_cross c ON c.tc_ms=m.tm_ms "
        "JOIN rpl_tape_crossw w ON w.tw_ms=m.tm_ms AND w.tw_wob=8 "
        "WHERE m.tm_armed=1 ORDER BY m.tm_ms", fetch=True)
    d.disconnect()
    return rows


def main():
    rows = load(); n = len(rows)
    ms = np.array([r['tm_ms'] for r in rows], np.int64)
    utc = np.array([r['tm_utc'] for r in rows])
    ins = utc < SPLIT
    cl = {'LONG': np.array([r['cu'] for r in rows], np.int8),
          'SHORT': np.array([r['cd'] for r in rows], np.int8)}
    side = np.array([(r['sd'] or '') for r in rows])
    V = {'LONG': np.array([r['vu'] for r in rows]).view('U1').reshape(n, -1),
         'SHORT': np.array([r['vd'] for r in rows]).view('U1').reshape(n, -1)}
    X = {'raw': np.array([r['cr'] for r in rows]).view('U1').reshape(n, -1),
         'wob8': np.array([r['wr'] for r in rows]).view('U1').reshape(n, -1)}
    A = {'raw': np.array([r['ca'] for r in rows]).view('U1').reshape(n, -1),
         'wob8': np.array([r['wa'] for r in rows]).view('U1').reshape(n, -1)}
    NC = {'raw': np.array([r['cn'] for r in rows], np.int16),
          'wob8': np.array([sum(1 for ch in r['wa'] if ch != '0') for r in rows], np.int16)}
    print('armed bars %d   in-sample %d   holdout %d' % (n, ins.sum(), (~ins).sum()), flush=True)

    net = {det: {s: (X[det][:, sl] == '+').sum(1) - (X[det][:, sl] == '-').sum(1)
                 for s, sl in TFSLICE.items()} for det in X}
    cnt = {det: {s: (X[det][:, sl] != '0').sum(1) for s, sl in TFSLICE.items()} for det in X}

    def evaluate(key, dtag, label, out):
        """key: per-bar cell id array. Collapse to episodes, split, sign-agreement over qualifying cells."""
        c = cl[dtag]
        same = np.r_[False, (key[1:] == key[:-1]) & (ms[1:] == ms[:-1] + 5000)]
        st = ~same
        bi = c[st & ins].mean(); bh = c[st & ~ins].mean()
        agree = tot = 0; best = None; cov_in = 0
        for k in np.unique(key):
            m = st & (key == k)
            mi = m & ins; mh = m & ~ins
            ni, nh = int(mi.sum()), int(mh.sum())
            if ni < MIN_IN or nh < MIN_HD:
                continue
            li = 100 * (c[mi].mean() - bi); lh = 100 * (c[mh].mean() - bh)
            tot += 1; agree += int((li > 0) == (lh > 0)); cov_in += ni
            if best is None or abs(li) > abs(best[2]):
                best = (str(k), ni, li, nh, lh)
        if tot < 4:
            return
        p = agree / tot
        z = (p - 0.5) / np.sqrt(0.25 / tot)
        out.append((label, dtag, tot, agree, 100 * p, z, int(st.sum()), cov_in, best))

    OUT = []
    # ---- pre-registered single test, run first and reported separately ----------------------------
    pre = {}
    for det in ('raw', 'wob8'):
        k = ((net[det]['s1'] > 0) & (net[det]['s2'] < 0)).astype(np.int8)
        same = np.r_[False, (k[1:] == k[:-1]) & (ms[1:] == ms[:-1] + 5000)]
        st = ~same
        for dtag in ('LONG', 'SHORT'):
            c = cl[dtag]
            for tag, msk in (('in', ins), ('hold', ~ins)):
                m = st & (k == 1) & msk
                b = st & msk
                pre[(det, dtag, tag)] = (int(m.sum()), 100 * c[m].mean(), 100 * (c[m].mean() - c[b].mean()))

    # ---- the families ----------------------------------------------------------------------------
    for det in ('raw', 'wob8'):
        for dtag in ('LONG', 'SHORT'):
            for s in ('s30', 's1', 's2', 's4'):
                evaluate(net[det][s], dtag, '%s net-%s' % (det, s), OUT)
                evaluate(cnt[det][s], dtag, '%s count-%s' % (det, s), OUT)
            for a, b in (('s1', 's2'), ('s2', 's4'), ('s30', 's1'), ('s1', 's4')):
                evaluate(net[det][a] * 100 + net[det][b], dtag, '%s net-%s x net-%s' % (det, a, b), OUT)
            rM = np.char.add(np.char.add(X[det][:, CROSS.index('s30_rM')], X[det][:, CROSS.index('s1_rM')]),
                             np.char.add(X[det][:, CROSS.index('s2_rM')], X[det][:, CROSS.index('s4_rM')]))
            evaluate(rM, dtag, '%s rM-vector s30/s1/s2/s4' % det, OUT)
            s4v = np.char.add(np.char.add(X[det][:, 30], X[det][:, 31]),
                              np.char.add(X[det][:, 32], X[det][:, 33]))
            evaluate(s4v, dtag, '%s s4 4-pair vector' % det, OUT)
            evaluate(A[det][:, CROSS.index('s4_rM')], dtag, '%s age s4_rM' % det, OUT)
            evaluate(NC[det], dtag, '%s total cross count' % det, OUT)
            mv = np.array([''.join(r) for r in V[dtag][:, :3]])
            evaluate(mv, dtag, 'momo triple s4/s15/s22', OUT)
            evaluate(np.char.add(mv, net[det]['s4'].astype('U3')), dtag,
                     '%s momo-triple x net-s4' % det, OUT)
            evaluate(np.char.add(mv, (net[det]['s1'] * 100 + net[det]['s2']).astype('U5')), dtag,
                     '%s momo-triple x net-s1 x net-s2' % det, OUT)
            evaluate(np.char.add(side, net[det]['s4'].astype('U3')), dtag,
                     '%s arm-side x net-s4' % det, OUT)
            evaluate(np.char.add(side, mv), dtag, 'arm-side x momo triple', OUT)

    print('\n== PRE-REGISTERED H1: TF1 net > 0 AND TF2 net < 0 ==')
    print('  %-5s %-6s %8s %9s %8s | %8s %9s %8s' %
          ('det', 'dir', 'ep_in', 'clean_in', 'lift_in', 'ep_hold', 'clean_hd', 'lift_hd'))
    for det in ('raw', 'wob8'):
        for dtag in ('LONG', 'SHORT'):
            a = pre[(det, dtag, 'in')]; b = pre[(det, dtag, 'hold')]
            print('  %-5s %-6s %8d %8.2f%% %+8.2f | %8d %8.2f%% %+8.2f'
                  % (det, dtag, a[0], a[1], a[2], b[0], b[1], b[2]))

    seen = set(); U = []
    for r in OUT:
        if (r[0], r[1]) in seen:
            continue
        seen.add((r[0], r[1])); U.append(r)
    U.sort(key=lambda r: -r[5])
    print('\n== FAMILIES ranked by sign-agreement z  (null 50%%, every qualifying cell counts) ==')
    print('%-38s %-6s %5s %7s %7s %9s %s' % ('family', 'dir', 'cells', 'agree%', 'z', 'ep_total', 'best cell (in|hold lift)'))
    for lab, dtag, tot, agree, pct, z, nep, cov, best in U:
        print('%-38s %-6s %5d %6.1f%% %+7.2f %9d   %s in %+.2f | hd %+.2f (n %d|%d)'
              % (lab, dtag, tot, pct, z, nep, best[0], best[2], best[4], best[1], best[3]))


if __name__ == '__main__':
    main()
