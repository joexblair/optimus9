"""Provision the o9-live DB (milestone ②) — reproducible on a fresh MySQL (local WSL or Managed).

    python3 ops/provision_o9live.py            # source = PK_DB_NAME (default pk_optimizer) → target o9_live

Creates o9_live from docs/o9_live_schema.sql and seeds the config/reference tables from the source DB
(dimensions → indicator_configs → optimus9_system/lp_config/lr_gate(_line) → trading_pairs → bl_lines).
Live-data tables (kline_collection, ticks) and fx_* stay empty — the collector + fake-exchange fill them.
Point any optimus9 process at it with PK_DB_NAME=o9_live (the config connection-string seam).
"""
import re
import sys

sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config

SCHEMA = '/home/joe/thecodes/docs/o9_live_schema.sql'
TARGET = 'o9_live'
SEED = ['indicator_value_modes', 'indicator_series', 'indicator_lines', 'indicator_timeframes',
        'indicator_configs', 'optimus9_system', 'lp_config', 'lr_gate', 'lr_gate_line',
        'trading_pairs', 'bl_lines']


def main():
    cfg = get_db_config()
    src = cfg['database']
    admin = DatabaseManager(**cfg); admin.connect()
    admin.execute("DROP DATABASE IF EXISTS %s" % TARGET)   # dev/build target — dev is the source of truth
    admin.execute("CREATE DATABASE %s CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci" % TARGET)
    admin.disconnect()

    tcfg = dict(cfg); tcfg['database'] = TARGET
    t = DatabaseManager(**tcfg); t.connect()

    schema = open(SCHEMA).read()
    schema = re.sub(r"DEFINER=`[^`]*`@`[^`]*` SQL SECURITY DEFINER ", "", schema)   # portable definer
    # strip ALL -- comments (inline too) before splitting — an inline comment can hold a ';'
    nocomm = '\n'.join((ln[:ln.find('--')] if '--' in ln else ln) for ln in schema.splitlines())
    n = 0
    for stmt in nocomm.split(';'):
        if stmt.strip():
            t.execute(stmt.strip()); n += 1
    print('schema: %d statements' % n)

    for tbl in SEED:
        t.execute("INSERT INTO %s SELECT * FROM %s.%s" % (tbl, src, tbl))
        print('  seeded %-22s %d' % (tbl, t.execute("SELECT COUNT(*) c FROM %s" % tbl, fetch=True)[0]['c']))

    s5m = t.execute("SELECT ic_bb_len FROM vw_indicator_configs_live WHERE ind_name='s5m'", fetch=True)
    lc = lr_config(t)
    print('verify: s5m_len live=%s · lr_config arms=%d gates=%d finishers=%d sl=%s'
          % (s5m[0]['ic_bb_len'] if s5m else '??', len(lc.arms), len(lc.gates), len(lc.finishers), lc.sl))
    t.disconnect()


if __name__ == '__main__':
    main()
