# The cadence event redesign, 2026-11-07

HIS DESIGN. Every ruling below is his, quoted. The few readings that are mine are marked MINE and
are the only places a reader should look for my judgement. NOTHING IS BUILT FROM THIS YET.

## WHY IT EXISTS - the three faults it closes

| the fault | the bar that caught it |
|---|---|
| the two-lines-above clause passed because it had nothing to check | 2026-08-23 12:07:15 - ws30 was the highest ex-20/80 `towards` line, nothing sat above it, and the rev-trade closed a +4.978% LONG |
| the cadence event issued no verdict of its own - it started a race and five mechs could each answer later | 2026-08-23 02:23:00 answered at 02:32:15 (555 s late) and 2026-08-23 16:17:00 at 16:32:15 (915 s late) |
| the one-shot fdm2-momo latch silenced a whole cad walk from its weakest-signal bar | the 28 legs it held longer went +32.523% to +25.974% |

HIS RULE, which the redesign exists to satisfy: *"cadence event can only produce cad_walk or
cad_rev-trade - there is no third option. the mechs that stand up to receive the cadence event's
verdict are also built with only 2 verdicts."*

## THE THREE VERDICT OWNERS, AND HIS PREFIXES

HIS 1106: *"prefix them with `cad_` and `cwlk_`"*, and HIS 1107: *"prefix for ws{TF}x-cross events:
`cwsx_`"*.

| the owner | its prefix | its verdicts |
|---|---|---|
| the cadence event | `cad_` | `cad_walk` or `cad_rev-trade`. Nothing else |
| the cad walk | `cwlk_` | `cwlk_rev-trade`, or its timecap expiring |
| the ws{TF}x-cross event | `cwsx_` | its 50% reversal rule and its grace walk resolving - *"not a third thing - just the two resolveing"* |

HIS 1106 on why the distinction matters: *"I'm calling this out specifically to ensure there is a
strict distinction between `cadence event`'s verdicts and `cad walk`'s verdicts."*
HIS 1106 on how he will speak: *"I'm still going to use 'rev_trade' or 'walk` when I talk with you,
because I often won't be looking at the debugging events. if it's ever ambiguous, call me out."*

## THE `4-pronged-exfence-test` - HIS NAME, 1106

| the prong | the read |
|---|---|
| 1 | closed-prev, on the 1min bar ending at the ws1 seam BEFORE the cadence event |
| 2 | emerging, same 1min bar - the side's extreme across it |
| 3 | closed-prev, on the 1min bar ending at the ws1 seam AFTER the cadence event |
| 4 | emerging, same 1min bar - the side's extreme across it |

| the rule | his words |
|---|---|
| the side | *"for a high target side, report the bars' high. for a low target-side, report the bars' low"* - 1105 |
| the window | *"it's the ending of the seam - if you think about it, that's the only way to capture the highest/lowest emerging value for the bar"* - 1107 |
| what it prints | `passed` when ANY r is `towards` while ex-20/80-fence. HIS 1107 on the cadence event's verdict: *"does any r towards while ex-fence mean cad_walk -- yes"* |
| the lines | ws4..ws30. HIS 1107: *"keep it the minTF at ws4"* |
| where it fires | at the cadence event, and *"on every ws1 seam during a cad walk, if the cad walk has been initialised"* |
| the pair, on a re-read | *"roll forward a minute at a time"* - 1107 |
| one read, not two | *"same - not two variants"* - 1107 |
| it REPLACES the board test's ex-fence read | *"replace unless you can see a negative consequence"* - 1106 |

HIS CORRECTION OF MY FIRST TWO OBJECTIONS, 1106, both of which I withdrew:
> *"ex-fence is a value that you **capture** at the seam grid. ex-fence if not a thing that you
> move: it's bound by the r line's contract, which can't be affected by a test"*
> *"the walk is stil walking every 5s bar regardless of ex-fence testing, so what is to stop the
> walk from accepting a rev-trade signal?"*

So the capture happens on the seam; the board test keeps its 5 s rate and reads the latest captured
value. There is no rev-trade delay and no mixed-rate test.

## WHY THE CADENCE EVENT FIRES 55 s AFTER THE WINDOW CLOSES - his option 6

