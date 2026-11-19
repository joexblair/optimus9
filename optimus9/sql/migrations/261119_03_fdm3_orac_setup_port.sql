-- Filed: 2026-11-19
--
-- Intent: let Joe tell one page's rows from another's in Excel.
--
--   HIS 1119: *"fdm3_orac_setup on 8792 - yes thanks. use a new key and I'll filter on it"*. The
--   port already sat inside the `knobs` string, since it is an ORAC_ knob, but that column is a
--   512 character set of name=value pairs and nothing in a spreadsheet can filter on it. `port` is
--   the same fact as a short number he can put in a filter.
--
--   THE PORT IS A KEY COLUMN, not just a label: his ORAC_EXHAUST_PORT moved 8791 -> 8792 at his
--   *"make this the machine"*, and the two pages carry DIFFERENT pivot trades under the same
--   timestamps - ws2Mage's on 8791, the four-read pooled ones on 8792. The same timestamp therefore
--   has two honest and different rows, and without the port in the key the second run would
--   overwrite the first.
--
-- Usage: mysql pk_optimizer < 261119_03_fdm3_orac_setup_port.sql
--   then: python3 docs/fdm3/oracle_rows.py setups <day> <out.txt> --db
--
-- Dependencies: 261119_01 and 261119_02.

ALTER TABLE fdm3_orac_setup
  DROP PRIMARY KEY,
  ADD COLUMN port SMALLINT NOT NULL DEFAULT 0
    COMMENT 'the oracle port these rows were read from: 8791 ws2Mage pivots, 8792 the four-read pooled pivots'
    AFTER day,
  ADD PRIMARY KEY (day, port, win_rows, knobs, setup_row),
  ADD KEY k_port (day, port, win_rows, is_setup);

UPDATE fdm3_orac_setup SET port = 8791 WHERE port = 0;
