-- Filed: 2026-11-16
--
-- Intent: Joe's `scene1`, as he revised it on 1116, as rows rather than as env knobs. Every number
--   here is his. Two of his fifteen lines are the scenario's frame, one is a window size that
--   belongs to a single gate, and the other twelve are gates.
--
--   HIS LINES, in his order, and where each one went:
--     max-consecutive-rows: 4                      -> fdm3_scenario.max_consecutive_rows
--     ltf-to-htf-pivot: 7                          -> fdm3_scenario.ltf_to_htf_pivot
--     min-total-aw: 12                             -> a gate
--     min-total-aw-flips: 9                        -> a gate
--     min-single-row-aw-flips: 4                   -> a gate, on ANY one row inside the range
--     min-ltf-xcross-rows: 1                       -> the window_rows of the next gate
--     min-ltf-xcross-hits: 7                       -> a gate, an X-CROSS alone over that window
--     min-ltf-aw: 6                                -> a gate
--     min-htf-aw: 4                                -> a gate
--     min-ltf-aw-flips: 4                          -> a gate
--     min-htf-aw-flips: 5                          -> a gate
--     max-allowed-ltf-toexf-at-last-row: 0         -> a gate
--     max-allowed-htf-toexf-at-last-row: 2         -> a gate
--     min-aw-flips-on-last-row: 4                  -> a gate
--     min-n-of-15: 13                              -> a gate, an x-cross OR an e-cross
--
--   HIS 1116 CORRECTION: *"my cross is x only. Nof15 covers x or e"*. So `min-ltf-xcross-hits`
--   reads the `cross` measure, which is the x bit alone, and `min-n-of-15` reads `nof15`.
--
-- Usage: mysql pk_optimizer < 261116_02_fdm3_scene1.sql
-- Dependencies: 261116_01_fdm3_scene_tables.sql

DELETE FROM fdm3_scenario WHERE scenario = 'scene1';

INSERT INTO fdm3_scenario
  (scenario, max_consecutive_rows, ltf_to_htf_pivot, confirmed, his_example, note) VALUES
  ('scene1', 4, 7, 0, '2026-09-22 02:16:00',
   'Joe 1116, his first scenario written as table data. NOT confirmed: he validates by eye first');

INSERT INTO fdm3_scenario_gate
  (scenario, seq, knob, measure, band, row_window, bound, threshold, window_rows) VALUES
  ('scene1',  1, 'min-total-aw',                      'aw',      'total', 'range',      'min', 12, NULL),
  ('scene1',  2, 'min-total-aw-flips',                'aw_flip', 'total', 'range',      'min',  9, NULL),
  ('scene1',  3, 'min-single-row-aw-flips',           'aw_flip', 'total', 'single_row', 'min',  4, NULL),
  ('scene1',  4, 'min-ltf-xcross-hits',               'cross',   'ltf',   'inner',      'min',  7, 1),
  ('scene1',  5, 'min-ltf-aw',                        'aw',      'ltf',   'range',      'min',  6, NULL),
  ('scene1',  6, 'min-htf-aw',                        'aw',      'htf',   'range',      'min',  4, NULL),
  ('scene1',  7, 'min-ltf-aw-flips',                  'aw_flip', 'ltf',   'range',      'min',  4, NULL),
  ('scene1',  8, 'min-htf-aw-flips',                  'aw_flip', 'htf',   'range',      'min',  5, NULL),
  ('scene1',  9, 'max-allowed-ltf-toexf-at-last-row', 'toexf',   'ltf',   'last_row',   'max',  0, NULL),
  ('scene1', 10, 'max-allowed-htf-toexf-at-last-row', 'toexf',   'htf',   'last_row',   'max',  2, NULL),
  ('scene1', 11, 'min-aw-flips-on-last-row',          'aw_flip', 'total', 'last_row',   'min',  4, NULL),
  ('scene1', 12, 'min-n-of-15',                       'nof15',   'total', 'range',      'min', 13, NULL);