HIS CONSTRAINT: *"it has to be incorporated because we can't lookahead for the bar after cadence
event, and without knowing the 4-pronged-exfence-test verdict there is no way for the cadence evnt
to fire an accurate verdict."*
HIS CHOICE: *"I like option6 - moving the cadence event outside of the cadence window's end and
testing at the window's end makes the most sense."*

| the bar | what it is |
|---|---|
| the window's close | ws1b crosses back to ib. That bar is the last 5 s bar of a 1min bar, so it is a ws1 seam, at HH:MM:55 |
| the first read | taken AT the close, on the 1min bar ending there |
| the cadence event | the NEXT ws1 seam, 55 s later. The first bar its verdict is knowable |
| the second read | taken at that bar, on the 1min bar ending there |

- the 55 s is not a delay anyone chose. It is when the information exists.

## THE FLOW

```
-cadence window opens
--ws1b goes oob on the trade's target side

-cadence tasks complete
--all of the preamble's tests, inside the window

-cadence window closes
--ws1b crosses back to ib
--that bar is the last 5s bar of a 1min bar, so it is a ws1 seam
--the 4-pronged-exfence-test takes its FIRST read here
---the 1min bar ending at this seam, closed-prev and emerging
---for a high-side target take the high, for a low-side target take the low

-one 1min bar later, at the next ws1 seam, 55s after the window closed
--the 4-pronged-exfence-test takes its SECOND read, same two reads, same side rule
--the test prints passed when ANY r on ws4..ws30 is towards while ex-fence
--the cadence event fires HERE, the first bar its verdict is knowable
---passed      -> cad_walk
---not passed  -> cad_rev-trade

-IF cad_rev-trade
--the leg closes, the router opens the opposite

-IF cad_walk
--the race begins: {stop, cadence window open, ws{TF}x-cross}
--the cad walk begins, at this same bar
--the cad walk races: {cwlk_rev-trade, cad-walk timecap 10min}
---every ws1 seam, the 4-pronged-exfence-test re-reads
----the pair rolls forward one 1min bar at a time
----IF passed -> walk directly to the next cadence event
-----no other mech may touch the leg until that cadence event is reached
-----the mae1.1 stop is UNCONDITIONAL and still applies
---every 5s bar, the board test asks: is any r towards while ex-fence
----the ex-fence value is the 4-pronged-exfence-test's latest read
----fdm2-momo votes first, and 3 of 3 vetoes the board test at that bar only
--IF cwlk_rev-trade
---the leg closes, the router opens the opposite
--IF cad-walk timecap
---wait for the race's winner

-the race's winners
--stop wins
---the leg goes flat, only the fdm re-entry opens another
--cadence window open wins
---back to the top
--ws{TF}x-cross wins
---the cwsx_ event owns everything that follows
----its 50% reversal rule fires at the cross
----its grace walk runs
-----IF the 4-pronged-exfence-test prints passed for any TF
------walk to the next cadence event
----those two resolving IS its verdict
```

HIS WORDS BEHIND THE LAST BLOCK, 1107: *"these all belong to the ws{TF}cross event. they fire when
the ws{TF}x crosses. during the grace walk, IF the target-side 4-pronged-exfence-test prints
`passed` for any TF, then walk to the next cadence event."*
HIS WORDS ON THE DIRECT WALK, 1107: *"IF the latest read == passed then walk directly to the next
cadence event (no other mech can touch the walk until the next cadence event is reached)"*, and on
the stop: *"the mae1.1 stop is unconditional - my "no other mech can touch the walk" didn't allow
for the stop"*.

## WHAT MOVES, WHAT GOES, WHAT STAYS

