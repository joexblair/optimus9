"""
seed_s7.py (Joe 0630) — seed s7m (s7min) + s7M (s7Mage): the BB pair on TF7 (TF420) that PREDICT the s7r K
line, the exit-cascade analog of predict_breach(s3r, s3m, s3M) in the entry. Cloned from s5m/s5M (is_pk=2,
il_pk=1/2 minor/major, ivm_pk=2 same stoch model as s7r), itf → TF7, src=ohlc4, per Joe: s7m=10/0.77,
s7M=37/0.83. value_mode is computed in the view (follows il_pk) → comes out 'emerging' like s5. Idempotent.
NOTE: both multis are to be SWEPT (step 0.03, 11d) — these seed the centre of that sweep.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()


def ic(name):
    r = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0]['ic_pk'] if r else None


itf7 = db.execute("SELECT ic.ic_itf_pk FROM indicator_configs ic JOIN pk_optimizer.vw_indicator_configs_live v "
                  "ON v.ic_pk=ic.ic_pk WHERE v.ind_name='s7r'", fetch=True)[0]['ic_itf_pk']

for tmpl, suffix, blen, bmult in (('s5m', 'm', 10, 0.77), ('s5M', 'M', 37, 0.83)):
    if ic('s7' + suffix) is not None:
        continue
    s = db.execute("SELECT * FROM indicator_configs WHERE ic_pk=%s", (ic(tmpl),), fetch=True)[0]
    db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,
        ic_src,ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
        VALUES (%s,%s,%s,'bb',(CURDATE()-INTERVAL 1 DAY),'ohlc4',%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        (s['ic_is_pk'], s['ic_il_pk'], itf7, s['ic_high_boundary'], s['ic_low_boundary'],
         blen, bmult, s['ic_k_len'], s['ic_rsi_len'], s['ic_stc_len'], s['ic_ivm_pk'], s['ic_wobble']))

print('s7 family:', db.execute("SELECT ind_name, itf_seconds, ic_bb_len, ic_bb_mult, ic_src, value_mode "
      "FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name LIKE 's7%' ORDER BY ind_name", fetch=True))
db.disconnect()
