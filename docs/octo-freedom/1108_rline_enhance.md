# `fdm2-rline-enhance`, 2026-11-08

GOAL: spawn an `fdm2-xcv` verdict at a bar where all four left r lines are blind, so the verdict
TIMESTAMP lands earlier. HIS 1108: *"the goal of this work is to improve the verdict timestamps in
fdm2-xcv"*. It exists for no other reason, and `fdm2-xcv`'s own goal is in
`1107_sandbox_xcross.md`.

PLAINLY: inside a forming candle only one piece of an r line can move. When the RSI under that line
runs past the edge of its own recent range, that piece sticks at its limit and the line freezes -
at any level, not only at an extreme - while the RSI keeps moving. At a bar where all four of
ws30r, ws29r, ws28r and ws27r read `flat` against the anchor, the four lines say nothing and the
RSI under them is the only thing left. This reads that RSI and spawns a verdict there.

NOTHING IS BUILT. Every rule below is settled; the code is not written.

---

## 0. HIS RULINGS, 1108

| his ruling | his words |
|---|---|
| it is worth trying | *"if it works, good, if not: at least we tried"* - on the reading being ours and not a documented practice |
| which RSI | *"developing"* - `rsi_d` at the 5 s grid, the series the r line itself uses |
| whose read | *"new reader, on the jig"*. `RSIDIV_LINES` stays at its banked `ws1r, gcws30r` and `bullish-rsi` / `bearish-rsi` is untouched |
| the cost | *"the cost is accepted"* |
| the name | `fdm2-rline-enhance`, replacing his placeholder `fdm2-name-me-joe` the same day |
| three substituted tokens alone | *"yes"*, with his reasoning *"my view is that if the answer was no, the timestamps would never have a chance to improve"* |
| the wiring | *"the earliest 4-flat bar be in a race with the cad-walks fires"* |
| where the verdict spawns | *"whatever mech created the earliest 4-flat bar timestamps is where the verdict will be spawned from"* |

## 1. THE SPAWN POINT - HIS RULE, AND IT REPLACED MINE

HIS RULE: the verdict spawns at the EARLIEST BAR WHERE ALL FOUR left tokens read `flat` against the
anchor - the 4-flat bar. Nothing spawns at a 3-flat or 2-flat bar.

MINE, REPLACED: substitute a `flat` token wherever one appears, at any bar. His rule is tighter and
it is the one that makes his race real. Under mine the two readings could never race: substitution
only turns `flat` into `up` or `down`, so the up and down counts can only rise, and the enhanced
reading would fire at or before the raw one every single time. Under HIS rule the two triggers are
DISJOINT - the raw reading needs 3 raw tokens agreeing, so it can only fire at a bar with at most 1
flat; this one fires only at a bar with 4 flat. Neither can pre-empt the other by construction.

| the racer | its trigger | what it reads |
|---|---|---|
| the cad walk, banked | 3 of the 4 raw tokens agree | the r lines' own directions against the anchor |
| `fdm2-rline-enhance` | all 4 raw tokens read `flat` | the RSI's direction against the same anchor, on each of the 4 lines |
| the winner | the earlier bar | a tie is not possible - the triggers cannot both hold at one bar |

## 2. THE SEVEN RULES

Five fell out of his goal statement, one out of his standing no-cap rule, one he ruled directly.

| the rule | the ruling | where it came from |
|---|---|---|
| what counts as blind | THE PIN CONDITION - `rsi_d` at or outside the window of the 7 closed RSI values. NOT "the value is unchanged from the previous bar" | derived from his goal: only the pin carries a direction, and a repeated value happens on 29.6% to 38.9% of all bars |
| what the reader returns | a direction token - `up` or `down` - in the vocabulary the 3-of-4 read already consumes, with the pinned state and the pin side beside it as evidence | derived: only a token can move a verdict timestamp |
| where the direction is measured from | THE CALLER'S ANCHOR, the same bar the raw tokens use - the x-cross for the cad walk, under his 1108 anchor ruling | derived: a substituted token sits beside three measured anchor-to-bar |
| which lines | ws30r, ws29r, ws28r, ws27r. The producer takes ANY tf; the caller picks the set, so no knob is needed | derived: his goal names `fdm2-xcv`, whose read is those four |
| what it says when not blind | a distinct not-pinned state, and the caller uses the r line's own token unchanged | derived: an unpinned line is tracking the RSI, so its own token is already the truth |
| a minimum freeze length | NONE | his standing no-cap rule. His goal argues against one anyway - a minimum could only delay a spawn |
| when to spawn | only at a 4-flat bar | HIS RULING, section 1 |