| the mech | what happens to it | his words |
|---|---|---|
| the two-lines-above clause | DELETED | *"this is unwanted drag"* |
| the tagged scope for the second clause | DELETED with it | - |
| step 1's count | REDUNDANT - the 4-pronged test asks the same question | *"if step 1s only job is to test for "towards ex-fence lines", then it is redundant"* |
| the 50% reversal rule | MOVES to the `cwsx_` event | *"these all belong to the ws{TF}cross event"* |
| the grace walk | MOVES to the `cwsx_` event, and the 4-pronged test can end it early | same |
| the ws{TF}x-cadence's verdict branch | MOVES to the `cwsx_` event | same |
| the `exfnc` whole-board fallback | REPLACED by the 4-pronged test at the cadence event | *"replace unless you can see a negative consequence"* |
| the race's candidate picker | STAYS - without it there is no race line | MINE: it is the only thing that names the ws{TF} the race runs on |
| the cad walk's 10 min timecap | STAYS, his own value | he names it *"cad-walk timecap"* |
| the mae1.1 stop | STAYS, unconditional | *"the mae1.1 stop is unconditional"* |
| fdm2-momo's per-bar veto | STAYS, inside the cad walk | his 1106 RCA |

## THE KNOBS THIS TOUCHES

| the knob = its value | what happens |
|---|---|
| FDM_XCAD_ABOVE = 2 | no reader left. Striking it from the bank needs his word |
| FDM_XCAD_C2_SCOPE = tagged | no reader left. Same |
| FDM_XCAD_RULE = A | no reader left. Same |
| FDM_XCAD_EXF = 0 | no reader left. Same |
| FDM_XCAD_FALLBACK = exfnc | its branch is replaced by the 4-pronged test |
| FDM_STEP1_ABOVE_TF = 3 | KEEPS ITS VALUE and gains a new role: the 4-pronged test's minimum timeframe, ws4. Its NAME now points at a deleted mech - renaming it needs his word |
| FDM_EXF_EM_BARS = 12 bars = 60 s | unchanged. Read at a seam it spans one whole 1min bar, which is exactly his 1105 *"between the seams"* |
| FDM_XCAD_FRM = confirm | the cad walk no longer starts from the race's confirm, so this has no reader |
| FDM_XCAD_SEAM_S = 15.0 | the cad walk now starts AT the cadence event, so the +15 s offset has no reader |

## A CORRECTION TO WHAT I BUILT ON 1106

His second RCA replaced the two clauses with one board-wide test, and I wrote that test over
ws1..ws30, citing his 1016 ruling that `board` means the full range. HIS 1107 *"keep it the minTF at
ws4"* settles it the other way: the test reads ws4..ws30. The code must be corrected before any run
is scored on it.

## OPEN - nothing on the flow, these are build items

| # | the item |
|---|---|
| 1 | the code's `passes()` means the OPPOSITE of his `passed`: it returns true when NO r is towards while ex-fence. His word wins; the function needs renaming so the two cannot be confused |
| 2 | striking the four dead knobs from the bank, and renaming FDM_STEP1_ABOVE_TF |
| 3 | whether the `cwsx_` event's two mechs keep their current thresholds - 50% to trade, 40% grace floor, 5 min grace walk |
| 4 | the fdm2-momo medians were measured against the OLD cad walk, which started at the race's confirm. Bolting the cad walk to the cadence event changes the population they were measured on |

---

# BUILD LOG, 2026-11-07

HIS GO on build items 1 and 2: *"1,2 - yes"*. On 3 and 4: *"3,4 - keep them for now"*.

## ITEM 1, DONE - the polarity collision is gone

| before | after |
|---|---|
| `passes(b)` returned True when NO line was towards while ex-fence | `exf_passed(b)` returns True when a line IS, which is HIS `passed` |
| the caller read `ok = passes(b)` | the caller reads `passed, why = exf_passed(b)` then `ok = not passed` |

- his word now means the same thing in the code and in conversation, so the two cannot be mixed up
- the every-bar trace and the leg report print `passed - walk on` or `NOT passed - REV-TRADE`

## ALSO DONE - the minTF correction

His second RCA's board test was written over ws1..ws30 by me, citing his 1016 full-range ruling.
HIS 1107 *"keep it the minTF at ws4"* settles it the other way, and the test now reads
ws{FDM_STEP1_ABOVE_TF+1}..ws{HI} = ws4..ws30 = 27 lines.

## ITEM 2, NOT DONE - and why I did not force it

Every one of the seven knobs still has a LIVE reader, because the redesign is not built:

