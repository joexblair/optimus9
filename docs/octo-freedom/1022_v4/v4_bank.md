# octo-v4 — the bank

Started 2026-10-22. Joe 1022: *"v3 is dead... we're now starting `octov4`"* / *"don't carry anything forward from v3"*.

SPLIT FROM `v4_spec.md` ON 1022, at Joe's word: *"good analysis.  action the split"*. One doc
per thing that can change independently - the bank, and one per mech. His verbatim text is
CARRIED, never retyped: the 1022 handover arrived as ONE message covering the knob, `rev-trade`
and `v4-lineage`, and its pieces are split by mech here with nothing reworded. The Jig's
producers get no doc - `lift_off`, `at_extreme` and `mage_cascade` document themselves in the
Jig header, where the code is, and a second copy would rot.

Joe's times carry no colons: `1305` is 13:05, `2051` is 20:51. His time estimates are +/- 5
minutes - take the mechanic, never fit a knob to the timestamp.

---

## 1. The board

Standing rulings, not v4's to change.

| the reading | value | Joe's words |
|---|---|---|
| oob | 15 / 85 | standing - oob is ALWAYS 15/85 |
| the sides | low < 50, high > 50 | 1022: *"low side = <50.  high side = >50"* |
| 50 itself | LOW | STRUCTURAL - his rule is "< 50" and "> 50", so one side must own the boundary. Stated, not decided quietly |

## 2. The side is an INPUT, never a derivation

BANKED 1022, after I derived it instead of reading it. Joe asked for *"a trade opens on the low side
ws5r reversal near 09-06 2220"*; I ran "low-side reversal" through `rev-trade`'s polarity to LONG /
target-side HIGH and v4saviour returned SAVIOUR REV off the wrong side. On his stated LOW side it
returns NOT ARMED. Joe: *"this is the proper way to view it - the v4saviour class will consume this
data from an external source"*.

| the rule | owner |
|---|---|
| `target_side` is +1 high / -1 low, set by the TRADE: LONG = high, SHORT = low | the trade |
| it is FIXED for the lifetime of the trade | RULED 1022: *"yes, the target-side is fixed for the lifetime of the trade"* |
| no mech computes it | every v4 mech takes it as an argument |

## 3. "Print" means the usable event

RULED 1022: *"when i say "print" about anything, I'll always be refering to the usable event"*. So a
wobbed event is read at its STAMP, bar + wob - 1, never at the bar the condition first changed.

## 4. The open signal

RULED 1022: *"accept the first open signal.  we'll build pyramid logic at a later time"*. The first
signal opens; later signals while a trade is open are ignored until pyramid logic exists.

## 5. open_bar and the warmup

RULED 1022: *"open_bar in warmup.  I don't see a case for this: in backtest we're reliant on the
line cache, and in o9-live the lines are already warm"*. No mech guards against it.

## 6. The handover, verbatim

Joe 1022, the lines that opened his first v4 message, unedited. The `v4-lineage` block from the
same message is carried in `v4_lineage.md`; nothing is reworded in either place.

```
v4_rmom_fnc, default 80 - fence used when testing if a r is close enough to oob to be predicted

`rev-trade` = close incoming trade on fill bar, and open a new "reversal" trade on the next bar. if target-side is low, the incoming trade is SHORT, the reversal trade is LONG

store this in memory: I'm no longer printing colons between hh and mm (1222 inplace of 12:22)
```

---

## 7. `rev-trade`

Joe: *"close incoming trade on fill bar, and open a new "reversal" trade on the next bar. if
target-side is low, the incoming trade is SHORT, the reversal trade is LONG"*.

| the field | the value |
|---|---|
| the incoming trade closes | on the fill bar |
| the reversal trade opens | the next bar |
| target-side low | incoming SHORT, reversal LONG |
| target-side high | not stated by Joe; the mirror would be incoming LONG, reversal SHORT — superseded - see below |

---

Joe 1022 completed the high side: *"15, if target-side is low, the incoming trade is SHORT, the
reversal trade is LONG. high target-side is receiving a LONG trade, the reversal is a SHORT trade"*,
and *"16, the reversal bar"* for the fill bar. The UNRULED note above is superseded by those two.

---

