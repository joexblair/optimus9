# wsf-dtf-v3 — spec

Opened 0911 on Joe's word: *"we're going to begin the v3 spec build"* / *"open a wsfdtfv3 spec
doc"* / *"bank the report's details in the doc, and add a knobs section"*.

Producer `build_wsf_dtf_v3.py`. Table `wsf_dtf_v3`.

This doc is the spec. `docs/tf_walk_spec.md` holds the TF2-23 walk and the Mage-crosses-boundary
signal; the wsf-dtf-v3 material there is the build record, and this doc supersedes it as the spec.

---

## 0. JOE'S ACTION POINTS (AP)

> **REMINDER — Claude: whenever you open this doc, tell Joe he has open action points and list the
> ones still open. Joe 0912 asked for this reminder to sit here so it reaches him.**

Joe owns these. They are not tasks for me and I do not close them - Joe does.

| # | status | action point |
|---|--------|--------------|
| AP-1 | open | review: the 10 minutes is the SPAN of the momentum lattice, not the gap. At 21 fixed samples the gap is 30 s = 6 bars, at EVERY timeframe |
| AP-2 | open | is the mid-zone fence the final outcome, or is there a better method available |
| AP-3 | open | which div tf belongs to which htf? |

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
`optimus9/compute/v3_config.py`, seeder `seed_v3_config.py`. **44 knobs at v5.**

**v5, 0915 — one knob added, no value changed.** `momo_expiry.return_bars` = 3, the hold on the
expiry's return cross (§18.1). Joe: *"I agree with your natural anchor, n can be 3 and swept (add
the knob)"*. The units are bars, and that reading is MINE.

**v4, 0914 — one knob added, no value changed.** `handoff.ride_tf_hi` = 4, the ride ceiling,
deliberately separate from `band_subwsf` and `band_wsf_hi` so a sweep can move it alone (19.2).

**v3, 0914 — four knobs added, no value changed.** Two for the ride end (17.2a) and two for the
momentum expiry (§18). Joe set all four values; the labels and both section names are MINE under
his 0913 delegation: *"I'll pass the knobs to you for labelling"*. v1 and v2 stay banked.

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

**At v3: 2 knobs are FITTED** - `momo_span_min` and `momo_slope_min`. **2 are MINE and unruled** -
`dwell` and `warm_utc`. The four added at v3 are Joe's values under my labels, so they are `joe`.

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
| **ride end** `mage_dwell` | **12 bars = 60 s** | not yet in any bank | Joe 0913: *"oob (15/85) with a dwell of {knob:12} (1 minute)"*. ws4Mage's run on the dr side of 15/85 |
| **ride end** `r_wob` | **3 steps = 4 bars = 20 s** | not yet in any bank | Joe 0913: *"r-momo-fence, wob {knob:3}"*. ws4r's run outside momo-fence-r on the dr side |
| **momo expiry** `fence` | **50** = a 50:50 fence | not yet in any bank | Joe 0914: *"make the fence 50:50"*. Fence knobs are 100 minus the closest edge. SEPARATE from the flat-run signal's 40/60 |
| **momo expiry** `xwob` | **5 bars = 25 s** | not yet in any bank | Joe 0914: *"yes, xwob5"*. Units BARS, matching `momo_xwob` and `boundary_xwob`, the two xwob rows already banked |

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

---

## 10. Spec context — what `r` is, Joe 0911/0912

Joe's words, and the frame everything below reads through.

### `r` is ONE line, zoomed

> *"`r` is a single contiuation that we 'zoom-in on' by referencing it across diminishing TFs:
> ws1/gcws30 are the most granular view of `r`, therefore the LTF `r`'s position on the board tells
> us its immediate future (generally, the next 5 minutes)"*

- ws1r and ws12r are not twelve different lines. They are one continuation sampled at twelve
  magnifications
- so the board is not a set of independent votes. The LTF rows are the near future of the HTF rows
- the horizon Joe gives for the granular view is **roughly the next five minutes**

### The first task at a dr flip

> *"at the dr flip, the first task is to assess where the walk is starting from. to do this, we look
> at the r line as a whole"*

Not "is there a signal" — **where on the continuation are we standing**. Read the board top to
bottom before reading any single row.

### r turning away from dr means pxs pivoted

> *"when r is low on the board and then turns away from its dr (ie r value starts to increase), this
> tells us that pxs has pivoted. the report will show this inidcated in changes to `verdict`,
> `heading`, so-on, with the added context of the walk's forward motion. the model-report will
> evolve the values for the important columns per-bar"*

- `low on the board` + `r rising at dr -1` = the pivot has happened
- it shows in `verdict` and `heading` before it shows anywhere else
- the report is a PER-BAR evolution, not a snapshot

### Waning versus reversing

> *"when you understand the purpose of `r`, then we can review `verdict` against `last-verdict`, in
> the context of `last-verdict dwell`, to learn if momentum is waning or reversing"*

The three columns are one reading, never three:

| you have | it means |
|---|---|
| `verdict` = none, `last-verdict` = momo or curl, dwell LARGE | the momentum is long gone — waning |
| `verdict` = none, `last-verdict` = sideways, dwell LARGE | it already flattened and then emptied — spent |
| `verdict` = momo, `last-verdict` = none, dwell SMALL | it just arrived — loading |

### AN `r` LINE WITH MOMENTUM PULLS THE TF ABOVE IT

Joe 0912, on ws2r sitting at 8.88 while ws1r had already turned:

> *"I guarantee that ws2 will lift in the upcoming bars, and here's why: an `r` line that has
> momentum will organically lead (or pull) the TF immediately above it"*

- the lead is STRUCTURAL, not coincidence. ws1 is the first minute of ws2's two
- so a split between adjacent lines is not a disagreement — it is a **lag**, and the direction of
  travel belongs to the faster line
- this reverses how a split should be read. The granular line is not an outlier to be discounted;
  it is the instruction the line above has not executed yet

---

## 11. Ingredients — my own learnings

Observations I have made from the data, each with the bars and values that produced it AND the
generalised shape. **Joe 0912: *"print the time's and values that you've observed, but also describe
the same observations with generalisation so that you don't get hyper-focussed on exact
values/exact differences ... you're modelling human behaviour, so no two sets of values will ever
be exactly the same."*** The numbers are the evidence; the shape is the ingredient.

### Why the shape and not the number — what StochRSI is measuring

StochRSI is the position of RSI inside RSI's own recent range: a momentum reading of a momentum
reading. What that measures about the people in the tape:

| reading | the crowd state it reflects |
|---|---|
| high in its range | FOMO, euphoria, chasing |
| low in its range | panic, capitulation |
| cooling back off an extreme | the crowd is spent — the signal fires HERE, not at the extreme |

That is why the ingredients below are written as shapes. A capitulation recurs; the number it
bottoms at never does. It also explains Joe's mechanics from underneath: `extrema dwell` is *how
long since the crowd's most extreme moment*, and `r turning away from its dr` is *the crowd
finishing*.

### INGREDIENT 1 — at a dr flip, the board can already be spent

**Observed, 08-25 17:06:30, the dr -1 flip:**

| what | value |
|---|---|
| lines reading `none` | 9 of 12 |
| lines reading `away` | ws2, ws4, ws5, ws6, ws7, ws8, ws12 |
| oldest extrema dwells | ws12 2525 s, ws4 2290 s, ws7 2290 s, ws5 1795 s, ws6 1565 s |
| lines `blocked by 50` | ws4, ws5, ws6, ws7 — r 54.99 to 66.34 against dr -1 |
| lines with momentum | ws3, and ws10/ws11 at dwell 5 s / 0 s |

**The shape:** a dr flip is a statement about two Mage lines, not about the board. The board it
lands on may have already made and left its move. The tells, in order of how much they carry:

1. most lines reading `none` — no momentum anywhere to inherit
2. `heading` = away on the majority, with `extrema dwell` in the **tens of minutes** rather than
   seconds — the extremes are old
3. the mid band sitting on the WRONG side of 50 for the new dr, with `blocked by 50` set — those
   lines are barred from momentum by position alone
4. whatever momentum exists having a **tiny** `last-verdict dwell` — it has just arrived and has
   established nothing

### INGREDIENT 2 — momo -> sideways -> none, with the dwell stacked by timeframe, is WANING

**Observed at the same bar:**

| line | last verdict | dwell |
|---|---|---|
| ws4 | momo | 2295 s |
| ws5 | sideways | 1555 s |
| ws6 | sideways | 1110 s |
| ws7 | sideways | 690 s |
| ws1 | curl | 410 s |
| ws2 | momo | 255 s |

**The shape:** the sequence `momo` then `sideways` then `none` is the decay of one impulse, not
three unrelated states. Read the dwells across timeframes, not per line:

- dwell **increasing** with timeframe = the impulse died at the fast end first and the slow lines
  are still holding the corpse. That is **waning**
- the same three states with dwells that are all SHORT and not ordered by timeframe = the board is
  changing its mind, not finishing. That is a transition, and it is not the same ingredient
- a large dwell on `sideways` is more final than a large dwell on `momo` — flattening first, then
  emptying, is a completed move

### INGREDIENT 3 — the granular line's turn precedes the board's, by about its own timeframe

**Observed, ws1r and ws2r across the 17:06:30 flip to the 17:12:15 event and beyond:**

| utc | what happened |
|---|---|
| 17:07:00, 17:07:15, 17:07:45 | ws1r printed three `curl`s, each dying within 5 s |
| 17:09:00 | ws1r `momo` at r 15.31 — its lowest r of the window |
| 17:09:20 | ws1r `momo` again at r 17.34 |
| 17:10:00 | ws1r `momo` -> `none`, r jumped 17.34 -> 39.10 in one step |
| 17:12:05 | ws2r bottomed, r 8.12, extrema 7.02 |
| 17:12:15 | the ws1mage-rev event. ws1r 42.48 `away`; ws2r 8.88 still low |
| 17:20:00 | ws1r 97.53, ws2r 65.74 |

**The shape:** Joe's lead/pull rule, seen once end to end.

- the faster line turns first; the line above it follows. Here the turn was ws1 at 17:10:00 and
  ws2 at about 17:12:05 — a lag on the order of **ws2's own timeframe**, not a fixed number of bars
- **repeated short-lived curls at the granular end are the crowd testing the extreme.** Three curls
  dying inside 5 s each preceded the real turn by about two minutes. Treat a cluster of instant
  curls as pressure building, not as failed signals
- the turn itself is not gradual. ws1's r moved more in one step than in the preceding minute, and
  the verdict died on the same bar. **A large single-step r move with the verdict collapsing is the
  pivot**, and it reads clearer than any threshold on r's level
- a split between adjacent lines at an event is a LAG. The faster line holds the instruction

### INGREDIENT 4 — a signal can fire while the granular view already disagrees

**Observed at the 17:12:15 ws1mage-rev event:** six lines read `momo` toward the low — ws3, ws4,
ws5, ws6, ws10, ws12 — with `blocked by 50` cleared on all four lines that had been barred at the
flip, as their r came back down through 50 (ws4 66.34 -> 40.70, ws5 61.08 -> 51.71). At the same
bar ws1r read 42.48 `away` with its momentum 135 s dead.

**The shape:** the mid band re-loading and the granular line leaving are not contradictory
readings, they are **different points on the same continuation**. The board describes where the
move has been; the granular line describes where it is going. When a signal fires on the board's
state while the granular line has already turned, the signal is late by construction — the amount
it is late by is the lag in Ingredient 3.

**This is not yet ruled and it is not yet scored.** It is one event. What would settle it is the
same board read at many ws1mage-rev events, with the granular line's heading recorded beside each.

### The standing caution on this section

Every ingredient here comes from ONE dr run on ONE day. They are hypotheses with a worked example
attached, not measured rates. Joe 0912: *"it's all science, testing hypothesese."* When an
ingredient is tested across a population, that result belongs here too — replacing the shape, not
decorating it.

---

## 12. Spec context — the divergence mech, Joe 0912

### The four steps, Joe's verbatim

> *"whenever a divergence test is requested*
> *-1. capture the current value of r, capture the current dr*
> *-2. look back to find the r extrema which is facing the opposing step 1's dr, and on the other*
> *side of 50 from the r value taken in step 1*
> *-3. look back from step 2, find the r extrema that is on the same side as step 1's dr. this r*
> *extrema is the floater, and the step 1 r value is the anchor*
> *-4 feed the andchor and floater timestamps and vaules into the divergence machine*
> *eg if 08-25 17:34 is the anchor (dr 1), the step 2 lookback will find a dr -1 extrema at*
> *~17:32:30, and the step 3 lookback will find the dr 1 floater at ~17:29"*

### Step 3 is a BACKWARD block loop, Joe 0912

> *"step 3 then looks back to 17:27, 17:22, etc (in one code loop) until it has proven that it has*
> *gone past the extrema. the extrema and the timestamp are then apparent"*

