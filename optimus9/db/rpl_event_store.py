"""
rpl_event_store.py (0719) — persistence seam for the rpl flow (r-pred → x-cross-pred →
bias_trend_flip → flip_div). Event-grain, NOT KPI-grain (that's GrindStore's job), so a sibling
store: a named `rpl_config` baseline holds every knob (no hardcoded values), each run pins the
config it read, and the teed event stream lands as rows.

    st  = RplEventStore(db)
    cfg = st.load_config('baseline')                 # knobs from DB — the flow reads THESE
    run = st.register_run('bull', w0, w1, cfg['rc_pk'], engine_rev=rev)
    st.log_events(run, events)                        # bulk; events = tee buffer
    st.set_entry(run, entry_ms)

Analysis is then SQL: vw_rpl_entries = every entry row joined to the knobs that produced it.
"""
import json
import datetime as _dtm
from datetime import timezone as _tz

_utc = lambda ms: _dtm.datetime.fromtimestamp(int(ms) / 1000, _tz.utc).strftime('%Y-%m-%d %H:%M:%S')


class RplEventStore:
    def __init__(self, db):
        self._db = db
        self._ensure()

    def _ensure(self):
        self._db.execute('''CREATE TABLE IF NOT EXISTS rpl_config (
            rc_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
            rc_name      VARCHAR(40) NOT NULL UNIQUE,     -- 'baseline', 'anti40' ...
            rc_knobs     JSON NOT NULL,                   -- every flow knob (line cfgs, fence, anti, vmin, carry, ...)
            rc_created_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
            rc_notes     VARCHAR(255))''')
        self._db.execute('''CREATE TABLE IF NOT EXISTS rpl_run (
            rr_pk           BIGINT AUTO_INCREMENT PRIMARY KEY,
            rr_config_pk    BIGINT NOT NULL,              -- → rpl_config.rc_pk (the knobs this run read)
            rr_side         VARCHAR(8) NOT NULL,          -- bull / bear
            rr_window_start BIGINT, rr_window_end BIGINT, -- ms epoch
            rr_engine_rev   VARCHAR(40),                  -- flow-script md5 — reproducibility pin
            rr_walk         VARCHAR(8),                   -- walk label MMDD_NN (e.g. 0712_01), first flip of the day = MMDD_01
            rr_rollercoaster TINYINT DEFAULT 0,           -- 1 = counter-trend rollercoaster flip (NO pyramid trade); 0 = climb flip
            rr_entry_ms     BIGINT,                       -- resolved flip_div entry (NULL = none)
            rr_created_dt   DATETIME DEFAULT CURRENT_TIMESTAMP,
            rr_notes        VARCHAR(255),
            INDEX (rr_config_pk), INDEX (rr_side),
            CONSTRAINT fk_rpl_run_config FOREIGN KEY (rr_config_pk) REFERENCES rpl_config (rc_pk))''')
        self._db.execute('''CREATE TABLE IF NOT EXISTS rpl_event (
            re_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
            re_run_pk   BIGINT NOT NULL,                  -- → rpl_run.rr_pk
            re_ts       BIGINT NOT NULL,                  -- ms epoch of the event
            re_utc      DATETIME,                         -- human-readable UTC of re_ts (store-written, UTC-correct)
            re_stage    VARCHAR(20) NOT NULL,             -- r-pred / x-cross-pred / bias_trend_flip / flip_div
            re_tf       INT,                              -- the TF this event belongs to (NULL for div)
            re_called_by INT,                             -- r-pred: the current_tf that initiated the upward scan
            re_r        FLOAT, re_x FLOAT,                -- line values at the event
            re_net      INT,                              -- div: same-side vote count
            re_votes    JSON,                             -- div: {s1r,s1M,s30r,s30M}
            re_mode     VARCHAR(24),                      -- x-cross-pred: predict/backstop + s2r
            re_note     VARCHAR(64),
            re_is_entry TINYINT DEFAULT 0,                -- 1 = this div row is the chosen entry
            INDEX (re_run_pk, re_stage), INDEX (re_ts),
            CONSTRAINT fk_rpl_event_run FOREIGN KEY (re_run_pk) REFERENCES rpl_run (rr_pk) ON DELETE CASCADE)''')
        # migrations BEFORE the view — the view references columns added here on pre-existing tables
        self._migrate_re_utc()
        self._migrate_col('rpl_event', 're_called_by', 'INT', 'AFTER re_tf')
        self._migrate_col('rpl_run', 'rr_walk', 'VARCHAR(8)', 'AFTER rr_engine_rev')
        self._migrate_col('rpl_run', 'rr_rollercoaster', 'TINYINT DEFAULT 0', 'AFTER rr_walk')
        self._migrate_fk('rpl_run', 'fk_rpl_run_config',
                         'FOREIGN KEY (rr_config_pk) REFERENCES rpl_config (rc_pk)')
        self._migrate_fk('rpl_event', 'fk_rpl_event_run',
                         'FOREIGN KEY (re_run_pk) REFERENCES rpl_run (rr_pk) ON DELETE CASCADE')
        self._db.execute('''CREATE OR REPLACE VIEW vw_rpl_entries AS
            SELECT r.rr_pk, r.rr_walk, r.rr_side, e.re_ts AS entry_ms, e.re_net, e.re_votes,
                   r.rr_window_start, r.rr_window_end, c.rc_name, c.rc_knobs
            FROM rpl_event e
            JOIN rpl_run r    ON r.rr_pk = e.re_run_pk
            JOIN rpl_config c ON c.rc_pk = r.rr_config_pk
            WHERE e.re_is_entry = 1
            ORDER BY e.re_ts DESC''')

    def _has_col(self, table, col):
        return bool(self._db.execute(
            '''SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE()
               AND table_name=%s AND column_name=%s''', (table, col), fetch=True))

    def _migrate_col(self, table, col, decl, pos=''):
        """Idempotently add a nullable column to a pre-existing table (no backfill)."""
        if not self._has_col(table, col):
            self._db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl} {pos}".strip())

    def _migrate_fk(self, table, name, spec):
        """Idempotently add a named FK to a pre-existing table (fresh installs get it in CREATE)."""
        exists = self._db.execute(
            '''SELECT 1 FROM information_schema.table_constraints WHERE table_schema=DATABASE()
               AND table_name=%s AND constraint_name=%s AND constraint_type='FOREIGN KEY' ''',
            (table, name), fetch=True)
        if not exists:
            self._db.execute(f"ALTER TABLE {table} ADD CONSTRAINT {name} {spec}")

    def _migrate_re_utc(self):
        """Add re_utc to a pre-existing rpl_event and backfill it UTC-correct (TIMESTAMPADD on the
        epoch literal is tz-independent, unlike FROM_UNIXTIME). No-op once the column exists."""
        self._migrate_col('rpl_event', 're_utc', 'DATETIME', 'AFTER re_ts')
        self._db.execute(
            "UPDATE rpl_event SET re_utc = TIMESTAMPADD(SECOND, re_ts DIV 1000, '1970-01-01 00:00:00') "
            "WHERE re_utc IS NULL")

    # --- config baseline (no hardcoded knobs) ---
    def upsert_config(self, name, knobs, notes=None) -> int:
        """Create/replace a named knob baseline. Returns rc_pk."""
        self._db.execute(
            '''INSERT INTO rpl_config (rc_name, rc_knobs, rc_notes) VALUES (%s,%s,%s)
               ON DUPLICATE KEY UPDATE rc_knobs=VALUES(rc_knobs), rc_notes=VALUES(rc_notes)''',
            (name, json.dumps(knobs), notes))
        return self.load_config(name)['rc_pk']

    def load_config(self, name) -> dict:
        """Return {'rc_pk': int, 'rc_name': str, **knobs}. Raises if the baseline is absent."""
        row = self._db.execute('SELECT rc_pk, rc_name, rc_knobs FROM rpl_config WHERE rc_name=%s',
                               (name,), fetch=True)
        if not row:
            raise KeyError(f'rpl_config baseline {name!r} not found — seed it first')
        r = row[0]
        return {'rc_pk': r['rc_pk'], 'rc_name': r['rc_name'], **json.loads(r['rc_knobs'])}

    # --- run + event stream ---
    def register_run(self, side, window_start, window_end, config_pk, engine_rev=None, walk=None, notes=None, rollercoaster=0) -> int:
        return self._db.execute(
            '''INSERT INTO rpl_run (rr_config_pk, rr_side, rr_window_start, rr_window_end,
               rr_engine_rev, rr_walk, rr_rollercoaster, rr_notes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
            (config_pk, side, window_start, window_end, engine_rev, walk, int(rollercoaster), notes))

    def log_events(self, run_pk, events) -> int:
        """`events` = [{ts, stage, tf?, r?, x?, net?, votes?, mode?, note?, is_entry?}, ...]. Bulk."""
        if not events:
            return 0
        rows = [(run_pk, int(e['ts']), _utc(e['ts']), e['stage'], e.get('tf'), e.get('called_by'),
                 e.get('r'), e.get('x'), e.get('net'),
                 json.dumps(e['votes']) if e.get('votes') is not None else None,
                 e.get('mode'), e.get('note'), 1 if e.get('is_entry') else 0)
                for e in events]
        return self._db.executemany(
            '''INSERT INTO rpl_event (re_run_pk, re_ts, re_utc, re_stage, re_tf, re_called_by, re_r, re_x,
               re_net, re_votes, re_mode, re_note, re_is_entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            rows)

    def set_entry(self, run_pk, entry_ms):
        self._db.execute('UPDATE rpl_run SET rr_entry_ms=%s WHERE rr_pk=%s', (entry_ms, run_pk))
