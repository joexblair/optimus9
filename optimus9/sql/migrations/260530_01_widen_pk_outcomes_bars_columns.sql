-- ═══════════════════════════════════════════════════════════════════════════
-- 260530_01_widen_pk_outcomes_bars_columns
-- ═══════════════════════════════════════════════════════════════════════════
--
-- Filed: 2026-05-30 (r07 grind setup)
--
-- Intent: widen `pko_bars_to_stop` and `pko_bars_to_max_profit` from
--   `smallint unsigned` (max 65,535) to `int unsigned`. Original schema
--   sized for 1-day grinds (~17,280 5s bars); 7-day grinds (~121K bars)
--   overflow `smallint` when a signal happens early and its event-bar
--   is far out. The MAE pipeline (r04) already widened
--   `pko_bars_to_max_adverse` to `int` — this migration brings the
--   other two bar-counter columns into line with it.
--
-- Surfaced by: first vote-sourced 7-day integration grind (tc_pk=103,
--   2026-05-30) failed at row 159 with
--   "Out of range value for column 'pko_bars_to_max_profit'".
--
-- Usage:
--   mysql -u<user> -p<pass> pk_optimizer < 260530_01_widen_pk_outcomes_bars_columns.sql
--
-- Reversible: yes, but values exceeding 65,535 would be lost on
--   downsizing — not recommended after this migration has shipped
--   long-window grind outcomes.
--
-- Dependencies: pk_outcomes table.
--
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE pk_outcomes
    MODIFY COLUMN pko_bars_to_stop        INT UNSIGNED NULL,
    MODIFY COLUMN pko_bars_to_max_profit  INT UNSIGNED NULL;
