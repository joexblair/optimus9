"""
seed_s2r.py (Joe 0627) — seed the s2r line + an INACTIVE s2r cascade gate (the TF2 r-line, a clone of
s6r at 2-minute). Idempotent. After running, s2r resolves in vw_indicator_configs_live and appears in the
lp-cascade gate table UNTICKED — tick it (+ untick xm45a) to swap it into the cascade. db-only, no code.

s2r = clone of s6r (k · close · rsi6 · stc6 · k5 · emerging) at TF2 (120s). Needs a new TF2 itf (label '2',
120s) — itf_label != minutes for some rows (the quirk), but s6r's label '6' = 360s is clean, so '2' = 120s.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()

# 1) the TF2 itf (label '2', 120s) — guard against a label clash with other seconds
clash = db.execute("SELECT itf_pk, itf_seconds FROM indicator_timeframes WHERE itf_label='2' AND itf_seconds<>120", fetch=True)
if clash:
    raise SystemExit(f"itf_label '2' already maps to {clash[0]['itf_seconds']}s — resolve the quirk before seeding s2r")
itf = db.execute("SELECT itf_pk FROM indicator_timeframes WHERE itf_label='2' AND itf_seconds=120", fetch=True)
if itf:
    itf_pk = itf[0]['itf_pk']
else:
    db.execute("INSERT INTO indicator_timeframes (itf_label, itf_seconds) VALUES ('2', 120)")
    itf_pk = db.execute("SELECT itf_pk FROM indicator_timeframes WHERE itf_label='2' AND itf_seconds=120", fetch=True)[0]['itf_pk']

# 2) the s2r ic — clone s6r (same is_pk/il_pk = 's'/'r' series+line), at the TF2 itf, live_after=yesterday
s6r = db.execute("""SELECT ic.* FROM indicator_configs ic JOIN indicator_series s ON s.is_pk=ic.ic_is_pk
                    JOIN indicator_lines il ON il.il_pk=ic.ic_il_pk JOIN indicator_timeframes itf ON itf.itf_pk=ic.ic_itf_pk
                    WHERE CONCAT(s.is_prefix, itf.itf_label, il.il_suffix)='s6r'""", fetch=True)[0]
exists = db.execute("SELECT ic_pk FROM indicator_configs WHERE ic_is_pk=%s AND ic_il_pk=%s AND ic_itf_pk=%s",
                    (s6r['ic_is_pk'], s6r['ic_il_pk'], itf_pk), fetch=True)
if exists:
    s2r_ic = exists[0]['ic_pk']
else:
    db.execute("""INSERT INTO indicator_configs
        (ic_is_pk, ic_il_pk, ic_itf_pk, ic_line_type, ic_live_after_dt, ic_src, ic_high_boundary, ic_low_boundary,
         ic_bb_len, ic_bb_mult, ic_k_len, ic_rsi_len, ic_stc_len, ic_ivm_pk, ic_wobble)
        VALUES (%s,%s,%s,%s,(CURDATE() - INTERVAL 1 DAY),%s,%s,%s,NULL,NULL,%s,%s,%s,%s,NULL)""",
        (s6r['ic_is_pk'], s6r['ic_il_pk'], itf_pk, s6r['ic_line_type'], s6r['ic_src'],
         s6r['ic_high_boundary'], s6r['ic_low_boundary'], s6r['ic_k_len'], s6r['ic_rsi_len'],
         s6r['ic_stc_len'], s6r['ic_ivm_pk']))
    s2r_ic = db.execute("SELECT ic_pk FROM indicator_configs WHERE ic_is_pk=%s AND ic_il_pk=%s AND ic_itf_pk=%s",
                        (s6r['ic_is_pk'], s6r['ic_il_pk'], itf_pk), fetch=True)[0]['ic_pk']

# 3) the INACTIVE s2r gate (seq 3 = xm45a's slot; tg_active=0 → shows UNTICKED) + its single line
if not db.execute("SELECT tg_pk FROM trade_gate WHERE tg_name='s2r'", fetch=True):
    db.execute("INSERT INTO trade_gate (tg_seq, tg_name, tg_op, tg_active) VALUES (3, 's2r', 'AND', 0)")
    tg = db.execute("SELECT tg_pk FROM trade_gate WHERE tg_name='s2r'", fetch=True)[0]['tg_pk']
    db.execute("INSERT INTO trade_gate_line (tgl_tg_pk, tgl_ic_pk) VALUES (%s, %s)", (tg, s2r_ic))

# verify
v = db.execute("SELECT ind_name, itf_seconds, value_mode, ic_line_type, ic_k_len, ic_rsi_len, ic_stc_len, ic_src "
               "FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name='s2r'", fetch=True)
print('s2r ic:', dict(v[0]) if v else 'NOT resolving — check')
print('s2r gate:', db.execute("SELECT tg_seq, tg_name, tg_op, tg_active FROM trade_gate WHERE tg_name='s2r'", fetch=True))
db.disconnect()
