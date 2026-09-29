"""report_leash_momtf - spec_label 22_go_20260921.

wsf_leash, three columns added 0920 and the report that prints them.

    momtf_dr      which of the momTF set are momentum-true at wsl_sig_utc, at the row's own dr
    momtf_non_dr  the same set at -wsl_dr
    mom_xfer      the first bar LATER than wsl_sig_utc where `mom_xfer.count_min` or more of the
                  momtf_dr set have left momtf_dr AT THE SAME BAR.  Leaving = no longer
                  momentum-true at the row's dr; it then either shows nothing or shows in
                  momtf_non_dr, which is the whole outcome space.  The walk ends at the dr flip.

AND THREE PER-TF COLUMNS, JOE 0929.  He asked for xfer columns on single timeframes: first
"add 3 more xfer columns that report when 11,10,and 9 fall out of the `momtf_dr`", then, shown both
a per-TF and a chained reading of that, "bank IND 9, and add IND8 and IND7" and "drop 11 and 10.
MOMTFS stays untouched".

    mom_xfer_9    the first bar LATER than wsl_sig_utc where ws9r  is no longer momentum-true
    mom_xfer_8    the same on ws8r
    mom_xfer_7    the same on ws7r

EACH IS ONE LINE, AND THEY ARE INDEPENDENT OF EACH OTHER.  Joe asked directly whether they were
built on a single line; they are - one `momentum_true(RA[t], ...)` call per column, no count, no
chaining, no shared search floor.  That is what makes them different from `mom_xfer`, which is a
COUNT across the momtf_dr set and is not tied to any one line.

ws7, ws8 AND ws9 ARE NOT IN MOMTFS.  They cannot "fall out of momtf_dr" because they were never in
it.  Joe ruled the set stays as it is - "MOMTFS stays untouched" - so these columns report each
line's own momentum exit, independent of set membership.  MOMTFS, momtf_dr, momtf_non_dr and
mom_xfer are all unchanged by this.

NULL MEANS TWO DIFFERENT THINGS, exactly as it already does for mom_xfer: either the line was not
momentum-true at the row's dr AT the sig bar, or it was and never left before the dr flip.  The
report tells them apart - `not tr` and `never` - the column cannot.  Measured over the banked 121
v7 rows: ws9 not-true 44 / exits 76 / never 1;  ws8 and ws7 print in the report.

THE WALK END AND THE PRODUCER ARE JOE'S 0920 RULINGS, UNCHANGED: the walk ends at the dr flip, and
the producer is momentum_true with STRIP-MOM-AT-FENCE on.

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

MOMTFS = (10, 11, 12)                       # Joe 0920. Joe 0929: "MOMTFS stays untouched"
XFER_TFS = (9, 8, 7)                        # Joe 0929, the per-TF xfer columns. NOT in MOMTFS
TABLE = 'wsf_leash'
XCOL = {t: 'mom_xfer_%d' % t for t in XFER_TFS}


def ensure_columns(db):
    """Add the per-TF xfer columns if they are not there yet. Idempotent.

    They sit immediately after wsl_sig_ms so they read next to wsl_sig_utc, which is where Joe
    asked for them ("the 3 new columns will live to the right of wsl_sig_utc"). Adding a column is
    additive - no row is rewritten and no existing column moves.
    """
    have = {r['Field'] for r in db.execute('SHOW COLUMNS FROM %s' % TABLE, fetch=True)}
    after = 'wsl_sig_ms'
    for t in XFER_TFS:                       # 9, 8, 7 - each after the previous, so they read 9 8 7
        c = XCOL[t]
        if c not in have:
            db.execute('ALTER TABLE %s ADD COLUMN %s DATETIME(3) NULL AFTER %s' % (TABLE, c, after))
        after = c
    return [XCOL[t] for t in XFER_TFS if XCOL[t] not in have]


def momtf(t, d, j):
    """momentum-true on ws{t}r at bar j toward dr d, STRIP-MOM-AT-FENCE on."""
    return W.momentum_true(RA[t], BK[t], CFG, d, j, SEAM[t], t, strip_mom_at_fence=FENCE)[0]


def per_tf_xfer(t, d, k, flip):
    """ws{t}r's OWN momentum exit after bar `k`, walking to the dr flip. -> (bar or None, why).

    `why` is 'exit', 'not tr' (the line was not momentum-true at `k`, so there is nothing to leave)
    or 'never' (it was, and it held all the way to the flip). The column stores the bar; only the
    report carries `why`.
    """
    if not momtf(t, d, k):
        return None, 'not tr'
    if flip is None:
        return None, 'never'
    j = next((x for x in range(k + 1, flip) if not momtf(t, d, x)), None)
    return (j, 'exit') if j is not None else (None, 'never')


def build(db, cy, count_min):
    """-> [(row, momtf_dr, momtf_non_dr, xfer_bar, left_count, flip_bar, sig_bar, per_tf)].

    `per_tf` is {tf: (bar or None, why)} for XFER_TFS - Joe 0929's single-line columns.
    """
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
        pt = {t: per_tf_xfer(t, d, k, flip) for t in XFER_TFS}
        out.append((r, ','.join(map(str, a)), ','.join(map(str, b)), hit, cnt, flip, k, pt))
    return out


def main(write=False):
    db = DatabaseManager(**get_db_config()); db.connect()
    added = ensure_columns(db)
    count_min = int(_C['count_min'])
    cy = [s for s in stretches(dr_latch_wob(M[1], Ln(13, 'm'), iw, n - 1, LATCH_W), iw, n)]
    out = build(db, cy, count_min)
    if write:
        cols = ', '.join('%s=%%s' % XCOL[t] for t in XFER_TFS)
        db.executemany(f'UPDATE {TABLE} SET momtf_dr=%s, momtf_non_dr=%s, mom_xfer=%s, {cols} '
                       f'WHERE wsl_pk=%s',
                       [(a, b, U(h) if h is not None else None)
                        + tuple(U(pt[t][0]) if pt[t][0] is not None else None for t in XFER_TFS)
                        + (int(r['wsl_pk']),)
                        for r, a, b, h, _c, _f, _k, pt in out])
    db.disconnect()

    print('leash momTF report   spec_label 22_go_20260921')
    print('  momTF set        ws%s' % ', ws'.join(map(str, MOMTFS)))
    print('  mom_xfer.count_min %d timeframes (wsf_dtf_v3_config v%d)' % (count_min, _C.version))
    print('  producer         momentum_true, STRIP-MOM-AT-FENCE on at the r-momo-fence %g/%g'
          % (FENCE[0], FENCE[1]))
    print('  mom_xfer         first bar after wsl_sig_utc where count_min of the momtf_dr set have')
    print('                   left it AT THE SAME BAR.  Walk ends at the dr flip.  Blank = never')
    print('  %s  Joe 0929. EACH ON ONE LINE, independent of each other and of'
          % ', '.join(XCOL[t] for t in XFER_TFS))
    print('                   MOMTFS: the first bar after wsl_sig_utc where ws{tf}r is no longer')
    print('                   momentum-true at the row dr.  not tr = not momentum-true AT the sig')
    print('                   bar.  never = it was, and held to the dr flip.  Both store NULL.')
    if added:
        print('  columns added    %s' % ', '.join(added))
    print('')
    hdr = ''.join('%-17s' % ('%s  lag' % XCOL[t]) for t in XFER_TFS)
    print('  dr  wsl_sig_utc       momtf_dr   momtf_non_dr  mom_xfer          lag min   ' + hdr)
    print('  ' + '-' * (70 + 17 * len(XFER_TFS)))
    for r, a, b, h, _c, _f, k, pt in out:
        cells = ''
        for t in XFER_TFS:
            j, why = pt[t]
            cells += '%-17s' % (('%s %4.1f' % (U(j)[11:], (j - k) * 5 / 60.0))
                                if j is not None else why)
        print('  %+d  %s  %-9s  %-12s  %-16s  %-8s  %s'
              % (r['wsl_dr'], r['wsl_sig_utc'].strftime('%m-%d %H:%M:%S'), a, b,
                 U(h)[5:] if h is not None else '',
                 '%.1f' % ((h - k) * 5 / 60.0) if h is not None else '', cells))
    st = [(1 if a else 0, 1 if b else 0, 1 if h is not None else 0) for _r, a, b, h, *_ in out]
    print('')
    print('  rows %d   momtf_dr non-empty %d   momtf_non_dr non-empty %d   mom_xfer stamped %d'
          % (len(out), sum(x[0] for x in st), sum(x[1] for x in st), sum(x[2] for x in st)))
    for t in XFER_TFS:
        w = [pt[t][1] for *_x, pt in out]
        print('  %-12s stamped %d   not momentum-true at the sig bar %d   never left %d'
              % (XCOL[t], w.count('exit'), w.count('not tr'), w.count('never')))
    return 0


if __name__ == '__main__':
    sys.exit(main('--write' in sys.argv))
