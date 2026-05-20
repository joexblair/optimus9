-- r05 wide 6-line grids — bny30 AND-gated calibration
-- ============================================================================
-- Joe runs 6 lines in parallel under bny30 AND-gating. Wider sweep on len,
-- pool_c, pool_w than r05 narrow round. At ~20K combos/hr per parallel slot,
--
-- Stop locked at 0.71 (middle of our 3 candidates; r05 grinds showed centroid
-- is stop-insensitive at ±0.05% expectancy across 0.60/0.71/0.95).
-- 
-- bny30 gating active via test_config_extensions tce_type='gate' rows.
-- Each tc points to its primary line via tc_ic_pk; OptimizerRunner runs the
-- single-line vote_overrides path per combo.
--
-- Per-line strategies:
--   BB lines (ic 4, 5, 8):  sweep len(7) × src(5) × pool_c(13) × pool_w(11)
--                            × pool_range(3) × slope_floor(5) = 75,075
--   K lines  (ic 6, 7, 9):  sweep k_len(3) × rsi(3) × src(5) × pool_c(13)
--                            × pool_w(11) × pool_range(3) × slope_floor(5) = 96,525
--
-- slope_floor 5 vals: 60, 90, 120, 150, 180 (centered on 120, step 30).
-- Diagnostic showed active region 80-110 for gcs5m ungated; under bny30
-- gating the active region likely shifts since signals are already filtered
-- upstream. Wide grid covers both the gcs5m-style "high floor" regime and
-- the possibility that lower floors work better post-gating.

-- NOTE: gca5m baseline len=6 with range 12 produces values [0, 2, ..., 12].
-- The 0 will be filtered by PGB's positive_length rule; gca5m gets 6 effective
-- len values (75,075 → 64,350 combos). Other 5 tcs unaffected.
-- ============================================================================

START TRANSACTION;

-- ───────────────────────────────────────────────────────────────────────
-- BB line 1: gcs5m (ic_pk=4)   baseline len=12, mult=0.74, src=hlcc4
-- ───────────────────────────────────────────────────────────────────────
INSERT INTO test_configs (
    tc_tp_pk, tc_ic_pk, tc_indicator_label,
    tc_dema_len, tc_dema_src, tc_stop_pct, tc_dynamic_stoploss,
    tc_stop_buffer, tc_profit_zone, tc_drag_pct, tc_max_bars
)
VALUES (1, 4, 'gcs5m_wide_gated', 2, 'close', 0.71, 0, 0.05, 0.60, 0.00, 1080);
SET @tc_gcs := LAST_INSERT_ID();

INSERT INTO test_config_extensions
    (tce_tc_pk, tce_type, tce_ic_pk, tce_is_active, tce_sort_order)
VALUES
    (@tc_gcs, 'gate', 2, 1, 1),
    (@tc_gcs, 'gate', 3, 1, 2);

INSERT INTO test_param_ranges
    (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
     tpr_enum_values, tpr_param_type)
VALUES
    (@tc_gcs, 'len',               12.0,  2.0,  12.0,   NULL,                              'int'),
    (@tc_gcs, 'mult',              0.74,  0.0,  0.0,   NULL,                              'float'),
    (@tc_gcs, 'src',               NULL,  NULL, NULL,  'close,hl2,hlc3,hlcc4,ohlc4',     'enum'),
    (@tc_gcs, 'pool_c',            32.0,  2.0,  24.0,  NULL,                              'int'),
    (@tc_gcs, 'pool_w',            70.0,  5.0,  50.0,  NULL,                              'int'),
    (@tc_gcs, 'pool_range',        4.0,   2.0,  4.0,   NULL,                              'int'),
    (@tc_gcs, 'slope_floor',       120.0, 30.0, 120.0, NULL,                              'float'),
    (@tc_gcs, 'multiplier',        1.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gcs, 'tcev_weight_close', 5.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gcs, 'tcev_weight_wide',  2.0,   0.0,  0.0,   NULL,                              'int');

