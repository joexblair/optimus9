-- r05 wider grid for parallel 3-grind overnight run.
-- Joe: stop=0.71 (tc_pk=7), Sifu: stop=0.95 (tc_pk=6), new: stop=0.60 (tc_pk=8).
-- Same param sweep for all three so centroids are directly comparable.
-- Drops `mult` from sweep (held at OG 0.74). Widens len/pool_c/pool_w/slope_floor
-- to surface real sensitivity that the previous narrow grid couldn't see.
--
-- Combo count per tc: 7 × 5 × 9 × 7 × 3 × 9 × 1 = 59,535 (~16hr each)

START TRANSACTION;

-- ── 1. Create tc_pk=8 (stop=0.60) by cloning tc_pk=6 ─────────────────────
INSERT INTO test_configs (
    tc_tp_pk, tc_ic_pk, tc_indicator_label,
    tc_dema_len, tc_dema_src,
    tc_stop_pct, tc_dynamic_stoploss, tc_stop_buffer,
    tc_profit_zone, tc_drag_pct, tc_max_bars
)
SELECT
    tc_tp_pk, tc_ic_pk, 'gcs5m_stop060',
    tc_dema_len, tc_dema_src,
    0.60, 0, tc_stop_buffer,
    tc_profit_zone, tc_drag_pct, tc_max_bars
FROM test_configs WHERE tc_pk = 6;

-- ── 2. Clear any existing param ranges for tc 6, 7, 8 (safety reset) ────
DELETE FROM test_param_ranges WHERE tpr_tc_pk IN (6, 7, 8);

-- ── 3. Bulk-insert identical ranges for all three tcs ───────────────────
-- CROSS JOIN expands each param row × each tc, so one VALUES block covers
-- all 3 grinds. Adjust the inline VALUES below to retune the sweep.
INSERT INTO test_param_ranges (
    tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
    tpr_enum_values, tpr_param_type
)
SELECT tc.tc_pk, p.name, p.curr, p.step, p.rng, p.enum, p.type
FROM test_configs tc
CROSS JOIN (
    --             name              curr  step   rng    enum                            type
    SELECT 'len'              AS name, 14.0 AS curr, 2.0 AS step, 12.0 AS rng, NULL AS enum, 'int'   AS type
    UNION ALL SELECT 'mult',              0.74,        0.0,           0.0,           NULL,                                  'float'
    UNION ALL SELECT 'src',               NULL,        NULL,          NULL,          'close,hl2,hlc3,hlcc4,ohlc4',           'enum'
    UNION ALL SELECT 'pool_c',            32.0,        2.0,           16.0,          NULL,                                  'int'
    UNION ALL SELECT 'pool_w',            70.0,        5.0,           30.0,          NULL,                                  'int'
    UNION ALL SELECT 'pool_range',        4.0,         2.0,           4.0,           NULL,                                  'int'
    UNION ALL SELECT 'slope_floor',       5.0,         0.5,           4.0,           NULL,                                  'float'
    UNION ALL SELECT 'multiplier',        1.0,         0.0,           0.0,           NULL,                                  'int'
    UNION ALL SELECT 'tcev_weight_close', 5.0,         0.0,           0.0,           NULL,                                  'int'
    UNION ALL SELECT 'tcev_weight_wide',  2.0,         0.0,           0.0,           NULL,                                  'int'
) p
WHERE tc.tc_pk IN (6, 7, 8);

COMMIT;

-- ── Verify ──────────────────────────────────────────────────────────────
SELECT tc.tc_pk, tc.tc_indicator_label, tc.tc_stop_pct,
       COUNT(tpr.tpr_pk) AS param_count
FROM test_configs tc
LEFT JOIN test_param_ranges tpr ON tpr.tpr_tc_pk = tc.tc_pk
WHERE tc.tc_pk IN (6, 7, 8)
GROUP BY tc.tc_pk, tc.tc_indicator_label, tc.tc_stop_pct
ORDER BY tc.tc_pk;

-- Expected output:
--  tc_pk  tc_indicator_label  tc_stop_pct  param_count
--      6  gcs5m_stop135_2         0.9500           10
--      7  gcs5m_2                 0.7100           10
--      8  gcs5m_stop060           0.6000           10
--
-- Each tc has 10 param rows producing:
--   len(7) × mult(1) × src(5) × pool_c(9) × pool_w(7) × pool_range(3) × slope_floor(9) × multiplier(1) = 59,535 combos