- the loop starts at the step-2 pivot and walks BACKWARD in blocks of 5 minutes (60 bars at the
  5 s grid)
- each block yields its own highest r (for a dr +1 anchor); the loop keeps the running highest
- the loop stops at the first block that adds no new high — that block proves the top has been
  passed
- every bar the loop reads is already in the past at the anchor bar, so there is no delay and no
  future bar is required

**Worked example, gcws30r, anchor 08-25 17:34:00, dr +1, pivot 17:32:40:**

| block | from | to | highest gcws30r in block | at | running highest | at | new high? |
|-------|------|----|--------------------------|----|-----------------|----|-----------|
| 1 | 17:27:40 | 17:32:40 | 90.65 | 17:29:30 | 90.65 | 17:29:30 | yes |
| 2 | 17:22:40 | 17:27:40 | 69.48 | 17:27:30 | 90.65 | 17:29:30 | no — loop stops |

- floater 17:29:30, gcws30r 90.65, close 0.18147
- anchor 17:34:00, gcws30r 70.73, close 0.18423
- osc delta −19.92, close delta +0.00276 → bearish

### WHY THE LOOP MUST STOP AT THE PREVIOUS BUMP, Joe 0912

> *"divergences rely on the previous peak for comparison against the current moment. when k is*
> *printing a smaller vlaue than the last k 'bump', we know that the momentum is not as strong"*
> *"the same goes for a trough, if the anchor is also a trough"*

- the comparator is the PREVIOUS bump, not the highest bump in history
- searching further back for a bigger peak substitutes an older bump and breaks the comparison
- the stop-on-first-quiet-block rule is what makes the loop return the previous bump
- the anchor being a trough is the mirror image: compare against the previous trough, and a
  higher trough against a lower price low is the bullish reading

**This is already in the 0711 research survey** (`docs/o9-live/divergence_research.md`), in two
places:
- Axis B option 1: *"Peak-to-peak / trough-to-trough (classic) — compare the two most recent
  same-type extremes: price HH & osc LH → bearish"*
- Finding 2: *"reading `s2r`+`s4r` at the turn vs the previous same-kind turn"*

### Open — not decided, not coded

- the loop's termination test on a TIE (a later block equalling the running high)
- which bar of a flat top is the extrema when consecutive bars hold the same r

CLOSED 0921, see 12.1: the empty-block question, and the 60 bars now banked as
`anchor_floater.block` at config v9.

---

## 12.1 STEP 2 REPLACED, and step 3's empty block — Joe 0921

### The ruling

> *"update step2: instead of relying on r passing 50 (paraphrasing), use "ws{tf+1}x dwelling in*
> *dr-opposing oob, for tf*{knob:1}""*
> *"eg, for a ws1 divergence test, the ws2x dwell in dr-opposing oob is 1 minute. for ws4r , its 4*
> *minutes"*

| item | value |
|------|-------|
| the line | `ws{tf+1}x` — a ws1r test reads ws2x, a ws4r test reads ws5x |
| the condition | in the dr-OPPOSING oob **15/85**: at dr +1 x <= 15, at dr −1 x >= 85 |
| the length | tf × `anchor_floater.dwell_min_per_tf` minutes, contiguous |
| the pivot | that run's **x extreme** — its min at dr +1, its max at dr −1. Joe 0921 chose the
  extreme over the run's first or last bar |
| no run qualifies | the test returns None |

`dwell_min_per_tf` is banked at **1**, config v10. The key name and the per-tf units are mine.

### Step 1 is unchanged

Joe 0921: *"step 1, no change"*. The anchor still returns None when `r[k]` sits on the wrong side
of 50 for the dr.

### Step 3 — the 50 filter stays, the empty-block STOP goes

The 50 filter is Joe's own step 3, verbatim from 0912: *"find the r extrema that is on the same
side as step 1's dr"*. It was never mine and it stays.

What was mine is what a block with **no** dr-side bar does. It used to end the walk. Joe 0921 ruled
it is **skipped** and the walk continues. His 0912 stop condition is *"until it has proven that it
has gone past the extrema"*, and an empty block proves nothing about the extrema.

- the walk now ends only at a non-improving block, or the tape start
- there is no backward horizon, so a floater may sit on the previous day

Worked on ws3r at 09-01 03:40:05, anchor r 60.68, dr +1:

| step 3 | block 1 03:22:00 → 03:27:00 | result |
|--------|------------------------------|--------|
| the old stop | 0 of 60 bars above 50 | walk ends, **no floater** |
| Joe 0921, skip | 0 of 60 bars above 50 | skipped, walk continues to **88.67 at 03:06:15**, d_osc −27.98, **bearish +1** |

### The fidelity gap this leaves

`xn`, `dwell_bars` and `oob` default to None on `anchor_floater`, so the three callers that hold no
x line — `jig.sideways_reversal`, `jig.causal.anchor_floater` and `docs/mage_cascade/stopsweep.py` —
still run the 50 rule Joe replaced. TWO STEP-2s NOW LIVE IN ONE PRODUCER. That is a gap to close,
not a design.

### The 09-01 report

32 v7 `wsl_sig_utc` signals, `anchor_floater` at each one:

| line | bearish +1 | bullish −1 | none 0 | no result |
|------|-----------|-----------|--------|-----------|
| ws3r | 3 | 11 | 11 | 7 |
| ws4r | 2 | 10 | 18 | 2 |

`jig.divergence`, the episode-based machine, returned 0 on all 32 for both lines — the two mechs
never share a bar. The full table is `docs/22_go_20260921/divergence_step2_20260921.txt`.

---

## 13. The sideways / reversal hypothesis, Joe 0912 — NOT YET SCORED

> *"we've landed here because I couldn't get a momentum stall/sideways/reversal with the existing*
> *mechs. now that we have a divergence machine, I want to use it to enhance the momentum outputs.*
> *we're in science mode, here's my hypothesis: if we see >= 3 samples printing the same values*
> *(tolerance ~2%) on the dr side of 50, and we test for divergence for the next 2 minutes, then we*
> *can create a reliable momentum sideways or reversal signal*
> *-reversal is a new state. I'm not 100% sure that we need it yet, but it will help me while we*
> *develop the science"*

- built as `jig.sideways_reversal`, delegating to `jig.anchor_floater` for the divergence test
- a SAMPLE is one 5 s bar. Evidence, not a choice: the per-sample table Joe read the hypothesis
  off was 61 rows across 17:30:00–17:35:00
- `sideways` fires on the bar a run REACHES 3 bars with every bar on the dr side of the MID-ZONE
  FENCE and the run's max minus min within tolerance

### THE MID-ZONE FENCE, Joe 0912

> *"let's modify the dr side of 50 rule. instead of 50, create a mid-zone-fence of 40:60. the*
> *sideways signal must be on the dr side of the fences edge"*

- replaces the plain 50 test in the `sideways` run only
- dr +1 reads the HIGH side, so every bar of the run must sit STRICTLY ABOVE 60
- dr -1 reads the LOW side, so every bar of the run must sit STRICTLY BELOW 40
- `anchor_floater` is untouched and still uses 50 for steps 1, 2 and 3 - that is the divergence
  machine's own boundary and Joe did not change it
- measured on the 18:45 walk: the ws1 sideways moves from 19:18:15 (ws1r 49.20) to 19:21:10
  (ws1r 38.73), 2m55s later
- `reversal` fires on the first bar in the following 24 bars (120 s) where the anchor/floater test
  returns non-zero, with that bar as the anchor

### Knobs

| knob | value | units | whose |
|------|-------|-------|-------|
| `SR_SAMPLES` | 3 | 5 s bars | Joe 0912, ">= 3 samples" |
| `SR_TOL` | 2.0 | r points across the run | MINE — Joe wrote "~2%", read as 2% of r's 0..100 scale |
| `SR_TEST` | 24 | 5 s bars = 120 s | Joe 0912, "the next 2 minutes" |
| `SR_FENCE` | (40.0, 60.0) | r points | Joe 0912, the mid-zone fence |
| `AF_BLOCK` | 60 | 5 s bars = 300 s | Joe 0912, the step-3 block |
| the line | ws1r | — | MINE — the report subject is ws1 |
| walk start | ws1Mage oob-low run reaching 3 bars | 15 s | MINE — `WS1MR_DWELL`, Joe has not ruled |

### THE WALK, Joe 0912

**The renaming.** Joe 0912: *"it's a dr -1 flip, so the previous walk was dr -1. now that I'm
typing, I see how the terminology is ambiguous. it would be better if I refered to flips that fire
on the low side of board as a dr +1 flip"*

- a flip that fires on the LOW side of the board is a **dr +1 flip**
- the walk it opens is read at dr +1: ws1r's verdict comes from the dr +1 bank, and the flat run
  must sit ABOVE 50
- the latch itself is unchanged — it still sets its internal dr to -1 on the low side. The
  renaming is how the WALK is labelled and read, not a change to `build_wsf_dtf_v3`

**ws1Mage begins the walk.** Joe 0912: *"this event needs to fire on the opposite side of dr.
ie ~16:42"*

- the trigger is ws1Mage reaching oob on the side OPPOSITE the side the flip fired on
- a low-side flip therefore waits for ws1Mage to reach HIGH oob (>= 75)
- oob-dwell 6 bars = 30 s. Joe's value, given earlier for this same event: *"the next walk begins
  at the opposing dr's ws1Mage oob cross (oob-dwell=6)"*
- measured: the 16:14:05 low-side flip gives 16:42:25, which is Joe's ~16:42

**Where the walk ends.** Joe 0912 ruled it: at the first `sideways`, or at its `reversal` when one
fires inside the 2-minute test window. One event per walk, not a stream.

### First run, 08-25, two dr +1 walks

| walk | dr +1 flip (fired low) | ws1Mage begins | ws1r momo/curl | sideways | reversal |
|------|------------------------|----------------|----------------|----------|----------|
| nearest 16:21 | 16:14:05 | 16:42:25 | curl 17:00:00 | 17:00:10 | none |
| nearest 17:09 | 17:05:10 | 17:20:00 | momo 17:20:00 | 17:20:00 | none |

**Neither walk produced a reversal, and the gate that stopped it is the same in both:** step 3's
block 1 held no bar above 50, so the loop stopped with no floater. That gate — "a block holding no
dr-side bar stops the loop" — is MINE and unruled.

- walk 1, anchors 17:00:15 and 17:00:20: pivot 16:57:05, block 1 = 16:52:05..16:57:05, no bar
  above 50
- walk 2, all 24 anchors: pivot 17:09:00, block 1 = 17:04:00..17:09:00, no bar above 50
- walk 1's remaining 22 anchors never ran: 19 of them sat below 50 (step 1 rejects), and the last
  3 did produce a floater at 17:00:00 r 58.29 but no divergence
- at walk 2's sideways bar ws1r reads 97.53 with a run spanning 0.45 r points. The 0711 survey
  Finding 4 names that shape: *"r pinned at 85/15 reads as a false equal-high"*

---

## 14. The seam jump and the r2 gate, Joe 0912 — SPEC STATED, NOT YET BUILT

### What the r2 gate is

- `momo_core.verdict` will only call a line `momo` when a straight line drawn through the 21
  lattice samples actually describes them. `wflb_fit` is that score, `momo_r2_min` 0.7 is the floor
- the score is 1.00 when every sample sits exactly on the line, and falls toward 0.00 as the
  samples scatter away from it
- the reason string on a failure is *"sloped, but too crooked to call a line"*

### Why a seam step scores badly

Five samples, the same total drop of 8 points, three shapes:

| shape | the five values | straight-line score | passes the 0.7 floor? |
|-------|-----------------|---------------------|-----------------------|
| a steady slide | 50, 48, 46, 44, 42 | 1.0000 | yes |
| flat, one step, flat | 50, 50, 50, 42, 42 | 0.7500 | yes |
| flat, one step at the end | 50, 50, 50, 50, 42 | 0.5000 | NO |

- the same move scores differently depending only on WHERE the step sits in the window
- a step near the end of the window scores worst, and that is the freshest information

### The seam, Joe 0912

> *"the jump happens because it traversed the TF bar seam. this is the accepted nature of emerging*
> *values"*
> *"if the jump happend on the TF seam, there is no need for a threshold. the mech should simply*
> *decide if the seam jump is towards dr"*
> *"it's the final seam that matters. if we think about it, you're describing a `curl` state"*

- no r-point threshold. The test is a timestamp test: was this step a seam step
- the seam grid is MIDNIGHT-aligned, not epoch-aligned:
  `(bar epoch ms - that day's midnight ms) mod (tf x 60 x 1000) == 0`
- verified on 08-25 against the measured jump offsets: 11 of 11 dtf lines match
- the offset changes every day, because 1440 minutes is not a whole number of 13-, 14-, 17-, 19-,
  21-, 22- or 23-minute bars. ws13 is 300 s on 08-25, 120 s on 08-26, 720 s on 08-27
