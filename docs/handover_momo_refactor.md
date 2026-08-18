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

## the plan

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

**The check:** `v_ws_fin_walk` must be unchanged. Baseline taken 0818 before any edit:

| | |
|---|---|
| rows | **121** |
| sha256 over all 15 columns | `98c5db7dd5d3356e2d072b06a75a0d875704168bfa6de3f1224d2f16881b2966` |

Rebuild with `build_ws_fin.py` and hash the view the same way. Anything but an exact match means
the refactor changed the verdict, and it must be reverted rather than explained.

## what this refactor is NOT

It does not tune anything. `MOMO_R2_MIN`, `MOMO_SLOPE_MIN`, `CURL_ARC_MIN` and `LEVEL_SLACK` were
all set against a 12-point fit and the domTF walk now runs them at 21 points. Re-deriving them is
task #1 and is Joe's call, not part of this.
