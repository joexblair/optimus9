-- r05_260520 pk_signals composite index for AM v2 Stage 2 lookups
-- ============================================================================
-- AM v2's Stage 2 ranker pulls per-combo signal sequences (100 combos per
-- or_pk) to walk the equity curve and compute gross_banked, max_drawdown,
-- Sharpe, Sortino, profit factor. Each lookup uses ~10 equality predicates
-- across the param columns.
--
-- Before this index:
--   - Only idx_pks_or existed (single column on pks_or_pk)
--   - EXPLAIN: rows ≈ 18M scanned, ~60s per query
--   - 100 combos × 60s = 100 minutes per or_pk Stage 2
--
-- After this index:
--   - EXPLAIN: rows ≈ 50-200 per combo, ~50-100ms per query
--   - 100 combos × 100ms = ~10s per or_pk Stage 2
--   - Speedup ≈ 600x for the Stage 2 portion
--
-- The column order matches Stage 2's WHERE-clause selectivity. or_pk first
-- (always present), then the line params (high selectivity), then pool
-- params, then K-line params last (most rows are NULL for BB grinds; less
-- discriminating overall but useful for K-line grinds).
--
-- Storage cost: ~5-10% of pk_signals size. Insert overhead: ~5-15% slower
-- during grinds. Acceptable trade for the analyze speedup.
-- ============================================================================

ALTER TABLE pk_signals
  ADD INDEX idx_pks_combo_lookup (
    pks_or_pk,
    pks_len,
    pks_mult,
    pks_src(8),           -- prefix index for varchar src
    pks_pool_c,
    pks_pool_w,
    pks_pool_range,
    pks_slope_floor,
    pks_multiplier,
    pks_len_rsi,
    pks_len_stoch
  );

-- Verify with:
--   SHOW INDEX FROM pk_signals WHERE Key_name = 'idx_pks_combo_lookup';
--
-- Confirm EXPLAIN uses the new index for a per-combo query:
--   EXPLAIN SELECT s.pks_timestamp, s.pks_dir,
--                  o.pko_max_profit_pct, o.pko_bars_to_stop
--   FROM pk_signals s
--   LEFT JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
--   WHERE s.pks_or_pk = <N>
--     AND s.pks_len = <X> AND s.pks_mult = <Y> AND s.pks_src = '<Z>'
--     AND s.pks_pool_c = <A> AND s.pks_pool_w = <B>
--     AND s.pks_pool_range = <C> AND s.pks_slope_floor = <D>
--     AND s.pks_multiplier = <E>
--     AND s.pks_len_rsi IS NULL AND s.pks_len_stoch IS NULL;
--
-- Expected: key=idx_pks_combo_lookup, rows ≈ 50-200, Extra='Using index condition'

--result:
--id,select_type,table,partitions,type,possible_keys,key,key_len,ref,rows,filtered,Extra
--1,SIMPLE,s,null,ref,"idx_pks_or,idx_pks_combo_lookup",idx_pks_combo_lookup,70,"const,const,const,const,const,const,const,const,const,const,const",48,100.0,Using index condition; Using where
--1,SIMPLE,o,null,eq_ref,pko_pks_pk,pko_pks_pk,4,pk_optimizer.s.pks_pk,1,100.0,null