- **THE FINAL SEAM IN THE WINDOW IS THE ONE THAT COUNTS.** Joe 0912. Earlier seams inside the same
  window do not vote
- **SCOPE: ACROSS THE BOARD.** Joe 0912 - every line, not only dtf. ws1's bar is 60 s so a 600 s
  window holds 10 seams; the final one is the one that counts there too
- a knob token is needed in the `wsf_line_bar` key, and the chain needs a rebuild

### The three ways to handle the seam step — STILL JOE'S CALL

Measured on the real 21 samples at 19:37:30, dr -1:

| line | as it stands now | drop the seam sample and refit | line the two halves up and refit | gate |
|------|------------------|--------------------------------|----------------------------------|------|
| ws13 | 0.5423 | 0.5599 | 0.0001 | 0.70 |
| ws14 | 0.4636 | 0.3835 | (undefined) | 0.70 |

- **skip the gate** when the final seam step points at dr: both lines become `momo`, since the
  slope, alignment and 50 gates already pass
- **drop the seam sample and refit**: 0.5599 and 0.3835 - both still fail the 0.70 floor
- **line the two halves up and refit**: removes the only movement in the window. ws13 falls to
  0.0001. ws14 becomes a perfectly flat series with no variance at all, so the score is undefined -
  the 1.0000 my helper returned there is an artefact of its divide-by-zero guard, not a score

### Still open

- off-seam movement is not covered by this rule. On 08-25 ws13 had 26 of its 96 moves above 5.0 r
  points land off the seam, largest 10.99, and 1,183 off-seam bars moved more than 1.0 r point.
  Joe 0912: *"noted. we'll get to them organically and consider the next move then"*

---

## 15. `momo_slack_ref` — the knob split out of `momo_slope_min`, Joe 0912

> *"SRP says to separate"*

### Why

`momo_slope_min` was doing two unrelated jobs in `momo_core.py`:

| job | where | what it decides |
|-----|-------|-----------------|
| the flat/sloped branch test | `momo_fit`, `flat=abs(sl) < MOMO_SLOPE_MIN` | whether a bar goes to the curl/sideways branch or the momo branch |
| the level-gate slack scaling | `momo_fit` and `level_gate`, `trk = fit x min(1, abs(slope) / ...)` | how much of `level_slack` a line earns toward the 50 gate |

- a sweep of that one number moved both at once and could not separate them
- measured on the ws14 journeys, 08-25 to 09-01: raising it from 0.2 to 0.8 sent 96,314 bars from
  the sloped branch to the flat branch, and the first firing of each journey flipped from
  153 `momo` / 21 `curl` to 13 `momo` / 161 `curl`
- it also shrank the slack for any given slope: a line at slope 0.4 keeps all of its slack at
  floor 0.2 and half of it at floor 0.8

### The knob

| | |
|---|---|
| name | `momo_slack_ref` — Joe 0912 chose it |
| what it is | the slope at which a line earns its FULL level-gate slack |
| units | r-points per lattice sample, the same units as `momo_slope_min` |
| where it lives | `momo_config.mmc_momo_slack_ref`, a DOUBLE NOT NULL |
| seeded at | equal to `momo_slope_min` in every existing bank row - v0 at 1.0, v1 at 1.2 |
| `momo_slope_min` now | the flat/sloped branch test ONLY |
| key token | `_sr{value}`, appended ONLY when it differs from `momo_slope_min`, so every knob
  string banked before the split is byte-identical and its rows stay matchable |

### Every file that had to move

| file | change |
|------|--------|
| `optimus9/compute/momo_core.py` | `MOMO_SLACK_REF = None`; both `trk` expressions now divide by it |
| `optimus9/compute/momo_config.py` | KNOBS entry, and the float coercion list |
| `build_momo_config.py` | the DDL column and the V1 seed dict |
| `momo_config` table | `ALTER TABLE ... ADD COLUMN mmc_momo_slack_ref DOUBLE NOT NULL`, seeded equal |
| `build_wsf_line_bar.py` | the conditional `_sr` key token, and the SLOPE_OVERRIDE site sets BOTH |
| `build_wsf_dtf_v3.py` | both SLOPE override sites set BOTH |
| `build_wsf_momo_flip_rep.py` | the conditional `_sr` key token |
| `build_wsf_pxs_momo_flip_rep.py` | the conditional `_sr` key token |

**THE OVERRIDE SITES ARE THE TRAP.** Before the split, `bk['momo_slope_min'] = 0.4` moved the
branch test AND the gate. Every override site now sets both knobs, or the gate would silently keep
the bank's 1.2 while the branch test ran at 0.4. To sweep them apart, set them apart deliberately.

### Proof that nothing moved

- recomputed 17,304 banked `wsf_line_bar` rows - 08-25 19:00:00 to 20:00:00, timeframes 1..12,
  both dr - against the split code at `momo_slack_ref` = `momo_slope_min` = 0.4
- compared the ungated verdict, the gated verdict, the slope, the straightness, the 50-gate pass
  and the flat flag
- **0 rows differ**
- the key token comes out empty, so every banked knob string is unchanged

---

## 16. The test-point walk — Joe's rules, 0912/0913

Producer `walk_mom_models.py`. Table `wsf_dtf_mom_models`.

### The loop, Joe 0912 verbatim

> *"-on each dr flip*
> *--walk to same-side-dr ws1Mage crossing to oob*
> *---walk to the next ws1r sideways or reverse (the test-point)*
> *----scan the ws2r line for momentum-true*
> *----for each r line (only ws2r for now) that continues to the dr-side fence exit, but is not*
> *printing momentum-true at the test-point:*
> *-----sweep your collection of mechs until you have a momentum-true state for the line*
> *-----store the config (in a db table), and make it your working config*
> *-----create a fake dr flip (eg if the last test-point was measured at dr 1, the fake flip is dr -1)*
> *-----loop back to `walk to same-side-dr ws1Mage crossing to oob` and continue*
> *------if the next test-point does not see momentum-true for ws2r*
> *-------sweep again, find a config that works for both this ws2r test-point AND the previous*
> *test-point*
> *keep looping, test-pointing, sweeping until you can't find a sweep config that works for all of*
> *the previous cycles. when you reach that stalemate stage, stop and produce a per-testpoint report*
> *of your findings. use simple terms, no jagon"*

### Spent momentum, Joe 0912 verbatim

> *"I see the reason why you couldn't match a config: the momentum is almost spent. add this*
> *condition: if ws2r is outside (or almost outside) the r-momo-fence at the test-point, then keep*
> *walking to the next dr flip"*
> *"let's stick with 17/83, no margin. we can review when this scenario recurs"*

- the test reads the dr SIDE only, Joe's choice: at dr -1 a line past the LOW edge is spent, one
  past the high edge is not
- the walk then resumes at the next REAL latch flip, at whatever dr that flip sets - Joe's choice
  over planting a flip

### The ws1r oob step, Joe 0913 verbatim

> *"that's another rule I missed: after walking to ws1Mage, the walk needs to walk to the next oob*
> *ws1r*
> *-in the case of 06:35, the market has been going sideways so there is no dr 1 ws1r oob (sideways*
> *market = weak `r`) following the dr 1 ws1Mage oob*
> *-the next event that fires after dr 1 ws1Mage , is a dr -1 ws1Mage at ~06:44, followed by a ws1r*
> *oob @ ~06:47*
> *-following the ~06:47 oob ws1r, the next dr -1 sideways/reverse signal (test-point) will be at*
> *either ~06:49, or a divergence-supported signal at ~06:58"*

> *"06:47:10 is fine"*
> *"oob is alwasy 15/85"*
> *"add `r` dwell as a knob, but don't sweep it during this walk. set the default to wob 2"*
> *"it abandons it. treat a dr flip as a fresh start"*

- `r` dwell is a wob, Joe 0913: 2 steps, so the oob run must reach 3 bars = 15 s
- an opposite-dr ws1Mage oob arriving before the dr-side ws1r oob ABANDONS the current dr. The
  walk takes the new dr and restarts its event hunt from that bar
- a fresh start resets the EVENT SEQUENCE only. Joe 0913 chose to KEEP the accumulated
  test-points, so a stalemate can still fire across a flip

**Measured against Joe's read, 08-25 06:00:00 -> 07:10:00:**

| what he read | what the data gives |
|--------------|---------------------|
| no dr +1 ws1r oob after the dr +1 ws1Mage oob | confirmed - none between 06:39:45 and 07:04:00 on either fence |
| a dr -1 ws1Mage at ~06:44 | 06:44:10, run reaching 6 bars, ws1Mage 17.04 |
| a ws1r oob @ ~06:47 | 06:47:00 on the 17 fence, 06:48:00 on the 15 boundary |
| a test-point at ~06:49 | the first sideways print after the 17-fence oob is 06:47:10, which Joe accepted |

### The trade signal, Joe 0913 verbatim — SHARED FOR CONTEXT, NOT BUILT

> *"note, ws2 and ws3 are both outside of the fence at the ~06:58 test-point. these 3 lines*
> *(ws1,2,3) + ws4Mage grazing low oob + a bull divergence from g30, is a trade signal. there is no*
> *momentum at ~06:58, so the walk continues*
> *-treat the trade signal as a dr flip"*

Joe 0913: *"I shared it for context."* Three parts have no definition yet and it is NOT a restart
trigger in the walk:
- which fence "outside of the fence" reads for ws1r, ws2r and ws3r - 15/85 or 17/83
- what "grazing low oob" means for ws4Mage
- which divergence machine and at what knobs - `jig.divergence` is episode-based, and the
  anchor/floater front end from Joe's four steps is a different one

### The ws3 / ws4 digression, Joe 0912 verbatim — PARKED

> *"if a stalemate fires at a test-point, run the same logic on ws3 and ws4. if either exit the*
> *fence and a sweep config gives them momentum at the test-point, bank the config and continue the*
> *loop on ws2 only (until the next stalemate)*
> *you'll need a column in the dB table to record the digression"*

> *"my perspective on the stalemate (ws3/ws4 temporary inclusion) stands, but it needs to be tested*
> *after the spent-momentum mech"*

Five things in it are unset: whether the ws3/ws4 config must satisfy every accumulated test-point
or only the current one; what happens to the ws2 test-point that caused the stalemate; what to do
if neither line works; whether to stop at the first that works; and the column name.

### Walk results so far

| walk | what it had | cycles | outcome |
|------|-------------|--------|---------|
| 1 | no spent rule, no ws1r oob step | 4 | stalemate at 08-25 06:01:55, 3 test-points, whole grid tried |
| 2 | spent rule | 4 | stalemate at 08-25 06:35:10, 2 test-points, whole grid tried |

- walk 2's spent rule fired once, at 08-25 04:59:30 with ws2r at 85.33, 2.33 past the high edge
- it removed one of walk 1's three irreconcilable test-points and the stalemate still recurred

---

## 17. THE MACHINE'S PLAN — Joe 0913

Joe 0913: *"this is part of a 15 step process that you created earlier. there has been changes
since then, which need to be incorporated"* / *"steps 1 to 7 and 9 to 12 reflect the plan I have
for the machine"* / *"update as needed and store the machine's plan in the spec, ensuring it is
all causal"*.

The 15-step list was my inventory of what `walk_mom_models.py` ran, written 0913. Joe selected
**1-7 and 9-12** from it as the machine's plan and dropped the rest. What he dropped, and why it
is consistent:

| dropped step | what it was | why it is not in the plan |
|---|---|---|
| 8 | the fence-exit test | **it looks forward 420 bars.** It was a scoring device for the walk, not a live step. Joe 0916 confirmed it is dead: *"exit_hi and exit_lo are not needed for this current work, because we're no longer tuning test-point and momentum"* — so `EXIT_HI` 80.0 / `EXIT_LO` 20.0 r-points and `REACH_BARS` 420 have no consumer |
| 13 | the sweep | the settings are fixed. Joe 0913: *"I don't think we need to sweep"* |
| 14 | the stalemate and the ws3/ws4 digression | both exist only to serve the sweep |
| 15 | the pool | the pool only fills when a sweep fails |
| 9 | the ws3 fallback | dropped 0913 after Joe answered O-1. ws3 arrives through 17.2 |

---

### 17.1 THE STEPS

**Step 1 — the dr latch.** ws1Mage AND ws13m both out of bounds on the SAME side, latched. dr +1
when both are at or above 75, dr -1 when both are at or below 25. Until both agree, the previous
dr holds. Verbatim from `build_wsf_dtf_v3`. CAUSAL: reads only bars at or before each bar.

**Step 2 — ws1Mage out of bounds.** From the cycle's start bar, the first bar where ws1Mage's
CONSECUTIVE run on the dr side of the 25/75 fence has REACHED `MAGE_DWELL` = 6 bars = 30 s.
CAUSAL: the run is counted backwards from each bar.

