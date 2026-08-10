# ⚠️ VOID — 0804 19:xx

**Every result below is invalid.** `s6_mode='fallback'` (sweep_s46_exit.py:266) suppresses the s6
exit whenever the leg fires anywhere in the future — that cannot be known at the s6 bar. Re-run
under the causal `'race'` mode, the headline goes from **+0.609/trade, t 2.26** to **−0.019/trade,
t −0.23**, and weeks-positive from 7/8 to 2/8. See ckpt 40 in the working notes.

The only survivor: `sr_x1` still lifts the stream from −0.0976 (t −2.37) to −0.0187 (t −0.23).
Nothing is profitable.

---

# 0804 handover — the 0802 s4/s6 strategy, priced against fees

Full working notes: `docs/260804_exit_permutation_notes.md` (2,290 lines, 38 checkpoints).
This is the short version.

---

## THE HEADLINE

**The exit was never the problem. It was entry selection.**

Every table below is **net of 0.110% round-trip taker** (the repo's own standard —
`replay.py:31 taker_bps=5.5`, `bias_pk_backtest.py:8`, `s30_exit_lever.py:7`), **short side**, and
**one position at a time** (item 15, no pyramiding).

| entry filter | exit | n | net mean | t | weeks+ | ex-top2 | OOS |
|---|---|---|---|---|---|---|---|
| **production** ib>24, s1h>24 | x15M30 H2 +G30 | 184 | +0.178 | 0.87 | 7/12 | +6.97 | +0.078 |
| ib>48, s1h>12 | x15M30 H2 +G30 | 207 | +0.252 | 1.31 | 8/12 | +18.72 | +0.073 |
| **+ sr_x1 >= −36.82** | x15M30 H2 +G30 | **150** | **+0.648** | **3.14** | **10/12** | **+45.15** | **+0.551** |

"ex-top2" = net sum with the two best weeks **removed**. It is the metric that killed every other
claim tonight, so every finding is reported against it.

### the number to actually quote — STRICT WALK-FORWARD

Threshold refit every week on **past weeks only**; nothing from the test week or later touches it.

| p70 walk-forward | n | net mean | t | weeks > 0 |
|---|---|---|---|---|
| **x15M30 H2 filtered** | 83 | **+0.609** | **2.26** | **7/8** |
| x15M30 H2 unfiltered | 143 | +0.101 | 0.47 | 4/8 |
| x22M H0 filtered | 85 | +0.509 | 2.16 | 6/8 |
| x15M H13 filtered | 89 | +0.380 | 2.00 | 7/8 |

All three legs clear **t ≥ 2.0** out of sample at **4–7×** their unfiltered baseline. Excluding the
two best weeks it still earns **+0.367/trade — 3.3× the cost line**.

In-sample t 3.14 → walk-forward t **2.26**; that drop is the selection premium. And **07-16 is a week
where the filter actively underperforms** (−0.029 vs +0.422). It is better on average and in 7 of 8
weeks, not universally.

---

## WHAT SURVIVED, AND THE CONTROL THAT ESTABLISHED IT

| finding | evidence |
|---|---|
| G30 momo gate helps the SHORT side | **104/104** paired leg×H, +0.0734/trade (ckpt 25) |
| the gate is already optimally configured | 84-config sweep; only 3 beat it, by ≤ +0.0165 (ckpt 26) |
| M-crossing legs required (not b, not r) | 3 independent lines (ckpt 23c, 25, 28c) |
| `sr_ib_bars > 48` is an interior optimum | argmax for **5 of 6** exits incl. 2 that LOSE money (ckpt 29) |
| `sr_s1hold` is a real entry filter | monotone on the **unselected bare-s6 exit**, −101.3 → −15.9 (ckpt 28) |
| **`sr_x1` is a dose-response entry filter** | **monotone p0→p70 on 5/5 exits incl. 2 losers** (ckpt 34) |
| the long side does NOT work | negative control: −0.110 / −0.082 (ckpt 32) |

### the dose-response — why `sr_x1` is believed

Net mean by `x1` percentile cutoff. Monotone p0→p70 on every exit, **no reversal anywhere**:

| keep x1 ≥ | s6 bare | x15M30 H2 | x22M H0 | x15M H13 | **x30r H5** |
|---|---|---|---|---|---|
| p0 | −0.122 | +0.252 | +0.232 | +0.159 | **+0.081** |
| p40 | −0.100 | +0.567 | +0.450 | +0.365 | +0.294 |
| **p70** | **−0.072** | **+0.762** | **+0.660** | **+0.518** | **+0.424** |
| p90 | −0.154 | +0.563 | +0.647 | +0.582 | +0.226 |

`x30r H5` is a leg that **never makes money at any setting** — and it still improves 5× across the
gradient. A fluke threshold gives a spike; this is a gradient across five mechanics that share
nothing but the entries.

