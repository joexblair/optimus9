# fdm2 - the spec as the code reads it

# every line read is the chart-matched value, except lift-off which is emerging
# "ex" means external of a fence, and it includes oob
# oob is 15/85
# a bar is 5 seconds
# lines marked #MINE are choices I made; he cleared the four in the body at 1103

## opening a trade

if there is no trade open
-the window OPENS on the bar where ws1b is oob AND gcws30b is ex-5/95
--either side for gcws30b, the window's own side for ws1b
-the window CLOSES on the bar ws1b crosses back to ib, held 1 bar
--one window per close: several opens before one close collapse onto that close
-at the close bar, test ws1r AND (ws2r or ws3r)
--a line passes if it printed ex 75/25 at any one bar inside the window
--they do not have to pass at the same bar, and they do not have to hold
-if the test is true, open a trade
--the side is ws1b's own oob side
--a high side opens a SHORT, a low side opens a LONG
--the trade opens 1 bar after the window closed
nothing bounds the window
-a long running ws1b excursion is a sign of a trending leg that hasn't stopped yet

## the cadence event

a cadence event prints when ws1b crosses from oob to ib, on the open trade's target side
-the excursion is the run of bars where ws1b was oob, ending on the bar before the cross
-two tests run over that excursion
--the nestle: at one bar, one of ws1r/ws2r/ws3r is oob and one of ws1Mage/ws2Mage is deeper oob
  than it
---any pair counts, and the Mage does not have to be the same timeframe as the r
---once it qualifies it stays qualified for the rest of the window
--ws3Mage prints ex 25/75 at any one bar in the excursion
-if both tests pass, the cross bar is the cadence event
-a cadence event on the counter side is ignored

### the ws3Mage gate's rescue

if the cross is gated only because ws3Mage stayed infence
-look back over the window that the re-entry's own opener would have opened
--so the same test that opens a trade's window, applied here: ws1b oob AND gcws30b ex-5/95
--from that bar through to this ws1b ib cross
-if ws3r was oob on this side at any bar in that window
--and ws3Mage was ex 40/60 on this side at any bar in that window
---print the cadence event anyway
40/60 is wider than the 25/75 it rescues, so ws3Mage has less distance to cover
-the price is the ws3r oob requirement, which 25/75 never asked for

## the decision at a cadence event

count the lines in ws4 to ws30 that, at the cadence event bar, are both
-ex 20/80 on the target side
-and travelling towards the target side
if the count is 0
-rev-trade at the cadence event bar
if the count is 1 or more
-walk to whichever comes first: the next same-side cadence event, or the ws10x-cadence
--if the next cadence event comes first, decide again there
--if they land on the same bar, the cadence event wins #MINE
--if neither exists before the walk's end, the trade stays open

## the ws10x-cadence

three races run from the bar after the cadence event, and the first to confirm wins
-ws10x crosses to ib
-ws10x crosses ws10r
-ws10x crosses ws10Mage
on a high target side the cross is ws10x going under, on a low side going over
each race holds for 24 bars = 120 seconds, and the confirm bar is the ws10x-cadence
-the cross itself must be after the cadence event, not just the confirm #MINE
-the confirm must land inside the walk's own end
only one ws10x-cadence fires per walk
-after it is used, only the next cadence event starts a new one

## the reversal count

the population is the lines in ws3 to ws30 that printed ex 20/80 on the target side at least once
-measured from the trade's open bar to the ws10x-cadence
-the population is fixed at the ws10x-cadence and does not grow after that
a line counts as reversed if it has a lift-off off the target-side extreme
-counted from the cadence event bar up to the bar being measured
-a lift-off counts at its stamp, which is 7 bars = 35 seconds after the line left its extreme
the percentage is reversed lines over the population

## at the ws10x-cadence

if the percentage is 50 or more
-rev-trade at the ws10x-cadence bar
if the percentage is 40 or more but under 50
-start the grace walk
if the percentage is under 40
-no action, wait for the next cadence event

## the grace walk

it runs for 5 minutes = 60 bars from the ws10x-cadence
-it stops early at the bar before the next cadence event #MINE
recount every bar, carrying on the same count from the ws10x-cadence
-the population stays as it was fixed
if the percentage reaches 50 or more
-rev-trade at that bar
if the 5 minutes expire
-no action, wait for the next cadence event

## what a rev-trade does

the router decides, and it costs bars
-if a trade is open: close it 1 bar after the signal, open the opposite 1 bar after that
--2 bars in total
-if no trade is open: open 1 bar after the signal
--1 bar in total
--this cannot happen today, because a rev-trade only exists while a trade is open
the new trade's target side is the opposite of the one that closed

## the stop

walk the price from the trade's open bar forward
-on a LONG read each bar's low, on a SHORT each bar's high
-the first bar where the move against the trade reaches 1.1% of the open price is the stop
--a bar that breaches it is the stop even if it also moved the right way in the same bar #MINE
the stop is found FIRST and it bounds the walk
-so no decision row and no rev-trade signal can sit past a leg's own exit
-a tie at one bar goes to the stop #MINE
at the stop the trade closes and there is no trade open
-the only way back in is the next window under "opening a trade"
-the side comes from that window's own ws1b oob side, never from flipping the trade that stopped

## v4saviour

it is OFF
-he dropped it at 1103: "I still think it has a place, but only if I can find the confluence it
 needs to be stable"
