# wsf-dtf-v3 — spec

Opened 0911 on Joe's word: *"we're going to begin the v3 spec build"* / *"open a wsfdtfv3 spec
doc"* / *"bank the report's details in the doc, and add a knobs section"*.

Producer `build_wsf_dtf_v3.py`. Table `wsf_dtf_v3`.

This doc is the spec. `docs/tf_walk_spec.md` holds the TF2-23 walk and the Mage-crosses-boundary
signal; the wsf-dtf-v3 material there is the build record, and this doc supersedes it as the spec.

---

## 1. The bands

Joe 0911, verbatim:

> spec: wsf = the lines between ws1 and ws12. sub-wsf = gcws30 to ws4. dtf = ws13 to ws23

| band | lines |
|---|---|
| sub-wsf | gcws30 to ws4 |
| wsf | ws1 to ws12 |
| dtf | ws13 to ws23 |

**sub-wsf and wsf overlap on ws1 to ws4.** That is what Joe wrote; it is recorded as written and
not reconciled.

**ws12 IS THE MAX wsf LINE. ws13 BELONGS TO dtf.** Joe 0911, correcting himself: *"I've made a
mistake: ws13 belongs to dtf, ws12 is the max wsf line. the wsf-model-report shows ws1..ws12"*.
This agrees with the code, which has held it since Joe 0826 (*"wsf is limited to TF12"*):
`build_wsf_line_bar.py:57`, `build_wsf_bar_tf.py:56` and `report_wsf_bar.py` are all
`range(1, 13)`. There is no ws13 anywhere in the wsf chain and none is wanted.

### The wsf-model-report

`report_wsf_bar.py` — THE wsf-model-report, format named and fixed by Joe 0820. Shows **ws1..ws12**,
one row per timeframe. Its source tables are `wsf_bar_tf` and `wsf_line_bar`; it recomputes nothing.

`wsf_setup_board` is the BANKED wsf-model-report and carries ws1..ws8 only, 32 rows - a narrower
slice than the report itself prints.

| chain step | producer | window built |
|---|---|---|
| `wsf_line_bar` | `build_wsf_line_bar.py` | 08-25 00:00:00 -> 08-28 00:00:00, Joe 0911 |
| `wsf_bar_tf` | `build_wsf_bar_tf.py` | 08-25 00:00:00 -> 08-28 00:00:00, Joe 0911 |

Joe 0911: *"replace that chain (08-04 is no longer needed), and use the live knob set"*. Both
producers read the CACHED .npy line arrays, not `ws_line_bar`, so nothing upstream had to be built.
The 08-04 rows were left in place - both producers delete only rows at their own (win_from, knobs)
key, and the standing rule is no deletes.

**THE LIVE KNOB SET**, from the producers' own constants:

    kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_mkstate_mf17_xw4

| knob | value | producer constant |
|---|---|---|
| k_window | 4 | `kw4` |
| fixed samples | 21 | `fs21` |
| stall n | 6 | `sn6`, `STALL_N` — build_ws_fin.py's value |
| boundaries | 85.0 / 15.0 | `hi85_lo15` |
| r2 min | 0.5 | `r20.5` |
| slope min | 1 | `sl1` |
| arc | 4 | `arc4` |
| level_slack | 13.9 | `sk13.9` — coin-tossed 0731, never swept |
| curl | 0.4 | `cr0.4` |
| momentum kill | state | `mkstate`, `MOMO_KILL` |
| momo fence r | 17 | `mf17`, `MOMO_FENCE_R` — the 83/17 fence |
| momo xwob | 4 | `xw4`, `MOMO_XWOB` |

**THE THREE-MAGE dr MECH IS DROPPED.** Joe 0911: *"drop the threemage dr mech. I'm happy with our
current dr mech"*. Removed from `report_wsf_bar.py` - the footnote, the `ws_line_bar` query that fed
it and the `wsf_facing_dr` / `wsf_dr_lookback` imports. The project's dr is the one in section 2:
ws1Mage and ws13m both out of bounds on the same side, latched.

