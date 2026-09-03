"""build_momo_config — the momentum knobs, one bank per machine.

WHY. Joe 0903: "I want the settings to be global per machine, ie dtf and wsf will have their own
config. individual configs can be applied to single line (if needed in the future)" and "it seems
like now is right for a SRP refactor".

THE FAULT THIS REMOVES. The eleven knobs were module globals in momo_core.py, momo_gated.py and
build_momo_landed.py, shared by every machine. On 0903 a sweep of ws20r in dtf was baked in
(K_WINDOW 4->6, MOMO_SLOPE_MIN 1.0->1.2, MOMO_R2_MIN 0.50->0.70) and it moved wsf's verdict too,
silently, because there was one set of globals and no way to name a machine.

SHAPED ON mech_line_config, which already solves this for the LINE specs: keyed on the machine,
versioned, with a live-after date. line_config.py:167 states the rule this inherits - "A SWEEP MUST
PASS A VERSION. Reading the live view during a sweep means a live config change mid-run silently
alters the run, and nothing on the rows says so."

TWO MACHINES ONLY. Joe 0903: "RPL is sunsetted", "s46 is dead", "sunset build_ws_momo". So the
consumers are domtf and wsf, and nothing else binds a bank.

BOTH BANKS START IDENTICAL. Joe 0903: "we have the wem table duplicated, so I'm fine for wsf to
inherit the dtf config". They are separable from row one; they are not different yet.

NO TIMEFRAME BAND COLUMNS - MY CALL, AND THE REASON. mech_line_config carries tf_lo/tf_hi/tf_step
because a line spec genuinely spreads across a band. Joe put the per-line momentum config in the
FUTURE ("if needed in the future"). Adding band columns now would mean inventing a rule for which
row wins when two rows cover the same timeframe, and nobody has asked for that rule. One row per
(machine, version). When Joe needs per-line, the band columns and HIS precedence rule arrive
together.

    python3 build_momo_config.py            create the table and seed version 1 if absent
    python3 build_momo_config.py --show     print every bank
"""
import sys
import datetime as dt
from datetime import timezone

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DDL = '''CREATE TABLE IF NOT EXISTS momo_config (
    mmc_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    mmc_mech      VARCHAR(16) NOT NULL,   -- 'domtf' | 'wsf'. A LABEL for a reader, not the key
    mmc_tf_lo     INT         NOT NULL,   -- the lowest timeframe this bank covers, minutes
    mmc_tf_hi     INT         NOT NULL,   -- the highest, inclusive. THE KEY - a line's own
    --                                       timeframe picks the bank, so no caller asserts a machine
    mmc_version   INT         NOT NULL,   -- a numbered bank. A sweep names one; it never reads live
    mmc_live_after_dt DATETIME NOT NULL,  -- this bank is the live one from this moment
    -- the straight-line fit
    mmc_momo_slope_min  DOUBLE   NOT NULL,  -- slope floor, r-points per sample. A flatter line is 'flat'
    mmc_momo_r2_min     DOUBLE   NOT NULL,  -- straightness floor of the straight-line fit, 0 to 1
    mmc_momo_window_min INT      NOT NULL,  -- default fit window, minutes, before K_WINDOW scales it
    mmc_momo_step_min   INT      NOT NULL,  -- spacing between fit samples, minutes
    mmc_momo_fixed_samples INT   NOT NULL,  -- fixed number of samples in the fit. 0 = derive from the window
    mmc_k_window        INT      NOT NULL,  -- the fit window is k_window x the line's own timeframe, minutes
    mmc_level_slack     DOUBLE   NOT NULL,  -- how far the 50 gate slackens for a cleanly tracking line
    -- the bend
    mmc_curl_arc_min    DOUBLE   NOT NULL,  -- how much the line must bend to be a curl, not sideways
    mmc_curl_vtx_lo     DOUBLE   NOT NULL,  -- the bend's turning point must sit past this fraction of the window
    mmc_curl_vtx_hi     DOUBLE   NOT NULL,  -- ... and before this one. Not on either edge
    mmc_curl_r2_min     DOUBLE   NOT NULL,  -- straightness floor of the BENT fit, 0 to 1
    mmc_note      VARCHAR(255) NOT NULL DEFAULT '',
    UNIQUE KEY uq_mmc (mmc_version, mmc_tf_lo, mmc_tf_hi),
    KEY ix_mmc_live (mmc_mech, mmc_live_after_dt))'''

