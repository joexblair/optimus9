# THE HTF HOLD — this lap's record. 1013. NOT COMMITTED, NOT LIVE.

Joe keeps the ledger; this is the code side of it so the two can be reconciled.

## HIS SPEC, VERBATIM

> "if the gate is still in place at the exhaustion, can we hold the 11:04 close event and keep
> walking until ws{>={knob:5}}r shows momentum, then let the last-mile handle the close / if the
> gate ends because of the x-cross, and if no momentum has been found, then the walk ends and we
> print the held close"

> "correction: first (ws>=5 and ws<=loop-tf+linhop) mom-true toward its own board"

> "gap1: A - standard last-mile lineage walk"

> "gap2 is lookahead. if the restriction is 'still in place at the end', the only choice is to walk
> forward"

> "the lin-hop TFs can't be used to delay an end signal, if they are greater than loop-tf. when
> ws{loop-tf}r crosses to oob, it defers to ws1 (the 'loop')"

## THE LEDGER

| # | update | knob | live value | state |
|---|---|---|---|---|
| 1 | hold_walk uses towards_dr | — | `_htfgate.hold_walk` | built |
| 2 | lineage last-mile loops to ws1 on ws{loop-tf}r oob | `W_LOOP_END` | oob | default moved 1013, was 'cp' (mine) |
| 3 | lin-hop TFs can't delay an end signal above loop-tf | `HOLD_TFS` | ws5-ws10 | built |

## THE KNOBS THIS LAP ADDED. NONE IS RULED.

| knob | default | whose |
|---|---|---|
| `W_HTF_HOLD_TF` | 5 | Joe's `{knob:5}` |
| `W_HTF_HOLD_MAX` | 0 = no limit | the literal reading of his spec; he set no limit |
| `W_HTF_REN_WOB` | 0 = no hold | the literal reading; he gave the release 48 and the re-enable none |

## THE NUMBERS

| what | figure |
|---|---|
| the chain, 9 legs, 2026-07-17 21:58:00 -> 2026-07-19 12:36:40 | +11.4743% |
| the same chain without the hold | +11.4656% |
| moved | +0.0088% |
| the 6 declared legs, frozen and matching | +10.4467% |
| the gated walk with the hold | +1.0276% |
| legs the hold applies to | 1 of 9, the 2026-07-19 09:54:25 SHORT |
| times it fired on that leg | 34 — 33 momentum handoffs, 1 release |

| W_HTF_HOLD_MAX | times it fired | that leg ends | the chain |
|---|---|---|---|
| 1 | 1 | 2026-07-19 11:08:15 | +11.4045% |
| 2 | 2 | 2026-07-19 11:11:55 | +11.4079% |
| 3 | 3 | 2026-07-19 11:14:05 | +11.5727% |
| 6 | 6 | 2026-07-19 11:20:35 | +11.3751% |
| 12 | 12 | 2026-07-19 11:33:30 | +11.5395% |
| 0 = no limit | 34 | 2026-07-19 12:36:40 | +11.4743% |

No knee. The chain spans +11.3751% to +11.5727% with no direction, and the no-hold +11.4656% sits
inside that range. There is nothing here to anchor the limit to.

## THE HTF GATE'S OWN SWEEP, 252 COMBOS

| rank | gross | combos | leg set |
|---|---|---|---|
| 1 | +1.0189% | 58 | 04:11:55 LONG, 05:53:30 SHORT, 09:54:25 SHORT |
| 2 | +0.8372% | 68 | 02:38:10 SHORT, 09:16:15 LONG |
| 3 | +0.5568% | 7 | 01:24:50 SHORT, 09:16:15 LONG |
| 4 | +0.1220% | 119 | 04:11:55 LONG, 05:53:30 SHORT, 09:16:15 LONG |

The ruled triple ws60 / release 48 / re-enable 0 is already on the maximum. Joe 1013: *"ok, no
change needed"*.

