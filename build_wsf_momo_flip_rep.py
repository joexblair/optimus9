"""build_wsf_momo_flip_rep — the table behind the wsf-momo-flip-rep report.

WHY. Joe 0904: "going forward, the report will be in a db table". Until now the report existed
only as two text files that the next run overwrote, so no knob change could be compared against
the one before it.

WHAT IT HOLDS. Joe 0904, answering how the table should be shaped: "the same format as
wsf-momo-flip-rep-B.txt". So the row is variant B's row - the twelve printed columns - plus the
exact bar timestamps behind the three rounded ones, so a row can be traced back to a bar.

ALONGSIDE, NOT INSTEAD. Joe 0904: "alongside". The report still writes
wsf-momo-flip-rep-A.txt and wsf-momo-flip-rep-B.txt.

THE KNOB SET IS ONE COLUMN. Joe 0904: "the key should be in one column so that I can easily
filter the version. you can see an example of this in `wsf_event_mark`.`wem_knobs`". That column
holds strings like `kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_...`, so `wmf_knobs` uses the same
shape - a short tag then its value, joined by underscores:

    vB_mw15_xwc5_xw1_hi85_lo15_bv1_kw6_sl1.2_r20.7

    v      the variant - which layout produced the row. 'A' can be banked later, no migration
    mw     the momentum wob on ws30/ws45/ws60, bars. Moves the ROW SET
    xwc    the wob on the ws10 x-crosses-r detector, bars. Moves the B column
    xw     the wob on the [m,x] cross searches, bars. Moves the `first ws10 cross` column
    hi/lo  the oob boundary at dr +1 and dr -1, %B points. Moves the B column
    bv     the momo_config version every verdict was computed under
    kw/sl/r2  that bank's k_window, slope floor and straightness floor, spelled out so the string
              says what it was without a join. wem_knobs spells its bank knobs out the same way

THE UNIQUE KEY is (wmf_knobs, wmf_utc, wmf_line, wmf_dr). Every knob that moves a row is inside
wmf_knobs, so the next knob change lands beside this one instead of overwriting it.
KNOBS() BUILDS THE STRING. A caller that does not pass a knob cannot build one.

WHAT IS NOT IN THE KEY, and why. FLIP_TFS, FALSE_TFS, STATE_TFS, HTF_SEQ and the line specs are
the report's SHAPE, not knobs Joe sweeps. If any of them becomes a swept knob it joins the key
then, not now.

    python3 build_wsf_momo_flip_rep.py            create the table if absent
    python3 build_wsf_momo_flip_rep.py --show     print what is banked, newest knob set first
"""
import sys

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DDL = '''CREATE TABLE IF NOT EXISTS wsf_momo_flip_rep (
    wmf_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    -- THE KNOB SET, one column, shaped like wsf_event_mark.wem_knobs. Every knob that moves a
    -- row is in here, and this column is the first part of the unique key
    wmf_knobs         VARCHAR(160) NOT NULL, -- eg 'vB_mw15_xwc5_xw1_hi85_lo15_bv1_kw6_sl1.2_r20.7'
    -- THE ROW. Its anchor is the ws45 or ws30 flip into `momo` that created it
    wmf_utc           DATETIME    NOT NULL,  -- that flip bar, exact. NOT the rounded display
    wmf_ms            BIGINT      NOT NULL,  -- the same bar in epoch milliseconds, for ordering
    wmf_disp          VARCHAR(12) NOT NULL,  -- the `utc` column as printed, eg '0804 02:14'
    wmf_line          INT         NOT NULL,  -- the `momo line` column - 30 or 45
    wmf_dr            INT         NOT NULL,  -- the `row dr` column - the latched dr at wmf_utc
    -- COLUMN 4. read at wmf_utc
    wmf_mask_htf_flip VARCHAR(24) NULL,      -- `sign mask ws13..ws30`
    -- THE first ws10 cross GROUP. every one of these is read at the cross bar
    wmf_cross_utc     DATETIME    NULL,      -- the cross bar, exact. NULL when no cross was found
    wmf_cross_disp    VARCHAR(12) NULL,      -- the `first ws10 cross` column as printed
    wmf_mask_htf_x    VARCHAR(24) NULL,      -- `sign mask ws13..ws30` at the cross bar
    wmf_mask_ltf_x    VARCHAR(24) NULL,      -- `sign mask ws1..ws12` at the cross bar
    wmf_state_x       VARCHAR(24) NULL,      -- `30|45|60 at ws10 cross`, eg 'mo / no / no'
    -- THE ws10 momentum-false COLUMNS
    wmf_false_b_disp  VARCHAR(12) NULL,      -- `ws10 momo false B` as printed, or '10r dirty'
    wmf_false_b_utc   DATETIME    NULL,      -- that bar, exact. NULL when dirty or none found
    wmf_dirty         TINYINT     NOT NULL,  -- 1 when the ws10 r line was tagged at wmf_utc
    wmf_false_a_disp  VARCHAR(12) NULL,      -- `ws10 momo false A` as printed
    wmf_false_a_utc   DATETIME    NULL,      -- that bar, exact
    wmf_state_a       VARCHAR(24) NULL,      -- `30|45|60 at the flip`, read at the A bar
    wmf_mask_ltf_b    VARCHAR(24) NULL,      -- `sign mask ws1..ws12  B`, read at the B bar
    wmf_built_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_wmf (wmf_knobs, wmf_utc, wmf_line, wmf_dr),
    KEY ix_wmf_ms (wmf_ms)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

COLS = ('wmf_knobs', 'wmf_utc', 'wmf_ms', 'wmf_disp', 'wmf_line', 'wmf_dr',
        'wmf_mask_htf_flip', 'wmf_cross_utc', 'wmf_cross_disp', 'wmf_mask_htf_x',
        'wmf_mask_ltf_x', 'wmf_state_x', 'wmf_false_b_disp', 'wmf_false_b_utc', 'wmf_dirty',
        'wmf_false_a_disp', 'wmf_false_a_utc', 'wmf_state_a', 'wmf_mask_ltf_b')

UPSERT = (f"INSERT INTO wsf_momo_flip_rep ({', '.join(COLS)}) "
          f"VALUES ({', '.join(['%s'] * len(COLS))}) "
          "ON DUPLICATE KEY UPDATE " +
          ', '.join(f'{c}=VALUES({c})' for c in COLS if c not in
                    ('wmf_knobs', 'wmf_utc', 'wmf_line', 'wmf_dr')))


def _n(x):
    """A number the way wem_knobs writes one - 1.0 becomes '1', 0.5 stays '0.5'."""
    t = f'{float(x):g}'
    return t


def KNOBS(variant, m_wob, xwob_cross, xwob, oob_hi, oob_lo, bank, mt):
    """The knob set as one string. `bank` is a momo_bank() dict - its version and the three
    momentum knobs Joe has swept are spelled out, the way wem_knobs spells its own out.

    `mt` is the momentum-true test the ROW SET was built on. 'cm' is dtf curl or dtf momo, Joe
    0904 "dtf curl and dtf momo are both momentum-true, curl can't be ignored". Rows banked
    before 0904 used the exact string `momo` and carry NO mt tag at all - which is how the two
    row sets stay apart in the table instead of mixing under one string."""
    return (f"v{variant}_mw{int(m_wob)}_xwc{int(xwob_cross)}_xw{int(xwob)}"
            f"_hi{int(oob_hi)}_lo{int(oob_lo)}_bv{int(bank['version'])}"
            f"_kw{_n(bank['k_window'])}_sl{_n(bank['momo_slope_min'])}"
            f"_r2{_n(bank['momo_r2_min'])}_mt{mt}")


def create(db):
    db.execute(DDL)
    print('wsf_momo_flip_rep ready')


def show(db):
    rs = db.execute(
        "SELECT wmf_knobs k, COUNT(*) n, SUM(wmf_dirty) d, MIN(wmf_utc) a, MAX(wmf_utc) b, "
        "MAX(wmf_built_at) t FROM wsf_momo_flip_rep GROUP BY 1 ORDER BY t DESC", fetch=True)
    if not rs:
        print('wsf_momo_flip_rep is empty')
        return
    print(f"  {'knobs':<50}{'rows':>7}{'dirty':>7}   {'first row':<21}{'last row':<21}built")
    for r in rs:
        print(f"  {r['k']:<50}{r['n']:>7}{int(r['d']):>7}   {str(r['a']):<21}{str(r['b']):<21}"
              f"{r['t']}")


if __name__ == '__main__':
    db = DatabaseManager(**get_db_config())
    db.connect()
    try:
        if '--show' in sys.argv:
            show(db)
        else:
            create(db)
    finally:
        db.disconnect()