`report_wsf_bar.py` is re-pointed at the 08-25 window and at the wsf_dtf_v3-matching knob string:

    kw6_fs21_sn6_hi85_lo15_r20.7_sl0.4_arc4_sk13.9_cr0.4_mkstate_mf17_xw4_sp10

**PROVEN, not asserted:** all 371 `wsf_dtf_v3` rows at ws1..ws12 read `sideways` on that bank at
their own bar and dr. 0 misses.

## 2. The dr flip

Joe 0911, verbatim:

> spec: the dr flip is the handoff between wsf and dtf

**As built today:** dr is set when **ws1Mage** and **ws13m** are both out of bounds on the SAME
side, and it LATCHES — the previous dr holds until that condition is met again on the other side.
Joe 0909 set the pair (he replaced ws2Mage with ws1Mage); the boundary is 85.0 at dr +1 and 15.0
at dr -1, read live from `optimus9_system`.

`dr +1` is the high side. `dr -1` is the low side.

**Proposed 0911 and DROPPED the same day.** Joe floated swapping ws1Mage for the ws1Mage-reversal
mech, so the pair would become ws1Mage-rev + ws13m. He withdrew it: *"I'll drop the idea, dr mech
will stay as ws1Mage + ws13m"*. It was never built. The reason it stalled is recorded in §8 — a
reversal returns a TURN, and the rule it would have joined needs both members to have a SIDE.

## 3. The row

One row per (line, dr run): the FIRST bar in that dr run where the line's r reads `sideways` AND
sits outside the fence. Joe 0909: *"keep the first sideways event per dr flip"*.

## 4. Knobs

**THE KNOBS LIVE IN THE DB.** Joe 0911: *"all hard-coded values need to be in the db. create a
config table for our spec"*. Table `wsf_dtf_v3_config`, loader
`optimus9/compute/v3_config.py`, seeder `seed_v3_config.py`. **38 knobs at v1.**

One row per knob, not one wide row - the spec is still forming and a wide table needs a DDL change
per knob. Each row carries its own provenance, which a wide table cannot:

| column | holds |
|---|---|
| `wdc_owner` | `joe` = Joe set it. `mine` = I picked it and he has not ruled it |
| `wdc_fitted` | 1 = the value was chosen by SCORING AGAINST JOE'S LABELS |
| `wdc_in_key` | 1 = it is inside a bank's knob string / unique key |
| `wdc_source` | Joe's words, or file:line |
| `wdc_version` | in the unique key, so a change lands BESIDE the old value |

Reading it:

    from optimus9.compute.v3_config import v3_config
    C = v3_config(db)
    C['momo_span_min']          # 10
    C.fitted('momo_span_min')   # True  -> say so when you quote it
    C.mine_keys()               # ['dwell', 'warm_utc'] -> re-flag them in every report

**At v1: 2 knobs are FITTED** - `momo_span_min` and `momo_slope_min`. **2 are MINE and unruled** -
`dwell` and `warm_utc`.

The table below is the same set, kept readable in the doc. The DB is the source of truth.



Every knob that moves a row. The ones marked **in KNOBS** are inside `wdv_knobs`, which is the
first part of the unique key `(wdv_knobs, wdv_utc, wdv_line)`, so a change lands BESIDE the
existing bank instead of overwriting it.

