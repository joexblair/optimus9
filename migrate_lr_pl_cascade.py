"""
migrate_lr_pl_cascade.py (Joe 0629) — re-spec the lp-cascade: drop s14M (bias has no place in pl-cascade —
set upstream), rename the role 'bias'→'gate', add a per-line lookback column, seed s2r as a GATE (finisher
clearance, lookback-11, same-side), set s30r/s15r per-line lookbacks. Idempotent.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()


def ic(name):
    r = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0]['ic_pk'] if r else None


# 1) per-line lookback column
cols = [r['Field'] for r in db.execute("SHOW COLUMNS FROM lr_gate_line", fetch=True)]
if 'lrgl_lookback' not in cols:
    db.execute("ALTER TABLE lr_gate_line ADD COLUMN lrgl_lookback INT NULL")

# 2) drop the s14_bias gate (bias is set upstream, not in pl-cascade)
g = db.execute("SELECT lrg_pk FROM lr_gate WHERE lrg_name='s14_bias'", fetch=True)
if g:
    db.execute("DELETE FROM lr_gate_line WHERE lrgl_lrg_pk=%s", (g[0]['lrg_pk'],))
    db.execute("DELETE FROM lr_gate WHERE lrg_pk=%s", (g[0]['lrg_pk'],))

# 3) rename the role enum bias→gate (safe now that no 'bias' rows remain)
roleenum = db.execute("SHOW COLUMNS FROM lr_gate LIKE 'lrg_role'", fetch=True)[0]['Type']
if 'gate' not in roleenum:
    db.execute("ALTER TABLE lr_gate MODIFY lrg_role ENUM('arm','finisher','gate') NOT NULL")

# 4) per-line lookbacks on the existing finisher r-lines (entry values; exit overrides to exit_rlb)
for nm, lb in [('s30r', 19), ('s15r', 19)]:
    db.execute('''UPDATE lr_gate_line l JOIN pk_optimizer.vw_indicator_configs_live i ON i.ic_pk=l.lrgl_ic_pk
        SET l.lrgl_lookback=%s WHERE i.ind_name=%s AND l.lrgl_check='lookback' ''', (lb, nm))

# 5) seed s2r as a GATE — finisher clearance, lookback-11, same-side
if not db.execute("SELECT 1 FROM lr_gate WHERE lrg_name='s2r'", fetch=True):
    db.execute("INSERT INTO lr_gate (lrg_role,lrg_name,lrg_op,lrg_active) VALUES ('gate','s2r','AND',1)")
    pk = db.execute("SELECT lrg_pk FROM lr_gate WHERE lrg_name='s2r'", fetch=True)[0]['lrg_pk']
    db.execute("INSERT INTO lr_gate_line (lrgl_lrg_pk,lrgl_ic_pk,lrgl_check,lrgl_lookback) VALUES (%s,%s,'lookback',11)", (pk, ic('s2r')))

# verify
print('lp-cascade gate-sets now:')
for g in db.execute("SELECT * FROM lr_gate ORDER BY FIELD(lrg_role,'arm','finisher','gate'), lrg_name", fetch=True):
    lines = db.execute('''SELECT i.ind_name nm, l.lrgl_check ch, l.lrgl_lookback lb FROM lr_gate_line l
        JOIN pk_optimizer.vw_indicator_configs_live i ON i.ic_pk=l.lrgl_ic_pk WHERE l.lrgl_lrg_pk=%s''', (g['lrg_pk'],), fetch=True)
    print(f"  [{g['lrg_role']:8}] {g['lrg_name']:9} active={g['lrg_active']} :: " +
          ' · '.join(f"{x['nm']}({x['ch']}{'/'+str(x['lb']) if x['lb'] else ''})" for x in lines))
db.disconnect()
