-- Filed: 2026-11-16
--
-- Intent: hold an fdm3 xe-aw scenario as TABLE DATA rather than as a paragraph and a pile of env
--   knobs. Joe 1116: *"instead of using a paragraph to describe a scenario, I'll now be explaining
--   scenarios as table data. this new method will allows us to drop the many 'knobs as envs' and
--   move the xe-aw scenarios into relational db tables. the tables are yours to build; my only
--   requirement is that the tables show a logical heirachy - be an SRP evangelist"*.
--
--   THE HIERARCHY, outermost first. Each table answers exactly one question and no value appears
--   in two places:
--
--     fdm3_measure      WHAT can be counted.      Scenario-independent vocabulary.
--     fdm3_band         WHICH timeframes.          Scenario-independent, resolved by the pivot.
--     fdm3_row_window   WHICH rows.                Scenario-independent, resolved by the range.
--     fdm3_scenario     the FRAME of one scenario: its range and its ltf/htf pivot.
--     fdm3_scenario_gate  one row per gate: a measure, over a band, over a window, against a bound.
--
--   So a gate carries no definitions of its own, a scenario carries no thresholds, and the
--   vocabulary carries no scenario. Adding a new kind of band or window is an INSERT, not a schema
--   change; adding a scenario touches only the last two tables.
--
-- Usage: mysql pk_optimizer < 261116_01_fdm3_scene_tables.sql
--   then a scenario's own seed, e.g. 261116_02_fdm3_scene1.sql
--
-- Dependencies: none. It reads fdm3-oracle's rows at run time through docs/fdm3/fdm3_scenes.py;
--   no table here depends on the oracle being up.

DROP TABLE IF EXISTS fdm3_scenario_gate;
DROP TABLE IF EXISTS fdm3_scenario;
DROP TABLE IF EXISTS fdm3_row_window;
DROP TABLE IF EXISTS fdm3_band;
DROP TABLE IF EXISTS fdm3_measure;