-- ───────────────────────────────────────────────────────────────────────
-- BB line 2: gcb5M (ic_pk=5)   baseline len=40, mult=1.00, src=hl2
-- ───────────────────────────────────────────────────────────────────────
INSERT INTO test_configs (
    tc_tp_pk, tc_ic_pk, tc_indicator_label,
    tc_dema_len, tc_dema_src, tc_stop_pct, tc_dynamic_stoploss,
    tc_stop_buffer, tc_profit_zone, tc_drag_pct, tc_max_bars
)
VALUES (1, 5, 'gcb5M_wide_gated', 2, 'close', 0.71, 0, 0.05, 0.60, 0.00, 1080);
SET @tc_gcb := LAST_INSERT_ID();

INSERT INTO test_config_extensions
    (tce_tc_pk, tce_type, tce_ic_pk, tce_is_active, tce_sort_order)
VALUES
    (@tc_gcb, 'gate', 2, 1, 1),
    (@tc_gcb, 'gate', 3, 1, 2);

INSERT INTO test_param_ranges
    (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
     tpr_enum_values, tpr_param_type)
VALUES
    (@tc_gcb, 'len',               40.0,  2.0,  12.0,   NULL,                              'int'),
    (@tc_gcb, 'mult',              1.00,  0.0,  0.0,   NULL,                              'float'),
    (@tc_gcb, 'src',               NULL,  NULL, NULL,  'close,hl2,hlc3,hlcc4,ohlc4',     'enum'),
    (@tc_gcb, 'pool_c',            32.0,  2.0,  24.0,  NULL,                              'int'),
    (@tc_gcb, 'pool_w',            70.0,  5.0,  50.0,  NULL,                              'int'),
    (@tc_gcb, 'pool_range',        4.0,   2.0,  4.0,   NULL,                              'int'),
    (@tc_gcb, 'slope_floor',       120.0, 30.0, 120.0, NULL,                              'float'),
    (@tc_gcb, 'multiplier',        1.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gcb, 'tcev_weight_close', 5.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gcb, 'tcev_weight_wide',  2.0,   0.0,  0.0,   NULL,                              'int');

-- ───────────────────────────────────────────────────────────────────────
-- BB line 3: gca5m (ic_pk=8)   baseline len=6, mult=0.74, src=close
-- ───────────────────────────────────────────────────────────────────────
INSERT INTO test_configs (
    tc_tp_pk, tc_ic_pk, tc_indicator_label,
    tc_dema_len, tc_dema_src, tc_stop_pct, tc_dynamic_stoploss,
    tc_stop_buffer, tc_profit_zone, tc_drag_pct, tc_max_bars
)
VALUES (1, 8, 'gca5m_wide_gated', 2, 'close', 0.71, 0, 0.05, 0.60, 0.00, 1080);
SET @tc_gca := LAST_INSERT_ID();

INSERT INTO test_config_extensions
    (tce_tc_pk, tce_type, tce_ic_pk, tce_is_active, tce_sort_order)
VALUES
    (@tc_gca, 'gate', 2, 1, 1),
    (@tc_gca, 'gate', 3, 1, 2);

INSERT INTO test_param_ranges
    (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
     tpr_enum_values, tpr_param_type)
VALUES
    (@tc_gca, 'len',               6.0,   2.0,  8.0,   NULL,                              'int'),
    (@tc_gca, 'mult',              0.74,  0.0,  0.0,   NULL,                              'float'),
    (@tc_gca, 'src',               NULL,  NULL, NULL,  'close,hl2,hlc3,hlcc4,ohlc4',     'enum'),
    (@tc_gca, 'pool_c',            32.0,  2.0,  24.0,  NULL,                              'int'),
    (@tc_gca, 'pool_w',            70.0,  5.0,  50.0,  NULL,                              'int'),
    (@tc_gca, 'pool_range',        4.0,   2.0,  4.0,   NULL,                              'int'),
    (@tc_gca, 'slope_floor',       120.0, 30.0, 120.0, NULL,                              'float'),
    (@tc_gca, 'multiplier',        1.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gca, 'tcev_weight_close', 5.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gca, 'tcev_weight_wide',  2.0,   0.0,  0.0,   NULL,                              'int');