| knob | value | in KNOBS | source |
|---|---|---|---|
| timeframe range | ws1 to ws23 | yes, `tf1.23` | Joe 0910 *"increase the max r lines to ws23"* then *"add the ws1,2,3,4 r lines to the report"*. It moves rows — `top mom TF` and `prev mom` both scan it |
| lattice span | **10 minutes = the SPAN, every line. The GAP between samples is 30 s** | yes, `sp10` | **FITTED** |
| `momo_slope_min` | 0.4 | yes, `sl0.4` | **FITTED** |
| fence | 25.0 / 75.0 | yes, `f25.75` | Joe 0910, raised from 30/70 |
| dr pair | ws1Mage + ws13m | yes, `drws1Mage.ws13m` | Joe 0909 |
| `momo_config` version | 1 | yes, `bv1` | the banked-bank HTF column |
| x-cross-race hold | 5 bars, a run spanning 20 s | **NO** | `XCROSS_XWOB` in `build_wsf_x_cross`, same value. A different hold OVERWRITES the two backstop columns instead of landing beside them |
| oob boundary | 85.0 / 15.0 | **NO** | live from `optimus9_system` |
| mask sequence | gcws30 then ws1..ws18 — 19 tags, 18 pairs | **NO** | Joe 0910 |
| HTF lines | ws120, ws90, ws60, ws45, ws30 | **NO** | Joe 0910 |
| warm-up | 2026-08-23 00:00:00 | **NO** | mine — the 21-sample lattice and the dr latch need history |
| **ws1mage-rev** reversal wob | **2 steps** = 10 s | not yet in any bank | Joe 0911: *"use these values, reversal:2, boundary:4. both are knobs"*. `jig.WS1MR_REV_WOB` |
| **ws1mage-rev** boundary xwob | **4 bars** — in-bounds must hold 4 bars | not yet in any bank | Joe 0911, same message. `jig.WS1MR_HOLD` |
| **ws1mage-rev** ws1Mage oob dwell | 3 bars = 15 s | not yet in any bank | **MINE.** Joe rejected the 10 s dwell at 03:29:20 and never named a floor. `jig.WS1MR_DWELL` |
| window | 2026-08-25 00:00:00 to 2026-08-28 00:00:00 | **NO** | Joe 0910 *"extend the report to 08-27 (full days)"* |

### THE 10 MINUTES IS THE SPAN, NOT THE GAP

`momo_window(10)` sets the TOTAL SPAN of the momentum lattice to 10 minutes. `MOMO_FIXED_SAMPLES`
is 21, so the GAP between samples is 600 s / 20 intervals = **30 s = 6 bars, at EVERY timeframe**.

`momo_gated.py:130-158`: with `MOMO_FIXED_SAMPLES` at 0 the GAP would be held at `MOMO_STEP_MIN`
and the sample count would float with the window. A positive value fixes the SAMPLE COUNT and
scales the gap instead. At 21 with the span pinned, every timeframe gets the same 30 s gap.

The producer prints it on every line: `lattice 21 points 6 bars apart = 30 s, span 600 s`.

Contrast with the bank's own `k_window` x TF span, which this overrides:

| bank | span | gap |
|---|---|---|
| plain v1, k_window 6 x TF | ws1r 360 s ... ws12r 4,300 s | ws1r 15 s ... ws12r 215 s |
| this bank, fixed 10 min | 600 s at every timeframe | 30 s at every timeframe |

`momo_gated.py:149` notes the consequence: with one fixed gap, the slope floor demands the same
r-per-minute of every timeframe.

### THE SPAN AND THE SLOPE FLOOR ARE FITTED, NOT MEASURED

Both were chosen by sweeping until ws7r read `sideways` at Joe's eyeballed ~05:36 on 08-25. Joe
0910 selected them: *"these 2 line's feel less like fitting, and the timing is close enough"*. A
knob chosen by scoring against Joe's label is fitted. Re-declare it as fitted every time it is
quoted. Nothing anchors either number to a mechanism.

## 4a. The wsf-model-report, as Joe reads it

Joe 0911 rulings on the board, all verbatim:

| item | Joe's ruling |
|---|---|
| the columns he scans | *"the current valuable columns are r value, heading, extrema, extrema dwell (time since last r extrema), verdict, last verdict, last verdict dwell"* |
| stoch / sat / RSI columns | *"these were created for you, but might not be needed now. create the columns and leave them empty"* - they exist in `wsf_bar_tf` and are NULL on all 1,244,184 rows of the 08-25 build |
| weak mage repeating on every row | *"yes, it repeats by design"* - `wbt_weak_mage_tf` is one answer for the bar, printed per line |
| the footnotes | *"the footnotes aren't needed"* - all 129 lines dropped from `report_wsf_bar.py` |
| curl direction | *"for wsf, curl is allowed to fire in both directions"* |
| `wsf-curl mode` | *"I don't know why wsf-curl mode is none. ignore it for now"* - OPEN |
| 50 gate / blocked by 50 | *"I can't recall what the 50 gate and blocked by 50 columns do"* - the answer is below |

### What the 50 gate and blocked-by-50 columns hold

`report_wsf_bar.py:98-105`, the level test inside `momo_core.level_gate()`:

- a line must be on the FAR side of 50 for its direction before momentum can be true
- the gate SLACKENS by up to `level_slack` 13.9 points, in proportion to how cleanly the line
  tracks: `slack = level_slack x r2 x min(1, |slope| / momo_slope_min)`, both read from the bound
  bank
- a line that tracks perfectly can therefore sit 13.9 points the WRONG side of 50 and still pass
- **`50 gate`** prints the level the line actually had to reach at that bar
- **`blocked by 50`** is `yes` when that gate is what turned the verdict to `none`. Joe 0820 on
  ws8r at 07:36:20: *"not over 50 ... therefore momentum = false"*

### THE CROSS BAR AND THE CONFIRM BAR - THE WOB DECIDES, NOT A RULING

A ws1mage-rev event has two timestamps and both are causal:

| bar | what it is | where it is used |
|---|---|---|
| `sig` | the CROSS bar - when gcws30Mage crossed the boundary | a HISTORICAL event's timestamp, eg `wdv_backstop_utc` |
| `sig_conf` | the CONFIRM bar - `sig + boundary_xwob - 1` | the bar the mechanic FIRES on |

**THE wsf-model-report GOES ON THE CONFIRM BAR.** Joe 0911: *"if the differnece is a wob
calculation, is it really a choice?"* It is not. Once `boundary_xwob` is 4,
`sig_conf = sig + 3` is arithmetic. And at the cross bar nothing has fired yet - the in-bounds run
is one bar old; the cross bar is a label computed backwards once the run completes.

At the 08-25 walk: cross 17:12:00, confirm **17:12:15**, and 17:12:15 is where the board goes.

I first called this a choice for Joe. It was not. Recorded because the pattern matters: before
escalating, check whether the alternative is actually reachable.

## 5. The columns

| column | holds |
|---|---|
| `wdv_knobs` | the knob string. First part of the unique key |
| `wdv_utc` | the row bar, exact |
| `wdv_ms` | the same bar in epoch ms, for ordering |
| `wdv_line` | the timeframe whose r went sideways, in minutes. An INT, not a line name — `WHERE wdv_line = 7`, never `'ws7r'` |
| `wdv_backstop_utc` | THE BACKSTOP. The first ws{`wdv_line`} x-cross-race confirmation strictly after the row bar, at the row's dr |
| `wdv_dr_run` | which dr run inside the window, 1-based |
| `wdv_dr` | +1 or -1 at the row bar |
| `wdv_r` | that line's r at the row bar |
| `wdv_top_mom_tf` | highest timeframe in the range that is momentum-true. 0 = none; it is not a timeframe number |
| `wdv_top` | r of `wdv_top_mom_tf`. NULL when it is 0 |
| `wdv_top1` | r of `wdv_top_mom_tf` + 1. NULL when 0 or above ws23 |
| `wdv_top_backstop_utc` | the same backstop mech read off ws{`wdv_top_mom_tf`}. NULL when that is 0. **Column name is MINE** — Joe has not named it |
| `wdv_prev_mom` | `'{TF} {verdict} -{mins}m'`. NULL when `wdv_top_mom_tf` is non-zero |
| `wdv_run_bars` | length of the sideways run this row opens, in 5 s bars |
| `wdv_nx1` .. `wdv_nx4` | r of the next four timeframes ascending, as `'{r} ({TF})'` |
| `wdv_mage_mask` | 18 pairs, gcws30 v ws1 ... ws17 v ws18. One char per ADJACENT PAIR: `+` the lower timeframe's Mage above the higher's, `-` below, `0` equal, `.` missing |
| `wdv_htf_bank` | which of ws120/90/60/45/30 are momentum-true at their own banked banks, eg `'120, 30'` |
| `wdv_htf_fit` | the same five at the report's own 10-minute span and slope 0.4 |

