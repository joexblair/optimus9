# strat-3-r-oob — open questions

Every one of these is Joe's. **None may be decided by the coder.**

## A. Knobs I set and he has not ruled on

| # | the knob | what I used | why it matters |
|---|---|---|---|
| A1 | **the event bar** | the last bar of the earliest qualifying 60 s window | it anchors the whole mage-rev walk |
| A2 | **the mage-rev walk start** | the event bar | on wsf_leash Joe ruled the walk starts at sig_utc. There is no sig_utc here |
| A3 | **which tf's mage-rev** | the earliest of the three that lands inside the stretch | Joe asked to see all three and has not chosen. On 24 of 28 episodes at least two tfs return the same bar, because `sig_conf` comes from the single `gcws30Mage` line |
| A4 | `ws1mage_rev.dwell` | 3 bars = 15 s | inherited from the wsf_leash config, still owner `mine` |

## B. Decisions never put to him

| # | question |
|---|---|
| B1 | **Is there an exit mechanic at all?** +33 min is a measurement offset, not a close. Nothing in this strategy closes a position |
| B2 | **Is the dr flip the backstop here too?** It bounds the scan, but no position has been closed by it |
| B3 | **Does a stop-loss exist?** sneaky-1 runs with none (`docs/sneaky_trade_1_handover.md`). Unstated here |
| B4 | **Is the `t` tag part of the strategy or an artefact?** The tag lives in Joe's spreadsheet, keyed to `wsl_sig_utc`. This strategy has no sig_utc, so `t` is not available to it live. The 20-row headline rests on a column the mech cannot read |
| B5 | **Pyramiding.** 24 of the 46 simultaneous runs sit within minutes of another. Episodes 8 and 9 are 3 minutes apart and map to the same wsf_leash row. Nothing says whether they are one trade or two |
| B6 | **Size.** 22,000 coins is banked for sneaky-1. Not stated for this |
| B7 | **The `sig_line`.** `gcws30Mage` was used. `sig_line_surgical` = `gcws15Mage` is banked at config v10 and untried here |

## C. Things that need measuring before any build

| # | |
|---|---|
| C1 | **OOS.** The 28 episodes are 5 days, all in-sample. There is no held-out block |
| C2 | **B4 is the blocker on the headline.** Strip the `t` tag and the set is 28 episodes at +0.213% mean, which does **not** clear the 0.1975% drag by much and does not clear 0.550% at all |
| C3 | **`min_travel` is 0.0.** Every reversal producer in the chain fires on any magnitude, dust included. Joe 0925: *"the true threshold is in the OOS data"* |
| C4 | **The horizon.** +33 min is one number from one sentence. No sweep of it exists |
| C5 | **Is the 60 s tolerance doing work?** 24 of the 28 episodes have all three lines oob on the **same** bar. The tolerance adds 4 |

## D. Explicitly closed — do not reopen

| | |
|---|---|
| the three-crossings reading of the tolerance | wrong, drops the motivating case. See `history.md` |
| `swing_detect(2)` as the confirmation | measured, median pivot 90 min away, 5 of 28 inside 33 min. Too coarse at this horizon |
| a "did price later exceed X" grading | lookahead and not a Joe mechanism. See `history.md` correction 4 |
| the price series | `J.px` **is** px_smooth, verified against the tape `__pxs__` to 3 dp |
| the position frame | dr +1 = SHORT, dr −1 = LONG. Joe 0925, verbatim |

## E. Added 0925, after the docs were first written

### E1 — `sig_lookback`, Joe's lookback allowance

Joe 0925 ruled the mage-rev walk may take a `sig` from up to **2 minutes = 24 bars BEFORE the
anchor** (the Mage line reversing). Banked as `jig.mage_rev_walk(..., sig_lookback)`, spec §22.17.
**It defaults to 0**, which is what `scan.py` and `scan_20260925.txt` were measured under.

**Measured impact on these 28 episodes at `sig_lookback` 24 bars — 3 move, all earlier:**

| episode | event bar | earliest mage-rev at lb 0 | at lb 24 | moved |
|---|---|---|---|---|
| 14 | 09-02 18:15:00 | 09-02 18:37:45 | **09-02 18:15:15** | **−22.5 min** |
| 19 | 09-03 16:52:00 | 09-03 16:53:40 | 09-03 16:52:35 | −1.1 min |
| 20 | 09-03 19:52:00 | 09-03 19:55:30 | 09-03 19:52:20 | −3.2 min |

The other 25 are unchanged.

**THE QUESTION: does this strategy run at `sig_lookback` 0 or 24?** Joe ruled 2 minutes for the
wsf_leash mage-rev walk. He has not said whether it carries here. `scan.py` is still at 0, so
**every figure in `measured.md` is the lb-0 measurement** and would need re-deriving at 24.

### E2 — episode 14's event bar is Joe's own walked time

`transfer/260924_strat_wsf_leash.xlsx` row 68 is `09-02 18:11:30`, column D = **09-02 18:15**,
column E = *"walked ws3"*. Row 69 is `09-02 18:15:00`.

So Joe walked 18:11:30 forward to 18:15, and the all-three-oob event bar is **09-02 18:15:00** —
the same bar. His walk and this detector landed on the same moment by different routes. That is
the strongest single agreement in the set and it should not be lost.

It also explains why the `sig_conf` at 18:11:45 is not a missed opportunity: it belongs to a
signal that was itself walked forward to 18:15.
