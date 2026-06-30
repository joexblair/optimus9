"""
seed_hb33.py (Joe 0630) — clone the bro-cross hb16 sets (hbhl16/hblo16/hbhi16, each M+m, TF960) to hb33 at
TF1980 (33 min), EMERGING value (per spec, affected by lp_bro_wob). For bro-cross bias testing in the kernel
walk. Idempotent.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()


def ic(name):
    r = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0]['ic_pk'] if r else None


if ic('hbhl33M') is None:
    itf = db.execute("SELECT itf_pk FROM indicator_timeframes WHERE itf_seconds=1980 AND itf_label='33'", fetch=True)
    itf33 = itf[0]['itf_pk'] if itf else None
    if itf33 is None:
        db.execute("INSERT INTO indicator_timeframes (itf_label, itf_seconds) VALUES ('33', 1980)")
        itf33 = db.execute("SELECT itf_pk FROM indicator_timeframes WHERE itf_seconds=1980 AND itf_label='33'", fetch=True)[0]['itf_pk']
    emerging = db.execute("SELECT ivm_pk FROM indicator_value_modes WHERE ivm_label='emerging'", fetch=True)[0]['ivm_pk']
    for src in ('hbhl16M', 'hbhl16m', 'hblo16M', 'hblo16m', 'hbhi16M', 'hbhi16m'):
        s = db.execute("SELECT * FROM indicator_configs WHERE ic_pk=%s", (ic(src),), fetch=True)[0]
        db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,ic_src,
            ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
            VALUES (%s,%s,%s,%s,(CURDATE()-INTERVAL 1 DAY),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (s['ic_is_pk'], s['ic_il_pk'], itf33, s['ic_line_type'], s['ic_src'], s['ic_high_boundary'], s['ic_low_boundary'],
             s['ic_bb_len'], s['ic_bb_mult'], s['ic_k_len'], s['ic_rsi_len'], s['ic_stc_len'], emerging, s['ic_wobble']))
print('hb33 sets:', db.execute(
    "SELECT ind_name, value_mode, itf_seconds FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name REGEXP '^hb(hl|lo|hi)33' ORDER BY ind_name", fetch=True))
db.disconnect()
