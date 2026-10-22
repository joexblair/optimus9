# octo-v4 — the spec

Started 2026-10-22. Joe: *"v3 is dead. bank and commit push all, then prepare a greenfield for us
to build on. we're now starting `octov4`"* / *"don't carry anything forward from v3"*.

**NOTHING IN THIS FILE COMES FROM v3.** v3 is committed at f29d7eb as a record of the rulings it
collected. Its knobs, wobs, race conditions, arm, `v3-class-pred1` and away/toward perspective
ruling are not inherited. Each v4 mech arrives in Joe's words and is quoted here verbatim.

Joe's times carry no colons: `1305` is 13:05, `2051` is 20:51. His time estimates are +/- 5
minutes — take the mechanic, never fit a knob to the timestamp.

---

## 1. The handover, verbatim

Joe 1022, his first v4 message, unedited:

```
v4_rmom_fnc, default 80 - fence used when testing if a r is close enough to oob to be predicted

`rev-trade` = close incoming trade on fill bar, and open a new "reversal" trade on the next bar. if target-side is low, the incoming trade is SHORT, the reversal trade is LONG

store this in memory: I'm no longer printing colons between hh and mm (1222 inplace of 12:22)

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

---

## 2. The knob

| the knob | default | Joe's words |
|---|---|---|
| `v4_rmom_fnc` | 80 | *"fence used when testing if a r is close enough to oob to be predicted"* |

Nothing else is a v4 knob yet.

---

## 3. `rev-trade`

Joe: *"close incoming trade on fill bar, and open a new "reversal" trade on the next bar. if
target-side is low, the incoming trade is SHORT, the reversal trade is LONG"*.

| the field | the value |
|---|---|
| the incoming trade closes | on the fill bar |
| the reversal trade opens | the next bar |
| target-side low | incoming SHORT, reversal LONG |
| target-side high | not stated by Joe; the mirror would be incoming LONG, reversal SHORT — UNRULED, see §5 item 15 |

---

## 4. `v4-lineage`, read as logic

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

Joe's three worked examples, to be walked before any code is written:

| the example | Joe's words | what it is meant to show |
|---|---|---|
| 09-02 13:05 | *"(example 09-02 1305)"* | the lin-hop TFs are not oob after ws5r walks to ib, so a rev-trade is created |
| 09-01 20:51 | *"examples 09-01 2051 on ws9rev"* | riderTF cannot see an ex-fence r inside the lin-hop TFs, so EXHAUST |
| 09-02 02:00 | *"09-02 0200 on ws6r"* | the same no-successor EXHAUST, on ws6r |

---

## 5. BUILD-GATE — unspecified concretions, HALTED

No v4 code is written until these are answered. Numbered so Joe can answer by number.

| # | the gap | why it blocks |
|---|---|---|
| 1 | `lin-hop` has no value in v4 | every lin-hop test reads a different set of TFs depending on it |
| 2 | "reversing" has no wob | the reverse bar and the stamp move with the width; ws1r/ws2r were tested at 6 and ws5r at 8, 12, 18, none ruled for v4 |
| 3 | "ex-fence" — is it `v4_rmom_fnc` 80, mirrored to (20, 80)? | the receiver gate and the no-successor test both read it |
| 4 | "target-side" — what sets it, and when? | the rider pool is filtered on `toward` the target-side, so nothing selects a rider until the side exists |
| 5 | the away/toward tag — whose perspective? | v3's ruling was ws1Mage's for the whole ladder; that ruling is dead with v3 |
| 6 | more than one ws1r..ws5r candidate tagged `toward` — which wins? | the rider is one line |
| 7 | NO candidate tagged `toward` — what happens? | the mech has no entry |
| 8 | the pass condition appears twice with different tests: riderTF+1 **oob** at the top level, riderTF+1 **ex-fence** inside the walk | the same event has two gates; which applies when |
| 9 | "if ws5r is oob and reversing" — must ws5r be the rider, or does this fire on ws5r whoever holds the baton? | changes when the post-ws5r branch opens |
| 10 | "walk ws5r to ib" — any wob on the ib cross? | ws5r flickers across a fence bar to bar |
| 11 | "ws{TF+lin-hop}r's" — TF is ws5, or riderTF? | different TFs are read |
| 12 | "the lin-hop TFs are **not oob**" — all of them, or any one? | plural in his words, singular in the formula |
| 13 | "EXHAUST is declared IF **a** linhop TF is not oob" — any one, so all must be oob to deny exhaust? | same ambiguity, opposite polarity to #12 |
| 14 | "an ex-fence rline **inside the linhop TFs**" — the range riderTF+1..riderTF+lin_hop, or the single riderTF+lin_hop? | the no-successor test's population |
| 15 | rev-trade with target-side HIGH — not stated | only the low case is given |
| 16 | rev-trade's "fill bar" — the reversal bar, the wob stamp, or a separate fill mech? | the close and the open both hang off it |
| 17 | what OPENS the first trade? | a rev-trade reverses an incoming trade; v4 has no open mech yet |
| 18 | is there a TF ceiling on riderTF advancing? | the chain has no stated end |
| 19 | "ws9rev" — read as the ws9r reversal? | the 09-01 20:51 example cannot be walked otherwise |

---

## 6. Structural choices I made, stated

| the choice | what I did |
|---|---|
| the directory | `docs/octo-freedom/1022_v4/`, named for the start date, matching the `1005_scoring` / `1018_v3` pattern |
| `ln.py` | moved in. It is a cached-line reader built on 2026-10-20 after a straight data question cost 44 s, not a v3 mech — it reads the ruled line spec from `mech_lines(db, 'wsf')` and mmaps the cached `.npy`. 0.5 s a read against 44 s through `import machine` |
| his words | quoted verbatim in §1 and never rewritten. My reading sits beside them in §4, in its own column |
| no code | no walker, no knob module, no collector. The gate in §5 is open |

---

## 7. What is NOT here

Not carried from v3, by Joe's instruction: `v3_min_tf`, `v3_rmom_fnc`, `v3_mage_fnc`, the ws1b arm
and its dwell, the ws1Mage ib-cross test-point and its xwob, the ws2r oob gate, the three race
conditions (a) (b) (c), the x-cross direction mech, `v3-class-pred1` and `pred1_reach`, the
mrider band and its ws1/ws2 exclusion, the MAE race at 1.1, `v3_traj_k`, the away confirmation at
12 bars, and the away/toward perspective ruling.

Available as producers in the tree, NOT as v4 mechs, and only when Joe names one:
`jig.away_toward` / `away_toward_series`, the GPU momentum cache at `.rpl_cache/momt`
(ws1-ws30 + ws45 + ws60, r, both sides, 0 mismatches over 104,509,440 bar-comparisons),
`momo_gpu.py`, `momo_gated.momo_g`, and the line cache at `.rpl_cache/lines`.
