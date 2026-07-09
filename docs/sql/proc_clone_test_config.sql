CALL clone_test_config(99, @new); SELECT @new AS new_tc_pk;

-- ═══════════════════════════════════════════════════════════════════════════
-- clone_test_config — clone a test_configs row + all dependent rows
-- ═══════════════════════════════════════════════════════════════════════════
--
-- Filed: r07.5 tooling (2026-05-29)
-- Intent: accelerate grind setup. Joe (or eventual UI) picks an existing
-- tc_pk, calls this proc, gets a NEW tc_pk that is a faithful clone of the
-- source — same params, same gate extensions, same vote rows. Joe then
-- tweaks the new tc_pk's rows directly (via DbForge or eventual UI) before
-- kicking off the grind.
--
-- This proc does NOT apply overrides. The intent (Joe-confirmed) is that
-- the UI workflow is "clone exactly, then tweak in the UI." JSON-overrides
-- pattern was considered and rejected as adding indirection where the UI
-- will provide a direct edit surface.
--
-- Label handling:
--   - new_label auto-suffixed with '_clone' (or '_cloneN' if cloning a
--     clone) so the source attribution survives a chain of derivations.
--   - tc_indicator_label is NOT enforced unique by schema; the suffix
--     pattern is convention, not constraint.
--
-- Source tc_pk is NOT modified. Cloning is creation of a new variant,
-- not retirement of the source.
--
-- Returns: new tc_pk via OUT parameter.
--
-- Usage:
--   CALL clone_test_config(99, @new_tc_pk);
--   SELECT @new_tc_pk;
--
-- ─────────────────────────────────────────────────────────────────────────
-- Cloning order matters (FK dependencies):
--   1. test_configs                  (parent)
--   2. test_param_ranges             (child of test_configs)
--   3. test_config_extensions        (child of test_configs)
--   4. test_config_ext_votes         (child of test_config_extensions)
--
-- Step 4 is the tricky one: each cloned tce row has its own NEW auto-
-- increment tce_pk, but the source's tcev rows reference the SOURCE's
-- tce_pks. We need an old→new tce_pk mapping to land tcev rows correctly.
--
-- Approach: temp table built during step 3 captures (old_tce_pk, new_tce_pk)
-- pairs, then step 4 INSERT...SELECT joins through the mapping.
-- ═══════════════════════════════════════════════════════════════════════════

DROP PROCEDURE IF EXISTS clone_test_config;

DELIMITER //

