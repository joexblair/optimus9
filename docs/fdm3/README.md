# fdm3 — the index

GOAL: hold every fdm3 mech in one place, so a reader can find what each one decides without
reading the code.

---

## what fdm3 does

fdm3 reads the state of the market at the moment a trade opens and shapes that trade's walk to suit
it, rather than running one fixed walk shape in every condition. Its first mech, `fdm3-sideways`,
asks a single question at the open bar — is the market consolidating or running — by taking the
`pxs` pivot inside a `ws1b` oob excursion and reading whether the `ws{fdm3-sideways-trigger}` b and
r lines are out of bounds there; a consolidating market leaves `sideways == true`, the resting
state, and a running one turns it off for the life of the trade. The flag can only ever turn off,
never back on, and it is re-tested at every ws1 seam so a market that starts flat and then runs is
caught mid-walk. A second, slower path can also turn it off: a `pxs` retest that compares two
`ws{fdm3-sideways-trigger}` OHLC open extrema twenty-five minutes apart and, when they sit within
`fdm3-sideways-retest-diff-pct` of each other, asks the divergence read whether `ws3r`, `ws4r` or
`ws5r` disagrees with price across that span.

---

## the mechs

| the mech | its doc | what it decides | state |
|---|---|---|---|
| `fdm3-sideways` | [fdm3-sideways.md](fdm3-sideways.md) | whether a trade opens in sideways mode | the trigger and the retest are specified and matched against Joe's examples. What sideways mode DOES is not yet specified. Only a probe exists |
| `scene1` | [fdm3_scenes.py](fdm3_scenes.py) + the five `fdm3_*` tables | an xe-aw scenario held as TABLE DATA, not as env knobs — thirteen gates over a 4-row window, split at an ltf-to-htf pivot of ws7 | built and loaded. ALL 13 gates pass at his 09-22 0216 example and it fires there. 45 rows over the 94 day tape, 0.48 a day, at the live A state. Awaiting his eyes before `confirmed` moves to 1 |
| `fdm3-ltf-5aw-6x` | [oracle_rows.py](oracle_rows.py), `ltf_5aw_6x` | an aw-exhaust event — five gates over a 3-row window of the oracle's rows: >=6 of ws1..ws8 carrying an x-cross inside 1 row, >=10 of ws1..ws15 crossing collectively, <=1 of ws8..ws15 printing exf, >=10 timeframes reading AW(\*), and >=5 new AW prints | **CONFIRMED by Joe 1116.** The evidence is [out/ltf_5aw_6x_0920_0923_A_ws1_ws6.txt](out/ltf_5aw_6x_0920_0923_A_ws1_ws6.txt) — 40 instances over 09-20..09-23, read with A ws1-ws6 on. What an aw-exhaust event DOES is still unspecified |
| `fdm3-4-ltf-aws` | [oracle_rows.py](oracle_rows.py), the `find` and rate modes | an aw-exhaust event — >=4 AW flips on one row within ws1..ws6, with >=13 of ws1..ws15 crossing collectively, both inside a 4-row window | built and measured: 816 rows over the tape, 8.6 a day. His 09-23 0157 example matches exactly. Not confirmed |
| `fdm3-ltf-xcross` | [oracle_rows.py](oracle_rows.py), `ltf_xcross` | >=6 of ws1..ws8 carrying an x-cross inside 2 rows, inside 3 rows carrying 13of15, with >=4 timeframes reading AW(\*) and >=2 new AW prints | built and measured: 19,687 rows over the tape, 208.3 a day. Four of his five examples fire on the row he named and 09-24 2230 one row later. Not confirmed |
| `orac-exhaust` | [1118_orac_exhaust.md](1118_orac_exhaust.md) | his three states over the 30 second oracle's rows, scored on the four-read pivots | **THE MACHINE, his 1118 *"we've landed well. make this the machine"***. 2026-09-24 on 8792, his 1119 pick: 472 rows print, 34 open a grace, 1 fires (07:45:30) - on 8791 it was 399, 51 and 3. Seven open rulings are listed in section 6 of its doc |
| `fdm3-small-trade` | [1119_small_trade.md](1119_small_trade.md) | per row, the distinct ws8-15 lines that have printed TO(exf) since the trade's first row: `sml` while 2 or fewer, `lrg` from the 3rd, held to the trade's close. Printed under legMage | **BANKED, LIVE on 8792 - his 1119 *"commit and push all. bank the updates and make this the machine"***. 2026-09-24: 35 trades, 20 `sml` at their close. The walk version is not built |
| "-" on the counter side of 50 (his name pending) | [1120_counter_side_of_50.md](1120_counter_side_of_50.md) | a line on the counter side of 50, emerging r, prints "-" instead of TO or AW, the trade's open included, and does not count toward scenario 2's lines-under test | BUILT on 8792, 2026-11-20, his *"be built on 8792"*. Off on the bank (`UNTAG50` 0), so a bank run of orac-exhaust refuses 8792 until he banks it |
| the four-read pivots | [sweep-pivots' spec, section 10](../octo-freedom/1022_v4/v4_sweep_pivots.md) | sweep-pivots' own since his 1120 *"the pivots can't belong in any fdm3 classes"*: ws1Mage and ws1b, each emerging and closed-prev, pooled into one pivot list, with their knobs, the +15 min and flipped sets, the lookahead and the pine view | **BANKED.** 3,006 on the tape. fdm3 only imports a set |
| `fdm3-oracle` | [docs/octo-freedom/1022_v4/out/fdm3_oracle.py](../octo-freedom/1022_v4/out/fdm3_oracle.py) | it SHOWS, it does not decide: one row per closed-prev ws1 bar, one cell per wsf line, carrying `breaching_line.predict_breach`'s -1/+1 on the emerging r, m and Mage, with the word towards or away under each cell | **8793 IS THE MACHINE since 2026-11-22 18:52:15**, launched with NO settings but its port - every fdm3 knob and every page setting at its default. It is his 1122 *"clone 8792 to a new port.  instead of using pivots to create legs, I now want two continuous trades that run for the full window's length, one short and the other long.  I'll use a button to flip between the 2 trades"*, banked at his 1122 *"this is good - bank it, commit push, update the docs.  make this the machine"*: ONE trade from the tape's first bar to its end - the short one as found, target-side LOW, and the long one on the button, target-side HIGH (the page default `FDM3_PIVOTS` = two, and 30 s rows, `FDM3_ROW_S` = 30, both moved at his answer *"Move them"*). No +15 button (no pivots to shift); legMage and `sml`/`lrg` print blank, his answer *"Blank both"*. ws1r..ws30r at K len 6, RSI len 6, stoch range 9 (fdm3 knob `ORACLE_R_CFG` = 6,6,9), read from its own cache by [fdm3_r_cache.py](fdm3_r_cache.py). The nine in-fence bands (fdm3 knob `INFENCE_EDGES`) read on his 1122 30 s seam at x:25 and x:55 (fdm3 knob `INFENCE_READ` = `closed_prev_30s`), with the (exf) suffix (`EXF_SUFFIX` = 1), the "-" on the counter side of 50 (`UNTAG50` = 1), and the red suffix on a ws2-ws15 line leaving +4 or -4 (his 1122 *"expand the red colour mech's coverage to include ws2-ws15"*) - see [1119_infence_power.md](1119_infence_power.md) sections 3b, 3c and 3d. Its path: 8794 served the two trades on the 1-minute seam from 2026-11-22 16:22:13 and was the machine at the bank; his answer *"Build on 8793, stop 8792"* built the 30 s seam and the ws2-ws15 red on 8793 while 8794 served, and 8794 was stopped 2026-11-22 18:52:45. **8794 is STOPPED since 2026-11-24 22:28:12**, his 1124 *"stop 8794.  I'm now using 8793 and 8795 only"* - it had no row cache (it ran the code from before the cache). Before that, 8794 served beside it from 2026-11-22 19:12:45, his *"can't I have 8794 and 8793 together?"* and his answer *"As it was"*: the two trades on the 1-minute seam with the red on ws8-ws15 (fdm3 knobs `INFENCE_READ` = `closed_prev_minute` and `RED4_LINES` = 8-15), an off-ruled page - its red and band-move counts equal the 18:52:45 page's, line by line. Every other port is stopped: 8792 at 2026-11-22 18:41:41 for the memory (it served pooled pivots with his 1121 *"B"* +15 and r 6,6,9, his 1121 *"clone 8793 to 8792 and change the config of r"*); 8793's 1121 bank, his *"8793 is good - bank it and make the machine."* (stored r, pooled pivots, the 1-minute read), at 2026-11-22 16:11:23, his answer *"Stop 8793"*; 8788 at his 1121 *"kill 8788"*; 8791 at his 1121 *"shut 8791 down - the hold 1 tol 0.67 isn't useful"* (fdm3 knob `TA_LIFT`, off on the bank); 8790 at his 1119 *"and stop the other instances"*. A page held about 8.0 GB until his 1124 *"the reason for the memory control"*, his answer *"Free start-up only"*: the start-up now runs in a forked child that hands back only the rows (29.9 MB on the whole tape, both trades) and exits, so a serving page holds about 0.2 GB - 8794 202,844 kB and 8793 204,232 kB after their restarts on 2026-11-24 (8794 serving 20:08:42, 8793 dark 20:08:59 to 20:20:05), every byte of both trades equal to the rows saved from each before its stop. A start-up still peaks near 9.3 GB while it runs. Since his 1124 *"the rows are a small file - it should be kept on disk as well as in memory to avoid downtime on small cosmetic changes or restarts"* the rows are ALSO ON DISK, one directory per page settings under optimus9/orchestration/.rpl_cache/fdm3_rows (git-ignored), and a start-up reads them - about 2 s - only when every source module, data file and database read its full start-up used is unchanged (comments, docstrings and the page's HTML do not count). Anything else is a full start-up that writes a new cache. `FDM3_ROWS_CHECK=1` (MY name) prints whether a start-up would read the cache, and stops; `FDM3_ROWS_REBUILD=1` (MY name) forces a full start-up. 8793's cache was written 2026-11-24 20:50:28 after a 652.8 s start-up (dark 20:39:33 to 20:50:30); a test page read it on 8796 in 2.0 s, every byte equal to 8793's, and was stopped. The `o9-fdm3-oracle` unit is stopped (2026-11-20, his password) and still enabled. Renamed from `fdm2-oracle` at his 1114 *"rename it to fdm3-oracle in all places... you can take ownership of it now"*, and owned by this session from that bar. The installed systemd unit still carries the OLD name and needs his password to change - see the commands in the handover
| `fdm3-htf-oracle` | [docs/octo-freedom/1022_v4/out/fdm3_htf_oracle.py](../octo-freedom/1022_v4/out/fdm3_htf_oracle.py) (fdm3_oracle.py with `FDM3_PAGE` = htf), lines from [fdm3_htf_lines.py](fdm3_htf_lines.py) | his 1124 *"I need a parallel webservice built, named fdm3-htf-oracle"*: the time column, then ws20 to ws30, ws45, ws60, ws90, ws120 and ws240 - *"these replacement columns will print the same data as fdm3-oracle's ws1-15 fields"* - on rows *"per 1 minute seam (not 30s)"*, on the two trades | **8795, serving since 2026-11-25 01:17:22 with the VWAP columns** (read from the row cache in 0.5 s, dark from 01:17:14; the test page on 8796 stopped). Before: serving since 2026-11-24 20:55:31 (restarted for the row disk cache, dark from 20:51:08; its full start-up 250.2 s wrote the cache, 15 MB; about 0.15 GB serving; first up 20:24:41). Its ws23..ws30 TO, AW and TO(exf) counts equal 8793's ws23-30 sum column on all 136,079 rows of both trades. towards/away runs scenario 1 on ws15..ws30 and the 5 minutes under each column over ws30 (his answer *"The 5 minutes under it"*: ws40..ws44 under ws45, ws55..ws59, ws85..ws89, ws115..ws119, ws235..ws239), and a state on his 16 columns. Every line no cache held - 26 TFs in r 6,6,9, Mage, x and e, plus r and e for ws45/60/90/120 - is in its own cache (his answer *"A separate cache"*), 112 lines built 2026-11-24 20:09:40, ws30 controls max diff 0. The b9 colours (his *"I'm now refering to the 9 bands as `b9`"*) go against the row's target-side: red off -4 (short) / +4 (long), orange off -3, -2, -1 (short) / +3, +2, +1 (long), any size of move - his answers *"Against the trade's side"*, *"Red against trade only"*, *"Orange on any such move"*; see [1119_infence_power.md](1119_infence_power.md) section 3e. The ws1 TO(exf) flip and the ws5 TO(inf)-after-TO(exf) flip print on every column, his answer *"On every column"*. No SL%, legMage, sums or A buttons; HIS 1124/1125 TWO VWAP COLUMNS on the far right, *"research VWAP.  we'll be adding its data to the fdm3-htf-oracle table, in 2 new columns on the far right"*: ws5 vw pct and ws10 vw pct, six lines each (lo udist, lo vdist, lo ldist, hi udist, hi vdist, hi ldist - % from each line to the close of the x:55 bar, (price - line) / line), rows 98 px tall, built by [fdm3_vwap.py](fdm3_vwap.py), which carries every rule and answer. Anchored VWAP on 1-minute candles, source close, bands +/- 2 volume-weighted standard deviations; anchors from the closed ws5/ws10Mage cross-to-ib pivots (an oob run counts past 0.5 points) by his walk-back; his seven chart readings off the 2026-09-05 04:13 anchor match within 0.08%. Built on test port 8796 2026-11-25 01:14:33 (start-up 251.2 s, which wrote the row cache 8795 reads): every byte outside the VWAP block equal to 8795, 280 sampled VWAP cells re-derived by a second construction, 0 off; with one button left, the text box under it widens until it is no deeper than the calendars, his answer *"a dox no deeper than the calendars"* (8793 and 8794 keep his 1118 width) |

---

## obscure or unexpected uses of a mech

| the mech | the ordinary use | how fdm3 uses it |
|---|---|---|
| the divergence read, `jig.anchor_floater` | timing an EXIT. A divergence between price and an oscillator is traditionally read as a warning that the move in progress is tiring, so it is used to leave a trade | fdm3-sideways reads it on the trade about to BEGIN. Joe 1114: *"divergences are traditionally used to time an exit. in sideways mode, we want divergence to tell us how to handle the trade that is about to begin"*. The sign is therefore compared against the OUTGOING trade's side, not the incoming one |
| `jig.anchor_floater`'s own anchor and floater selection | the producer picks both bars itself, through its four-step look-back from one bar `k` | fdm3-sideways already knows which two bars to compare, so steps 1 to 3 must not run. `jig.anchor_floater_given` is Joe's ruled entry point: step 4 alone, on two bars handed in |
| a price match from the divergence read | `state ±2` is real evidence — price and the oscillator AGREE, the trend continuing | fdm3-sideways IGNORES it. Joe 1114: *"Price Match (state +/-2) will be ignored by sideways mode"*. Only `abs(state) == 1` counts |
| the `sideways` verdict's owner | a verdict read at a decision bar normally belongs to the trade being CLOSED, because the exit is the lever | `sideways` belongs to the trade being OPENED. Joe 1114: *"if we applied a sideways verdict to the incoming trade, that information would be lost when the incoming trade ends"* |
| a `ws1b` oob excursion | fdm2's cadence event is a `ws1b` oob→ib cross with its own nestle and gate tests | fdm3-sideways uses the same excursion as a CONTAINER — it looks inside it for the most extreme `pxs` bar, and the excursion's side sets every read's side |
| a bar's OHLC open | the lines and the backtest run off closes, highs and lows | the retest's two comparison points are OPENS of `ws{fdm3-sideways-trigger}` bars, which are not on disk and come from `kline_collection` directly |
| an x-cross and an e-cross | each print is its own event, and a timeframe can print several inside one window | every fdm3 scenario counts a cross ONCE per timeframe per window, so either count tops out at 15. Joe 1115: *"the x and e crosses are 1 type per TF per scenario (ie the max for any scenario is 15 of e and 15 of x)"*. The per-timeframe double prints stay unread until he rules on them |
| a scenario's definition | a paragraph of spec text, turned into knobs read from the environment | Joe 1116 writes a scenario as TABLE DATA in five relational tables, so a threshold is a cell he edits rather than a code change. The env knobs stay only for the scenarios written before that bar |
| the oracle's A buttons | a viewing option on the page, for looking at the lift-off reads a different way | Joe 1116: *"the A ws1-ws6 button is enabled now - I've found it to be better than having it disabled. bank this as the live machine"*. It is NOT a scenario gate — his earlier word was that it *"sits outside of the scenarion building. that button is underlying an infrastructure decision"* — so it is banked once, fdm3-wide, and EVERY fdm3 read of the oracle's rows is taken at it. It moves the AW columns only: the x and e cross bits are built outside the oracle's state loop and no A button can touch them |

---

## operating the oracle

| | |
|---|---|
| the unit | `o9-fdm3-oracle.service`, running as `joe` from `docs/octo-freedom/1022_v4/out`. STOPPED 2026-11-20 and still enabled: a reboot brings it back on 8788 at the page defaults - since 2026-11-22 the machine's own (30 s rows, the two trades, r 6,6,9, the 30 s seam) |
| the page | 127.0.0.1:8788 |
| the log | `/home/joe/thecodes/fdm3_oracle.log` |
| **a restart costs ~18 minutes** | Joe 1114: *"it takes ~18 minutes to restart"*. The 7 towards/away runs go one after another at 97.9 s to 109.4 s each, and the matrix is in memory with no disk cache |
| so | a restart is EXPENSIVE. Batch code changes to that file, and read the running page rather than restarting to check something |
| the standing idea for cutting it | Joe 1113: build the 8 combinations in parallel. cupy 14.1.1 and one RTX 3060 Ti are available, and every state must stay byte-identical to the serial page |

---

## the knobs

All fdm3 knobs live in [fdm3_knobs.py](fdm3_knobs.py), not in `v4_knobs`, so a v4 ruling and an
fdm3 ruling cannot move each other. Banked means the default has moved and an off-ruled run raises
at import unless `W_FDM3_EXPERIMENT=1`. The env override is `W_FDM3_<NAME>`.

| the knob | his name | value |
|---|---|---|
| `SIDEWAYS_TRIGGER` | `fdm3-sideways-trigger` | 5 |
| `SIDEWAYS_RETEST_SCAN_WINDOW` | `fdm3-sideways-retest-scan-window` | 12.5 |
| `SIDEWAYS_RETEST_DIFF_PCT` | `fdm3-sideways-retest-diff-pct` | 0.88 |
| `MOM_FNC` | `fdm3-23-77-fnc` (MY name, off his `fdm-20-80-fnc`) | 23.0 |
| `LTF_XCROSS_HITS` | `fdm3-ltf-xcross-hits` | 6 |
| `LTF_XCROSS_ROWS` | `fdm3-ltf-xcross-rows` | 2 |
| `LTF_XCROSS_MAXTF` | `fdm3-ltf-xcross-maxTF` | 8 |
| `LTF_XCROSS_NOF15_ROWS` | `fdm3-ltf-xcross-nof15-rows` | 3 |
| `MIN_AW_PRINTS` | `fdm3-min-aw-prints` | 4 |
| `MIN_AW_FLIPS` | `fdm3-min-aw-flips` | 2 |
| `LTF_5AW_6X_XCROSS_ROWS` | `fdm3-ltf-5aw-6x-xcross-rows` | 1 |
| `LTF_5AW_6X_MIN_AW_PRINTS` | `fdm3-ltf-5aw-6x-min-aw-prints` | 10 |
| `LTF_5AW_6X_MIN_AW_FLIPS` | `fdm3-ltf-5aw-6x-min-aw-flips` | 5 |
| `A_WS1_WS6` | the oracle's A ws1-ws6 button (MY name) | 1 |
| `A_WS7_WS15` | the oracle's A ws7-ws15 button (MY name) | 0 |
| `SMALL_TRADE_MAX_TOEXF` | `fdm3-small-trade-max-toexf` | 2 |
| `INFENCE_EDGES` | his `+4` / `-4` ranges on `fdm3-infence-power` (MY name for the knob) | 8, 23, 28, 38, 62, 73, 77, 92 - banked 1121 |
| `INFENCE_READ` | his 30 s seam, *"it should fire at x:25 and x:55"* (MY name for the knob) | closed_prev_30s - banked 1122; his 1121 *"per closed-prev minute"* is off-ruled |
| `EXF_SUFFIX` | his suffix on TO(exf), AW(exf) and -(exf) (MY name for the knob) | 1 - banked 1121 |
| `UNTAG50` | his "-" on the counter side of 50 (his name pending) | 1 - banked 1121 |
| `ORACLE_R_CFG` | his *"K len:6, RSI len:6, stoch range: 9"* (MY name for the knob) | 6,6,9 - banked 1122 with the machine |
| `RED4_LINES` | the lines of his red suffix, *"expand the red colour mech's coverage to include ws2-ws15"* (MY name for the knob) | 2-15 - banked 1122 with the machine; 8-15 on 8794 |

`fdm-20-80-fnc` in `v4_knobs` stays at 20.0. Joe 1115: *"keep it as a fdm3 fence"* — so fdm2 step
1, the reversal population, the handoff walk's candidate test and the re-entry's inside test are
untouched by the 23/77 move.

---

## how the spec arrives

Joe 1114: *"the full spec is huge so I'm teaching you and validating us in chunks"*. Each chunk is
read for holes before anything is built, the holes go back to him as a numbered list, and only his
answers go into these docs. A reading that is mine and not his is labelled MINE wherever it appears.