**Step 3 — the abandon rule. REMOVED, Joe 0916.** It raced ws1r's out-of-bounds dwell against
ws1Mage reaching its dwell on the OPPOSITE side, and on the opposite-side win it PLANTED a dr
flip. Planting a dr cannot survive Joe 0916's *"dr is global: ALL chains should be sharing the
dr"*, and he ruled the case directly — *"keep going on dr +1 and set the test-point at
16:32:10"*. Measured before removal: it fired on 1 of 167 dr stretches = 0.6%.

**Step 4 — ws1r out of bounds. REMOVED, Joe 0916.** It read ws1r against the 15/85 oob fence.
Joe 0916: *"r is never constrained by oob (85/15). r has its own r-momo-fence."* On r's own
fence the step became a strict subset of step 5, which reads the same band plus a flatness test,
so it could reject nothing step 5 accepts. Its only remaining effect was to stop step 5's 3-bar
window straddling the anchor — a 2-bar block, superseded by the look-back below.

**Step 5 — the flat-run signal. THIS IS THE TEST-POINT.** 3 consecutive bars of the line under
test where the highest minus the lowest across the run is 2.0 r points or less, and all 3 sit on
the dr side of **the r-momo-fence, 17/83** — above 83 at dr +1, below 17 at dr -1. Joe 0915 moved
this off the 40/60 mid-zone: *"apply r-momo-fence to the test-points"*, ALL of them. The
test-point is the bar the run REACHES 3. CAUSAL: backward-looking over 3 bars.

**Step 5a — the look-back. NEW, Joe 0916.** At the anchor (step 2's bar, which Joe named *"mk ==
established ws1Mage oob"*), look BACK up to `tp_lookback_min` = 4 minutes = 48 bars for a flat run
that has ALREADY completed on the dr side of 17/83. A hit means **the test-point IS the anchor
bar**. Joe 0916 set the knob — *"idk - lets use {knob:4} minutes"* — and bounded it: *"if dr flips
while the lookback is looking back, then we abandon and continue with the established mech"*, so
it never reads earlier than the dr stretch's own start. It requires NOTHING of r at the anchor:
*"at mk, nothing. lookback either finds a flat run, or it doesn't"*. No hit means the established
forward scan runs instead. Measured: the look-back produces 21% to 41% of test-points, and the
stretch start clips it on 84.8% of ws1 stretches. CAUSAL: reads bars at or before the anchor.

**Step 5b — one test-point per dr stretch PER TIMEFRAME. NEW, Joe 0916.** *"one test-point per dr
cycle, so long as the code treats this per tf - ie there will be multiple tf's setting test-points
inside of a dr cycle"*. Once wsN has produced in a stretch it stops hunting until the next latch
change. Without it the hunt re-fires every 30 s while the lines stay pinned — 79 test-points on
09-03 against 21.

**Step 5c — what advances the walk. CORRECTED, Joe 0916.** *"the dr latch only sets the cycle's
dr"* — NOT its start bar. The bar comes from the walk, the dr is read from the latch at that bar.
The forward scan is bounded by the opposing dr flip; if no flat run lands before it, that
timeframe produces nothing in that stretch. The old build PLANTED a flip at
`fence_exit(ws2r, 80/20, 420 bars) + 1` and planted `dr = -dr` with it — measured wrong against
the latch on 21.0% of its own test-points.

- `SR_SAMPLES` = 3 bars. Joe 0912: *">= 3 samples printing the same values"*.
- `SR_TOL` = 2.0 r points across the run. MINE, from Joe's *"tolerance ~2%"*, read as 2% of the
  0..100 scale. UNRULED.
- `SR_FENCE` = 40 / 60. Joe 0912: *"create a mid-zone-fence of 40:60. the sideways signal must be
  on the dr side of the fences edge"*.

**Step 6 — the divergence.** Runs ONLY when the line under test is not already momentum-true at
the test-point. Joe 0913: *"if a test-point finds momentum on its own, divergence is not needed so
the 2 minute delay is moot"* / *"if there is no momentum at the test-point, then the 2 minutes
grace is accepted"*. The anchor is each of the `SR_TEST` = 24 bars = 120 s AFTER the test-point,
and the line is momentum-true if any of them fires. Joe 0913 settled every part:

| what | answer |
|---|---|
| price series | `__pxs__` from the tape — source `close`, DEMA length 2 |
| the r line the divergence reads | `gcws30r`, registered at 30 seconds |
| does the divergence move or gate the test-point | neither |
| what a firing divergence does | marks the line momentum-true |
| the alignment test | redundant. The machine returns bearish only at dr +1 and bullish only at dr -1, so any verdict that fires already aligns |
| the anchor bar | each of the 24 bars AFTER the test-point |

CAUSAL: `anchor_floater` reads back from its anchor bar only. The EVENT'S KNOWABLE BAR is the
divergence's firing bar, up to 120 s after the test-point.

**Step 7 — the spent test.** Is the line already past the dr-side edge of the 17/83 fence at the
test-point. Joe 0912 fixed the edges and took no margin: *"let's stick with 17/83, no margin"*.
CAUSAL: reads the line's value at the bar.

**Step 9 — the ws3 fallback. DROPPED.** Joe 0913, answering O-1: *"O1 drop it. ws3 will be reached
through the natural flow. this is where the """momentum and divergence test for momentum-true"""
step comes into play."* Its trigger was step 8, which was dropped for looking forward. ws3 now
arrives through 17.2 instead, which tests every line in the range.

**Step 10 — the momentum verdict.** 21 samples 30 s apart, spanning 10 minutes back from the bar.
A straight-line fit and a bend fit, then the gates in order:

| # | gate | outcome |
|---|---|---|
| 1 | not enough usable samples | no verdict |
| 2 | slope below `momo_slope_min` -> the line is treated as FLAT | go to gate 3 |
| 3 | flat and on the wrong side of 50 | none |
| 4 | flat, level, and a qualifying bend | curl |
| 5 | flat and level | sideways |
| 6 | sloped and on the wrong side of 50 | none |
| 7 | sloped but not pointing at dr | none |
| 8 | straightness below `momo_r2_min` | none, unless step 11 excuses it |
| 9 | otherwise | momo |

A curl counts as momentum only when the end of the curl faces dr — n-shaped at dr -1, u-shaped at
dr +1. "Level" is judged against a band whose width is scaled by how weak the slope is, measured
against `momo_slack_ref`. CAUSAL: both fits read only bars at or before the bar.

**Step 11 — the seam rule.** Each timeframe's bar boundaries are laid out from that day's
midnight. A jump across the line's own boundary that points at dr excuses the straightness gate.
Joe 0912: *"if the jump happend on the TF seam, there is no need for a threshold. the mech should
simply decide if the seam jump is towards dr"*. CAUSAL.

**Step 12 — the lower-timeframe gate.** An optional condition read on the timeframe one below the
line being tested. Four settings: none; the line below must itself be momentum-true; the line
below's r must be further along than this line's r; the line below's Mage must be further along
than this line's Mage. Joe 0913 set which settings the lower line is read at: **the candidate
combination, not the held ws1 settings.** The "one below" is relative to the line under test —
MINE, and UNRULED; the alternative is a fixed ws1/ws2 pair. CAUSAL.

---

### 17.2 THE HAND-OFF — Joe 0913, NEW

**Verbatim:**

> when we reach a test-point and find a higher TF showing momentum-true, we can confidently predict
> price will continue its current course. to continue predicting price's course, we must move our
> focus to the line carrying momentum, ride it, and repeat the same test-point process when it
> reaches a flat-run signal
> -eg ws2 is momentum true at a ws1 test-point
> --ws2 walks forward until the "flat-run signal" (per your #5, below)
> --momentum and divergence test for momentum-true
> --the highest TF printing momentum is the line we ride until its flat-run signal
> ---for now, highest TF = 4 and divergence is provided by g30

**Joe 0913 improved the middle line, verbatim:**

> I'll improve the statement: "momentum and divergence test for momentum-true from all lines in the
> range (ie 1 to 4, at present)"

**The loop this sets:**

1. a test-point fires on the line currently in focus (ws1 at the start of a cycle).
2. **every line ABOVE the one in focus is tested for momentum-true, up to the ws4 ceiling.** Not
   in order, not until one prints: all of them. The step 10 verdict, or the step 6 divergence when
   the verdict says none. At a ws1 test-point that is ws2, ws3, ws4. At a ws3 test-point it is ws4
   alone. Joe 0913 corrected his own "1 to 4" wording: *"you're right"*.
3. the HIGHEST timeframe printing momentum becomes the line in focus.
4. step 5's flat-run signal is then run on THAT line, and the loop returns to 1.
5. the ceiling is ws4. The divergence is always read on gcws30r, whatever line is in focus.
6. **dr does not change during a ride.** Joe 0913, answering O-6: *"no"*.

**The line in focus is never re-tested.** Joe 0913 corrected the range to lines ABOVE the one in
focus. At a ws4 test-point there is nothing above it, so the ride ends — see 17.2a.

**CAUSAL.** Every leg reads only bars at or before itself. The hand-off bar is the test-point bar
when the verdict carries it, or the divergence's firing bar when the divergence carries it.

**THIS REPLACES THE WALK-5 SHAPE.** Walk 5 tested ws2, fell back to ws3 only when ws2 never reached
the fence, and ended the cycle at the fence exit. The plan tests ws2, ws3 and ws4 together, takes
the highest that prints momentum, and ends the ride at that line's own flat-run signal. No fence
is involved in either decision.

---

### 17.2a THE RIDE ENDS — Joe 0913

**Three ways a ride ends. Two are Joe's direct answers; the third follows from the ws4 ceiling.**

| # | ride end | source |
|---|---|---|
| E-1 | the line in focus is ws4 and it produces a flat-run signal. Nothing above it can take the hand-off | follows from the ws4 ceiling plus Joe's "lines above the one in focus" |
| E-2 | ws1Mage **bare-crosses** to the opposing-dr out of bounds. No dwell. Joe 0913, answering P-1: *"bare cross"* | Joe, answering O-4 then P-1 |
| E-3 | no line above the one in focus prints momentum at a test-point | Joe, answering O-7 |

**WHAT HAPPENS AT A RIDE END — Joe 0913, verbatim:**

> P2 wait for dr change. context: when the ride ends, one of 2 things happen - 1) ws4Mage and ws4r
> are both firmly oob on dr side, so we handover to dtf to complete the ride, or 2) ws4Mage or ws4r
> are weak (one has not exited the fence), and weak predicts a reversal - we would place a trade,
> ride pxs until the dr change, then start the wsf process from scratch

**CORRECTED 0913.** Joe's P2 sentence said both ws4 lines had to be out of bounds. He withdrew it:
*"ahh - I did make a mistake when I said oob for them both"*. **ONE TEST PER LINE:**

| branch | condition | what follows |
|---|---|---|
| A | ws4Mage out of bounds on the dr side **AND** ws4r outside momo-fence-r on the dr side | hand over to dtf to complete the ride |
| B | anything else — the negation of A | weak predicts a reversal. Place a trade, ride pxs until the dr change, then start the wsf process from scratch |

**A AND B ARE EXHAUSTIVE BY CONSTRUCTION.** B is A's negation, so no ride end falls between them.
Measured 0913 at walk 5's 90 test-points: 2 branch A, 88 branch B, 0 left over.

**The two tests, one per line:**

| line | test | Joe's answer, verbatim | what it resolves to |
|---|---|---|---|
| ws4Mage | out of bounds | *"oob (15/85) with a dwell of {knob:12} (1 minute)"* | the 15/85 fence, dr side, consecutive run REACHING 12 bars = 60 s |
| ws4r | outside the fence | *"r-momo-fence, wob {knob:3}"* | momo-fence-r = 83/17, knob `MOMO_FENCE_R` = 17, Joe 0820: *"create a new fence: momo-fence-r 100-{knob:17}"*. wob 3 steps spans 4 bars = 20 s |

**ws4r is NOT tested against 15/85, and ws4Mage is NOT tested against momo-fence-r.** That was the
mistake, and it is what created the 2-point band between the fences where a ride end could fall
through. Under one test per line the band does not exist.

**BRANCH A IS ONLY REACHABLE AT ws4.** Joe 0913, answering Q-3: *"yes, both A and B branch are
possible, but there is no DTF handoff for ws1,2,3. ie, if we've riden ws3 to a flat-run signal and
there is no ws4 momentum, the only option is to end the ride by delegating to the trade machine"*.

| ride ends with the line in focus at | branches available |
|---|---|
| ws4 | A or B, decided by the ws4Mage / ws4r tests above |
| ws1, ws2, ws3 | **B only.** There is no dtf hand-off below ws4 |

