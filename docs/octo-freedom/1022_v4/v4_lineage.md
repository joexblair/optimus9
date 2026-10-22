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

## 4. BUILD-GATE - still open

| # | the gap | status |
|---|---|---|
| 17 | what OPENS the first trade | deferred by Joe: *"different mech.  you'll have the answer after we lock `v4-lineage`"* and *"not for v4-saviour.  I'm holding it back so that your SRP is on point"* |
| 39 | the ws2x-cross | Joe 1022: *"in-design presently. not for v4-saviour"* |
| - | NOTHING IS CODED for v4-lineage. The producers exist; no walker wires them | OPEN |

`TF_CEILING` 10 and `GAP_PER_TF` 2.8 are PROVISIONAL by his own words; they live in `v4_bank.md`.
