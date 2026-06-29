"""
seed_lr_exit.py (Joe 0629) — lr EXIT stage A: create s6M (the s6 major BB predictor for s6r) + the exit
knobs. s6M = BB · ohlc4 · bb_len 37 · bb_mult 0.72 · TF6 (cloned off s6m, overriding suffix/src/bb params).
Exit knobs: lp_lr_exit_rlb (the s30a&s15a r-liftoff lookback, relative-TF bars) + lp_lr_sl (the stop floor).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()


def ic(name):
    r = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0]['ic_pk'] if r else None


# 1) s6M — clone s6m's config (is/itf/boundaries/ivm), override → suffix M · BB · ohlc4 · len37 · mult0.72
if ic('s6M') is None:
    s6m = db.execute("SELECT * FROM indicator_configs WHERE ic_pk=%s", (ic('s6m'),), fetch=True)[0]
    il_M = db.execute("SELECT ic_il_pk FROM indicator_configs WHERE ic_pk=%s", (ic('s30M'),), fetch=True)[0]['ic_il_pk']
    db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,
        ic_src,ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
        VALUES (%s,%s,%s,'bb',(CURDATE()-INTERVAL 1 DAY),'ohlc4',%s,%s,37,0.72,%s,%s,%s,%s,%s)''',
        (s6m['ic_is_pk'], il_M, s6m['ic_itf_pk'], s6m['ic_high_boundary'], s6m['ic_low_boundary'],
         s6m['ic_k_len'], s6m['ic_rsi_len'], s6m['ic_stc_len'], s6m['ic_ivm_pk'], s6m['ic_wobble']))
    print('s6M created:', db.execute(
        "SELECT ind_name, value_mode, itf_seconds FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name='s6M'", fetch=True))

# 2) exit knobs
KNOBS = [
    ('lp_lr_exit_rlb', 22.0, 'lr exit: r-line liftoff lookback (relative-TF bars) for the s30a&s15a exit finisher (entry uses 19)'),
    ('lp_lr_sl', 0.5, 'lr exit: stop-loss % — the loss floor (closes at -SL if the finisher exit never comes)'),
]
for name, val, note in KNOBS:
    if not db.execute("SELECT 1 FROM lp_config WHERE name=%s", (name,), fetch=True):
        db.execute("INSERT INTO lp_config (name, val, note) VALUES (%s,%s,%s)", (name, val, note))
print('exit knobs:', db.execute("SELECT name, val FROM lp_config WHERE name IN ('lp_lr_exit_rlb','lp_lr_sl') ORDER BY name", fetch=True))
db.disconnect()