## 3. THE ARITHMETIC THIS RESTS ON

`optimus9/compute/indicator_computer.py:593-643`, the emerging r value at a 5 s bar inside a
forming candle:

| the term | what it is |
|---|---|
| `R_RSI` 5 | the RSI length |
| `R_STC` 8 | the stoch length, so the window is the previous `8 - 1` = 7 CLOSED RSI values |
| `R_KLEN` 7 | the %K average length, so 6 CLOSED stoch terms + 1 DEVELOPING term |
| `rsi_d` | the developing RSI - a Wilder one-step update from the last closed RSI state onto the developing bar's close |
| `lb_rsi_min`, `lb_rsi_max` | min and max of those 7 closed RSI values |
| `stoch_d` | `100 * (rsi_d - min(lb_rsi_min, rsi_d)) / (max(lb_rsi_max, rsi_d) - min(...))`, or `50.0` when that range is 0 |
| the r value | `(the 6 closed stoch terms + stoch_d) / 7` |

ONLY `stoch_d` CAN MOVE INSIDE THE CANDLE:

| the state | `stoch_d` | the r line | the RSI |
|---|---|---|---|
| `rsi_d` at or above `lb_rsi_max` | 100 exactly | FROZEN for the rest of the candle | keeps rising, invisible to the line |
| `rsi_d` at or below `lb_rsi_min` | 0 exactly | FROZEN for the rest of the candle | keeps falling, invisible to the line |
| `lb_rsi_max` equals `lb_rsi_min` | 50.0, the else branch | FROZEN | the line says nothing at all |
| `lb_rsi_min` < `rsi_d` < `lb_rsi_max` | tracks `rsi_d` | moves with the RSI | the line carries it |

THE FROZEN LEVEL IS NOT AN EXTREME. The 6 closed terms set the level, so a frozen line sits at
77.39 or 37.94. That is why these flats do not look like a pinned indicator.

`R_KLEN` 7 ALSO EXPLAINS THE 14.2857 STEP: one closed stoch term flipping 0 to 100 at a candle roll
moves the average by exactly 100 / 7.

## 3a. THE PRODUCER IS BUILT - 1108, AND ONE STRUCTURAL CALL CHANGED

HIS CORRECTION: *"I said to wire it as a race"*. His 1108 wiring instruction was an instruction to
BUILD, and I treated it as a spec instruction. The producer is now in.

| what | where | state |
|---|---|---|
| `IndicatorComputer._k_developing` | `optimus9/compute/indicator_computer.py` | NEW. Every intermediate of the developing K chain, extracted VERBATIM out of `f_k_lookahead`, which now calls it. The Wilder one-step update exists in one place |
| `IndicatorComputer.f_k_lookahead` | same file | unchanged in behaviour, proved bit-identical on 6 TFs |
| `IndicatorComputer.f_k_pin` | same file | NEW. `(pin, rsi_d)` - `+1` the RSI is at or above the closed window's max, `-1` at or below the min, `0` free or degenerate |
| the identity proof | `1108_rline_enhance/check_fk_identity.py` | runnable in seconds on a fixed-seed synthetic frame, no DB and no tape. 6 of 6 TFs bit-identical |

MY EARLIER CALL WAS WRONG. I said this needed *a third line type in `line_config.py`*. It does not:
the pin needs `stc_len` for the window and `k_len` for the average, so it is a property of the
K-line's own computation, not a line of its own. It is a sibling of `f_k_lookahead` sharing one
helper, which is also why no new cache key and no `line_config` change are needed for the producer
itself.

### THE PIN COUNTS ON A SYNTHETIC 3-DAY FRAME, ws30