## TWO DEFECTS FOUND AND FIXED THIS LAP

| # | the defect | the fix |
|---|---|---|
| 1 | the hold's momentum test read bare mom-true, so a line already crossed to IB still counted | `towards_dr` |
| 2 | the `left-target-dr` tag scanned only the bars between a handoff and the next momentum bar, so it stayed EMPTY for the whole walk | the tag advances over every bar from the exhaustion forward |

The tag bars that now register on the 09:54:25 SHORT: ws6 11:33:25, ws5 11:50:20, ws10 12:00:10,
ws8 12:03:20, ws7 12:15:25, ws9 12:27:05. Every one is before the release at 12:36:40, which is
Joe's own read: *"my view sees all of the higher wsf lines crossing to IB considerably earlier than
12:36, which should have signalled the end"*.

## WHAT APPLYING THE GATE TO THE DECLARED OPENS WOULD COST

| leg | the preceding close | HTF oob there | permitted? |
|---|---|---|---|
| 07-18 08:46 LONG | 2026-07-18 08:44:30 | ws30r 0.10 LOW oob | NO, BLOCKED, -0.3934% |

Three of the six have no preceding close to test, because they open before the leg ahead of them
ends. NOT APPLIED — blocking a declared leg rewrites the frozen reference, which is Joe's call.

## THE OPEN QUESTION

The hold's momentum handoff calls `C.run_leg(bar, dr)`, which re-arms the last mile from scratch:
the JUMPSTART picks a fresh rider, capped at ws7 by `LASTMILE_KICK_TFCAP`. On the 11:56:05 handoff
that rider was ws7 with ws7r 2.44, and it never moved, so `W_LOOP`'s trigger `rider >= ws10` was
never met and the walk exhausted on ws7 at 12:22:45. ws10r WAS low oob at 11:56 and crossed to IB
at 12:00:10, so the loop's own line condition held while the rider never reached it.

Joe: *"this is the key piece of data, and the reason why 11:56 should be printing EXHAUSTION"*.

UNANSWERED: does the hold's handoff re-arm the last mile, or continue the walk the leg already
held? Both are measurable; neither is built on a guess.

## THE FILES

`_htfgate.py` hold_walk, re_enable, active_at, permits_live, instance wob/ren_wob/x_tf.
`machine.py` imports `_htfgate`, builds the gate in `build()` which now returns a 4-tuple,
`chain(..., hold=None)`, HOLD_TFS, HOLD_MAX.
`_chain10.py` W_LOOP_END default cp -> oob.
`_ruled.py` W_LOOP_END ruled 'oob'.

`python3 machine.py` still matches all 14 frozen figures.

## THE JUMPSTART-DISABLED FLAG. Joe 1013, built and unexercised.

> "new mech to live inside of lineage last-mile: if the loop cycles from loop-tf to ws1, the
> jumpstart is disabled for the remainder of the walk"

> "the jumpstart-disabled flag can only be enabled on 'ws{loop-tf}r going oob and redirecting the
> walk to ws1'"

| where | what |
|---|---|
| `_chain10.run_leg` | `jump_off=False`, `state=None`, both keyword with defaults — no existing call site changes |
| `_chain10.py:1675` | the W_LOOP reset under `LOOP_END='oob'`, the ONLY place the flag is set |
| the jumpstart block | skipped while the flag is set; the ws1-cp arm and `W_KICK='off'` untouched |
| `machine.chain` | carries the flag into every later `run_leg` for the same leg |
| clearing | none. Joe named no clear |

The flag crosses the call boundary in a dict, not a 7th return value, because 13 return points sit
inside `run_leg` and ~100 scripts unpack its 6-tuple. MY CHOICE, stated.

| what | figure |
|---|---|
| the chain | +11.4743%, unchanged |
| the frozen reference | all 14 figures match |
| W_LOOP firings across the chain's 42 last-mile walks | 0 |
| `JUMPSTART DISABLED` rows emitted | 0 |

