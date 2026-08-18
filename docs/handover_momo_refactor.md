# handover — the momo refactor

Written 0818. Joe 0817 asked *"is the SRP fu strong with this one?"* about `momo` / `momo_g`. The
answer was no, with three faults, then: *"refactor as you see fit. confirm a bit-matched
v_ws_fin_walk table after the changes."*

## the three faults, as measured

### fault 1 — measurement and verdict are fused

`momo_core.momo()` fits a straight line, computes the tracking score, the slack, the level gate,
then in the flat branch fits a quadratic and computes its turning point and its bend. It returns
four things: `(state, slope, r2, r_at_bar)`. Everything the quadratic measured is discarded inside
the function.

That is exactly the number the reversal producer needs. At 08-04 11:33:30 ws1r bends **+17.65**
under a downward read — the line is turning up while the read says down. `momo_g` gate 2 sees it,
returns `'none'`, and throws the number away. Nothing outside the function can ever see it.

### fault 2 — `none` means ten different things

| file | line | why it returned `none` |
|---|---|---|
| `momo_core.py` | 53 | not enough history for the sample grid |
| `momo_core.py` | 56 | a NaN in the samples |
| `momo_core.py` | 70 | flat, and the level gate failed |
| `momo_core.py` | 91 | sloped, but failed level, alignment or the fit floor |
| `momo_gated.py` | 54 | curl, slope points the wrong way |
| `momo_gated.py` | 58 | curl, not enough history for the quadratic window |
| `momo_gated.py` | 61 | curl, a NaN in the quadratic window |
| `momo_gated.py` | 66 | curl, the quadratic is degenerate |
| `momo_gated.py` | 68 | curl, the bend points the wrong way — **this is the reversal** |
| `momo_gated.py` | 71 | curl, the quadratic does not describe the window |

A caller cannot tell "no data" from "the line reversed". Both print `none`.

### fault 3 — the same quadratic is fitted twice per call

`momo_core.py:82` `qa, qb, _ = np.polyfit(xx, yy, 2)` and `momo_gated.py:63` `co = np.polyfit(xx,
yy, 2)`. Same slice `r[w-nb+1 : w+1]`, same x, same degree, both across `MOMO_WINDOW_MIN * 12`
bars. Every gated curl pays for it twice.

## the plan, as built

**Split measurement from verdict, and leave the verdict identical.**

1. New `momo_core.momo_fit(r, dr, w, quad=...) -> dict`. It measures and decides nothing. Every
   number the two files currently compute goes in the dict: the sample indices, whether they were
   usable, slope, linear fit, the value at the bar, the tracking score, the slack, whether the
   level gate passed, whether the slope is aligned, and — when the quadratic is fitted — its
   coefficients, its turning point, its bend, its own fit and its sign against `dr`.

2. `momo()` becomes a thin verdict over that dict. Its 4-tuple return does not change, by value or
   by type.

3. `momo_g()` reads the SAME dict instead of re-fitting. Fault 3 disappears as a consequence, not
   as a separate change.

4. Each `none` gets a reason, exposed on the dict and through a new `momo_why()`. `momo()` and
   `momo_g()` keep returning the bare string, so no existing caller changes.

**`quad`**: the quadratic is fitted today only inside the flat branch. Fitting it on every bar
would add cost to every call. So `quad='auto'` (the default) fits it exactly where it is fitted
today; `quad=True` forces it, for the reversal producer, which needs the bend on every bar
regardless of branch.

## the hard constraint

`momo()`'s 4-tuple must stay bit-identical. Three vectorised mirrors match its formula and are NOT
being touched: `predict_board.py:170`, `vmomo.py`, `build_trades2.py:93`. `build_exhv2.py` imports
the constants back and rebinds them from argv, so they must stay module globals read at call time.

**The check:** `v_ws_fin_walk` must be unchanged.

### run it

    python3 verify_momo_refactor.py

Exit 0 means all three checks passed. The script reads the pre-refactor code straight out of git at
`BASE_COMMIT = 5a9c604`, the last commit before the refactor, so there is no frozen second copy of
the formula anywhere.

### check 1 and check 2 — the old code against the new code

Three r lines off the 08-04 tape (ws1r, ws2r, ws10r), 17,281 bars each, read both upward and
downward:

| check | what it walks | calls compared | mismatches |
|---|---|---|---|
| 1 | `momo()` and `momo_g()` at the default 60-minute window, every 7th bar | 29,628 | **0** |
| 2 | `momo_g()` inside `momo_window(4 x TF)` at 21 fixed points, timeframes 13 / 21 / 27, every 23rd bar | 13,536 | **0** |

