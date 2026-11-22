# orac-exhaust, scored on sweep-pivots' four-read pivots

GOAL: find the lowest common denominator of a profitable setup. HIS 1118: *"this report's purpose
is to find the lowest common demoninator. if gates are applied, we don't have a fighting chance"*.
Every state below is a COLUMN in the report, never a filter on it.

---

## 1. HIS SPEC, as it stands

Verbatim, his 1118 final revision:

```
# the oracle exhaust
### the generalised oracle pattern that will create `orac-exhaust` needs to produce these 3 states
1) six x-crosses printing in 2 rows in lowband (refered to as `6x`)
***the next 2 must qualify within 3 rows, and those 3 rows encompass 6x***
2) lowband is printing (>=5 AW(any) OR >=2 AW flips) and 0 TOexf
3)
IF >=4 AWs print in lowband at the 3rd row
-highband has 5 minutes (walk forward) grace to produce >=2 AW flips and a maximum of 1 TOexf
```

with his later corrections: *"allow 4 rows to build 6x, and make it seven ws1-7 distinct x
crosses"*, so `6x` is now **seven** of ws1..ws7 inside **four** rows.

### his general notes, still in force

- *"all sides are target-side unless otherwise specified"*
- *"lowband is ws1-ws7. highband is ws8-ws15"*
- *"AW, TO, x, e prints are all per distinct TF"* - every count in the mech is distinct timeframes,
  never cells
- *"the zero TOexf condtion belongs to the final row, the other conditions are placed anywhere in
  the three rows"*
- *"1, 30sec"* - the mech reads the 30 second oracle: port 8791 until his 1119 pick moved it to 8792, the same 30 s rows on the four-read pivot trades
- *" LOW target-side creates a *OUTGOING* LONG,..."* - the setup row is the INCOMING trade, the one
  being closed; what is SCORED is the OUTGOING trade

---

## 2. THE FOUR-READ PIVOTS - sweep-pivots' own, not this mech's

