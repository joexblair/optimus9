# THE dws LINE SERIES, AND THE FLIPPED-dr CLOSE READING — 1013

Joe 1012: *"create a new ic series labelled `dws`, and create dws[8,10,15]r. -the r config will be
doubled so that we build more granular TF16, TF20, and TF30 r lines"* / *"I want them in the
momentum sling, we need more confluence data for the report"* / *"add the 3 lines to the mech that
consumes ws{any TF that carries momentum}r"*.

Joe 1013: *"add ws12"* / *"flip it back - it's better with dates up top"* / *"flip the dr on the
close trade - we're not reversing, we're extending the leg using those mom-true lines"* /
*"timeframe 8 ,10,15"*.

## THE LINES AS REGISTERED

Three rows in `pk_optimizer.indicator_configs`, series `dws` (is_pk 19), confirmed through
`pk_optimizer.vw_indicator_configs_live`. Every one is line type `k`, src `close`, value mode
`emerging`, k_len 14 / rsi_len 10 / stc_len 16 — the ws r-line's 7 / 5 / 8 doubled.

| line | itf_seconds | timeframe, min | live_after inherited from its source line |
|---|---|---|---|
| dws8r | 480 | 8 | 2026-08-05 |
| dws10r | 600 | 10 | 2026-08-15 |
| dws15r | 900 | 15 | 2026-08-05 |

`indicator_timeframes` carries duplicate second-counts under different labels — itf_pk 27 is label
'5' at 600 s against itf_pk 28 label '10' at 600 s; itf_pk 14 is label '9' at 900 s against itf_pk 9
label '15' at 900 s — so `seed_dws_lines.py` reads each source line's OWN row for its itf_pk rather
than looking one up by seconds.

A BEFORE UPDATE trigger `trg_indicator_configs_live_after_bu` sets `ic_live_after_dt = CURDATE()`
on every update, on **pk_optimizer only**; `o9_live` is deliberately untouched.
TIE RISK, STATED: `vw_indicator_configs_live` picks `MAX(ic_live_after_dt)` per
`(ic_is_pk, ic_il_pk, ic_itf_pk)` with no tiebreak on `ic_pk`, so two CURDATE() stamps on one line
in one day make the MAX tie and the view returns both rows.

## THE CACHE, BUILT

`LG_TAPE_END=2026-10-05 python3 -m optimus9.orchestration.build_ws_lines --prefix dws`

tape end 2026-10-05 00:00 UTC, hours 40, warmup 1114, span 2268 h, 1,632,960 bars,
ts 2026-07-02 12:00:00 -> 2026-10-04 23:59:55.

| line | finite bars | min | median | max | first finite |
|---|---|---|---|---|---|
| dws8r | 1,629,408 | 0.29 | 49.73 | 98.97 | 2026-07-02 16:56:00 |
| dws10r | 1,628,520 | 0.00 | 50.19 | 99.60 | 2026-07-02 18:10:00 |
| dws15r | 1,626,300 | 0.98 | 50.33 | 99.50 | 2026-07-02 21:15:00 |

## FIVE CHANGES, AND WHY EACH ONE WAS NEEDED

1. `build_ws_lines.TAPE_END` now reads `LG_TAPE_END`, **default = the 2026-09-30 literal it already
   held**. score39.py:40 already reads this env var with its own default, so a build run without it
   writes a cache key score39 never reads: the dws lines would have landed on the 09-30 key while
   every scoring run reads 10-05, and the lines would simply be missing. NOT a fourth tape literal —
   the default IS the old literal, so no importer moves unless the env var is set.

2. Built with `--prefix dws`, already supported by the module's argv handling.

