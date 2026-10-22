# octo-v4 — the bank

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

## 1. The board

Standing rulings, not v4's to change.

| the reading | value | Joe's words |
|---|---|---|
| oob | 15 / 85 | standing - oob is ALWAYS 15/85 |
| the sides | low < 50, high > 50 | 1022: *"low side = <50.  high side = >50"* |
| 50 itself | LOW | STRUCTURAL - his rule is "< 50" and "> 50", so one side must own the boundary. Stated, not decided quietly |

## 2. The side is an INPUT, never a derivation

BANKED 1022, after I derived it instead of reading it. Joe asked for *"a trade opens on the low side
ws5r reversal near 09-06 2220"*; I ran "low-side reversal" through `rev-trade`'s polarity to LONG /
target-side HIGH and v4saviour returned REV-TRADE off the wrong side. On his stated LOW side it
returns NOT ARMED. Joe: *"this is the proper way to view it - the v4saviour class will consume this
data from an external source"*.

| the rule | owner |
|---|---|
| `target_side` is +1 high / -1 low, set by the TRADE: LONG = high, SHORT = low | the trade |
| it is FIXED for the lifetime of the trade | RULED 1022: *"yes, the target-side is fixed for the lifetime of the trade"* |
| no mech computes it | every v4 mech takes it as an argument |

## 3. "Print" means the usable event

RULED 1022: *"when i say "print" about anything, I'll always be refering to the usable event"*. So a
wobbed event is read at its STAMP, bar + wob - 1, never at the bar the condition first changed.

## 4. The open signal

RULED 1022: *"accept the first open signal.  we'll build pyramid logic at a later time"*. The first
signal opens; later signals while a trade is open are ignored until pyramid logic exists.

## 5. open_bar and the warmup

RULED 1022: *"open_bar in warmup.  I don't see a case for this: in backtest we're reliant on the
line cache, and in o9-live the lines are already warm"*. No mech guards against it.

## 6. The handover, verbatim

Joe 1022, the lines that opened his first v4 message, unedited. The `v4-lineage` block from the
same message is carried in `v4_lineage.md`; nothing is reworded in either place.

```
v4_rmom_fnc, default 80 - fence used when testing if a r is close enough to oob to be predicted

`rev-trade` = close incoming trade on fill bar, and open a new "reversal" trade on the next bar. if target-side is low, the incoming trade is SHORT, the reversal trade is LONG

store this in memory: I'm no longer printing colons between hh and mm (1222 inplace of 12:22)
```

---

## 7. `rev-trade`

Joe: *"close incoming trade on fill bar, and open a new "reversal" trade on the next bar. if
target-side is low, the incoming trade is SHORT, the reversal trade is LONG"*.

| the field | the value |
|---|---|
| the incoming trade closes | on the fill bar |
| the reversal trade opens | the next bar |
| target-side low | incoming SHORT, reversal LONG |
| target-side high | not stated by Joe; the mirror would be incoming LONG, reversal SHORT — superseded - see below |

---

Joe 1022 completed the high side: *"15, if target-side is low, the incoming trade is SHORT, the
reversal trade is LONG. high target-side is receiving a LONG trade, the reversal is a SHORT trade"*,
and *"16, the reversal bar"* for the fill bar. The UNRULED note above is superseded by those two.

---

## 8. The knobs, BANKED

`v4_knobs.py` is the in-force copy. Importing it REFUSES an off-ruled run unless
`W_V4_EXPERIMENT=1`, and an experiment run prints every delta first. A spec doc is not in-use.

| the knob | value | units | Joe's words |
|---|---|---|---|
| `RMOM_FNC` | 80.0 | r-points | *"v4_rmom_fnc, default 80 - fence used when testing if a r is close enough to oob to be predicted"* |
| `LIN_HOP` | 2 | TFs | *"1, 2"* |
| `REV_WOB` | 3 | bars | *"2, 3"* |
| `IB_WOB` | 3 | bars | *"10, 3"* |
| `TF_CEILING` | 10 | TF | *"18, unsure.  use 10"* - PROVISIONAL |
| `SAV_WS2_OOB_TEST` | 10.0 | minutes | *"CAP: {knob:10, `V4_SAV_WS2_OOB_TEST`} minutes"* |
| `SAV_IB_XWOB` | 2 | bars | *"23, 2"* |
| `LIFT_PTS` | 6 | samples | *"34, 6 knob"* |
| `LIFT_TOL` | 2.0 | r-points | *"35, 2.0 knob"* |
| `LIFT_WOB` | 8 | bars | *"37, 8 knob"* |
| `GAP_PER_TF` | 2.8 | bars per TF-minute | *"let\'s choose 2.8 until we get to the sweep"* - PROVISIONAL |

The cascade's knobs are NOT re-declared. `MC_GAP` 48, `MC_ZOOM` 2, `MC_MIN` 4, `MC_TF_LO` 1 and
`MC_TF_HI` 12 are Joe\'s 1017 rulings and the Jig is their one home; `v4_knobs` asserts them, so a
change there refuses a v4 run rather than silently moving a verdict.

| the derived read | value |
|---|---|
| `fence()` | (20.0, 80.0) |
| `sav_cap_bars()` | 120 bars |
| `gap_for` ws1..ws5 | 3, 6, 8, 11, 14 |
| `gap_for` ws10, ws12, ws30 | 28, 34, 84 |

The gap rounding is RULED: *"38, yes"* to `round()`. ws3 8.4 -> 8, ws7 19.6 -> 20.

| the TF | TF x 2.8 | the gap | = seconds | the lattice span at pts 6 |
|---|---|---|---|---|
| ws1 | 2.8 | 3 bars | 15 s | 75 s |
| ws2 | 5.6 | 6 bars | 30 s | 150 s |
| ws3 | 8.4 | 8 bars | 40 s | 200 s |
| ws4 | 11.2 | 11 bars | 55 s | 275 s |
| ws5 | 14.0 | 14 bars | 70 s | 350 s |
| ws6 | 16.8 | 17 bars | 85 s | 425 s |
| ws7 | 19.6 | 20 bars | 100 s | 500 s |
| ws8 | 22.4 | 22 bars | 110 s | 550 s |
| ws9 | 25.2 | 25 bars | 125 s | 625 s |
| ws10 | 28.0 | 28 bars | 140 s | 700 s |
| ws11 | 30.8 | 31 bars | 155 s | 775 s |
| ws12 | 33.6 | 34 bars | 170 s | 850 s |

---

## 9. What is NOT here


Not carried from v3, by Joe's instruction: `v3_min_tf`, `v3_rmom_fnc`, `v3_mage_fnc`, the ws1b arm
and its dwell, the ws1Mage ib-cross test-point and its xwob, the ws2r oob gate, the three race
conditions (a) (b) (c), the x-cross direction mech, `v3-class-pred1` and `pred1_reach`, the
mrider band and its ws1/ws2 exclusion, the MAE race at 1.1, `v3_traj_k`, the away confirmation at
12 bars, and the away/toward perspective ruling.

Available as producers in the tree, NOT as v4 mechs, and only when Joe names one:
`jig.away_toward` / `away_toward_series`, the GPU momentum cache at `.rpl_cache/momt`
(ws1-ws30 + ws45 + ws60, r, both sides, 0 mismatches over 104,509,440 bar-comparisons),
`momo_gpu.py`, `momo_gated.momo_g`, and the line cache at `.rpl_cache/lines`.
