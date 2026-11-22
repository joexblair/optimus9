# fdm3-small-trade

**GOAL: tell, as the trade runs, whether it is still a small trade.** His 1119: *"to gather this
data, you'll start with finding the psuedo-trades that print mostly mid-board in the highband.  this
is a sign of a small trade, the game in which our Fu is not yet strong"*. The read feeds his wider
question, *"what I need is a way to predict if a TOexf line will convert to AW, based on the 4 mechs
and their states"*.

HIS NAME for this mech, 2026-11-19: `fdm3-small-trade`. His labels: `sml` and `lrg`.

## 1. HIS WORDS, in order

| step | his words |
|---|---|
| the first read, mine | over 50% of a trade's ws8-15 TO(inf) cells in -1, 0 or +1 - his *"mostly in the mid board ranges (0,-1,+1)"* |
| it failed | *"0258 was anything but small, so this tells me that my criteria is inadequate."* |
| his marker | *"the other marker is the count of distinct lines printing TO(exf) during the trade - I think anthing more the 1 line in TO(exf) during the trade would make the trade 'not small'"* |
| his number | *"highband lines printing TO(exf) during the trade:  2 is the max for a small trade."* |
| the decider | *"there's no differentiation here.  this means the TOexf prints are the decider"* - the travel marker and the mid-board share separated nothing on 09-24 once TO(exf) was applied |
| causal | *"can you turn this small-trade detector into a causal mech?  it would have to evolve with the walk - the resting state is `small-trade` until the mech(s) prove `large-trade`"* |
| where | *"print it underneath the existing 'legmage' data.  the labels will be `sml` and `lrg`"*, 8792 first, then the walk |
| the hold | his pick: `lrg` holds to the trade's close |

## 2. THE RULE

| what | the rule |
|---|---|
| the count | distinct ws8..ws15 lines whose cell reads TO(exf) on ANY row from the trade's first row to the row being read |
| `sml` | the resting state, from the trade's first row, while the count is 2 or less |
| `lrg` | from the first row where the count reaches 3, held to the trade's close |
| the next trade | opens back at `sml` |
| outside a trade | nothing prints |

A trade can open `lrg`. Towards/away resets every line to TO at a trade's open, so a highband line
already ex-fence on the new target-side reads TO(exf) on the trade's first row. On 09-24 three
trades go `lrg` on their first row: 12:03:35, 13:56:25 and 18:40:45.

## 3. CAUSAL

The count at a row reads that row and the rows before it in the same trade, and nothing later. It
only ever grows, so `lrg` cannot go back to `sml` inside a trade - an assert holds that.

**THE TRADE ITSELF IS NOT CAUSAL ON THE PAGE.** When 8792's pseudo trades are knowable is sweep-pivots'
to state, not this mech's - [sweep-pivots' spec, section 10d](../octo-freedom/1022_v4/v4_sweep_pivots.md) (his 1120
SRP ruling). So on the page the detector is causal inside each trade, and the trade's start is not. In a walk, the trade
is the walk's own, opened with its side at its open bar, and the detector is causal end to end.

## 4. WHERE IT LIVES

| the piece | where |
|---|---|
| the knob | `SMALL_TRADE_MAX_TOEXF` = 2 in `fdm3_knobs.py`, his `fdm3-small-trade-max-toexf`, BANKED - an off-bank run refuses |
| the detector | `small_trade(code, side, prt, cap)` in `fdm3_oracle.py`, per page state, at the page's row grain |
| the bit | bit 6 (64) of the legMage byte. legMage is ws1..ws15 in bits 0-3, so every legMage read masks with 15. The row stays 55 bytes |
| /meta | `smallmax` 2, `smallbit` 64 |
| the text | the legMage cell's second line: `sml` or `lrg` under the ws{TF} value |
| the reader | `oracle_rows.load()` returns `R['lrg']` and masks `R['legmage']` with 15 |

The encoding is the workmate's call (sidegig chat #70): the stride stays 55 so no reader breaks, and
spare bits of a related byte are this page's pattern - the Mage side of 50 rides in the up/dn byte,
`fdm3-infence-power` in the TO/AW byte. On the record: legMage is per LEG and the small-trade state
is per TRADE, two grains in one byte. If they ever need to move apart, a byte of its own is still
there.

## 5. THE CHECKS

| check | result |
|---|---|
| the page's start-up assert: a second count, per trade off the state's own trade list, against the detector, every row, all 4 page states | passed |
| 8792 rebuilt, against the 8792 it replaced, all 4 states: bytes that differ outside the legMage byte | 0 |
| legMage bits 0-5 that differ | 0 |
| 1109 r-pred control | 257,295, MATCH |
| start-up | 615.6 s |
| 2026-09-24 trades, pivots as found | 35 |
| `sml` on the trade's last row | 20 - the same 20 as his culled list |
| last-row label against the whole-trade count | 0 of 35 disagree |

| rows | pivots as found | flipped | +15 min | +15 min, flipped |
|---|---|---|---|---|
| in a trade | 271,884 | 271,884 | 271,854 | 271,854 |
| `lrg` | 98,301 | 124,193 | 118,719 | 97,571 |

## 6. OPEN

| the question | the state |
|---|---|
| the walk version | his pick, 8792 first and then the walk - not built. On 5 s bars it reads the towards/away state per bar, not per 30 s row, so a line that prints TO(exf) between two print bars counts there and not on the page |
| the 4 mechs that predict TO(exf) into AW | his 1119 analysis, on 09-24 only: docs/octo-freedom/1109_towards_away/notes_1119_small_trades_0924.md |