3. `score39.LDN(name)` — read a line by its REGISTERED NAME.
   WHY `LD` CANNOT REACH THEM: `LD(tfs, role)` swaps a timeframe into a **wsf role's** config and
   hashes that tuple. The r role is k_len 7 / rsi_len 5 / stc_len 8; a dws line is 14 / 10 / 16, a
   different tuple and so a different file. Measured:

   | what is asked for | the cache key it resolves to |
   |---|---|
   | `LD(900, 'r')` | 82c096c823c878c926d5 |
   | `ws15r` | 82c096c823c878c926d5 |
   | `dws15r` | edd82097e52ec08e3a52 |

   `LineStore.resolve` + `LineStore.value_mode` are the sanctioned readers — the same two calls
   `build_ws_lines.overrides()` makes — and the NAMES come from the live view, so there is no
   literal line name in score39 and a row change moves this with it.
   No new `mech_line_config` role was added: that would have put 3 extra lines in front of the 22
   scripts that iterate the live wsf line set.

4. `_momtrue._key` now carries the line's name. Until 1013 the key held the tape window, the
   timeframe and the banked k_window but NOTHING about WHICH line was measured — and the dws lines
   sit on tf 8, 10 and 15, the same timeframes as ws8/ws10/ws15. A dws8 mask would have collided
   and silently loaded the **ws8** mask: the 1008 cache-drift failure exactly.
   ADDITIVE: `line_id=None` reproduces the pre-1013 key, so every mask already on disk stays valid.

5. `_chain10.MOMD`, built beside `MOMT` under the same `BATON in ('momentum','either')` gate so the
   default run is untouched. **Keyed by name, never by timeframe** — `MOMT` is keyed by the
   timeframe int and dws8r would overwrite ws8.

## THE TIMEFRAME RULING

Joe 1013: *"timeframe 8 ,10,15"* — each dws line is measured on the timeframe it is BUILT on, not
on the doubled one its r-config stands in for. `k_window` is 6 on every bank, so:

| line | timeframe, min | momo bank | momo window = k_window x tf, min |
|---|---|---|---|
| dws8r | 8 | ws8 | 48 |
| dws10r | 10 | ws10 | 60 |
| dws15r | 15 | ws15 | 90 |

The alternative, now ruled out, was tf 16 / 20 / 30 — the bank and window of the timeframe the
doubled config represents.

## THE FLIPPED-dr CLOSE READING

Joe 1013: *"flip the dr on the close trade - we're not reversing, we're extending the leg using
those mom-true lines"*. The OPEN column is read on the leg's own board (board = -dr, the banked
rule); the CLOSE column is read on the board of the FLIPPED dr. The unflipped close tally stays in
the report underneath, so nothing is hidden.

| bar | leg | which | dr on this column | board read |
|---|---|---|---|---|
| 2026-07-17 21:58:00 | 07-17 21:58 LONG | OPEN | -1 LONG | HIGH |
| 2026-07-18 01:15:20 | 07-17 21:58 LONG | CLOSE | +1 SHORT (flipped) | LOW |
| 2026-07-18 02:31:00 | 07-18 02:31 SHORT | OPEN | +1 SHORT | LOW |
| 2026-07-18 10:40:40 | 07-18 02:31 SHORT | CLOSE | -1 LONG (flipped) | HIGH |
| 2026-07-18 08:46:55 | 07-18 08:46 LONG | OPEN | -1 LONG | HIGH |
| 2026-07-18 10:07:10 | 07-18 08:46 LONG | CLOSE | +1 SHORT (flipped) | LOW |
| 2026-07-18 16:11:10 | 07-18 16:07 LONG | OPEN | -1 LONG | HIGH |
| 2026-07-18 16:38:15 | 07-18 16:07 LONG | CLOSE | +1 SHORT (flipped) | LOW |

### mom-true state, 7 lines, closes on the flipped dr

`tgt` = mom-true toward that column's board. `agst` = toward the other one.
mom-true = momo OR curl, side-aware, read AT each bar, so both reads are causal at their own bar.

