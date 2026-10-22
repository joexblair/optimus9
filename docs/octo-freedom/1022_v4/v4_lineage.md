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

### Why `REV_WOB` 3 is a formality under #20

On the full tape, ws1r to ws10r, 9,349 of 136,989 excursions fail the 3-bar hold and all 9,349 fail
the same way: the hold window runs past the excursion's own end. Inside its own excursion the hold
cannot fail, because after the last bar at the extreme the line never returns to it.

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
| the leg's start | the open mech | no | UNMEASURABLE - #17 is unbuilt |

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

And it recurses without a special case: a line that later receives the baton already spent becomes
the current rider with a reversal in its lookback, and the same second walk applies.

### The knobs - NO NEW ONES

Everything it reads is already banked. `v4_knobs.py` is the in-force copy.

| what it reads | the knob | value |
|---|---|---|
| the ib dwell, both walks | `LIN_IB_DWELL` | 2.5 bars per TF, int(TF x 2.5) |
| the oob fence | `OOB_FNC` | 15 -> (15, 85) |
| the receiver's ex-fence | `RMOM_FNC` | 80 -> (20, 80) |
| the reversal detector | `LIFT_PTS` / `LIFT_TOL` / `LIFT_WOB` / `GAP_PER_TF` | 6 / 2.0 / 8 / 2.8 |
| the chain's top | `TF_CEILING` | 10, PROVISIONAL |

ONE THING IS A CHOICE, NOT A KNOB, and it is stated rather than defaulted quietly: the LOOKBACK is
bounded by the line's own same-side oob RUN, not by a bar count. A reversal outside that run belongs
to a different move and is not read. No `lookback` window knob is invented; if a bar count is wanted
there instead, that is Joe's to set.

### The 2026-08-31 trace, reproducible

`v4_lineage_trace.py '2026-08-31 19:00:00' '2026-08-31 21:30:00' 5 low` prints this:

| the step | the bar | the reading |
|---|---|---|
| ws5 is the rider and reverses | 2026-08-31 19:23:20 | ws5r 4.92 |
| ws5 walks to ib, dwell 12 bars | 2026-08-31 19:45:40 | held 352 bars = 1760 s |
| ws5 -> ws6, the receiver gate | 2026-08-31 19:45:40 | ws6r 5.76, ex-fence YES |
| ws6 takes the baton | 2026-08-31 19:45:40 | its reversal 2026-08-31 19:43:55, FOUND in its lookback |
| the SECOND walk to ib on ws6 | 2026-08-31 19:48:55 | dwell 15 bars, held 16 bars = 80 s |
| ws6 -> ws7, the receiver gate | 2026-08-31 19:48:55 | ws7r 11.22, ex-fence YES |
| ws7 is the second-new-rider | 2026-08-31 19:48:55 | its reversal 2026-08-31 19:45:50, FOUND in its lookback |
| **EXHAUST** | **2026-08-31 19:48:55** | the second-new-rider carried a reversal too |

The second walk buys 195 s. In that window ws7's reversal moves from 5 s in the future and contended
to 185 s in the past and settled. The ws6 ib run holds 16 bars against a 15-bar requirement - ONE
BAR of margin, which is thin and is recorded as such.

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
| - | NOTHING IS CODED for v4-lineage. The producers exist; no walker wires them | OPEN |

`TF_CEILING` 10 and `GAP_PER_TF` 2.8 are PROVISIONAL by his own words; they live in `v4_bank.md`.