HIS 1120: *"this isn't SRP.  the pivots can't belong in any fdm3 classes"*. The four-read pivots' rule, their knobs,
the sets a page imports (as found, +15 min, flipped), their LOOKAHEAD and their pine view are written once, in
[sweep-pivots' spec, section 10](../octo-freedom/1022_v4/v4_sweep_pivots.md). This section held the rule until 2026-11-20. orac-exhaust only imports the set
the page it reads reports in `/meta`.

---

## 3. THE MAE/MFE SCORING

HIS 1118: *"then we can use sweep-pivot's MAE/MFE to find what works and what doesn't"*.

| the choice | what it is | why |
|---|---|---|
| the span | the setup's own bar to the close of the leg that HOLDS it | mechanism-defined. No horizon and no percentage |
| the leg rule | `mode='last_cross'` - each run of same-side crosses collapses to its last, so legs tile and never overlap | his *"from a 'final' cross to ib, to the next 'final' cross to ib"* |
| the line | ws2Mage | under his leg mode it reads his 06:06 and 12:05 targets as LOW legs, and it is the line the pseudo trades already pivot on |
| the favourable direction | the OPPOSITE of the row's target-side | his *" LOW target-side creates a *OUTGOING* LONG,..."*. MAE is never above 0, MFE never below it - asserted |
| the ranking | MFE over abs(MAE), inside each side | his *"I take your recommendation"*. Ranking on MAE alone keeps a row with a tiny MAE AND a tiny MFE, which is a non-event scoring as a winner |
| the cut | top 20% and bottom 20% of each side | his *"would the 'top' 20% be a good starting place to pare from?"*, with the bottom printed beside it because a column the top shares means nothing if the bottom shares it too |

A row with no MAE at all sorts above every finite ratio, by its MFE, and prints `no MAE`.

---

## 4. THE BANKED KNOBS

All in `fdm3_knobs.py`; an off-ruled run raises at import unless `W_FDM3_EXPERIMENT=1`.

| the knob | value | his words |
|---|---|---|
| `ORAC_EXHAUST_PORT` | 8792 | *"1, 30sec"*; 8792 at his 1119 pick, was 8791 |
| `ORAC_EXHAUST_ROW_S` | 30 | the same |
| `ORAC_6X_ROWS` | 4 | *"allow 4 rows to build 6x"* |
| `ORAC_6X_HITS` | 7 | *"make it seven ws1-7 distinct x crosses"* |
| `ORAC_ROWS` | 3 | *"must qualify within 3 rows"* |
| `ORAC_LOW_HI` | 7 | *"lowband is ws1-ws7"* |
| `ORAC_HIGH_HI` | 15 | *"highband is ws8-ws15"* |
| `ORAC_LOW_AW` | 5 | *">=5 AW(any)"* |
| `ORAC_LOW_FLIPS` | 2 | *"OR >=2 AW flips"* |
| `ORAC_LOW_AW_3RD` | 4 | *"IF >=4 AWs print in lowband at the 3rd row"* |
| `ORAC_GRACE_MIN` | 5.0 | *"highband has 5 minutes (walk forward) grace"* |
| `ORAC_HIGH_FLIPS` | 2 | *">=2 AW flips"* |
| `ORAC_HIGH_TOEXF_MAX` | 1 | *"a maximum of 1 TOexf"* |
| `ORAC_OOB_JUMP` | 2 | *"jumps of 2 should be allowed to make it more sane"* |
| `ORAC_MAGE_HI` | 15 | *"this new spec intentionaly contains the in-use TFs to ws1-ws15"* |
| `ORAC_LEG_MODE` | last_cross | *"from a 'final' cross to ib, to the next 'final' cross to ib"* |
| `ORAC_MAEMFE_LINE` | ws2Mage | the scoring line |
| `ORAC_RANK_BY` | mfe_over_mae | *"I take your recommendation"* |
| `ORAC_CUT_PCT` | 20.0 | *"would the 'top' 20% be a good starting place"* |
| `ORACLE_X_REOPEN` | any | *"the only workable answer is B"* |
| `ORACLE_E_REOPEN` | winner | his 1109 4B, not re-ruled |

---

## 5. CAUSALITY

| the read | knowable at |
|---|---|
| states 1 and 2, the state 3 gate | the setup row itself |
| the state 3 grace | the bar inside the grace where highband completes. **The event fires THERE**, not at the 3rd row, because a forward walk cannot be answered before it happens. `gate_row` records which 3rd row opened it, and an assert holds that no event precedes its own 3rd row |
| a pivot, and so the pseudo trade's open, close and target-side | sweep-pivots' answer, [its spec](../octo-freedom/1022_v4/v4_sweep_pivots.md) §10d: FINAL only when the first opposite-side cross confirms - 940 s after its confirm bar at the median, never at it. Until 2026-11-20 this row said the confirm bar |
| MAE / MFE | the leg's close. SCORING ONLY - no mech step may read them |

The report marks every column with "at the bar?" so a column that cannot become a rule is visible
as such. The three grace columns are the only NOs.

---

## 6. WHICH PRODUCER MAKES WHAT - READ THIS BEFORE READING A NUMBER

**TWO DIFFERENT OBJECTS SCOPE THIS MECH, and they are not the same producer.** Joe 1119 caught the
first one being wrong: *"we shouldn't be using ws2Mage. a new mode was build in sweep-pivots that
relies on ws1 to ib, to the opposing oob to ib - this is the mode that 8792 is using"*.

| the object | its producer | what it scopes | its knob |
|---|---|---|---|
| the pseudo trade | `v4_sweep_pivots.pooled_trades` at sweep-pivots' bank - four reads of ws1Mage and ws1b, a run's FINAL cross to ib, the next pivot opposite. 3006 trades | the row's target-side, and every TO/AW, x-cross and TO(exf) read, because each is "anywhere in this trade" | sweep-pivots' `POOL_TF` 1, `POOL_DWELL_S` 0 - [its spec](../octo-freedom/1022_v4/v4_sweep_pivots.md) §10b |
| the MAE/MFE span | the `ws2Mage` leg that HOLDS the setup bar, under the `last_cross` leg mode | where the scoring starts and ends | `ORAC_MAEMFE_LINE` ws2Mage |

**THE PROBE NO LONGER GUESSES THE FIRST ONE.** It reads `pivots` from the page's own `/meta` and
builds that producer. Before his 1119 ruling it called the ws2Mage producer whatever port it read,
and on 09-24 the two target-sides were OPPOSITE on 679 of 2880 rows.

**THE SECOND ONE IS STILL A ws2Mage OBJECT, and he has not ruled on it.** His 1118 words named it -
*"then we can use sweep-pivot's MAE/MFE"* on ws2Mage legs - and his 1119 words were about the
trades, not the scoring span. Measured on 09-24, reading 8792:

| the check | rows |
|---|---|
| rows carrying both a trade and a scoring span | 2880 |
| the scoring span sits WHOLLY INSIDE its trade | 182 |
| the scoring span CROSSES its trade boundary | 2698 |

So a row's MAE and MFE are measured over a stretch that mostly runs past the end of the trade the
row belongs to. That may be exactly what he wants - a leg is a move, not a trade - but it is NOT
derivable from anything he has said, so it stays named here rather than changed.

## 7. OPEN, and his to rule

| # | what is unsettled |
|---|---|
| 1 | **no ELSE** in state 3. A 3rd row whose gate fails produces nothing - the literal reading of an IF with no ELSE |
| 2 | the grace's span: the 3rd row and the 9 rows after it, 10 rows = 5 minutes, the 3rd row included |
| 3 | *">=2 AW flips"*: distinct ws8..ws15 counted from the 3rd row to the bar being tested |
| 4 | *"a maximum of 1 TOexf"*: read on the bar the flips complete. Could be at most 1 anywhere in the grace instead |
| 5 | the rev-trade rule for ws1r+ws1b against gcws30r+gcws30b. No spec line, so the exit cannot be scored |
| 6 | does the MAE/MFE span move off the `ws2Mage` leg onto the pooled trade's own span. On 09-24 the span crosses its trade's boundary on 2698 of 2880 rows. His 1118 named ws2Mage and his 1119 spoke only of the trades - see section 6 |
| 7 | where his *"lineage2 has already printed exhaust at 02:11:30"* on 09-24 came from. This mech fires ONCE that day reading 8792, at 07:45:30, so it is not this one |

**TWO ITEMS LEFT THIS LIST AT HIS 1119, both ruled:**

| what it was | how he ruled it |
|---|---|
| the max oob tag's moment - the setup-row read against the incoming-leg read | *"drop the one-bar read columns"*. The setup-row read is gone; `legMage`, the incoming leg's max carried across the leg, is the only one |
| whether the *"towards/away x race = B"* button stays | *"say the word and the button comes out"* / *"yes"*. It is out; his B is permanent on the cross row |

## 8. THE ARTEFACTS

| what | where |
|---|---|
| the mech and every report mode | `oracle_rows.py` - modes `orac-exhaust`, `setups`, `contrast`, `line`, `mage50`. `pine` moved to sweep-pivots at his 1120 SRP ruling and now prints the new command |
| the four-read pivots | `v4_sweep_pivots.pooled_pivots` |
| the trades those pivots make | `v4_sweep_pivots.pooled_trades` - ONE HOME, called by the page AND the probe |
| which producer a page used | the page's own `/meta`: `pivots` is the machine value, `pivlabel` what a person reads |
| the knobs | `fdm3_knobs.py`; the pivots' own are sweep-pivots' ([its spec](../octo-freedom/1022_v4/v4_sweep_pivots.md) §10b) |
| the Excel table | `fdm3_orac_setup` in `pk_optimizer`, `port` in the primary key so 8791's and 8792's rows sit side by side |
| the 09-24 report | `out/orac_exhaust_0924.txt` |
| the setup hunt | `out/orac_setups_0924.txt` |
| the top/bottom 20% contrast | `out/orac_contrast_0924.txt` |
| the pivots for TradingView | `out/fdm3_pivots_0922_0928.pine`, made 1118 by the old fdm3 `pine` mode, a 1 minute pane, green = LOW pivot = OUTGOING LONG. New ones: `python3 v4_sweep_pivots.py pine D0 D1` ([its spec](../octo-freedom/1022_v4/v4_sweep_pivots.md) §10e) |
