# THE LAST-MILE MECH — 1013

Joe 1013: *"now there's one last layer to apply, example 17:39 -when the extension fires, walk the
last mile using lineage"* / *"create a last-mile mode that doesn't rely on ws1cp and fires kickstart
at the last-mile handoff"* / *"the end is the EXHAUSTION event. I'm sure that this is the existing
mech"*.

It runs in `_chain10.py` under `W_ARM=lastmile`, not in a module of its own: it IS the lineage walk,
with the entry conditions and one test changed. The extension mech (`_extmom.py`) hands it the bar.

## THE CHAIN

| stage | mech | 07-18 16:07 LONG's bar |
|---|---|---|
| the trade opens | not shared yet, Joe's open mech | 2026-07-18 16:11:10 |
| the close event fires | the IB-cross mech | 2026-07-18 16:38:15 |
| the close is HELD and extended | `_extmom.py`, the momentum extension | fires 2026-07-18 17:39:10 |
| the last mile walks from there | this file | ends 2026-07-18 18:12:00 |

A close that the momentum test did NOT hold still gets a last mile — it starts at the standing close
bar. Joe 1013: *"we apply the mech to all trades because any improvement is better than none"*.

## WHAT THE MODE CHANGES, AND WHY EACH ONE WAS NEEDED

| # | change | the measurement that forced it |
|---|---|---|
| 1 | ARMED at the handoff — no ws1-cp, no ws{ARM_TF}Mage arm | the banked ws2Mage arm does not fire until 2026-07-18 18:25:10 on this handoff, 46.0 min late and already past the ending. Arming gates the walk, so no other knob reaches it |
| 2 | the KICKSTART fires at the handoff, capped at `LIN_LASTMILE_KCKSTRT_TFCAP` ws5 | uncapped it takes ws12 (r 90.72), the highest oob line under the lineage ceiling, and ws7 can never become the rider. Under the cap it takes ws1 (r 95.74) |
| 3 | the baton moves on the RIDER's oob → ib cross, `W_PASS=crossing_to_ib` | with `W_KICK` low or off the walk starts on ws1 and the exhaustion test ends it on the next bar — ws2 73.41 and ws3 59.44 are already in-fence at the handoff |
| 4 | the receiver must itself be `towards-dr` | without it the baton went to ws5 at 2026-07-18 18:12:00 although ws5 was tagged at 18:05:35, and exhaustion fired a bar later: 18:13:00 / +1.7511% instead of 18:12:00 / +1.7205% |
| 5 | EXHAUSTION's inner test becomes "none of the reach is towards-dr" | see the table below — one substitution corrects two bars |
| 6 | that test replaces the stall gate | Joe 1013 verbatim: *"replaces the stall gate ONLY for the last mile mech"*. At 2026-07-18 18:12:00 the rider ws4 is NOT stalled, so the `on_stall` gate alone blocks the end |
| 7 | `final stalled` is suppressed | MINE, an extension of 6 — it is a stall gate too. Live, it ends the walk at 2026-07-18 17:39:20 on `final stalled on ws1 (r 88.98 O)`, 5 s after the kickstart |
| 8 | the >ws12 mech is off | *"walk the last mile using lineage"*. ws12r is already oob at this handoff, so the handover fires 6.1 min in at ~17:45:20 and lineage never climbs |

## THE CYCLE — JOE'S MECH

Joe 1013: *"when the baton-pass collects r values, it must allow for the r lines 'cycle' - ie, is it
heading towards target dr, or has it just left target-dr"*.

**THE TAG.** A TF under the loop TF that crosses oob → ib on the target end is tagged
`left-target-dr` from that bar on. Joe: *"it would be less cost to tag {TFs < loop-tp} lines with
'left-target-dr' as they cross to ib, and then clear all tags when lineage finishes its walk. your
code, your call"*. Built as a dict local to `run_leg`, so it clears itself on return — no reset code
and no state that can leak into the next leg.

