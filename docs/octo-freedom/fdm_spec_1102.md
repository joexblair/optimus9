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
    -------walk forward an additional 10 minutes #to capture a late ws30r
    -------IF ws30r reverses inside the 10 minute range
    --------truncate the 10 minute walk forward, and print exhaust, and send rev-trade to router
    -------ELSE #if ws30r has not reversed inside the 10min window, then our only option is walk to
           the next cadence, or a ws10x fallback (the backstop)
    --------this cadence window is closed - cadence event is printed here. walk to the next cadence
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
| 0 | SETTLED 1102 - the fdm-cadence level-4 scan's range is **ws2 to ws12**, his words: *"ws2 to ws12.  the scan can only look upwards"*. ws1 is excluded. ONE THING HIS "upwards" DOES NOT FIX: whether it means the range is read from ws2 upward, or that the scan never adds a TF below the ones already in the array |
| 1 | SETTLED 1102 - the fence is `fdm-20-80-fnc`, his name, value 20, read as (100 - 20) = (20.0, 80.0) |
| 2 | SETTLED 1102 - his design, not a gap: *"the scan-while-walking adds more TFs to an array, and the reversal gate on the highest TF in the array automatically overrides the notion of a rider"*. The array IS the anchor, and the highest TF in it is what the reversal gate reads. See THE RIDER QUESTION below |
| 3 | `walk forward until ws1b is ib ELSE walk forward until gcws30b is ib` - what makes the ELSE fire. His note says *"ie we will use the fast gcws30 line in the absence of exfence lines"*, which reads as a condition on the lines, not on ws1b |
| 4 | "the last two cadence events" - the ws{>25}r ex-fence lookback. Two events of either side, or two same-side |
| 5 | "the prior same-side cadence window opened" - the blast radius's reversal window. Its opening bar, or its closing bar |
| 6 | which 5 TFs `fdm-blst-rad-conf-tfs` names - the 5 immediately below the highest ex-20/80 line, or the 5 lowest of the collected set |
| 7 | SETTLED 1102 - the line is now *"walk forward an additional 10 minutes #to capture a late ws30r"* with no "from cadence event", and it moved to level 7. The anchor is the bar the walk is on |
| 8 | "if a last cadence event fails to print" - what makes a cadence event the last one |
| 9 | the reversal reads: he names *"emerging lift-off"* for the highest-oob-TF test and *"lift-off-reversed"* for the ex-20/80 lines. Whether the second is emerging too |
| 10 | wsf is ws1-ws12 and dtf is >ws12, his 1017 band names. Confirmed by those, not by this spec |

## THE 1102 INDENT MOVE, AND WHAT IT CHANGES

He ruled: *"that should be in lvl7, not lvl6"* / *"every line under "walk forward an additional 10
minutes" needs one additional indent, so that "IF ws30r reverses inside the 10 minute range" is the
same level as "walk forward an additional 10 minutes""*.

| the line | was | now |
|---|---|---|
| walk forward an additional 10 minutes | level 6 | **level 7** |
| IF ws30r reverses inside the 10 minute range | level 6 | **level 7** |
| truncate, print exhaust, send rev-trade | level 7 | level 8 |
| ELSE, with his narration | level 6 | **level 7** |
| this cadence window is closed, walk to the next window | level 7 | level 8 |

SETTLED 1102: *"the 10min capture is correctly placed"*. So the late-ws30r capture nests INSIDE
`------if any ws{>25}r has printed ex-fence inside the last two cadence events` and runs only when
that test holds. It is a sibling of the collect and the 4-of-5 blast-radius test, not of the
ws{>25}r test itself.

## THE RIDER QUESTION - his design, and I am not pushing back

He invited it: *"pushback if you need to"*. I do not.

