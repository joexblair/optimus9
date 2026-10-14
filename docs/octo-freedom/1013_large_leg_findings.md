# LARGE-LEG DETECTION — WHAT WAS MEASURED AND WHY IT IS NOT IN THE MACHINE — 1013

Joe 1013 asked for a large-leg process at the ws1cp-ib, then: *"have we landed here on a tangent, or
are we in a state where large-leg detection has broken the profit we've gained"* — a tangent, and
nothing shipped. This file exists so the 3.3177% is not re-learned later.

**NONE OF THIS IS IN THE CODE.** `machine.py`, `_chain10.py`, `_extmom.py` and `_ibmech.py` carry no
part of it. The machine still closes on the move test and still measures +8.0377%.

## THE TWO TESTS, AS JOE SPECIFIED THEM

**TEST 1 — the sampling match.** At the ws1cp-ib, build a sample set from the ws1Mage oob crossing to
the ws1cp-ib bar, and compare the same-width set of the TFs above ws1. Joe: *"the higher TFs will
EITHER print a sample set that loosely matches ws1cp-ib's samples, OR the higher TF will print a
sample set that is geared more towards the target dr (ie not a ~matching sample-set that prints a
clear u or n shape)"*.

**TEST 2 — matryoshka.** Joe: *"ws3Mage is drawn to ws1-2Mage, ie ws1-2Mage is leading ws3Mage. for
this to be valid, ws{higher TF being tested}Mage must be heading towards the target, not away from
it"* / *"if the test detects a diff between the lower Mage and the higher Mage, and the diff is
>={knob:4}, walk to the next (ws1mage oob + g30 cross to ib)"*.

MY READING OF TEST 2'S LINE, after Joe's *"I don't know tbh. ws4,5,6,7 are all in the casacde -
maybe their data is what we need ... your call - pick and mix"*: among the TFs above ws1 that are
in-fence, keep the ones that are BOTH **lagging** - below ws1Mage on a HIGH board, above it on a LOW
board - and **heading** toward the target, then take the DEEPEST gap. His knob is a diff in r-points,
so the statistic has to be a gap for the knob to keep its meaning.

TWO SIGN ERRORS I MADE FIRST, both corrected before the retest:
- I used `abs(gap)`. On a HIGH board a lagging line sits BELOW ws1, so its gap is NEGATIVE. At
  2026-07-18 20:03:25 ws2Mage's +4.24 means it is AHEAD of ws1; `abs` read it as a gap to close.
- I ignored his direction precondition. ws2Mage was heading AWAY (-0.70) there, so the matryoshka
  premise was invalid and I walked on anyway.

THE DIRECTION WINDOW, 36 bars = 3 min, IS MINE. His words carried no span.

## THE LOOP

Joe: *"this is a one-time cascade validation. if it passes, the next stop is the same-side
ws1cp-ib"*.

    ws1cp-ib -> tests 1 and 2
      LARGE LEG -> walk to the next (ws1Mage oob + g30Mage cross to ib), validate ONCE
                   validated     -> on to the next target-side ws1cp-ib, repeat the tests
                   not validated -> pass to link 3
      not large  -> pass to link 3 at that ws1cp-ib bar
    END, Joe: all ws{<= loop-tf + lin_hop}Mages oob while ws1cp-ib is firing

The ws1cp has no reversal condition, so the reversal was dropped from the next event on his ruling:
*"if ws1cp doesn't have the reversal, then drop it"*.

## THE ACID TEST PASSES — 07-18 02:31 SHORT at 2026-07-18 04:16:50, board LOW

| test | reading | verdict |
|---|---|---|
| 1, the sampling match | ws1Mage +9.48 cp -> ib against ws2Mage -1.54 | no match, large leg |
| 2, the block | 11 lines in-fence above ws1, all lagging and heading, deepest ws12Mage +51.90 | large leg |
| the end condition | 0 of 12 Mages oob | nowhere near |

Joe's 1012 call reproduces. This is the leg the process exists for.

## THE RETEST ON ALL SIX TRADES — WHERE IT BREAKS