THE TAG IS MAINTAINED AT THE TOP OF THE BAR LOOP, before any `continue`. Placed lower it is skipped
on every bar that `continue`s, and a baton pass is one of those: ws6 crossed oob → ib at
2026-07-18 18:12:00, the same bar the baton passed, so the cross was missed and ws6 read as tagged
at 18:13:15 instead. Same class of bug as the `held` holder list, fixed 1012 for the same reason.

**towards-dr.** Joe: *"I'd calculate 'towards dr' based on states: has momentum / has not been
tagged as 'crossed to ib'"*. Nothing about the line's position is read — a line can be in-fence and
still be heading to the target end, which is what qualified ws7 at 18:05:35 sitting at 79.93.

**WHY THE EXHAUSTION SUBSTITUTION WORKS**, measured on 07-18 16:07, board HIGH:

| bar | rider | reach | the EXISTING test — all inside the ex-fence 17/83 | the CYCLE test — none is towards-dr |
|---|---|---|---|---|
| 2026-07-18 17:39:20 | ws1 | ws2 73.41, ws3 59.44 | **FIRES** — the walk is over 5 s in | no — both untagged and mom-true, climbing to 95.64 and 100.00 within 9 min |
| 2026-07-18 18:12:00 | ws4 | ws5 71.72, ws6 84.38 | no — ws6 is above the ex-fence 83 | **FIRES** — ws5 tagged 18:05:35, ws6 tagged 18:12:00 |

One change, both bars corrected.

## RADIUS BLAST AND MATRYOSHKA — JOE'S READING, MEASURED

Joe 1013: *"ws7 is affected by radius blast and matryohska, a true fact for all TFs and all lines.
when ws5 and ws6 are 'left-target-dr', they have begun the reversal for ws7. this is why we create
the EXHAUSTION event in the way that we do: lower lines that are 'left-target-dr' lead/pull the
exhaustion line around where-ever it is on the board"*.

07-18 16:07 LONG, board HIGH, the walk from 2026-07-18 17:39:10:

| line | its oob extreme | extreme bar | `left-target-dr` tag bar |
|---|---|---|---|
| ws1 | 99.83 | 2026-07-18 17:41:00 | 2026-07-18 17:43:00 |
| ws2 | 95.64 | 2026-07-18 17:45:40 | 2026-07-18 17:50:30 |
| ws3 | 100.00 | 2026-07-18 17:48:15 | 2026-07-18 18:04:20 |
| ws4 | 100.00 | 2026-07-18 17:56:35 | 2026-07-18 18:12:00 |
| ws5 | 89.49 | 2026-07-18 18:04:55 | 2026-07-18 18:05:35 |
| ws6 | 97.11 | 2026-07-18 18:06:10 | 2026-07-18 18:12:00 |
| ws7 | **85.43** | 2026-07-18 18:12:50 | 2026-07-18 18:13:00 |
| ws8 | never reached oob, best 77.99 | 2026-07-18 18:08:05 | never tagged |
| ws9 | 86.39 | 2026-07-18 18:09:00 | 2026-07-18 18:09:15 |
| ws10 | 88.96 | 2026-07-18 18:10:20 | 2026-07-18 18:11:10 |

- the tags close in on ws7: ws1 +29.8 min out, ws2 +22.3, ws3 +8.5, ws5 +7.2, then ws4 and ws6
  together at **+0.8 min**. ws7 turns 50 s after the last two.
- ws7 clears oob by **0.43 points for 2 bars** and crosses straight back. What it had left to spend
  was what the lines under it had not already spent.
- NOT MONOTONE ACROSS THE WHOLE LADDER, stated: ws9 and ws10 tagged before ws7 did, and ws8 never
  reached oob at all. The cascade is monotone for ws1 through ws7 only.

## THE BLAST-RADIUS GATE ON THE JUMPSTART — 1013

