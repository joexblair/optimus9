-- r05 slope_floor extended diagnostic — find the ceiling
-- ============================================================================
-- or_pk=13 (15-day) showed slope_floor climbing monotonically to +0.6435% at
-- the 50.0 boundary — no peak found within 0-50 range. This sweep extends
-- 50→150 step 5 (21 values) to locate where the curve actually peaks or
-- where signal counts collapse to the point of statistical noise.
--
-- All other params locked at or_pk=13 centroid:
--   len=14, mult=0.74, src=close, pool_c=34, pool_w=56, pool_range=3,
--   multiplier=1, weights (5, 2), stop=0.71
--
-- NOTE: Run on a 15+ day window. The 3-day version already produced only
-- 57 signals at slope_floor=50; pushing to 150 on 3-day will be unusable
-- (single-digit signal counts). 15-day gives ~1610 signals at slope=50,
-- so we should still have hundreds at slope=150 if the curve hasn't already
-- collapsed.
--
-- Combos: 21. Runs in ~30s.
-- ============================================================================

START TRANSACTION;

-- Clone tc_pk=9 (the existing slope diag) for a new sweep range
INSERT INTO test_configs (
    tc_tp_pk, tc_ic_pk, tc_indicator_label,
    tc_dema_len, tc_dema_src,
    tc_stop_pct, tc_dynamic_stoploss, tc_stop_buffer,
    tc_profit_zone, tc_drag_pct, tc_max_bars
)
SELECT tc_tp_pk, tc_ic_pk, 'gcs5m_slope_diag_hi',
       tc_dema_len, tc_dema_src,
       0.71, 0, tc_stop_buffer,
       tc_profit_zone, tc_drag_pct, tc_max_bars
FROM test_configs WHERE tc_pk = 9;

SET @sf_tc := LAST_INSERT_ID();

-- All params locked except slope_floor (sweep 50→150 step 5)
-- curr=100, step=5, range=100 → [50, 55, 60, ..., 150] = 21 values
INSERT INTO test_param_ranges (
    tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
    tpr_enum_values, tpr_param_type
) VALUES
    (@sf_tc, 'len',                14.0,  0.0,  0.0,   NULL,    'int'),
    (@sf_tc, 'mult',               0.74,  0.0,  0.0,   NULL,    'float'),
    (@sf_tc, 'src',                NULL,  NULL, NULL,  'close', 'enum'),
    (@sf_tc, 'pool_c',             34.0,  0.0,  0.0,   NULL,    'int'),
    (@sf_tc, 'pool_w',             56.0,  0.0,  0.0,   NULL,    'int'),
    (@sf_tc, 'pool_range',         3.0,   0.0,  0.0,   NULL,    'int'),
    (@sf_tc, 'slope_floor',        100.0, 5.0,  100.0, NULL,    'float'),
    (@sf_tc, 'multiplier',         1.0,   0.0,  0.0,   NULL,    'int'),
    (@sf_tc, 'tcev_weight_close',  5.0,   0.0,  0.0,   NULL,    'int'),
    (@sf_tc, 'tcev_weight_wide',   2.0,   0.0,  0.0,   NULL,    'int');

COMMIT;

-- Report the new tc_pk
SELECT @sf_tc AS new_tc_pk,
       (SELECT COUNT(*) FROM test_param_ranges WHERE tpr_tc_pk = @sf_tc) AS param_count,
       21 AS expected_combos;

-- After running on 15-day window: look at signal counts. If the lowest still
-- has 200+ signals, we have a real ceiling to find. If counts collapse below
-- 100 quickly, the ceiling is between 50-100 and we tighten the next sweep.