-its measured settings are kept so the config is not lost

---

# every knob the machine reads

## fdm2's own, all banked 1103

| the knob | value | units | what it does | whose value |
|---|---|---|---|---|
| FDM_RE_WIN_OPEN | both | - | what opens the re-entry window: ws1b oob AND gcws30b ex-fence | his, arm E |
| FDM_RE_WIN_CLOSE | ws1b | - | what closes it: ws1b's oob to ib cross | his |
| FDM_RE_B_FNC | 95.0 | r-points | gcws30b's fence in the opener, 95 -> (5, 95) | his |
| FDM_RE_IB_XWOB | 1 | bars | the ws1b ib cross hold that closes the window | his |
| FDM_RE_GATE_FNC | 75.0 | r-points | the gate's fence on ws1r/ws2r/ws3r, 75 -> (25, 75) | his |
| FDM_M3_FNC | 25.0 | r-points | ws3Mage's fence in the cadence event, 25 -> (25, 75) | his |
| FDM_M3_RESCUE_ON | 1 | - | runs the ws3Mage gate's rescue | his |
| FDM_M3_RESCUE_FNC | 40.0 | r-points | the rescue's ws3Mage fence, 40 -> (40, 60) | his |
| FDM_FNC_2080 | 20.0 | r-points | step 1's fence and the population's, 20 -> (20, 80) | his, he named the knob |
| FDM_STEP1_ABOVE_TF | 3 | timeframe | step 1 scans STRICTLY above this, so ws4..ws30 | his, "above in timeframe" |
| FDM_POP_LO | 3 | timeframe | the population's floor, so ws3..ws30 | his |
| FDM_X10_WOB | 24 | bars | the ws10x race's hold, 120 s | his |
| FDM_X10_FRM | cross | - | the race's CROSS must follow the cadence event, not just its confirm | MINE, he cleared it |
| FDM_X10_GRACE_PCT | 40.0 | percent | the grace walk's floor | his, he named the knob |
| FDM_X10_TRADE_PCT | 50.0 | percent | the rev-trade threshold | his value, my knob |
| FDM_X10_GRACE_MIN | 5.0 | minutes | the grace walk's length, 60 bars | his value, my knob |
| FDM_REV_FROM | event | - | the reversal count starts at the cadence event bar, not its window open | his 2-pole ask; "window" is unmeasured |
| FDM_MAE_CAP | 1.1 | percent | the stop, adverse from the open | his |
| FDM_SAV_ON | 0 | - | v4saviour is off | his |
| FDM_SAV_READ | emerging | - | which read v4saviour gets when it is on | his |
| FDM_SAV_TF_HI | 3 | timeframe | its cascade ladder's top rung | his |
| FDM_SAV_MIN | 3 | lines | lines a cascade cluster must cover | his |
| FDM_SAV_ZOOM | 2 | rungs | rungs each cluster step compares across | unchanged from the shared value |
| FDM_SAV_ARM | 0 | - | its ws5r walkback arm is off | his |

## INHERITED, AND NEVER CALLED OUT FOR fdm2

These are read by the machine and none of them was ever ruled FOR fdm2. They came in with octo-v4.

| the knob | value | units | what it does in fdm2 | the risk in it |
|---|---|---|---|---|
| OOB_FNC | 15.0 | r-points | the oob fence, mirrored to 15/85 | his standing "oob ALWAYS means 15/85", so this one is settled by that rule |
| L2_MOM_MAXTF | 30 | timeframe | THE BOARD'S TOP RUNG. It sets step 1's ws30 and the population's ws30 | a lineage2-NAMED knob setting fdm2's board. Moving it moves six other places in the sealed stack |
| LIFT_PTS | 6 | samples | the lift-off's sample count | drives EVERY reversal in the count. Never ruled for fdm2 |
| LIFT_TOL | 2.0 | r-points | how far off the window extreme still counts as at-extreme | same |
| LIFT_WOB | 8 | bars | the lift-off hold, so the stamp is +7 bars = 35 s | same, and it sets the 35 s the whole count is lagged by |
| TRAJ_MIN_TRAVEL | 0.0 | r-points | the smallest travel that counts as `towards` | at 0.0 any travel counts, so step 1's second half has no magnitude floor at all |
| BARS_PER_MIN | 12 | bars | minutes to bars, for the grace walk | arithmetic, not a judgement |

## INHERITED PER-TIMEFRAME FUNCTIONS, ALSO NEVER CALLED OUT

| the function | what it feeds | ws1 | ws3 | ws5 | ws10 | ws20 | ws30 |
|---|---|---|---|---|---|---|---|
| gap_for, bars | the lift-off's sampling gap | 3 | 8 | 14 | 28 | 56 | 84 |
| traj_block, bars | the `towards` block width | 21 | 63 | 105 | 210 | 420 | 630 |
| traj_min_bars, bars | the `towards` age floor | 10 | 31 | 52 | 105 | 210 | 315 |

- `traj_block` at ws30 is 630 bars = 52.5 min, so a ws30 `towards` reads over a 52-minute block.
- `traj_min_bars` at ws30 is 315 bars = 26.3 min: a ws30 line must have been travelling 26 minutes
  before it counts as `towards` at all.
- these three shape step 1 and the reversal count more than any fdm2 knob does, and he has never
  been asked about any of them.
