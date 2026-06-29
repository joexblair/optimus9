"""
seed_lr_gate.py (Joe 0628) — lr decoupling step 1: the lr_gate / lr_gate_line tables + the CURRENT mechanic
seeded 1:1 as data (arm s6m · finisher s30a · bias s14), PLUS a DISABLED s15 finisher candidate (s15M/m/r
cloned from s30 at TF15s if absent). Idempotent. Lines referenced by ic_pk (the bias-producer tagging
convention). The lr_detect refactor to WALK these gate-sets is step 2; this just lays the data.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()

# 1) tables (lrg_ = lr_gate, lrgl_ = lr_gate_line — prefix convention)
db.execute('''CREATE TABLE IF NOT EXISTS lr_gate (
    lrg_pk INT AUTO_INCREMENT PRIMARY KEY, lrg_role ENUM('arm','finisher','bias') NOT NULL,
    lrg_name VARCHAR(40) NOT NULL UNIQUE, lrg_op ENUM('AND','OR') NOT NULL DEFAULT 'AND',
    lrg_active TINYINT NOT NULL DEFAULT 1)''')
db.execute('''CREATE TABLE IF NOT EXISTS lr_gate_line (
    lrgl_pk INT AUTO_INCREMENT PRIMARY KEY, lrgl_lrg_pk INT NOT NULL, lrgl_ic_pk INT NOT NULL,
    lrgl_check ENUM('oob','lookback','mid') NOT NULL DEFAULT 'oob', INDEX(lrgl_lrg_pk))''')


def ic(name):
    r = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0]['ic_pk'] if r else None


# 2) ensure s15M/s15m/s15r exist (clone s30M/m/r at TF15s) — the disabled candidate's lines
if ic('s15M') is None:
    itf = db.execute("SELECT itf_pk FROM indicator_timeframes WHERE itf_label='15' AND itf_seconds=15", fetch=True)
    itf15 = itf[0]['itf_pk'] if itf else None
    if itf15 is None:
        db.execute("INSERT INTO indicator_timeframes (itf_label, itf_seconds) VALUES ('15', 15)")
        itf15 = db.execute("SELECT itf_pk FROM indicator_timeframes WHERE itf_label='15' AND itf_seconds=15", fetch=True)[0]['itf_pk']
    for suff in ('M', 'm', 'r'):
        s = db.execute('''SELECT ic.* FROM indicator_configs ic JOIN indicator_series si ON si.is_pk=ic.ic_is_pk
            JOIN indicator_lines il ON il.il_pk=ic.ic_il_pk JOIN indicator_timeframes itf ON itf.itf_pk=ic.ic_itf_pk
            WHERE CONCAT(si.is_prefix, itf.itf_label, il.il_suffix)=%s''', (f's30{suff}',), fetch=True)[0]
        db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,
            ic_src,ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
            VALUES (%s,%s,%s,%s,(CURDATE()-INTERVAL 1 DAY),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (s['ic_is_pk'], s['ic_il_pk'], itf15, s['ic_line_type'], s['ic_src'], s['ic_high_boundary'],
             s['ic_low_boundary'], s['ic_bb_len'], s['ic_bb_mult'], s['ic_k_len'], s['ic_rsi_len'],
             s['ic_stc_len'], s['ic_ivm_pk'], s['ic_wobble']))

# 3) seed the gate-sets (1:1 with the current mechanic + the disabled s15a)
GATES = [
    ('arm',      's6m_arm',   'AND', 1, [('s6m', 'oob')]),
    ('finisher', 's30a',      'AND', 1, [('s30M', 'oob'), ('s30m', 'oob'), ('s30r', 'lookback')]),
    ('bias',     's14_bias',  'AND', 1, [('s14M', 'mid')]),
    ('finisher', 's15a',      'AND', 0, [('s15M', 'oob'), ('s15m', 'oob'), ('s15r', 'lookback')]),
]
for role, name, op, active, lines in GATES:
    if db.execute("SELECT lrg_pk FROM lr_gate WHERE lrg_name=%s", (name,), fetch=True):
        continue
    db.execute("INSERT INTO lr_gate (lrg_role, lrg_name, lrg_op, lrg_active) VALUES (%s,%s,%s,%s)", (role, name, op, active))
    gpk = db.execute("SELECT lrg_pk FROM lr_gate WHERE lrg_name=%s", (name,), fetch=True)[0]['lrg_pk']
    for ln, chk in lines:
        db.execute("INSERT INTO lr_gate_line (lrgl_lrg_pk, lrgl_ic_pk, lrgl_check) VALUES (%s,%s,%s)", (gpk, ic(ln), chk))

# 4) verify
print('lr_gate seed:')
for g in db.execute("SELECT * FROM lr_gate ORDER BY FIELD(lrg_role,'arm','finisher','bias'), lrg_name", fetch=True):
    lines = db.execute('''SELECT i.ind_name nm, l.lrgl_check ch FROM lr_gate_line l
        JOIN pk_optimizer.vw_indicator_configs_live i ON i.ic_pk=l.lrgl_ic_pk WHERE l.lrgl_lrg_pk=%s''', (g['lrg_pk'],), fetch=True)
    print(f"  [{g['lrg_role']:8}] {g['lrg_name']:10} op={g['lrg_op']} active={g['lrg_active']}  ::  " +
          ' · '.join(f"{x['nm']}({x['ch']})" for x in lines))
db.disconnect()
