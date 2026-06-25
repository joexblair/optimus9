import sys; sys.path.insert(0,'/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
db=DatabaseManager(**get_db_config()); db.connect()

# 1. dimension table (parallels indicator_series/lines/timeframes)
db.execute("""CREATE TABLE IF NOT EXISTS indicator_value_modes (
  ivm_pk INT PRIMARY KEY, ivm_label VARCHAR(16) UNIQUE, ivm_description VARCHAR(160))""")
db.execute("""INSERT INTO indicator_value_modes VALUES
  (1,'closed','TF last CLOSED bar value — TV-verbatim, stable'),
  (2,'emerging','still-forming intrabar value — faster, what realtime sees pre-close')
  ON DUPLICATE KEY UPDATE ivm_label=VALUES(ivm_label), ivm_description=VALUES(ivm_description)""")

# 2. FK column on indicator_configs — declarative only until consumers wire in; default closed (TV-stable)
cols=[c['Field'] for c in db.execute("SHOW COLUMNS FROM indicator_configs", fetch=True)]
if 'ic_ivm_pk' not in cols:
    db.execute("ALTER TABLE indicator_configs ADD COLUMN ic_ivm_pk INT DEFAULT 1")
    db.execute("UPDATE indicator_configs SET ic_ivm_pk=1 WHERE ic_ivm_pk IS NULL")

# 3. add value_mode to the live view via DDL transform (no clause dropped)
ddl=db.execute("SHOW CREATE VIEW pk_optimizer.vw_indicator_configs_live", fetch=True)[0]['Create View']
# strip the CREATE...VIEW algorithm/definer preamble -> rebuild as CREATE OR REPLACE
i=ddl.lower().find('select')
body=ddl[i:]
body=body.replace("`itf`.`itf_seconds` AS `itf_seconds`",
  "`itf`.`itf_seconds` AS `itf_seconds`,`ic`.`ic_ivm_pk` AS `ic_ivm_pk`,`vm`.`ivm_label` AS `value_mode`")
body=body.replace(" where ",
  " left join `indicator_value_modes` `vm` on((`vm`.`ivm_pk` = `ic`.`ic_ivm_pk`)) where ",1)
db.execute("CREATE OR REPLACE VIEW vw_indicator_configs_live AS "+body)

# 4. verify
r=db.execute("SELECT ind_name, value_mode FROM vw_indicator_configs_live WHERE ind_name='hb16m'", fetch=True)
modes=db.execute("SELECT value_mode, COUNT(*) n FROM vw_indicator_configs_live GROUP BY value_mode", fetch=True)
print("indicator_value_modes:", db.execute("SELECT * FROM indicator_value_modes", fetch=True))
print("sample line:", r)
print("mode distribution:", [dict(m) for m in modes])
db.disconnect()
