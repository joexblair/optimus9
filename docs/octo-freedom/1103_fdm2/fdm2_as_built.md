# fdm2 - the spec as the code reads it

# every line read is the chart-matched value, except lift-off which is emerging
# "ex" means external of a fence, and it includes oob
# oob is 15/85
# a bar is 5 seconds
# lines marked #MINE are choices I made that you have not ruled

## opening a trade

if there is no trade open
-wait for gcws30b to print ex 5/95 - this opens a window
--the window closes on the bar gcws30b crosses back to ib
---at that bar, test ws1r AND (ws2r or ws3r)
----a line passes if it printed ex 75/25 at any one bar inside the window
----they do not have to pass at the same bar, and they do not have to hold
---if the test is true, open a trade
----the side is the oob side the lines were found on
----a high side opens a SHORT, a low side opens a LONG
----the trade opens 1 bar after the window closed

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
--if neither exists before the tape ends, the trade stays open

## the ws10x-cadence

three races run from the bar after the cadence event, and the first to confirm wins
-ws10x crosses to ib
-ws10x crosses ws10r
-ws10x crosses ws10Mage
on a high target side the cross is ws10x going under, on a low side going over
each race holds for 24 bars = 120 seconds, and the confirm bar is the ws10x-cadence
-the cross itself must be after the cadence event, not just the confirm #MINE
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
at the stop the trade closes and there is no trade open
-the only way back in is the next window under "opening a trade"
-the side comes from that window's own oob side, never from flipping the trade that stopped

## the knobs, and whose value each one is

| the knob | value | whose |
|---|---|---|
| the re-entry window's fence | 5/95 | yours |
| the re-entry gate's fence | 75/25 | yours |
| the re-entry window's ib cross hold | 1 bar | yours, the 00:41:30 bank |
| ws3Mage's fence in the cadence event | 25/75 | yours |
| the step count's fence | 20/80 | yours, you named the knob |
| the step count's lowest timeframe | ws4 | yours, "above ws3 in timeframe" |
| the population's lowest timeframe | ws3 | yours |
| the population's highest timeframe | ws30 | yours |
| the ws10x race's hold | 24 bars = 120 s | yours |
| the grace walk's floor | 40% | yours, you named the knob |
| the grace walk's trade threshold | 50% | your value, my knob |
| the grace walk's length | 5 min | your value, my knob |
| the stop | 1.1% | yours |
| the lift-off stamp | 7 bars = 35 s | the producer's own contract |
| which bar of the ws10x race must follow the cadence event | the cross | MINE, unruled |