| the knob = its value | its live readers today |
|---|---|
| FDM_XCAD_ABOVE = 2 | the race's candidate picker, the tag read, the chain driver's own header |
| FDM_XCAD_C2_SCOPE = tagged | the chain driver's both-verdicts arm |
| FDM_XCAD_RULE = A | the candidate picker |
| FDM_XCAD_EXF = 0 | the candidate picker |
| FDM_XCAD_FALLBACK = exfnc | the whole-board fallback branch, still live |
| FDM_XCAD_FRM = confirm | the seam read's start bar, still the race's confirm |
| FDM_XCAD_SEAM_S = 15.0 | the cad walk's first bar, still seam + 15 s |

- they are dead UNDER the redesign, not dead today. Striking them now breaks the candidate picker,
  the fallback and the cad walk's start bar.
- SO ITEM 2 WAITS for the redesign to land. The same applies to renaming FDM_STEP1_ABOVE_TF: it has
  16 readers and its value is now his minTF, so the rename goes in with the redesign.

---

# HIS 1107 EVENT LIST, BANKED - `fdm2_leg_event`

HIS ASK: *"actioanable events to cache (and to report on in the leg report)"*, and on the
infrastructure: *"DB tables are in your wheelhouse - you have complete control of the infra"*.

## WHAT HE ASKED FOR, AND WHAT IT IS CALLED NOW

| his event | the kind | the owner | rows on 2026-08-23 |
|---|---|---|---|
| cadence window open | `cad_window_open` | the cadence event | 11 |
| cadence window closed | `cad_window_closed` | the cadence event | 11 |
| any race results | `cad_race` | the cadence event | 6 |
| ws{TF}x cross | `cwsx_cross` the raw cross, `cwsx_confirm` after the hold | the ws{TF}x-cross event | 6 and 6 |
| 50% test decisions | `cwsx_pct` | the ws{TF}x-cross event | 2 |
| grace walk events | `cwsx_grace_start`, `cwsx_grace_expired` | the ws{TF}x-cross event | 0 - the grace walk did not run that day |
| fdm2-momo decisions | `cwlk_momo_vote` | the cad walk | 3 |
| rev-trade signal | `leg_rev_trade_signal` | the leg | 5 |
| exit event | `leg_exit` | the leg | 11 |
| 4-pronged-exfence-test decisions | NOT BUILT | - | - the redesign has to land first |

ALSO BANKED, because a timeline without them cannot be read: `leg_open`, `cad_walk`,
`cad_rev_trade`, `cad_no_action`, `cwlk_seam`, `cwlk_start`, `cwlk_rev_trade`, `cwsx_rev_trade`,
`cwsx_no_action`.

HIS RULING 3 IS APPLIED TO THE LABELS: the 50% rule's verdict, the grace walk's hit and the
under-40% branch all moved from `cad_` to `cwsx_`, because *"these all belong to the ws{TF}cross
event"*. Only step 1's zero count and the no-candidate branch still print `cad_rev_trade`.

## THE TABLE

| the choice | why |
|---|---|
| ONE table, NULLable per-kind columns | the house pattern, `l2_live_seam_event`. A table per kind would split one leg's timeline across ten joins to read it in order |
| `f2e_knobs` in the unique key | a 12-char hash over EVERY banked knob. His own rule, and the fault that bit us on 1106 - ab_legs.json held 2,453 rows with no record of the knobs behind them, so a report replayed a superseded arm |
| `f2e_tape_end` in the key | a different tape is different rows |
| `f2e_seq` in the key, NOT NULL DEFAULT 0 | MySQL lets two genuinely distinct events collide on a key, and a silent overwrite is worse than a duplicate. The re-entry producer already emits two signals on one bar |
| `f2e_tf` NOT NULL DEFAULT 0 | the precedent's own lesson: a NULL inside a UNIQUE KEY never collides in MySQL, so every re-run would duplicate the rows that have no timeframe |
| every write an upsert | a re-run is safe |
| `f2e_arm` beside the hash | so a reader does not have to decode the hash to see which arm produced the row |

- 2026-08-23 banked 93 rows across 11 legs and 16 kinds, knob hash `08e57da0aad1`, arm `momo_ON=1`
- the 4-pronged test needs no schema change when it lands: the kind is a column, not a table
