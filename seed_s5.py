"""
seed_s5.py (Joe 0629) — clone the s6 family → s5 at TF300 (5 min) as the trial exit line. s5m/s5M/s5r =
s6m/s6M/s6r with itf swapped to TF5 (itf_seconds 300). Idempotent.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()


def ic(name):
    r = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0]['ic_pk'] if r else None


if ic('s5m') is None:
    itf = db.execute("SELECT itf_pk FROM indicator_timeframes WHERE itf_label='5' AND itf_seconds=300", fetch=True)
    if itf:
        itf5 = itf[0]['itf_pk']
    else:
        db.execute("INSERT INTO indicator_timeframes (itf_label, itf_seconds) VALUES ('5', 300)")
        itf5 = db.execute("SELECT itf_pk FROM indicator_timeframes WHERE itf_label='5' AND itf_seconds=300", fetch=True)[0]['itf_pk']
    for src in ('s6m', 's6M', 's6r'):
        s = db.execute("SELECT * FROM indicator_configs WHERE ic_pk=%s", (ic(src),), fetch=True)[0]
        bb_mult = 0.65 if src == 's6m' else s['ic_bb_mult']   # s5m widened 0.4→0.65 (#45 — kill small breaches; v2 arm)
        db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,
            ic_src,ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
            VALUES (%s,%s,%s,%s,(CURDATE()-INTERVAL 1 DAY),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (s['ic_is_pk'], s['ic_il_pk'], itf5, s['ic_line_type'], s['ic_src'], s['ic_high_boundary'], s['ic_low_boundary'],
             s['ic_bb_len'], bb_mult, s['ic_k_len'], s['ic_rsi_len'], s['ic_stc_len'], s['ic_ivm_pk'], s['ic_wobble']))
print('s5 family:', db.execute(
    "SELECT ind_name, itf_seconds FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name LIKE 's5%' ORDER BY ind_name", fetch=True))
db.disconnect()