**Neither knob is named.** Joe wrote them as `{knob:12}` and `{knob:3}`. They need names and a home
in the config table before anything reads them.

**P-2 answered.** *"wait for dr change"* — the next dr CHANGE from the latch, not merely a bar where
the latch holds a dr. My earlier reading is now Joe's answer, so the flag is discharged.

**E-3's branch is a stub.** Joe 0913, answering P-4: *"stub it. report them in a standalone table
showing timestamps and the data present at the test-point"*. No trade machine exists.

---

### 17.3 JOE'S ANSWERS, 0913

| # | question | Joe's answer, verbatim |
|---|---|---|
| O-1 | step 9's trigger | *"O1 drop it. ws3 will be reached through the natural flow."* Step 9 is dropped |
| O-2 | all lines tested, or in order | answered by O-1's improved statement: **all lines in the range, 1 to 4** |
| O-3 | flat-run knobs on ws2/ws3/ws4 | *"same, but likely to evolve as we develop the spec"* — 3 bars, 2.0 r points, 40:60, on every line |
| O-4 | what ends a ride with no flat-run signal | *"presently, ws1Mage crossing over opposing-dr oob. this needs to be developed further"* |
| O-5 | after a ride ends | *"wait for dr"*. And: *"these events needs to be tagged as their own row in the summary report"* |
| O-6 | does dr change during a ride | *"no"* |
| O-7 | no line prints momentum | *"it delegates to the unbuilt trade machine. stub it for now, tag as its own row in the summary report"* |
| O-8 | `SR_TOL` = 2.0 r points | *"I can't remember why I set the tolerance. I won't change it - the ws1 test-points have been validated"* |

**O-8 stands as Joe's.** He has validated the ws1 test-points it produces. The 2.0 reading was
mine, from his *"tolerance ~2%"*; he has now adopted it rather than ruled on the derivation.

---

### 17.3a JOE'S ANSWERS TO THE NARROWER SET, 0913

| # | question | Joe's answer, verbatim |
|---|---|---|
| P-1 | the ride-end cross — dwell or bare | *"bare cross"* |
| P-2 | "wait for dr" | *"wait for dr change"*, with the two-branch context now at 17.2a |
| P-3 | the summary report | *"similar to your reports that you showed after the OOS test. no need for a producer yet - you always create at least one report that we can build on, I'll let you know when I want to solidify"* |
| P-4 | the trade machine stub | *"stub it. report them in a standalone table showing timestamps and the data present at the test-point"* |
| P-5 | step 12's "one below" being relative to the line under test | *"we're in sync on this"* — my reading is adopted. The flag is discharged |

**P-3 sets the report's form, not a producer.** The shape is the per-day category table and the
per-test-point list produced for the 14-day out-of-sample run: one outcome category per row with
counts, then every test-point as its own row. Joe 0913 will say when it should be solidified into
a table and a producer.

**Two categories need their own rows in that report**, per O-5 and O-7: the ride-end events, and
the test-points where no line above prints momentum.

---

### 17.3b JOE'S ANSWERS ON THE RIDE-END TESTS, 0913

| # | question | Joe's answer, verbatim |
|---|---|---|
| Q-1 | "firmly oob on dr side" | *"oob (15/85) with a dwell of {knob:12} (1 minute)"* |
| Q-2 | "weak ... has not exited the fence" | *"r-momo-fence, wob {knob:3}"* |
| Q-3 | do A and B apply to every ride end | *"yes, both A and B branch are possible, but there is no DTF handoff for ws1,2,3"* |

---

### 17.3c THE RIDE-END TESTS — ALL SETTLED, 0913

**R-1 CLOSED.** It was the gap between branch A and branch B, and it existed only under the
both-lines-oob reading Joe withdrew: *"ahh - I did make a mistake when I said oob for them both"*.
One test per line leaves nothing between them. The bar that exposed it — cycle 49, 08-27 11:07:10,
dr +1, ws4Mage 111.72, ws4r 83.01 — is branch A under the corrected rule.

**R-2, R-3, R-4 CLOSED.** Joe 0913: *"your reads are good"*. They are now the rule, not my readings:

| # | now the rule |
|---|---|
| R-2 | ws4r is "outside momo-fence-r" when its consecutive run outside 83/17 on the dr side REACHES 4 bars |
| R-3 | the A/B test is read at the ride-end bar |
| R-4 | ws4Mage's dwell is counted BACKWARDS from the ride-end bar, which is what keeps it causal |

**R-5 CLOSED.** Joe 0913: *"I'll pass the knobs to you for labelling"*. **THE LABELS ARE MINE.**

New rows in `wsf_dtf_v3_config`. No schema change — the table is already key/value:

| section | key | value | units | owner | note |
|---|---|---|---|---|---|
| `ride_end` | `mage_dwell` | 12 | bars | joe | ws4Mage's run on the dr side of 15/85 must REACH this. 12 bars = 60 s. Joe 0913 `{knob:12}` (1 minute). Label mine |
| `ride_end` | `r_wob` | 3 | steps | joe | ws4r's run outside momo-fence-r on the dr side. 3 steps SPAN 4 bars = 20 s. Joe 0913 `wob {knob:3}`. Label mine |
| `momo_expiry` | `fence` | 50 | r-points | joe | the expiry fence, 100 - the closest edge, so 50 = 50:50. Joe 0914. Label and section mine |
| `momo_expiry` | `xwob` | 5 | bars | joe | the line must hold past the expiry fence for this to CLEAR. Joe 0914 `"yes, xwob5"`. Label mine |
| `momo_expiry` | `return_bars` | 3 | bars | joe | the line must hold back INSIDE momo-fence-r for this before the expiry BITES. Joe 0915 `"n can be 3 and swept"`. Anchored to the flat-run's own 3 bars. Units bars, not wob: mine. SWEEP CANDIDATE. See 18.1 |
| `handoff` | `ride_tf_hi` | 4 | timeframe | joe | the highest timeframe the machine RIDES. Joe 0914, eyeballed not swept. Label mine. See 19.2 |

Python constants, following `walk_mom_models.py`'s `R_DWELL_WOB` / `R_OOB_BARS` pairing:

```
RIDE_MAGE_DWELL = 12                      # bars = 60 s
RIDE_R_WOB      = 3                       # steps
RIDE_R_BARS     = RIDE_R_WOB + 1          # 4 bars = 20 s
```

**NO NEW FENCE KNOBS.** Both fences the ride-end test needs are already banked at v1 and v2:

| what | where it already lives | value |
|---|---|---|
| the 15/85 boundary | `wsf_dtf_v3_config` `[dr] oob_hi` / `oob_lo` | 85.0 / 15.0 r-points |
| momo-fence-r 83/17 | `wsf_dtf_v3_config` `[wsf_chain] momo_fence_r` | 17 r-points, band 100-17 |

**ONE TRAP, FLAGGED.** The repo does not agree with itself on what a wob value counts.
`[ws1mage_rev] boundary_xwob` = 4 carries units `bars`, while `walk_mom_models.R_DWELL_WOB` = 2
spans 3 bars. `ride_end.r_wob` = 3 is written with units `steps` and its 4-bar span spelled out in
the note, so a reader cannot take it for 3 bars. The wider inconsistency is untouched.

**WRITTEN 0914.** Both rows are banked at v3 and `handoff_routing.ws4_pair()` reads them. The
python constants above were NOT written - the values arrive from the config, not from a module
constant, so they are kept here only as the units they stand for.

---

### 17.4 NOT BUILT

No producer runs 17.1 as a sequence or 17.2 at all. What exists:

| step | where it lives today |
|---|---|
| 1, 2, 3, 4, 7 | `walk_mom_models.py` — as walk-5 scaffolding, not a machine |
| 5 | `jig.sideways_reversal` — runs on ws1 only, and its caller reads the flat-run bar |
| 6 | `jig.anchor_floater` — walk 5 fed it a price series of all zeros, so it never fired |
| 9 | `walk_mom_models.py` — trigger depends on the dropped step 8 |
| 10, 11, 12 | `momo_core.verdict`, `momo_seam`, `walk_mom_models.gate_ok` |
| 17.2 | nowhere |


---

## 17.3 SNEAKY-TRADE-1 — Joe 0916 named it

Joe 0916: *"to remove pyramid and main-trade references, I'm going to call this mech
'sneaky-trade-1'"*.

### The direction — settled, and it does NOT follow the dr-bias rule

> *"when you reach a test-point (the moment when the sneaky trade signals), you will enter a long
>  position if dr is +1, and short if dr is -1. this is all you need to consider - don't be swayed
>  by the other potential activities that might be reliant on dr"*

| dr | sneaky-trade-1 |
|---|---|
| +1 | LONG |
| -1 | SHORT |

In code that is scoring `* dr` — profit when price moves in the +dr direction. Spec 17.2's
dr-bias rule (dr +1 = SHORT) governs OTHER mechanics and must not be applied here. Joe ruled this
explicitly to stop the two being confused.

### The trade

| step | what | source |
|---|---|---|
| open | the first bar after the test-point where **ws1x**, having been out of bounds on the OPPOSING dr side (15/85), comes back IN BOUNDS. Bounded by the dr flip | Joe 0916: *"start calculating from the moment after 'test-point' when ws1x has crossed from opposing-dr-side oob, to ib"* |
| close | the **first** `gcws30mage-rev` after the carrying line's r-momo-fence exit. The open must land BEFORE it, else no trade | causal; see the note below |
| size | 22,000 coins, fixed | Joe 0916: *"I agree with 22K coins - its a good strategy to build from"* |
| producer | `optimus9/compute/sneaky_trade_1.py` | the signal. Owns no threshold |
| banked | `sneaky_trade_1` table, `build_sneaky_trade_1.py` | EVERY signal, taken or not, keyed on (test-point bar, src) so o9-live can reconcile a fill against it |
| stop | NONE | swept on pxs at 5 s over the full observed range: every binding level loses, monotonically |

**THE CLOSE WAS NOT CAUSAL AND IS FIXED.** It used to be the leash's maximum coil — `argmax` over
every rev in the window. That is the global maximum of an oscillating series (60.1% of windows
carry 2+ local peaks, median 2, max 11), so it is only knowable once the window has ended. A
proper causal peak detector agrees with it on 0.7% of rows. Joe 0915 asked for three picks —
*"test all 3: filter, time, size"* — and **size is the one that cannot be built**.

### The gate — this is the entry condition, not a filter

All three read at the test-point, before anything opens.

| test | condition | why it is there |
|---|---|---|
| `drop` >= 50 | dr-signed ws1Mage minus ws12Mage at the test-point | marginal is + in all 3 time blocks and in both contexts it is testable in |
| src is ws1 or ws2 | the test-point came from the 1- or 2-minute line | the only gate whose marginal is + in ALL FOUR contexts and all 3 blocks |
| `hi` == ws4 | the carrying line is the 4-minute line | + in all 3 real contexts and all 3 blocks |

`climb` is NOT in the gate: once `hi` is ws4 and `src` is ws1 or ws2, the ladder has climbed by
construction, so it adds nothing. Its own marginal is + (+0.92 / +0.56 / +0.72) but only in the
ungated context.

GATES TESTED AND REJECTED, each for a stated reason:

