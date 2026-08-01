# r-pred — the moment, the cancel, and the clean/dirty flag

**Joe 0730.** The spec for what an r-pred *is*, when it fires, when it is cancelled, when a line may not
produce one, and how the resulting event is labelled. Supersedes every downstream reconstruction of an
"r-pred time" that existed before this date.

---

## 1. The problem this closes

`predict_breach` (`optimus9/compute/breaching_line.py`) emits a **per-bar state** `{+1 hi, -1 lo, 0 none}`.
Nothing recorded **when** the state turned on. Every "r-pred timestamp" in the project was therefore
reconstructed downstream, each consumer choosing its own rule for turning a state array into a moment.

Three different derives were tried on 0730 and gave three different answers for the same event
(`0520 17:58`, `cur_tf` s119):

| derive | value | why it was wrong |
|---|---|---|
| last rising edge before the exhaustion | `0520 16:34` | a re-trigger inside a flickering series; r straddles FH |
| first rising edge since `ea_setup_ms` | `0520 15:52` | correct here by luck; the scope is the setup bar, not the mechanic |
| most recent false→true at/before the exhaustion | `0520 16:34` | identical to derive 1 under a new name |

The fix is to record the moment **at the producer**, and to have the ladder and the recorded moment agree
by construction rather than by coincidence.

---

## 2. `predict_breach` — the only r-pred detector

`optimus9/compute/breaching_line.py:26`

```python
pred_hi = ((k >= fence_hi) & (k < hi) & (anchor_hi >= hi) &
           ((anchor_hi - hi) + tol > (hi - k)))
pred_lo = ((k <= fence_lo) & (k > lo) & (anchor_lo <= lo) &
           ((lo - anchor_lo) + tol > (k - lo)))
return pred_hi.astype(np.int8) - pred_lo.astype(np.int8)
```

