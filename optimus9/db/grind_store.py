"""
grind_store.py (Joe 0622) — the single persistence seam for grind results (docs/grind_storage_spec.md).

Any grind, any machine, stores THROUGH here: one `grind_run` (config JSON, window, engine_rev,
headline KPI) + per-cell `grind_result` rows (cell params JSON, metrics JSON, the KPI a named
column for ranking). SRP: the ONLY home for grind persistence — no bespoke per-grind tables.
`vw_grind_leaderboard` ranks live runs by KPI per kind (the discovery surface).

    gs  = GrindStore(db)
    run = gs.register_run('bias_cascade', config=cfg_dict, window_start=R0, window_end=R1,
                          engine_rev=rev, kpi_name='cascade_placement_rate')
    gs.write_results(run, [{'cell': {...}, 'metrics': {...}, 'kpi': 0.43}, ...])
    gs.finalize(run, kpi_value=0.43, mark_live=True)
"""
import json


class GrindStore:
    def __init__(self, db):
        self._db = db
        self._ensure()

    def _ensure(self):
        self._db.execute('''CREATE TABLE IF NOT EXISTS grind_run (
            gr_pk           BIGINT AUTO_INCREMENT PRIMARY KEY,
            gr_kind         VARCHAR(40) NOT NULL,        -- bias_cascade / s30_swing / bl_dialin ...
            gr_config       JSON,                        -- the grind's knobs (BiasConfig / grid def ...)
            gr_window_start BIGINT, gr_window_end BIGINT, -- ms epoch (multi-window → list in gr_config)
            gr_engine_rev   VARCHAR(40),                 -- engine md5 — pins reproducibility
            gr_kpi_name     VARCHAR(40),                 -- e.g. cascade_placement_rate
            gr_kpi_value    FLOAT,                        -- headline KPI (best cell / aggregate)
            gr_is_live      TINYINT DEFAULT 0,           -- 1 = current/live result for this gr_kind
            gr_created_dt   DATETIME DEFAULT CURRENT_TIMESTAMP,
            gr_notes        VARCHAR(255),
            INDEX (gr_kind, gr_is_live))''')
        self._db.execute('''CREATE TABLE IF NOT EXISTS grind_result (
            grr_pk      BIGINT AUTO_INCREMENT PRIMARY KEY,
            grr_run_pk  BIGINT NOT NULL,                 -- → grind_run.gr_pk
            grr_cell    JSON,                            -- the config-cell params
            grr_metrics JSON,                            -- all metrics for the cell
            grr_kpi     FLOAT,                           -- the cell's KPI — named/indexed for ranking
            INDEX (grr_run_pk), INDEX (grr_kpi))''')
        self._db.execute('''CREATE OR REPLACE VIEW vw_grind_leaderboard AS
            SELECT gr_kind, gr_pk, gr_kpi_name, gr_kpi_value, gr_window_start, gr_window_end,
                   gr_engine_rev, gr_config, gr_created_dt
            FROM grind_run WHERE gr_is_live = 1 ORDER BY gr_kind, gr_kpi_value DESC''')

    def register_run(self, kind, config, window_start=None, window_end=None,
                     engine_rev=None, kpi_name=None, notes=None) -> int:
        """Open a run; returns gr_pk. `config` is any JSON-able dict (the grind's knobs)."""
        return self._db.execute(
            '''INSERT INTO grind_run (gr_kind, gr_config, gr_window_start, gr_window_end,
               gr_engine_rev, gr_kpi_name, gr_notes) VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            (kind, json.dumps(config), window_start, window_end, engine_rev, kpi_name, notes))

    def write_results(self, run_pk, cells) -> int:
        """`cells` = [{'cell': {...}, 'metrics': {...}, 'kpi': float}, ...]. Bulk insert; returns
        the first grr_pk. The KPI is promoted to its column; everything else stays in JSON."""
        rows = [(run_pk, json.dumps(c['cell']), json.dumps(c['metrics']), c.get('kpi'))
                for c in cells]
        return self._db.executemany(
            'INSERT INTO grind_result (grr_run_pk, grr_cell, grr_metrics, grr_kpi) VALUES (%s,%s,%s,%s)',
            rows)

    def finalize(self, run_pk, kpi_value, mark_live=False):
        """Set the headline KPI. `mark_live` promotes this run as THE live result for its kind
        (demoting siblings), so vw_grind_leaderboard shows one current row per kind."""
        self._db.execute('UPDATE grind_run SET gr_kpi_value=%s WHERE gr_pk=%s', (kpi_value, run_pk))
        if mark_live:
            kind = self._db.execute('SELECT gr_kind FROM grind_run WHERE gr_pk=%s',
                                    (run_pk,), fetch=True)[0]['gr_kind']
            self._db.execute('UPDATE grind_run SET gr_is_live=0 WHERE gr_kind=%s AND gr_pk<>%s',
                             (kind, run_pk))
            self._db.execute('UPDATE grind_run SET gr_is_live=1 WHERE gr_pk=%s', (run_pk,))
