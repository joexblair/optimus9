# machine: final-draft-maybe - THE VERBATIM SPEC, original + every update to 2026-11-02

HIS WORDS THROUGHOUT. The only lines that are not his are the ones marked #CLAUDE, which flag the
two places a choice is still open. Take this offline as the new master.

## mech: fdm-cadence

cadence windows open when ws1r or ws2r or ws3r oob AND are nestled inside of ws1Mage or ws2Mage at any time during ws1Mage/ws2Mage's oob excursion
-#nestled: ws1Mage or ws2Mage is deeper oob when ws1-3r is less deeper oob
#cadence events fire when the cadence window closes
-if a cadence window is open
--walk forward
--IF ws{lowest of ws{1,2,3}r that is oob}r is oob while ws3Mage is ex-20/80-fence, and then the selected "lowest TF"'s `r` subsequently crosses to ib # example 08-03 0254, ws3Mage:18.4 and ws1r:10.2 qualify, and the ws1r crosses to ib at 0256
---IF any wsf r`s are still oob # "wsf r`s" means the faster wsf lines, not the "ex-20/80-fence lines" that we test later in the mech
----#this is the loop I refer too later
----walk forward. while the walk is walking, scan for new {lines inside of lin-hops reach} crossing to oob. add any new oob lines to the current list of "wsf r`s" lines
----# the faster wsf lines group (the "wsf r`s") can grow to accomodate any wsf TF if they are detected by the walk's scan. example: 0814 1702 ws7r low oob
----# the scan covers ws2 to ws12. the scan can only look upwards
----IF ws{highest TF that is oob}r has reversed on emerging lift-off #this is a dialed-down version of lineage - I'm swapping `ib` with `reverse`. there is no rider in this mech
-----IF there are wsf and dtf lines that are ex-20/80-fence AND have not lift-off-reversed after crossing to ex-20/80-fence
-----#that line  <- for the goto command I set later
------walk forward until ws1b is ib or is already ib
-----ELSE
------walk forward until gcws30b is ib or is already ib #ie we will use the fast gcws30 line in the absence of exfence lines
-----if any ws{>25}r has printed ex-fence inside the last two cadence events. IF two prior cadence events do not exist in this trade THEN use the trade open bar
------collect the number of lines that are 1) a TF that is lower than the highest "ex-20/80-fence wsf or dtf line" and 2) have reversed since the prior same-side cadence window opened
------#this is the blast-radius test - do the lines within {knob:5,'fdm-blst-rad-conf-tfs'} TFs of the highest TF ex-20/80-fence reverse?  if yes, then it is more likely that the highest TF will follow them, so exhaust can be printed:
------IF 4 of the 5 fdm-blst-rad-conf-tfs r lines have reversed
-------EXHAUST and send rev-trade to router #stub
------walk forward an additional 10 minutes #to capture a late ws30r
------IF ws30r reverses inside the 10 minute range
-------truncate the 10 minute walk forward, and print exhaust, and send rev-trade to router
------ELSE #if ws30r has not reversed inside the 10min window, then our only option is walk to the next cadence, or a ws10x fallback (the backstop)
-------this cadence window is closed - cadence event is printed here. walk to the next cadence window open
-----ELSE if no higher r lines are ex-80/20-fence
------loop until all of the "wsf r`s" lines have been processed #sorry,I couldn't figure out how to say this line logically. the loop I'm refering to is tagged as "#this is the loop"
------if the loop ends on a bar that detects """wsf and dtf lines that are ex-20/80-fence AND have not lift-off-reversed after crossing to ex-20/80-fence"""
-------continue from that bar, at the line tagged "#that line", and keep walking
------this cadence window is closed - cadence event is printed here
------send rev-trade to router #stub

#CLAUDE - ONE STRUCTURAL QUESTION, and it is the only thing in this file that is not settled.
#CLAUDE His 1102 fix gave the walk-until line its own IF/ELSE pair. That IF is the same level as the
#CLAUDE pre-existing "-----ELSE if no higher r lines are ex-80/20-fence", so ONE IF now has TWO
#CLAUDE ELSE branches: the new one carrying the gcws30b walk, and the old one carrying the loop.
#CLAUDE Under his own indent rule that cannot stand. Two readings:
#CLAUDE   a) the new IF/ELSE pair is a SEPARATE test, nested one level deeper than the old IF, and
#CLAUDE      the old "ELSE if no higher r lines" keeps the loop. The walk-until choice is then made
#CLAUDE      inside the branch where the ex-20/80 lines exist, so its ELSE is still unreachable.
#CLAUDE   b) the new ELSE REPLACES the old one, and the loop moves under it. The "absence of
#CLAUDE      exfence lines" case and the "no higher r lines are ex-80/20" case become one branch.
#CLAUDE The lines above are laid out as (a) with his new levels applied as written.

