# machine: final-draft-maybe - THE SPEC AS HE RULED IT, 2026-11-02

HIS SPEC, with the six things he settled on 1102 folded in. Nothing here is mine except the
"OPEN FOR THE BUILD" list at the end, which is what a build would otherwise have to guess.

## mech: fdm-cadence

    cadence windows open when ws1r or ws2r or ws3r oob AND are nestled inside of ws1Mage at any
    time during
    -#nestled: ws1Mage is deeper oob when ws1-3r is less deeper oob
    #cadence events fire when the cadence window closes
    -if a cadence window is open
    --walk forward
    --IF ws{lowest of ws{1,2,3}r that is oob}r is ib AND ws3Mage is ex-20/80-fence
    ---IF any wsf r`s are still oob
    ----#this is the loop I refer too later
    ----walk forward. while the walk is walking, scan for new {lines inside of lin-hops reach}
        crossing to oob. add any new oob lines to the current list of "wsf r`s" lines
    ----IF ws{highest TF that is oob}r has reversed on emerging lift-off
    -----IF there are wsf and dtf lines that are ex-20/80-fence AND have not lift-off-reversed
          after crossing to ex-20/80-fence
    -----#that line  <- for the goto command I set later
    ------walk forward until ws1b is ib ELSE walk forward until gcws30b is ib
    ------if any ws{>25}r has printed ex-fence inside the last two cadence events
    -------collect the number of lines that are 1) a TF that is lower than the highest
           "ex-20/80-fence wsf or dtf line" and 2) have reversed since the prior same-side cadence
           window opened
    -------IF 4 of the 5 fdm-blst-rad-conf-tfs r lines have reversed
    --------EXHAUST and send rev-trade to router #stub
    ------walk forward an additional 10 minutes from cadence event
    ------IF ws30r reverses inside the 10 minute range
    -------truncate the 10 minute walk forward, and print exhaust, and send rev-trade to router
    ------ELSE #if ws30r has not reversed inside the 10min window, then our only option is walk to
          the next cadence, or a ws10x fallback (the backstop)
    -------this cadence window is closed - cadence event is printed here. walk to the next cadence
           window open
    -----ELSE if no higher r lines are ex-80/20-fence
    ------loop until all of the "wsf r`s" lines have been processed
    ------if the loop ends on a bar that detects "wsf and dtf lines that are ex-20/80-fence AND
          have not lift-off-reversed after crossing to ex-20/80-fence"
    -------continue from that bar, at the line tagged "#that line", and keep walking
    ------this cadence window is closed - cadence event is printed here
    ------send rev-trade to router #stub

### HIS 1102 RESOLUTIONS, each one quoted

| # | what was unclear | his ruling |
|---|---|---|
| 1 | the `#cadence events fire...` comment sat at level 1, so the whole mech nested inside a comment | *"yes, this should be level 0, beside the opener"* |
| 2 | "nestled" had a definition but no threshold | *"there is no threshold. the requirement is for ws1Mage's value to be greater than ws1r for a high side excursion, and for ws1Mage's value to be less than ws1r for a low side excursion"* / *"when this qualifies, it stays qualified until the cadence window ends"* |
| 3 | which r line the nestle compares against when ws2r or ws3r is the oob one | asked whether his comment naming all three was the rule: *"confirmed"*. So it is ws1Mage against whichever of ws1r, ws2r, ws3r is oob |
| 4 | the `#that line` goto had no bar | *"continue from the bar that detects wsf and dtf lines that are ex-20/80-fence"* |
| 5 | the blast radius mixed a 5-TF set with an 80% gate | *"I must have overthought that piece of the mech. it's 4 of 5, not a percentage"* |
| 6 | whether a window close without an exhaust trades | *"only if I've explicitly stated exhaust"*, and the ELSE under the 10-minute ws30r test was missing its narration |

### HIS NESTLE EXAMPLES, VERIFIED 1102 - target side high, oob 15.0/85.0

