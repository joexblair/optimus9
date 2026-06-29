"""
setup_db.py (Joe 0628) — stand up the o9-live forward-test DB (Phase 1, WSL MySQL): create the database,
apply docs/o9_live_schema.sql, seed the config/reference tables from the dev DB (pk_optimizer). Idempotent.
Live tables (kline_collection, ticks) left empty for the collector; fx_* start empty.

  python3 live/setup_db.py
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import re
import mysql.connector
from optimus9.config import get_db_config

DB = 'o9_live'
SRC = 'pk_optimizer'
CONFIG = ['indicator_value_modes', 'indicator_series', 'indicator_lines', 'indicator_timeframes',
          'indicator_configs', 'optimus9_system', 'bl_lines', 'trading_pairs', 'lp_config']

cfg = get_db_config()
cx = mysql.connector.connect(**{k: v for k, v in cfg.items() if k != 'database'})
cur = cx.cursor()
cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB}")
cur.execute(f"USE {DB}")

# apply the schema (drop comment lines + the view DEFINER so any connection user works)
sql = open('docs/o9_live_schema.sql').read()
sql = re.sub(r'--[^\n]*', '', sql)                            # strip ALL line comments (inline ones can hold ';')
sql = re.sub(r'DEFINER=`[^`]+`@`[^`]+` ', '', sql)
applied = 0
for stmt in [s.strip() for s in sql.split(';') if s.strip()]:
    try:
        cur.execute(stmt); applied += 1
    except mysql.connector.Error as e:
        if e.errno != 1050:                                       # 1050 = table already exists
            print('  warn:', str(e)[:100])
cx.commit()

# seed config/reference rows (cross-DB, idempotent)
for t in CONFIG:
    cur.execute(f"INSERT IGNORE INTO {DB}.{t} SELECT * FROM {SRC}.{t}")
cx.commit()

print(f'{DB} stood up ({applied} statements applied):')
for t in CONFIG + ['kline_collection', 'ticks', 'fx_order', 'fx_position', 'fx_fill', 'o9_decision']:
    cur.execute(f"SELECT COUNT(*) FROM {DB}.{t}")
    print(f'  {t:26} {cur.fetchone()[0]} rows')
cur.close(); cx.close()

# verify the engine reads o9_live (lr_params + the live-config view resolve)
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_params
o9 = DatabaseManager(**{**cfg, 'database': DB}); o9.connect()
print('lr_params(o9_live):', lr_params(o9))
print('view resolves:', o9.execute(
    "SELECT ind_name, itf_seconds, value_mode FROM vw_indicator_configs_live WHERE ind_name='s30m'", fetch=True))
o9.disconnect()
