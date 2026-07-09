CALL delete_test_config(101);
-- ═══════════════════════════════════════════════════════════════════════════
-- delete_test_config — safe delete of a tc_pk and all dependent rows
-- ═══════════════════════════════════════════════════════════════════════════
--
-- Filed: r07.5 tooling (2026-05-29)
-- Enhanced: 2026-05-29 — added confirmation_token, fixed FK-correct
--   deletion order (cascade is NOT enabled on the relevant FKs).
--
-- Intent: clean up unused clones produced by clone_test_config, and
-- (with explicit override) delete tc_pks that have grind runs against
-- them. Both paths use FK-correct deletion order; cascade was originally
-- assumed but is not present on the test_configs / test_config_extensions
-- / test_param_ranges parent FKs.
--
-- ─────────────────────────────────────────────────────────────────────────
-- Confirmation token (β workflow, intentional friction):
--
-- The second parameter is required, even for the safe path. It exists
-- to keep the safety surface visible at every callsite. Passing '' is
-- the conscious "I'm using the safe path" act; passing 'force' is the
-- conscious "I'm overriding the safety check" act. Neither is implicit.
--
-- Token values:
--   ''       — safe path: refuse if optimizer_runs exist
--   'force'  — override: also delete optimizer_runs + their pk_signals +
--              pk_outcomes. Case-sensitive (lowercase only).
--   anything else — error (caller mistyped or passed wrong intent)
--
-- ─────────────────────────────────────────────────────────────────────────
-- Deletion order (force path, bottom-up to satisfy each FK):
--   1. pk_outcomes         (child of pk_signals)
--   2. pk_signals          (child of optimizer_runs)
--   3. optimizer_runs      (child of test_configs)
--   4. test_config_ext_votes (child of test_config_extensions)
--   5. test_config_extensions (child of test_configs)
--   6. test_param_ranges   (child of test_configs)
--   7. test_configs        (the target)
--
-- Safe path skips steps 1-3 (refusing if any rows would be deleted there)
-- and proceeds to 4-7.
--
-- Usage:
--   CALL delete_test_config(101, '');         -- safe
--   CALL delete_test_config(101, 'force');    -- override
-- ═══════════════════════════════════════════════════════════════════════════

DROP PROCEDURE IF EXISTS delete_test_config;

DELIMITER //

CREATE PROCEDURE delete_test_config(
    IN target_tc_pk          INT UNSIGNED,
    IN confirmation_token    VARCHAR(20)
)
BEGIN
    DECLARE tc_exists        INT DEFAULT 0;
    DECLARE tc_label         VARCHAR(255);
    DECLARE run_count        INT DEFAULT 0;
    DECLARE force_mode       TINYINT(1) DEFAULT 0;

    DECLARE runs_deleted     INT DEFAULT 0;
    DECLARE signals_deleted  INT DEFAULT 0;
    DECLARE outcomes_deleted INT DEFAULT 0;

    -- ──────────────────────────────────────────────────────────────────────
    -- 0. Validate token. Reject anything that's not '' or 'force' to catch
    --    typos (e.g. 'Force', 'FORCE', 'yes', 'true').
    -- ──────────────────────────────────────────────────────────────────────
    IF confirmation_token IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'delete_test_config: confirmation_token must be supplied (use empty string for safe delete, or "force" to override)';
    END IF;

    IF confirmation_token NOT IN ('', 'force') THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'delete_test_config: confirmation_token must be "" or "force" (case-sensitive, lowercase)';
    END IF;

    SET force_mode = IF(confirmation_token = 'force', 1, 0);

    -- ──────────────────────────────────────────────────────────────────────
    -- 1. Validate target exists.
    -- ──────────────────────────────────────────────────────────────────────
    SELECT COUNT(*), MAX(tc_indicator_label)
      INTO tc_exists, tc_label
      FROM test_configs
     WHERE tc_pk = target_tc_pk;

    IF tc_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'delete_test_config: tc_pk does not exist';
    END IF;

    -- ──────────────────────────────────────────────────────────────────────
    -- 2. Safe-path check: refuse if any optimizer_runs reference this tc_pk
    --    and force_mode is off.
    -- ──────────────────────────────────────────────────────────────────────
    SELECT COUNT(*) INTO run_count
      FROM optimizer_runs
     WHERE or_tc_pk = target_tc_pk;

    IF run_count > 0 AND force_mode = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'delete_test_config: tc_pk has optimizer_runs attached. Pass "force" to delete them too, or clean up runs first.';
    END IF;

    -- ──────────────────────────────────────────────────────────────────────
    -- 3. Force path: cascade delete runs + their signals + outcomes.
    --    Bottom-up by FK: outcomes → signals → runs.
    -- ──────────────────────────────────────────────────────────────────────
    IF force_mode = 1 AND run_count > 0 THEN
        -- 3a. pk_outcomes (child of pk_signals)
        DELETE pko FROM pk_outcomes pko
          JOIN pk_signals pks ON pks.pks_pk = pko.pko_pks_pk
          JOIN optimizer_runs orr ON orr.or_pk = pks.pks_or_pk
         WHERE orr.or_tc_pk = target_tc_pk;
        SET outcomes_deleted = ROW_COUNT();

        -- 3b. pk_signals (child of optimizer_runs)
        DELETE pks FROM pk_signals pks
          JOIN optimizer_runs orr ON orr.or_pk = pks.pks_or_pk
         WHERE orr.or_tc_pk = target_tc_pk;
        SET signals_deleted = ROW_COUNT();

        -- 3c. optimizer_runs (child of test_configs)
        DELETE FROM optimizer_runs WHERE or_tc_pk = target_tc_pk;
        SET runs_deleted = ROW_COUNT();
    END IF;

    -- ──────────────────────────────────────────────────────────────────────
    -- 4. Test-config dependents: votes → extensions → params.
    --    Bottom-up by FK so each parent is empty when its DELETE runs.
    -- ──────────────────────────────────────────────────────────────────────
    -- 4a. test_config_ext_votes (child of test_config_extensions)
    DELETE FROM test_config_ext_votes
     WHERE tcev_tce_pk IN (
        SELECT tce_pk FROM test_config_extensions WHERE tce_tc_pk = target_tc_pk
     );

    -- 4b. test_config_extensions (child of test_configs)
    DELETE FROM test_config_extensions WHERE tce_tc_pk = target_tc_pk;

    -- 4c. test_param_ranges (child of test_configs)
    DELETE FROM test_param_ranges WHERE tpr_tc_pk = target_tc_pk;

    -- ──────────────────────────────────────────────────────────────────────
    -- 5. Finally, the test_configs row.
    -- ──────────────────────────────────────────────────────────────────────
    DELETE FROM test_configs WHERE tc_pk = target_tc_pk;

    -- ──────────────────────────────────────────────────────────────────────
    -- 6. Confirmation result set.
    -- ──────────────────────────────────────────────────────────────────────
    SELECT
        target_tc_pk     AS deleted_tc_pk,
        tc_label         AS deleted_label,
        IF(force_mode = 1, 'yes', 'no') AS force_used,
        runs_deleted     AS runs_deleted,
        signals_deleted  AS signals_deleted,
        outcomes_deleted AS outcomes_deleted,
        'OK'             AS status;
END //

DELIMITER ;