### The backstop mech

`build_wsf_x_cross`'s, verbatim. The race is the FIRST of three to cross — x against its Mage, its
b, or the boundary. `x X r` is stored beside the race in that producer and is not in it. dr +1 the
x crosses DOWN under its target, dr -1 it crosses UP over. x must hold the far side for 5
consecutive bars and must have been on the NEAR side before it crossed; the crossing confirms on
the bar the run reaches 5, not the bar it started.

## 6. The banks

| knob string | rows | lines | dr runs | span |
|---|---|---|---|---|
| `v3_sp10_sl0.4_f25.75_drws1Mage.ws13m_bv1` | 565 | ws5..ws23 | 61 | 08-25 00:00:00 -> 08-27 23:12:10 |
| `v3_tf1.23_sp10_sl0.4_f25.75_drws1Mage.ws13m_bv1` | 654 | ws1..ws23 | 62 | 08-25 00:00:00 -> 08-27 23:12:10 |

The first string carries no `tf` prefix; that absence means ws5..ws23.

## 7. Open

1. **The ws1Mage reversal wob.** Not settled. §9 carries what 2 and 6 measure.
2. **Name `wdv_top_backstop_utc`.** The name and its position after `wdv_top1` are both mine.
3. **The x-cross-race hold is not in the unique key.** A sweep of it overwrites both backstop
   columns.
4. **sub-wsf and wsf overlap on ws1..ws4**, as Joe wrote the bands.

## 8. Why the dr-flip swap stalled — kept as the record, the idea is dropped

The rule today needs both members to have a SIDE: "ws1Mage and ws13m both oob on the same side".
`_mage_rev(ws1Mage, 2)` returns a TURN, not a side: `+1` a down-to-up turn, `-1` an up-to-down
turn, `0` no turn. There is no single obvious mapping from a turn to a side, and the two candidate
mappings are opposites of each other, so the choice changes every dr run in the report.

Joe dropped the idea 0911 rather than rule the mapping.

---

## 9. ws1mage-rev — the mechanic, on the Jig

Joe 0911 named it and put it on the Jig: *"this is the reversal mech that we built. add it to the
Jig, name it ws1mage-rev"*, and *"everything we build must run through the Jig"*.

Producer `ws1mage_rev(g1, sig_mage, hi, lo, dwell, rev_wob, hold, gate)` at
`optimus9/analysis/jig.py:151`, exposed as `jig.causal.ws1mage_rev(...)`. It DELEGATES - the
reversal to `lr_v2._mage_rev`, the boundary cross to the Jig's own `oob_ib_cross`. Nothing is
re-implemented.

Four index arrays per dr: `dwell_ok`, `rev`, `sig` (the cross bar), `sig_conf` (the bar the cross
becomes knowable = cross + hold - 1).

### THE TWO KNOBS, Joe 0911

| knob | value | units |
|---|---|---|
| `WS1MR_REV_WOB` | **2** | STEPS between bars. A run of n steps spans n x 5 s across n + 1 bars, so 2 = 10 s |
| `WS1MR_HOLD` | **4** | BARS in-bounds must hold for the boundary cross to count |

`WS1MR_DWELL` = 3 bars is the third knob in the chain and it is MINE, unruled.

### THE xwob IS NOT LOOKAHEAD - truncation-tested 0911