Joe 1013: *"the last mile mech need an update. it shouldn't have fired, for blast-radius reasons: at
18:44:15 ws1 and ws2 are tagged ib, and ws4 is oob and heading away from target-dr / blast-radius
says that the TFs above ws1,2,4 will follow the lower lines / this means the jumpstart should not
fire - the blast-radius + ws1-cp crossing to ib tells the mech that there is no momentum left"* /
*"it's r"* / *"a 12-bar walk forward would likely settle the verdict with more votes"* / *"we bank
the {knob:12,'LINFIN_WALK_DELAy'}-bar gate"*.

**IT IS A DELAY, NOT A PEEK.** His own word. The verdict needs the 12 bars to form, so the walk is
HELD for them and the verdict lands at handoff + 12. Deciding at the handoff bar on bars that come
after it would be lookahead.

A line votes `AWAY` at a bar when it is oob on the target end AND further from that end than it was
at the handoff. The gate fires when `LINFIN_WALK_AWAY_MIN` lines have voted at least once. Lines are
the TFs under the loop TF, matching the tag rule.

### why `AWAY` alone — the full vote count is useless

| handoff | the last mile did | votes of 108 | LEFT | AWAY | lines voting AWAY |
|---|---|---|---|---|---|
| 07-18 18:12 SHORT | -0.1849% | 29 | 12 | **17** | **3 of 9** |
| 07-17 21:58 LONG | +0.0304% | 28 | 27 | 1 | 1 of 9 |
| 07-18 08:46 LONG | +0.0084% | 38 | 37 | 1 | 1 of 9 |
| 07-18 16:07 LONG | +0.9238% | 97 | 96 | 1 | 1 of 9 |
| 07-18 02:31 SHORT | -0.0277% | 67 | 67 | **0** | **0 of 9** |

- `LEFT` — been oob, now in-fence — is the **winner's** signature: 96 of 16:07's 97 votes. It is not
  a stand-down signal, and the combined count reads highest on the biggest winner.
- `AWAY` separates 3 lines from 1, cleanly.
- JOE'S ws2r CALL WAS RIGHT: at the handoff bar ws2r 10.61 is oob and moving toward the target, a
  blip. Walked 12 bars it votes AWAY on 7 of them.
- IT CATCHES 1 OF THE 2 LOSERS. 07-18 02:31 lost 0.0277% with 0 AWAY votes, and nothing in this
  measurement explains that one. Stated.

### what the gate is worth

| | the 07-18 18:12 SHORT |
|---|---|
| no gate — the last mile runs to exhaustion at 2026-07-18 18:58:55 | +0.2592% |
| with the gate — the held close goes at 2026-07-18 18:45:15 | **+0.3769%** |
| the gross at the handoff bar 18:44:15, for reference only | +0.4441% |

- the 12-bar delay costs 0.0672% against the handoff bar. That bar is NOT available as an exit — the
  verdict does not exist there.
- the four banked trades sit at 1, 0, 1, 1 AWAY lines, so the gate fires on none of them and
  **+8.0377% does not move**. Verified by a full run.

## ALL FOUR TRADES

| trade | momentum test held the close? | last mile starts | ends at | +min | why | riders walked | gross at the start | gross at the end | moved |
|---|---|---|---|---|---|---|---|---|---|
| 07-17 21:58 LONG | no | 2026-07-18 01:15:20 | 2026-07-18 01:16:20 | 1.0 | exhaustion | ws2 | +1.0517% | +1.0821% | +0.0304% |
| 07-18 02:31 SHORT | YES | 2026-07-18 11:11:15 | 2026-07-18 11:13:35 | 2.3 | exhaustion | ws5 | +4.8615% | +4.8337% | -0.0277% |
| 07-18 08:46 LONG | no | 2026-07-18 10:07:10 | 2026-07-18 10:07:20 | 0.2 | exhaustion | ws5 | +0.3929% | +0.4014% | +0.0084% |
| 07-18 16:07 LONG | YES | 2026-07-18 17:39:10 | 2026-07-18 18:12:00 | 32.8 | exhaustion | ws1 → ws2 → ws3 → ws4 | +0.7967% | +1.7205% | +0.9238% |
| **TOTAL** | — | — | — | — | — | — | **+7.1028%** | **+8.0377%** | **+0.9349%** |

