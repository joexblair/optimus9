# octo-v4 — `v4-lineage`

Started 2026-10-22. Joe 1022: *"v3 is dead... we're now starting `octov4`"* / *"don't carry anything forward from v3"*.

SPLIT FROM `v4_spec.md` ON 1022, at Joe's word: *"good analysis.  action the split"*. One doc
per thing that can change independently - the bank, and one per mech. His verbatim text is
CARRIED, never retyped: the 1022 handover arrived as ONE message covering the knob, `rev-trade`
and `v4-lineage`, and its pieces are split by mech here with nothing reworded. The Jig's
producers get no doc - `lift_off`, `at_extreme` and `mage_cascade` document themselves in the
Jig header, where the code is, and a second copy would rot.

Joe's times carry no colons: `1305` is 13:05, `2051` is 20:51. His time estimates are +/- 5
minutes - take the mechanic, never fit a knob to the timestamp.

---

## 1. The handover, verbatim

Joe 1022, unedited, from `there are new mechs to learn` on. The knob, `rev-trade` and
no-colons lines opened the same message and are carried verbatim in `v4_bank.md`; nothing is
reworded in either place.

```
there are new mechs to learn. here's the first:
`v4-lineage` mech  (based on `lineage`. it adds post-ws5r logic)
time estimates are +/-5 minutes
-choose the rider from a limited "ws1r to ws5r" pool, by testing them for trajectory
--rider candidates must have trajectory tagged `toward` the target-side
-baton-pass on riderTF reversing while riderTF+1 is oob
-if ws5r is oob and reversing
--if v4-lineage prints `EXHAUST`, create a rev-trade at the ws5r reversal
--else if no exhaust, walk ws5r to ib and test if ws{TF+lin-hop}r's are oob 
---if the lin-hop TFs are not oob, create a rev-trade (example 09-02 1305)
---else walk v4lineage until it prints exhaust, baton-passing on riderTF reversal
----riderTF can only advance one TF at a time. riderTF + linhop is a forward looking view only. the TF lineage must evolve in single steps, when rider-tf is reversing 
----for riderTF+1 to accept a baton-pass, riderTF+1 must be exfence at the time of riderTF reversing
----if the receiver of the baton is between ex-fence and oob when the baton is taken
-----if the receiver reverses while still positioned between ex-fence and oob
------EXHAUST is declared IF a linhop TF is not oob
----if riderTF cannot see an ex-fence rline inside the linhop TFs at the time of riderTF reversing
-----declare EXHAUST
------examples 09-01 2051 on ws9rev. 09-02 0200 on ws6r
---at exhaust, create a rev-trade 
```

Joe 1022, the last lines of the mech, unedited:

```
-else if ws5r is reversing and not OOB
--create a rev-trade
```

Joe, same message: *"linhop is view only. if ws9 or ws10 are somehow reached, the linhop TFs will
tell the mech if ws9 or ws10 will exhaust."* / *"for your context, the 09-01 2051 was reversed by
ws5r while ws5r was infence."* / *"I overlooked the ELSE IF that completes this: \"-if ws5r is oob
and reversing\""*.

---

---

## 2. `v4-lineage`, read as logic

Read by the indentation rule: a deeper level nests INSIDE the one above, so `--` under `-` is AND.

| the level | Joe's line | what it says |
|---|---|---|
| `-` | choose the rider from a limited "ws1r to ws5r" pool, by testing them for trajectory | the rider pool is ws1r..ws5r, selected on trajectory |
| `--` | rider candidates must have trajectory tagged `toward` the target-side | AND the candidate's tag is `toward` |
| `-` | baton-pass on riderTF reversing while riderTF+1 is oob | the pass condition at the top level: riderTF reverses AND riderTF+1 is oob |
| `-` | if ws5r is oob and reversing | the post-ws5r branch opens here |
| `--` | if v4-lineage prints `EXHAUST`, create a rev-trade at the ws5r reversal | rev-trade anchored on the ws5r reversal bar |
| `--` | else if no exhaust, walk ws5r to ib and test if ws{TF+lin-hop}r's are oob | walk forward to the ib cross, then read the lin-hop TFs |
| `---` | if the lin-hop TFs are not oob, create a rev-trade | Joe's example: 09-02 13:05 |
| `---` | else walk v4lineage until it prints exhaust, baton-passing on riderTF reversal | the chain continues |
| `----` | riderTF can only advance one TF at a time. riderTF + linhop is a forward looking view only | lin-hop READS ahead; the baton MOVES one TF |
| `----` | for riderTF+1 to accept a baton-pass, riderTF+1 must be exfence at the time of riderTF reversing | the receiver's own gate, read on the reversal bar |
| `----` | if the receiver of the baton is between ex-fence and oob when the baton is taken | the stuck receiver case |
| `-----` | if the receiver reverses while still positioned between ex-fence and oob | AND it reverses while still stuck |
| `------` | EXHAUST is declared IF a linhop TF is not oob | AND a lin-hop TF is not oob |
| `----` | if riderTF cannot see an ex-fence rline inside the linhop TFs at the time of riderTF reversing | the no-successor case |
| `-----` | declare EXHAUST | Joe's examples: 09-01 20:51 on ws9r reversing, 09-02 02:00 on ws6r |
| `---` | at exhaust, create a rev-trade | every exhaust path ends in a rev-trade |
| `-` | else if ws5r is reversing and not OOB | the ELSE to "if ws5r is oob and reversing" - same level, same test on ws5r, opposite oob state |
| `--` | create a rev-trade | no exhaust test, no lineage walk, no lin-hop read. The reversal alone creates it |