| what he said | what the code says |
|---|---|
| *"the scan-while-walking adds more TFs to an array"* | the level-4 loop line: *"while the walk is walking, scan for new {lines inside of lin-hops reach} crossing to oob. add any new oob lines to the current list of "wsf r`s" lines"* |
| *"the reversal gate on the highest TF in the array automatically overrides the notion of a rider"* | the level-4 test: *"IF ws{highest TF that is oob}r has reversed on emerging lift-off"* |

In lineage2 the rider was two things at once: the rung whose reversal decides, and the anchor the
candidate band is measured from. This mech splits them. The array holds every oob line the walk has
found, the decision reads its highest TF, and the array grows by its own scan - so there is no rung
to measure a band from because nothing is being handed anything. His *"I'm swapping `ib` with
`reverse`. there is no rider in this mech"* is the same statement from the other side.

ONE THING THAT FOLLOWS, and it is a real question rather than a pushback: with no rider, the phrase
*"lines inside of lin-hops reach"* in the scan has nothing to measure a reach from either. The scan
needs a range. Three readings exist and none is his yet - within `L2_LIN_HOP` of the array's
highest TF, of its lowest, or the whole board. The lineage2 value was 2.

## THE RE-ENTRY MECH, REVIVED 1102

His word: *"revive the latest re-entry mech from the last machine"*. This is his 1101 update
verbatim, which was never built - it was gated on four of his answers and lineage2 was sealed with
it still pending. It is carried here so the greenfield build has it.

    re-entry
    delete the current ws5Mage reentry (from spec and code)
    -IF there is no trade open (because of a STOP, or because of the machine starting)
    --IF gcws30b is ex-95/5-fnc
    ---OPTION 1 (possibly defunct): walk the bars until ws1r, gcws30b, and ws{>1}r are all
       same-side oob (example: high side 09-04 1128)
    ---OPTION 2: IF any 2 TFs are same-side of gcws30b and ex-v4mom-fence (example 08-14 0529,
       ws3 and ws4)
    ----the highest TF is tagged as the rider. arm is not required
    ----follow the lineage walk (baton pass on rider to ib)
    ----IF lineage prints exhaustion (example: 09-04 1221 on ws11, 08-14 0600 on ws7)
    -----send a trade signal to the router (ie the router will handle the OPEN)

### WHAT IT WAS GATED ON, 1101 - still open

| # | the question | his 1102 answer |
|---|---|---|
| 1 | does the `gcws30b is ex-95/5-fnc` read carry the wob 6 | the LINE is the chart-matched read, banked - `LIN2_CP_GCWS30B` 'closed_prev'. *** THE WOB 6 IS A NO-OP ON IT: *** gcws30b steps once per 30 s = 6 bars, so a 6-bar hold spans exactly one coarse bar and can never ask for a second. Same shape as the t1 xwob he agreed was confirming nothing |
| 2 | does OPTION 1 stay unbuilt | *"option1 stays unbuilt"* |
| 3 | which timeframes the *"any 2 TFs"* scan covers | STILL OPEN - *"I'll need to see my spec notes"* |
| 4 | the signal's direction rule | *"the oob side where the lines were found"* |
| 5 | whether a rider-and-ib walk stays alive beside fdm-cadence | *"that's fine - it only fires for re-entry"* |

### WHAT CHANGED UNDER IT SINCE HE WROTE IT

| the piece | then | now |
|---|---|---|
| `follow the lineage walk (baton pass on rider to ib)` | lineage2's walk, with a rider | fdm-cadence has no rider and swaps `ib` for `reverse`. The sentence points at a mech that no longer exists in that form |
| `the highest TF is tagged as the rider` | the rider was the band's anchor and the deciding rung | in fdm-cadence the array's highest TF is the deciding rung and nothing is an anchor |
| `gcws30b` | emerging | he banked it on the chart-matched read on 1101 |
| `ex-v4mom-fence` | the r fence, 25/75 at RMOM_FNC 75 | unchanged, and it is NOT the new `fdm-20-80-fnc` |

*** THE ONE THAT MATTERS: *** the re-entry's body is three lines of lineage2 - tag a rider, baton
pass to ib, read the exhaust. fdm-cadence has none of those three. Reviving the mech as written
means either keeping a rider-and-ib walk alive beside the new one, or rewriting those three lines
against fdm-cadence. That is a design call and it is his.