NOT TESTED. The condition has never occurred in the data: no walk's rider reaches ws10. The instance
that would exercise it is a walk that reaches ws10 with ws10r oob, and there are 0 in 42.

## THE LOOP TRIGGER, REBUILT ON HIS WORDS. 1013.

Audit finding: the loop had fired 0 times in 42 walks because of two clauses I wrote and his words
do not contain.

| clause | his words covering it | whose |
|---|---|---|
| `rider >= t` — the walk's current line had to be ws10 or higher | none, in any of his four descriptions | MINE, self-labelled "MY READING" in my own comment |
| `rider is not None` — the loop could not fire before the walk had a line | none | MINE, unflagged |
| `oobf(t, j, d)` — the oob STATE at the bar | *"I think this is ok. the event becomes the state until a counter-event removes the state"* | HIS, confirmed 1013 |
| `rider = ALL_TF[0]` | *"loop back to ws1"* | his |
| no cap on re-looping | he set none | his |
| the loop checked before exhaustion on the same bar | *"this is good"* | his, confirmed 1013 |

His rulings that replaced them:

> "we take the first signal - I haven't specified any delays on ws{loop-tf}r crossing to oob"

> "delete this. ws{loop-tf}r oob is the only qualification needed to send the walk to ws1"

> on the handoff carrying on with the line the walk was already following: "this is the correct
> behaviour"

| what the code does now |
|---|
| the loop fires on the FIRST bar of a ws{loop TF}r oob state, and re-arms when that line leaves oob |
| no rider qualification of any kind - a walk with no line yet is ARMED by the loop, rider ws1 |
| the hold's handoff continues with the line the walk was already following, via `rider0` |
| the jumpstart-disabled flag still set only at the loop's reset, and carried across the handoffs |

| what | before | after |
|---|---|---|
| last-mile walks traced | 42 | 141 |
| W_LOOP firings | 0 | 13 |
| walks whose loop fired | 0 | 3 — the 08:46 LONG, the 16:07 LONG, the 04:11:55 LONG |
| the hold's handoffs on the 09:54:25 SHORT | 33 | 107 |

| leg | before | after | moved |
|---|---|---|---|
| 07-18 08:46 LONG | 2026-07-18 10:20:05, +0.3934% | 2026-07-18 10:09:10, +0.3920% | -0.0014% |
| 07-18 16:07 LONG | 2026-07-18 18:12:00, +1.7205% | 2026-07-18 18:10:05, +1.9325% | +0.2120% |
| 2026-07-19 04:11:55 LONG | 2026-07-19 05:22:55, +0.3741% | 2026-07-19 05:12:30, +0.5051% | +0.1310% |
| the chain, 9 legs | +11.4743% | +11.8160% | +0.3417% |

TWO THINGS FOR JOE, NEITHER TOUCHED:

1. THE FROZEN REFERENCE IS REFUSED - 3 mismatches: 07-18 08:46 LONG end +0.3920% vs +0.3934%,
   07-18 16:07 LONG end +1.9325% vs +1.7205%, TOTAL +10.6574% vs +10.4467%. The re-freeze is his.
2. THE 18:12 JOIN. Leg 4 now ends 2026-07-18 18:10:05 and leg 5 opens 18:12:00, a 1.9 min gap where
   he had an unbroken join: *"the goal is to build a chain that is unbroken, so 18:12 is the exit
   and the open"*. The loop moved that exit.

---

# THE LAP CLOSED. 1013 -> 1014. Joe: "bank, commit and push. update docs. make this machine live".

## WHAT IS LIVE