Joe's worked examples, measured against the ruled knobs. `v4_rev_wob` 3, `v4_lin_hop` 2,
ex-fence 20/80, oob 15/85, all three on the low side.

| the example | the branch it belongs to | the matching event | measured | vs his time |
|---|---|---|---|---|
| 09-02 13:05 | ws5r oob and reversing, no exhaust, walk ws5r to ib, lin-hop TFs not oob | the ws5r ib cross, xwob 3 stamped | 2026-09-02 13:05:10 | +10 s |
| 09-01 20:51 | ws5r reversing and NOT oob | the first bar at the ws5r extreme | 2026-09-01 20:51:10 | +10 s |
| 09-01 20:51 | the same | the ws5r reverse | 2026-09-01 20:53:15 | +135 s |
| 09-02 02:00 | riderTF sees no ex-fence r in the lin-hop range | the ws6r reverse | 2026-09-02 01:54:05 | -355 s |

The lin-hop reads at each reverse:

| the example | the lin-hop range | the TF | value | oob | ex-fence |
|---|---|---|---|---|---|
| 09-02 13:05 | ws6..ws7 | ws6r | 14.69 | YES | YES |
| 09-02 13:05 | ws6..ws7 | ws7r | 18.05 | no | YES |
| 09-02 13:05 at the ib stamp | ws6..ws7 | ws6r | 22.15 | no | no |
| 09-02 13:05 at the ib stamp | ws6..ws7 | ws7r | 21.74 | no | no |
| 09-01 20:51 | ws10..ws11 | ws10r | 20.64 | no | no |
| 09-01 20:51 | ws10..ws11 | ws11r | 28.45 | no | no |
| 09-02 02:00 | ws7..ws8 | ws7r | 33.74 | no | no |
| 09-02 02:00 | ws7..ws8 | ws8r | 36.83 | no | no |

### 09-01 20:51 moved branch, by Joe

His first message placed it under the no-successor EXHAUST: *"examples 09-01 2051 on ws9rev"*. His
second placed it under the new else-if: *"the 09-01 2051 was reversed by ws5r while ws5r was
infence"*. Both quotes stand as written; neither is rewritten.

Measured, the two fire 10 s apart, which is why one timestamp can name either:

| the event | bar | value | not oob |
|---|---|---|---|
| the ws5r reverse, ws5r in-fence | 2026-09-01 20:53:15 | 29.19 | YES |
| the ws9r reverse, no ex-fence r in ws10..ws11 | 2026-09-01 20:53:25 | 2.31 trough | ws10r 20.64, ws11r 28.45 |

Which branch owns 20:51 decides which rev-trade is created and on which line. Joe to confirm.

---

---

## 3. Its own rulings

| # | the rule | Joe's words |
|---|---|---|
| 4 | target-side is set by an OPEN trade. LONG = high, SHORT = low | *"it is set by an OPEN trade.  if the trade is LONG, target-side is high. inverse for SHORT"* |
| 5 | the away/toward perspective is the open trade's | *"5, the perspective of the open trade"* |
| 6 | two or more ws1r..ws5r candidates tagged `toward` - the higher TF wins | *"6, the higher"* |
| 7 | no candidate tagged `toward` - keep walking | *"7, keep walking"* |
| 8 | the baton-pass gate is riderTF+1 ex-fence | *"8, riderTF+1 ex-fence"* |
| 9 | "if ws5r is oob and reversing" reads ws5r itself, whoever holds the baton | *"9, ws5r is fixed for that condition"* |
| 11 | `ws{TF+lin-hop}r` - TF is riderTF | *"11, riderTF.  if you have any uncertainty about this, refer back to me - don't invent anything"* |
| 12 | "the lin-hop TFs are not oob" - ANY of them | *"12, any"* |
| 14 | "inside the linhop TFs" - the range riderTF+1 .. riderTF+lin_hop | *"14, the range"* |
| 18 | lin-hop is VIEW ONLY and may read past `TF_CEILING` | *"linhop is view only. if ws9 or ws10 are somehow reached, the linhop TFs will tell the mech if ws9 or ws10 will exhaust"* |
| 20 | "reversing" is the excursion extreme | *"#20, excursion-extreme reading"* |

