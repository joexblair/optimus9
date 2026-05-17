-- ═══════════════════════════════════════════════════════════════════════════
-- r04_260517 seed addendum: xlsx weights as fixed combo dimensions
-- ═══════════════════════════════════════════════════════════════════════════
--
-- Adds tcev_weight_close + tcev_weight_wide to test_param_ranges for each
-- r04 5s singular tc. step=0 + range=0 → ParameterGridBuilder produces a
-- single value (the current value), so weights are fixed per tc.
--
-- Values come from xlsx (consolidated_indicators_260514.xlsx):
--   gcs5m  weight_close=5  weight_wide=2
--   gcb5M  weight_close=1  weight_wide=2
--   gca5m  weight_close=0  weight_wide=6  (wide-pool-only line, by design)
--
-- These flow into each combo dict, then into OptimizerRunner._build_target_vote
-- when constructing single-line vote_overrides for Pk5sGateComputer. Weights
-- are NOT swept in r04 — they characterize how the line is used in the vote
-- machine, not what the line "is." A future round could sweep them to ask
-- "what weight balance would maximize this line's value to the vote machine."
--
-- Apply AFTER r04_260517_seed_5s_tcs.sql.
-- ═══════════════════════════════════════════════════════════════════════════

START TRANSACTION;

-- ── gcs5m (tc_pk=2) ──
INSERT INTO test_param_ranges
  (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
   tpr_enum_values, tpr_param_type)
SELECT tc_pk, 'tcev_weight_close', 5, 0, 0, NULL, 'int'
FROM test_configs WHERE tc_indicator_label = 'gcs5m';

INSERT INTO test_param_ranges
  (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
   tpr_enum_values, tpr_param_type)
SELECT tc_pk, 'tcev_weight_wide', 2, 0, 0, NULL, 'int'
FROM test_configs WHERE tc_indicator_label = 'gcs5m';

-- ── gcb5M ──
INSERT INTO test_param_ranges
  (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
   tpr_enum_values, tpr_param_type)
SELECT tc_pk, 'tcev_weight_close', 1, 0, 0, NULL, 'int'
FROM test_configs WHERE tc_indicator_label = 'gcb5M';

INSERT INTO test_param_ranges
  (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
   tpr_enum_values, tpr_param_type)
SELECT tc_pk, 'tcev_weight_wide', 2, 0, 0, NULL, 'int'
FROM test_configs WHERE tc_indicator_label = 'gcb5M';

-- ── gca5m ──
INSERT INTO test_param_ranges
  (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
   tpr_enum_values, tpr_param_type)
SELECT tc_pk, 'tcev_weight_close', 0, 0, 0, NULL, 'int'
FROM test_configs WHERE tc_indicator_label = 'gca5m';

INSERT INTO test_param_ranges
  (tpr_tc_pk, tpr_param_name, tpr_current_value, tpr_step, tpr_range,
   tpr_enum_values, tpr_param_type)
SELECT tc_pk, 'tcev_weight_wide', 6, 0, 0, NULL, 'int'
FROM test_configs WHERE tc_indicator_label = 'gca5m';

COMMIT;

-- Verify
SELECT tc.tc_indicator_label, tpr.tpr_param_name, tpr.tpr_current_value
FROM test_param_ranges tpr
JOIN test_configs tc ON tc.tc_pk = tpr.tpr_tc_pk
WHERE tpr.tpr_param_name IN ('tcev_weight_close', 'tcev_weight_wide')
  AND tc.tc_indicator_label IN ('gcs5m', 'gcb5M', 'gca5m')
ORDER BY tc.tc_indicator_label, tpr.tpr_param_name;