| trade | banked close | the new close | why it ended | banked gross | new gross | moved |
|---|---|---|---|---|---|---|
| 07-17 21:58 LONG | 2026-07-18 01:15:20 | 2026-07-18 01:15:20 | empty block | +1.0517% | +1.0517% | 0.0000% |
| 07-18 02:31 SHORT | 2026-07-18 10:40:40 | 2026-07-18 05:44:35 | all Mages oob | +4.5067% | +1.7219% | **-2.7848%** |
| 07-18 08:46 LONG | 2026-07-18 10:07:10 | 2026-07-18 12:17:45 | cascade not validated | +0.3929% | +0.0971% | **-0.2958%** |
| 07-18 16:07 LONG | 2026-07-18 16:38:15 | 2026-07-18 17:43:00 | empty block | +0.4857% | +0.9203% | +0.4346% |
| 07-18 18:12 SHORT | 2026-07-18 18:44:15 | 2026-07-19 07:53:25 | empty block | +0.4441% | -2.1730% | **-2.6171%** |
| 07-18 18:45 LONG | 2026-07-18 20:04:00 | 2026-07-18 21:17:45 | all Mages oob | +0.4494% | +1.4948% | +1.0454% |
| **TOTAL** | — | — | — | **+6.3305%** | **+3.0128%** | **-3.3177%** |

## THE THREE REASONS IT LOSES

**1. THE END CONDITION CUTS THE ACID-TEST LEG SHORT BY 4 h 56 m.** 02:31 reads LARGE LEG at
04:16:50, validates at 04:19:50, and then the next ws1cp-ib at 05:44:35 has 12 of 12 Mages oob so
the end fires - at +1.7219% against the banked +4.5067%.

**2. ALL-MAGES-OOB AS A HANDOFF DOES NOT RESCUE IT EITHER.** Joe: *"the use I see in 'all mages
out': it's a sign to defer to momentum. in a way, that's what we've already built"*. He is right that
the machine already serves it - link 3 asks the n-of-7 question at that bar. Measured:

| trade | the all-Mages-oob bar | link 3: n of 7 | held? | link 4 ends | gross | against banked |
|---|---|---|---|---|---|---|
| 07-18 02:31 SHORT | 2026-07-18 05:44:35 | **0 of 7** | no | 2026-07-18 05:46:40, max jumpstart gap | +1.6049% | **-2.9018%** |
| 07-18 18:45 LONG | 2026-07-18 21:17:45 | 1 of 7 | no | 2026-07-18 21:17:55, exhaustion | +1.5793% | +1.1299% |

There is no momentum at 05:44:35 to defer to. The end-the-walk and defer-to-link-3 routes land
within 0.12% of each other and 2.9% below the banked walk. THE REAL PROBLEM IS HAVING A DECISION
POINT AT 05:44:35 AT ALL - the banked move test gave RIDE at 04:16:50 and then said nothing until
10:40:40. It had no 05:44:35 event to get wrong.

**3. THE GAP BETWEEN EVENTS IS UNBOUNDED, AND 18:12 PROVES IT.** Its ws1cp-ib is 2026-07-18
18:44:10; the next ws1Mage oob is **5 h 43 m later** at 2026-07-19 00:27:45. The loop validates on a
cascade measured 5 h 43 m earlier, walks into the next day, and ends at -2.1730%.

## THE EMPTY-BLOCK BRANCH IS MINE, AND IT CARRIED 3 OF THE 6 VERDICTS

At a ws1cp-ib, if no TF above ws1 is both lagging and heading, there is no cascade to follow, so I
end the walk. It is NOT Joe's end condition:

| state | what it means |
|---|---|
| Joe's end, all Mages oob | every line has arrived at the target end |
| my empty block | no line is both behind ws1 AND moving toward the target |

A line can be behind and moving away, so the block empties while nothing has arrived. Measured at
2026-07-18 20:16:40: block 0, **2 of 12** Mages oob. It fired on 21:58, 16:07 and 18:12 - including
the worst row in the table.

## WHAT IS WORTH KEEPING

| piece | verdict |
|---|---|
| test 1, the sampling match | classifies 04:16:50 and 20:03:25 correctly, no measured harm |
| test 2, the block, lagging + heading + deepest gap | same, and the acid test passes |
| the one-time g30 validation | improves 16:07 by +0.4346% and 18:45 by +1.0454% |
| **the end condition, either as an end or a handoff** | costs 2.90% on 02:31. DO NOT SHIP |
| **the unbounded gap between events** | costs 2.62% on 18:12. DO NOT SHIP |
| my empty-block branch | unmeasured against any alternative, and it decided 3 of 6 |

The two improvements are real but they ride on a walk that loses 3.3177% over the set. Splitting them
out needs a ruling on what replaces the end condition, which Joe has not given.

## THE DRIVERS

Throwaway, in the scratch dir, not in the repo: `_0414.py` the acid test, `_blk.py` the block
reading, `_loop2.py` the corrected one-time loop, `_all2t.py` the six-trade retest, `_defer.py` the
link-3 handoff, `_samp.py` the sample sets, `_sign.go.py` the three readings of test 2's line.
