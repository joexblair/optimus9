-- ═══════════════════════════════════════════════════════════════════════════
-- inspect_test_config — show the complete picture of a tc_pk
-- ═══════════════════════════════════════════════════════════════════════════
--
-- Filed: r07.5 tooling (2026-05-29)
-- Intent: one CALL shows everything that defines a tc_pk's grind setup.
-- Used to verify a clone landed correctly, audit an existing config before
-- a grind, or compare two tc_pks side-by-side by running twice.
--
-- Returns FOUR result sets in this order:
--   1. tc header  — the test_configs row itself
--   2. params     — test_param_ranges rows
--   3. extensions — test_config_extensions rows
--   4. votes      — test_config_ext_votes rows (via extensions)
--
-- Usage:
--   CALL inspect_test_config(99);
--
-- DbForge / mysql CLI / Python clients all handle multi-result-set output;
-- iterate through them in order.
-- ═══════════════════════════════════════════════════════════════════════════

DROP PROCEDURE IF EXISTS inspect_test_config;

DELIMITER //

CREATE PROCEDURE inspect_test_config(
    IN target_tc_pk INT UNSIGNED
)
BEGIN
    DECLARE tc_exists INT DEFAULT 0;

    -- ──────────────────────────────────────────────────────────────────────
    -- 0. Validate target exists. Empty result sets are fine if not, but
    --    a clean error helps the caller distinguish "no such tc" from
    --    "tc exists but is empty."
    -- ──────────────────────────────────────────────────────────────────────
    SELECT COUNT(*) INTO tc_exists
      FROM test_configs
     WHERE tc_pk = target_tc_pk;

    IF tc_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'inspect_test_config: tc_pk does not exist';
    END IF;

    -- ──────────────────────────────────────────────────────────────────────
    -- Result set 1: tc header.
    -- ──────────────────────────────────────────────────────────────────────
    SELECT
        tc_pk,
        tc_indicator_label,
        tc_tp_pk,
        tc_ic_pk,
        tc_dema_len,
        tc_dema_src,
        tc_stop_pct,
        tc_dynamic_stoploss,
        tc_stop_buffer,
        tc_profit_zone,
        tc_drag_pct,
        tc_max_bars
      FROM test_configs
     WHERE tc_pk = target_tc_pk;

    -- ──────────────────────────────────────────────────────────────────────
    -- Result set 2: param ranges (the grind dimensions).
    -- ──────────────────────────────────────────────────────────────────────
    SELECT
        tpr_pk,
        tpr_param_name,
        tpr_param_type,
        tpr_current_value,
        tpr_step,
        tpr_range,
        tpr_enum_values
      FROM test_param_ranges
     WHERE tpr_tc_pk = target_tc_pk
     ORDER BY tpr_param_name;

    -- ──────────────────────────────────────────────────────────────────────
    -- Result set 3: extensions (gates + pk_5s).
    -- ──────────────────────────────────────────────────────────────────────
    SELECT
        tce_pk,
        tce_type,
        tce_ic_pk,
        tce_sort_order,
        tce_is_active,
        tce_params
      FROM test_config_extensions
     WHERE tce_tc_pk = target_tc_pk
     ORDER BY tce_sort_order, tce_pk;

    -- ──────────────────────────────────────────────────────────────────────
    -- Result set 4: vote lines (via extensions).
    -- ──────────────────────────────────────────────────────────────────────
    SELECT
        tcev.tcev_pk,
        tcev.tcev_tce_pk,
        tce.tce_type AS parent_tce_type,
        tcev.tcev_ic_pk,
        tcev.tcev_weight_close,
        tcev.tcev_weight_wide,
        tcev.tcev_is_active,
        tcev.tcev_trigger_mode,
        tcev.tcev_roc_threshold
      FROM test_config_ext_votes tcev
      JOIN test_config_extensions tce ON tce.tce_pk = tcev.tcev_tce_pk
     WHERE tce.tce_tc_pk = target_tc_pk
     ORDER BY tcev.tcev_tce_pk, tcev.tcev_pk;
END //

DELIMITER ;