| the state | bars |
|---|---|
| a pin value exists | 50160 of 51840 |
| pinned HIGH, +1 | 8004 |
| pinned LOW, -1 | 8875 |
| free or degenerate, 0 | 33281 |

## 3b. A DEFECT IN THE EXISTING xcv FLAT TEST, FOUND BY BUILDING THIS

`stoch_d` is computed `100.0 * (rsi_d - stoch_min) / rng`, which is `(100 * numerator) / denominator`
rather than `100 * (numerator / denominator)`. On a HIGH pin the numerator and denominator are the
same quantity, so the result should be exactly 100 and instead lands on `100.00000000000001` or
`99.999999999999986`. The K line therefore JITTERS by up to 1.42e-14 while it is mathematically
frozen. On a LOW pin the numerator is exactly zero, so `stoch_d` is exactly 0 and the line is
bit-exact.

MEASURED ON THE REAL CACHED ARRAYS, 2026-08-25 - moves that are not zero but are under 1e-9:

| the line | bars that change | moves under 1e-9 but not 0 | the smallest non-zero move |
|---|---|---|---|
| ws30r | 11404 | 78 | 3.55e-15 |
| ws29r | 11292 | 7 | 7.11e-15 |
| ws28r | 12171 | 30 | 7.11e-15 |
| ws27r | 11101 | 38 | 7.11e-15 |
| ws10r | 10556 | 32 | 3.55e-15 |
| ws5r | 10681 | 55 | 3.55e-15 |
| ws3r | 10599 | 34 | 3.55e-15 |
| ws1r | 11115 | 71 | 1.78e-15 |

HIS 1 dp RULING, AND IT IS APPLIED: *"can you int test it or reduce the dp? I only need 1dp for
line values - there must be a way to handle it so that the float variance doesn't bite us"*.
`xcv_report.tenths` turns a line value into an INTEGER number of tenths and
`xcv_report.direction` compares two of them. Two ints are either equal or they are not, so no
comparison downstream can be decided by a last bit. NaN has no integer and reads `flat`.

WHAT IT MOVED on 2026-08-25, RULED_OK True, `W_V4_EXPERIMENT` not set - 1 row of 28:

| xcv row | the cadence event | the ws5x cross | the float direction read | the 1 dp direction read |
|---|---|---|---|---|
| 9 | 2026-08-25 08:08:00 | 2026-08-25 08:14:20 | cad-walks to 2026-08-25 08:14:25, `up` | cad-walks to 2026-08-25 08:14:35, `up` |

That is the row whose smallest counted diff was 0.0035 on a 0-100 line. At 1 dp those diffs are
`flat`, so the walk carries 2 bars further and reaches a verdict that is not noise. The verdict
direction did not change, and the other 27 rows did not move.

SCOPE, STATED: the integer read is applied to the DIRECTION reads - `fdm2-xcv`'s 3-of-4 and the
diff block's direction row. It is NOT applied to a threshold test like `v >= 85`, because that
would change firing behaviour across the whole machine and he ruled the float variance, not the
fences.

WHY IT MATTERED TO `fdm2-xcv` AS IT STOOD: its diff reader is
`up if d > 0 else down if d < 0 else flat` on exact floats, so a 3.55e-15 difference reads as a
DIRECTION. A line that is frozen can therefore contribute `up` or `down` to the 3-of-4 count, and
a 4-flat spawn bar can be missed because one line jittered. HIS PARKED FLOOR IS THE DECISION THIS
NEEDS - he ruled no minimum diff size on 1108 and parked it as the first troubleshooting target.
NOTHING IS APPLIED.

## 4. MY STRUCTURAL CALLS - STATED, NOT ASKED

| the call | why |
|---|---|
| the substituted token is the SIGN OF `rsi_d[bar] - rsi_d[anchor]`, not the pin side | the pin side only says the line is blind. The direction must span anchor-to-bar like the tokens it replaces, and a pin that began after the anchor would otherwise describe a shorter span than its neighbours |
| a third line type in `optimus9/compute/line_config.py`, behind its own one-door entry beside `jig.kline` / `jig.bbline` | precedent: every other line goes through that door, and the module warns that hand-building a spec tuple is silent when transposed |
| `f_k_lookahead` calls the shared developing-RSI function rather than keeping its own copy | the Wilder one-step arithmetic in two places is the drift trap the second cross reader was removed for |
| the reader returns a dict with a `state` key | precedent: `jig.fdm2_cad_mom_detector` |
| this doc, not a section of `1107_sandbox_xcross.md` | it is its own mech with its own goal, and his 1108 idea puts a goal at the top of a spec |