All four verdicts appear in check 1's sample — 1,763 momo, 1,652 ungated curl (168 surviving the
gates), 278 sideways, 11,121 none.

### check 3 — v_ws_fin_walk

| | before the refactor | after |
|---|---|---|
| rows | 121 | 121 |
| sha256 | `98c5db7dd5d3356e2d072b06a75a0d875704168bfa6de3f1224d2f16881b2966` | same |

**BIT MATCH.** The recipe, so anyone can redo it by hand:

1. `SELECT * FROM v_ws_fin_walk` — the view carries its own `ORDER BY wfw_row`, so no ordering is
   added.
2. every column of every row cast to text, the 15 columns of a row joined with `|`.
3. the rows joined with a newline, in the order the view returned them.
4. sha256 of those bytes, utf-8.

### check 4 — nothing else broke

Every module that reads the verdict still imports: `build_exhv2`, `build_momo_landed`,
`build_handoff`, `build_ws_momo`, `s46_momo`, `build_s46_event`, `sweep_s46_momo`, `curl_pred`.
This one is not in the script — it is eight import statements.

## what it now gives the reversal producer

`momo_g_why(r, dr, w, quad=True)` returns `(state, reason, fit)`. On ws1r read downward, 4-minute
window, 21 points — the bars Joe pointed at:

| bar | ws1r | slope | fit | bend | turning point | gated | reason |
|---|---|---|---|---|---|---|---|
| 11:33:20 | 16.86 | -0.773 | 0.606 | 10.40 | 1.159 | sideways | sideways |
| 11:33:25 | 16.86 | -0.563 | 0.494 | 14.05 | 0.985 | sideways | sideways |
| 11:33:30 | 16.86 | -0.615 | 0.520 | 17.65 | 0.883 | none | curl, but the bend points against dr |
| 11:33:35 | 16.86 | -0.489 | 0.420 | 21.15 | 0.816 | none | curl, but the bend points against dr |
| 11:34:00 | 21.51 | -0.054 | 0.029 | 37.90 | 0.622 | none | curl, but the bend points against dr |

The bend climbs 10.40 to 37.90 while the read is downward. Before the refactor every one of those
bars printed `none` and the number was gone. Nothing about the verdict changed — only what a
caller can see.

## what this refactor is NOT

It does not tune anything.

`MOMO_R2_MIN` (the straight-line fit floor, 0.50), `MOMO_SLOPE_MIN` (the slope floor, 1.0) and
`LEVEL_SLACK` (13.9, whose slack is scaled by both of those) were set against a 12-point fit and
the domTF walk now runs them at 21 points. Re-deriving those three is task #1 and is Joe's call,
not part of this.

`CURL_ARC_MIN` (the arc floor, 4.0) and `CURL_R2_MIN` (the bend's own fit floor, 0.40) are NOT on
that list. The bend is fitted on every 5-second bar in the window against an x-axis stretched 0 to
1, so the point count cannot move it. Measured on ws1r at 11:33:30, 4-minute window, read downward:

| points in the straight-line fit | slope | straight-line fit | bend | arc | bend fit |
|---|---|---|---|---|---|
| 2 | -15.6117 | 1.0000 | 17.6460 | 4.4115 | 0.6216 |
| 12 | -1.1627 | 0.6230 | 17.6460 | 4.4115 | 0.6216 |
| 21 | -0.6146 | 0.5199 | 17.6460 | 4.4115 | 0.6216 |

The axis those two move on is WINDOW LENGTH, which is `K_WINDOW` (4) times the timeframe. A
re-derive aimed at the point count would not move them at all.


## one more thing the rebuild found

The run's own "by domTF verdict" print reported **542** rows from 121 signals. The DELETE that
precedes a rebuild filtered on all 15 knobs in the unique key; that summary filtered on 8, so it
summed the 08-04 and 08-05 windows and every vote setting in the table and called the mixture a
result.

Fixed by giving the key ONE definition, `_wsf_key(win_from, hi, lo)`, used by both. The print now
reads BLOCKED 62 / FREE 59, which totals 121 and agrees with `ws_fin_weak_mage`.

`v_ws_fin_walk` had the same fault and was NOT covered by that fix. Its join named 9 of the 15 knob
columns in `ws_fin_walk`'s unique key. It returned one walk only because the six it omitted
— `wfw_hold`, `wfw_sticky`, `wfw_g30_level`, `wfw_ho_xwob`, `wfw_curl_tfbars`, `wfw_htf_band` —
each held a single value across the whole table. The first second value would have put two walks in
one report with no warning. The view is now built by `create_view(db)` from `WFW_KEY_COLS`, all 15.
Rebuilt and re-checked: 121 rows, same hash.