**ONE POINT PRODUCES IT, 1024. See `v4_router.md`.** Joe: *"the code should be asking 'where is my
rev-trade event?', but we haven't (SRP) built a routing mech. without a single point producing
rev-trade, mechs conflate internally"*. The close bar, the open bar and the direction are no longer
computed inside a mech:

| the thing | where it lives now |
|---|---|
| what a signal IS | `v4_signal` |
| the fire bar, `the signal bar + 1` | `v4_signal.fire_bar`, replacing five computations by four rules |
| the direction | `v4_signal.direction`, from the signal's own side, replacing `flip(the previous trade)` |
| the open trades, the count, the cap, the close-all | `v4_pyramid.Pyramid` |
| the signal loop and the journal | `v4_router.route` |

---

## 8. The knobs, BANKED

`v4_knobs.py` is the in-force copy. Importing it REFUSES an off-ruled run unless
`W_V4_EXPERIMENT=1`, and an experiment run prints every delta first. A spec doc is not in-use.

ALL 48 RULED KNOBS, GENERATED FROM `v4_knobs.RULED` so this table cannot drift from
the code. An off-ruled run refuses unless `W_V4_EXPERIMENT=1`.

| the knob | value | units | Joe's words, or the measurement that set it |
|---|---|---|---|
| `ARM2` | 1 | yes/no | v4core's second arm, live. "add a second v4core arm" - 1024 |
| `ARM2_DWELL` | 18 | bars | "min dwell 18 bars" - 1024. The ws1r oob run's own length, so the earliest arm is bar 18 of the run |
| `ARM2_POOL_MIN` | 2 | lines | "any TWO of ws4-8r are same-side oob" - 1024 |
| `BSTOP_CASCADE_AT` | 'lift' | mode | "not extrema - measure where the r reversals print" - #25, defaulted 1023 |
| `BSTOP_OOB_WHEN` | 'window' | mode | "I think the answer is 'just recent'" - 1022, defaulted 1023 |
| `BSTOP_POOL_HI` | 3 | TF | "(ws1r or ws2r or ws3r are same side oob)" |
| `BSTOP_SYNC_MIN` | 8.8 | minutes | "the ws1r,ws2r,ws3r oob condition has a +/-8.8 minute window to sync with ws5r reversing. this needs to be causal" |
| `CORE_LIN_ENTRY_TF` | 4 | TF | "maybe setting the entry TF to {knob:4,'V4_CORE_LIN_ENTRY_TF'} will settle it" - 1024, replacing his earlier "start from ws1" |
| `GAP_PER_TF` | 2.8 | bars per TF-minute | "let's choose 2.8 until we get to the sweep" - PROVISIONAL |
| `IB_WOB` | 3 | bars | "10, 3" - SUPERSEDED by LIN_IB_DWELL |
| `LIFT_PTS` | 6 | samples | "34, 6 knob" |
| `LIFT_TOL` | 2.0 | r-points | "35, 2.0 knob" |
| `LIFT_WOB` | 8 | bars | "37, 8 knob" and "add a wob 8 to reduce the early reversals" |
| `LIN_HOP` | 2 | TFs | "1, 2" |
| `LIN_IB_DWELL` | 2.5 | bars per TF | "it needs to be dynamic: let's start with int(TF * {knob:2.5, `V4_LIN_IB_DWELL`})" |
| `LIN_LOOKBACK_FLOORED` | 1 | yes/no | "yes" to rungs below ws6 never looking back - 1023 |
| `LIN_LOOKBACK_FLOOR_TF` | 6 | TF | "ws6 needs to be the complimentary knob" - 1023 |
| `LIN_PASS` | 'ib' | mode | the code's original. His 1022 spec says "reversal" - 1023 |
| `LIN_W4` | 0 | yes/no | arm A is the bank. The handover is arm B of the 1024 A/B and is NOT the machine until he rules it |
| `LIN_W4_G1_XWOB` | 4 | bars | Joe 0911 "reversal:2, boundary:4. both are knobs" - the boundary one |
| `LIN_W4_GRACE_S` | 180 | seconds | "I propose we give 3 minutes grace to overcome the scenario" - 1024. UNANCHORED: the jump-back distribution has no knee, p75 is 0.3705 |
| `MAX_PYRAMID` | 2 | positions | "including 2 max_pyramid" - 1023 |
| `MID_FNC` | 50.0 | r-points | "change `mid` to a fence, same logic as above. 100-{knob:50}" |
| `OOB_FNC` | 15.0 | r-points | standing - oob is ALWAYS 15/85. ONE knob: *"oob_hi and oob_lo are expressed as one knob, to avoid imbalnace. the formula is (100 -{knob:15})"* |
| `RMOM_FNC` | 80.0 | r-points | "v4_rmom_fnc, default 80 - fence used when testing if a r is close enough to oob to be predicted" |
| `R_KLEN` | 7 | length | DEBANKED to the DB row 1024 - see the R_* block above |
| `R_RSI` | 5 | length | DEBANKED to the DB row 1024 - see the R_* block above |
| `R_STC` | 8 | length | DEBANKED to the DB row 1024 - unchanged, the DB and the sweep centroid agree on stc |
| `SAV_ARM_WALKBACK` | 30 | minutes | "at trade open, walkback in 5 minute jumps (cap: 30 minutes) to find the ws5r extrema. if the extrema is oob, the gate is closed and saviour may not fire" - 1024, with "full range" on the sampling |
| `SAV_CASCADE_GAP` | 12 | bars | "create a v4-saviour specific knob that looks back in 1 minute jumps" |
| `SAV_CASCADE_MIN` | 4 | lines | his 1017 "4 or more consecutive TFs" - the Jig's MC_MIN, captured at v4 level |
| `SAV_CASCADE_MODE` | 'extrema' | mode | "25, not extrema - measure where the r reversals print" for the r-driven reads; the ROUTED read is anchored on the ws1Mage extrema, so this mode is 'extrema' |
| `SAV_CASCADE_ZOOM` | 2 | rungs | "26, 2 knob" - the Jig's MC_ZOOM, captured at v4 level |
| `SAV_IB_XWOB` | 2 | bars | "23, 2" |
| `SAV_MAGE_GATE_WOB` | 8 | bars | "IF any ws1Mage bar lands outside of the past-50-gate (wob 8), route to the ws1r mage-cascade test" |
| `SAV_WS2_OOB_TEST` | 16.0 | minutes | "increase CAP to {knob:16} minutes, and start the timer when the trade opens" |
| `SP_ALIGN_S` | 300 | seconds | "agreed on 300s" - 1024. UNREAD by the banked SP_PICK; it gates only the 'window' arm, kept as the comparison |
| `SP_BAND` | 0.0 | pct points | his near-same band. MEASURED: 53.6% of the 37,178 consecutive-pct gaps are EXACTLY 0 - TFs sharing a leg extremum - and p10 to p50 are all 0.0000 while p75 is 0.3705. So 0.0 already captures the clustering; widening to 0.5 cost 43.6% -> 28.8% within 0.25% of the pivot and bought only +1.397% -> +1.802% of leg. No knee - 1024 |
| `SP_CONTAIN` | 0 | yes/no | OFF. Right on the 3 events it was proposed against, wrong on 5,323: 2,198 events lose EVERY candidate, the median candidate count falls 8.0 -> 1.0, and the median distance off the pivot goes 0.327% -> 1.157% with the worst 8.953% -> 26.146% - 1024 |
| `SP_PICK` | 'lowest_pct' | mode | "start at the lowest TF and scan upwards ... the TF swing/pivot to pick should be the highest TF printing the lowest pct (between pivot and event)" - 1024 |
| `SP_TFS` | 'wide' | set | THE ONE ITEM AWAITING HIS WORD. His 1024 list was SIX - ws3Mage, ws5Mage, ws10Mage, ws15Mage, ws20Mage, ws30Mage. ws1Mage and ws2Mage are MINE, and every measurement that justified banking used all eight, so the banked value is the one that was RUN. On his six alone the 18-row check scores 8 of 18 against 17 of 18. At ALIGN_S 300 ws1Mage and ws2Mage are the scale TF on 41.0% of events |
| `SP_XWOB` | 18 | bars | "introduce a wob 18 and retest" - 1024. The only wob he named for this mech. It lifted the MFE-side rate on every TF |
| `TF_CEILING` | 10 | TF | "18, unsure. use 10" - PROVISIONAL |
| `TRAJ_MIN_FRAC` | 0.5 | fraction | HELD at 0.5 through the width sweep, NOT swept itself |
| `TRAJ_MIN_TRAVEL` | 0.0 | r-points | Joe 0924: *"I would say the true threshold is in the OOS data"* - UNSET, and it passes dust |
| `TRAJ_WIDTH` | 21.0 | bars | "lock it in" - 1.75 of the line's own bar, the measured peak on BOTH ws21r and ws13r |
| `V4CORE_MAGE_FNC` | 5.0 | r-points | "same-side past 5/95" - 1023, his eyeballing, held |
| `V4CORE_STEP0_JOIN` | 'and' | mode | "STEP0 is specifically AND to avoid re-entering mid cycle and creating a second stop" - 1023 |