CREATE PROCEDURE clone_test_config(
    IN  src_tc_pk INT UNSIGNED,
    OUT new_tc_pk INT UNSIGNED
)
BEGIN
    DECLARE src_label       VARCHAR(255);
    DECLARE new_label       VARCHAR(255);
    DECLARE clone_suffix    VARCHAR(20);
    DECLARE clone_counter   INT DEFAULT 1;
    DECLARE existing_count  INT DEFAULT 0;

    -- ──────────────────────────────────────────────────────────────────────
    -- 0. Validate source exists.
    -- ──────────────────────────────────────────────────────────────────────
    SELECT tc_indicator_label
      INTO src_label
      FROM test_configs
     WHERE tc_pk = src_tc_pk;

    IF src_label IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'clone_test_config: source tc_pk does not exist';
    END IF;

    -- ──────────────────────────────────────────────────────────────────────
    -- 1. Build new label with _clone[N] suffix.
    --    - 'foo' becomes 'foo_clone'
    --    - 'foo_clone' becomes 'foo_clone2'
    --    - 'foo_clone3' becomes 'foo_clone4'
    --    - Bumps until no existing label collides.
    -- ──────────────────────────────────────────────────────────────────────
    IF src_label REGEXP '_clone[0-9]*$' THEN
        -- Strip existing _clone[N] suffix to find the base
        SET clone_suffix = SUBSTRING_INDEX(src_label, '_clone', -1);
        IF clone_suffix = '' THEN
            SET clone_counter = 2;
        ELSE
            SET clone_counter = CAST(clone_suffix AS UNSIGNED) + 1;
        END IF;
        SET new_label = CONCAT(
            SUBSTRING(src_label, 1, LENGTH(src_label) - LENGTH(clone_suffix) - 6),
            '_clone', clone_counter
        );
    ELSE
        SET new_label = CONCAT(src_label, '_clone');
    END IF;

    -- Bump counter if the candidate already exists.
    SELECT COUNT(*) INTO existing_count
      FROM test_configs
     WHERE tc_indicator_label = new_label;

    WHILE existing_count > 0 DO
        SET clone_counter = clone_counter + 1;
        IF src_label REGEXP '_clone[0-9]*$' THEN
            SET new_label = CONCAT(
                SUBSTRING(src_label, 1,
                    LENGTH(src_label) - LENGTH(SUBSTRING_INDEX(src_label, '_clone', -1)) - 6),
                '_clone', clone_counter
            );
        ELSE
            SET new_label = CONCAT(src_label, '_clone', clone_counter);
        END IF;
        SELECT COUNT(*) INTO existing_count
          FROM test_configs
         WHERE tc_indicator_label = new_label;
    END WHILE;

    -- ──────────────────────────────────────────────────────────────────────
    -- 2. Clone test_configs row.
    -- ──────────────────────────────────────────────────────────────────────
    INSERT INTO test_configs (
        tc_tp_pk, tc_ic_pk, tc_indicator_label,
        tc_dema_len, tc_dema_src,
        tc_stop_pct, tc_dynamic_stoploss, tc_stop_buffer,
        tc_profit_zone, tc_drag_pct, tc_max_bars
    )
    SELECT
        tc_tp_pk, tc_ic_pk, new_label,
        tc_dema_len, tc_dema_src,
        tc_stop_pct, tc_dynamic_stoploss, tc_stop_buffer,
        tc_profit_zone, tc_drag_pct, tc_max_bars
      FROM test_configs
     WHERE tc_pk = src_tc_pk;

    SET new_tc_pk = LAST_INSERT_ID();

    -- ──────────────────────────────────────────────────────────────────────
    -- 3. Clone test_param_ranges rows.
    -- ──────────────────────────────────────────────────────────────────────
    INSERT INTO test_param_ranges (
        tpr_tc_pk, tpr_param_name, tpr_param_type,
        tpr_current_value, tpr_step, tpr_range, tpr_enum_values
    )
    SELECT
        new_tc_pk, tpr_param_name, tpr_param_type,
        tpr_current_value, tpr_step, tpr_range, tpr_enum_values
      FROM test_param_ranges
     WHERE tpr_tc_pk = src_tc_pk;

    -- ──────────────────────────────────────────────────────────────────────
    -- 4. Clone test_config_extensions, capturing old→new tce_pk mapping.
    -- ──────────────────────────────────────────────────────────────────────
    DROP TEMPORARY TABLE IF EXISTS _tce_pk_map;
    CREATE TEMPORARY TABLE _tce_pk_map (
        old_tce_pk INT UNSIGNED NOT NULL,
        new_tce_pk INT UNSIGNED NOT NULL,
        PRIMARY KEY (old_tce_pk)
    ) ENGINE = MEMORY;

    -- Insert clones one at a time so LAST_INSERT_ID() captures each new PK.
    -- A single INSERT...SELECT would only give us the first inserted ID.
    BEGIN
        DECLARE done INT DEFAULT 0;
        DECLARE cur_tce_pk INT UNSIGNED;
        DECLARE cur_type ENUM('gate', 'pk_5s');
        DECLARE cur_ic_pk INT UNSIGNED;
        DECLARE cur_sort_order INT;
        DECLARE cur_is_active TINYINT(1);
        DECLARE cur_params JSON;

        DECLARE tce_cursor CURSOR FOR
            SELECT tce_pk, tce_type, tce_ic_pk, tce_sort_order,
                   tce_is_active, tce_params
              FROM test_config_extensions
             WHERE tce_tc_pk = src_tc_pk
             ORDER BY tce_pk;

        DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

        OPEN tce_cursor;
        clone_tce: LOOP
            FETCH tce_cursor INTO cur_tce_pk, cur_type, cur_ic_pk,
                                   cur_sort_order, cur_is_active, cur_params;
            IF done = 1 THEN
                LEAVE clone_tce;
            END IF;

            INSERT INTO test_config_extensions (
                tce_tc_pk, tce_type, tce_ic_pk,
                tce_sort_order, tce_is_active, tce_params
            ) VALUES (
                new_tc_pk, cur_type, cur_ic_pk,
                cur_sort_order, cur_is_active, cur_params
            );

            INSERT INTO _tce_pk_map (old_tce_pk, new_tce_pk)
            VALUES (cur_tce_pk, LAST_INSERT_ID());
        END LOOP;
        CLOSE tce_cursor;
    END;

    -- ──────────────────────────────────────────────────────────────────────
    -- 5. Clone test_config_ext_votes, remapped to new tce_pks.
    -- ──────────────────────────────────────────────────────────────────────
    INSERT INTO test_config_ext_votes (
        tcev_tce_pk, tcev_ic_pk,
        tcev_weight_close, tcev_weight_wide, tcev_is_active,
        tcev_trigger_mode, tcev_roc_threshold
    )
    SELECT
        m.new_tce_pk, tcev.tcev_ic_pk,
        tcev.tcev_weight_close, tcev.tcev_weight_wide, tcev.tcev_is_active,
        tcev.tcev_trigger_mode, tcev.tcev_roc_threshold
      FROM test_config_ext_votes tcev
      JOIN _tce_pk_map           m   ON m.old_tce_pk = tcev.tcev_tce_pk
     WHERE tcev.tcev_tce_pk IN (
        SELECT tce_pk FROM test_config_extensions WHERE tce_tc_pk = src_tc_pk
     );

    DROP TEMPORARY TABLE IF EXISTS _tce_pk_map;

    -- new_tc_pk is the OUT parameter — already set above.