| mech | state |
|---|---|
| the loop fires on ws{loop-tf}r's own oob state, no condition on the walk's current line | live |
| the reset to ws1 is one-time per leg | live |
| the jumpstart is off for the rest of the walk after that reset | live |
| the oob state carries across a walk boundary, so the edge is not re-detected | live |
| the per-line "been out and back" memory is cleared at every reset | live |
| the trade closes when the walk lands on a weak ws1 with no baton | live |
| the chain restart, `restart-chain-on-loop-tf-oob` | live, `_restart.py` |
| loop-tf | 10 |
| the MAE stop | 1.1, the DB's 2.5 untouched |

## WHAT WAS REMOVED THIS LAP

| mech | why |
|---|---|
| the oob hack's keep-going layer | Joe: *"the oob hack state changes do not have any bearing on an open trade"* and *"11:04 closes the leg"*. It overrode the first exhaustion 82 times on one leg |
| the oob-hack close extension | measured at -3.3618% on the chain and dropped |

## THE CHAIN, 14 LEGS, 2026-07-17 21:58:00 TO 2026-07-20 01:02:15

| # | opens | side | how it opened | the chain ends | why it ends | gap reason | gross |
|---|---|---|---|---|---|---|---|
| 1 | 2026-07-17 21:58:00 | LONG | declared | 2026-07-18 03:45:40 | exhaustion | first leg | +1.3945% |
| 2 | 2026-07-18 02:31:00 | SHORT | declared | 2026-07-18 08:44:30 | blast radius | opens before end | +4.9508% |
| 3 | 2026-07-18 08:46:55 | LONG | declared | 2026-07-18 10:07:20 | loop close, ws1 weak | hack blocked LONG | +0.4014% |
| 4 | 2026-07-18 16:11:10 | LONG | declared | 2026-07-18 18:10:05 | loop close, ws1 weak | walk skipped bar | +1.9325% |
| 5 | 2026-07-18 18:12:00 | SHORT | declared | 2026-07-18 18:45:35 | blast radius | hack blocked SHORT | +0.4083% |
| 6 | 2026-07-18 18:45:15 | LONG | declared | 2026-07-18 21:17:55 | exhaustion | opens before end | +1.5793% |
| 7 | 2026-07-18 23:23:50 | SHORT | restart | 2026-07-19 07:59:55 | exhaustion | hack blocked SHORT | +0.6580% |
| 8 | 2026-07-19 09:54:25 | SHORT | ws1cp-ib | 2026-07-19 11:04:50 | exhaustion | hack blocked LONG | +0.1058% |
| 9 | 2026-07-19 12:00:10 | LONG | restart | 2026-07-19 13:46:05 | exhaustion | hack blocked LONG | +0.5652% |
| 10 | 2026-07-19 14:05:50 | SHORT | ws1cp-ib | 2026-07-19 14:55:05 | max jumpstart gap | walk skipped bar | +0.2683% |
| 11 | 2026-07-19 16:17:35 | LONG | restart | 2026-07-19 19:29:20 | exhaustion | walk skipped bar | -0.2531% |
| 12 | 2026-07-19 20:05:25 | SHORT | ws1cp-ib | 2026-07-19 21:19:00 | blast radius | walk skipped bar | -0.3953% |
| 13 | 2026-07-19 21:59:10 | LONG | ws1cp-ib | 2026-07-19 23:01:35 | exhaustion | walk skipped bar | +0.8165% |
| 14 | 2026-07-20 00:15:25 | SHORT | ws1cp-ib | 2026-07-20 01:02:15 | blast radius | walk skipped bar | +1.2167% |
| **TOTAL** | — | — | — | 2026-07-20 01:02:15 | — | — | **+13.6487%** |

| how the legs opened | count | gross |
|---|---|---|
| declared, Joe's own open mech | 6 | +10.6668% |
| the chain restart | 3 | +0.9701% |
| the next permitted cross-back | 5 | +2.0118% |

## THE GAP COLUMN - WHY THE CHAIN IS NOT CONTINUOUS

