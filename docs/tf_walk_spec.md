# The TF2-23 walk

**THE MECHANIC STILL HAS NO NAME.** Joe has called it "the mech" and "the walk". Every filename
and heading for the WALK is a placeholder — rename on his word, do not coin one.

Joe 0910 named the **report** built beside it: `wsf-dtf-v3`. That is the report's name, not the
walk's. §7 covers it. §6 item 6 stays open.

Joe 0909, given as six numbered steps. This doc records the steps, every concretion that had to be
settled to run them, who settled each one, and what is still open.

---

## 1. Joe's six steps, verbatim

> all times are eyeballed and estimated
> starting from 08-25 00:18
> setting dr from ws2Mage oob + ws13m oob
>
> 1. walk forward until ws1r is oob
>    -examples: 00:39, 01:35, 01:59, 03:28, 04:21, 05:09, 06:58
> 2. when ws1r enters oob, scan upwards through TF2-23, and tag the lines that have same dr momentum
>    -the lines must be clean (refer the latest definition of clean/dirty)
> 3. when a tagged line is oob and stalled/sideways, add a timestamped row
>    -locate the next 2 highest TF whose r is inside the fence
>    --print the TF and its r value in column `wk-tf-1` and column `wk-tf-2`, using this format "{TF}:{r value}"
> 4. scan for momentum, in reverse from TF23 to {the oob TF+1}
> 5. walk forward,
> 6. repeat 3,4,5 until the highest TF holding momentum reports an x cross m
>    -the x-cross-m must complete while Mage is closer to 50. eg post x-cross-m values are 0 and 1, and Mage is 12 for dr -1

Superseded by Joe 0909 later the same day: **dr uses ws1Mage, not ws2Mage.**

---

## 2. The rules as built, with provenance

| rule | value | source |
|---|---|---|
| start | 08-25 00:18 | Joe 0909 |
| window | the WALK is contained to 08-25 | Joe 0909, "contain the walk to 08-25" |
| warm-up | verdicts and the clean latch computed from 08-23 00:00 | mine — the latch and the 21-sample verdict need history before 00:18. Joe contained the walk, not the warm-up |
| dr source | ws1Mage AND ws13m | Joe 0909, "replace ws2Mage with ws1Mage" |
| dr rule | both oob on the SAME side; the previous dr holds until that happens | Joe 0909, "both oob, both same side. until that happens, the previous dr value holds" |
| fence | 83 / 17, from `MOMO_FENCE_R` = 17 | Joe 0909 |
| oob | the dr-side boundary — 85 at dr +1, 15 at dr -1 | standing convention |
| clean | a dirty line goes clean when its r is INSIDE the fence and its verdict advances to `momo` or `curl` | Joe 0909, "clean is applied when a dirty line's state advances to momo or curl" + "a dirty line must be inside the fence and converted to momo or curl" |
| clean/dirty instance | NOT the 0731 rpl/exhv2 producer | Joe 0909, "we're not using the rpl logic" |
| momentum-true | verdict `momo` or `curl` from `momo_g_why` at that bar's dr | established |
| stalled/sideways | verdict `sideways` | established |
| advance | the next row needs a HIGHER tagged TF oob + sideways | Joe 0909 |
| exit | the highest CLEAN momentum-true TF has its x cross its m, with Mage strictly closer to 50 than both x and m | Joe 0909, "yes" to clean-only |
| x-cross-m direction | dr -1 x crosses OVER m; dr +1 x crosses UNDER m | Joe 0909, "if dr -1, x crosses over" |
| restart | the walk restarts after the x-cross-m event; walks chain and do not overlap | Joe 0909, "the walk re-starts after the x-cross-m event" |
| xwob, x-cross-m | 12 bars = 60 s | Joe 0909, "increase the x cross m wob to 12" |
| xwob, everything else | 6 bars = 30 s | Joe 0909, "that xwob change was specific to x cross m only" |

### The Mage condition

