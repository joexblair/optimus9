# THE EX-FENCE LATCH RE-LATCH MECH - his 1031 rulings, as given

NOTHING IS WIRED. This is the ruling sheet, written as each ruling landed.

## the release, revised 1031

His 1029 spec line read *"-the latch releases on barrage's signal"*. His 1031 replacement, verbatim:
*"I was premature to use barrage - it wasn't fully tested and clearly isn't helping us on our
08-14 0659 walk / replace "-the latch releases on barrage's signal" with "-the latch releases on
lift-off's signal""*. APPLIED: `LIN2_EXFNC_LATCH_REL` default and ruling moved 'bank' -> 'lift',
and the old arm renamed 'barrage'.

## the fault that revision exposed

A lift-off can fire while the line is STILL ex-fence, which ends the latch episode. The on-edge is
a CROSS from in-fence to ex-fence, so a line that has not reached in-fence has no edge available
and stays unlatched. His read: *"the reversal "bumped" the line closer to in-fence, but infence was
never reached"*.

MEASURED, 2026-08-14 07:02:10, side low, fence (25.0, 75.0), ladder ws1..ws30:

| the read | value |
|---|---|
| rungs past the fence by value | ws5 19.09, ws7 22.93, ws8 4.46, ws9 12.02, ws10 7.65, ws11 24.41, ws27 19.05, ws28 24.89 |
| of those, LATCHED | ws9, ws10, ws11, ws27, ws28 |
| of those, NOT latched | ws5, ws7, ws8 |
| ws8's release stamp | 2026-08-14 06:50:55, 11.3 min before the cadence |
| ws8's value at the cadence | 4.46, as far past the 25.0 fence as the window gets |

## OPTION 1 - RULED IN. the fall-back test, plus his candidate rule

His option, verbatim: *"if lift off prints a reversal for a line, and that line's value falls back
to the value printed at lift-off, re-enable the latch"*.

His candidate rule, 1031, verbatim: *"if ws12 is printing 31, then it's infence and it must return
to ex-fence if it wants to be latched. it shouldn't be included in the "bump that pushes a line
towards infence, only to fail reaching infence" candidates"*.

So the mech is two tests, both kept - his *"keep the fall-back test anyway - absolutely"*:

| # | the test | the bar it reads |
|---|---|---|
| 1 | the lift-off that released the latch fired while the line was STILL ex-fence | the lift-off bar |
| 2 | and the line has not reached in-fence between that lift-off and now | every bar from the lift-off to the cadence |
| 3 | and the line's value has come back to the value it printed at that lift-off | the cadence bar |

AT CADENCES ONLY, his ruling and his reason: *"cadence only.  the point of cadences: at ws1r
reversing, that is the moment when matryoshka is leading the higher lines direction"*.

MEASURED on the four t1 cadences of the 0659 walk:

| the t1 cadence | the candidates - tests 1 and 2 | count | of those, test 3 fires | count |
|---|---|---|---|---|
| 2026-08-14 07:02:10 | ws5, ws7, ws8, ws29 | 4 | ws5, ws7, ws8, ws29 | 4 |
| 2026-08-14 07:14:15 | ws8, ws9, ws10, ws29 | 4 | ws8, ws9, ws10, ws29 | 4 |
| 2026-08-14 07:34:35 | ws10, ws12, ws29 | 3 | ws10, ws12, ws29 | 3 |
| 2026-08-14 07:47:20 | ws10, ws11, ws12, ws13, ws14, ws29 | 6 | ws10, ws11, ws12, ws13, ws14, ws29 | 6 |

Test 3 fires on 17 of 17 candidates. His reading of that: *"that was my expectation: it proves
that the leg is continuing its trend"*.

## OPTION 2 - DROPPED 1031

His word: *"1, drop option 2"*. No mechanics, no numbers, no arms kept here.

## the rider jump - his 1031 rule

*"at a cadence marker, the rider TF can only jump by {knob:8} TFs"* / *"arm starts with rider=0. at
the 0701 t1, the rider is ws8"* / *"for this lineage walk, a riderTF can advance no more than
{knob:8} TFs - this makes the rider ws8 (or techincally ws7, because init rider is zero) for this
cadence"*.

WITH OPTION 1 IN, THIS RESOLVES WITHOUT A VALUE READ. The re-latch puts ws5, ws7 and ws8 back in
the latched set at 2026-08-14 07:02:10, so "the highest LATCHED rung at or below rider + 8" gives
ws8 - his answer - and the rider scan keeps querying the latch exactly as his 1029 spec requires.
Before the re-latch mech, no rung at or below ws8 was latched and that reading gave nothing.

## his 1031 rulings on the five open items

| # | the item | his ruling |
|---|---|---|
| 1 | option 2 | DROPPED 1031 - *"1, drop option 2"* |
| 2 | option 2's window | moot, dropped |
| 3 | the rider jump bound | *"ws8.  it's a knob, so either way we can tune if needed"* |
| 4 | what releases a re-latched line | *"yes"* - the next lift-off on that line, reviewable the same way at the following cadence |
| 5 | raw bar or stamp for test 1 | *"understood and agreed - good catch"* - THE RAW BAR |

### the limbo statement, withdrawn

I proposed that the lift-off release only fire once the line has reached in-fence. His read: *"would
not this leave lines in limbo?  I feel uneasy about your statement"*. He is right: a line that stays
ex-fence would never be released, which is the barrage-arm fault he rejected. His own shape has no
limbo - the release is real at the lift-off, and each cadence reviews it.

## OPEN, still his

| # | the item |
|---|---|
| 1 | whether the rider jump bound applies to the v4-arm-lineage-retest gate's own re-scan |
| 2 | the opposite-side ex-fence clear - HELD 1031, *"I haven't given up on barrage yet"*. Mine, unattributed, alive only in the 'barrage' release arm |
