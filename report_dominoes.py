"""report_dominoes — re-derive every §9 headline from rpl_dominoes. DB-only, no rebuild, no build imports.

Precedent: report_exhv2.py. The numbers in docs/260802_handover.md §9 were measured on `A ungated` (the raw
s15x X s15m cross) and are void. rpl_dominoes now holds ONE configuration — REWALK 2 + gcs15 confirm — so
every figure below is that mechanic's own.

WHAT IS PRINTED
  1  confirm lag        dm_sig_ms - dm_s15x_ms. The cost of the confirm, in minutes
  2  dominoes detector  precision / base / lift for strict, loose and reverse, on 3 slices
                        base      = P(dm_mfe_side) on the slice
                        precision = P(dm_mfe_side | detector fired)
                        lift      = precision / base
  3  the trade          ONE causal exit. Joe 0802: lookahead numbers are meaningless, so the dm_c* pair
                        is gone and the 240 s test is per-bar/backward (B.oob_qualified)
  3b MAE / MFE          the entry judged on excursion, which does not depend on the exit rule
  4  the reframe        strict fires split by dm_mfe_side: is it an entry-quality filter or an
                        MFE-side detector

SLICES  ALL = every row.  OLD / FRESH split at 06-04, matching §9(2).

    python3 report_dominoes.py
"""
import sys
import numpy as np
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

SPLIT = '06-04'                     # OLD < SPLIT <= FRESH, on dm_sig_utc '%m-%d %H:%M:%S'


def med(v):
    v = np.asarray([x for x in v if x is not None], float)
    return float(np.median(v)) if len(v) else float('nan')


def mean(v):
    v = np.asarray([x for x in v if x is not None], float)
    return float(np.mean(v)) if len(v) else float('nan')


