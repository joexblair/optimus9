"""report_leash_momtf - spec_label 22_go_20260921.

wsf_leash, three columns added 0920 and the report that prints them.

    momtf_dr      which of the momTF set are momentum-true at wsl_sig_utc, at the row's own dr
    momtf_non_dr  the same set at -wsl_dr
    mom_xfer      the first bar LATER than wsl_sig_utc where `mom_xfer.count_min` or more of the
                  momtf_dr set have left momtf_dr AT THE SAME BAR.  Leaving = no longer
                  momentum-true at the row's dr; it then either shows nothing or shows in
                  momtf_non_dr, which is the whole outcome space.  The walk ends at the dr flip.

JOE'S RULINGS, 0920:
    the momTF set    "reduce the momTFs to only these 3: 10,11,12"
    count_min        "2 is arbitrary. the more TFs I see leaving the dr mom, the more comfortable
                     I'll be" -> banked as mom_xfer.count_min in wsf_dtf_v3_config v8
    same bar         "at the same bar. there's strength in numbers"
    walk end         "dr flip"
    the producer     momentum_true with STRIP-MOM-AT-FENCE on, so a line that has exited the
                     r-momo-fence on the dr side carries no tag

THE IN-PLACE UPDATE IS JOE'S CALL, 0920: "the key isn't changing, so break the no-update rule".
leash_bank.py still says "Nothing is ever updated in place"; that sentence no longer holds for
these three columns.

NOT IN THE CONFIG: the momTF set (10, 11, 12) lives here, not in wsf_dtf_v3_config.
NOT IN THE KEY: mom_xfer.count_min is in_key, but leash_bank.knob_string filters
wdc_section == 'stretchy_leash', so it never reaches wsl_knobs.  A change to the knob overwrites
these rows instead of landing beside them.
"""
import io
import os
import sys

import numpy as np

sys.stdout, _real = io.StringIO(), sys.stdout
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_prelude.py')).read()
     .split("k=int(np.searchsorted")[0])
sys.stdout = _real

from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

MOMTFS = (10, 11, 12)                       # Joe 0920
TABLE = 'wsf_leash'


def momtf(t, d, j):
    """momentum-true on ws{t}r at bar j toward dr d, STRIP-MOM-AT-FENCE on."""
    return W.momentum_true(RA[t], BK[t], CFG, d, j, SEAM[t], t, strip_mom_at_fence=FENCE)[0]


def build(db, cy, count_min):
    """-> [(row, momtf_dr, momtf_non_dr, xfer_bar, left_count, flip_bar, sig_bar)]."""
    rows = db.execute(f'SELECT wsl_pk,wsl_dr,wsl_sig_ms,wsl_sig_utc FROM {TABLE} '
                      f'WHERE wsl_sig_ms IS NOT NULL ORDER BY wsl_sig_ms', fetch=True)
    out = []
    for r in rows:
        k = int(np.searchsorted(ts, int(r['wsl_sig_ms'])))
        d = int(r['wsl_dr'])
        a = [t for t in MOMTFS if momtf(t, d, k)]
        b = [t for t in MOMTFS if momtf(t, -d, k)]
        st = next((x for x in cy if x[0] <= k < x[1]), None)
        flip = st[1] if st else None
        hit, cnt = None, 0
        if flip is not None and len(a) >= count_min:
            for j in range(k + 1, flip):
                c = sum(1 for t in a if not momtf(t, d, j))
                if c >= count_min:
                    hit, cnt = j, c
                    break
        out.append((r, ','.join(map(str, a)), ','.join(map(str, b)), hit, cnt, flip, k))
    return out


def main(write=False):
    db = DatabaseManager(**get_db_config()); db.connect()
    count_min = int(_C['count_min'])
    cy = [s for s in stretches(dr_latch_wob(M[1], Ln(13, 'm'), iw, n - 1, LATCH_W), iw, n)]
    out = build(db, cy, count_min)
    if write:
        db.executemany(f'UPDATE {TABLE} SET momtf_dr=%s, momtf_non_dr=%s, mom_xfer=%s '
                       f'WHERE wsl_pk=%s',
                       [(a, b, U(h) if h is not None else None, int(r['wsl_pk']))
                        for r, a, b, h, _c, _f, _k in out])
    db.disconnect()

    print('leash momTF report   spec_label 22_go_20260921')
    print('  momTF set        ws%s' % ', ws'.join(map(str, MOMTFS)))
    print('  mom_xfer.count_min %d timeframes (wsf_dtf_v3_config v%d)' % (count_min, _C.version))
    print('  producer         momentum_true, STRIP-MOM-AT-FENCE on at the r-momo-fence %g/%g'
          % (FENCE[0], FENCE[1]))
    print('  mom_xfer         first bar after wsl_sig_utc where count_min of the momtf_dr set have')
    print('                   left it AT THE SAME BAR.  Walk ends at the dr flip.  Blank = never')
    print('')
    print('  dr  wsl_sig_utc       momtf_dr   momtf_non_dr  mom_xfer          lag min')
    print('  ' + '-' * 70)
    for r, a, b, h, _c, _f, k in out:
        print('  %+d  %s  %-9s  %-12s  %-16s  %s'
              % (r['wsl_dr'], r['wsl_sig_utc'].strftime('%m-%d %H:%M:%S'), a, b,
                 U(h)[5:] if h is not None else '',
                 '%.1f' % ((h - k) * 5 / 60.0) if h is not None else ''))
    st = [(1 if a else 0, 1 if b else 0, 1 if h is not None else 0) for _r, a, b, h, *_ in out]
    print('')
    print('  rows %d   momtf_dr non-empty %d   momtf_non_dr non-empty %d   mom_xfer stamped %d'
          % (len(out), sum(x[0] for x in st), sum(x[1] for x in st), sum(x[2] for x in st)))
    return 0


if __name__ == '__main__':
    sys.exit(main('--write' in sys.argv))