-- ───────────────────────────────────────────────────────────────────────
-- K line 1: gcb.5.p (ic_pk=6)   baseline k=5, rsi=38, stc=29, src=hlc3
-- ───────────────────────────────────────────────────────────────────────
INSERT INTO test_configs (
    tc_tp_pk, tc_ic_pk, tc_indicator_label,
    tc_dema_len, tc_dema_src, tc_stop_pct, tc_dynamic_stoploss,
    tc_stop_buffer, tc_profit_zone, tc_drag_pct, tc_max_bars
)
VALUES (1, 6, 'gcb5p_wide_gated', 2, 'close', 0.71, 0, 0.05, 0.60, 0.00, 1080);
SET @tc_gcbp := LAST_INSERT_ID();

INSERT INTO test_config_extensions
    (tce_tc_pk, tce_type, tce_ic_pk, tce_is_active, tce_sort_order)
VALUES
    (@tc_gcbp, 'gate', 2, 1, 1),
    (@tc_gcbp, 'gate', 3, 1, 2);

INSERT INTO test_param_ranges
    (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
     tpr_enum_values, tpr_param_type)
VALUES
    (@tc_gcbp, 'len',               5.0,   1.0,  2.0,   NULL,                              'int'),
    (@tc_gcbp, 'len_rsi',           38.0,  5.0,  10.0,  NULL,                              'int'),
    (@tc_gcbp, 'len_stoch',         29.0,  0.0,  0.0,   NULL,                              'int'),
    (@tc_gcbp, 'src',               NULL,  NULL, NULL,  'close,hl2,hlc3,hlcc4,ohlc4',     'enum'),
    (@tc_gcbp, 'pool_c',            32.0,  2.0,  24.0,  NULL,                              'int'),
    (@tc_gcbp, 'pool_w',            70.0,  5.0,  50.0,  NULL,                              'int'),
    (@tc_gcbp, 'pool_range',        4.0,   2.0,  4.0,   NULL,                              'int'),
    (@tc_gcbp, 'slope_floor',       120.0, 30.0, 120.0, NULL,                              'float'),
    (@tc_gcbp, 'multiplier',        1.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gcbp, 'tcev_weight_close', 5.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gcbp, 'tcev_weight_wide',  2.0,   0.0,  0.0,   NULL,                              'int');

-- ───────────────────────────────────────────────────────────────────────
-- K line 2: gca.5.o (ic_pk=7)   baseline k=4, rsi=9, stc=50, src=ohlc4
-- ───────────────────────────────────────────────────────────────────────
INSERT INTO test_configs (
    tc_tp_pk, tc_ic_pk, tc_indicator_label,
    tc_dema_len, tc_dema_src, tc_stop_pct, tc_dynamic_stoploss,
    tc_stop_buffer, tc_profit_zone, tc_drag_pct, tc_max_bars
)
VALUES (1, 7, 'gca5o_wide_gated', 2, 'close', 0.71, 0, 0.05, 0.60, 0.00, 1080);
SET @tc_gcao := LAST_INSERT_ID();

INSERT INTO test_config_extensions
    (tce_tc_pk, tce_type, tce_ic_pk, tce_is_active, tce_sort_order)
VALUES
    (@tc_gcao, 'gate', 2, 1, 1),
    (@tc_gcao, 'gate', 3, 1, 2);

INSERT INTO test_param_ranges
    (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
     tpr_enum_values, tpr_param_type)
VALUES
    (@tc_gcao, 'len',               4.0,   1.0,  2.0,   NULL,                              'int'),
    (@tc_gcao, 'len_rsi',           9.0,   5.0,  10.0,  NULL,                              'int'),
    (@tc_gcao, 'len_stoch',         50.0,  0.0,  0.0,   NULL,                              'int'),
    (@tc_gcao, 'src',               NULL,  NULL, NULL,  'close,hl2,hlc3,hlcc4,ohlc4',     'enum'),
    (@tc_gcao, 'pool_c',            32.0,  2.0,  24.0,  NULL,                              'int'),
    (@tc_gcao, 'pool_w',            70.0,  5.0,  50.0,  NULL,                              'int'),
    (@tc_gcao, 'pool_range',        4.0,   2.0,  4.0,   NULL,                              'int'),
    (@tc_gcao, 'slope_floor',       120.0, 30.0, 120.0, NULL,                              'float'),
    (@tc_gcao, 'multiplier',        1.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gcao, 'tcev_weight_close', 5.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gcao, 'tcev_weight_wide',  2.0,   0.0,  0.0,   NULL,                              'int');