def main(argv):
    d = DatabaseManager(**get_db_config()); d.connect()
    rows = d.execute('SELECT * FROM rpl_dominoes ORDER BY dm_sig_ms', fetch=True)
    modes = sorted({int(x['dm_rewalk']) for x in rows})
    d.disconnect()

    print('')
    print('rpl_dominoes  %d rows  |  dm_rewalk present: %s' % (len(rows), modes))
    if len(modes) != 1 or modes[0] != 2:
        print('  !! expected ONE mode, REWALK 2. The table is not on the approved configuration.')
    if not rows:
        return

    # --- 1  confirm lag ---------------------------------------------------------------------------
    lag = [(x['dm_sig_ms'] - x['dm_s15x_ms']) / 60000.0 for x in rows if x['dm_s15x_ms'] is not None]
    print('')
    print('CONFIRM LAG  gcs15 signal minus s15 anchor, minutes')
    print('  n %d   med %.2f   mean %.2f   min %.2f   max %.2f   zero-lag rows %d'
          % (len(lag), med(lag), mean(lag), min(lag), max(lag), sum(1 for v in lag if v == 0)))

    SL = [('ALL  ', rows),
          ('OLD  ', [x for x in rows if (x['dm_sig_utc'] or '') < SPLIT]),
          ('FRESH', [x for x in rows if (x['dm_sig_utc'] or '') >= SPLIT])]

    # --- 2  the detector --------------------------------------------------------------------------
    print('')
    print('DOMINOES DETECTOR vs the MFE-side base rate')
    H = '  slice   n    base           strict n/prec/lift      loose n/prec/lift       reverse n/prec/lift'
    print(H); print('  ' + '-' * (len(H) - 2))
    for nm, sub in SL:
        if not sub:
            print('  %s  (empty slice)' % nm); continue
        base = np.mean([int(x['dm_mfe_side']) for x in sub])
        cells = []
        for col in ('dm_dom_strict', 'dm_dom_loose', 'dm_dom_reverse'):
            f = [x for x in sub if int(x[col] or 0)]
            if not f:
                cells.append('%3d      -       -   ' % 0); continue
            p = np.mean([int(x['dm_mfe_side']) for x in f])
            cells.append('%3d   %5.1f%%   %5.2fx' % (len(f), 100 * p, (p / base) if base else float('nan')))
        print('  %s %3d  %5.1f%%   %s  %s  %s' % (nm, len(sub), 100 * base, cells[0], cells[1], cells[2]))

    # --- 3  the trade, ONE causal exit ------------------------------------------------------------
    # The dm_c* lookahead pair is GONE (Joe 0802: "no need to report lookahead numbers - they're
    # meaningless"). The 240 s test is now per-bar and backward, so dm_exit_* IS the causal exit.
    print('')
    print('THE TRADE  exit = the next bar at which s4Mage HAS BEEN OOB for 240 s. Causal.')
    H = '  %-34s %4s %9s %10s %9s %7s' % ('', 'n', 'ret med', 'ret mean', 'ret sum', 'win%')
    print(H); print('  ' + '-' * (len(H) - 2))
    r = [x['dm_ret'] for x in rows if x['dm_ret'] is not None]
    w = 100.0 * sum(1 for v in r if v > 0) / len(r) if r else float('nan')
    print('  %-34s %4d %+9.3f %+10.3f %+9.2f %7.1f' % ('ALL', len(r), med(r), mean(r), sum(r), w))

    # --- 3b  MAE / MFE ----------------------------------------------------------------------------
    # Joe 0802: "MAE and MFE reporting is exactly what we need for now" - the exit rule is rudimentary,
    # so the realised return judges the exit, not the entry. Excursion does not.
    # ratio = MFE/MAE per row, then the MEDIAN of those. Rows with MAE <= 1e-9 are excluded from the
    # ratio only (they still count in n) - same guard build_exh_stat uses.
    SPL = [('ALL', lambda x: True),
           ('OLD  sig < 06-04', lambda x: (x['dm_sig_utc'] or '') < SPLIT),
           ('FRESH sig >= 06-04', lambda x: (x['dm_sig_utc'] or '') >= SPLIT),
           ('MFE-side = 1', lambda x: int(x['dm_mfe_side']) == 1),
           ('MFE-side = 0', lambda x: int(x['dm_mfe_side']) == 0),
           ('strict dominoes fired', lambda x: int(x['dm_dom_strict'] or 0) == 1),
           ('strict did not fire', lambda x: int(x['dm_dom_strict'] or 0) == 0),
           ('reverse order fired', lambda x: int(x['dm_dom_reverse'] or 0) == 1),
           ('SHORT', lambda x: x['dm_dir'] == 'SHORT'),
           ('LONG', lambda x: x['dm_dir'] == 'LONG')]
    for tag, lbl in (('', 'signal bar -> the causal exit'),):
        print('')
        print('MAE / MFE   %s' % lbl)
        H = ('  %-22s %4s %8s %8s %8s %8s %8s %9s %9s'
             % ('split', 'n', 'MAE med', 'MAE p90', 'MFE med', 'MFE p90', 'ratio', 'hold med', 'MFE>MAE'))
        print(H); print('  ' + '-' * (len(H) - 2))
        for nm, f in SPL:
            sub = [x for x in rows if f(x)]
            if not sub:
                print('  %-22s %4d   (empty)' % (nm, 0)); continue
            a = [x['dm_%smae' % tag] for x in sub if x['dm_%smae' % tag] is not None]
            m = [x['dm_%smfe' % tag] for x in sub if x['dm_%smfe' % tag] is not None]
            h = [x['dm_%shold_min' % tag] for x in sub if x['dm_%shold_min' % tag] is not None]
            rt = [x['dm_%smfe' % tag] / x['dm_%smae' % tag] for x in sub
                  if x['dm_%smae' % tag] is not None and x['dm_%smae' % tag] > 1e-9
                  and x['dm_%smfe' % tag] is not None]
            bt = [1 for x in sub if x['dm_%smfe' % tag] is not None and x['dm_%smae' % tag] is not None
                  and x['dm_%smfe' % tag] > x['dm_%smae' % tag]]
            p90 = lambda v: float(np.percentile(v, 90)) if v else float('nan')
            print('  %-22s %4d %8.3f %8.3f %8.3f %8.3f %8.2f %9.1f %8.1f%%'
                  % (nm, len(sub), med(a), p90(a), med(m), p90(m), med(rt), med(h),
                     100.0 * len(bt) / len(sub)))

    # --- 4  the reframe ---------------------------------------------------------------------------
    print('')
    print('THE REFRAME  §9(2) last bullet: entry-quality filter, or MFE-side detector?')
    H = '  strict fires        n    win%   ret med   MAE med   MFE med    ratio'
    print(H); print('  ' + '-' * (len(H) - 2))
    fired = [x for x in rows if int(x['dm_dom_strict'] or 0)]
    for lbl, sub in (('MFE-side     ', [x for x in fired if int(x['dm_mfe_side'])]),
                     ('non-MFE-side ', [x for x in fired if not int(x['dm_mfe_side'])])):
        r = [x['dm_ret'] for x in sub if x['dm_ret'] is not None]
        if not r:
            print('  %s  (no rows)' % lbl); continue
        w = 100.0 * sum(1 for v in r if v > 0) / len(r)
        rt = [x['dm_mfe'] / x['dm_mae'] for x in sub
              if x['dm_mae'] is not None and x['dm_mae'] > 1e-9 and x['dm_mfe'] is not None]
        print('  %s %4d   %4.1f   %+7.3f   %6.3f   %6.3f   %6.2f'
              % (lbl, len(sub), w, med(r), med([x['dm_mae'] for x in sub]),
                 med([x['dm_mfe'] for x in sub]), med(rt)))
    print('')


if __name__ == '__main__':
    main(sys.argv[1:])
