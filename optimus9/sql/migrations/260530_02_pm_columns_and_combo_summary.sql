-- ═══════════════════════════════════════════════════════════════════════════
-- 260530_02_pm_columns_and_combo_summary
-- ═══════════════════════════════════════════════════════════════════════════
--
-- Filed: 2026-05-30 (r07 sweep architecture fix)
--
-- Intent: two coupled changes that unblock per-pm-dim analysis:
--
--   1. ADD pks_pm_additive + pks_pm_suppression columns to pk_signals so
--      vote-sourced grinds can tag each signal with the PM dial values that
--      produced it. Until this, 39K-combo sweeps over (slope_floor x
--      pm_additive x pm_suppression) conflated to ~41 visible groups in AM
--      (one per slope_floor) because no column carried the pm dims.
--
--   2. CREATE pk_combo_summary — a per-combo aggregate table that
--      OptimizerRunner populates as each combo's outcomes complete. AM
--      reads from this table directly instead of running a multi-million-
--      row GROUP BY on pk_signals + pk_outcomes. The GROUP BY did 40 min
--      on or_pk=54 (76.5M signals → 41 groups); pre-aggregation makes the
--      same load O(combos) instead of O(signals).
--
-- Surfaced by: first vote-sourced 7-day grind (or_pk=54, tc_pk=104,
-- 2026-05-30) producing 76.5M signals collapsed to 41 analytical buckets
-- instead of 39,401.
--
-- Usage:
--   mysql -u<user> -p<pass> pk_optimizer < 260530_02_pm_columns_and_combo_summary.sql
--
-- Reversible: pk_signals columns nullable, can be dropped. pk_combo_summary
--   can be DROP TABLE-d; AM has a fallback path to GROUP BY on pk_signals
--   when no summary rows exist for an or_pk (backward compat for pre-
--   refactor grinds).
--
-- Dependencies: pk_signals (extended), pk_combo_summary (new).
--
-- ═══════════════════════════════════════════════════════════════════════════

-- ─── 1. Extend pk_signals with PM dial columns ──────────────────────────────
-- DECIMAL(6,4) covers the swept range [0.0, 1.5] with 4-digit precision.
-- NULL = "this signal's path doesn't have pm dials" (line-sourced grinds).
ALTER TABLE pk_signals
    ADD COLUMN pks_pm_additive    DECIMAL(6,4) NULL AFTER pks_slope_floor,
    ADD COLUMN pks_pm_suppression DECIMAL(6,4) NULL AFTER pks_pm_additive;

-- ─── 2. Per-combo aggregates table ──────────────────────────────────────────
CREATE TABLE pk_combo_summary (
    pcs_pk              INT UNSIGNED   NOT NULL AUTO_INCREMENT PRIMARY KEY,
    pcs_or_pk           INT UNSIGNED   NOT NULL,
    -- Combo-identifying columns (mirror pk_signals)
    pcs_len             SMALLINT UNSIGNED  NULL,
    pcs_mult            DECIMAL(8,4)       NULL,
    pcs_src             VARCHAR(10)        NULL,
    pcs_pool_c          SMALLINT UNSIGNED  NULL,
    pcs_pool_w          SMALLINT UNSIGNED  NULL,
    pcs_pool_range      SMALLINT UNSIGNED  NULL,
    pcs_slope_floor     DECIMAL(8,4)       NULL,
    pcs_multiplier      SMALLINT UNSIGNED  NULL,
    pcs_len_rsi         SMALLINT UNSIGNED  NULL,
    pcs_len_stoch       SMALLINT UNSIGNED  NULL,
    pcs_pm_additive     DECIMAL(6,4)       NULL,
    pcs_pm_suppression  DECIMAL(6,4)       NULL,
    -- Provenance: profit_zone that the won/stopped/inconc counts were
    -- computed against. Lets AM detect stale summaries if the tc's
    -- profit_zone changes.
    pcs_profit_zone     DECIMAL(8,4)       NOT NULL,
    -- Aggregates (1:1 with AnalyzeManager._load_combo_summaries output)
    pcs_total           INT UNSIGNED       NOT NULL,
    pcs_won             INT UNSIGNED       NOT NULL,
    pcs_stopped_ct      INT UNSIGNED       NOT NULL,
    pcs_inconclusive_ct INT UNSIGNED       NOT NULL,
    pcs_avg_win_pct     DECIMAL(12,6)      NULL,  -- NULL if no wins
    pcs_avg_bars        DECIMAL(12,4)      NULL,  -- NULL if all stop=NULL
    pcs_avg_bars_peak   DECIMAL(12,4)      NULL,
    INDEX idx_pcs_or_pk (pcs_or_pk)
) ENGINE=InnoDB;
