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
            rr_entry_ms     BIGINT,                       -- resolved flip_div entry (NULL = none)
            rr_created_dt   DATETIME DEFAULT CURRENT_TIMESTAMP,
            rr_notes        VARCHAR(255),
            INDEX (rr_config_pk), INDEX (rr_side))''')
        self._db.execute('''CREATE TABLE IF NOT EXISTS rpl_event (
            re_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
            re_run_pk   BIGINT NOT NULL,                  -- → rpl_run.rr_pk
            re_ts       BIGINT NOT NULL,                  -- ms epoch of the event
            re_stage    VARCHAR(20) NOT NULL,             -- r-pred / x-cross-pred / bias_trend_flip / flip_div
            re_tf       INT,                              -- the TF this event belongs to (NULL for div)
            re_r        FLOAT, re_x FLOAT,                -- line values at the event
            re_net      INT,                              -- div: same-side vote count
            re_votes    JSON,                             -- div: {s1r,s1M,s30r,s30M}
            re_mode     VARCHAR(24),                      -- x-cross-pred: predict/backstop + s2r
            re_note     VARCHAR(64),
            re_is_entry TINYINT DEFAULT 0,                -- 1 = this div row is the chosen entry
            INDEX (re_run_pk, re_stage), INDEX (re_ts))''')
        self._db.execute('''CREATE OR REPLACE VIEW vw_rpl_entries AS
            SELECT r.rr_pk, r.rr_side, e.re_ts AS entry_ms, e.re_net, e.re_votes,
                   r.rr_window_start, r.rr_window_end, c.rc_name, c.rc_knobs
            FROM rpl_event e
            JOIN rpl_run r    ON r.rr_pk = e.re_run_pk
            JOIN rpl_config c ON c.rc_pk = r.rr_config_pk
            WHERE e.re_is_entry = 1
            ORDER BY e.re_ts DESC''')

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
    def register_run(self, side, window_start, window_end, config_pk, engine_rev=None, notes=None) -> int:
        return self._db.execute(
            '''INSERT INTO rpl_run (rr_config_pk, rr_side, rr_window_start, rr_window_end,
               rr_engine_rev, rr_notes) VALUES (%s,%s,%s,%s,%s,%s)''',
            (config_pk, side, window_start, window_end, engine_rev, notes))

    def log_events(self, run_pk, events) -> int:
        """`events` = [{ts, stage, tf?, r?, x?, net?, votes?, mode?, note?, is_entry?}, ...]. Bulk."""
        if not events:
            return 0
        rows = [(run_pk, int(e['ts']), e['stage'], e.get('tf'), e.get('r'), e.get('x'),
                 e.get('net'), json.dumps(e['votes']) if e.get('votes') is not None else None,
                 e.get('mode'), e.get('note'), 1 if e.get('is_entry') else 0)
                for e in events]
        return self._db.executemany(
            '''INSERT INTO rpl_event (re_run_pk, re_ts, re_stage, re_tf, re_r, re_x, re_net,
               re_votes, re_mode, re_note, re_is_entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            rows)

    def set_entry(self, run_pk, entry_ms):
        self._db.execute('UPDATE rpl_run SET rr_entry_ms=%s WHERE rr_pk=%s', (entry_ms, run_pk))