**The threshold used (−36.82) sits at p50 — conservative.** p60–p70 is materially better.

### what `sr_x1` is

`E[1]['x'][a]` — the **x line (`bb 4|0.37`) at TF1**, read at the entry bar (`build_s46.py:257-261`).
For a short, **higher x1 is better**. Verified causal (ckpt 35).

---

## ⚠️ LOOKAHEAD FOUND IN s46_run

Three columns sit in the **same INSERT** as the causal ones with nothing in the naming to separate
them:

| column | code | |
|---|---|---|
| `sr_ib_bars` | `ibrun[a-1]` | ✅ causal |
| **`sr_dwell_bars`** | `int(b - a + 1)` | ❌ **run length — known only at run END** |
| **`sr_m4_min` / `sr_m4_max`** | `M4[a:b+1]` | ❌ **spans forward to `b`** |

`sr_ib_bars` and `sr_dwell_bars` differ by one character of code (`a-1` vs `b`) and are both
plausible-sounding entry features. **The headline result is unaffected** — the three columns that
cleared the null calibration (`sr_x1`, `sr_ib_bars`, `sr_mg15`) are all causal, and `sr_dwell_bars`
did not clear it. But anyone mining this table will hit the same trap.

**Your call**: a comment at `build_s46.py:257` marking the boundary, or an `sr_post_*` naming
convention so the distinction is visible at the query. Not applied.

---

## WHAT IS DEAD (with the reason, not a shrug)

| mechanic | why |
|---|---|
| the whole 8,320-config exit grid | underpowered ~17× — sd 2.390 vs a 0.110 cost line (ckpt 19) |
| tight TRAIL exit | gross-t artefact; t **+4.46 → −8.27** once fees are priced (ckpt 18) |
| STALL exit (new class, built tonight) | never fires (ckpt 17) |
| swing_detect peak-finder | mathematically identical to TRAIL (ckpt 17) |
| hard STOP, **any** level | breached trades recover to **better than −X** at every level (ckpt 20) |
| entry filter on realised vol | non-monotone (ckpt 19) |
| week-scale regime detection | best \|r\| 0.454 vs a 0.577 bar (ckpt 22) |
| long-bias / beta explanation | 49.8% long; beta contribution −0.039 (ckpt 22) |

---

## THREE CLAIMS I RETRACTED

1. **ckpt 22's short-side numbers** — my code applied no-pyramiding across both sides then subsetted
   shorts. That describes a strategy running longs purely to block positions. Corrected: n 112→184,
   +0.291→+0.178.
2. **x15M30 as THE config** — rank **1 of 208** on the exact metric I selected it with, in a family
   whose median is negative. That is what selection looks like.
3. **`s1hold` interior optimum at 12** — held only for the selected exit. Argmax across six exits is
   96/12/48/48/48/96. Higher `s1hold` is simply better, monotonically.
4. **"Both sides fade the x extreme"** — a story I wrote from `sr_x1` (shorts, HIGH) and `sr_x90`
   (longs, LOW) landing in the same column family with opposite signs. Registered it as a
   falsifiable prediction, tested it, and it **failed**: `sr_x1` LOW on longs is 8/20 and goes
   negative when tightened, while the same operation on shorts is 16/20 and goes up (ckpt 38).

---

## HONEST LIMITS

- one 12-week window, one instrument, one side
- `sr_x1` was chosen from **58 screened columns**. The time-split is genuine OOS evidence for the
  *threshold*; the *choice* of x1 stays selection-exposed. The dose-response (ckpt 34) is the reason
  to believe it anyway.
- the null calibration (ckpt 33) is **ambiguous** — it gives p≈0.014 assuming independent exits, but
  the four exits share trades; under perfect correlation you'd expect 30 of 60 clears by chance and
  we saw 3. I am not claiming the flattering end of that range.
- **`weeks*` = 10** — the stack is only just at the edge of provability with data that exists.

---

## SUGGESTED NEXT (yours to weigh)

1. `sr_x1` at **p60–p70** rather than p50 — the response peaks there, worth +0.11/trade.
2. `sr_ib_bars > 48` rather than `> 24` — established independently of any exit.
3. Everything here is SHORT-side. The long side got its **own independent screen** (ckpt 37), not
   just the short-fitted threshold — `sr_x90` LOW emerged as a candidate with a monotone
   dose-response, but its mirror test failed and it has had no walk-forward. **There is no validated
   long-side filter.** Worth a proper run if you want longs; do not assume symmetry — I tested the
   "fade the x extreme" story that would have unified both sides and it **failed** (ckpt 38).
4. Do **not** run more exit permutations on this window. Ckpt 19's arithmetic says the grid cannot
   resolve 0.11% at n≈250, and ckpt 18 shows exactly how that manufactures a t of +4.46 that is
   really −8.27.