### 11 carries an instruction, not just a value

Joe: *"if you have any uncertainty about this, refer back to me - don't invent anything"*. It applies
to every TF reference in this mech, not only to that line.

### 13 was not a second rule

Joe: *"I'm not clear how you reached this all-or-nothing logic"*. It was his own "any" read
backwards. With `LIN_HOP` 2 and riderTF ws6 the range is ws7..ws8; measured at the ws6r reversal
2026-09-02 01:54:05, ws7r 33.74 and ws8r 36.83, neither oob, so EXHAUST fires under "any". The only
state in which it does NOT fire is both oob.

### `REV_WOB` is DELETED - Joe 1023

Joe 1023: *"delete REV_WOB"*. It is gone from `v4_knobs.py`; the lineage reversal hold is `LIFT_WOB`
inside `lift_off`, and nothing ever read `REV_WOB`. This section used to argue it was *"a formality
under #20"*, which kept a deleted knob alive in the spec at a value it no longer has.

---

## 4. The baton-pass hatch - CONFIRMED 1022

Joe 1022, verbatim, after two earlier attempts at the same hole were measured and set aside:

```
-IF current-rider found a reversal in its lookback <- current code, triggered by ws6r
--walk current-rider until cross to ib <- this applies only to a current rider that carried a reversal in lookback
--pass the baton to tf+1 or exhaust
--if the baton passes to tf+1 (second-new-rider) and second-new rider finds a reversal in lookback 
---declare exhaust
```

Joe, same message: *"the logic: the 2nd "walk to ib" gives enough time for a reversal to print
without contention"*. And confirming it: *"cool beans.  find the knobs etc, and bank this mech as
the confirmed build"*.

### What hole it closes

A rider can arrive already spent: the baton reaches it AFTER its own reversal has printed, so
*"baton-passing on riderTF reversal"* has nothing left to pass on. Measured 2026-08-31: ws6 takes
the baton at 19:45:40 with its reversal 105 s behind it, at 19:43:55.

### Why it beats the three floors that were measured first

His first wording was a FLOOR - *"new-rider has a previous same-side reversal which printed >=
old-rider's reversal timestamp"*. Three candidate floors were measured over 08-30..09-06 on
ws5..ws10, both sides:

| the floor | what it reads | can it invert | measured |
|---|---|---|---|
| the old rider's reversal, his first wording | ANOTHER line's timing | YES | **129 of 447 clustered hand-offs invert, 29%**. ws9 -> ws10 inverts 50% of the time |
| the new rider's own oob run | only the new rider | no | admits a reversal a median 510 s stale, max 3,540 s |
| the leg's start | the open mech | no | **IT IS THE BOUND IN FORCE** - see "What bounds the lookback" below. Recorded as unmeasurable while #17 was unbuilt; the code had it all along |

THE SECOND WALK NEEDS NO FLOOR AT ALL. It never compares two lines' reversal timestamps, so the
29% inversion rate cannot touch it. That is the whole reason it is the build.

### It has no stuck state

| at the receiver gate | the outcome |
|---|---|
| receiver not ex-fence | EXHAUST |
| receiver ex-fence, no reversal in lookback | the baton passes, the normal path |
| receiver ex-fence, reversal in lookback | the SECOND walk to ib |
| after the second walk, second-new-rider has a reversal in lookback | EXHAUST |
| after the second walk, second-new-rider does not | the baton passes, the normal path |

IT IS ONE LEVEL PER HAND-OFF, AND THAT IS HIS SPEC, NOT A LIMITATION. The two spent receivers are
NOT treated alike:

| who arrives spent | what happens | where it is written |
|---|---|---|
| the receiver at a normal hand-off | the SECOND walk to ib | his `--walk current-rider until cross to ib` |
| the second-new-rider, after that walk | EXHAUST, no third walk | his `---declare exhaust` |

