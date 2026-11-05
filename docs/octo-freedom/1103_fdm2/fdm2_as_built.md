# fdm2 - the spec as the code reads it

# every line read is the chart-matched value, and since 1104 the re-entry's ws5/ws6 lift-off
# is chart-matched too - every other lift-off in the machine is still emerging
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
-walk forward from the window's open until ws5 reverses
--the reversal is a lift-off on ws5r, on the window's own side
--the reversal is read on the chart-matched line, so it lands on ws5's own 5 minute step
--the bar used is the lift-off stamp, 35 s after the lift, which is when it is knowable
--the walk is NOT bounded by the window's close
-if ws5r is ex-20/80 at that reversal
--if ws6r holds the ex-20/80 fence there
---walk forward until ws6 reverses, then scan
--if ws6r is inside the fence there
---scan at the ws5 reversal bar
-the scan looks at ws7r to ws12r at the scan bar
--a line passes if it is strictly inside 20/80, both ends
-if at least one of ws7r to ws12r is inside the fence, open a trade
--the side is ws1b's own oob side
--a high side opens a SHORT, a low side opens a LONG
--the trade opens 1 bar after the LAST of these to fire
---the ws5 reversal
---the ws6 reversal, when that branch ran
---ws1b crossing back to ib, the window's close
if ws5r is NOT ex-20/80 at its first reversal, the window produces nothing
-the first ws5 reversal is the only test point
if no line from ws7r to ws12r is inside the fence, the window produces nothing
nothing bounds the window
-a long running ws1b excursion is a sign of a trending leg that hasn't stopped yet
2026-09-15 13:31 is accepted as it stands
-there is no available high side cadence to close that 1331 LONG before it is stopped
the limited re-entries on 2026-09-16 follow the ~11 hours of consolidation on that day

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

- every fence knob holds the SMALLER end of its pair - his 1103 ruling, *"the way that I
  should be supplying a knob is (100 - {knob:15}), ie I use the smallest number to describe
  the fence's max"*
- the pair and the per-side edge come from K.fnc_pair / K.side_edge, the one home, which
  asserts a fence knob is at or under 50
- RMOM_FNC 75.0 is the one fence still held at its upper end - lineage2 and the live octo-v4
  machine read it through K.fence(), so it is out of fdm2's scope to move

| the knob | value | units | what it does | whose value |
|---|---|---|---|---|
| FDM_RE_WIN_OPEN | both | - | what opens the re-entry window: ws1b oob AND gcws30b ex-fence | his, arm E |
| FDM_RE_WIN_CLOSE | ws1b | - | what closes it: ws1b's oob to ib cross | his |
| FDM_RE_B_FNC | 5.0 | r-points | gcws30b's fence in the opener, 5 -> (5, 95) | his |
| FDM_RE_IB_XWOB | 1 | bars | the ws1b ib cross hold that closes the window | his |
| FDM_RE_REV_READ | closed_prev | - | which read the ws5 and ws6 reversals come off | his, 1104 |
| FDM_RE_WS5_FNC | 20.0 | r-points | ws5r's fence at its own reversal, 20 -> (20, 80) | his, 1104 |
| FDM_RE_WS6_GATE | ex2080 | - | what makes the walk wait for ws6 to reverse; oob is the arm it replaced | his, 1104 |
| FDM_RE_SCAN_LO | 7 | timeframe | the scan band's floor, ws6 + 1 | his "above ws6" |
| FDM_RE_SCAN_HI | 12 | timeframe | the scan band's ceiling, wsf's own top | his band names, 1017 |
| FDM_RE_FIRE_IB | 1 | - | ws1b's ib close is in the last-to-fire set | his, 1104 |
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

## WHAT 1105 ADDED — his words, and what each one moved

HIS BANK INSTRUCTION, 1105: *"I don't think there is anything outstanding for that mech. if you
agree then bank everything, commit and push, update specs and store all knobs, and make that config
the machine"*.

### the reason column on the leg table

HIS 1105: *"`the reason` needs to print 'why did this trade exit?' eg, ws10x cad walk, ws10x
cadence, no linhop candidates, etc"*. `fdm2_chain._why_rev` reads the leg's OWN last REV-TRADE row,
so the label cannot drift from the decision that produced it. The x line's timeframe comes off the
row because the fdm2-wsxcad-director chooses it per event, so the label prints `ws12x cad walk` and
not a fixed `ws10x`.

| what it prints | when |
|---|---|
| `mae1.10 stop` | the leg hit FDM_MAE_CAP |
| `ws{TF}x cadence` | the director's seam read fired at a cadence event |
| `ws{TF}x cad walk` | the director's seam read fired inside the truncating walk |
| `no linhop candidates` | the director found no candidate |
| `step 1, 0 of n` | step 1 counted zero |
| `v4saviour` | the saviour signal won on chronology |
| `no rev-trade before the day ends` | the leg ran to the day's end |

### fdm2-blaster — HIS NAME, a PRODUCER WITH NO CALLER

`optimus9/analysis/jig.fdm2_blaster(rows, bar, head_tfs=(1, 2), lo=2, hi=None)`. It holds no
threshold and returns no verdict: `head`, `head_both`, `head_away`, `head_age`, `away_run`,
`away_tfs`, `broke_at`, `why`, `lags`. It touches no array - the caller hands in the
`fdm2_cad_mom_detector` rows it already builds.

**IT IS NOT WIRED INTO THE LEG WALK, AND THAT IS HIS HOLD, NOT AN OPEN ITEM.** His 1105: *"how to
model: this is on hold - I need to improve the cadence event before we can accurately model"*. So
the 2026-08-07 08:26:00 cadence still prints WALK in the ruled machine; `fdm2_router_probe.py`
measures what the router does when a signal IS supplied, under a loud banner saying so.

### the four knobs 1105 added

| the knob | value | units | whose name | whose value |
|---|---|---|---|---|
| FDM2_BLAST_SCAN_HI | 12 | timeframe | mine | HIS, *"ws12"* |
| FDM2_MATR_LFTOF_CONF | 10 | timeframe | HIS | HIS |
| FDM2_CAD_FLATIN_WIDTH | 3 | timeframe | HIS | HIS |
| FDM2_CAD_FLATIN_TOL | 8 | bars = 40 s | mine, on his *"your call on the label"* | HIS, *"40s"* |

None of them has a reader yet - the flattening read lands after the cadence event work. They are in
the RULED registry so the values survive a session and an off-ruled run refuses:

    RuntimeError: OFF-RULED v4 run refused. FDM2_BLAST_SCAN_HI is 10, ruled 12 ...
    Set W_V4_EXPERIMENT=1 to run it as an experiment.

### what was STRUCK from the spec at 1105

| what went | his word |
|---|---|
| the 4-of-5 blast-radius gate, its `fdm-blst-rad-conf-tfs` row and its reversal-origin row | *"no"* to whether it survives |
| the lazy-g spec as a reference, and the "order is guaranteed by construction" sentence - MINE, in two files | *"sunset this spec and drop the words"* |
| the ws1r exception and its rulings 1, 2 and 4 | *"that nulls my concerns about ws1r, and cancels #1,#2,#4 rulings"* |
| my order/age gate inside fdm2-blaster | *"if the towards and aways are telling us the truth, why is the aging important?"* |