| value | legs | what it means |
|---|---|---|
| hack blocked SHORT / LONG | 4 | the hack would not let the flipped side open on the previous end bar |
| walk skipped bar | 6 | the hack allowed it; the cross-back walk never looks at the end bar |
| opens before end | 2 | a declared open that starts before the leg ahead of it finishes |
| no gap | 0 | the chain has never once opened on the bar the previous leg ended |

OPEN, HIS TO RULE: whether the walk should test the end bar itself as an open. Six of the fourteen
gaps exist only because it does not.

## THE FROZEN REFERENCE, RE-FROZEN

| leg | end gross before | after |
|---|---|---|
| 07-18 08:46 LONG | +0.3934% | +0.4014% |
| 07-18 16:07 LONG | +1.7205% | +1.9325% |
| the six declared | +10.4467% | +10.6667% |

`python3 machine.py` matches all 14 figures.

ALSO FLAGGED: leg 4 now ends 2026-07-18 18:10:05 and leg 5 opens 18:12:00, so the 18:12 join Joe
built on 1013 - *"18:12 is the exit and the open"* - is 1.9 min broken by the loop's new close.

## THE KNOB INVENTORY

| what | count |
|---|---|
| ruled, his value with his words | 31 |
| recorded as unruled, with whose number each is | 14 |

## THE DIFF REVIEW, 1014. Five dead items stripped, all left by the hold removal.

Joe asked for a review of the committed chain diff. Every one of these is mine.

| # | the defect | the fix |
|---|---|---|
| 1 | `run_leg`'s docstring opened with "JOE 1013'S JUMPSTART-DISABLED FLAG" - one small flag had taken over the function's own description | the docstring describes the leg walk, and records what was removed |
| 2 | `rider0`, `looped_once`, `loop_oob0`, `jump_off`, `state` had no caller | removed; they carried state across the keep-going layer's pieces |
| 3 | `W_LOOP_STATE_CARRY` could not change anything - it guarded `loop_oob0` | removed from the code AND from the ruled set, where it sat as Joe's ruling with his words |
| 4 | the "JUMPSTART DISABLED" trace row was unreachable | the branch stays because the flag is his mech; the reason it cannot print is now written next to it rather than left silent |
| 5 | `_DB_MAE` assigned and never read | removed |

| check after the strip | result |
|---|---|
| `python3 machine.py` | all 14 frozen figures match |
| the chain, 14 legs | +13.6487%, unchanged |
| ruled knobs | 30 |
| unruled knobs recorded | 14 |

Defect 3 is the one that mattered: a knob banked as Joe's ruling that could not affect the machine.
It is the same shape as `W_LOOP_END` sitting at my own 'cp' default for two days while his words
said 'oob'.

## JOE'S 16:46 READ ON THE 2026-07-19 16:17:35 LONG - VALIDATED

His view: it should end ~16:46, and does not because ws1Mage oob and ws1r oob are out of sync by
about 5.5 minutes. A cross-back needs ws1r >= 85 AND ws1Mage >= 85 held 2 bars.

| line | its high-oob runs, 16:17 to 17:10 |
|---|---|
| ws1r | 16:17:05-16:18:55, 16:39:05-16:39:15, 16:40:05-16:40:10, 16:40:20-16:40:55, 16:41:05, 17:07:00-17:09:55 |
| ws1Mage | 16:45:15-16:46:10, 16:46:20-16:47:40, 16:48:00-16:50:10, 16:50:40-16:50:55, 16:51:20 |

| what | figure |
|---|---|
| bars where both are high oob, 16:17 to 17:10 | none |
| ws1r's last high bar before ws1Mage turns | 2026-07-19 16:41:05 at 87.36 |
| ws1Mage's first high bar | 2026-07-19 16:45:15 at 147.85 |
| the gap | 4 min 10 s, inside his 5.5 min |
| so the leg ran to | 2026-07-19 19:29:20, exhaustion, -0.2531% |

HIS READ IS CORRECT. No mech is built for it - a sync tolerance between the two lines does not
exist and he has not asked for one.
