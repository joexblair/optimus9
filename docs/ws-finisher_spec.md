# ws-finisher spec

Opened 2026-08-17. Joe: *"we can begin the ws-finisher spec now. bank domTF, then purge it from
your memory - it's important that you don't conflate domTF with ws-finisher, and more important
that you don't bring any other logic into the is spec dev (besides what I directly ask of you)."*

**NOTHING FROM domTF IS IN THIS SPEC.** No stall, no handover race, no median line, no momentum
check, no tagged group, no HTF-curl. domTF's own spec is `domTF-finisher_spec.md` and it stays
there. The only thing this spec takes from that side of the house is the `domTF` state column,
read as given from `v_ws_fin_walk` — Joe 0817: *"don't spend time validating my domTF claims: I'm
manually validating against the raw data from the v_ws_fin_walk view."*

---

## the preamble, Joe 0817 verbatim

> Mage's purpose is to travel from source oob to target oob, in an endless loop, matching the ebb
> and flow of pxs.
>
> a smaller TF's Mage forms the tail of a higher TF's Mage
>
> when Mage is oob, it's strength will wane. this waning is the moment of weakness

## the weak-mage-tf mechanism, Joe 0817 verbatim

> when the market loses momentum and becomes weak, all of the finisher Mages will reverse (to
> continue matching pxs'a ebb and flow)
>
> wsf9of12 events are positioned to capture these reversal patterns. all weak-mage-tf data
> collection will take place when wsf9of12 fires
>
> when this reverse happens, the individual TFs will each have their own value for Mage. because a
> higher TF is slower moving than a LTF, a higher TF may not have reached target oob before the pxs
> reversal
>
> this disparity between a lower and higher TF Mage forms a load bearing decision: if a higher TF
> (eg 4) Mage's value is IB, and the lower TFs (1,2,3) are in the target oob, it proves that the
> higher TF Mages line is exhausted and a trade signal is created
>
> to find weakness, the code will scan the Mage values, upwards from TF1 to TF8, to find the first
> mage that is not OOB
>
> the first Mage that prints an IB value, is the weak-mage-tf

---

## THE RULE, as built

Producer: `jig.weak_mage_tf`. Runs at every `ws_fin_9of12` signal bar, and only there.

1. Scan ws1Mage, ws2Mage, ... up to ws8Mage, in that order.
2. A line counts as out of bounds if it was out of bounds at **any** bar inside the lookback
   window, not only at the signal bar.
3. The **weak-mage-tf** is the first line in the scan that was not out of bounds at any point in
   that window.
4. If every line from TF1 to TF8 was out of bounds inside the window, the weak-mage-tf is
   **None**. That is a result, not a failure. Joe 0817: *"no signals are created, but a stub needs
   to capture and report this when it happens."* Every such bar is kept in `ws_fin_weak_mage`
   with each line's seconds-since-last-out, so the reason is on the row.

### rule C

Joe 0817, the original wording: *"if weak-mage-tf == None and domTF state is FREE, fire a trade
signal"*.

**CORRECTED, Joe 0826, verbatim:** *"I've missed a step in this, and it's the reason why TF1 is
excluded from weak-mage-tf: the rule should read `if weak-mage-tf == None and domTF state is FREE,
fire a trade signal on the next ws2x-cross`"*.

So rule C does NOT fire at the exhaust bar. It walks forward to the next ws2x-cross, the same way
a named weak-mage-tf walks forward to its own line's cross. **ws2 is the fallback line when the
scan from TF2 upward finds no Mage that is inside the fence.**

Joe gives TF1's exclusion from the weak-mage-tf scan (`WMT_TF_LO` = 2, Joe 0821) as the reason for
this step. He has not said more than that.

**THE CROSS IS THE RACE**, as it is for a named weak-mage-tf. Joe 0818: *"use ' x X [MAge,b,boundary]'
for now"* and *"any one - race condition"* - `wxc_race_won` on `wsf_x_cross` at `XCROSS_XWOB` = 5
bars = 20 s hold.

### the dtf-free assumption, Joe 0826

Joe 0826, verbatim: *"for the duration of our wsf modelling, assume that dtf-free == true"*.

Rule C's second condition - *"domTF state is FREE"* - is therefore held TRUE for every bar of the
wsf modelling. Nothing reads `dtf_delegation` and nothing tests a dtf block.

**IT IS AN ASSUMPTION, NOT A MEASUREMENT.** It is scoped to the modelling and expires when Joe
lifts it. Joe 0824 on the real thing: *"not yet; we need to build our wsf fu first. it's on my
radar."*

### direction

Joe 0817: *"confirm you are using dr to identify the direction. adding new LONG/SHORT logic isn't
SRP - dr gives us all that we need for postitioning and trade direction."*

The producer reads `dr` and tests its sign. It holds no LONG/SHORT logic and never converts the
bias to a word.

### settled against Joe's own reads, 08-04

| signal bar | dr | weak-mage-tf | domTF | rule C |
|---|---|---|---|---|
| 10:53:35 | +1 | TF8 | FREE | — |
| 11:34:00 | −1 | TF2 | FREE | — |
| 08:02:50 | +1 | TF4 | BLOCKED | — |
| 04:49:15 | +1 | None | FREE | fires |

Joe read all four. On 04:49:15 he first said TF2, then: *"I agree with your 04:49 view -
weak-mage-tf = None"*.

---

## what is banked

| | |
|---|---|
| `jig.weak_mage_tf` | the producer |
| `build_ws_finisher.py` | runs it over every signal in `v_ws_fin_walk`, applies rule C, writes the table |
| `ws_fin_weak_mage` | one row per signal, including every bar with no weak-mage-tf. The knobs are in the unique key |

---

---

## THE r LINE'S MOMENTUM DIES WHEN IT LEAVES momo-fence-r OR STALLS. Joe 0820

> IF a momentum-true r line leaves momo-fence-r or stalls THEN its momentum = false (or none).

The first form of this rule, given earlier the same day, tested the global 85/15 boundary. Joe 0820
replaced it: *"we need to shrink the fence: ws8 needs to be printing `OOB` at 08:02:50 so that it's
momentum is none, but I don't want it to be global. create a new fence: momo-fence-r 100-{knob:17}"*.

**THE 0817 WORDING IS DELETED.** It read *"wsf-momoc (ws strategy->finisher mech->momo or curl) and
wsf-exhaust (stall OR reverse OR (cross into oob))"*. Joe 0820: *"I've conflated terms. the first
statement was meant to target r lines, but I've referred to it as if it were machine states - delete
the 0817 note"*. The rule above replaces it and applies to a LINE, not to a machine state.

### what it is

| | |
|---|---|
| the lines | `ws{tf}r` only, TF1 to TF8 |
| momentum-true | the producer's verdict is `momo` or `curl` — Joe 0817: *"(curl or momo) create wsf-momoc"* |
| left momo-fence-r | at or past **83** on an upward read, at or below **17** on a downward read — the side the line is read |
| stalled | `STALL_N` 6 lattice samples in a row with no new extreme |
| the result | the verdict reads `none` |

### momo-fence-r

Joe 0820 writes it as `100-{knob:17}`, so the band is 100 − 17 = **83** at the top and **17** at the
bottom.

| | |
|---|---|
| the knob | `MOMO_FENCE_R` = **17**, in `build_wsf_line_bar.py`, in the unique key |
| the band | 83 / 17 |
| the column | `wflb_mfr_out` — 1 when the line has left the band on the side it is read |
| what else reads it | the `heading` column in `report_wsf_bar.py` |

### last-verdict-dwell

Joe 0820: *"add a `last-verdict-dwell` column. report the seconds that have past since the verdict
changed"*. Stored as `wflb_verdict_dwell` on `wsf_line_bar`, in seconds, 0 on the bar the verdict
changed. It counts from the start of the window, so the first bars of 08-04 undercount.

**IT IS NOT GLOBAL.** The 85/15 boundary in `optimus9_system` is untouched, and `wflb_oob` still
reports against it. Two fences now sit side by side on the row: `wflb_oob` against 85/15, and
`wflb_mfr_out` against 83/17. Only the second one feeds this rule.

MOVED ONTO momo-fence-r, Joe 0820 *"apply the fence to this mech"*: the `heading` column's
"already past its fence" test in `report_wsf_bar.py`. It now reads `wflb_mfr_out`.

STILL ON 85/15, because Joe has not moved it: the `r IB` column's "inside the fence" test. That
leaves a band between 83 and 85 where a line reads `away` (it has left momo-fence-r) and still
counts as inside the fence, so `r IB` prints yes there.

### where it lives, and where it does NOT

- it lives in `build_wsf_line_bar.wsf_verdict()`, and its answer is stored as `wflb_verdict`.
- **`momo_core.verdict()` is untouched.** That producer is shared with domTF, the s46 path and RPL,
  none of which Joe has asked to change. Putting the rule there would move domTF's verdicts silently.
- **`wflb_ungated` is untouched.** It keeps the producer's own answer, so the raw measurement and
  the rule applied to it both sit on the row and either can be read back.

### the reading, and the knob

`MOMO_KILL` in `build_wsf_line_bar.py`, in the unique key so another reading lands alongside.

| reading | what turns the verdict to none | rows affected on 08-04 |
|---|---|---|
| **`state`** — the current setting | the line **is** out of bounds, or **is** stalled | **52,359** |
| `moment` | only the bar it crossed, or the bar the stall began | 2,138 |
| `off` | nothing; the producer's own verdict stands | 0 |

`state` is the setting because Joe wrote *"it's momentum = false"* — the line's condition, not a
one-bar event. Under `moment` the verdict would print `none` for a single bar and return to `momo`
on the next, which is a blip rather than momentum being false. THE 25x GAP BETWEEN THE TWO READINGS
IS WHY THIS IS A KNOB.

### what is still unbuilt

The three-state flow — wsf-momoc, wsf-exhaust, wsf-momo-none. Joe 0820: *"flow = wsf-momoc ->
wsf-exhaust -> none -> wsf-momoc. 'none' occurs when a trade fires, or when domTF blocks (overrides
excluded). wsf-momoc needs to be re-aquired after a none state"*, and *"let's rename 'none' to
`wsf-momo-none`"*. Five questions on it are open: what acquiring wsf-momoc means, whether the
all-in-bounds reset fires wsf-momo-none, whether a domTF block is a moment or a stretch, the
starting state, and whether one bar can hold two changes. `report_wsf_bar.py` prints a footer that
reads ONE BAR under the IF/ELIF and carries no history.

**NOT BUILT.** Nothing in the code produces either state. What is settled:

| | |
|---|---|
| the lines | `ws{tf}r` only. Not Mage, not x, not b |
| coverage | TF1 to TF12. Joe 0826: *"wsf is limited to TF12. 13 to 27 belongs to dtf, which is not our current task"*. Was TF1 to TF8 |
| the two are exclusive | only one is active at a time |
| what wsf-momoc does | blocks all trade activity |
| what wsf-exhaust does | arms the weak-mage-tf. The trade signal then fires when ws{weak-mage-tf}x crosses ws{weak-mage-tf}r |
| **what is unknown** | how the per-line states combine into "true for the lines" — per line, or one verdict over all eight. Joe 0817: *"these 2 states are the output of the modelling"* |

### the maxTF declaration, Joe 0819

**When the maxTF line is carrying momentum and its verdict flips to none, wsf-exhaust is declared.
No lower line is read.**

Joe 0819, the instruction to bank it, verbatim:

> *"add this to the spec and re-create:*
> *- stall TF values can only increase (eg a ws6r stall event cannot happen after a ws7r stall)*
> *- when ws8r stalls or crosses to oob, wsf-exhaustion is declared"*

Joe 0819, concreting it after correcting my wording, verbatim:

> *"ws8r is the highest TF, so the wsf-exhaust signal is created when ws8r stalls or crosses into
> oob"*

Joe 0819, the precondition, verbatim: *"it needs to be carrying momentum before it"*.

Joe 0819, his own worked example eg#2, verbatim: *"08:00 wsf9of12 and ws8r crossing to oob. ws8r is
the highest TF, so the wsf-exhaust signal is created"*.

**HOW IT IS READ TODAY.** Joe 0821 moved the stall-or-oob test into the verdict column: *"IF a
momentum-true r line crosses into oob or stalls THEN it's momentum = false (or none). this needs to
show up in the `verdict` column"*. So the declaration now reads off `wflb_verdict` on the maxTF
line: momo -> none.

**ws8r IS NOT A CONSTANT.** Joe wrote ws8 because TF8 was the ceiling on 0819. The rule names the
maxTF line. maxTF is 12 from Joe 0826.

**MEASURED, 08-04, dr +1, maxTF 12.** ws12r sits at 78.53 inside momo-fence-r 83 through 02:47:55
carrying momo. Its 12-minute bar forms at 02:48:00 and it prints 88.10, past both momo-fence-r 83
and the 85/15 system boundary. The `MOMO_XWOB` hold of 4 bars = 20 s completes at **02:48:15** and
`wflb_verdict` flips momo -> none. wsf-exhaust is declared there.

At that bar ws1r reads 60.83 and ws5r reads 66.12, both momo, both inside the fence. **Neither
blocks the declaration** - they sit below the ceiling and the rule does not consult them. Joe 0826
confirmed the event: *"02:48 is perfect"* and *"02:48:15 is a normal wsf-exhaust moment, which is
also ok and correct"*.

**WHERE IT WAS.** Joe asked for it in this spec on 0819 and it never landed here. It is not in
`build_wsf_walk.py` either - that walk's exhaust test reads every line and has no maxTF branch.
Restored 0826.

**THE TWO COMPANIONS FROM THE SAME 0819 MESSAGE ARE STILL ABSENT**, and Joe has not ruled on
restoring them: the stall-TF ratchet (*"stall TF values can only increase"*) and the latch reset
(*"latch 1 and 2 reset on a trade fire, or when all ws{current-max-tf-with-momentum} lines are
IB"*).

### carry-forward

Joe 0817, the 11:34:00 case: *"11:34 is dr -1. at ~11:32, ws1r stalled and reversed. this state
should be carried forward to the 11:34."*

Joe on the window: *"there is no window for this mechanic - 'carried forward' = hold on to the last
momoc/exhaust state (which would be produced at 11:32, if the code was already built to handle
reversals)."* So the state is held indefinitely until the next one replaces it. There is no decay
and no expiry.

### Joe's answers to the six open questions, 0817

| # | question | Joe |
|---|---|---|
| 1 | is the reverse in wsf-exhaust the stall's reverse, or its own thing | *"we can't derive this yet. building a reversal producer is the next step"* |
| 2 | what separates stall from sideways | *"we need to know 1) the difference between the stall mech and the sideways mech, 2) why did 11:33:30 report 'none', while the prior bar was 'sideways' - ie why did it flip at that moment?"* — both measured below |
| 3 | is the wsf stall the same code as the domTF stall | *"domTF and wsf stall logic are the same. the only difference would be in the sampling interval - less width for smaller TFs"* |
| 4 | what sampling width for TF1-8 | *"we'll need to tune it based on the results. I don't know what results I'm looking for yet"* — OPEN |
| 5 | the carry-forward window | no window, hold the last state |
| 6 | which side does "cross into oob" mean | *"yes, same-side dr. eg dr +1 = crossing over 85"* |

### the answer to question 2, measured on ws1r 08-04

**stall and sideways measure different things.** Sideways is about the SHAPE of the fitted window:
a near-straight line whose slope is under the floor, with too little bend to be a curl. Stall is
about EXTREMES: N samples in a row with no new extreme. They can be true at the same time and
neither implies the other.

Proof on the same line and window — ws1r holds 17.11 from 11:31:40 to 11:32:10, which is a stall,
while the verdict reads `sideways` throughout at slope about -0.8. At 11:32:25 it prints 15.77, a
new low, and the stall breaks. `sideways` carries on to 11:33:30 regardless.

**why 11:33:30 flipped.** Read downward, one bar apart:

| bar | ws1r | slope | fit | bend | turning point | verdict |
|---|---|---|---|---|---|---|
| 11:33:25 | 16.86 | -0.563 | 0.494 | 14.05 | 0.985 | sideways |
| 11:33:30 | 16.86 | -0.615 | 0.520 | 17.65 | 0.883 | curl |

Two gates flip on the same bar. The bend measure (bend x 0.25) goes 3.51 to 4.41, crossing the 4.0
floor; the turning point moves from 0.985, outside the 0.05-0.95 band, to 0.883, inside it. So the
raw verdict is `curl`. The gated verdict then prints `none`, because for a downward read the gate
requires the bend to be negative and it is +17.65 — the line is bending UP under a downward read.
That is the reversal Joe saw at 11:32, and the gate throws away the number that proves it.

**This is why the reversal producer is the next step, and why the momo refactor comes first.** See
`docs/handover_momo_refactor.md`.

---

## KNOBS

| knob | value | what it does |
|---|---|---|
| `WMT_LOOKBACK_S` | **120 seconds** | the lookback tolerance. A Mage that was out of bounds at any bar inside this window still counts as out. Joe 0817: *"add a lookback tolerance to capture Mage values that were recently oob. knob:120sec"*. At the 5-second grid that is 25 bars, the signal bar included |
| `WMT_TFS` | **1 to 8** | the timeframes the scan walks, in order. Joe 0817: *"confirmed: TF1 to TF8"* |
| `WMT_SAME_SIDE` | **True** | with it on, a line's out-of-bounds readings only count on the side `dr` points at. With it off either side counts. Joe 0817: *"unsure. create a knob for it. default to same-side"*. The definition of what same-side means is mine and is untested |
| the boundaries | **85 / 15** | read from `optimus9_system`. Joe 0817: *"85/15 is good for now, BUT the final spec will have fuzzy logic applied to boundaries. the final spec will be model based"* |
| `STALL_N` | **6** | consecutive lattice samples with no new extreme in the direction the line is read. Joe 0819: *"add this to the knobs"*. No boundary condition — the domTF spec, 0814: *"a stalled line has stopped moving wherever it sits"*. Inherited from `build_ws_fin.py`; the wsf sampling width around it is Joe's held task #60 |

### the momentum knobs — one bank per machine, 0903

Joe 0903: *"I want the settings to be global per machine, ie dtf and wsf will have their own
config. individual configs can be applied to single line (if needed in the future)"* and *"wsf and
dtf become internal labels that apply to different indicator groups"*.

They live in the `momo_config` table, built by `build_momo_config.py` and read by
`optimus9/compute/momo_config.py`. **THE LOOKUP TAKES A TIMEFRAME, NOT A MACHINE NAME.** The bands
do not overlap, so a line's own timeframe picks its bank and no caller ever asserts a machine — a
producer that could name a machine could name the wrong one, which is exactly what happened on 0903
before the split.

| bank | timeframes | set by |
|---|---|---|
| `wsf` | **1 to 12** | Joe 0826: *"wsf is limited to TF12"* |
| `domtf` | **13 to 60** | Joe 0813: *"make the domTF range 13 to 27"*, extended to 60 on 0903 when asked whether the band runs 13 to 60 — *"yes"* — after the ws30, ws45 and ws60 lines joined the cache |

Both banks are at version 1 and hold identical values. Joe 0903: *"we have the wem table
duplicated, so I'm fine for wsf to inherit the dtf config"*. They are separable from row one; they
are not different yet.

| knob | v1 | what it does |
|---|---|---|
| `momo_slope_min` | **1.2** | slope floor, r-points per sample. Under it the fit reads flat. **Was 1.0** |
| `momo_r2_min` | **0.70** | how straight the straight-line fit must be to read as a line, 0 to 1. **Was 0.50** |
| `momo_window_min` | **60** | the default fit window in minutes, before `k_window` scales it per line |
| `momo_step_min` | **5** | minutes between fit samples. 5 min = 60 bars at the 5-second grid |
| `momo_fixed_samples` | **21** | points in the fit. A fixed count scales the gap with the line instead of the count. Joe 0814, made global 0820 |
| `k_window` | **6** | the fit window is `k_window` × the line's own timeframe, in minutes. **Was 4.** Joe 0810 set the shape; 0903 set the value and moved it out of `build_momo_landed.py` |
| `level_slack` | **13.9** | how far the 50 gate slackens for a cleanly tracking line. Joe 0731 *"coin-toss it"* |
| `curl_arc_min` | **4.0** | how much the line must bend to read as a curl rather than sideways. Joe 0731 |
| `curl_vtx_lo` | **0.05** | the bend's turning point must sit past this fraction of the window |
| `curl_vtx_hi` | **0.95** | and before this one. Not on either edge |
| `curl_r2_min` | **0.40** | how well the BENT fit describes the window, 0 to 1. Joe 0805, chosen to clear the errant 07-27 09:19 curl |

**HOW `momo_slope_min`, `momo_r2_min` AND `k_window` GOT THEIR 0903 VALUES.** A 75-setting grid,
scored against eight 08-04 pivots Joe eyeballed at ±22 minutes, on **ws20r only**. Joe 0903: *"good
work - bake it in"*. **FITTED, NOT MEASURED**, and fitted on one line in the `domtf` band. The
grid's ceiling was 6 of 8 — at the 17:00 dr −1 and 21:25 dr +1 pivots ws20r reads `none` for the
whole 20 minutes beforehand, so no setting can produce a flip there. Joe 0903 on those two: *"21:25
and 17:00 are ok. if they are both none, then wsf is free to handle the trade decisions"*.

**UNBOUND RAISES.** `momo_core` ships with all of these set to `None`. A producer that calls the
verdict without naming a timeframe gets a plain error, not another band's numbers. There is
deliberately no default — a default is what let one machine borrow another's values.

    from optimus9.compute.momo_config import momo_bank, momo_config
    with momo_config(momo_bank(db, 20)):     # timeframe 20 -> the domtf bank
        ...

**A SWEEP MUST PASS A VERSION.** Carried over from `line_config.py:167`: reading the live bank
during a sweep means a live config change mid-run silently alters the run, and nothing on the rows
says so.

### the dtf knobs

Joe 0903 moved these here: *"dtf and wsf knobs will both live in the wsf spec"*. That overrides
this spec's opening line, which says nothing from domTF is in it. The domTF **mechanic** still
lives in `docs/domTF-finisher_spec.md`; only its knob values are recorded here.

| knob | value | where | what it does |
|---|---|---|---|
| `DOMTF_MIN` / `DOMTF_MAX` | **13** / **27** | `build_ws_fin.py` | shortest and longest timeframe the domTF layer may use. Joe 0813: *"make the domTF range 13 to 27"* |
| `DOMTF_HTF_BAND` | **(22, 27)** | `build_ws_fin.py` | when a line in this band has recently curled into the move, only this band may end the domTF turn. Joe 0814: *"from 22-27 (semi arbitrary)"* |
| `CURL_RECENCY_TF_BARS` | **2** | `build_ws_fin.py` | how recent that curl must be, in bars of the line's OWN timeframe. 44 min on ws22r, 54 min on ws27r. Joe 0814 |
| `RESCUE_REJECTED_CURL` | **True** | `build_ws_fin.py` | a bend thrown away for pointing against the move still counts as a vote the other way. Joe 0813: *"yes"* / *"if other lines are backing the curl line, it has considerable weight"* |
| `HANDOVER_RULE` | **'median'** | `build_ws_fin.py` | `'first'` is the race, first past the post. `'median'` is one watched line, the median of the tagged group, re-derived every bar. Joe 0814: *"this is, in part, our AB between task8 and task9"* |
| `STALL_N` | **6** | `build_ws_fin.py` | lattice samples in a row with no new extreme. Joe 0810 set 3; Joe 0814 raised it to 6 because at 3 the stall won 48 of 51 handovers |
| `HANDOVER_XWOB` | **4** | `build_ws_fin.py` | bars the fast partner must hold on the far side of its r line |
| `NESTED_OPPOSITION_MIN` | **3** | `build_ws_fin.py` | how many r lines must print a reversal or curl before the opposition counts. Joe 0813: *"there has to be a domino effect for the logic to be stable"* |
| `FENCE_OVERRIDE` | **None** | `build_ws_fin.py` | `None` uses `optimus9_system`'s 85 / 15. A pair runs one walk at a different fence and writes nothing back |
| `G30_LEVEL` | **'g30_marker'** | `build_ws_fin.py` | Joe 0813 named it |
| `XWOB` | **2** | `build_ws_fin.py` | bars held, for the 9-of-12 signal |

### the wsf knobs

| knob | value | where | what it does |
|---|---|---|---|
| `TFS` / `MAX_TF` | **1 to 12** | `build_wsf_line_bar.py`, `build_wsf_walk_events.py` | the lines wsf measures. Joe 0826: *"wsf is limited to TF12. 13 to 27 belongs to dtf"* |
| `STALL_N` | **6** | `build_wsf_line_bar.py` | lattice samples with no new extreme. Inherited from `build_ws_fin.py`. The wsf sampling width around it is Joe's held task #60 |
| `MOMO_FENCE_R` | **17** | `build_wsf_line_bar.py` | momo-fence-r, so the band is 83 at the top and 17 at the bottom. Joe 0820: *"create a new fence: momo-fence-r 100-{knob:17}"* and *"I don't want it to be global"* |
| `MOMO_XWOB` | **4** | `build_wsf_line_bar.py` | bars the line must hold outside momo-fence-r. 4 bars = 20 s. Joe 0821: *"add an {knob:4} xwob to the fence exit"* |
| `MOMO_KILL` | **'state'** | `build_wsf_line_bar.py` | `'state'` = the line IS outside or IS stalled, so the verdict is none. `'moment'` = only the crossing bar. `'off'` = no override. Joe 0820: *"it's momentum = false"*, which describes a condition |
| `MAGE_KNOB` | **20** | `build_wsf_walk_events.py` | the three-Mage dr fence is 80 / 20. Joe 0823 |
| `DR_LOOKBACK_S` | **180 seconds** | `build_wsf_walk_events.py` | Joe 0823: *"restrict the lookback to 3 minutes"*. 36 bars at the 5-second grid |
| `XCROSS_XWOB` | **5** | `build_wsf_walk_events.py` | bars the x must hold on the far side. 5 bars = 20 s |
| `XCROSS_TARGET` | **'r'** | `build_wsf_walk_events.py` | what the x crosses. Joe 0828: *"add this as a knob - we'll chose the better option later"*. Open as task #61 |
| `HIGH_TF_GAP` | **15.0** | `build_wsf_walk_events.py` | the r gap under which the H+1 line takes the ungated cross. Joe 0828 |
| `DR_SEED` | **+1** | `build_wsf_walk_events.py` | Joe 0829: *"I can tell you that 08-04 starts the day on dr +1"* |
| `HO_RULE` / `LINE_HCAP` | **'median'** / **'ws1b:1'** | `build_wsf_walk_events.py` | which `ws_fin_9of12` variant sets the dr. Four are stored per day |
| `WMT_TF_LO` / `WMT_TF_HI` | **2** / **12** | `build_wsf_walk_events.py` | the weak-mage scan's floor and ceiling. Joe 0821, then Joe 0826: *"weak-mage-tf scan is now TF2 to TF12"* |
| `MAX_TRADES` | **2** | `build_wsf_walk_events.py` | Joe 0825: *"allows pyramiding, max 2 trades"*. Open as task #7 |
| `WS1X_GATE` / `WS1X_XWOB` | **0** / **4** | `build_wsf_walk_events.py` | the ws1x entry gate, off. Joe 0828: *"wob 4"* |
| the 5-second grid | **5 seconds** | `GRID_S`, `GRID` | seconds per bar. Not a knob — the tape's resolution |

**TWO ENTRIES ABOVE CONTRADICT WHAT IS WRITTEN ELSEWHERE IN THIS SPEC.** Recorded, not resolved:

- `WMT_TFS` in the table at the top of this section says **1 to 8**, from Joe 0817. The code runs
  **2 to 12**, from Joe 0826. The later ruling is in the code; the earlier one is still in the table.
- `build_wsf_walk_events.py:63` holds a literal knob signature,
  `kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_mkstate_mf17_xw4`. It names the momentum
  knobs at their pre-0903 values, and it is a POINTER to the `wsf_line_bar` rows banked under that
  signature, not a setting. It is correct for the rows that exist today. The next
  `build_wsf_line_bar` run banks under `kw6_..._r20.7_sl1.2_...` and this literal will no longer
  find them.

### knobs this spec does not own

| value | where it is set | note |
|---|---|---|
| everything that makes a wsf9of12 bar | `build_ws_fin.py`, `jig.py` — listed in `docs/domTF-finisher_spec.md` → KNOBS | the signal bars are an INPUT here. Changing any of them changes which bars this spec runs on, but they are not knobs of this spec |
| the `domTF` state column | `v_ws_fin_walk` | read as given. Joe 0817: *"don't spend time validating my domTF claims"* |
| `MOMO_CHECK_TFS` **2 to 10** | `optimus9/analysis/jig.py` | coverage for the ad-hoc momentum reports Joe asks for by timestamp. Joe 0816: *"permanently include ws[2,3,4,5]r in the momo check"*, then *"reduce coverage: ws2 to w10"*. The wsf per-TF reads use TF1 to TF8 instead |

### knobs this spec needs and does not have

| knob | state |
|---|---|
| the wsf stall's sampling width for TF1-8 | UNSET. Joe 0817: *"less width for smaller TFs"* and *"we'll need to tune it based on the results. I don't know what results I'm looking for yet"* |
| whatever the reversal producer needs | UNSET. Not built |
| how per-line states become "true for the lines" | UNSET. Joe 0817: *"these 2 states are the output of the modelling"* |
