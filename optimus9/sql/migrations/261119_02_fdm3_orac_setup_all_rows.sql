-- Filed: 2026-11-19
--
-- Intent: widen fdm3_orac_setup to EVERY oracle row of the day, and add the counts Joe named.
--
--   HIS 1119, on the population: *"show all of the raw rows, ie the pre 20% cull"*, and he ruled it
--   as every row of the day with no gate. The setup hunt's own flag becomes a column, `is_setup`,
--   so he filters in Excel instead of the table filtering for him. His 1118 reason, verbatim:
--   *"this report's purpose is to find the lowest common demoninator. if gates are applied, we
--   don't have a fighting chance"*.
--
--   HIS 1119, on the shape: *"collate them instead of separating them into 2 partitions of the
--   table - ie print the 2-row-count values for a timestamp, and the following table row will print
--   the 3-row-count for the same timestamp. this will need a sequence column"*. So one timestamp
--   owns two consecutive table rows, the 2-row window then the 3-row window, and `seq` numbers them
--   in that print order.
--
--   HIS 1119, the new counts: *"add columns for the count of lowband AWs and highband AWs"* and
--   *"add TOexf counts for lband, hband, 16-22, 23-30"*.
--
--   THE SPANS. low_aw, high_aw, low_toexf and high_toexf are DISTINCT TIMEFRAMES reading that tag
--   anywhere across the window - the same span as low_aw_flip, at his ruling. toexf_16_22 and
--   toexf_23_30 are the HIGHEST per-row count seen in the window, because the oracle serves those
--   two bands as a count of lines and not as a per-line mask, so a distinct-timeframe read is not
--   available for them. That difference is on each column's comment.
--
--   THE KEY still carries the knobs, for the reason the first migration gives.
--
-- Usage: mysql pk_optimizer < 261119_02_fdm3_orac_setup_all_rows.sql
--   then: python3 docs/fdm3/oracle_rows.py setups <day> <out.txt> --db
--
-- Dependencies: 261119_01_fdm3_orac_setups.sql, and the fdm3-oracle serving the 30 second page.

ALTER TABLE fdm3_orac_setup
  ADD COLUMN seq            INT      NOT NULL DEFAULT 0
    COMMENT 'print order: 1-based, ascending by setup_row then win_rows, so one timestamp owns two consecutive rows'
    AFTER knobs,
  ADD COLUMN is_setup       TINYINT  NOT NULL DEFAULT 0
    COMMENT 'HIS 1118 setup hunt flag: 1 where the window carries >=ORAC_6X_HITS lowband x-crosses AND >=1 lowband AW flip'
    AFTER side,
  ADD COLUMN low_aw         TINYINT  NOT NULL DEFAULT 0
    COMMENT 'distinct lowband TFs reading AW, either AW(inf) or AW(exf), anywhere across the window',
  ADD COLUMN high_aw        TINYINT  NOT NULL DEFAULT 0
    COMMENT 'distinct highband TFs reading AW anywhere across the window',
  ADD COLUMN low_toexf      TINYINT  NOT NULL DEFAULT 0
    COMMENT 'distinct lowband TFs reading TO(exf) anywhere across the window',
  ADD COLUMN high_toexf     TINYINT  NOT NULL DEFAULT 0
    COMMENT 'distinct highband TFs reading TO(exf) anywhere across the window',
  ADD COLUMN toexf_16_22    TINYINT  NOT NULL DEFAULT 0
    COMMENT 'ws16-ws22: the highest per-row count of lines reading TO(exf) seen in the window. A count, not distinct TFs - the oracle serves this band as a count',
  ADD COLUMN toexf_23_30    TINYINT  NOT NULL DEFAULT 0
    COMMENT 'ws23-ws30: the same read on that band',
  ADD KEY k_seq (day, knobs, seq),
  ADD KEY k_setup (day, win_rows, is_setup);