- `k` = the r line
- `anchor_hi = max(mini_bb, Major_bb)`, `anchor_lo = min(...)` — the prediction anchor uses **both** BBs
- `HI` = 85, `LO` = 15 (boundary, from `optimus9_system`)
- `FH` = 70, `FL` = 30 (fence, from `rpl_config` — machine-specific, Joe 0727)
- `tol` = 0.0 (spec'd default)
- returns a **state**, not an edge. No timestamp anywhere in the producer

**Called once for the TF stack**, `rpl_walk.py:71`:

```python
P = {TF: predict_breach(E[TF]['r'], E[TF]['m'], E[TF]['M'], HI, LO, FH, FL, 0.0) for TF in TFS}
```

stored as `R.L0['P']`. Every consumer reads that dict. A second call at `rpl_walk.py:94` builds `Ps30`.

**Two conditions must both hold**, and either can be the binding one. Worked example — `s69` bull,
`0520 07:00`, where the chart shows a committed anchor but no prediction fires:

```
              r        m       Mage    anchor | anc-HI   vs  HI-r  | r>=FH70
05-20 07:00  62.78    93.37    67.76    93.37 |   8.37   vs 22.22  |   no
05-20 07:30  64.09   104.82    75.67   104.82 |  19.82   vs 20.91  |   no
05-20 10:21  70.62    99.20    71.37    99.20 |  14.20   vs 14.38  |  YES
```

At 07:00 the fence gate fails (r 62.78 < FH 70) **and** the margin test fails independently
(8.37 < 22.22). 07:30 is the closest approach before 10:21 — short by 1.09 points.

---

## 3. The r-pred RUN — cancelled by the x/r cross

`predict_breach` is a state that can stay true after x has already crossed through r. That kept a spent TF
participating in the ladder long after the move was over.

**Evidence.** s69 dir +1, an r-pred at `0518 20:42` running 8.2 min, still counted as participating at the
`0520 10:26` exhaustion — **37.75 hours later**.

**The run is now a latch:**

- **set** on the `predict_breach` rising edge
- **reset** by the polarity-matched debounced x/r cross already built in `rpl_walk.build_lines`
  - bull: `fx_bull = _wx(x - r, -1)` — x crosses **under** r
  - bear: `fx_bear = _wx(x - r, +1)` — x crosses **over** r
- **set wins on ties** (`_latch_with_reset` uses `last_set >= last_reset`)
- `oob_climb(r)` is **never** cancelled — r out of bounds is a fact, not a prediction

Producer: `optimus9/analysis/jig.py::_latch_with_reset`. The crosses carry `XCPW` (destination debounce)
and `XCPD` (origin dwell) already.

**A/B result (two-stage, 0730).** The cancel swaps **56 of 174** applied events and lifts median `cur_tf`
from 72 to 78. Excursion is a wash: at `swing_detect` 4.00% ratio 2.17 → 2.22; at 2.22% ratio 2.22 → 2.15.
The 28 events dropped score ratio 1.41 and the 25 added score 1.83 — both below the 2.17 pooled, so the
churn is in the weak tail. **Keep it for correctness, not for return.**

---

## 4. The clean/dirty flag on the r line

Prevents an r-pred firing on a line whose breach is spent and has not re-formed. The failure it closes:
r retreating from OOB passes back **down** through the band `FH ≤ r < HI` — the same band a genuine
pre-breach prediction occupies — and re-triggers `predict_breach`.

**State:** one flag per **line and direction** `(tf, dir)`, `tf` ∈ TF22..120, `dir` ∈ {+1 bull, −1 bear}.
198 flags.

| event | condition | scope |
|---|---|---|
| **dirty** | an exhaustion prints **AND** this line is outside its fence | **global** — any exhaustion, any TF, matching bias |
| **clean** | **either** x crosses back through r **or** r returns to the FH/FL fence | **line-local** |

- bull: outside the fence = `r ≥ FH`; clean = x crosses **over** r (`fx_bear[tf]`), **or** r falls back below FH
- bear: outside the fence = `r ≤ FL`; clean = x crosses **under** r (`fx_bull[tf]`), **or** r rises back above FL
- **two clean scenarios, both first-class** (Joe 0731, verbatim for RPL and exhv2):
  1. **x crosses back through r** — a higher TF spent the line early; price swung back and x travelled
     back out to OOB to collect the swing
  2. **r returns to the FH/FL fence**
- both are live in `line_state` (`rearm | back`). Earlier drafts of this doc listed only the first and
  presented fence re-entry as a warm-start special case — that was a documentation defect, not a code one
- the asymmetry is deliberate — the exhaustion is a **system-wide spend signal**, the x/r cross is a
  **per-line recovery signal**. A line that re-armed on its own terms is not held to another timeframe's
  event

**Why the boundary is NOT the dirty trigger.** r frequently never goes OOB:

```
leg   n     r OOB at the exhaustion   r min   r avg   r max
b    205              4               13.0    47.0    89.2
M      1              1               13.8    13.8    13.8
r      2              2               85.1    86.5    87.9
```

**65 of 208** applied exhaustions fire with r **inside** the 30/70 fence; only 7 with r OOB. 205 of 208 are
leg b, which is **x** crossing the boundary and says nothing about r.

**Why fence re-entry alone is not enough.** The live rule ORs both scenarios (`rearm | back`), so dirty
clears on whichever comes first. The measurement below compared the two **in isolation** — neither arm is
what the code runs. It is kept because it shows what each contributes: the fence-only arm suppresses 29% of
episodes and 97% of that is cross-line, so the x/r scenario is what makes the flag usable. **Live
suppression is at most the 3% of the x/r arm, and in practice lower**, because the union clears sooner than
either alone. Measured over 18,334 r-pred episodes from 05-18:

```
clean = r re-enters the fence   -> suppressed  5238 (29%)
clean = x crosses back thru r   -> suppressed   526  (3%)
  RELEASED by the x/r rule      : 4743 of 5238  (91%)
  still suppressed under both   :  495
dirty fraction of tape per line : fence rule med 0.036 | x/r rule med 0.017
```

Under the fence rule, **5,069 of 5,238** suppressions were cross-line — an exhaustion on one TF killing a
prediction on another. Released examples sitting within 0.02-0.19 of `HI = 85`:

```
06-01 19:35:25  s22 dir +1  r 84.95  | had been dirtied by an exhaustion on s45
06-01 19:36:55  s22 dir +1  r 84.98  | had been dirtied by an exhaustion on s45
06-01 19:53:40  s22 dir +1  r 84.81  | had been dirtied by an exhaustion on s45
```

The 495 that stay dirty under both rules are exactly the target: an exhaustion printed, the line is outside
its fence, and x has **not** recovered above r.

**Initial state.** Every line starts **dirty**. At bar 0 a line already outside the fence cannot be told
from a retreat. Cleared by the first recovery of either kind — x back through r, or r re-entering the fence.

**Debounce.** Fence crossings use `cross_wob` at `WOBN` = 9 bars = 45 s at the 5 s grid, like every other
cross in the chain. Raw `r >= FH` flickers exactly as `predict_breach` does — the s69 trace showed three
fragments in two minutes (`10:21:15`, `10:21:50`, `10:23:25`).

**What it gates.** The **predict term inside `rp_matrix`**, so a prediction the machine should not have made
cannot make a timeframe participate. `oob_climb` is untouched, so `dirty` has effect only in the band
`FH ≤ r < HI` (bull) / `LO < r ≤ FL` (bear) — the retreat corridor.

---

## 5. The `2nd x r-pred` label

**Joe 0730:** *"the 'x re-breaching' r-pred event needs to have its own '2nd x r-pred' label. This is
important when we're reviewing `rpl_micro`."* Narrowed: *"'2nd x r-pred' belongs only to the scenario when
x returns to oob after a **higher tf** has created an exhaustion event."*

| label | condition |
|---|---|
| `r-pred` | ordinary |
| `2nd x r-pred` | dirtied by an exhaustion on a **higher TF**, x recovered through r, **and** x returned OOB |
| `2nd r-pred` | as above but x did **not** return OOB between the clean and the episode |

- armed only when `dirtying_tf > line_tf`. A same-TF or lower-TF exhaustion cleans normally but earns no
  label
- `pending` is cleared when the line is re-spent, so each recovery-to-spend span earns its own label
- applied to the **first** r-pred episode after each dirty→clean transition, not to every episode after
- x OOB = `x >= HI` (bull) / `x <= LO` (bear), tested between the clean bar and the episode start

**Counts, full applied set (208 rows):** `r-pred` 169 · `2nd x r-pred` 38 · `2nd r-pred` 1.

---

## 6. Causality and the two-pass

`rp_matrix` needs the flag → the flag needs exhaustion bars → those come from `applied()` → which needs
`rp_matrix`. **Circular in batch.**

**Live has no circularity.** At bar `i` the flag reads only exhaustions with `conf_ms ≤ ts[i]` — those have
already printed. Live is a single forward pass: update the flag from what has printed, then evaluate
participation.

**Batch resolves it by iterating** (`build_rplwalk2.applied_2pass`). Pass 1 runs unflagged; each later pass
feeds the previous pass's confirmed bars into the flag. Only the final pass persists.

```
pass 1: 208 rows, 144 distinct events  (no flag)
pass 2: 208 rows, 147 distinct events | vs prev: -1 +4
pass 3: 208 rows, 147 distinct events | vs prev: -0 +0
  converged at pass 3
```

`line_state` applies each exhaustion **at its own bar index**, so the flag array at bar `i` already depends
only on bars ≤ `i`. At a fixed point the exhaustion set used to build the flag is the set the flag
produces, which is what a forward pass generates incrementally.

**OPEN:** convergence is strong evidence, **not proof**. A bar-by-bar causal simulation that never sees a
future exhaustion is the check that would settle it. It has not been built. If a future tape does not
converge, the batch result is not realizable live and the iteration hides it.

---

## 7. Where it lives

| what | where |
|---|---|
| `predict_breach` | `optimus9/compute/breaching_line.py:26` |
| the TF-stack `P` build | `rpl_walk.py:71` → `R.L0['P']` |
| the x/r crosses | `rpl_walk.build_lines` → `fx_bull` / `fx_bear` |
| the latch | `optimus9/analysis/jig.py::_latch_with_reset` |
| clean/dirty flag | `build_rplwalk2.line_state(tf, dr, exh_ms)` |
| episodes + label | `build_rplwalk2.rpred_episodes` / `rpred_at` |
| participation gate | `build_rplwalk2.rp_matrix(bias, ceiling, exh_ms)` |
| the stamp | `build_rplwalk2.applied()` at the **confirmed** marker bar |
| iteration | `build_rplwalk2.applied_2pass` |
| full episode record | `rpl_walk.persist_rpred` → `rpl_rpred` (opt-in, `RPRED_PERSIST`) |

`RPRED_PERSIST` defaults **False**: `build_lines` runs at **import** and ~20 scripts import `rpl_walk`; an
unconditional write would make every import a DB writer. `RPRED_START` = 05-18 — pre-05-18 is synthetic
warmup, never analysis.

---

## 8. Columns

**`rpl_exh_applied`** (`build_rplwalk2.applied`)

- `ea_rpred_ms` / `ea_rpred_utc` — the r-pred episode live at the confirmed marker bar
- `ea_rpred_end_ms` — episode end. `end < ea_conf_ms` means it had lapsed
- `ea_rpred_bars` — episode length in 5 s bars
- `ea_rpred_label` — `r-pred` | `2nd x r-pred` | `2nd r-pred`

**`rpl_exh_stat`** (`build_exh_stat`) carries the same four as `es_rpred_*`, alongside MFE/MAE at
`swing_detect` 2.22% and 4.00%, the r-OOB breach lifecycle, the bar range and the pivot.

**`rpl_rpred`** (`rpl_walk.persist_rpred`) — every episode, not just the ones an exhaustion used.
`rp_ts`, `rp_tf`, `rp_dir`, `rp_r`, `rp_mini_bb`, `rp_maj_bb`, `rp_anchor`, `rp_margin`, `rp_end_ts`,
`rp_run_bars`, `rp_prev_exh_ms`. `UNIQUE (rp_tf, rp_dir, rp_ts)`.

---

## 9. Measured state, 05-20 → 06-03

87 events, every row with a stamped r-pred.

| label | n | MAE4 | MFE4 | ratio | lead avg | live at exh |
|---|---|---|---|---|---|---|
| `r-pred` | 65 | 3.00 | 5.58 | 1.86 | 56 min | 11 |
| `2nd x r-pred` | 21 | 2.00 | 4.98 | **2.49** | 61 min | 6 |
| `2nd r-pred` | 1 | 5.67 | 13.60 | 2.40 | 37 min | 0 |

- lead range **0 to 356 min**; 17 of 87 had the r-pred run still true at the exhaustion
- **CAVEAT: means only, n=21.** Ratios of 534 and 200 in the sample make the means untrustworthy on their
  own. Medians, p90 MAE and a random baseline are not yet computed. Earlier full-set random was ratio 2.02
  at 4.00%
- **CAVEAT:** the 05-20/05-21 rows all sit inside one 10% leg with MAE near 10 and will be inflating the
  `r-pred` group mean specifically

---

## 10. Open items

- **causal single-pass check** on the two-pass flag (§6). Not built
- **medians / p90 / random baseline** for the label split (§9). Task #20
- **`kc_volume` was never repaired** — the event tape is degenerate across the analysis window. `ei` =
  807,432 of 807,432 bars = 100%. Affects `_px_smooth_evt` and the climb cadence, not `predict_breach` or
  the lines. Task #21
- **04-28 → 05-17 is synthetic** — flat bars 6.6% vs 22.5-36.1%, zero-volume 0.0% vs 3.6-31.7%. It is the
  warmup feeding s109-s120 at the start of the analysis window. Task #22
- **`2nd r-pred`** is my split of Joe's label for the x-never-OOB case. Rename or fold in on request
- **`rpl_walk.py:189`** — `_climb_to_prov`'s `rpred` lambda has the same uncancelled-prediction flaw and is
  **untouched**. It drives `run_chain` and the live flip chain; propagating there is a separate decision