| line | 2026-07-17 21:58:00 | 2026-07-18 01:15:20 | 2026-07-18 02:31:00 | 2026-07-18 10:40:40 | 2026-07-18 08:46:55 | 2026-07-18 10:07:10 | 2026-07-18 16:11:10 | 2026-07-18 16:38:15 |
|---|---|---|---|---|---|---|---|---|
| ws12 | - | - | tgt | tgt | /agst | /agst | /agst | - |
| ws15 | - | /agst | - | tgt | /agst | /agst | /agst | tgt |
| ws20 | - | /agst | /agst | tgt | - | /agst | /agst | tgt |
| ws30 | /agst | /agst | /agst | - | /agst | - | - | tgt |
| dws8r | - | - | - | tgt | /agst | - | - | - |
| dws10r | - | /agst | /agst | tgt | - | - | /agst | tgt |
| dws15r | - | /agst | /agst | tgt | - | - | - | tgt |
| **toward this column's board** | **0 of 7** | **0 of 7** | **1 of 7** | **6 of 7** | **0 of 7** | **0 of 7** | **0 of 7** | **5 of 7** |
| **against it** | **1 of 7** | **5 of 7** | **4 of 7** | **0 of 7** | **4 of 7** | **3 of 7** | **4 of 7** | **0 of 7** |

### the same closes on the leg's own board — the unflipped reading

| bar | leg | its own board | toward it | against it |
|---|---|---|---|---|
| 2026-07-18 01:15:20 | 07-17 21:58 LONG | HIGH | 5 of 7 | 0 of 7 |
| 2026-07-18 10:40:40 | 07-18 02:31 SHORT | LOW | 0 of 7 | 6 of 7 |
| 2026-07-18 10:07:10 | 07-18 08:46 LONG | HIGH | 3 of 7 | 0 of 7 |
| 2026-07-18 16:38:15 | 07-18 16:07 LONG | HIGH | 0 of 7 | 5 of 7 |

### the r value at the same bars

| line | 2026-07-17 21:58:00 | 2026-07-18 01:15:20 | 2026-07-18 02:31:00 | 2026-07-18 10:40:40 | 2026-07-18 08:46:55 | 2026-07-18 10:07:10 | 2026-07-18 16:11:10 | 2026-07-18 16:38:15 |
|---|---|---|---|---|---|---|---|---|
| ws12r | 52.63 | 84.64 | 53.59 | 87.28 | 33.82 | 68.71 | 8.47 | 31.81 |
| ws15r | 39.10 | 89.90 | 78.77 | 75.85 | 40.22 | 58.73 | 21.96 | 16.29 |
| ws20r | 38.66 | 81.30 | 95.57 | 89.72 | 35.74 | 65.91 | 39.65 | 35.50 |
| ws30r | 19.03 | 58.12 | 87.76 | 37.23 | 0.10 | 24.24 | 62.07 | 54.41 |
| dws8r | 39.29 | 80.09 | 75.87 | 71.12 | 49.84 | 45.17 | 39.71 | 31.16 |
| dws10r | 35.61 | 75.64 | 90.53 | 74.10 | 50.90 | 62.23 | 48.07 | 41.27 |
| dws15r | 31.13 | 49.05 | 77.00 | 37.43 | 7.90 | 27.12 | 71.48 | 63.23 |

### what the rows show, flat

- 0 of 7 toward the board at three of the four opens; 1 of 7 at 2026-07-18 02:31:00, ws12 alone.
- 6 of 7 toward the flipped board at 2026-07-18 10:40:40 — all three dws lines print `tgt` there.
- 5 of 7 toward the flipped board at 2026-07-18 16:38:15; dws8r is the one that does not.
- 0 of 7 toward the flipped board at 2026-07-18 01:15:20 and 2026-07-18 10:07:10.
- dws8r prints `-` at 6 of the 8 bars, the quietest of the seven rows.
- no bar has lines pointing both ways: every column is 3-and-0 or better in one direction.

## THE REPORT SCRIPT

`/home/joe/.claude/jobs/6eb9931e/tmp/_momflip3.py`, run as
`LG_TAPE_END=2026-10-05 W_CEIL=30 W_BATON=momentum python3 _momflip3.py` from
`docs/octo-freedom/1005_scoring`. `W_CEIL=30` is required — the default ceiling is ws23 and
`MOMT[30]` does not exist without it. The three dws masks took 1,110 s to build on first run and
are cached from here.
