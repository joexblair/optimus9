# fdm2-3r-cadence — the spec, as he ruled it

HIS NAME, 1107: *"the mech has no name. Yours to give --fdm2-3r-cadence"*.
Prefix `c3r_`. Where it sits, 1107: *"it fires on each bar, while the walk is walking"*.

Every line below is quoted from him or marked MINE.

## the read

| what | the read | his words |
|---|---|---|
| ws3r | **emerging** | 1107: *"it's closed-prev causing the problem. if we make ws3r emerging for this c3r mech, does it satisfy all of examples?"* — it did, 6 of 7 markers, and he dropped the seventh |
| every other line | closed-prev | the standing default |

## the five clauses, his indentation

His pasted spec, 1107, verbatim:

```
1) IF a ws3r line's trajectory is matching ws1r's trajectory until ws1r crosses to ib
2) -IF the ws3r line continues its trajectory and reaches oob without returning past counter-side 50
3) --IF ws3Mage or ws3b is past counter-side 50
4) ---IF ws3r crosses to in-20/80-fence
5) ----IF ws1b has not been same-side oob between 'ws1r reversal' and 'ws3r crossing to in-20/80-fence'
6) -----rev-trade ELSE stop
```

## his rulings on each clause

| the clause | what he ruled |
|---|---|
| 1, what "trajectory matching" means | *"both lines read towards the same side"* |
| 1, where the match must start | *"ws1r's oob entry. note that ws1r will not be oob shortly after and ws3r will not.. this makes the 'ws1r's oob entry.' test a one-time-only test"* |
| 2, what it is for | *"clause 2 was designed to reject an unstable ws3r, a line that bends back and forth before it reaches the target side. an example of this is seen between 08-24 0836 and 0915"* |
| 2, where the window opens | *"ws3r's first print on the target side of 50 after ws1r's target-side oob entry"* |
| 2, how many returns make it unstable | *"one return is enough to trigger unstable"* |
| 3, at which bar | *"the full TF bar before the cross to infence"* |
| 4, the second branch | *"4) ---IF ws3r crosses to in-20/80-fence OR (ws1Mage is same-side oob and reversing while ws3r is oob, and ws4r is infence)"* / *"ws1Mge reversal is lift-off driven"* |
| 4, branch B vs the cross | *"my reading for both is 'the branch-B bar replaces the cross'"* |
| 5, which event | *"same event: ws1r to ib"* |
| 6, what "ELSE stop" means | *"I wrote this only so the mech would have closure. I'm saying the outcomes are either rev-trade, or kill (stop) the 3r-cadence mech"* |

## HIS 1108 ADDITION — the rev-trade waits for ws1Mage

His words: *"one addition to c3r's rev-trade sepc line: walk to ws1MAge same-side reversal
(where ever it is on the board) before placing the rev-trade"*.

So clause 6 is no longer the placement bar. Clause 6 arms a walk; the walk places the rev-trade.

| what | the ruling | source |
|---|---|---|
| what the walk waits for | the first ws1Mage **same-side** reversal | his words |
| any level requirement on it | NONE — *"where ever it is on the board"*. "board" is the full range, never a region | his words, and his 1016 ruling on the word board |
| which producer reads it | `jig.lift_off(ws1Mage emerging, side, LIFT_PTS, gap_for(1), LIFT_TOL, LIFT_WOB)` | his 1108 pick between two candidates. It takes the side as an input, so same-side is direct, and c3r branch B already reads this exact stamp |
| what ends the wait with no rev-trade | **a race: the MAE 1.1 stop, or the next cadence event — first of** | his 1108 words: *"race mae stop and next cadence event (first of)"* |

### decided and stated, not his

| the concretion | MY choice | why |
|---|---|---|
| which bar the walk starts from | the clause-4 bar — branch A's cross bar or branch B's bar, whichever fired | it is the bar clause 6 reaches today |
| which bar the rev-trade is placed on | the lift-off **stamp**, `K.lift_stamp(b)` = b + LIFT_WOB - 1 = b + 35 s at LIFT_WOB 8 | his standing rule: a lift-off is not knowable until its hold completes, and every consumer adds the wob in one place |
| the ws1Mage read for the lift-off | emerging | his standing rule: lift-off reads emerging, every other line read is chart-matched. Branch B already reads `LN['MGE'][1]` |
| the cadence-event producer for the race | `v4_fdm2.cadence_events(LN, side, A, B)` | it is the one that enumerates them |

### OPEN — needs his ruling before the race is wired

| the gap | the question |
|---|---|
| a tie | the lift-off stamp and a cadence event land on the SAME bar. Which wins? His banked tie convention is *"A TIE GOES TO THE STOP"*, but that was the price stop against a signal, not two signals |
| the cadence event's side | does ANY cadence event end the wait, or only one on the same side as the c3r arm? |