Joe 0911: *"applying a wob should never impact lookahead"*. Correct, and an earlier claim of mine
that it was lookahead is WITHDRAWN. Recomputing with the tape cut bar by bar, at xwob 4: the
17:12:00 crossing is not reported at a cut of 17:12:05 or 17:12:10, appears for the first time at
17:12:15, and never moves after that. The hold delays KNOWLEDGE; nothing reads forward. `sig` and
`sig_conf` are both causal.

### The walk from the 08-25 17:06:30 dr -1 flip, at reversal 2 / boundary 4

| leg | utc | +s |
|---|---|---|
| dr -1 flip (start) | 17:06:30 | 0 |
| ws1Mage oob dwell met | 17:08:10 | 100 |
| ws1Mage reversal | 17:08:20 | 110 |
| **ws1mage-rev event (cross)** | **17:12:00** | 330 |
| knowable at | 17:12:15 | 345 |

ws1Mage 8.13 at the reversal; gcws30Mage 16.00 at the cross.

### The reversal wob, measured

`_mage_rev(ws1Mage, n)` from `optimus9/analysis/lr_v2.py:272`. Returns per bar: `+1` ws1Mage turned
from falling to rising, `-1` turned from rising to falling, `0` no turn.

**`n` COUNTS STEPS BETWEEN BARS, NOT BARS.** `_mage_rev` runs on `np.diff(line)`, so `n` is the
number of consecutive same-direction steps and the event fires on the step that reaches `n`. A run
of `n` steps spans `n x 5 s` of movement across `n + 1` bars: wob 2 = 10 s, wob 6 = 30 s. A flat
step extends the run rather than breaking it. Boundary-agnostic: it does not require the line to be
outside a fence.

This is the OPPOSITE arithmetic to the x-cross hold, which counts BARS — there a 5-bar run spans
20 s. Do not carry one formula to the other.

Worked example, the 17:19:10 event at wob 6:

| utc | ws1Mage | step |
|---|---|---|
| 17:18:40 | 45.42 | -5.55 |
| 17:18:45 | 47.89 | +2.47 |
| 17:18:50 | 47.89 | +0.00 |
| 17:18:55 | 54.98 | +7.09 |
| 17:19:00 | 57.45 | +2.46 |
| 17:19:05 | 61.14 | +3.70 |
| 17:19:10 | 63.29 | +2.14 |

The up-run starts at 17:18:45 and the 6th step lands on 17:19:10, where the event fires. 17:18:50
is a flat step that extends the run.

**Line identity, checked 0911.** `build_mage_boundary_signal.py` resolves ws1Mage through the
registry (`OVR['ws1Mage']`); the wob tests resolve it through the wsf mech role spec
(`override(60, *SPEC['Mage'])`). Both give cache key `25cfa2ad06f04c39a0b7` — the same array.

Joe 0911: *"we need a wob for the reversal. test with wob 6"*.

### Density across the whole cache, 1,632,960 bars

| wob | reversals | one every |
|---|---|---|
| 2 | 360,738 | 4.5 bars = 22.6 s |
| 6 | 66,650 | 24.5 bars = 122.5 s |

wob 6 keeps 18.5% of what wob 2 fires.

### The 08-25 17:06:30 test

The dr -1 flip at 17:06:30 — ws1Mage 14.06 and ws13m 12.81, both below 15.0. The dr -1 run ends at
the next flip, 17:19:45.

| setting | next reversal after the flip | gap |
|---|---|---|
| wob 2 | 17:07:00 | 30 s |
| wob 6 | 17:19:10 | 760 s |
| **Joe's read** | **~17:09** | **~150 s** |

Neither wob lands on Joe's read. At wob 2 there IS a reversal at 17:09:00, but it is the 9th of 20
in that stretch, not the first. At wob 6 there is no reversal at all between 17:06:30 and 17:19:10.
wob 6 produces 2 reversals in the whole 13.25-minute dr -1 run, and one of them is the dr flip bar
itself.

The disagreement between Joe's ~17:09 and both measured values is OPEN. Neither is ranked.