| gate | why not |
|---|---|
| `drop` >= 39.1 (route 3's floor) | marginal sign flips: -0.08 / +3.39 / +1.61 across blocks |
| `wrong` <= 1 (route 3's own gate) | sign flips in ALL FOUR contexts; block 2 negative every time |
| KEEP the r-weak rows | NEGATIVE marginal in every gated context, all 3 blocks |
| DROP the r-weak rows | sign REVERSES by context: -8.19 ungated, +10.16 gated. 16 trades/block |
| dr -1 only | sign reverses by context |

Joe 0916 defined r weakness: *"an r that prints inside the fence is weak, if a lower TF is outside
of the fence"*. Measured both directions. It is context-dependent, not directional, so it is not a
gate.

**Mandatory.** The drag is a flat 16.06 USDT per trade at 22,000 coins, and the median move across
all rows is +0.288% against the 0.550% needed to clear it. 73% of rows never clear the drag. The
gate lifts that to 44.2%. Ungated the account goes to zero; gated it does not.

### Measured — 87 days, gates chosen in-sample, tested on a held-out third

Selection read BLOCK 1 ONLY. Blocks 2 and 3 were never read during selection. A candidate had to
produce at least 30 trades in every block, and a gate had to hold one sign across all 3 blocks AND
across contexts before it was even eligible.

| block | window | rows | mean net | wins | end bal from 600 | maxDD |
|---|---|---|---|---|---|---|
| 1  CHOSEN ON | 06-10 -> 07-08 | 92 | +7.03 | 48.9% | 1,247.00 | -6.43% |
| 2  HELD OUT | 07-09 -> 08-06 | 76 | +1.97 | 38.2% | 750.09 | -23.90% |
| 3  HELD OUT | 08-07 -> 09-04 | 93 | +13.72 | 65.6% | 1,876.37 | -12.21% |
| HELD OUT 2+3 | | 169 | **+8.44** | | | |
| ALL 87 DAYS | | 261 | +7.94 | 51.7% | 2,673.45 | -14.03% |

It did not degrade out of sample — the held-out mean is above the block it was chosen on. Block 2
is the weak month: +1.97 per trade, barely clearing the 0.55% drag.

### The ride ceiling and the concurrency limit — BANKED, Joe 0917

`handoff.ride_tf_hi` stays at **4**. The pyramid limit stays at **2**. Both were tested against
alternatives with selection on block 1 and the verdict read on blocks 2 and 3.

| configuration | b1 mean (chosen on) | HELD OUT 2+3 | degradation | 87-day total | maxDD |
|---|---|---|---|---|---|
| **tf4 alone, cap 2** | +7.03 | **+8.27** | **+1.24** | +1,995.12 | **-7.33%** |
| tf5 alone, cap 1 | +10.25 | +6.53 | -3.72 | +1,286.53 | -6.61% |
| union tf4+tf5, cap 2 | +8.22 | +6.80 | -1.42 | +2,357.95 | -10.25% |
| union tf4+tf5, cap 3 | +7.97 | +7.35 | -0.62 | +2,531.16 | -7.85% |

**tf4 alone at cap 2 is the only configuration whose held-out mean EXCEEDS its selection block.**
Every candidate block 1 preferred degraded out of sample. It ranked 11th of 15 on block 1 — a
block-1 selection would have discarded it.

Two rejected alternatives, each with its reason:

| tried | why not |
|---|---|
| ride ceiling 5 | +7.45/trade against 4's +7.82, and -356.55 over 87 days. It moves the carrying line up wholesale: `hi ws4` falls 1,534 -> 204 as ws5 takes the top |
| merge tf4 and tf5 on span overlap | it is a concurrency limit of 1 wearing a merge's clothes — max concurrent falls to 1 and 109 of the 240 it removes are separate positions, not duplicates. +5.47/trade, -16.83% |
| union with a raised cap | cap 3 and 4 read better across all 87 days (+7.58, +8.10) but that was never held out. Block 1 prefers cap 1, and cap 1 degrades hardest |

THE MAE AND MFE ARE THE SIGNALS. Joe 0917: *"your MAE and MFE results are baked on known-good
causal events, so that becomes sneaky-1's entry and exit signals"*. The excursion was always
measured between the ws1x crossing and the first rev — those two bars ARE the entry and the exit,
not markers around them.

MAE and MFE read **pxs at every 5 s bar**. Sampling that series every 30 s was a defect; reading
raw high/low instead is a different measurement — raw runs 0.624% deeper at the median, and that
gap is the spike content pxs exists to remove.

---

## 18. THE MOMENTUM EXPIRY — Joe 0914

**Verbatim:**

> there's a missing mech from the momentum machine: if an r-line has already exited the
> r-momo-fence and reversed back into the fence (ie its dr-side momentum has expired), it can not
> be tagged as mom-true until it has travelled past the mid-zone-fence (40/60) edge
> example: 08-27 17:09:10 dr +1, ws6 was outside of the fence at ~16:30. it won't be eligible for
> mom-true until ~17:24

**The rule, with Joe's 0914 answers folded in:**

1. a line ARMS the expiry when it exits momo-fence-r 83/17 on the dr side. **No wob on the arming
   cross** - Joe 0914: *"drop it"*.
2. the expiry BITES when the line reverses back inside momo-fence-r **and holds there for
   `momo_expiry.return_bars`** - Joe 0915. From the bar it first came back inside, the line cannot
   be tagged momentum-true; the state is KNOWABLE `return_bars - 1` bars later, when the hold
   completes. A brush against the fence that does not hold no longer bites.
3. the expiry CLEARS when the line travels past the expiry fence, held for `momo_expiry.xwob`.
4. the expiry also clears on a **dr flip** - Joe 0914, answering M-4.

| # | question | Joe's answer, verbatim |
|---|---|---|
| (a) | is the 50:50 the flat-run signal's fence too | *"(a) - the expiry fence is its own knob, flat-run keeps 40/60"* |
| M-2 | does the crossing need a dwell or wob | *"yes, xwob5"* |
| M-3 | what arms the expiry | *"honour any wobs in place. if there isn't one, attach a wob 1 to it"* -> then, on being told the arming cross has no wob anywhere in the chain: *"drop it"* |
| M-4 | does the expiry survive a dr flip | *"clears on a dr flip"* |
| 0915 | should the return cross carry a wob | *"create a wob that ensures we don't miss those mission-critical sideways"*, then *"C makes more sense to me"*, then *"I agree with your natural anchor, n can be 3 and swept (add the knob)"* and *"my read on your summary: it's a happy accident - keep the wob"* |

**THE EXPIRY FENCE IS NOT THE MID-ZONE FENCE.** `momo_expiry.fence` = 50 is its own knob. The
flat-run signal keeps `SR_FENCE` = 40/60 and every test-point already measured is unaffected.

**Measured 0914 on Joe's own example** - ws6r, 08-27, dr +1. Last bar at or above 83 was 16:53:55
at 84.54:

| fence | knob | first bar at or below the edge after the exit | ws6r |
|---|---|---|---|
| 60:40 | 40 | 17:12:00 | 53.54 |
| 55:45 | 45 | 17:12:00 | 53.54 |
| **50:50** | **50** | **17:30:35** | **49.60** |
| 45:55 | 55 | 18:18:00 | 40.06 |
| 40:60 | 60 | 18:19:00 | 39.82 |

- the 50:50 fence removes the 17:12 excursion, which is what Joe asked of it: *"my eyes didn't see
  the 17:12 excursion. it's too early"*. ws6r bottomed at 53.54 there and never reached 50.
- Joe's eyes read ~17:24. The 50 fence lands at 17:30:35, six and a half minutes later. Both
  readings are on the table and the knob is set to be swept.
- the 17:30:35 crossing is one bar deep - ws6r is back above 50 fifteen seconds later - which is
  what `xwob` = 5 bars is for.

**At the bar this came from**, 08-27 17:09:10 dr +1, ws6r is 79.63: armed at 16:36, bitten by
16:54, and not yet past the expiry fence. Under this rule its `momo` verdict is disqualified.

### 18.1 THE RETURN HOLD — Joe 0915

Joe asked for it to stop a sideways being missed. **It was measured first, and nothing was being
missed.** 08-25 to 08-28, ws2..ws12, at the banked knobs:

| return_bars | seconds held | arm->bite pairs | with a flat-run inside the excursion | without | without % |
|---|---|---|---|---|---|
| 1 | 5 | 2,665 | 2,411 | 254 | 9.5% |
| 2 | 10 | 2,072 | 1,896 | 176 | 8.5% |
| **3** | **15** | **1,767** | **1,633** | **134** | **7.6%** |
| 4 | 20 | 1,582 | 1,479 | 103 | 6.5% |
| 5 | 25 | 1,442 | 1,351 | 91 | 6.3% |
| 6 | 30 | 1,341 | 1,266 | 75 | 5.6% |
| 8 | 40 | 1,184 | 1,128 | 56 | 4.7% |
| 12 | 60 | 1,028 | 989 | 39 | 3.8% |

The residual - the excursions that bit with no flat-run in them - is **entirely short**. At
`return_bars` 4, 95 of the 103 are 15 s or less and 8 are 16-30 s. At 12, 38 of 39 are 15 s or
less. **At every setting, including no hold at all, not one residual excursion exceeds 60 seconds.**

**JOE'S CLAIM IS VALIDATED.** He wrote: *"for a line to expire, it must pass through either of
these 2 states: sideways or reverse ... by definition, a line can't be ridden and expired at the
same time"*. Across 2,665 arm->bite pairs there is no case of a line making a real run past
momo-fence-r and coming back without going sideways first. The residual is brushes, not rides.

**SO THE WOB DOES NOT DO WHAT IT WAS ASKED TO DO, and Joe kept it knowing that** - *"it's a happy
accident - keep the wob"*. What it actually does is stop the expiry arming and biting on a
five-second touch of the fence.

**THE VALUE IS ANCHORED, NOT PREFERRED.** There is no knee in the curve - the miss rate falls
smoothly from 9.5% to 3.8% and is still falling at 60 s. 3 bars is the **flat-run signal's own
minimum**: the shortest excursion that could contain a sideways at all. Joe: *"I agree with your
natural anchor, n can be 3 and swept"*.

**UNITS ARE BARS, and that is MINE.** The sweep table above was originally numbered in wobs, where
a wob of 2 spans the 3 bars of the anchor. Reading the knob in bars makes both halves of Joe's
sentence agree - the anchor is 3 and n is 3 - and steps around the repo's own split, where
`momo_xwob` and `boundary_xwob` are bars but `ride_end.r_wob` is steps.

**BUILT.** `momo_expiry.expired()` takes `return_bars`; `handoff_routing.route()` passes it from
the config. Banked at v5.

**IT MOVES NOTHING WE HAVE MEASURED.** Re-run at `return_bars` 1 and 3: ws6r on 08-27 arms at
16:36:00 and bites at 16:54:00 under both, and all 40 in-sample ws2 momentum bars route `dtf`
under both, carrying the same 272 lines. The ws6 excursion is 18 minutes long - a real one.


---

## 19. THE HANDOFF ROUTING MACHINE — Joe 0914 named it

Joe 0914: *"I see how this new route 2 is affected by route 1 - will it flow cleanly if I replace
route 1's 'If not, place a trade instead' with 'if not, delegate to the handoff routing machine'?"*
and *"if so, build a machine that handles both routes"*.

**IT FLOWS, AND IT COLLAPSES THE TWO ROUTES INTO ONE.** Joe 0914: *"route 1 would only open up if
ws4Mage and ws4r have exited their respective boundaries, ie that would be the first test in any
case"*. So there are not two routes with two entry points. There is one decision:

| step | test | outcome |
|---|---|---|
| 1 | ws4Mage out of bounds on the dr side held `ride_end.mage_dwell` bars, AND ws4r outside momo-fence-r on the dr side held `ride_end.r_wob`+1 bars | hand to dtf |
| 2 | otherwise, scan ws5 up to `band_wsf_hi` for momentum-true. **Any one line is enough** — Joe 0914 C-2 | hand to dtf |
| 3 | otherwise | the trade machine |

**The consolidation is not a separate route.** Joe's *"ws[1,2,3,4]Mage are all not oob because the
market is consolidating"* is step 1 failing, which is exactly what step 2 is for.

**Joe's 0914 answers that shape it:**

| # | question | answer |
|---|---|---|
| C-1 | how far up does the scan run | **ws12**. Joe corrected his own ws13: *"my earlier call on ws13 was incorrect, I should have said ws12"* |
| C-2 | how many lines must agree | *"only one is required"* |
| C-3 | what settings the verdict uses above ws4 | *"use the ws2-ws4 config"*, and it is no longer to be called fitted: *"1) our OOS tests have proven value, 2) the line's config is consistent across the TFs"* |
| C-4 | which fence is "not oob" | *"oob is always 15/85"* |

**CAUSAL, with one stated delay.** Every test reads bars at or before the bar, except the
divergence, whose anchors are the 24 bars after it (17.1 step 6). When a divergence carries a line,
the decision is knowable at the firing bar, up to 120 s later. The producer returns `known_at` so a
caller never acts earlier than it may.

**BUILT 0914.** `optimus9/compute/handoff_routing.py` decides the route;
`optimus9/compute/momo_expiry.py` answers §18's expiry question. SRP: the router owns no threshold
— every knob arrives from `wsf_dtf_v3_config` — and it does not detect a ride end, ride a line or
place a trade. **Nothing calls it yet**; §17.2 is still unbuilt.

**Measured 0914 at the bars that exist:**

| what | result |
|---|---|
| the expiry on Joe's example, ws6r 08-27 | armed 16:36:00, bitten 16:54:00, never cleared, expired at 17:09:10 |
| the route at 08-27 17:09:10 dr +1, the one miss of 40 | **dtf**, carried by ws8, ws9, ws10, ws11, ws12. Knowable at the bar itself |
| the ws4 pair at that bar | ws4Mage 82.92 with a 0-bar run, ws4r 36.92 with a 0-bar run — both fail |
| the route at all 40 in-sample ws2 momentum bars | **dtf at 40 of 40**, every one carried by step 2 |
| the ws4 pair across those 40 | passed **0 of 40** |
| the trade machine | reached **0 times** in 41 bars |

**OPEN**

| # | item |
|---|---|
| H-1 | **CLOSED 0914.** Joe: *"the hand-off is simply wsf tell dtf that it has control. when dtf receives control, it starts walking the wdv_utc rows (causal, currently pre-built in wsf_dtf_v3)"*. So the hand-off carries control and the bar, nothing more, and `handoff_routing.route` returning `'dtf'` with its `known_at` is the whole of it. See 19.1 |
| H-2 | **CLOSED 0914.** Banked as `handoff.ride_tf_hi` = 4 at v4, deliberately separate from `band_subwsf` and `band_wsf_hi`. See 19.2 |
| H-3 | **DEFERRED 0914.** Joe: *"we'll sweep it when the o9-live loop is built"*. See 19.3 |


### 19.1 WHAT THE dtf HAND-OFF CARRIES — Joe 0914, H-1 closed

**Verbatim:**

> the hand-off is simply wsf tell dtf that it has control. when dtf receives control, it starts
> walking the wdv_utc rows (causal, currently pre-built in wsf_dtf_v3)

So the hand-off is a transfer of control and nothing else. `handoff_routing.route` returning
`{'route': 'dtf', 'known_at': bar}` is the complete payload - there is no state to pass, because
dtf reads the same `wsf_dtf_v3` rows from `wdv_utc` onward.

**CONTEXT ONLY, NOT SPEC.** Joe 0914, marked by him as *"for context, but not for right-now
spec-building"*:

> dtf's walk is hunting for a sequence that's built off the other columns. when it finds the right
> pattern, it will hand-off to the routing machine
> the routing machine will probably engage ws1 to improve the trade's entry, then fire a trade
> signal
> this is still in dev

That closes the loop: wsf hands control to dtf, dtf walks the rows, and dtf hands back to the
routing machine when it finds its pattern. **None of dtf's walk is specified and none of it is
built.** Nothing in §19 depends on it.


### 19.2 THE RIDE CEILING — Joe 0914, H-2 closed

**Verbatim:**

> we're talking about the TF limit of wsf, and where it belongs. I see it as a knob in a db table:
> 4 was chosen by eyeballing only, so we might find that 5 is "better" in a sweep. `better` is yet
> to be baked: it needs the routing completed after wsf and dtf are locked down

**Banked at v4 as `handoff.ride_tf_hi` = 4, units timeframe.** It is the highest timeframe the
machine will RIDE. `handoff_routing.route` reads it with no fallback.

**IT IS DELIBERATELY SEPARATE** from the two band knobs it could have been folded into:

| knob | value | what it bounds |
|---|---|---|
| `handoff.ride_tf_hi` | 4 | the highest line the machine rides |
| `band_subwsf` | gcws30..ws4 | the sub-wsf band, per Joe 0911 |
| `band_wsf_hi` | 12 | how far the hand-off scan reaches, per Joe 0914 C-1 |

Reading the ceiling off `band_subwsf` would have needed no new knob, and Joe rejected that: a sweep
must be able to move the ride ceiling to 5 without moving the band.

**EYEBALLED, NOT FITTED.** `wdc_fitted` is 0 because the flag means *chosen by scoring against
Joe's labels*; 4 was his own eye, which is a different provenance. The note records it as a sweep
candidate.

**`better` IS NOT DEFINED YET.** Joe 0914: *"it needs the routing completed after wsf and dtf are
locked down"*. Until then there is no target to sweep this knob against.

---

### 19.3 THE MOMENTUM CONFIG — Joe 0914, H-3 deferred

The config the router runs - slope floor 0.05, reference slope 0.05, straightness floor 0, level
band 40, seam `skip_r2` - is **not** in `wsf_dtf_v3_config`, against Joe's standing rule that
hard-coded values live in the DB.

**Its provenance, both halves:**

| | |
|---|---|
| **origin** | configuration number 1 of 2,580,480 - the loosest entry - taken by walk 5's cycle-7 ws4 digression on try 1, under the loosest-first ordering Joe himself called a fault on 0913: *"this highlights a fault in my instruction. the better method would be to sweep backwards from the tightest collection"* |
| **validation** | the 14-day out-of-sample run: 213 tested test-points, 196 covered, 92.0%. That is independent of the sweep order |

**The reversed sweep was never run.** Within the hour the divergence covered 12 of the 14 hard bars
and Joe closed the sweep: *"I don't think we need to sweep"*.

**DEFERRED, not dropped.** Joe 0914: *"I did, and it was based on the positive coverage that we
pulled from IS and OOS. having said that, somewhere in my thoughts is tugging at it, but I can't
pin it down. --we'll sweep it when the o9-live loop is built"*.

His unresolved doubt is recorded as his, not interpreted. Nothing here tries to name what is
tugging at it.

---

## 20. THE STRETCHY LEASH — Joe 0917 named it

Joe 0917, verbatim, from the session that built it:

> "we know that m and Mage will lead r around the board like it's on a stretchy leash. the further
> m and Mage are away from r, the more energy is coiled up in the stretchy leash"

> "stretchy leash: m and Mage vs r, does r still have room to be pushed"

### 20.1 THE COIL

    coil(line, bar, dr) = dr * ((m + Mage)/2 - r)

Positive = m and Mage sit ahead of r on the dr side, so r still has room to be pushed toward dr.
Causal by construction — three `emerging` lines read at the same bar, nothing forward.

The **combined coil** is the sum of the coils on the `coil_lines` knob: `gcws30` and `ws1`, the
30 s line and the 1 min line.

Producer: `optimus9/compute/stretchy_leash.py`.

### 20.2 THE CONFLUENCE MOMENT

A run of CONSECUTIVE `wsf_dtf_v3` rows that all carry `support_min` lines at a positive coil. The
run ends when the next row prints below `support_min`, **or with a different `dr`**.

Joe asked what defines the end — time or the coil's values. **Neither.** The rows define it, which
is why a moment's `end` is only knowable when the next row prints. Measured over 09-01 → 09-06:
the wait from the `end` row to the row that breaks the run is **median 300 s**, p25 160 s, p75
492 s, max 5000 s. Only 18 of 59 (30.5%) are knowable inside 180 s.

Over 09-01 → 09-06 at the banked key: 1179 rows, 269 at full support, grouping into **121 moments**
— 61 with a span of more than 0 bars, 60 single-bar.

Producer: `optimus9/compute/coil_moment.py:moments`.

### 20.3 THE CONFIRMED RELEASE

> Joe 0917: "the combined bar timestamp seems to need a lag during which it checks for a true
> release of the coil. test every 60 seconds"

A turn-down candidate is bar `t` where the combined coil at `t+1` is lower than at `t`; `t` is the
peak. It is CONFIRMED only if the coil never gets back above its value at `t` within
`confirm_lag_s`. If it does, the release was false — reject `t` and carry on walking.

The confirm window may read bars past the moment's last row. That is forward in time, not
lookahead: the verdict is only KNOWN at `t + confirm_lag_s`. The peak itself sits inside the moment.

The window is clipped to the last bar on the tape, so a moment near the end reads a SHORT window
rather than running off the end. A clipped window can only fail to disconfirm — such a release is
confirmed on less evidence than the rest. No moment in 09-01 → 09-06 is close enough to be clipped:
the report is byte-identical with and without the clamp.

The 60 s sweep, scored at the named bar across the 61 moments with a span:

| lag s | hit | coil % | unconfirmed |
|---|---|---|---|
| 0 | 13/61 | 68.8% | 1 |
| 60 | 28/61 | 84.1% | 2 |
| 120 | 28/61 | 86.9% | 6 |
| **180** | **31/61** | **88.2%** | **8** |
| 240 | 33/61 | 91.1% | 10 |
| 300 | 35/61 | 90.5% | 14 |
| 600 | 32/61 | 80.6% | 28 |

The knee is at 60 s: +15.3 points on one step. `confirm_lag_s` is banked at **180**; 240 buys
+2.9 points of coil from 5 moments and costs 2 confirmations, all of them 2-row moments.

Joe 0917: **"that 180s is required to provide the targeted results - it's not negotiable"**.

Producer: `optimus9/compute/coil_moment.py:release`.

### 20.4 THE EXIT — WHEN IT BECOMES ACTIONABLE

`ACTIONABLE` is the exit bar. Joe 0917: **"the lookback and setting of actionable timestamps is a
bolt-on, not an overwrite"**.

**A moment with a confirmed release — 62 of 121.** `ACTIONABLE = release bar + confirm_lag_s`.
The lookback never touches these rows.

**A moment with no confirmed release — 59 of 121.** Its `named bar` is the moment's end row, and
three steps run in order:

1. **LOOKBACK** — a `ws1mage-rev` whose cross sits in `[named bar - lookback_s, named bar]`
   → `ACTIONABLE = the named bar`.
   Joe: *"when you find ws1mage-rev in the 4 minute lookback that is anchored on `named bar`,
   `named bar`'s timestamp become the actionable time"*. **25 of 59.**
2. **GAP** — else, a `ws1mage-rev` strictly after the named bar and at or before the bar the
   moment's `end` becomes knowable → `ACTIONABLE = THE FIRST of them`.
   Joe: *"the `events in between` are all perfect. use the first timestamp"*. **23 of 59.**
3. else `ACTIONABLE` = the bar the `end` becomes knowable, unchanged. **11 of 59.**

Step 2 exists because step 1 alone left a dead zone. Row 3 of the report missed the lookback by
**20 seconds** — its event is at 02:40:20 against a window ending 02:40:00 — and the forward walk
began at 02:42:00, skipping it and landing 4140 s later. 23 of the 34 rows the lookback missed had
a `ws1mage-rev` sitting in that gap.

**CAUSALITY.** A `ws1mage-rev` counts only when its `sig_conf` — the bar it becomes KNOWABLE — is
at or before the bar being tested. `sig_conf = cross + boundary_xwob - 1`. The cross bar alone is
not enough. Joe 0917: *"keep it causal"*.

Producer: `optimus9/compute/coil_exit.py`. The event itself is `jig.ws1mage_rev` (spec 20.6), not
re-implemented.

### 20.5 MEASURED, 09-01 → 09-06, the banked build

| | |
|---|---|
| moments | 121 |
| CONFIRM, untouched by the bolt-on | 62 |
| END — lookback hit | 25 of 59 |
| END — gap hit | 23 of 59 |
| END — neither | 11 of 59 |
| exits carrying a `ws1mage-rev` at the actionable bar | 48 of 59 END rows |
| the 48 moved rows, actionable pulled earlier | median 290 s, min 15 s, max 4970 s |
| total pulled forward | 23150 s |
| exits validated within 180 s of the actionable bar | 70 of 121 |

The largest single pull is moment 85 at 4970 s (07:08:45 → 05:45:55). The smallest is moment 9 at
15 s. 10 of the 23 gap hits land on a negative combined coil.

**NOT MEASURED:** no forward return has been taken on any of these 121 exits. Every number above
is line geometry and event timing. Joe's chart read — *"most of the `end knowable at` timestamps
are well placed for profit"*, and the same for the 180 s `known at` set — stands as the only
measurement of whether the timestamps are good, and it predates the 48 rows that later moved.

### 20.6 THE KNOBS — `wsf_dtf_v3_config` v7, section `stretchy_leash`

| key | value | units | owner | in key | source |
|---|---|---|---|---|---|
| `coil_lines` | `["gcws30","ws1"]` | lines | joe | yes | Joe 0917: "the lower 30 sec coil will move/reverse before the 1 minute coil" |
| `support_min` | 23 | lines | **mine** | yes | I used full support from the first confluence report; Joe named no floor |
| `confirm_lag_s` | 180 | seconds | joe | yes | swept in 60 s steps; Joe banked the 180 s build |
| `lookback_s` | 240 | seconds | joe | yes | Joe 0917: "add a 4 minute lookback" |
| `exit_anchor` | `named_bar` | — | joe | yes | Joe 0917: "the lookback is anchored on `named bar`" |
| `gap_fill` | 1 | — | joe | yes | Joe 0917: "use the first timestamp" |

Knobs this section reads from elsewhere, never duplicated:

| key | section | used for |
|---|---|---|
| `band_wsf_lo` / `band_dtf_hi` | bands | the support set — ws1..ws23. `support_min` counts against it |
| `grid_s` | wsf_chain | 5 s. Converts `confirm_lag_s` and `lookback_s` into bars |
| `dwell`, `rev_wob`, `boundary_xwob`, `sig_line` | ws1mage_rev | the event producer's own knobs |
| `dr_line_a` | dr | ws1Mage, the line `ws1mage-rev` dwells and reverses on |
| `oob_hi` / `oob_lo` | dr | 85.0 / 15.0, the boundary the cross must land inside |

`support_min` is the one knob here that is **mine**. It is a sweep candidate and must be
re-declared as mine every time a result depending on it is quoted.

### 20.7 THE REPORT

    python3 report_coil_exit.py --from 2026-09-01 --to 2026-09-06

Defaults to the newest `wdv_knobs` in `wsf_dtf_v3` and that key's own full date range. `--md`
emits pipe-delimited rows. The script holds no values — every one is read from the config table.

**PROOF OF THE MOVE:** the 121 rows the packaged producers emit are byte-identical to the
scratchpad build Joe reviewed — 121 rows, 12 compared fields, md5 `ba4701655154a12ad57c404ca6ced440`
on both sides, 0 differences.

### 20.8 THE BANK — `wsf_leash`

Joe 0917: *"carve out these 7 columns and print them to a db table"*. Joe 0918 named the exit
stamp **`signal`**.

    python3 report_coil_exit.py --from 2026-09-01 --to 2026-09-06 --bank

| column | Joe's name | note |
|---|---|---|
| `wsl_n` | `#` | the moment's ordinal in the window |
| `wsl_source` | `source` | CONFIRM or END |
| `wsl_dr` | `dr` | |
| `wsl_act_utc` / `wsl_act_ms` | `ACTIONABLE` | the exit bar |
| `wsl_sig_utc` / `wsl_sig_ms` | **`signal`** | the signal stamp. NULL when none is found. NOT an exit — Joe 0923 |
| `wsl_rows` | `rows` | rows in the confluence moment |
| `wsl_first_utc` / `wsl_first_ms` | `moment first` | |

Each timestamp is stored twice — `_utc` to read, `_ms` to join on — exactly as `wsf_dtf_v3` stores
`wdv_utc` / `wdv_ms`.

**THE UNIQUE KEY** is `(wsl_knobs, wsl_v3_knobs, wsl_win, wsl_first_ms)`:

    wsl_knobs     every in-key knob in the `stretchy_leash` section, prefixed with the config version
    wsl_v3_knobs  the wsf_dtf_v3 key the moments were read from
    wsl_win       the walk window

A run at a different knob, a different source key or a different window lands BESIDE the old rows.
Nothing is updated in place, nothing is dropped. A re-run at the same key writes nothing and says so.

Banked at v7: **121 rows** — 62 CONFIRM, 59 END, 0 with a NULL `signal`. Verified field-by-field
against the printed report: 121 rows compared, 0 mismatches.

**`signal` HOLDS TWO KINDS OF BAR.** It is the stamp the exit acts on, and the route decides what
that stamp is:

| route | rows | the stamp is |
|---|---|---|
| confirmed | 62 | a `ws1mage_rev` sig bar |
| lookback | 25 | the moment's END ROW — the event only QUALIFIES it (2 coincide with a sig bar) |
| gap | 23 | a `ws1mage_rev` sig bar |
| forward | 11 | a `ws1mage_rev` sig bar |

Measured over the banked 121: **98 are a sig bar, 23 are the moment end row.** Nothing in the table
separates them; the route is not stored.

**DO NOT CONFLATE THE TWO COUNTS.** `jig.ws1mage_rev` emits **1297** sig events over 09-01 → 09-06
(588 at dr +1, 709 at dr −1). The stretchy mech emits **121** rows, **109** distinct stamps — one per
confluence moment, 12 moments sharing a stamp with the one before. The mech CONSUMES the producer;
it is not the producer.

Producer: `optimus9/compute/leash_bank.py`. It holds no rule — the rule is 20.4.

---

## 21. THE TRADE GATE — rule#1 and the scenario, Joe 0923/0924

A `wsf_leash` signal is not a trade. This section is the filter that decides whether a signal is
allowed to open one. It sits ON TOP of §20 and changes nothing in it.

### 21.1 RULE#1 — Joe 0923, verbatim

> "rule#1: a sig_utc timestamp must be qualified by ws1r and (ws2r or ws3r) exiting the same
> fence, within {knob:4} minutes of each other. -the fence is 27:73"

His rulings on the parts, each a separate answer:

| | Joe |
|---|---|
| which edge | 0923: "exiting the same edge, on dr side" |
| which side | 0923: "dr side" |
| measured between | 0923: "between sig_utc and the `r` lines" |
| the window | 0923: "within (either side)" — look back AND forward inside it |
| the knob's name | 0923: "`rule1_tol`" |
| the tolerance | 0924: "I was wrong about the tolerance. change it to 7 minutes" — 7 min TOTAL |
| qualification | 0924: "the lines can be qualifed at any time they are outside of the fence" |
| the dwell | 0924: "so far, it looks like the dwell is hurting so we'll drop it" |
| the ws1Mage support | 0923: "disable this ws1Mage-support mech for now" — it is NOT in the build |

`rule1_tol` 7 min TOTAL = ±42 bars = ±210 s at the 5 s grid.

### 21.2 THE SCENARIO — Joe 0924

> "how often do you see the scenario of ws1 diverging away from dr while ws2r, ws3r, and gcws30r
> are oob on dr side? test at each wsl_sig_utc"

then, on the window: *"the same 7 minute window that we've been using since last night"*, and
*"bake it into rule#1 and recreate the gate data"*.

**JOE HAS NOT NAMED THIS MECHANIC.** `scenario` is his own word for it and the code uses that
rather than a coined one.

Why it earns a place beside rule#1, Joe 0924: *"this highlights the divergence test's value-add:
8.6 is outside of the tolerance so ws1r cannot contribute to the #1 rule's qualifiers"*. The
divergence lets ws1r speak when its fence exit is out of the window — or absent.

**"DIVERGING AWAY FROM dr" IS A NON-ZERO VERDICT.** `anchor_floater` step 4 fires bearish at
dr +1 and bullish at dr −1, and can return nothing else. Joe 0924 on the frame: *"-1dr = low
board = launchpad for a long postion"*.

**oob IS 15/85.** 27/73 is rule#1's fence, 25/75 is the Mage fence, 17/83 is the r-momo fence.
Four different numbers, and no producer here defaults one to another.

### 21.3 MEASURED — v7, 09-01 → 09-06, 121 rows

| | n |
|---|---|
| rule#1 alone, open | 71 |
| scenario hits | 9 |
| **gate open, rule#1 OR scenario** | **74** |
| closed | 47 |
| rows the scenario adds | 3, at 2 distinct timestamps |

The two rows the scenario adds, both with ws1r at **0 bars** outside 27/73:

| # | wsl_sig_utc | dr | ws2r oob | ws3r oob | g30r oob |
|---|---|---|---|---|---|
| 42 | 09-02 07:30:30 | −1 | 38 | 16 | 6 |
| 87, 88 | 09-04 10:20:00 | −1 | 41 | 85 | 23 |

#87 and #88 are the duplicate v7 CONFIRM pair on one bar. Joe read the same 2 differences off his
own chart before the build was run.

**MFE in the direction that opposes dr**, over the 9 scenario rows, hold = sig → next opposing-dr
sig (the §20 baseline hold). Joe 0924 set the bar: *">=0.7% in the direction that opposes dr"*.

| | |
|---|---|
| ≥ 0.700% | 7 of 9 rows |
| min / median / max / mean | 0.086 / 1.561 / 4.667 / 2.053 |
| the two misses | 09-02 07:30:30 at 0.302, 09-05 06:29:25 at 0.086 |

n is 9. Nothing about reliability rests on more than 9 episodes.

### 21.4 MINE, AND UNRULED BY JOE

| | |
|---|---|
| the OR | Joe said "bake it into rule#1", not how the two legs combine. A row-level OR is what the producer does. It adds exactly the 2 differences his chart read said it should |
| the comparison | STRICTLY outside the fence and STRICTLY outside oob, never `>=` or `<=`. Measured on the same 121 rows: switching to inclusive changes **0 rows** |
| `dwell bars` | reports the rule#1 leg only, so a row opened by the scenario alone reads 0. A reporting field, never a gate |

### 21.5 NOT CAUSAL AT THE SIGNAL BAR

Joe 0924 ruled the window is "within (either side)", so the gate reads 42 bars AFTER the signal
and is knowable 210 s late. His rule, recorded here so no caller mistakes it for a live gate.

### 21.6 NOT IN `wsf_dtf_v3_config`

`rule1_tol` 7 min, the 27/73 fence and the ws2r/ws3r/gcws30r line set are Joe's values, said in
chat and held as module constants in `report_rule1_gate.py`.

Banking them needs a new config version, and `leash_bank.knob_string` puts the config version
INSIDE `wsl_knobs` — the v7/v8 in the 121-row bank IS the config version. A v11 would make the
next leash bank write `v11_…` and split it off from the rows this report reads. **That consequence
is Joe's to sanction, so nothing was written.**

The two divergence knobs ARE banked and are read from the config: `anchor_floater.block` 60 bars
(v9) and `anchor_floater.dwell_min_per_tf` 1 min per timeframe (v10).

### 21.7 THE CODE

| | |
|---|---|
| `optimus9/compute/rule1_gate.py` | the decision. Owns no threshold — fence, oob, window and verdict all arrive as arguments. No DB, no printing, no line building |
| `report_rule1_gate.py` | loads the lines, runs `anchor_floater`, prints. `--instance v7\|v8`, `--md` |
| `rule1_gate_20260924.txt` | the banked output, v7, 121 rows |
| `rule1_verdicts_FROZEN.txt` | the pre-scenario freeze, taken before Joe shared any of his own verdicts |

---

## 22. RULE#2 — THE TRAJECTORY WALK, Joe 0924

### 22.1 THE PREMISE — Joe verbatim

> "the general premise of #2 is this: if a signal prints when ws[1,2,3]r has not completed its
> cycle, we walk them to completion if they are showing trajectory towards dr
> -"trajectory" is detected when any of the 3 lines are travelling towards dr, for more than 2
>  minutes. this can be measured by looking back across the line to find its dr-opposed extrema"

**ONLY THE FIRST MECHANISM IS BUILT.** `trajectory` answers "is this line travelling towards dr".
The walk to completion — what a completed cycle is, what the walk does, where it ends — is not
built and not specified.

### 22.2 THE LOOK-BACK — Joe 0924

> "use the same mech the divergence uses to discover an extrema - look back in 5 minute windows"

That is `anchor_floater` step 3's block walk, mirrored:

| | |
|---|---|
| block n | `[k − n×block, k − (n−1)×block)` — the test bar itself is excluded, as step 3 excludes the pivot |
| block size | `anchor_floater.block` 60 bars = 300 s = 5 min, banked at config v9 |
| each block yields | its **dr-opposed** extreme. dr +1 → the block minimum, dr −1 → the maximum |
| an empty block | SKIPPED, not a stop — Joe 0921 |
| the walk ends | at the first block that does not improve the running best |
| trajectory | the extrema is more than 2 min back AND the travel from it runs towards dr |

**NO 50 FILTER.** Step 3 masks to bars on the dr side of 50. Joe 0924, asked directly:
*"yes: there is no 50 filter"*.

### 22.3 WHY BAR-TO-BAR WAS THE WRONG READING

Measured at 09-03 02:52:20 before Joe ruled — all three lines tick DOWN on the signal bar:

| line | previous bar 02:52:15 | test bar 02:52:20 | tick |
|---|---|---|---|
| ws1r | 87.90 | 79.72 | −8.18 |
| ws2r | 53.47 | 44.84 | −8.63 |
| ws3r | 66.33 | 56.42 | −9.91 |

An unbroken-climb test returns **0 bars on every line**. Travel measured extrema-to-bar does not
care. Joe 0924: *"gap2 might not be a gap if you have the correct extrema"*. It was not.

### 22.4 THE TESTCASE — 09-03 02:52:20, dr +1

| line | dr-opposed extrema | value | bars back | min back | travel | TRAJECTORY |
|---|---|---|---|---|---|---|
| ws1r | 09-03 02:42:35 | 11.02 | 117 | 9.8 | +68.70 | YES |
| ws2r | 09-03 02:46:30 | 25.21 | 70 | 5.8 | +19.63 | YES |
| ws3r | 09-03 02:51:20 | 54.72 | 12 | 1.0 | +1.69 | no |

Joe 0924: *"your results match mine"*.

ws3r fails on **time**, not direction — its extrema is 1.0 min back against a 2 min threshold.

### 22.5 THE FIRST FLAT-RUN IN THE TWO LINES WITH TRAJECTORY

Forward from 09-03 02:52:20, no limit. `flat_run_at` at the r-momo fence 17/83, samples 3 bars,
tol 2.0 r-points — the same knobs `all_wsf_flatruns` is banked on:

| line | first flat-run bar | min after the signal | r there | run span |
|---|---|---|---|---|
| ws1r | 09-03 03:54:10 | 61.8 | 92.00 | 0.00 |
| ws2r | 09-03 03:56:10 | 63.8 | 83.43 | 0.00 |

### 22.6 NOT IN `wsf_dtf_v3_config`

The 2 minute threshold is Joe's value, said in chat, held by the caller. `block` is banked —
`anchor_floater.block` 60 bars, v9. §21.6 holds the reason no new config version has been written.

### 22.7 THE CODE

| | |
|---|---|
| `optimus9/compute/rule2_trajectory.py` | `opposed_extrema()` and `trajectory()`. No DB, no printing, no thresholds of its own |
