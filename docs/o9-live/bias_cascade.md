# The bias cascade + ladder-delay entry (0713–0714)

Joe's cascade, built this session. `bias_emit.py` (the emit + the mechanic), `bias_trace.py` (the per-30s
condition trace → `bias_trace`). Causal/emerging throughout; every read via the jig.

## THE NOTATION TRAP — read this before touching a k-line config

**Joe's notation and the DB tuple are NOT the same order.** Getting it wrong is silent.

```
Joe writes a k-line as   k_len | rsi_len | stc_len | src
the DB tuple is         ('k',  rsi_len,  stc_len,  k_len, src)
                                ^^^^^^^ Joe's FIRST number is the tuple's LAST
```
Verified against TV (`transfer/BYBIT_FARTCOINUSDT.P_s120.csv`, 54 bars): `s120r` built as `5|7|7`
(= `('k',7,7,5)`) matches TradingView to **mean absolute error 0.03**. Built the other way round it is off
by **9.33**. The bb notation and tuple DO agree (`len|mult|src`).

**FIXED 0714 — the order is now UNSAYABLE.** `optimus9/compute/line_config.py` is the only module that
knows the DB column order or the positional layout. Build every override through the jig, by name:

```python
from optimus9.analysis.jig import Jig, kline, bbline
overrides = {**kline('s45r', 45, k_len=7, rsi=5, stc=7, src='ohlc4'),
             **bbline('s8m',   8, length=6, mult=0.56, src='ohlc4')}
```
Legacy positional tuples still work (`coerce` bridges them) so no existing script broke — but **new code
never hand-builds a tuple.** Reordering the DB columns later is now a safe, mechanical change confined to
one file.

SRP: `LineStore` moved out of `bias_machine` — the bias engine CONSUMES configs, it does not OWN them.

I got this wrong for the whole first day and built the cascade on a transposed r. Joe's call after the A/B:
**keep the transposition** — `k_len 7 | rsi 5 | stc 7` positions the trades better than the chart's `5|7|7`.
We deliberately run a different r from the one on the chart.

## The cascade (promoted 0714)

```
s15m  OOB (es)                                       seam 112s, running min/max since the seam
  s8r already breached (OOB on es)
    OR was predicted when s15m went OOB (latched at the breach)
    OR predicted now
    OR s8Mage OOB on es                              seam 60s, running min/max since the seam
      s8m closer to s8r than at the previous seam
        s1m WAS OOB (es) within 4 eval samples
          AND s1m crosses s1r toward 50               30s grid
Lines: r = k_len 7|rsi 5|stc 7|ohlc4 · m = bb 6|0.56|ohlc4 · Mage = bb 37|0.83|ohlc4.  TFs 15 / 8 / 1.
```

**Knobs, and why each is where it is** (all in `bias_emit.py`):