END //

DELIMITER ;

-- ═══════════════════════════════════════════════════════════════════════════
-- Verification queries (run after CALL clone_test_config(...))
-- ═══════════════════════════════════════════════════════════════════════════
--
-- After:    CALL clone_test_config(99, @new_tc_pk);
--           SELECT @new_tc_pk;
--
-- Verify the clone is faithful:
--
-- 1. New row exists with expected label:
--    SELECT tc_pk, tc_indicator_label FROM test_configs WHERE tc_pk = @new_tc_pk;
--
-- 2. Param row counts match:
--    SELECT
--        (SELECT COUNT(*) FROM test_param_ranges WHERE tpr_tc_pk = 99) AS src_params,
--        (SELECT COUNT(*) FROM test_param_ranges WHERE tpr_tc_pk = @new_tc_pk) AS new_params;
--
-- 3. Extension row counts match:
--    SELECT
--        (SELECT COUNT(*) FROM test_config_extensions WHERE tce_tc_pk = 99)         AS src_tce,
--        (SELECT COUNT(*) FROM test_config_extensions WHERE tce_tc_pk = @new_tc_pk) AS new_tce;
--
-- 4. Vote row counts match (via tce children):
--    SELECT
--        (SELECT COUNT(*) FROM test_config_ext_votes tcev
--           JOIN test_config_extensions tce ON tce.tce_pk = tcev.tcev_tce_pk
--          WHERE tce.tce_tc_pk = 99) AS src_votes,
--        (SELECT COUNT(*) FROM test_config_ext_votes tcev
--           JOIN test_config_extensions tce ON tce.tce_pk = tcev.tcev_tce_pk
--          WHERE tce.tce_tc_pk = @new_tc_pk) AS new_votes;
--
-- 5. Spot-check that vote weights survived:
--    SELECT tcev.* FROM test_config_ext_votes tcev
--      JOIN test_config_extensions tce ON tce.tce_pk = tcev.tcev_tce_pk
--     WHERE tce.tce_tc_pk = @new_tc_pk
--     ORDER BY tcev.tcev_pk;
-- ═══════════════════════════════════════════════════════════════════════════
