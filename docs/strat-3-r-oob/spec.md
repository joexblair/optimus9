# strat-3-r-oob — the spec

**STATUS: nothing built.** This describes the mechanic as it was measured on 0925, not a producer
that exists in `optimus9/`.

## 1. The premise — Joe 0925, verbatim

On row #6 of the wsf_leash IS set (09-02 18:11:30), Joe:

> "all 3 `r`s are oob at ~18:14. when all 3 are out together, there's really nowhere for them to go
> other than up - the trajectory can't last for long. this might be a clue; to test it you would
> need to scan _all_ of sig_utc to find the same scenario, then see if pxs reverses after the
> ensuing ws{unsure which}mage-rev"

His four rulings when asked how to build the test:

| # | Joe 0925 |
|---|---|
| 1 | *"use a 1min tolerance instead of a dwell"* |
| 2 | *"unsure: let's start with anywhere in the strtech"* |
| 3 | *"swing_detect(2). this isn't easy to quantify … maybe a secondary test that checks pxs 33 minutes after the signal would be useful confluence"* |
| 4 | *"let's see all 3 of the mage-revs, and the order of each `r` crossing to oob"* |

## 2. The mechanic

| step | |
|---|---|
| 1 | inside a dr stretch, find every bar where **ws1r, ws2r and ws3r are each out of bounds on the dr side at some bar inside a rolling 60 s window** |
| 2 | the **event bar** is the last bar of the earliest qualifying window |
| 3 | from the event bar, walk `ws1Mage`-rev, `ws2Mage`-rev and `ws3Mage`-rev in the producer's prescribed order |
| 4 | take the **earliest** of the three `sig_conf` prints that lands inside the stretch |
| 5 | the position is **dr +1 = SHORT, dr −1 = LONG** |
| 6 | the outcome measured so far is the position return at **the print + 33 minutes** |

## 3. The knobs

| knob | value | owner | note |
|---|---|---|---|
| oob | **15 / 85** | joe | constant. Never 25/75, 17/83 or 27/73 |
| the dr side | ≤ 15 at dr −1, ≥ 85 at dr +1 | joe | *"nowhere for them to go other than up"* at dr −1 |
| the tolerance | **60 s = 12 bars** at the 5 s grid | joe | *"use a 1min tolerance instead of a dwell"* |
| where it is tested | **anywhere in the dr stretch** | joe | *"let's start with anywhere in the strtech"* |
| the event bar | the **last** bar of the earliest qualifying window | **MINE, unruled** | |
| the mage-rev walk start | the event bar | **MINE, unruled** | on wsf_leash Joe ruled the walk starts at sig_utc; there is no sig_utc here |
| which tf's mage-rev | the **earliest** of the three | **MINE, unruled** | Joe asked to see all three; he has not chosen |
| the mage-rev print | `sig_conf` = `sig` + `boundary_xwob` 4 − 1 | joe | his 0925 ruling on the wsf_leash chain, carried here |
| `ws1mage_rev.dwell` | 3 bars = 15 s | **mine, unruled** | |
| `ws1mage_rev.rev_wob` | 2 steps | joe | |
| `ws1mage_rev.boundary_xwob` | 4 bars | joe | |
| `ws1mage_rev.sig_line` | `gcws30Mage` | joe | `sig_line_surgical` = `gcws15Mage` is banked and untried here |
| the outcome horizon | **+33 minutes** = 396 bars | joe | *"a secondary test that checks pxs 33 minutes after the signal"* |
| the bound | the dr latch flip | joe | his banked backstop |
| `swing_detect` pct | **2.0** | joe | tested and found too coarse — see `measured.md` |

## 4. The producers it reads — all existing, none new

| producer | where | role |
|---|---|---|
| `dr_latch_wob(m1, mx, i0, i1, wob)` | `docs/mage_cascade/stopsweep.py:62` | the dr. `LATCH_TF` 13, `LATCH_W` 8 bars = 40 s, fences `MAGE_HI` 75 / `MAGE_LO` 25 |
| `Ln(tf, 'r')` | the per-line cache | ws1r, ws2r, ws3r on the 5 s grid |
| `Ln(tf, 'Mage')` | the per-line cache | ws1Mage, ws2Mage, ws3Mage |
| `jig.ws1mage_rev(g1, sig_mage, hi, lo, …)` | `optimus9/analysis/jig.py:151` | **already parameterised on `g1`** — the ws2 and ws3 variants are calls, not clones |
| `compute.swing_detect.find_pivots(price, pct)` | `optimus9/compute/swing_detect.py:17` | the 2% ZigZag pivots |
| `J.px` | the Jig | the price. **It is px_smooth** — verified against the tape's `__pxs__` to 3 dp |

## 5. The position frame — Joe 0925, verbatim

> "here's the rule for trading: +dr = SHORT position, -dr = LONG postition"

So the return is **−(px move) × dr**. A price fall of 0.764% on a dr +1 event is a **+0.764%**
return, not a loss. This was got wrong once — see `history.md`.

## 6. The costs — already banked, do not re-derive

| figure | source |
|---|---|
| **0.1975%** per trade at 22,000 coins = 8.75 bps slippage round trip + 2 × 5.50 bps taker fee | `docs/mage_cascade_findings.md:307` |
| **0.550%** per trade, **measured at 88,000 coins**, carried into sneaky-1 as the conservative floor. Joe: *"accepting it is ok"* | `docs/sneaky_trade_1_handover.md:150, 348` |
| flat **16.06 USDT** per trade at 22,000 coins | `docs/sneaky_trade_1_handover.md:150`, `docs/wsf_dtf_v3_spec.md:1489` |
| taker 5.5 bps/side, slippage 3.35 bps/side, break-even round trip 0.1154% | `docs/arm_delay_book.md:117–128` |
| size **22,000 coins fixed** | `docs/wsf_dtf_v3_spec.md:1450`, Joe 0916 |
| the fill model — order-book walk, no order splitting | `docs/o9_live_design.md:45, 49` |

## 7. Why it is a separate strategy

Joe 0925: *"given that '3 `r`s oob' mostly fails to align with wsf_leash, I'm declaring it as a
second strategy to be developed separately"*.

**Measured:** of the 28 episodes, **1** lands exactly on a `wsl_sig_utc`. 8 of 28 are within 2 min
of one; the gaps reach ±2 hours. Three map to a wsf_leash row carrying the **opposite** dr.