THREE CONSTANTS IN `v4_knobs` ARE NOT KNOBS and are deliberately outside `RULED` - they are the
control row's expected values, the drift check Joe 1023 ruled after a stale label read as cache
drift:

| the constant | value | what it is |
|---|---|---|
| `CONTROL_TS` | '2026-09-03 00:35:00' | the bar every run's control row reads |
| `CONTROL_DB` | 12.48 | ws5r there on the DB row - THE BANK as of 1024. Every run must read this |
| `CONTROL_BANK` | 6.77 | ws5r there on the 1023 sweep centroid k_len 6 / rsi 6 / stc 8 |

`REV_WOB` was here at 3 bars until 1023, when Joe said *"delete REV_WOB"*. It is deleted, not
superseded, and the row is removed rather than annotated.

The cascade's knobs are NOT re-declared. `MC_GAP` 48, `MC_ZOOM` 2, `MC_MIN` 4, `MC_TF_LO` 1 and
`MC_TF_HI` 12 are Joe\'s 1017 rulings and the Jig is their one home; `v4_knobs` asserts them, so a
change there refuses a v4 run rather than silently moving a verdict.

| the derived read | value |
|---|---|
| `fence()` | (20.0, 80.0) |
| `sav_cap_bars()` | 120 bars |
| `gap_for` ws1..ws5 | 3, 6, 8, 11, 14 |
| `gap_for` ws10, ws12, ws30 | 28, 34, 84 |