| the bar | ws1r | ws1Mage | ws1Mage > ws1r? | qualifies? | ws1r oob? |
|---|---|---|---|---|---|
| 2026-08-14 15:24:00 | 84.19 | 73.47 | no | no | no |
| 2026-08-14 15:24:30 | 90.69 | 86.91 | no | no | YES |
| 2026-08-14 15:25:00 | 91.74 | 97.04 | YES | YES | YES |
| 2026-08-14 15:25:30 | 96.24 | 94.97 | no | no | YES |
| 2026-08-14 15:26:00 | 75.87 | 84.10 | YES | YES | no |

His 1524 figures were ws1r 91.7 / ws1Mage 86.9 - the 15:24:30 bar reads 90.69 / 86.91. His 1525
figures were 88.7 / 94.1 - the 15:25:00 bar reads 91.74 / 97.04, the relationship he called.
THE RULE FLICKERS PER BAR - it is back off at 15:25:30 - so his *"it stays qualified until the
cadence window ends"* is load-bearing, not a convenience.
ws2r and ws3r are not oob at any of those bars, so these examples do not exercise that path.

## mech: fdm-10x-fallback

    IF ws30r prints oob, latch/ungate any ws10x cross race:{boundary, r, Mage} wob 24 event.
    cross under for high-side, cross over for low-side.
    -this is a fallback that will deploy if a last cadence event fails to print
    -ws10x will be in emerging mode for this fallback mech
    -strictly causal - the ws10x-cross will fire only when latched. if a cadence event fires when
     ws10x-cross is latched, the ws10x cross race:{boundary, r, Mage} event is
     delatched/gated/defunct
    -example ws30r crosses to oob at 08-14 1600, and no further cadences are printed before pxs
     reverses at 1638
    --the latch is latched at 1600 high-side. the wsx10 (emerging) crosses under the race
      candidates with wob24 at 1623

### HIS EXAMPLE, VERIFIED 1102

| the read | value |
|---|---|
| ws30r crosses to the high oob | 2026-08-14 16:00:00, 86.14 from 72.54 |
| emerging ws10x crosses under 85.0 in 16:00:00..16:33:00 | 5 - at 16:00:40, 16:05:25, 16:06:10, 16:21:20, 16:31:45 |
| of those, surviving the wob 24 = 120 s hold | **1** - raw bar 16:21:20, confirm bar **16:23:15** on 72.39 |
| the four that break | at 16:00:50 on 90.81, 16:05:40 on 95.39, 16:06:50 on 89.23, 16:31:50 on 93.63 |
| his own number | 1623 |

The confirm bar matches his 1623 to the minute. His indents are flat here and the mech has no
structural gaps.

## OPEN FOR THE BUILD - MINE, not his. Each one a guess a build would otherwise make

| # | the concretion |
|---|---|
| 1 | the 20/80 fence is a THIRD fence beside oob 15/85 and the r fence 25/75. It needs a knob and a name |
| 2 | "lines inside of lin-hops reach" - the reach is measured FROM a rider, and he wrote *"there is no rider in this mech"*. What anchors the reach |
| 3 | `walk forward until ws1b is ib ELSE walk forward until gcws30b is ib` - what makes the ELSE fire. His note says *"ie we will use the fast gcws30 line in the absence of exfence lines"*, which reads as a condition on the lines, not on ws1b |
| 4 | "the last two cadence events" - the ws{>25}r ex-fence lookback. Two events of either side, or two same-side |
| 5 | "the prior same-side cadence window opened" - the blast radius's reversal window. Its opening bar, or its closing bar |
| 6 | which 5 TFs `fdm-blst-rad-conf-tfs` names - the 5 immediately below the highest ex-20/80 line, or the 5 lowest of the collected set |
| 7 | "an additional 10 minutes from cadence event" - which bar is the cadence event at that point, given the event is printed when the window CLOSES |
| 8 | "if a last cadence event fails to print" - what makes a cadence event the last one |
| 9 | the reversal reads: he names *"emerging lift-off"* for the highest-oob-TF test and *"lift-off-reversed"* for the ex-20/80 lines. Whether the second is emerging too |
| 10 | wsf is ws1-ws12 and dtf is >ws12, his 1017 band names. Confirmed by those, not by this spec |
