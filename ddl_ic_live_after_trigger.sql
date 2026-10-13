-- ddl_ic_live_after_trigger.sql — stamp ic_live_after_dt on every config UPDATE. Joe 1012.
--
-- Joe 1012: *"that field needs a trigger to fire =now() on update"*, corrected to *"my
-- misundestanding - to trigger. use today()"*.
--
-- TODAY() IS NOT A MySQL FUNCTION. CURDATE() is the equivalent and returns midnight today, which
-- stores into this datetime column as 'YYYY-MM-DD 00:00:00'.
--
-- WHY A DATE WORKS HERE. vw_indicator_configs_live picks, per (ic_is_pk, ic_il_pk, ic_itf_pk), the
-- row with MAX(ic_live_after_dt) among the rows whose ic_live_after_dt <= now(). The field is a
-- VERSION STAMP, not a start date. Midnight today is always <= now, so an updated row goes live
-- immediately.
--
-- THE COST OF A DATE RATHER THAN A TIMESTAMP, stated because it is a real behaviour. The view has
-- NO tiebreak on ic_pk, so if two rows for the SAME (is_pk, il_pk, itf_pk) are both stamped
-- CURDATE(), MAX() ties and the view returns BOTH. Callers that take r[0] - seed_ic_working.live()
-- does - then read an arbitrary one of the two. With NOW() that collision needs the same second;
-- with CURDATE() it needs only the same day. seed_ic_working.py inserts at
-- CURDATE()-INTERVAL 1 DAY so an insert and an update cannot tie, but two updates to one line on
-- one day can.
--
-- WHICH SCHEMA. indicator_configs is a BASE TABLE in BOTH pk_optimizer and o9_live, and each
-- schema's view reads its own copy. The ws / gcws / dws series live ONLY in pk_optimizer:
--     o9_live.indicator_configs        106 rows, 15 series, no ws8r
--     pk_optimizer.indicator_configs   222 rows, 18 series, ws8r present
-- This trigger is on pk_optimizer ONLY. o9_live is the live trading system's own config set and is
-- deliberately untouched.
--
-- WHAT IT CHANGES FOR EVERY WRITER. It fires on EVERY update of the table, so an UPDATE that sets
-- ic_live_after_dt explicitly - a backfill correcting a historical stamp - is overwritten with
-- now(). That is unconditional by Joe's instruction; the alternative is to skip when the statement
-- supplies the column, which needs his word.
--
-- There is no existing trigger on this table, so nothing is being replaced.

USE pk_optimizer;

DROP TRIGGER IF EXISTS trg_indicator_configs_live_after_bu;

CREATE TRIGGER trg_indicator_configs_live_after_bu
BEFORE UPDATE ON indicator_configs
FOR EACH ROW
SET NEW.ic_live_after_dt = CURDATE();

-- verify:
--   SELECT TRIGGER_NAME, ACTION_TIMING, EVENT_MANIPULATION, ACTION_STATEMENT
--     FROM information_schema.TRIGGERS
--    WHERE EVENT_OBJECT_SCHEMA='pk_optimizer' AND EVENT_OBJECT_TABLE='indicator_configs';