The gap rounding is RULED: *"38, yes"* to `round()`. ws3 8.4 -> 8, ws7 19.6 -> 20.

| the TF | TF x 2.8 | the gap | = seconds | the lattice span at pts 6 |
|---|---|---|---|---|
| ws1 | 2.8 | 3 bars | 15 s | 75 s |
| ws2 | 5.6 | 6 bars | 30 s | 150 s |
| ws3 | 8.4 | 8 bars | 40 s | 200 s |
| ws4 | 11.2 | 11 bars | 55 s | 275 s |
| ws5 | 14.0 | 14 bars | 70 s | 350 s |
| ws6 | 16.8 | 17 bars | 85 s | 425 s |
| ws7 | 19.6 | 20 bars | 100 s | 500 s |
| ws8 | 22.4 | 22 bars | 110 s | 550 s |
| ws9 | 25.2 | 25 bars | 125 s | 625 s |
| ws10 | 28.0 | 28 bars | 140 s | 700 s |
| ws11 | 30.8 | 31 bars | 155 s | 775 s |
| ws12 | 33.6 | 34 bars | 170 s | 850 s |

---

## 9. What is NOT here


Not carried from v3, by Joe's instruction: `v3_min_tf`, `v3_rmom_fnc`, `v3_mage_fnc`, the ws1b arm
and its dwell, the ws1Mage ib-cross test-point and its xwob, the ws2r oob gate, the three race
conditions (a) (b) (c), the x-cross direction mech, `v3-class-pred1` and `pred1_reach`, the
mrider band and its ws1/ws2 exclusion, the MAE race at 1.1, `v3_traj_k`, the away confirmation at
12 bars, and the away/toward perspective ruling.

Available as producers in the tree, NOT as v4 mechs, and only when Joe names one:
`jig.away_toward` / `away_toward_series`, the GPU momentum cache at `.rpl_cache/momt`
(ws1-ws30 + ws45 + ws60, r, both sides, 0 mismatches over 104,509,440 bar-comparisons),
`momo_gpu.py`, `momo_gated.momo_g`, and the line cache at `.rpl_cache/lines`.
