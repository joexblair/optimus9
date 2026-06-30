"""
seed_s2bb.py (Joe 0630) — seed s2m + s2M (the s2 BBs) at s2r's TF120 for the s2M-reversal entry path.
s2m = s6m cloned with bb_mult 0.56 · s2M = s6M (37|0.72|ohlc4). Closed-bar. Idempotent.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()


def ic(name):
    r = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0]['ic_pk'] if r else None


if ic('s2M') is None:
    itf2 = db.execute("SELECT ic_itf_pk FROM indicator_configs WHERE ic_pk=%s", (ic('s2r'),), fetch=True)[0]['ic_itf_pk']
    closed = db.execute("SELECT ivm_pk FROM indicator_value_modes WHERE ivm_label='closed'", fetch=True)[0]['ivm_pk']
    for src, mult_override in [('s6m', 0.56), ('s6M', None)]:
        s = db.execute("SELECT * FROM indicator_configs WHERE ic_pk=%s", (ic(src),), fetch=True)[0]
        bb_mult = mult_override if mult_override is not None else s['ic_bb_mult']
        db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,ic_src,
            ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
            VALUES (%s,%s,%s,%s,(CURDATE()-INTERVAL 1 DAY),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (s['ic_is_pk'], s['ic_il_pk'], itf2, s['ic_line_type'], s['ic_src'], s['ic_high_boundary'], s['ic_low_boundary'],
             s['ic_bb_len'], bb_mult, s['ic_k_len'], s['ic_rsi_len'], s['ic_stc_len'], closed, s['ic_wobble']))
    db.execute("UPDATE indicator_configs SET ic_ivm_pk=%s WHERE ic_pk IN (%s,%s)" % (closed, ic('s2m') or 0, ic('s2M') or 0))
print('s2 family:', db.execute(
    "SELECT ind_name, value_mode, itf_seconds FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name REGEXP '^s2[a-zA-Z]' ORDER BY ind_name", fetch=True))
db.disconnect()