## 5. THE BOUND THAT IS INHERENT, NOT APPLIED

A pin cannot survive its own candle roll: at the roll, `lb_rsi_min` and `lb_rsi_max` are recomputed
over a window that now includes the bar that was pinning, and `stoch_d` is free again. So the
blindness is bounded by the forming candle - 30 min on ws30r, 27 min on ws27r. NO CAP IS APPLIED;
this is the producer's own shape.

## 6. CAUSALITY - AN ASSERT, NOT A COMMENT

`rsi_d` at bar b is a one-step update from the last CLOSED bar before b's forming candle, onto b's
own close. `lb_rsi_min` and `lb_rsi_max` are over closed RSI values ending before that candle.
Every input is at or before b. The assert belongs at the reader's return site.

## 7. THE PRIZE, MEASURED ON 2026-08-25

The 4-flat spawn bar against today's cad-walk fire, over the 11 distinct cad walks. The spawn bar
is a SPAWN POINT, not a verdict - a verdict there needs 3 of the 4 RSI directions to agree, which
needs this reader built:

| xcv rows | the cross | the 4-flat spawn bar | the cad-walk fires | how much earlier | bars earlier |
|---|---|---|---|---|---|
| 1 | 2026-08-25 00:50:00 | 2026-08-25 00:50:05 | 2026-08-25 00:58:00 | 7 min 55 s | 95 |
| 5, 6 | 2026-08-25 05:35:00 | 2026-08-25 05:35:05 | 2026-08-25 05:59:00 | 23 min 55 s | 287 |
| 7 | 2026-08-25 07:02:15 | 2026-08-25 07:11:10 | 2026-08-25 07:12:00 | 0 min 50 s | 10 |
| 9 | 2026-08-25 08:14:20 | none | 2026-08-25 08:14:25 | - | - |
| 10 | 2026-08-25 09:59:15 | 2026-08-25 09:59:55 | 2026-08-25 10:09:10 | 9 min 15 s | 111 |
| 11 | 2026-08-25 11:40:00 | none | 2026-08-25 11:40:05 | - | - |
| 19 | 2026-08-25 17:35:00 | 2026-08-25 17:35:05 | 2026-08-25 18:00:00 | 24 min 55 s | 299 |
| 20 | 2026-08-25 17:50:00 | 2026-08-25 17:50:05 | 2026-08-25 18:00:00 | 9 min 55 s | 119 |
| 21, 22 | 2026-08-25 18:00:00 | 2026-08-25 18:00:05 | 2026-08-25 18:30:00 | 29 min 55 s | 359 |
| 25 | 2026-08-25 20:50:25 | 2026-08-25 20:50:30 | 2026-08-25 21:09:00 | 18 min 30 s | 222 |
| 26 | 2026-08-25 21:00:00 | none | 2026-08-25 21:09:00 | - | - |

| the 11 distinct cad walks | value |
|---|---|
| walks with a 4-flat spawn bar before the fire | 8 of 11 |
| walks with none | 3 of 11 - xcv 9, 11 and 26, all of which fire within 1 bar to 9 min anyway |
| the spawn bar is earlier by, median | 14 min 12 s |
| the spawn bar is earlier by, min | 0 min 50 s |
| the spawn bar is earlier by, max | 29 min 55 s |

THE VERDICT AT THE SPAWN BAR IS UNKNOWN until this reader exists. Today's verdicts at the LATER
fire are `up` on xcv 19, 20, 21 and 22.

AGREEMENT WITH THE LATER VERDICT IS NEVER A GATE. HIS 1108 CATCH: *"wouldn't that make the
rline-enhancer ineffective? it can't lookahead"*. He is right that the comparison is lookahead and
wrong that it disables the reader - the two are different things:

