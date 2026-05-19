-- r05 slope_floor diagnostic
-- ============================================================================
-- Joe's TV experiments suggest values like 11/33/15 reduce trade count and
-- improve PnL — but the r05 grinds at 3.0-7.0 showed FLAT sensitivity
-- (spread < 0.01%). Either the active region is outside 3-7 entirely, or
-- the param does something nonlinear we haven't grasped.
--
-- This sweep: 0 → 50 step 2.5 (21 values), everything else locked at
-- or_pk=7 centroid. Goal: find the active region where trade count starts
-- dropping. From there we tighten ranges for r06.
--
-- All other params fixed at the or_pk=7 centroid:
--   len=14, mult=0.74, src=close, pool_c=34, pool_w=56, pool_range=3,
--   multiplier=1, weights (5, 2)
--
-- Combos: 1 × 1 × 1 × 1 × 1 × 1 × 21 × 1 = 21 → runs in ~30 min.
-- ============================================================================

START TRANSACTION;

-- Clone tc_pk=7 as a baseline for the slope sweep
INSERT INTO test_configs (
    tc_tp_pk, tc_ic_pk, tc_indicator_label,
    tc_dema_len, tc_dema_src,
    tc_stop_pct, tc_dynamic_stoploss, tc_stop_buffer,
    tc_profit_zone, tc_drag_pct, tc_max_bars
)
SELECT tc_tp_pk, tc_ic_pk, 'gcs5m_slope_diag',
       tc_dema_len, tc_dema_src,
       0.71, 0, tc_stop_buffer,
       tc_profit_zone, tc_drag_pct, tc_max_bars
FROM test_configs WHERE tc_pk = 7;

SET @sf_tc := LAST_INSERT_ID();

-- All params locked at or_pk=7 centroid except slope_floor (sweep 0→50)
INSERT INTO test_param_ranges (
    tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
    tpr_enum_values, tpr_param_type
) VALUES
    (@sf_tc, 'len',                14.0, 0.0,  0.0,  NULL,    'int'),
    (@sf_tc, 'mult',               0.74, 0.0,  0.0,  NULL,    'float'),
    (@sf_tc, 'src',                NULL, NULL, NULL, 'close', 'enum'),
    (@sf_tc, 'pool_c',             34.0, 0.0,  0.0,  NULL,    'int'),
    (@sf_tc, 'pool_w',             56.0, 0.0,  0.0,  NULL,    'int'),
    (@sf_tc, 'pool_range',         3.0,  0.0,  0.0,  NULL,    'int'),
    (@sf_tc, 'slope_floor',        25.0, 2.5,  50.0, NULL,    'float'),
    (@sf_tc, 'multiplier',         1.0,  0.0,  0.0,  NULL,    'int'),
    (@sf_tc, 'tcev_weight_close',  5.0,  0.0,  0.0,  NULL,    'int'),
    (@sf_tc, 'tcev_weight_wide',   2.0,  0.0,  0.0,  NULL,    'int');

COMMIT;

-- Report new tc_pk and expected combo count
SELECT @sf_tc AS new_tc_pk,
       (SELECT COUNT(*) FROM test_param_ranges WHERE tpr_tc_pk = @sf_tc) AS param_count,
       21 AS expected_combos;

-- After running the grind: in the sensitivity output, look at signal count
-- per slope_floor value. Active region = where signal count starts collapsing.
-- Expected pattern if Joe's TV findings hold:
--   slope_floor 0-10:  high signal count, low avg PnL (many noisy fires)
--   slope_floor 10-30: signal count drops, PnL improves (filter working)
--   slope_floor 30+:   signal count very low, may improve PnL but few trades
