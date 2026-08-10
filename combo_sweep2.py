"""combo_sweep2 — family sweep with the instrument defect fixed, and the HTF set included. Joe 0803 02:55.

THE FIX (rpl_learn ln_pk 54). combo_sweep.py scored a family by sign-agreement against a 50% null. It
ranked `arm-side x net-s4` top at 89.5% over 19 cells, z +3.44 — and unpacking it showed every hi cell
positive and every lo cell negative across all 13 values of net-s4. net-s4 contributed nothing; it
partitioned ONE variable into 19 cells that all inherited its sign. Agreement counted a partition of
something real as a discovery.

    FIX: every lift is computed WITHIN its arm-side stratum, against that stratum's own base. A family
    that is arm-side wearing a partition now scores 50%, because its cells have no lift left to agree on.

Arm-side is the control because it is the one variable measured to carry a real effect tonight
(rpl_learn ln_pk 53: AGAINST the breach beats WITH by 1.38 pts in-sample, 2.68 holdout).

THE HTF SET, tested for the first time. Joe's handover names it as the thing to look at when predictions
fail — "something bigger cutting an opposing path" — and every dimension measured so far sits at s4 or
below. rpl_tape_htf carries h30/h45/h60/h90 per bar with their bands, the ladder ordering, the OOB count
and the h30 5-min slope sign.

EPISODES, NOT BARS. Contiguous armed bars sharing a cell key collapse to their first bar.
SPLIT. in-sample 05-18 -> 07-27 03:21, holdout after. The holdout chose nothing.

    python3 combo_sweep2.py
"""
import sys, logging
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
logging.disable(logging.INFO)
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from build_scn import CROSS, SETS

SPLIT = '07-27 03:21:00'
MIN_IN, MIN_HD = 300, 60
TFSLICE = {s: slice(i * 6, i * 6 + 6) for i, (s, _) in enumerate(SETS)}


def main():
    d = DatabaseManager(**get_db_config()); d.connect()
    rows = d.execute(
        "SELECT m.tm_ms,m.tm_utc,m.tm_arm_side sd,m.tm_clean_up cu,m.tm_clean_dn cd,"
        "m.tm_vec_up vu,m.tm_vec_dn vd,c.tc_dir cr,w.tw_dir wr,"
        "h.th_band hb,h.th_stack hs,h.th_oob_n ho,h.th_slope hp,"
        "h.th_h30 h30,h.th_h90 h90 FROM rpl_tape_momo m "
        "JOIN rpl_tape_cross c ON c.tc_ms=m.tm_ms "
        "JOIN rpl_tape_crossw w ON w.tw_ms=m.tm_ms AND w.tw_wob=8 "
        "JOIN rpl_tape_htf h ON h.th_ms=m.tm_ms "
        "WHERE m.tm_armed=1 ORDER BY m.tm_ms", fetch=True)
    d.disconnect()
    n = len(rows)
    ms = np.array([r['tm_ms'] for r in rows], np.int64)
    utc = np.array([r['tm_utc'] for r in rows]); ins = utc < SPLIT
    side = np.array([(r['sd'] or '') for r in rows])
    cl = {'LONG': np.array([r['cu'] for r in rows], np.int8),
          'SHORT': np.array([r['cd'] for r in rows], np.int8)}
    V = {'LONG': np.array([r['vu'] for r in rows]).view('U1').reshape(n, -1),
         'SHORT': np.array([r['vd'] for r in rows]).view('U1').reshape(n, -1)}
    X = {'raw': np.array([r['cr'] for r in rows]).view('U1').reshape(n, -1),
         'wob8': np.array([r['wr'] for r in rows]).view('U1').reshape(n, -1)}
    HB = np.array([r['hb'] for r in rows]); HS = np.array([r['hs'] for r in rows])
    HO = np.array([r['ho'] for r in rows], np.int8); HP = np.array([r['hp'] for r in rows])
    H30 = np.array([r['h30'] if r['h30'] is not None else np.nan for r in rows], float)
    H90 = np.array([r['h90'] if r['h90'] is not None else np.nan for r in rows], float)
    print('armed bars %d   in-sample %d   holdout %d' % (n, ins.sum(), (~ins).sum()), flush=True)
    net = {det: {s: (X[det][:, sl] == '+').sum(1) - (X[det][:, sl] == '-').sum(1)
                 for s, sl in TFSLICE.items()} for det in X}

    OUT = []

    def ev(key, dtag, label):
        """Lift measured WITHIN each arm-side stratum, so arm-side itself cannot produce agreement."""
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
            return
        p = agree / tot
        OUT.append((label, dtag, tot, 100 * p, (p - 0.5) / np.sqrt(0.25 / tot), best))

    for dtag in ('LONG', 'SHORT'):
        # ---- HTF families, first time tested -----------------------------------------------------
        ev(HB, dtag, 'HTF band vector h30/45/60/90')
        ev(HS, dtag, 'HTF ladder order A/D/M')
        ev(HO.astype('U2'), dtag, 'HTF count OOB 0-4')
        ev(HP, dtag, 'HTF h30 5-min slope sign')
        ev(np.char.add(HS, HP), dtag, 'HTF ladder x h30 slope')
        ev(np.char.add(HS, HO.astype('U2')), dtag, 'HTF ladder x oob-count')
        ev(np.char.add(HB, HP), dtag, 'HTF band x h30 slope')
        gap = np.where(np.isfinite(H30 - H90), np.clip(((H30 - H90) / 15).astype(int), -6, 6), 99)
        ev(gap.astype('U3'), dtag, 'HTF h30-h90 gap /15')
        mv = np.array([''.join(r) for r in V[dtag][:, :3]])
        ev(np.char.add(HS, mv), dtag, 'HTF ladder x momo triple')
        ev(np.char.add(HP, mv), dtag, 'HTF h30 slope x momo triple')
        for det in ('raw', 'wob8'):
            ev(np.char.add(HS, net[det]['s4'].astype('U3')), dtag, '%s HTF ladder x net-s4' % det)
            ev(np.char.add(HP, net[det]['s4'].astype('U3')), dtag, '%s HTF h30 slope x net-s4' % det)
        # ---- the previously top families, re-scored inside arm-side ------------------------------
        ev(mv, dtag, 'momo triple s4/s15/s22')
        for det in ('raw', 'wob8'):
            ev(net[det]['s4'], dtag, '%s net-s4' % det)
            ev(net[det]['s1'] * 100 + net[det]['s2'], dtag, '%s net-s1 x net-s2' % det)
            ev(net[det]['s30'], dtag, '%s net-s30' % det)

    seen = set(); U = []
    for r in OUT:
        if (r[0], r[1]) in seen:
            continue
        seen.add((r[0], r[1])); U.append(r)
    U.sort(key=lambda r: -r[4])
    print('\n== FAMILIES, lift measured WITHIN arm-side  (null 50%%; arm-side alone now scores ~50) ==')
    print('%-36s %-6s %5s %7s %7s  %s' % ('family', 'dir', 'cells', 'agree%', 'z', 'best cell (in | hold)'))
    for lab, dtag, tot, pct, z, best in U:
        print('%-36s %-6s %5d %6.1f%% %+7.2f  %-12s in %+6.2f | hd %+6.2f  (n %d|%d)'
              % (lab, dtag, tot, pct, z, best[0], best[2], best[4], best[1], best[3]))


if __name__ == '__main__':
    main()
