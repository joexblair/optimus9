# fdm2-momo, his 1106 spec update

HIS NAME for the mech, HIS WIRING for the latch, and now HIS REVISION of all three signals. Nothing
in here has moved a code default. The sections marked OPEN are the concretions his words do not
settle, and they are listed rather than filled.

## HIS VERBATIM UPDATE, 2026-11-06

> r-pred needs to gated by `towards`.  ie, r-pred has no value after the line has spent its momentum
>
> I think r-pred would be better served with a maxTF of 10 or 12 (ie ws11r/ws13r to ws30r are not
> queried by r-pred).
>
> `signal 2`:
> """The vote fires on a LOW count, because few turned-up fast lines means the board is still
> pressed down."""
> -reduce `signal 2` to maxTF 10 or 12 (same as r-pred)
>
> -add an extra internal `signal 2` vote: if x has crossed Mage in the last minute, then Mage will
> follow x **because of matryoshka**.
> --all four possible examples:
> ---if the incoming trade is SHORT, then x crossing under Mage is a vote for `walk`.
> ---if the incoming trade is SHORT, then x crossing over Mage is a vote for `rev-trade`.
> ---if the incoming trade is LONG, then x crossing under Mage is a vote for `rev-trade`.
> ---if the incoming trade is LONG, then x crossing over Mage is a vote for `walk`.
>
> `signal 2` needs a third dimension (for reporting only at present): trajectory
> -measure both line's trajectory, on emerging bars, between the current bar and the cadence event.
> -plot their expected path based on the incoming trajectory
> --if the plot predicts x crossing (and travelling away from) Mage,
> OR
> --if both lines are already travelling away from target-side
> THEN you might have an internal `signal 2` "vote" to improve the mech's outcome
>
> JOE: remember to test 08-23 0232 when updating the cadence event mech

## WHAT HIS WORDS SETTLE

| the ruling | his words | consequence |
|---|---|---|
| r-pred carries a `towards` gate | *"r-pred needs to gated by `towards`"* | a line counts for r-pred only if it is ALSO travelling toward the target side at that bar |
| the reason for the gate | *"r-pred has no value after the line has spent its momentum"* | a line already past the fence with its travel spent is not a carrier |
| r-pred carries a maxTF | *"a maxTF of 10 or 12"* | the carrier set stops below ws30 for this signal |
| signal 2 carries the same maxTF | *"same as r-pred"* | one shared knob, not two |
| the x/Mage cross is read per line | *"an extra internal `signal 2` vote"* | it reads the same pair signal 2 already reads, ws{t}x against ws{t}Mage |
| the cross window | *"in the last minute"* | 12 bars = 60 s at the 5 s grid, ending at the bar being read |
| the cross's four cases | his four lines, verbatim | SHORT + x under Mage = walk; SHORT + x over Mage = rev-trade; LONG + x under Mage = rev-trade; LONG + x over Mage = walk |
| why the cross means anything | *"Mage will follow x **because of matryoshka**"* | the fast line leads, the slow one is dragged after it |
| the trajectory dimension is not wired | *"for reporting only at present"* | measured and printed; no vote, no latch effect |
| the trajectory span | *"between the current bar and the cadence event"* | the cadence event bar to the bar being read, on emerging |
| the trajectory's two triggers | *"the plot predicts x crossing (and travelling away from) Mage"* OR *"both lines are already travelling away from target-side"* | two separate reads, both reported |
| 2026-08-23 02:32 is a test case | *"remember to test 08-23 0232"* | task #48. That leg printed no ws1b cross on the HIGH side in 477 bars, so no cadence window opened |

## WHAT HIS WORDS DO NOT SETTLE - OPEN, NO CODE