Joe's example — "post x-cross-m values are 0 and 1, and Mage is 12 for dr -1" — was **withdrawn**
by him 0909 ("I accidentaly infered an inverted view of the logic because of my incorrect
(inverted) values for x and m"). The condition is built from his words, not the numbers:
`|Mage - 50| < |x - 50|` AND `|Mage - 50| < |m - 50|`, on the crossing line's own timeframe.

### The clean latch

Clean **latches**. This is MINE, not Joe's. Step 3 requires a tagged (clean) line to be **oob**;
tagging requires clean; clean requires **inside the fence**. A line cannot be inside the fence and
oob at the same instant, so a live state test makes step 3 unreachable. The latch is the only
reading under which step 3 fires at all.

No dirtying event was ever specified, so the latch is monotonic. **Measured consequence:** all 22
timeframes are clean at 00:18 and still clean at 08-26 00:00. Step 2's clean requirement and the
clean-only exit therefore include and exclude nothing in every run to date.

---

## 3. What is still MINE and unruled

| item | what I did | the alternative reading |
|---|---|---|
| **step 1 discretisation** | "walk forward until ws1r is oob" is a state. I take the rising edge of a 6-bar hold, one walk per edge | the first bar ws1r is beyond the boundary, no hold |
| **the clean latch** | latches, never resets | a live state test — which makes step 3 unreachable |
| **mid-walk dr flip** | nothing applied; the walk continues and each row carries the dr at its own bar | abort the walk, or re-tag |
| **strict vs inclusive oob** | ws1r's trigger uses `cross_wob`, which is strictly beyond the boundary. The tagged-line oob test in step 3 uses at-or-above | make them consistent either way |

Joe's eyeballed step-1 examples against the built construction, 08-25:

| Joe's estimate | built | note |
|---|---|---|
| 00:39 | 00:39:45 | walk 1 |
| 01:35 | 01:35:25 | walk 2 — appeared only after the ws1Mage dr change |
| 01:59 | none | nearest is walk 2's exit at 01:59:00 |
| 03:28 | 03:28:35 | walk 3 |
| 04:21 | 04:20:25 | walk 4 |
| 05:09 | 05:09:15 | walk 5 |
| 06:58 | 06:48:25 | walk 7 |

Both are measurements. The disagreement is open.

---

## 4. Lines the mechanic needs

`r`, `x`, `m`, `Mage` at every timeframe 2..23, plus `ws1r` and `ws1Mage`, plus `ws13m`.
The registry (`vw_indicator_configs_live`) carries TF1-10, 12, 15 and 22 only; the rest were built
by `build_wsf_role_lines.py` at the wsf role specs. 92 role lines are cached at the 09-08 key.

Momentum verdicts are cached per dr source — `st_0823_0826_<dr source>.npz`. **The dr source is
part of the key.** Verdicts are computed at each bar's dr, so a different dr rule is a different
verdict set; keying on the bar range alone silently reuses the wrong verdicts.

---

## 5. Results to date, 08-25, dr from ws1Mage + ws13m

| item | value |
|---|---|
| ws1r oob confirming edges | 47 |
| walks after chaining | 24 |
| exit events on 08-25 | 71 |
| rows | 8 |
| walks emitting 2 rows | 1 (walk 16) |
| dr flips on 08-25 | 31 |
| clean timeframes at 00:18 | 22 of 22 |

The eight rows:

| walk | row utc | dr | oob tf | r | sw bars | wk-tf-1 | wk-tf-2 | hi clean mom tf |
|---|---|---|---|---|---|---|---|---|
| 2 | 01:54:20 | -1 | 5 | 1.12 | 1 | 11:22.01 | 12:18.91 | 16 |
| 5 | 05:16:10 | +1 | 4 | 87.03 | 1 | 6:81.30 | 7:66.14 | 8 |
| 10 | 09:43:20 | +1 | 4 | 90.68 | 1 | 6:79.31 | 7:65.74 | 18 |
| 16 | 17:46:40 | +1 | 3 | 87.15 | 1 | 5:77.82 | 6:72.20 | 13 |
| 16 | 17:56:05 | +1 | 4 | 96.48 | 1 | 5:82.39 | 8:80.75 | 14 |
| 20 | 20:47:35 | -1 | 2 | 4.17 | 1 | 4:33.83 | 5:43.69 | 22 |
| 21 | 22:17:05 | +1 | 6 | 95.21 | 1 | 11:74.96 | 12:72.92 | 19 |
| 24 | 23:46:10 | -1 | 4 | 13.59 | 1 | 6:20.73 | 8:20.37 | 11 |

Every row has a sideways run of exactly 1 bar = 5 s.

**Joe 0909, on the first four rows:** *"the mech is starting to shape up - the first 4 rows are
exiting at good times"*. That is his read, and it stands.

**Joe 0909, on walk 5's exit at 05:28:40 tf 13:** *"the x-cross-m exit fires too early. it's not a
fault in the build - it is a new mechanism that I've been expecting to build"*. The mechanism does
not exist yet.

### Superseded configurations

Numbers from these are void, not context:

| configuration | walks | rows |
|---|---|---|
| dr ws2Mage, x-cross-m wob 2, overlapping walks | 47 | 4 |
| dr ws2Mage, x-cross-m wob 12, overlapping walks | 47 | 7 |
| dr ws2Mage, x-cross-m wob 12, chained walks | 23 | 4 |
| dr ws1Mage, x-cross-m wob 12, chained walks | 24 | 8 |

---

## 6. Open

1. Rule the step-1 discretisation. Every walk count and row count depends on it.
2. Name a dirtying event, or the clean test stays inert.
3. Rule what a mid-walk dr flip does. Walk 20 hit one.
4. Rule strict vs inclusive on the oob boundary tests.
5. The mechanic that walk 5's early exit calls for does not exist.
6. Name the mechanic.

---

## 7. wsf-dtf-v3

**Joe named it 0910.** Producer `build_wsf_dtf_v3.py`, table `wsf_dtf_v3`.

One row per (line, dr run): the FIRST bar in that dr run where the line's r is `sideways` AND
outside the fence. Joe 0909: *"keep the first sideways event per dr flip"*.

### Settings

| item | value | source |
|---|---|---|
| window | 08-25 00:00:00 -> 08-28 00:00:00 | Joe 0910 "extend the report to 08-27 (full days)" |
| warm-up | 08-23 00:00 | mine - the 21-sample lattice and the dr latch need history |
| lines | ws5..ws23 | Joe 0910 "increase the max r lines to ws23" |
| dr | ws1Mage AND ws13m both oob, same side, latched | Joe 0909 |
| fence | 25 / 75 | Joe 0910, raised from 30/70 |
| lattice span | 10 minutes, every line | **FITTED** |
| momo_slope_min | 0.4 | **FITTED** |
| mask sequence | gcws30 then ws1..ws18 - 19 tags, 18 pairs | Joe 0910 |
| HTF momentum | ws120, ws90, ws60, ws45, ws30, at BOTH the banked banks and the fitted settings | Joe 0910 "Both, as two columns" |
| knob set | `v3_sp10_sl0.4_f25.75_drws1Mage.ws13m_bv1` | in `wdv_knobs`, first part of the unique key |

`wdv_line` is an **INT holding the timeframe**, not a line name - `WHERE wdv_line = 7`, never
`'ws7r'`, which matches nothing and returns an empty result rather than an error.

### THE SPAN AND THE SLOPE FLOOR ARE FITTED, NOT MEASURED

Both were chosen by sweeping until ws7r read `sideways` at Joe's eyeballed ~05:36 on 08-25.
Joe 0910 selected two rows from that sweep: *"these 2 line's feel less like fitting, and the
timing is close enough"*. A knob chosen by scoring against Joe's label is fitted, and must be
re-declared as fitted every time it is quoted. Nothing anchors either number to a mechanism.

The extended test Joe set for them: *"the extended test will be to show the sideways moment on
ws9 and ws10. both should have fired before ~05:55"*. Both did, and the banked table carries them
in dr run 5:

| line | banked utc | r | note |
|---|---|---|---|
| ws7r | 05:37:35 | 88.4 | Joe eyeballed ~05:36 - this is the knob's own target |
| ws10r | 05:40:00 | 87.1 | before ~05:55 |
| ws9r | 05:51:15 | 89.0 | before ~05:55 |

ws7r lands 95 s after Joe's eyeball, not on it. The sweep was scored against the sideways verdict
alone; this row additionally requires r outside 25/75, so the first qualifying bar is later.

### The mask mech

`build_wsf_event_mark.sign_mask`. One character per ADJACENT PAIR in the sequence: `+` the lower
timeframe's Mage is above the higher's, `-` below, `0` equal, `.` a line is missing.
`flip_report.py`, which filled `wsf_momo_flip_rep`'s mask columns, is ABSENT from the repo;
`build_wsf_event_mark` is the surviving implementation.

### Result, first run

| item | value |
|---|---|
| rows | 565 |
| span | 08-25 00:00:00 -> 08-27 23:12:10 |
| distinct lines | 19 |
| dr runs carrying rows | 61 of 66 in the window |
| top_mom_tf = 0 | 112 rows, all carrying a prev_mom |
| htf_bank non-null | 418 |
| htf_fit non-null | 48 |
| build time | 660 s |

`htf_bank` names at least one momentum-true line on 418 of 565 rows; `htf_fit` on 48. The
10-minute span reads those five lines as momentum-true far less often than their own banked
spans do.

### Joe's reads standing against this report

- 0910: *"so far, I don't think we're fitting"*
- 0909: *"the mech is starting to shape up - the first 4 rows are exiting at good times"*
- 0909: *"the x-cross-m exit fires too early. it's not a fault in the build - it is a new
  mechanism that I've been expecting to build"*
- 0910: *"I was expecting ~9 events for each TF"* - under the first-per-dr-run rule the lines
  produce 4 to 7 per 8 hours against a structural ceiling of 8 dr runs. Open.
- 0910: *"at 00:42, that should be TF19, TF22, or TF23"* - measured at three spans and at
  momo_config v0 and v1; none reads those three as momentum-true at that bar. Open.

---

## 8. The Mage-crosses-boundary signal

**THIS MECHANIC HAS NO NAME.** Joe 0910: *"this new mech doesn't have a specific job at present"*.
`build_mage_boundary_signal.py`, table `mage_boundary_signal`, column prefix `mbs_` — every one of
those is a PLACEHOLDER built from Joe's own words. Rename on his word; do not coin one.

Joe 0910 passed it: *"that's the best outcome - bank it and add to the spec"*.

### The row

One row per (`wsf_dtf_v3` row, mode). The wsf_dtf_v3 row is the HAND-OFF — its bar and its dr.
From that bar:

1. walk forward, **no cap**, to the first bar ws1Mage's consecutive-oob run reaches 3 bars = 15 s.
   oob is the dr-side boundary: 85.0 at dr +1, 15.0 at dr -1.
2. at gate `rev`, find the first **ws1Mage reversal** at or after that bar — `_mage_rev(ws1Mage, 2)`,
   2 consecutive same-direction 5 s bars. At gate `off` this step is skipped.
3. the SIGNAL is the first bar **strictly after** the anchor (the reversal at `rev`, the dwell bar
   at `off`), where gcws{30|15}Mage crosses the same boundary in the dr direction — dr +1 crosses
   DOWN through 85.0, dr -1 crosses UP through 15.0.
4. no confirmation hold on that crossing.

### Provenance

| item | value | source |
|---|---|---|
| hand-off population | every `wsf_dtf_v3` row at `v3_sp10_sl0.4_f25.75_drws1Mage.ws13m_bv1` | Joe's three examples are all rows of that table |
| dr | the source row's own `wdv_dr` | from the row |
| ws1Mage oob dwell floor | 3 bars = 15 s | Joe 0910 *"ws1Mage needs to be oob for longer than the 03:29:20 dwell"*. **The floor value is MINE** — that dwell measured 2 bars = 10 s, so 3 bars is the smallest satisfying run. Any larger floor also satisfies him and moves every timestamp |
| dwell counted through bars before the hand-off | yes | **MINE.** A line already oob on arrival satisfies the floor at the hand-off bar itself |
| boundary | 85.0 / 15.0, live from `optimus9_system` | standing |
| crossing direction | dr +1 crosses under its target, dr -1 crosses over | the settled x-cross rule. It is also the out-of-bounds -> in-bounds direction `gcws30b` uses in `build_ws_fin` and `emit_ws_gated` |
| confirmation hold | none | Joe was offered one 0910 and did not take it |
| signal strictly after the dwell bar | yes | **MINE.** It is what reproduces the three timestamps Joe read |
| modes | `g30` = gcws30 lines, `g15` = gcws15 lines | Joe 0910 *"add a mode that uses gcws15 in place of gcws30, to make the signals more surgical"*. ws1Mage and the boundary are the same in both |
| gates | `off` = no reversal step, `rev` = the signal must follow one | Joe 0910 *"apply the first two items"*. Both banks are kept |
| reversal | `_mage_rev(ws1Mage, 2)` — 2 consecutive same-direction 5 s bars | Joe 0910 *"use a reversal wob of 2 for ws1Mage"* |
| reversal at or after the dwell bar | yes | **MINE.** Joe gave no rule on where the reversal sits relative to the dwell |
| reversal direction | not filtered — an up-turn and a down-turn both count | **MINE.** Joe said "ws1 Mage reversing" and never ruled on direction |

### The reversal step, and how little it filters

**MEASURED:** `_mage_rev(ws1Mage, 2)` fires **360,738** times on the cache's 1,632,960 bars — one
every 4.5 bars, one every ~23 seconds. A step that only requires "a reversal" filters almost
nothing. It moved 47 of 565 hand-offs at `g30` and 65 of 565 at `g15`, and none of the three
hand-offs Joe read.

### STILL HELD — the gcws15 x-cross-m 15-second lookback

Joe 0910: *"I'm not sure about lookback direction - expand on it please"*. Not applied, not banked.

**A CORRECTION TO WHAT WAS WRITTEN HERE BEFORE.** The earlier note called the split "cross within
15 s after the reversal" against "look back 15 s from the cross". Those are the same condition
described from the two ends, not two readings. The real split is which event LEADS, and it sits
inside Joe's own two sentences:

| reading | window | which event leads | Joe's words it fits |
|---|---|---|---|
| cross follows the reversal | cross bar in [reversal, reversal + 15 s] | ws1Mage turns, then gcws15 crosses | *"ws1 Mage reversing, **followed by** gcws30 x cross m"* |
| cross precedes the reversal | cross bar in [reversal − 15 s, reversal] | gcws15 crosses, then ws1Mage turns | *"inside a **lookback** period of 15 seconds **from** the ws1Mage's reversal"* |

Both are causal. Both use 15 s = 3 bars. Measured over all 565 hand-offs at `g30`, against the
ungated reversal step:

| gate | signals | no signal | mean min | median min | same as ungated |
|---|---|---|---|---|---|
| every reversal counts | 565 | 0 | 24.69 | 11.00 | 565 |
| cross follows the reversal | 565 | 0 | 25.27 | 12.67 | 471 |
| cross precedes the reversal | 565 | 0 | 25.22 | 12.00 | 520 |
| cross either side | 565 | 0 | 24.78 | 11.50 | 557 |

Neither reading loses a hand-off. "Cross follows" moves 94 of 565; "cross precedes" moves 45. The
three hand-offs Joe read are identical under all four, so they cannot separate the readings.

### The three hand-offs Joe read

| hand-off | dr | mode | dwell met | signal | +min | Mage at the signal |
|---|---|---|---|---|---|---|
| 00:45:30 | +1 | g30 | 00:45:30 | 00:49:10 | 3.67 | 84.60 |
| 00:45:30 | +1 | g15 | 00:45:30 | 00:48:00 | 2.50 | 84.93 |
| 01:50:00 | -1 | g30 | 01:50:00 | 01:54:35 | 4.58 | 21.85 |
| 01:50:00 | -1 | g15 | 01:50:00 | 01:51:20 | 1.33 | 17.22 |
| 03:24:00 | +1 | g30 | 03:31:45 | 03:33:50 | 9.83 | 83.07 |
| 03:24:00 | +1 | g15 | 03:31:45 | 03:33:20 | 9.33 | 84.38 |

The g30 column reproduces the three timestamps Joe passed. At gate `rev` all six rows keep the
same signal; the reversals they run through are 00:45:35, 01:50:05 and 03:32:10.

### Result, first run

| item | g30 off | g30 rev | g15 off | g15 rev |
|---|---|---|---|---|
| knob set | `mb_g30_dw3_hold0_srcv3` | `mb_g30_dw3_hold0_rev2_srcv3` | `mb_g15_dw3_hold0_srcv3` | `mb_g15_dw3_hold0_rev2_srcv3` |
| rows | 565 | 565 | 565 | 565 |
| hand-offs with no signal | 0 | 0 | 0 | 0 |
| signal minutes, min | 0.08 | 0.17 | 0.08 | 0.17 |
| signal minutes, mean | 24.30 | 24.69 | 23.88 | 24.28 |
| signal minutes, max | 219.17 | 219.17 | 218.92 | 218.92 |
| hand-offs moved by the reversal step | - | 47 | - | 65 |

The earlier two-column figures, kept for the record:

| item | g30 | g15 |
|---|---|---|
| knob set | `mb_g30_dw3_hold0_srcv3` | `mb_g15_dw3_hold0_srcv3` |
| rows | 565 | 565 |
| hand-offs with no dwell | 0 | 0 |
| hand-offs with no signal | 0 | 0 |
| signal minutes, min | 0.08 | 0.08 |
| signal minutes, mean | 24.30 | 23.88 |
| signal minutes, max | 219.17 | 218.92 |
| mean boundary crossings, hand-off to signal | 6.07 | 9.56 |
| hand-off span | 08-25 00:00:00 -> 08-27 23:12:10 | same |

Every hand-off produced a signal in both modes. The g15 mode fires earlier at all three of the
hand-offs Joe read, and its mean over all 565 is 0.42 minutes earlier than g30's.

### Open

1. Name the mechanic.
2. Rule the ws1Mage reversal DIRECTION — an up-turn and a down-turn both count today.
3. Rule which event leads in the 15-second lookback. Held on Joe 0910: *"I'm not sure about
   lookback direction"*.
4. Rule the ws1Mage oob dwell floor. 3 bars = 15 s is the smallest value satisfying Joe's sentence,
   not a value he gave.
5. Joe 0910: *"this new mech doesn't have a specific job at present"* — it consumes wsf-dtf-v3
   hand-offs and emits a timestamp. Nothing reads it.
