"""
seed_s78r.py (Joe 0629) — clone s6r → s7r (TF420) + s8r (TF480) as slower curl-line candidates for the exit
sweep. Just the r-lines (the curl only needs r). Idempotent.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()


def ic(name):
    r = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0]['ic_pk'] if r else None


for label, secs in [('7', 420), ('8', 480)]:
    if ic(f's{label}r') is not None:
        continue
    itf = db.execute("SELECT itf_pk FROM indicator_timeframes WHERE itf_label=%s AND itf_seconds=%s", (label, secs), fetch=True)
    if itf:
        itfp = itf[0]['itf_pk']
    else:
        db.execute("INSERT INTO indicator_timeframes (itf_label, itf_seconds) VALUES (%s,%s)", (label, secs))
        itfp = db.execute("SELECT itf_pk FROM indicator_timeframes WHERE itf_label=%s AND itf_seconds=%s", (label, secs), fetch=True)[0]['itf_pk']
    s = db.execute("SELECT * FROM indicator_configs WHERE ic_pk=%s", (ic('s6r'),), fetch=True)[0]
    db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,
        ic_src,ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
        VALUES (%s,%s,%s,%s,(CURDATE()-INTERVAL 1 DAY),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        (s['ic_is_pk'], s['ic_il_pk'], itfp, s['ic_line_type'], s['ic_src'], s['ic_high_boundary'], s['ic_low_boundary'],
         s['ic_bb_len'], s['ic_bb_mult'], s['ic_k_len'], s['ic_rsi_len'], s['ic_stc_len'], s['ic_ivm_pk'], s['ic_wobble']))
print('curl candidates:', db.execute(
    "SELECT ind_name, itf_seconds FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name REGEXP '^s[5678]r$' ORDER BY itf_seconds", fetch=True))
db.disconnect()
