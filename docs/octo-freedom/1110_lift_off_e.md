# lift-off's e-cross reversal, the 1110 update — BANKED and LIVE

GOAL: lift-off prints its reversal earlier and closer to the pivot, using the ws{TF}e cross. Joe 1110: *"my hope is
that the AW fields that fire at 0159, will start printing earlier"*, and his read of the result: *"good, the AWs are
printing earlier and closer to the pivot"*.

| item | state |
|---|---|
| banked | 1110, *"after that's validated, bank both mechs and make their configs the live machine"*. Knobs in `1022_v4/v4_lift_e.py`; an off-bank run refuses on import unless `W_LIFTE_EXPERIMENT=1` |
| live | the lift-off we develop on: every v4 lift-off reader gets it (his 6B, *"SRP rules"*; 2A, *"if they move, they move"*). 1112: live on its current config, his *"make the machines (lift-off, webui, towards/away) live on their current configs"*. The towards/away 1112 update does not change it - towards/away takes its own excursion sample (his answer "Towards/away only") |
| producer | `optimus9/analysis/jig.py`: `lift_off_e`, with `e_race_prep`, `e_race_wins`, `e_walk_back`. `lift_off` and `lift_off_pivot` take it as `e_path` |
| the e line | `1022_v4/v4_ws_e.py`, shared with the towards/away mech (`1109_towards_away.md`) |

## 1. His spec, 1110

- *"when ws{TF}e crosses a racer, "walk back to look forward" for the time when ws{TF}e was most extreme, before the
  cross. capture the ws{TF}r value at that time"*
- *"-make that bar's value the new r extremum"*
- *"-if the following lift-off sample is less extreme (ie is closer to 50), then print the reversal"*
- *"--this might need a "minimum less extreme" knob - the data will tell us when I review the update"*
- his 1109 note, moved here on SRP: *"lift-off is partially building a pre-fire six-sample reversal setup (ie lines
  are flattened or printing away from target-side)"*; 1110 *"I see these as different things.  the "folowing
  sample"  is produced by lift-offs natural sampling"*
- his scoring: *"the scoring is (would lift-off still complete the same six-sample run and turn it into a reversal,
  without the early e-cross)"*
- the lines: *"add ws1-3 to towards/away and liftoff, and update webUI"*

## 2. The mechanic, in firing order

| step | rule | from |
|---|---|---|
| the race | ws{TF}e against race:{boundary 15 LOW / 85 HIGH, closed-prev ws{TF}Mage, closed-prev ws{TF}r}; HIGH crosses UNDER, LOW crosses OVER; no hold; the first line crossed wins; the race re-opens once e crosses back over that line. Over the whole tape, per side | his 3A, 4B |
| gate 1 | r on the cross bar is NOT a new extreme: not beyond every r value in lift-off's window before it, `[c - (pts-1) x gap, c - 1]` | his 1B; the window span is mine |
| gate 2 | no lift-off reversal (natural or e) has stamped since r's most extreme bar in that window, up to the cross | his 1109 5A; the latest extreme bar is mine |
| the extremum | walk back to look forward on ws{TF}e from the cross (jig.mage_cascade_bar, 48-bar = 240 s steps) to e's most extreme bar; r there is the extremum and that bar is the reversal's pivot | his spec, 1A |
| the samples | every lift-off gap after the cross, `c + n x gap` (gap = TF x 2.8 bars). The first whose r is closer to 50 than the extremum by more than LIFT_E_MIN_LESS prints the reversal ON THAT BAR, no hold | his 2B; *"yes"* to no hold |
| the wait ends | printing nothing, at the first of: r goes strictly past the extremum on any bar from the cross; a natural lift-off reversal stamps; the next race win; the tape's end | MINE, all four |
| to a caller | an e reversal's raw bar is `stamp - (wob - 1)`, so every caller's own `raw + wob - 1` lands on its stamp whatever wob it passes. lift_off_pivot maps it to the walk-back bar | MINE (the contract) |
| natural lift-off | unchanged. An e reversal does not cancel the natural reversal of the same turn | MINE |

## 3. KNOBS

### 3a. Banked in `v4_lift_e.py` (env `W_LIFTE_<NAME>`, off-bank refuses on import)

