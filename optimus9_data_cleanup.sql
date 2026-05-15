-- ─────────────────────────────────────────────────────────────────────────────
-- 260515 — optimus9 data cleanup
--
-- Two corrections to optimizer_runs accumulated during the 5s gate + p-rev
-- development cycle:
--
--   1. or_pk=1 (the original 30-day grind) predates both feature flags but
--      the schema ALTER set them to DEFAULT 1, retroactively mislabeling
--      that run as "production". Set both back to 0 to mark it as the
--      true baseline.
--
--   2. or_pks 2 and 3 were abandoned smoke attempts:
--        or_pk=2 → crashed in lookahead_resample dtype bug (no pk_signals)
--        or_pk=3 → crashed in analyser idxmax NaN bug (had signals but
--                  no useful outcomes — fix lifted them from NaN to -0.33
--                  expectancy retroactively, but the data is from a
--                  broken pipeline state)
--      Best practice: delete. They confuse cross-run analysis and serve
--      no purpose in the historical record.
--
-- Run from project root:
--   mysql -u root -p'<pw>' pk_optimizer < optimus9_data_cleanup.sql
--
-- Reversible (assuming you've taken a recent backup of optimizer_runs).
-- Read each statement before running — adjust or_pk values if your DB
-- state differs from what I'm assuming below.
-- ─────────────────────────────────────────────────────────────────────────────

USE pk_optimizer;

-- ─── 0. inspect first ──────────────────────────────────────────────────────
-- Run this to see current state and verify which or_pks need each treatment.
-- Comment out the rest of the file, run, then uncomment the operations that
-- match your reality.
--
SELECT r.or_pk, r.or_tc_pk, r.or_p_rev_enabled, r.or_pk5s_gate_enabled,
       r.or_completed_at,
       (SELECT COUNT(*) FROM pk_signals WHERE pks_or_pk = r.or_pk) AS signals,
       (SELECT COUNT(*) FROM pk_outcomes po JOIN pk_signals ps ON ps.pks_pk = po.pko_pks_pk
        WHERE ps.pks_or_pk = r.or_pk) AS outcomes
FROM optimizer_runs r
ORDER BY r.or_pk;


-- ─── 1. relabel or_pk=1 as baseline ────────────────────────────────────────
-- The 30-day grind ran before either feature existed. Mark accordingly.
-- Also stamp completed_at to a sensible past date (rough approximation —
-- adjust to actual completion if you know it).

UPDATE optimizer_runs
SET or_p_rev_enabled     = 0,
    or_pk5s_gate_enabled = 0
WHERE or_pk = 1;


-- ─── 2. delete abandoned smoke rows ────────────────────────────────────────
-- VERIFY FIRST. The exact or_pks of abandoned smokes depend on order of
-- events on your DB. Adjust the IN list to whatever the inspection query
-- above reveals as having 0 signals or 0 outcomes.

-- Deletions cascade to pk_signals via FK, and pk_outcomes via FK from
-- pk_signals (assuming both are set up ON DELETE CASCADE — verify in schema).
-- If they aren't, delete child rows first.

DELETE FROM pk_outcomes
WHERE pko_pks_pk IN (
    SELECT pks_pk FROM pk_signals WHERE pks_or_pk IN (2, 3)
);

DELETE FROM pk_signals
WHERE pks_or_pk IN (2, 3);

DELETE FROM optimizer_runs
WHERE or_pk IN (2, 3);


-- ─── 3. stamp completion on successful historical runs ────────────────────
-- or_pk=1 finished successfully (we have its analysis). Stamp it so
-- compare's warnings block doesn't flag it.
-- or_pks 4 and 5 (the successful smokes) — stamp them too if they don't
-- already have completed_at. From this round forward, ReportManager.run
-- writes the stamp automatically.

UPDATE optimizer_runs
SET or_completed_at = NOW()
WHERE or_completed_at IS NULL;


-- ─── verification ──────────────────────────────────────────────────────────
-- Re-run the inspection query from step 0 to confirm the result is sane:

SELECT r.or_pk, r.or_tc_pk, r.or_p_rev_enabled AS prev, r.or_pk5s_gate_enabled AS gate,
       DATE_FORMAT(r.or_completed_at, '%Y-%m-%d') AS completed,
       (SELECT COUNT(*) FROM pk_signals WHERE pks_or_pk = r.or_pk) AS signals
FROM optimizer_runs r
ORDER BY r.or_pk;
