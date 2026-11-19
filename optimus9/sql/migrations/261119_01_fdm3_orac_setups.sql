-- Filed: 2026-11-19
--
-- Intent: hold the fdm3 SETUP HUNT's rows so Joe can open them in Excel. Joe 1119, naming the
--   columns himself: *"| the setup row | side | MAE % | MFE % | max oob Mage | max oob b |
--   M-no-rev | lowband x-cross | lowband AW flip | highband x-cross | grace lowband AW flips |
--   grace highband AW flips | grace highband x-crosses | the leg closes |"*, then *"drop this into
--   a db table - I'll read it in excel"*.
--
--   HIS 1119: *"drop the one-bar read columns"*. max_oob_mage and max_oob_b - the climb read
--   at the setup row's own bar - are gone. leg_mage, the INCOMING leg's max, is the one he
--   keeps; the two disagreed on 354 of 399 rows on 09-24.
--
--   ONE ROW PER SETUP. The text report stays as it is; this is the same rows in a form a
--   spreadsheet can sort and filter.
--
--   THE KEY CARRIES THE KNOBS. A setup row is a function of the day, the window width (his "2 or
--   3 rows") AND every ORAC_ knob the hunt reads. `knobs` holds that set as the text the report
--   prints, so an A/B at different values lands beside its sibling instead of overwriting it.
--   Without it a rerun at a new knob would silently replace rows that answered a different
--   question.
--
-- Usage: mysql pk_optimizer < 261119_01_fdm3_orac_setups.sql
--   then: python3 docs/fdm3/oracle_rows.py setups <day> <out.txt> --db
--
-- Dependencies: the fdm3-oracle must be serving the 30 second page, since every count is read
--   from its rows.

DROP TABLE IF EXISTS fdm3_orac_setup;

CREATE TABLE fdm3_orac_setup (
  day            DATE         NOT NULL COMMENT 'the day the hunt ran over',
  win_rows       TINYINT      NOT NULL COMMENT 'his "across 2 or 3 rows" - the setup window width',
  knobs          VARCHAR(512) NOT NULL COMMENT 'every ORAC_ knob and its value, the set these rows were built at',
  setup_row      DATETIME     NOT NULL COMMENT 'the oracle row the setup ends on, UTC',
  side           ENUM('HIGH','LOW','none') NOT NULL COMMENT 'the pseudo trade target-side at that row',
  mae_pct        DOUBLE       NULL COMMENT 'adverse excursion %, the setup bar to its leg close, scoring the OUTGOING trade. Never above 0',
  mfe_pct        DOUBLE       NULL COMMENT 'favourable excursion %, the same span. Never below 0',
  mfe_over_mae   DOUBLE       NULL COMMENT 'mfe_pct / abs(mae_pct). NULL when mae_pct is 0',
  rank_in_side   SMALLINT     NULL COMMENT '1 is the best of this row own side on mfe_over_mae',
  leg_mage       TINYINT      NOT NULL COMMENT 'the INCOMING leg max oob Mage TF, carried across the leg. HIS 1119 replaced M-no-rev with it',
  low_xcross     TINYINT      NOT NULL COMMENT 'distinct lowband TFs with an x-cross across the window',
  low_aw_flip    TINYINT      NOT NULL COMMENT 'distinct lowband TFs flipping TO -> AW across the window',
  high_xcross    TINYINT      NOT NULL COMMENT 'distinct highband TFs with an x-cross across the window',
  grace_low_flip TINYINT      NOT NULL COMMENT 'distinct lowband TFs flipping TO -> AW inside the grace',
  grace_high_flip TINYINT     NOT NULL COMMENT 'distinct highband TFs flipping TO -> AW inside the grace',
  grace_high_x   TINYINT      NOT NULL COMMENT 'distinct highband TFs with an x-cross inside the grace',
  leg_closes     DATETIME     NULL COMMENT 'the bar v4_sweep_pivots closes the scoring leg on',
  PRIMARY KEY (day, win_rows, knobs, setup_row),
  KEY k_side_rank (day, win_rows, side, rank_in_side),
  KEY k_leg (day, win_rows, leg_mage)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='fdm3 setup hunt rows, one per setup. Joe 1119: "drop this into a db table - I will read it in excel"';