| the question | when it is answerable | is it causal |
|---|---|---|
| what does `fdm2-rline-enhance` emit at the spawn bar | AT the spawn bar. Every input - the 4 flat tokens, `rsi_d[bar] - rsi_d[anchor]`, the pin test - is at or before that bar | YES |
| does that verdict match what the cad walk says later | only OFFLINE, after the day is walked | NO - and it may never appear in the code |
| was the earlier verdict the better one | only OFFLINE, by what price did after each. The cad walk's own verdict is not ground truth either | NO |

So the reader runs live and emits at the spawn bar. His *"I need to be sure that their verdicts on
19, 20, 21 and 22 are all UP"* is an OFFLINE check over built days, and a rule of the form "spawn
only when it agrees with the later verdict" would be lookahead and must never be written. The
two-stage rule: bank the causal timestamps first, score them second.

## 7a. THE REAL EXPOSURE - THE SPAN, NOT THE LOOKAHEAD

The spawn bar is the FIRST bar where all four read `flat`, so the direction is read over whatever
span has elapsed since the anchor. On 6 of the 8 walks that have a spawn bar, that span is ONE BAR:

| xcv rows | the cross = the anchor | the 4-flat spawn bar | the span the direction is read over | bars |
|---|---|---|---|---|
| 1 | 2026-08-25 00:50:00 | 2026-08-25 00:50:05 | 0 min 05 s | 1 |
| 5, 6 | 2026-08-25 05:35:00 | 2026-08-25 05:35:05 | 0 min 05 s | 1 |
| 7 | 2026-08-25 07:02:15 | 2026-08-25 07:11:10 | 8 min 55 s | 107 |
| 9 | 2026-08-25 08:14:20 | none | - | - |
| 10 | 2026-08-25 09:59:15 | 2026-08-25 09:59:55 | 0 min 40 s | 8 |
| 11 | 2026-08-25 11:40:00 | none | - | - |
| 19 | 2026-08-25 17:35:00 | 2026-08-25 17:35:05 | 0 min 05 s | 1 |
| 20 | 2026-08-25 17:50:00 | 2026-08-25 17:50:05 | 0 min 05 s | 1 |
| 21, 22 | 2026-08-25 18:00:00 | 2026-08-25 18:00:05 | 0 min 05 s | 1 |
| 25 | 2026-08-25 20:50:25 | 2026-08-25 20:50:30 | 0 min 05 s | 1 |
| 26 | 2026-08-25 21:00:00 | none | - | - |

| the span at the spawn bar | walks |
|---|---|
| 1 bar = 5 s | 6 |
| 8 bars = 40 s | 1 |
| 107 bars = 535 s | 1 |

WHETHER A 5 s RSI MOVE CARRIES A DIRECTION IS UNMEASURED. It is the same shape as the raw cad
walk's own weakest firing: xcv 9 takes an `up` verdict on a smallest counted diff of 0.0035 on a
0-100 line, 1 bar after its cross. NO MINIMUM IS APPLIED to either - he has ruled none.

## 8. THE FLAT-TOKEN CENSUS BEHIND HIS RULE

1733 walked bars over the 13 cad walks of 2026-08-25, by how many of the 4 left tokens read `flat`
against the cross:

| flat tokens at a walked bar | bars | which racer can fire there |
|---|---|---|
| 4 of 4 | 285 | `fdm2-rline-enhance` only |
| 3 of 4 | 573 | neither |
| 2 of 4 | 693 | neither |
| 1 of 4 | 170 | the cad walk only |
| 0 of 4 | 12 | the cad walk only |

A `flat` token is not proof of a pin, so these counts BOUND the spawn opportunity rather than
measure it. The pin counts need this reader built.

## 9. OPEN - HIS CALL, ONE ITEM

| the gap | the question |
|---|---|
| the ON knob's banked default | every reading added since 1022 banked OFF - `RSIDIV_ON` 0, `FDM2_MOMO_ON` 0, `FDM_SAV_ON` 0. Does this one bank ON so `fdm2-xcv` runs with it, or OFF behind a flag until a day's numbers are in |