## mech: fdm-10x-fallback

IF ws30r prints oob, latch/ungate any ws10x cross race:{boundary, r,Mage} wob 24 event.  cross under for high-side, cross over for low-side.
-this is a fallback thjat will deploy if a last cadence event fails to print
-ws10x will be in emerging mode for this fallback mech
-strictly causal - the ws10x-cross will fire only when latched.  if a cadence event fires when ws10x-cross is latched, the ws10x cross race:{boundary, r,Mage} event is delatched/gated/defunct
-example ws30r crosses to oob at 08-14 1600, and no further cadences are printed before pxs reverses at 1638
--the latch is latched at 1600 high-side. the wsx10 (emerging) crosses under the race candidates with wob24 at 1623

## mech: re-entry - BUILT 2026-11-02 as v4_fdm_reentry.py

re-entry
delete the current ws5Mage reentry (from spec and code)
-IF there is no trade open (because of a STOP, or because of the machine starting)
--IF gcws30b is ex-95/5-fnc  #the window OPENS here
---the window CLOSES when gcws30b returns to ib - the oob_ib_cross mech, not a value test
---the gate is ws1r AND (ws2r or ws3r), each SEEN ex-v4mom-fence anywhere inside the window
---the lines need to be seen in the window, but do not need to dwell for the window's full range
---tested at gcws30b window's close.  if the test is true, open a trade
---the side is the oob side where the lines were found
-OPTION 1: dropped. "option1 stays unbuilt"
-the lineage walk is dropped: "drop the lineage walk"

## HIS SETTLED VALUES

| the knob or term | value |
|---|---|
| fdm-20-80-fnc | 20, read as (100 - 20) = (20.0, 80.0) |
| what "ex" means on ANY fence he names | "external of", and it INCLUDES oob - *"note my preference: ex-any-fence includes oob - this is my literal use of "ex" meaning "external of""*. So ex-20/80 low means r <= 20, which contains the oob lines at r <= 15 and everything below. Never read a fence as a band |
| fdm-blst-rad-conf-tfs | 5 TFs, selected dynamically as the lines within 5 TFs of the highest ex-20/80-fence TF. 4 of those 5 must have reversed |
| the level-4 scan's range | ws2 to ws12, upwards only |
| the blast radius's reversal origin | the prior same-side cadence window's OPENING bar |
| the ws{>25}r ex-fence lookback | the last two SAME-SIDE cadence events. If two do not exist in this trade, the trade's open bar |
| every lift-off in this machine | emerging bars, always |
| EVERY OTHER LINE READ in this machine | the chart-matched read - *"we're using emerging in lift-off only.  all other line activities are closed-prev"*. A value, a fence test, oob, ex-fence, a cross, an excursion's start: all chart-matched |
| wsf | ws1-ws12 |
| sub-wsf | g5-g30 |
| dtf | above ws12 |
| the re-entry's window fence | gcws30b at or beyond (5.0, 95.0) |
| the re-entry's close | the oob_ib_cross at 15/85, hold 1 bar, so the close is the cross bar |
| the re-entry's gate fence | 75.0, his "ex v4mom fence" |
| the re-entry's trade | a HIGH oob side opens a SHORT, a LOW opens a LONG. Banked in v4_signal.direction |
| the 10-minute capture's place | level 7, inside the ws{>25}r test, which he confirmed as correctly placed |
| the nestle's lifetime | once it qualifies it stays qualified until the cadence window ends |

## WHAT HE HAS VERIFIED AGAINST THE TAPE

| his read | the measurement |
|---|---|
| the nestle at 08-14 1524 does not qualify, 1525 does | 15:24:30 ws1r 90.69 / ws1Mage 86.91 - no. 15:25:00 ws1r 91.74 / ws1Mage 97.04 - yes |
| the fallback's ws10x cross at 08-14 1623 | 5 emerging crosses under 85.0 in 16:00..16:33, 1 survives the wob 24, confirming 16:23:15 |
| the re-entry window closes 08-03 0041 | the oob_ib_cross bar is 00:41:30 - "00:41:30 is my view also" |
| the re-entry's gate at that close | ws1r 00:35:00, ws2r 00:36:00, ws3r 00:36:00, all past 75.0. TRUE |