The hatch can still fire again LATER in the same walk - if the second-new-rider is clean the baton
passes to it, and the next hand-off tests its own receiver from scratch. What cannot happen is a
second walk stacked on a second walk.

*Corrected 1023.* This section previously read *"it recurses without a special case: a line that
later receives the baton already spent becomes the current rider with a reversal in its lookback,
and the same second walk applies"*. That sentence was not from Joe and not from the code - it was a
generalisation of the mech written into the spec as if it were the mech. His own spec line
`---declare exhaust` is the terminal case, and the code does exactly that.

### The knobs - NO NEW ONES

Everything it reads is already banked. `v4_knobs.py` is the in-force copy.

| what it reads | the knob | value |
|---|---|---|
| the ib dwell, both walks | `LIN_IB_DWELL` | 2.5 bars per TF, int(TF x 2.5) |
| the oob fence | `OOB_FNC` | 15 -> (15, 85) |
| the receiver's ex-fence | `RMOM_FNC` | 80 -> (20, 80) |
| the reversal detector | `LIFT_PTS` / `LIFT_TOL` / `LIFT_WOB` / `GAP_PER_TF` | 6 / 2.0 / 8 / 2.8 |
| the chain's top | `TF_CEILING` | 10, PROVISIONAL |

### What bounds the lookback - CORRECTED 1023, and it is not what this section used to say

This section used to state: *"the LOOKBACK is bounded by the line's own same-side oob RUN, not by a
bar count"*. **That was never implemented.** `v4_fast.walk` seeds every rung's reversal with
`first_rev_at_or_after(R[t], t, side, A, B)`, and `A` is the walk's anchor, so:

| the bound the code actually applies | the consequence |
|---|---|
| **the leg's own start** - no reversal before the anchor is visible to any rung | the oob-run bound is absent; nothing reads a line's own run |
| the stamp is `bar + LIFT_WOB - 1`, always after the raw bar | a receiver's reversal is ALWAYS at or after the anchor, never before it |

So *"a rider arrives already spent"* can only ever mean **spent relative to the baton-pass bar,
having reversed during the walk** - never spent before the walk began. The latter is unreachable by
construction, not rare.

THIS MOVES A ROW IN THE FLOOR TABLE ABOVE. *"the leg's start"* was recorded as UNMEASURABLE because
#17 was unbuilt; it is in fact the bound in force, and since 1023 the machine produces the anchor
itself (`v4_machine._lineage` asserts the anchor is machine state, never a window edge), so it is
now measurable.

**UNRULED, and Joe's to settle:** whether the oob-run bound this section claimed should be built. It
would SHRINK the lookback - a reversal inside the leg but outside the receiver's own oob run would
stop counting - so it is a mech change, not a correction. No `lookback` bar-count knob is invented
either way.

### The leg - REPLACED 1023, because the first one was never legitimate

**WHAT WAS WRONG WITH THE OLD EVIDENCE.** This section used to carry a 2026-08-31 trace produced by
`v4_lineage_trace.py '2026-08-31 19:00:00' '2026-08-31 21:30:00' 5 low` - a hand-made call that
starts the walk at the window's own left edge. Joe 1023 caught it: *"it can't: ws1b doesn't reach
low oob until 19:17"*. cws1b first reads low oob at 19:17:00 (13.41); at 19:02:55 ws1b was 69.98.
**No trade existed at 19:00:00, so there was nothing for lineage to walk.** The hatch's only
measured evidence came from an anchor the machine would never have produced, and the mech was
banked on it.

`v4_machine._lineage` now asserts the anchor is machine state, so that call is no longer reachable:
the driver's `trace` mode refuses the old bar outright - *"no leg contains 2026-08-31 19:45:40 | the
chain has not opened by then"*.

**THE REPLACEMENT, on Joe's own key setup.** Joe 1023: *"find the hatch a legitimate leg. the key
setup (that you probably already know) is ws5r oob plus ws6r oob"*. Reproduce it with:

`v4_machine.py trace - '2026-09-01 00:00:00' '2026-09-03 23:59:55' saviour,core,backstop drop '2026-09-01 01:35:30'`

| where the anchor came from | the reading |
|---|---|
| the mech | v4-ws5rbackstop, fire 2026-09-01 01:16:55 |
| the anchor lineage walks from | 2026-09-01 01:16:20, the fire's own ws5r reversal - machine state, not a window edge |
| ws5r at the anchor | 3.47, LOW oob |
| ws6r at the anchor | 6.93, LOW oob - **his key setup, both oob** |
| the same-side oob run holding ws5 | ws4-ws6, so the walk starts at ws4 |