-- ───────────────────────────────────────────────────────────────────────
-- K line 3: gcs.5.r (ic_pk=9)   baseline k=6, rsi=40, stc=96, src=hl2
-- ───────────────────────────────────────────────────────────────────────
INSERT INTO test_configs (
    tc_tp_pk, tc_ic_pk, tc_indicator_label,
    tc_dema_len, tc_dema_src, tc_stop_pct, tc_dynamic_stoploss,
    tc_stop_buffer, tc_profit_zone, tc_drag_pct, tc_max_bars
)
VALUES (1, 9, 'gcs5r_wide_gated', 2, 'close', 0.71, 0, 0.05, 0.60, 0.00, 1080);
SET @tc_gcsr := LAST_INSERT_ID();

INSERT INTO test_config_extensions
    (tce_tc_pk, tce_type, tce_ic_pk, tce_is_active, tce_sort_order)
VALUES
    (@tc_gcsr, 'gate', 2, 1, 1),
    (@tc_gcsr, 'gate', 3, 1, 2);

INSERT INTO test_param_ranges
    (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
     tpr_enum_values, tpr_param_type)
VALUES
    (@tc_gcsr, 'len',               6.0,   1.0,  2.0,   NULL,                              'int'),
    (@tc_gcsr, 'len_rsi',           40.0,  5.0,  10.0,  NULL,                              'int'),
    (@tc_gcsr, 'len_stoch',         96.0,  0.0,  0.0,   NULL,                              'int'),
    (@tc_gcsr, 'src',               NULL,  NULL, NULL,  'close,hl2,hlc3,hlcc4,ohlc4',     'enum'),
    (@tc_gcsr, 'pool_c',            32.0,  2.0,  24.0,  NULL,                              'int'),
    (@tc_gcsr, 'pool_w',            70.0,  5.0,  50.0,  NULL,                              'int'),
    (@tc_gcsr, 'pool_range',        4.0,   2.0,  4.0,   NULL,                              'int'),
    (@tc_gcsr, 'slope_floor',       120.0, 30.0, 120.0, NULL,                              'float'),
    (@tc_gcsr, 'multiplier',        1.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gcsr, 'tcev_weight_close', 5.0,   0.0,  0.0,   NULL,                              'int'),
    (@tc_gcsr, 'tcev_weight_wide',  2.0,   0.0,  0.0,   NULL,                              'int');

COMMIT;

-- ── Verify ──────────────────────────────────────────────────────────────
SELECT
    tc.tc_pk,
    tc.tc_indicator_label,
    tc.tc_ic_pk,
    tc.tc_stop_pct,
    (SELECT COUNT(*) FROM test_param_ranges WHERE tpr_tc_pk = tc.tc_pk)        AS params,
    (SELECT COUNT(*) FROM test_config_extensions WHERE tce_tc_pk = tc.tc_pk
        AND tce_type='gate' AND tce_is_active=1)                                AS gates
FROM test_configs tc
WHERE tc.tc_indicator_label LIKE '%_wide_gated'
ORDER BY tc.tc_pk;

-- Expected combo counts per tc:
--   BB lines: len(5) × mult(1) × src(5) × pool_c(11) × pool_w(7)
--             × pool_range(3) × slope_floor(4) × multiplier(1) = 29,700
--   K  lines: len(3) × len_rsi(3) × len_stoch(1) × src(5) × pool_c(7)
--             × pool_w(7) × pool_range(3) × slope_floor(4) × multiplier(1) = 22,680
-- Total: 3 × 75,075 + 3 × 96,525 = 225,225 + 289,575 = 514,800