- all four end on `exhaustion`. No MAE stop, no tape end, no fallthrough.
- 16:07 carries +0.9238% of the +0.9349% — 98.8% of the gain is one trade.
- Joe expected the closes the momentum test held to benefit most. It holds for one of the two:
  16:07 +0.9238%, 02:31 **-0.0277%**, and 02:31 is the only trade that loses.
- both unheld closes improved, +0.0304% and +0.0084%.
- the hold adds no leg boundary, so drag is unchanged by every row above. These are gross figures.

### 07-18 16:07 LONG, the trace

| ts | event |
|---|---|
| 2026-07-18 17:39:10 | LAST MILE — armed at the handoff, no ws1-cp and no ws2Mage arm |
| 2026-07-18 17:39:15 | JUMPSTART — rider ws1, highest oob line at or under ws5, r 95.74 |
| 2026-07-18 17:39:20 | lineage ruled ws1 STALLED; crossing_to_ib IGNORES it |
| 2026-07-18 17:43:00 | baton → ws2, r 90.80; ws1 crossed back inside the fence at 71.43 |
| 2026-07-18 17:45:30 | lineage ruled ws2 STALLED; crossing_to_ib IGNORES it |
| 2026-07-18 17:50:30 | baton → ws3, r 100.00; ws2 crossed back inside the fence at 79.79 |
| 2026-07-18 17:53:45 | lineage ruled ws3 STALLED; crossing_to_ib IGNORES it |
| 2026-07-18 18:04:20 | baton → ws4, r 91.57; ws3 crossed back inside the fence at 81.29 |
| 2026-07-18 18:04:40 | lineage ruled ws4 STALLED; crossing_to_ib IGNORES it |
| 2026-07-18 18:12:00 | EXHAUSTED on ws4 — none of the 2 above is towards-dr (ws5 71.72 tagged 18:05:35, ws6 84.38 tagged 18:12:00) |

### why the three short walks end in 1 to 2.3 minutes

| trade | kickstart takes | the 2 above it at the exhaustion bar |
|---|---|---|
| 07-17 21:58 LONG | ws2, r 85.38 | ws3 61.01 no momentum, ws4 52.66 no momentum |
| 07-18 02:31 SHORT | ws5, r 5.12 | ws6 18.69 tagged 11:12:25, ws7 15.77 tagged 11:13:35 |
| 07-18 08:46 LONG | ws5, r 86.23 | ws6 92.23 no momentum, ws7 98.63 no momentum |

- 21:58 and 08:46 fail on momentum, untagged — those lines never got a cycle.
- 02:31's cascade had already run: ws6 and ws7 crossed to ib inside the first 2.3 min.
- **08:46 IS A POI.** ws6 92.23 and ws7 98.63 are both oob on the target end and still read "no
  momentum", so the walk stops with two lines sitting past the fence above the rider.

## WHAT IS MINE, NOT RULED BY JOE

| # | mine | status |
|---|---|---|
| 7 above | `final stalled` suppressed in last-mile mode | an extension of his stall-gate ruling to a second stall gate. Noted by him 1013 |
| `W_LOOP_END` default `cp` | the loop waits for a ws1-cp instead of recycling on the oob bar | his 1011 words were *"an observation, not a mech"*. His described mech is the `oob` value. Does not bite on any of the four walks — none reaches ws10. Noted by him 1013 |
| the receiver is rider+1, not the highest of the reach | `max(cand)` over the reach breaks his confirmed 17:50:30 ws2 pass (ws1 jumps to ws3) and skips ws7 at 18:12:00 | his conditional was *"unless it breaks the 18:12 verdict"*; it does |

## DELETED

My own "the walk ends when no line in the rider's reach is eligible" was exhaustion wearing a
different test. Joe 1013: *"the end is the EXHAUSTION event. I'm sure that this is the existing mech
- pushback if I'm wrong"*. He was right. There is no separate end condition.