| # | the gap | the candidates |
|---|---|---|
| 1 | maxTF: 10 or 12 | he named both |
| 2 | which read feeds the `towards` gate | fdm2-momo reads emerging throughout (`FDM2_MOMO_READ`); step1's own precedent calls `towards()` on closed-prev |
| 3 | how the x/Mage cross combines with the Mage-beyond-x count inside signal 2 | signal 2 fires only if both agree; either one firing is enough; the cross replaces the count |
| 4 | what a `rev-trade` vote from the cross does | cancels the latch outright; subtracts from the vote; is reported only |
| 5 | how many lines must carry the cross | no count threshold was named; `FDM2_MOMO_MED_MX` 7 governs the other half of signal 2 |
| 6 | does the maxTF also apply to signal 3, pinned | he named r-pred and signal 2 only, so pinned stays ws4..ws30 unless he says otherwise |

## WHAT IS NOT CHANGING UNTIL HE RULES

- `FDM2_MOMO_ON` stays 0. The banked machine is unchanged.
- signal 3, pinned, keeps `LIFT_PTS` 6 samples, `LIFT_TOL` 2.0 r-points and the ws4..ws30 set.
- `FDM2_MOMO_VOTES` 3, `FDM2_MOMO_MED_RPRED` 0, `FDM2_MOMO_MED_MX` 7 and `FDM2_MOMO_MED_PIN` 9 keep
  their measured values. Every one of them was measured on the ws4..ws30 set, so a maxTF change
  invalidates all four and they need re-measuring on the new carrier set before any A/B.

---

# HIS 1106 RCA - the latch was the fault, and it is gone

> this might be the RCA
>
> plainly speaking, if there is a walk verdict, there is no need to truncate the cad walk.  there
> is no harm caused if the verdict continues to be `walk` after the intial `walk` verdict, but if
> the verdict flips inside of the cad walk's max time then we don't miss that **correcting**
> verdict (ie rev-trade)  and are able to react accordingly
> -if you understand my point, update the mech based on my truth

## WHAT WAS WRONG

His 1106 wiring was *"we need to see fdm2-momo fire only once when we're cad walking, then we know
we're safe to walk to a ex-20/80-fence bar without being rev-traded"*, and *"per cad walk is my
answer to 3"*. I read "fire only once" as ONE READ that silenced the whole cad walk. His truth is
that the verdict is a per-bar state: `walk` at a bar means no rev-trade AT THAT BAR, and the cad
walk keeps asking.

| what the latch cost | the number |
|---|---|
| read bars against test bars | 1 against up to 121 |
| the bar it read | the cad walk's first bar, the weakest-signal bar of the cad walk |
| the 28 legs it held longer | +32.523% to +25.974%, a loss of 6.549% |
| the 2026-08-23 05:30:20 SHORT | MFE +4.565% at 07:48:20, the vote at 07:55:10, the 1.10% stop at 11:09:20, nothing deciding for 3 h 14 min |

## WHAT IS BUILT NOW

| the rule | the shape |
|---|---|
| when the vote is read | every bar of the cad walk, `FDM_XCAD_WALK_MIN` 10.0 min = 120 bars, so 121 bars |
| a `walk` verdict | vetoes the truncation test AT THAT BAR ONLY |
| the verdict ending | that bar is decided by the cad walk's own test, which can print the rev-trade - his *"correcting verdict"* |
| stickiness | none. The verdict is re-read from scratch at every bar |
| the cad walk's length | unchanged, it runs its full length either way |
| the rows | one per verdict TRANSITION, stamped on its own bar, stage `MOMO VOTE` |
| the counts | the bars read and the bars vetoed ride in the seam read's own text |

- `FDM2_MOMO_ON` stays 0, so the banked machine is untouched and an armed run needs `W_V4_EXPERIMENT=1`
- the rows' stage label moved from `MOMO LATCH` to `MOMO VOTE`, because there is no latch to name

## WHAT THIS INVALIDATES

| the artefact | why |
|---|---|
| the 94.5-day A/B in `1105_momo_dish.md` | every number in it is the one-shot latch's. The shape changed, so the A/B needs re-running before any of them is quoted |
| the three median knobs | measured at 417 cad-walk FIRST bars. The vote now reads every cad-walk bar, so they describe a subset of the bars they are applied to |
| the 1106 signal updates | still OPEN. The six concretions above are untouched by this change - this is the latch's shape only |

---

# HIS 1106 RULINGS ON THE SIX, AND WHAT WAS BUILT

