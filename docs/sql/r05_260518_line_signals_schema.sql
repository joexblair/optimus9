-- r05 — line_signals schema for support/friction (SnF) affinity analysis
-- ============================================================================
-- Captures per-line PK fires from centroid configs, with outcomes computed
-- against the three candidate stops. Foundation for MultilineOptimiser
-- (weights from line affinity rather than xlsx intuition).
--
-- Two tables:
--   line_signal_runs — one row per generation event (a fold). Captures
--                      the window, the centroid config per line, and
--                      whether gating was on. Reproducible/regeneratable.
--   line_signals    — one row per PK fire. Slope/value at signal time
--                      plus outcomes per stop (3 stops × 2 fields = 6 cols).
--
-- Why per-fire outcomes instead of computing at query time:
--   Affinity matrices need to filter "supports preceding wins" vs
--   "supports preceding losses". Pre-computing outcome fields keeps
--   query SQL straightforward. Stops 0.60/0.71/0.95 are fixed for r05.
-- ============================================================================

CREATE TABLE line_signal_runs (
    lsr_pk           int UNSIGNED NOT NULL AUTO_INCREMENT,
    lsr_tp_pk        int UNSIGNED NOT NULL,          -- trading pair
    lsr_window_start bigint UNSIGNED NOT NULL,       -- ms epoch
    lsr_window_end   bigint UNSIGNED NOT NULL,       -- ms epoch
    lsr_ic_pks       varchar(200) NOT NULL,          -- comma-separated, e.g. '4,5,6,7,8,9'
    lsr_centroids    json NOT NULL,                  -- { "4": {len, mult, src, pool_c, ...}, ... }
    lsr_stops_json   json NOT NULL,                  -- ["0.60", "0.71", "0.95"]
    lsr_gating_on    tinyint UNSIGNED NOT NULL DEFAULT 0,  -- bny30M/p gating applied?
    lsr_created_at   datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lsr_notes        varchar(255) DEFAULT NULL,
    PRIMARY KEY (lsr_pk),
    INDEX idx_lsr_tp_window (lsr_tp_pk, lsr_window_start)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


CREATE TABLE line_signals (
    ls_pk           int UNSIGNED NOT NULL AUTO_INCREMENT,
    ls_lsr_pk       int UNSIGNED NOT NULL,           -- FK → line_signal_runs
    ls_timestamp    bigint UNSIGNED NOT NULL,        -- ms epoch
    ls_ic_pk        smallint UNSIGNED NOT NULL,      -- which line fired
    ls_direction    tinyint NOT NULL,                -- +1=LONG, -1=SHORT

    -- Per-bar diagnostics at signal time (for slope-weighted affinity)
    ls_line_value   decimal(14,6) DEFAULT NULL,      -- line value at fire bar
    ls_slope        decimal(14,6) DEFAULT NULL,      -- line slope at fire bar (signed)
    ls_dema_value   decimal(14,6) DEFAULT NULL,      -- DEMA value at fire bar

    -- Outcomes per stop. max_profit_pct = max favorable %; bars_to_stop NULL
    -- means the trade ran out the max_bars window without stopping.
    ls_max_profit_60   decimal(8,4) DEFAULT NULL,
    ls_bars_to_stop_60 int DEFAULT NULL,
    ls_max_profit_71   decimal(8,4) DEFAULT NULL,
    ls_bars_to_stop_71 int DEFAULT NULL,
    ls_max_profit_95   decimal(8,4) DEFAULT NULL,
    ls_bars_to_stop_95 int DEFAULT NULL,

    PRIMARY KEY (ls_pk),
    INDEX idx_ls_lsr_ts     (ls_lsr_pk, ls_timestamp),
    INDEX idx_ls_lsr_ic     (ls_lsr_pk, ls_ic_pk),
    INDEX idx_ls_lsr_ic_dir (ls_lsr_pk, ls_ic_pk, ls_direction, ls_timestamp),
    CONSTRAINT fk_ls_lsr FOREIGN KEY (ls_lsr_pk)
        REFERENCES line_signal_runs(lsr_pk)
        ON DELETE CASCADE
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


-- ── Sanity-check query (run after first fold) ───────────────────────────
-- Counts fires per line per direction in the latest fold:
-- SELECT ls_ic_pk, ls_direction, COUNT(*) AS fires
-- FROM line_signals ls
-- JOIN line_signal_runs lsr ON lsr.lsr_pk = ls.ls_lsr_pk
-- WHERE lsr.lsr_pk = (SELECT MAX(lsr_pk) FROM line_signal_runs)
-- GROUP BY ls_ic_pk, ls_direction
-- ORDER BY ls_ic_pk, ls_direction;