| knob | value | what it does | from |
|---|---|---|---|
| `LIFT_E_ON` | 1 | the e path on for every reader; 0 is the 1022 lift-off exactly | his 6B + 2A |
| `LIFT_E_STEP` | 48 bars = 240 s | the walk-back step, every TF | his 1A |
| `LIFT_E_MIN_LESS` | 0.0 r-points | how much closer to 50 a sample must be; 0 = any amount | his knob; he sets it from the data |
| `LIFT_E_RACE` | boundary, Mage, r | the race lines, in tie-report order | his race:{boundary,Mage,r} |
| `LIFT_E_RACE_READ` | closed_prev | how the race's r and Mage are read | the standard race (v4_fdm2.x_race) |
| ws{TF}e identity | towards-away, version 2 | the config row (checked in the same registry) | his 1110 add ws1-3 |

### 3b. Read from their own homes

| knob | value | home |
|---|---|---|
| ws{TF}e | BB%B 3\|0.5\|close, emerging, ws1..ws30, every 60 s | mech_line_config `towards-away` / `e` / version 2 (v1 = ws4..ws30, sweep-only since 1110) |
| ws{TF}e control | ws4e..ws30e sum 2174735698.786861 and ws30e 99.629759 at 2026-08-25 03:28:00 (1109); ws1e..ws3e sum 241557997.374598 (1110) | v4_ws_e, asserted on every load |
| LIFT_PTS | 6 samples | v4_knobs |
| GAP_PER_TF | 2.8 bars per TF-minute | v4_knobs |
| LIFT_TOL | 2.0 r-points | v4_knobs |
| LIFT_WOB | 8 bars (the natural hold) | v4_knobs; each caller may pass its own wob |
| OOB_FNC | 15, so the race boundary is 15 / 85 | v4_knobs |

## 4. Who reads it

| reader | the call |
|---|---|
| v4_fdm2 | LIFT stamps per (TF, side), built at load |
| v4_fdm_reentry | the reversal stamps and the pivot table |
| v4_fast.revs | the cached raw bars (lineage, proxy, cadence, seam stream, test script ws4r) |
| v4_lineage2 | ws{TF}r reversals at LIN2_REV_WOB 12 |
| v4_l2_cadence | cws1r reversals at L2_CWS1R_WOB 1, and the latch-walk stamps at LIN2_REV_WOB 12 |
| v4_l2_proxy | the ex-fence latch's lift release, and the 1031 re-latch check (`relatch_ok`, wired 1110 after the bank: it had been missed) |
| v4_lineage_trace | the first reversal at or after a bar |
| v4_saviour | the saviour cascade's lift-off anchor |
| v4_backstop | ws5r reversals |
| towards/away | scenario 1's extremum (stored only when more extreme, his 3B; ex-20/80 only, 5A) |
| NOT | v4_test_script's ws2Mage lift-off, out/momo_render.py's ws1Mage lift-offs and out/xcv_report.py's ws{TF}Mage lift-offs (Mage lines, not r); live_seam (a live grid has no cached e line) |
| NOT WIRED, open | report scripts in the dated folders that call jig.lift_off on an r line themselves: 1103_fdm/fdm_cadence_census.py, 1030_mom_fence/latch_release_ab.py and wob_7_11_17.py, and the 20 scripts in 1027_pseudo_closed that call it. Re-run as they stand, they print the 1022 lift-off |

| cache | keyed on the e-path knobs |
|---|---|
| v4_fast, v4_lineage2, v4_l2_cadence, v4_l2_proxy | in-process, `LE.knobs()` in the key |
| out/re_sigcache.py | on disk: `LE.knobs()`, the e line identity, and a hash of the e lines in the key - a cold rebuild once |

## 5. Checks

| check | result |
|---|---|
| lift_off_e against a separate bar-by-bar version: ws4r, ws11r, ws30r both sides (1110) | 14,693 reversals, identical |
| the same on ws1r, ws2r, ws3r both sides (1110) | see the 1110 bank report |
| ws1e..ws3e cached against a fresh in-memory build | max diff 0, NaN positions equal |
| line cache: existing files changed by the e writes | 0 (27 new 1109, 3 new 1110) |
| ws1r with LIFT_E_ON and no e line (before 1110) | equal to the natural lift-off |

## 6. His scoring, ws4..ws30 (before ws1-3 were added)

MY reading of *"the same six-sample run"*: a natural lift-off stamps after the e reversal, before r goes past the e
extremum.

| set | e reversals | natural reversal followed | none before r went past | e lead, median s | p10 s | p90 s |
|---|---|---|---|---|---|---|
| ws4..ws30 | 74,972 | 49,495 | 25,477 | 680 | 40 | 3,483 |

## 7. Not done

- the banked v4 results that read lift-off (fdm2 legs, lineage, backstop) have not been re-run on it.