# THE BANDS, from Joe's own rulings. They do not overlap and they leave no gap in 1..27.
#   wsf    1..12   build_wsf_line_bar.py:46, Joe 0826: "wsf is limited to TF12"
#   domtf 13..60   Joe 0903, asked "does domtf's band run 13 to 60?" - "yes". EXTENDS his 0813
#                  ruling ("make the domTF range 13 to 27"), which predates the ws30/ws45/ws60
#                  lines being added to the cache on 0901. The cache holds ws1..ws27, ws30, ws45,
#                  ws60, so 13..60 covers every line above wsf's band with no gap.
# KEYED ON THE BAND, NOT THE MACHINE, Joe 0903: "wsf and dtf become internal labels that
# apply to different indicator groups". A line at timeframe 20 is computed by whichever
# machine owns 20; the caller passes its timeframe and never asserts a machine, so the fault
# that started this - one machine silently running on the other's numbers - has nothing to
# assert wrongly. Joe 0903 on task #14: "instantiate dtf and consume its lines", so a
# timeframe is never computed twice under two different banks.
BANDS = {'wsf': (1, 12), 'domtf': (13, 60)}

# VERSION 1 = the values live in the code at the moment of the split, so the refactor changes the
# SHAPE and not a single number. K_WINDOW 6 / slope 1.2 / r2 0.70 are Joe's 0903 bake-in; the other
# eight are unchanged from where they have sat.
V1 = dict(momo_slope_min=1.2, momo_r2_min=0.70, momo_window_min=60, momo_step_min=5,
          momo_fixed_samples=21, k_window=6, level_slack=13.9,
          curl_arc_min=4.0, curl_vtx_lo=0.05, curl_vtx_hi=0.95, curl_r2_min=0.40)
MECHS = ('domtf', 'wsf')
NOTE = ("v1 = the module globals at the 0903 SRP split. slope/r2/k_window are Joe's 0903 bake-in, "
        "fitted to 8 eyeballed 08-04 pivots on ws20r. wsf inherits dtf, Joe 0903.")


