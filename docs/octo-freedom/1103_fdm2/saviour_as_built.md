# v4saviour - the spec as the code reads it

# read off 1022_v4/v4_saviour.py. v4_saviour.md is older than the code in two places - the arm and
# the clock - and this file follows the code
# every line read here is the LIVE line, not fdm2's chart-matched read. This mech was built and
# validated on the live lines
# oob is 15/85
# "the counter verdict" is DOWN when the target side is high, UP when the target side is low
# a bar is 5 seconds

## the arm

at the trade's open bar, look back 30 minutes
-find the most extreme ws5r value anywhere in that span, on the COUNTER side to the target side
--a high target side looks for ws5r's lowest value, a low target side looks for its highest
-if that extreme is oob, the arm is shut and saviour never fires on this trade
-otherwise saviour is armed

## the clock

one clock of 16 minutes, started at the trade's open bar
-every test below must finish inside it, including the last ib cross
-if the clock runs out at any point, the trade stays open

## the first test, on ws1r

find the first run of bars where ws1r is oob on the target side, at or after the open
-no such run inside the clock means the trade stays open
wait for ws1r to cross back to in-fence
-the cross sits on the bar after the run's last bar
-it must stay in-fence for 2 bars, so it is only proven on the second of them
--if ws1r goes back oob inside those 2 bars it is a flicker, and the next run is tried
-a proven cross past the clock means the trade stays open
at the proven cross, read two things
-the cascade verdict
--read at ws1r's most recent lift-off stamp at or before the cross
--the stamp is the lift-off bar plus 7 bars = 35 seconds
--the cascade reads ws1Mage to ws12Mage at that one bar and answers UP, DOWN or NEITHER
---a cluster must cover 4 lines, stepping 2 rungs at a time
-whether ws1Mage is past 50 towards the target side
--a high target side means above 50, a low target side means below 50
if the verdict is the counter one AND ws1Mage is NOT past 50 towards the target side
-end the trade, and open the reverse on the next bar
else
-go to the second test

## the second test, on ws2r

from the ws1r cross, walk forward inside the same clock
while walking, watch two things at once
-ws2r going oob on the target side and then crossing back to in-fence, held 2 bars
-ws1Mage leaving the past-50 gate and staying out for 8 bars = 40 seconds
whichever lands first in time is taken

### if ws2r's cross lands first

read the same two things at that cross
-the cascade verdict, at ws2r's most recent lift-off stamp at or before it
-whether ws2Mage is past 50 towards the target side
if the verdict is the counter one AND ws2Mage is NOT past 50 towards the target side
-end the trade, and open the reverse on the next bar
else
-the trade stays open, saviour is finished

### if ws1Mage's 8 bars outside the gate land first

this routes back to the ws1r test, on a different anchor
-the anchor is ws1Mage's most recent target-side extreme, found by walking back in 1-minute jumps
-read the cascade at that anchor bar
if the verdict is the counter one
-end the trade, and open the reverse on the next bar
else
-the trade stays open, saviour is finished

### if neither lands inside the clock

the trade stays open, saviour is finished

## what it answers

| the answer | when |
|---|---|
| NOT ARMED | the 30-minute walkback found ws5r oob on the counter side |
| SAVIOUR REV | a counter cascade at the ws1r cross, the ws2r cross, or the ws1Mage route |
| STAYS OPEN | no counter cascade anywhere, or the clock ran out, or no ws1r oob run followed the open |

## the knobs, and whose value each one is

| the knob | value | whose |
|---|---|---|
| the arm's walkback | 30 min | his - "walkback in 5 minute jumps (cap: 30 minutes)" |
| the clock | 16 min from the open | his - "increase CAP to 16 minutes, and start the timer" at the open |
| the ib cross hold | 2 bars = 10 s | his - "23, 2" |
| the cascade's cluster width | 4 lines | his 1017 - "4 or more consecutive TFs" |
| the cascade's rung step | 2 | his - "26, 2 knob" |
| the ws1Mage gate hold | 8 bars = 40 s | his - "IF any ws1Mage bar lands outside of the past-50-gate (wob 8)" |
| the route's look-back jump | 12 bars = 1 min | his - "a v4-saviour specific knob that looks back in 1 minute" jumps |
| the lift-off stamp | 7 bars = 35 s | the producer's own contract |

## what it needs handed in

| the input | what it is |
|---|---|
| the open bar | the bar the trade opened on |
| the target side | +1 high, -1 low. AN INPUT, NEVER DERIVED - he banked that after a derived side returned the wrong verdict |
| ws1r, ws2r, ws5r | the three r lines it reads |
| ws1Mage to ws12Mage | the cascade's ladder |

## one thing to settle before it joins fdm2

fdm2 reads chart-matched values everywhere except lift-off. v4saviour was built and validated on the
LIVE lines. Feeding it chart-matched lines would move the verdicts away from the four examples he
checked it against - 09-01 2059, 09-01 2125, 09-02 1215, 09-02 1630 - so the run below hands it the
live lines, as banked.