| knob | value | why |
|---|---|---|
| `seam_mode` | `since` | `hold` samples the rung AT the seam and freezes it — a breach landing mid-bucket is invisible for up to a full seam-width. It dropped the 18:42 and 10:22 turns. `since` = "has it held at ANY point since the seam opened" (Joe's running min/max) and answers within one 30s sample. |
| `seam_div` | 8 | Same staleness fix by a different route. Largely redundant with `since` — that's the point: `since` makes the seam width much less load-bearing. |
| `tf_coarse` | 15 | s20m → s15m. Loses 4 fires, gains 3. Joe: all 4 lost were bad actors, the 1 gained was good. |
| `s1m_oob_mem` | 4 | **`1` (= "s1m IS OOB") NEVER FIRES.** s1m leaves OOB on the very sample it crosses s1r — the two conditions cannot co-occur. 4 catches the 09:22 turn (s1m spent 2 samples climbing out of the band before it took out s1r). |
| `RUNG_MIDLINE_RESET` | True | A rung that has completed an OOB excursion on `es` may not be picked as the apex again until its r crosses 50. Without it the mini's next dive re-predicts a breach the r has just finished making (s19r: 87 min OOB-low, left at 10:26, re-predicted low at 10:47 from 28.4). |

## The ladder-delay entry (Joe 0714)

A cascade fire **LATCHES** — it does not print. Later same-side fires are absorbed by the open latch.

```
at the fire   current_tf = the HIGHEST rung 8..22 predicting on es
              no rung predicting -> PRINT IMMEDIATELY (there is no ladder to delay on)
walk forward  s{current_tf}r coarse-curls  -> a higher rung predicting?  climb, keep walking
                                           -> nothing above?             UNLATCH
PRINT         the next s2Mage turn toward the trade, while s2Mage is OOB on es
CANCEL        s15m breaches the OPPOSING side (stay: s2Mage turns back within 60 bars)
NO TIME CAP. EVER.
```

- **The curl has no OOB condition, deliberately** (Joe). A prediction that never breaches still unlatches on
  its curl. That is the design, not a hole — do not "fix" it.
- **s2Mage here is the ESTABLISHED line** (itf 60s, `bb 37|0.72|hlcc4`), NOT this cascade's uniform s2.
- The print requires s2Mage OOB. This **contradicts the canonical lp-cascade rule** ("s2Mage reverses
  ANYWHERE — boundary-agnostic; do NOT add an OOB requirement"). That rule governs the **gate**; this is the
  **print**. Different consumer, same line. Noted, not resolved.

### The print trigger: coarse curl, NOT wob — decisively

`s2Mage` at `wob=1` reverses **5,846 times in 24 hours** (one every 15 seconds). It is noise at that setting.

| | HI prints | LO prints | worst case |
|---|---|---|---|
| slope-flip, `wob 10` | 2 | 8 | printed the 05:14 short at **16:47** — 11 hours late; dropped 9 of 22 latches |
| **coarse curl, 30s seam** | **7** | **14** | every print within an hour of its fire; dropped none |

[read] **Every s-line curl in the system is a coarse curl with no wob** — `jig.coarse` + `jig.curl` →
`lr_v2._curl_detect`. `wob` exists only in `jig.reversal` (`_mage_rev`), a different producer.

## Jig producers added this session

All live-legal, all in `jig.causal`:

- `seam_prev(name, seam_ms)` — a line's value at the previous seam. Companion to `coarse()`.
- `seam_hold(cond, seam_ms)` — sample a condition AT the seam, freeze it.
- `seam_since(cond, seam_ms)` — has it held at ANY point since the seam opened (the running min/max).
- `grid_any(cond, grid_ms, n)` — held at any of the last n grid samples ("WAS x, and now y").
- `hold_at_start(episode, sample)` — was `sample` true when `episode` began (latched for its life).
- `cross(a, b, grid_ms)` — line-vs-line crossing on a grid. Distinct from `sign()` (vs a boundary) and
  `reversal()` (vs its own slope).
- `reset_since(event, reset)` — has `reset` occurred since the last `event` (the re-fire guard).
- `emit_bgcolor(..., notes=)` — the config block is now baked into the .pine header. A chart that cannot say
  which knobs produced it is a human-error trap.

## The emit — ONE artefact, one labelling scheme

`bias_emit.py` → `transfer/bias_emit.pine`. A separate A/B pine was a human-error trap and is deleted.

```
RED   = HI base print      BLUE   = HI candidate-only
GREEN = LO base print      YELLOW = LO candidate-only
```
Candidate paints first, base over it, so blue/yellow are exactly what the candidate BUYS. Set
`CAND == BASE` when no A/B is in flight and nothing paints blue/yellow.

## What the bias filter has to hit — the target, measured (`leg_cost.py`, 11 days)

**This is the sharpest result of the session.** Labels are hindsight (`jig.score.legs`); it measures the
**ceiling** of a perfect bias machine, not a tradeable rule.

```
                                        n  MAEmed  MFEmed  MFE/MAE  MAE>2
LONGS   outside any macro down-leg     45    0.14    1.53    11.22     0%
        IN down-leg, on a micro UP leg 21    0.06    1.15    19.76     0%   <- the BEST cohort in the book
        IN down-leg, on a micro DOWN   71    1.11    0.45     0.41    23%   <- all the damage

SHORTS  outside any macro down-leg     89    0.90    0.75     0.83    25%   <- all the damage
        IN down-leg, on a micro UP leg 21    0.52    1.60     3.06     0%
        IN down-leg, on a micro DOWN   20    0.01    1.51   275.09     0%   <- near-perfect
```
macro = 3% down-leg · micro = 0.9% leg.

**The two rules are NOT symmetric:**
- **SHORTS want a MACRO gate** — only inside a 3% down-leg. Outside it, 89 of 130 shorts, MFE/MAE 0.83.
- **LONGS want a MICRO gate** — anywhere except a micro-down leg inside a macro-down leg.
- **A blanket "block longs in a bear leg" filter destroys the best cohort in the book** (the 21 retracement
  longs, MFE/MAE 19.76, zero above 2% MAE). Joe called this before the measurement.

## Killed this session — do not re-propose

- **`predict_breach` on slow s-lines as a bias filter.** Swept 2,800 configs (TF 30/45/60/90/120 × 80 r-configs
  × 7 m-mults) over 11 days with a held-out split. **Best held-out score 0.15; best worst-day 0.02**; the lines
  predict on only 4–11% of bars. The single-day fit scored **0.60** and collapsed to **0.00 on three of five
  held-out days** — the +59% failure again, exactly as `ci_initiatives.md` warns.
- **The `cs` series (`cs{tf}b`) as a predict-gate.** `k_len 65` crushes the line onto its mean at every TF —
  zero bars in the engage band across all 16 TFs. At `k_len 34` it produced one clean episode that happened to
  hit the target, which is a coincidence, not a signal.
- **The cs-ladder confluence study** — null, and my build was wrong three ways (curl-while-OOB as the "flip"
  event, no base-rate control, a 120-min follow window wide enough to swallow the event rate). `cs120b` was
  OOB-LOW 34% of the week and OOB-HIGH **0%** — there were no bias flips in the sample to study.
- **s8Mage gravity flip prediction.** 262 episodes / 7 days: P(flip) = 12.2%, and the dominant predictor is
  **duration**, not the LTF. Median MEANDER lasts 0.96 min; surviving 5 min triples P(flip) to 0.333. The
  s2Mage far-OOB signal is real (4.2× at the 20-min mark) but rests on a 9-episode null cell. Joe: parked —
  "doesn't feel right for our volatility".