def show(db):
    rows = db.execute('SELECT * FROM momo_config ORDER BY mmc_version, mmc_tf_lo', fetch=True)
    if not rows:
        print('  momo_config is empty', flush=True); return
    keys = [k for k in rows[0] if k.startswith('mmc_') and k not in
            ('mmc_pk', 'mmc_mech', 'mmc_version', 'mmc_live_after_dt', 'mmc_note',
             'mmc_tf_lo', 'mmc_tf_hi')]
    print(f"  {'label':<8}{'timeframes':>12}{'version':>8}  {'live after':<20}" +
          ''.join(f'{k[4:]:>22}' for k in keys), flush=True)
    for r in rows:
        band = f"{r['mmc_tf_lo']}..{r['mmc_tf_hi']}"
        print(f"  {r['mmc_mech']:<8}{band:>12}{r['mmc_version']:>8}  "
              f"{str(r['mmc_live_after_dt']):<20}" +
              ''.join(f"{str(r[k]):>22}" for k in keys), flush=True)


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    if '--show' in sys.argv:
        show(db); db.disconnect(); return 0
    # the band columns arrived after the first seed. Added, not versioned - SRP: mmc_version
    # identifies a set of knob VALUES so a sweep can name one, and a v2 holding identical values
    # would make that field mean "values OR schema revision", two responsibilities on one column.
    have_cols = {r['Field'] for r in db.execute('SHOW COLUMNS FROM momo_config', fetch=True)}
    # the table was first created keyed on (mech, version). The key moved to the band when the
    # lookup did, so an existing table needs the index swapped or the DDL above describes a shape
    # the database does not have. Indexes only - no row is touched.
    idx = {r['Key_name'] for r in db.execute('SHOW INDEX FROM momo_config', fetch=True)}
    for c, after in (('mmc_tf_lo', 'mmc_mech'), ('mmc_tf_hi', 'mmc_tf_lo')):
        if c not in have_cols:
            db.execute(f'ALTER TABLE momo_config ADD COLUMN {c} INT NOT NULL DEFAULT 0 AFTER {after}')
            print(f'  momo_config : added column {c}', flush=True)
    if 'uq_mmc' in idx and 'mmc_tf_lo' in have_cols:
        cur = [r['Column_name'] for r in db.execute('SHOW INDEX FROM momo_config', fetch=True)
               if r['Key_name'] == 'uq_mmc']
        if cur != ['mmc_version', 'mmc_tf_lo', 'mmc_tf_hi']:
            db.execute('ALTER TABLE momo_config DROP INDEX uq_mmc, '
                       'ADD UNIQUE KEY uq_mmc (mmc_version, mmc_tf_lo, mmc_tf_hi)')
            print(f'  momo_config : unique key moved {cur} -> [version, tf_lo, tf_hi]', flush=True)
    cols = ['mmc_mech', 'mmc_tf_lo', 'mmc_tf_hi', 'mmc_version', 'mmc_live_after_dt', 'mmc_note'] \
           + [f'mmc_{k}' for k in V1]
    for mech in MECHS:
        lo, hi = BANDS[mech]
        row = db.execute('SELECT mmc_pk, mmc_tf_lo, mmc_tf_hi FROM momo_config '
                         'WHERE mmc_mech=%s AND mmc_version=1', (mech,), fetch=True)
        if row:
            # the row exists from the first seed. Fill its band if it has none; never touch a knob.
            if int(row[0]['mmc_tf_lo']) == 0 and int(row[0]['mmc_tf_hi']) == 0:
                db.execute('UPDATE momo_config SET mmc_tf_lo=%s, mmc_tf_hi=%s WHERE mmc_pk=%s',
                           (lo, hi, row[0]['mmc_pk']))
                print(f'  {mech} v1 band set to {lo}..{hi}', flush=True)
            elif (int(row[0]['mmc_tf_lo']), int(row[0]['mmc_tf_hi'])) != (lo, hi):
                # widening a band is not a knob change - no value moves, and a version identifies
                # values. Joe 0903 set domtf to 13..60 after the ws30/45/60 lines landed.
                was = f"{row[0]['mmc_tf_lo']}..{row[0]['mmc_tf_hi']}"
                db.execute('UPDATE momo_config SET mmc_tf_lo=%s, mmc_tf_hi=%s WHERE mmc_pk=%s',
                           (lo, hi, row[0]['mmc_pk']))
                print(f'  {mech} v1 band {was} -> {lo}..{hi}', flush=True)
            else:
                print(f'  {mech} v1 already banded, left alone', flush=True)
            continue
        db.execute(f'INSERT INTO momo_config ({",".join(cols)}) '
                   f'VALUES ({",".join(["%s"] * len(cols))})',
                   tuple([mech, lo, hi, 1, dt.datetime(2026, 1, 1, tzinfo=timezone.utc)
                          .strftime('%Y-%m-%d %H:%M:%S'), NOTE] + [V1[k] for k in V1]))
        print(f'  {mech} v1 seeded, band {lo}..{hi}', flush=True)
    # SQL cannot express "no two bands in a version overlap", so it is checked here, where they
    # are written, and again in momo_bank(), where they are read.
    ov = db.execute('SELECT a.mmc_mech m1, b.mmc_mech m2, a.mmc_version v FROM momo_config a '
                    'JOIN momo_config b ON a.mmc_version=b.mmc_version AND a.mmc_pk<b.mmc_pk '
                    'AND a.mmc_tf_lo<=b.mmc_tf_hi AND b.mmc_tf_lo<=a.mmc_tf_hi', fetch=True)
    if ov:
        for r in ov:
            print(f"  OVERLAP: v{r['v']} {r['m1']} and {r['m2']} cover the same timeframe", flush=True)
        raise SystemExit('overlapping bands - a timeframe would match two banks')
    show(db)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
