"""mech_line_config: add `mlc_tf_list`, and define wsf v2 as the TFs it really uses. Joe 1003.

IDEMPOTENT. Re-running prints what is already in place and changes nothing.

Joe: *"allow an explicit TF list in mech_line_config (e.g. an mlc_tf_list column) alongside the band,
and move the non-conforming lines into mech line config so we're optimised and consistent"*.

WHY A LIST. The band is `range(tf_lo, tf_hi+1, tf_step)` - a uniform arithmetic sequence. The wsf
mech's real timeframe set is not one: {5, 15, 30, 60..480, 540, 600, 900, 1320}. `range(5,1321,5)`
would build 265 lines for the 15 that are used.

WHY v2 AND NOT A CHANGE TO v1. `mech_lines()` is the ONLY expander, and 12+ callers read the LIVE
view. Adding TFs to the live rows changes what every one of them enumerates. So v2 carries the full
set with `mlc_live_after_dt` 2099-01-01, which the live view's `<= now()` test excludes. Nothing
changes until Joe moves that date.

    python3 docs/octo-freedom/1003_mech_line_config/migrate.py
"""
import io
import sys

sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr
sys.stderr = io.StringIO()
from optimus9.compute.line_config import mech_lines                      # noqa: E402
from optimus9.config import get_db_config                                # noqa: E402
from optimus9.db.database_manager import DatabaseManager                 # noqa: E402
sys.stderr = _e

TFS = '5,15,30,60,120,180,240,300,360,420,480,540,600,900,1320'
NOT_LIVE = '2099-01-01 00:00:00'
NOTE = ('wsf v2: the band 60-480 plus the TFs it really uses - gcws5/15/30 below it and '
        'ws9/10/15/22 above. Joe 1003. NOT LIVE until live_after_dt is moved.')

VIEW = """CREATE OR REPLACE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW vw_mech_line_config_live AS
select c.mlc_pk, c.mlc_mech, c.mlc_role, c.mlc_tf_lo, c.mlc_tf_hi, c.mlc_tf_step, c.mlc_tf_list,
       c.mlc_version, c.mlc_live_after_dt, c.mlc_line_type, c.mlc_src, c.mlc_bb_len, c.mlc_bb_mult,
       c.mlc_k_len, c.mlc_rsi_len, c.mlc_stc_len, c.mlc_value_mode, c.mlc_hi_boundary,
       c.mlc_lo_boundary, c.mlc_boundary_offset, c.mlc_note
from mech_line_config c
where c.mlc_live_after_dt = (select max(c2.mlc_live_after_dt) from mech_line_config c2
      where c2.mlc_mech = c.mlc_mech and c2.mlc_role = c.mlc_role and c2.mlc_tf_lo = c.mlc_tf_lo
        and c2.mlc_tf_hi = c.mlc_tf_hi and c2.mlc_live_after_dt <= now())"""

INSERT = """INSERT INTO mech_line_config
  (mlc_mech,mlc_role,mlc_tf_lo,mlc_tf_hi,mlc_tf_step,mlc_tf_list,mlc_version,mlc_live_after_dt,
   mlc_line_type,mlc_src,mlc_bb_len,mlc_bb_mult,mlc_k_len,mlc_rsi_len,mlc_stc_len,mlc_value_mode,
   mlc_hi_boundary,mlc_lo_boundary,mlc_boundary_offset,mlc_note)
  VALUES (%s,%s,5,1320,0,%s,2,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""


def main():
    db = DatabaseManager(**get_db_config())
    db.connect()
    cols = [r['Field'] for r in db.execute('SHOW COLUMNS FROM mech_line_config', fetch=True)]
    if 'mlc_tf_list' in cols:
        print('1 column mlc_tf_list        already present')
    else:
        db.execute("ALTER TABLE mech_line_config ADD COLUMN mlc_tf_list VARCHAR(255) NULL "
                   "COMMENT 'explicit CSV timeframe seconds; when set it OVERRIDES tf_lo/hi/step' "
                   "AFTER mlc_tf_step")
        print('1 column mlc_tf_list        ADDED')
    db.execute(VIEW)
    print('2 vw_mech_line_config_live  recreated (exposes mlc_tf_list)')
    n = db.execute("SELECT COUNT(*) n FROM mech_line_config WHERE mlc_mech='wsf' AND mlc_version=2",
                   fetch=True)[0]['n']
    if n:
        print('3 wsf v2 rows               already present: %d' % n)
    else:
        for c in db.execute("SELECT * FROM mech_line_config WHERE mlc_mech='wsf' AND mlc_version=1",
                            fetch=True):
            db.execute(INSERT, (c['mlc_mech'], c['mlc_role'], TFS, NOT_LIVE, c['mlc_line_type'],
                                c['mlc_src'], c['mlc_bb_len'], c['mlc_bb_mult'], c['mlc_k_len'],
                                c['mlc_rsi_len'], c['mlc_stc_len'], c['mlc_value_mode'],
                                c['mlc_hi_boundary'], c['mlc_lo_boundary'],
                                c['mlc_boundary_offset'], NOTE))
        print('3 wsf v2 rows               INSERTED (5 rows, live_after_dt %s)' % NOT_LIVE)
    live = len(db.execute('SELECT 1 FROM vw_mech_line_config_live', fetch=True))
    print()
    print('CHECKS')
    print('  live view rows                 %d   (must be 7)' % live)
    print('  live  mech_lines(wsf)          %d   (must be 40 - unchanged)' % len(mech_lines(db, 'wsf')))
    print('  live  mech_lines(domtf)        %d   (must be 30 - unchanged)' % len(mech_lines(db, 'domtf')))
    print('  v2    mech_lines(wsf, 2)       %d   (5 roles x 15 TFs)' % len(mech_lines(db, 'wsf', version=2)))
    db.disconnect()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