| the step | the bar | the reading |
|---|---|---|
| ws4 is the rider and reverses | 2026-09-01 01:16:20 | ws4r 6.91, knowable 2026-09-01 01:16:55 |
| ws4 walks to ib, dwell 10 bars | 2026-09-01 01:20:45 | crossed 2026-09-01 01:20:00, dwell proven 10 bars = 50 s |
| ws4 -> ws5, the receiver gate | 2026-09-01 01:20:45 | ws5r 11.13, ex-fence YES |
| ws5 takes the baton | 2026-09-01 01:20:45 | its reversal 2026-09-01 01:16:20 knowable 2026-09-01 01:16:55, below the ws6 lookback floor - no lookback test |
| the normal path | 2026-09-01 01:20:45 | ws5 waits for its own reversal |
| ws5 reverses | 2026-09-01 01:16:20 | ws5r 3.47, knowable 2026-09-01 01:16:55 |
| ws5 walks to ib, dwell 12 bars | 2026-09-01 01:35:30 | crossed 2026-09-01 01:34:35, dwell proven 12 bars = 60 s |
| ws5 -> ws6, the receiver gate | 2026-09-01 01:35:30 | ws6r 11.64, ex-fence YES |
| **ws6 takes the baton** | **2026-09-01 01:35:30** | **its reversal 2026-09-01 01:34:00 knowable 2026-09-01 01:34:35, FOUND in its lookback - THE HATCH** |
| the SECOND walk to ib on ws6 | 2026-09-01 01:37:10 | dwell 15 bars, held 15 bars = 75 s |
| ws6 -> ws7, the receiver gate | 2026-09-01 01:37:10 | ws7r 10.20, ex-fence YES |
| ws7 is the second-new-rider | 2026-09-01 01:37:10 | its reversal 2026-09-01 01:18:40 knowable 2026-09-01 01:19:15, FOUND in its lookback |
| **EXHAUST** | **2026-09-01 01:37:10** | the second-new-rider carried a reversal too |

| what the leg produced | value |
|---|---|
| the verdict | EXHAUST 2026-09-01 01:37:10 |
| the trade it opens | 2026-09-01 01:37:15, LONG |
| what the second walk bought | 100 s, 01:35:30 to 01:37:10 |
| the ws6 ib run | 15 bars against a 15-bar requirement - ZERO bars of margin, thinner than the old leg's one bar, and recorded as such |

### The same leg is also the floor knob's A/B

Note the ws5 hand-off at 01:20:45: ws5 arrives with its reversal already behind the baton too, and
is passed WITHOUT a lookback test because the ws6 floor excludes it. Running the SAME leg with the
floor off - `W_V4_EXPERIMENT=1 W_V4_LIN_LOOKBACK_FLOORED=0`, one variable changed - moves the hatch
down a rung:

| `LIN_LOOKBACK_FLOORED` | where the hatch fires | the second walk runs on | EXHAUST |
|---|---|---|---|
| 1, banked - the floor is ON at ws6 | ws6 takes the baton 01:35:30 | ws6, dwell 15 bars, held 15 | 2026-09-01 01:37:10 |
| 0 - every rung looks back, which is what the code did 1022 to 1023 | ws5 takes the baton 01:20:45 | ws5, dwell 12 bars, held 12 | 2026-09-01 01:35:30 |

100 s apart on this leg. With the floor off the hatch fires on the FIRST hand-off, which is the
by-construction case already recorded in §7 (The start TF): the walk starts at the bottom of the
oob run, so its own starting rung is spent the moment it hands over.

### The hand-off inventory, and what it is built from

`v4_machine.py hatch` walks the chain once and records EVERY baton hand-off the walks made, from the
`events` hook inside `v4_fast.walk`. Nothing is re-implemented and nothing is parsed from a
printout, so the inventory cannot drift from the walk it describes.

Full tape, 2026-07-02 12:00:00 .. 2026-10-04 23:59:55, 1086 backstop fires, `LIN_PASS` 'ib',
STALE COUNT - 1086 was measured on the 1023 centroid config (k_len 6, rsi 6, stc 8). On the DB row
banked 1024 - R_RSI 5 / R_STC 8 / R_KLEN 7 - the same tape carries 602 fires, 468 of them with a
walkable run. The percentages below were not re-measured and are the 1086 population's.
lookback floor ON at ws6, `RULED_OK True`:

| the read | value |
|---|---|
| baton hand-offs the chain made | 2881 |
| of those, the receiver arrived SPENT - the hatch fires | 617 |
| of those, ws5r AND ws6r both oob AT THE ANCHOR - his key setup | 223 |
| the lookback cannot reach behind the anchor | `first_rev_at_or_after(.., A, ..)` seeds every ST from A, so "already spent" ALWAYS means reversed DURING the walk |
| hand-offs blocked by the ws6 lookback floor | 2151 |
| the pass bar can never show ws5r oob | LIN_PASS is 'ib': the sender is IN bounds there |
| how stale the receiver was at the pass, median | 280 s |
| how stale the receiver was at the pass, max | 3845 s |

| what the hatch branch ITSELF did | hatch fires | of those on his setup |
|---|---|---|
| EXHAUST, second-new-rider not ex-fence | 192 | 62 |
| EXHAUST, second-new-rider spent too | 415 | 159 |
| PASSES ON to ws7 | 9 | 2 |
| PASSES ON to ws8 | 1 | 0 |

| the hand-off rung | hatch fires | of those on his setup |
|---|---|---|
| ws5 -> ws6 | 547 | 205 |
| ws6 -> ws7 | 64 | 18 |
| ws7 -> ws8 | 6 | 0 |

**THE HATCH IS NOT A DEAD END, AND IT NEARLY IS.** 10 of 617 fires pass the baton on - 9 to ws7, 1
to ws8. The other 607 declare EXHAUST at the second-new-rider. On his ws5r+ws6r setup it is 2 of
223. A 3-day sample showed 0 of 22 passing on, which is why the count is taken on the full tape.

What his spec asks of the second walk it delivers: *"the 2nd 'walk to ib' gives enough time for a
reversal to print without contention"*, and the reversal does print. On this evidence it is the
second-new-rider's OWN reversal 415 times, which then declares exhaust - so the second walk moves
WHEN exhaust fires far more often than whether it fires.

The `events` hook is behaviour-neutral and that is measured, not asserted:

| the parity run | result |
|---|---|
| 2026-08-27 12:00:00 .. 2026-09-04 11:59:55, 77 fires, 77 walks, 5835 ib_cross probes | 0 disagreements |
| the 3-day hatch counts, before and after the hook | 104 / 22 / 8 both times |

### It is NOT the v4-lineage walker

`v4_lineage_trace.py` traces the baton chain and nothing else. There is no v4-lineage walker, no
rider selection from the ws1r-ws5r trajectory pool, and no rev-trade - #17 the open mech is held
back by Joe on purpose: *"I'm holding it back so that your SRP is on point"*.

## 5. Dropped

| the mech | Joe's word | the date |
|---|---|---|
| the ws5x escape hatch for a stale baton-pass | *"I think the idea is flawed - I'd rather forego a bit of profit than pay for stops"* | 1022 |

Dropped, and it gets no code, no knobs and no further explanation. `LIN_X_TRAVEL` and
`XCROS_MIN_SPEED` were banked and have been removed from `v4_knobs.py`.

The hole it was aimed at is closed by SS4, the second walk to ib, which needs no x line.

## 6. BUILD-GATE - still open

| # | the gap | status |
|---|---|---|
| 17 | what OPENS the first trade | deferred by Joe: *"different mech.  you'll have the answer after we lock `v4-lineage`"* and *"not for v4-saviour.  I'm holding it back so that your SRP is on point"* |
| 39 | the ws2x-cross | Joe 1022: *"in-design presently. not for v4-saviour"* |
| 43 | a baton-pass whose new rider has already reversed | CLOSED 1022 by SS4, the second walk to ib |
| - | NOTHING IS CODED for v4-lineage. The producers exist; no walker wires them | CLOSED - v4_fast.walk and v4_lineage_trace.walk, in parity |
| - | **a rev-trade that aligns with an ws{TF>3}r crossing to same-side oob** | **PARKED BY JOE 1024, HIS TO RESUME** - see below |

### The rev-trade that should have deferred to lineage — PARKED 1024

Joe 1024, raising it twice:

> if a rev-trade signal aligns with an ws{TF>3}r crossing to same-side oob, defer to lineage
> eg 0816 rev-trade would be squashed by ws5r crossing to low oob
> --this likely infers a deeper issue in the baton passing process

Then, on seeing the sweep-pivots score of the 09-01 machine chain: *"hold on to
'2026-09-01 10:07:35 SHORT, backstop' for me - I'll come back to it. I think it's the same issue I
brought to you for 0816"*.

THE NUMBERS ON HIS 10:07:35 EXAMPLE, so it is recoverable without re-deriving it. Scored by
`sweep-pivots` on the machine's own ARM2-on chain for 2026-09-01, the trade's OPEN bar:

| the read | value |
|---|---|
| the trade | 2026-09-01 10:07:35 SHORT, v4-ws5rbackstop |
| its fire | 2026-09-01 09:49:35, start TF ws5, EXHAUST 2026-09-01 10:07:30 |
| the scale TF sweep-pivots picked | ws1Mage, 1 TF agreeing |
| the pivot | 2026-09-01 10:40:05 |
| **the open is off the pivot by** | **-2.040%** - the worst of the 14 trades by a factor of 1.4 |
| **the share of the leg already behind** | **1.081** |
| the leg MFE | +1.888% |

A share ABOVE 1 is the tell and it is why he linked the two: the swing the open was scored against
had already FINISHED before the trade opened. The other 13 trades that day run 0.007 to 0.726.

NOT BUILT, NOT DIAGNOSED, AND NOT TO BE PICKED UP WITHOUT HIM. Two concretions were already put to
him on the 0816 version and neither is answered: what *"aligns with"* means - the same bar or a
window - and whether *"defer to lineage"* drops the rev-trade or postpones it.

`TF_CEILING` 10 and `GAP_PER_TF` 2.8 are PROVISIONAL by his own words; they live in `v4_bank.md`.

## 7. The start TF, BANKED 1023 — and the walk that confirmed it

Until 1023 the backstop always handed lineage **ws5**, because the backstop is a ws5r mech. Joe
1023 replaced that:

> at v4-ws5rbackstop's signal, find the highest same-side oob ws{1-maxTF}r and pass it to lineage

> swap `highest` with `lowest` and retest

and, shown a set of ws4, ws5, ws7:

> why is ws7 there?  the v4lineage spec only allows jumps of +1

So the set must be CONSECUTIVE. An oob rung the baton cannot reach by +1 steps is a separate
island and is not part of the run. `K.walkable_run(R, fire_bar, side)` returns the contiguous
same-side oob run holding ws5; the start TF is its BOTTOM rung.

| the fire | all same-side oob | walkable runs | the run holding ws5 | start TF |
|---|---|---|---|---|
| 2026-09-01 19:15:35 | ws4, ws5, ws7 | ws4-ws5 **+** ws7 | ws4-ws5 | **ws4** |
| 2026-09-01 19:32:45 | ws3..ws10 | ws3-ws10 | ws3-ws10 | **ws3** |

### The walk Joe signed off

`19:15:35` fire, start ws4, side HIGH, anchored on the ws5r reversal at 19:15:00. Joe 1023, on
seeing the ws6 row: *"outstanding! I couldn't see the ws6r reversal on TV so I wasn't 100% sure of
the mech - now you've shown me that our work is paying off: 19:39 is a good result"*.

| the step | the bar | the reading |
|---|---|---|
| ws4 is the rider and reverses | 2026-09-01 19:24:00 | ws4r 93.03, knowable 2026-09-01 19:24:35 |
| ws4 walks to ib, dwell 10 bars | 2026-09-01 19:39:00 | crossed 2026-09-01 19:38:15, dwell proven 10 bars = 50 s |
| ws4 -> ws5, the receiver gate | 2026-09-01 19:39:00 | ws5r 82.29, ex-fence YES |
| ws5 takes the baton | 2026-09-01 19:39:00 | its reversal 2026-09-01 19:15:00 knowable 19:15:35, FOUND in its lookback |
| the SECOND walk to ib on ws5 | 2026-09-01 19:39:55 | dwell 12 bars, held 12 bars = 60 s |
| ws5 -> ws6, the receiver gate | 2026-09-01 19:39:55 | ws6r 86.47, ex-fence YES |
| ws6 is the second-new-rider | 2026-09-01 19:39:55 | its reversal 2026-09-01 19:24:25 knowable 19:25:00, FOUND in its lookback |
| **EXHAUST** | **2026-09-01 19:39:55** | the second-new-rider carried a reversal too |

The rev-trade opens 2026-09-01 19:40:00. Joe's own read of that leg was 19:31.

THE 14-MINUTE DELAY IS ONE STEP: ws4 reverses at 19:24:00 and does not cross to ib until 19:38:15.
Everything after that happens inside 55 seconds.

### A side effect of starting below ws5, stated not hidden

Lineage is anchored on the ws5r reversal, so when the baton reaches ws5 that reversal is ALWAYS
already in its lookback. Starting below ws5 therefore opens the baton-pass hatch on the first
hand-off every time, by construction - the hatch was written for a rider that happens to arrive
spent, not one that arrives spent by design. Joe was shown this and banked the mech anyway.