> -NOTE some of these are now report-only. the RCA is a global change to the momo machine so we
> need to step with caution
> 1 maxTF --set it at 10
> 2 which read feeds the towards gate --report-only on this: "step1's own precedent calls
>   towards() on closed-prev"
> 3 how the cross combines with the Mage-beyond-x count inside signal 2 --either one firing is
>   enough.  let's make this reporting-only
> 4 what a rev-trade vote from the cross does --report-only: subtracts one from the 3
> 5 how many lines must carry the cross --report-only
> 6 does the maxTF also reach signal 3, pinned --unsure.  report on both ws10 and ws12
> and *"no need to recreate the 94.5 day data yet"* / *"thanks, go for A"*

## WHAT IS LIVE

| the knob | value | the carrier set | the test |
|---|---|---|---|
| `FDM2_MOMO_MAX_TF` | 10 | r-pred and Mage-beyond-x | ws4..ws10 = 7 lines |
| `FDM2_MOMO_FLOOR_RPRED` | 1 | ws4..ws10 | count >= 1 |
| `FDM2_MOMO_MED_MX` | 7 | ws4..ws10 | count < 7 |
| `FDM2_MOMO_MED_PIN` | 9 | ws4..ws30 = 27 lines | count >= 9 |
| `FDM2_MOMO_VOTES` | 3 | the three signals | 3 of 3 |
| `FDM2_MOMO_ON` | 0 | - | the banked machine is unchanged |

- `FDM2_MOMO_MED_RPRED` was RENAMED to `FDM2_MOMO_FLOOR_RPRED`, because a floor is not a median
  and the old name would have read as one. His option A set its value.

## WHAT IS REPORT-ONLY

| his ruling | what prints | the knob behind it |
|---|---|---|
| 2 | r-pred's count if gated by `towards` on closed-prev | - |
| 3 | signal 2 under *"either one firing is enough"* - the count test OR a `walk` cross | - |
| 3 | both lines' slope from the cadence event to the bar, and the bar their fitted paths cross | - |
| 4 | the vote with one subtracted when a `rev-trade` cross is present | - |
| 5 | how many carriers crossed, split into `walk` and `rev-trade` votes | `FDM2_MOMO_XWIN` 12 bars = 60 s |
| 6 | pinned on the capped set beside the live full-set count | - |

- the report-only reads are computed ONLY at a verdict-transition bar, which is the only bar that
  gets a row. Paying for the `towards` gate's opposed-extremum scan at all 121 bars buys nothing.
- there is NO HORIZON in the trajectory projection: the crossing bar comes from the two fitted
  slopes and is unbounded.

## THE MEASUREMENT BEHIND THE TWO MEDIANS

`out/momo_meds.py`, over all 50,457 cad-walk bars - 417 cad walks x 121 bars - off the cached
walk0/side with one tape load and no leg-chain re-run.

| the control | value |
|---|---|
| the population | the 417 cad-walk FIRST bars, emerging, ws4..ws30 |
| the medians returned | 0 / 7 / 9 |
| the banked knobs | 0 / 7 / 9, REPRODUCED, and bar-for-bar against `momo_vote` |

| the live signal, emerging | the test | fires on, of 50,457 |
|---|---|---|
| r-pred, ws4..ws10 | count >= 1 | 9,470 = 18.8% |
| Mage-beyond-x, ws4..ws10 | count < 7 | 24,868 = 49.3% |
| pinned, ws4..ws30 | count >= 9 | 25,757 = 51.0% |
| the vote | 3 of 3 | 8,178 = 16.2% |

- no vote is a constant
- A CONCERN OF MINE THAT THE MEASUREMENT KILLED: I argued that "count < 7 of 7 lines" could not
  discriminate. The count SITS AT 7 on more than half the bars, so it fires on 49.3%. I reasoned
  about the arithmetic instead of measuring the distribution.
- A FAULT THE CONTROL CAUGHT: a first draft harvested each TRUNCATION bar instead of each cad
  walk's first bar, and returned 0 / 11 / 5 against the banked 0 / 7 / 9. Those numbers were never
  reported.