-- WHAT can be counted. One row per thing an fdm3 gate can measure on fdm3-oracle's rows.
-- This is the ONLY place that says what a word like `aw` means and how it is tallied.
CREATE TABLE fdm3_measure (
  measure      VARCHAR(24)  NOT NULL,
  oracle_read  VARCHAR(96)  NOT NULL COMMENT 'the oracle row field and the bit or code it reads',
  counted_as   ENUM('timeframes','prints') NOT NULL
               COMMENT 'timeframes: once per timeframe per window, ceiling 15. prints: every cell',
  note         VARCHAR(255) NOT NULL,
  PRIMARY KEY (measure)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='fdm3: what a gate can count. Joe 1116 scenarios-as-table-data';

INSERT INTO fdm3_measure (measure, oracle_read, counted_as, note) VALUES
  ('aw',      'TO/AW code 2 or 4',       'timeframes',
   'the cell reads AW(*) - AW(inf) or AW(exf). Joe 1115 ruled this one DISTINCT TIMEFRAMES'),
  ('aw_flip', 'cross code bit 4',        'prints',
   'a new AW: the cell reads AW where the row before read TO. Joe 1110. Counted as prints'),
  ('toexf',   'TO/AW code 3',            'timeframes',
   'the cell reads TO(exf) alone. Joe 1116: his 09-22 0216 example passes only on TO(exf), not on '
   'TO(exf) or AW(exf) together'),
  ('cross',   'cross code bit 1 or 2',   'timeframes',
   'an x-cross OR an e-cross - what his Nof15 counts. Joe 1115: once per timeframe, ceiling 15');


-- WHICH timeframes a gate reads. `lo_tf`/`hi_tf` are absolute; a NULL end is taken from the
-- scenario's ltf_to_htf_pivot plus the matching offset, so one pivot drives every band.
CREATE TABLE fdm3_band (
  band          VARCHAR(16) NOT NULL,
  lo_tf         TINYINT UNSIGNED NULL COMMENT 'absolute low end, or NULL to take it from the pivot',
  hi_tf         TINYINT UNSIGNED NULL COMMENT 'absolute high end, or NULL to take it from the pivot',
  lo_pivot_off  TINYINT NULL COMMENT 'added to the pivot when lo_tf is NULL',
  hi_pivot_off  TINYINT NULL COMMENT 'added to the pivot when hi_tf is NULL',
  note          VARCHAR(255) NOT NULL,
  PRIMARY KEY (band),
  CONSTRAINT fdm3_band_lo CHECK ((lo_tf IS NULL) <> (lo_pivot_off IS NULL)),
  CONSTRAINT fdm3_band_hi CHECK ((hi_tf IS NULL) <> (hi_pivot_off IS NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='fdm3: which timeframes a gate reads, resolved by the scenario pivot';

INSERT INTO fdm3_band (band, lo_tf, hi_tf, lo_pivot_off, hi_pivot_off, note) VALUES
  ('total', 1,    15,   NULL, NULL, 'every timeframe the oracle prints a cell for, ws1..ws15'),
  ('ltf',   1,    NULL, NULL, 0,    'ws1 up to and including the pivot - Joe 1116 ltf-to-htf-pivot '
                                    'is *"the highest ltf TF"*'),
  ('htf',   NULL, 15,   1,    NULL, 'the first timeframe above the pivot, up to ws15');


-- WHICH rows a gate reads, every window ENDING on the row the scenario qualifies on - Joe 1114
-- *"treat N rows as a window. if all of the gates are present inside the window, then the mech
-- qualifies"*. `n_rows` NULL takes the scenario's max_consecutive_rows.
CREATE TABLE fdm3_row_window (
  row_window  VARCHAR(16) NOT NULL,
  n_rows      TINYINT UNSIGNED NULL COMMENT 'rows back from the qualifying row, or NULL for the range',
  note        VARCHAR(255) NOT NULL,
  PRIMARY KEY (row_window)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='fdm3: which rows a gate reads, resolved by the scenario range';

INSERT INTO fdm3_row_window (row_window, n_rows, note) VALUES
  ('range',    NULL, 'the scenario''s whole range - its max_consecutive_rows, ending on the '
                     'qualifying row'),
  ('last_row', 1,    'the qualifying row alone - Joe 1116 *"at-last-row"* and *"on-last-row"*');


-- THE FRAME of one scenario. Its range and its pivot, and nothing else: no thresholds live here.
CREATE TABLE fdm3_scenario (
  scenario              VARCHAR(32) NOT NULL,
  max_consecutive_rows  TINYINT UNSIGNED NOT NULL COMMENT 'Joe: *"the scenarios range"*',
  ltf_to_htf_pivot      TINYINT UNSIGNED NOT NULL COMMENT 'Joe: *"the highest ltf TF"*',
  confirmed             TINYINT(1) NOT NULL DEFAULT 0
                        COMMENT '1 only once Joe has validated it by eye',
  his_example           VARCHAR(32) NULL COMMENT 'the row he named when he specified it',
  note                  VARCHAR(255) NOT NULL,
  PRIMARY KEY (scenario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='fdm3: one xe-aw scenario frame. Joe 1116 scenarios-as-table-data';


-- ONE ROW PER GATE. A measure, over a band, over a window, against a minimum or a maximum. The
-- knob name is his own, kept so a report can print his words back to him.
CREATE TABLE fdm3_scenario_gate (
  scenario    VARCHAR(32) NOT NULL,
  knob        VARCHAR(48) NOT NULL COMMENT 'his own knob name for this gate',
  seq         TINYINT UNSIGNED NOT NULL
              COMMENT 'where this gate sat in HIS list, so a report prints his order not the ABC one',
  measure     VARCHAR(24) NOT NULL,
  band        VARCHAR(16) NOT NULL,
  row_window  VARCHAR(16) NOT NULL,
  bound       ENUM('min','max') NOT NULL,
  threshold   SMALLINT NOT NULL,
  PRIMARY KEY (scenario, knob),
  KEY fdm3_gate_scenario (scenario),
  CONSTRAINT fdm3_gate_scenario_fk FOREIGN KEY (scenario)   REFERENCES fdm3_scenario (scenario)
    ON DELETE CASCADE,
  CONSTRAINT fdm3_gate_measure_fk  FOREIGN KEY (measure)    REFERENCES fdm3_measure (measure),
  CONSTRAINT fdm3_gate_band_fk     FOREIGN KEY (band)       REFERENCES fdm3_band (band),
  CONSTRAINT fdm3_gate_window_fk   FOREIGN KEY (row_window) REFERENCES fdm3_row_window (row_window)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='fdm3: the gates of one scenario, one row each. Joe 1116 scenarios-as-table-data';
