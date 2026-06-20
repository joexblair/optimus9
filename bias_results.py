"""
bias_results.py — SRP persistence for bias-machine sweeps (Joe 0620).

  bias_config   — one row per config; columns INTROSPECTED from BiasConfig (single source of truth),
                  auto-migrated when BiasConfig gains a field. Code (str) columns are case-sensitive
                  (utf8mb4_0900_as_cs) so 'm' != 'M'.
  bias_eval     — one row per (config × window) run: FK cfg, window bounds, run_ts, engine_rev.
  bias_pk_results — the pk-anchor/floater mechanic's metrics, FK eval. Future mechanics (line
                  positioning, line cross) land as SIBLING tables under the same bias_eval.
"""
import dataclasses
import hashlib
import bias_machine as bm

ENGINE_FILE = '/home/joe/thecodes/bias_machine.py'


def _sqltype(v):
    if isinstance(v, bool):  return 'TINYINT'                    # bool before int (bool ⊂ int)
    if isinstance(v, int):   return 'INT'
    if isinstance(v, float): return 'FLOAT'
    return 'VARCHAR(16) COLLATE utf8mb4_0900_as_cs'             # code columns: case-sensitive


def _col(name):
    # MySQL column NAMES are case-insensitive → gate_M/gate_m collide. Map the _M/_m line refs to
    # case-distinct column names (the BiasConfig field keeps its _M/_m — this is storage-layer only).
    if name.endswith('_M'): return name[:-2] + '_maj'
    if name.endswith('_m'): return name[:-2] + '_min'
    return name


def engine_rev():
    return hashlib.md5(open(ENGINE_FILE, 'rb').read()).hexdigest()[:12]


class BiasResults:
    def __init__(self, db):
        self.db = db
        self._fields = [f.name for f in dataclasses.fields(bm.BiasConfig)]

    def _id(self):
        return self.db.execute('SELECT LAST_INSERT_ID() id', fetch=True)[0]['id']

    def ensure_tables(self):
        db = self.db
        db.execute('''CREATE TABLE IF NOT EXISTS bias_config (
            cfg_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
            cfg_created_dt    DATETIME NOT NULL,
            cfg_live_after_dt DATETIME NOT NULL DEFAULT '2000-01-01')''')
        have = {c['Field'].lower() for c in db.execute('SHOW COLUMNS FROM bias_config', fetch=True)}
        proto = bm.BiasConfig()
        for name in self._fields:                               # introspected columns + auto-migrate
            col = _col(name)
            if col.lower() not in have:
                db.execute(f'ALTER TABLE bias_config ADD COLUMN `{col}` {_sqltype(getattr(proto, name))}')
        db.execute('''CREATE TABLE IF NOT EXISTS bias_eval (
            eval_pk BIGINT AUTO_INCREMENT PRIMARY KEY, eval_cfg_pk BIGINT NOT NULL,
            eval_window_start DATETIME, eval_window_end DATETIME,
            eval_run_ts DATETIME, eval_engine_rev VARCHAR(16),
            FOREIGN KEY (eval_cfg_pk) REFERENCES bias_config(cfg_pk))''')
        db.execute('''CREATE TABLE IF NOT EXISTS bias_pk_results (
            res_pk BIGINT AUTO_INCREMENT PRIMARY KEY, res_eval_pk BIGINT NOT NULL,
            res_correct INT, res_total INT,
            FOREIGN KEY (res_eval_pk) REFERENCES bias_eval(eval_pk))''')

    def config_pk(self, cfg, created, live_after):
        # find-or-insert by exact knob match (columns are _cs so '=' is case-sensitive on codes)
        vals = [getattr(cfg, n) for n in self._fields]
        where = ' AND '.join(f'`{_col(n)}`=%s' for n in self._fields)
        ex = self.db.execute(f'SELECT cfg_pk FROM bias_config WHERE {where}', tuple(vals), fetch=True)
        if ex:
            return ex[0]['cfg_pk']
        cols = ['cfg_created_dt', 'cfg_live_after_dt'] + [f'`{_col(n)}`' for n in self._fields]
        ph = ','.join(['%s'] * len(cols))
        self.db.execute(f'INSERT INTO bias_config ({",".join(cols)}) VALUES ({ph})',
                        tuple([created, live_after] + vals))
        return self._id()

    def write_eval(self, cfg_pk, w0, w1, run_ts, rev):
        self.db.execute('''INSERT INTO bias_eval
            (eval_cfg_pk, eval_window_start, eval_window_end, eval_run_ts, eval_engine_rev)
            VALUES (%s,%s,%s,%s,%s)''', (cfg_pk, w0, w1, run_ts, rev))
        return self._id()

    def write_pk_result(self, eval_pk, correct, total):
        self.db.execute('INSERT INTO bias_pk_results (res_eval_pk, res_correct, res_total) VALUES (%s,%s,%s)',
                        (eval_pk, correct, total))