## 8. rev-trade's trigger, PART-RULED 1023

Joe 1023: *"rev-trade (the action of closing an incoming trade and opening a trade in the opposite
direction) fires on a signal from the mechs. for lineage, its `EXHAUST`. for the others, I don't
know yet."*

| the path | what fires the rev-trade |
|---|---|
| v4-ws5rbackstop, which defers to lineage | **EXHAUST** |
| v4core STEP4, which walks lineage | **EXHAUST** |
| v4saviour, which returns SAVIOUR REV directly | **NOT RULED** |
| the "immediate rev" legs in his walkthrough | **NOT RULED** |

### The open bar carries a guard

`max(EXHAUST, the fire) + 1`. Measured 1023 on the full tape: 4 of 911 walks exhaust BEFORE their
own fire bar, by up to 5.9 minutes, because the walk anchors on the raw ws5r reversal while the
fire waits up to `BSTOP_SYNC_MIN` 8.8 min for its oob partner. Without the guard those four would
open before their own signal existed. It lives in `v4_deferred_trades` so no caller can forget it.

### 175 fires have no walkable run

ws5r is not same-side oob at the fire bar on 175 of 1086 fires - it had already left oob while the
oob partner was setting the fire bar. Those fires can produce no start TF. `defer(..., fallback=)`
takes what to do, and NOTHING IS DEFAULTED: `None` drops the fire, a TF number uses that instead.
Joe has not ruled it.

## 9. The baton pass: the code differs from the handover ON PURPOSE — RULED 1023

READ THIS BEFORE "FIXING" THE PASS RULE. Joe's 1022 handover says the baton passes on the rider's
REVERSAL, three times over:

> baton-pass on riderTF reversing while riderTF+1 is oob

> baton-passing on riderTF reversal

> for riderTF+1 to accept a baton-pass, riderTF+1 must be exfence at the time of riderTF reversing

and he caught the code not doing that, 1023: *"I thought v4lineage uses reverse to pass the baton.
the only exception belongs to ws5 and ws6, under specific conditions"*. He is right about the
handover. The ib walk belongs to two places only - ws5r's own step, and the hatch, which his own
spec marks *"this applies only to a current rider that carried a reversal in lookback"*.

THE CODE WALKS EVERY RIDER TO IB ANYWAY, because that measures better. `LIN_PASS` carries both.

### The 94-day A/B, everything else at the bank

| LIN_PASS | trades | win % | net USDT | net % | worst DD | net/DD | PF |
|---|---|---|---|---|---|---|---|
| **ib**, the code | **565** | **66.9** | **+19115.41** | +546.35 | **344.61** | **55.47** | **3.61** |
| reversal, the handover | 594 | 66.2 | +18886.96 | +547.49 | 426.85 | 44.25 | 3.39 |

| the move to `reversal` | value |
|---|---|
| trades | +29 |
| win rate | -0.7 pp |
| net USDT | -228.45 |
| worst drawdown | +82.24, 23.9% worse |
| net / worst DD | -11.22, 20.2% worse |
| profit factor | -0.22 |

Joe 1023: *"let's align the machine with ib"*.

### It is not a one-cell result

Nine paired knob cells were run under each pass rule. `reversal` carries the bigger drawdown in 7
of 9, and the two rules want OPPOSITE `RMOM_FNC` values:

| the cell | ib net/DD | reversal net/DD |
|---|---|---|
| the bank | 55.47 | 44.25 |
| LIN_IB_DWELL 1.5 | 41.50 | 36.82 |
| LIN_IB_DWELL 4.0 | 61.56 | 64.93 |
| RMOM_FNC 70 | **66.40** | 39.05 |
| RMOM_FNC 90 | 50.85 | **32.12** |
| LIFT_WOB 6 | **70.75** | 58.88 |
| LIFT_WOB 12 | 42.37 | 27.68 |
| TF_CEILING 8 | 55.12 | 45.22 |
| TF_CEILING 12 | 55.47 | 45.24 |

### A knob move this sweep found, NOT applied

`RMOM_FNC` 70 under `ib` gives net/DD **66.40** against the bank's 55.47, on 552 trades against
565, with the drawdown falling 344.61 -> 293.30 and PF rising 3.61 -> 3.88. It is a candidate and
it is Joe's to rule; the bank stays at 80.

`LIFT_WOB` 6 gives the best net in both sweeps - +20,884.54 under ib - but it lifts fires from
1086 to 1274, so it is a volume lever rather than a quality one.

`TF_CEILING` still does nothing, at 8, 10 or 12. Same as the 1022 mech sweep found.
