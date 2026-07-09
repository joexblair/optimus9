# Causal look-ahead — register & changelog

Branch `causal/lookahead`. Started 2026-07-09.

**Purpose.** One doc, two halves. Part 1 is the **register**: everything we have judged as needing work, so
nothing is missed. Part 2 is the **changelog**: every change made, with its reason, in time order — including
the ideas we tested and dropped, and why.

**Ground rule for this work.** A forward read is look-ahead **iff it lets the machine act, or refrain from
acting, at a bar earlier than the information it used.** A forward loop that stops at the first fire and acts
*there* is a faithful bar-by-bar simulation, not look-ahead. That discriminator is what separates the confirmed
sites below from the ~16 forward loops that are perfectly causal (`gate_open`, `_finish`, `fin_gate`,
`lr_exit_v2`).

---

## Part 1 — Register

### A. Confirmed look-ahead, on the live producer path

| # | Site | Mechanism | Live consequence | Status |
|---|---|---|---|---|
| A1 | `lr_v2.py:433` `fin_unlatch` | Unordered `.any()` over a box extending `fin_fwd` bars past the unlatch, then entry at the **first** `q15 >= i`. Entry can precede the s30a that authorised it. | Live `cap <= T+1` ⇒ when the late s30a lands, `next(q15)` returns an earlier bar, `tk != T`, and `strategy.py:106` **silently drops the trade**. Backtest books them all. | OPEN |
| A2 | `lr_v2.py:421` `arm_delay` | `kc = next(k in range(i+1, cap) if cond[k])` — **suppresses** the arm at `i` using a future bar. The *placement* at `da` is causal; the *refusal to run the cascade from `i`* is not. | Live can't see `kc`, so it arms at `i` and takes trades the backtest never books. Inverse gap to A1. | OPEN |
| A3 | `greenfield_producer.py:35` `greenfield_walk` | `ep[min(n-1, i+fin_fwd)]` = forward co-occurrence, then entry at `next q15 >= i`. Same bug as A1. | Docstring claims *"NO forward scan… window-invariant (causal)"*. It isn't. Dangerous because it is the module written to **replace** A2. | OPEN |
| A4 | `indicator_computer.py:43,78` `resample`/`align_to_base` | `resample` stamps each bar at window-**open** while aggregating the **whole** window; `align_to_base` maps a mid-window base bar onto that still-forming bar. Up to one full TF of future (30 min on the 30-min gate masks). | Backtest-only: live reads index `-1`, where the aggregate covers `<= T`. Affects `value_mode='closed'` lines and every closed-bar gate mask. | **SEAM BUILT, OFF** — `92d0fe5` |

### B. Latent — not currently firing, but loaded

| # | Site | Issue |
|---|---|---|
| B1 | `bias_machine.py:78` vs `bl_detect.py:237` | The `value_mode` default **disagrees with itself**: `closed` in one module, `emerging` in the other. A new line inherits look-ahead or not depending on which reads it. Nobody chose this. |
| B2 | `lr_v2.py:226` `s30M_wob` | Reads a closed `_line`, bypassing `BiasWindow.line()`. **Zero callers** — dead. A trap for whoever rewires it. |
| B3 | `lr_v2.py:780` `strand_rescue` | Harness-only by construction (gated on the completed `x[6]=='SL'`). Off the live exit path — but **exit_v2's headline `-0.020 → +0.208` rests on it.** That number cannot be earned live as written. |
| B4 | `lr.py:161` `lr_setups` | Closed `_line` read. v1 machine, not on the `ad` path. Off-path, not wrong. |

### C. Settled — verified clean, do not re-litigate

- **All 21 cascade lines are `value_mode='emerging'`** (DB check, 0709). The closed path does not touch the lr book.
- **The RSI 70/30 rescale is per-bar with fixed constant endpoints** — not a full-series normalisation. Long-standing suspect, cleared.
- **`f_bb_lookahead` / `lookahead_resample` are causal** despite the names — `cummax`/`cummin` *within* the window. The name is a lie in the safe direction.
- **No `.shift(-n)`, `[::-1]`, `center=True`, `bfill`, or `interpolate` anywhere in `compute/`.**
- **Causal forward loops** (act at the first fire, or at `max()` of both fires): `gate_open`, `_finish`, `fin_gate`, `q1_gate`, `lr_exit_v2`, `v2_arm`'s `[::-1]` cap builder.
- **Harness-by-design, forward on purpose**: `lr_walk` (MFE/MAE), `bracket_walk`, `bl_grind` scoring, `find_pivots`, `outcome_walker`, `profit_partition`. Correctly quarantined under `jig.score.*`.
- **`closed` mode is not "future" at the live edge** — it is *stale*. It leaks only in the vectorized backtest, via A4. So the `emerging` mandate buys **backtest honesty**, not live safety.

### D. Open design questions (Joe's call, not resolved)

| # | Question | Options |
|---|---|---|
| D1 | Big leg prints while the arm is live but the cascade hasn't traded | (a) suspend → wait s5Mage reversal → re-arm · (b) cancel outright · (c) suspend only if the gate hasn't opened |
| D2 | Arm retirement (`cap`'s expiry job) | opposite-s5m-breach (current) **vs** die at s3s4 gate-open (Joe's idea). Spec §1 says *"persists until the gate resolves"* — today it can gate twice. |
| D3 | `fin_unlatch` repair | Enter at `max(entry, j30)` — matches `fin_gate` and spec §4's *"walk forward with 2×30s tolerance for a late line"*. This is a **behaviour change**, not a bug fix. |
| D4 | Verdict placement | (a) rewrite each scan as per-bar state · (b) re-window the harness per bar (zero engine change, but naively quadratic over 725k bars) |

**Sequencing constraint.** D2 cannot be measured on a book whose arms were placed with future data. **A2 lands before D2.**

---

## Part 2 — Changelog

### 2026-07-09 · `92d0fe5` · `resample` emits `close_ts`; `align_to_base` gains `ALIGN_CLOSE_STAMP` (default **off**)

**Reason.** `align_to_base`'s docstring already promised *"each base bar sees the last completed source bar.
Mimics Pine Script `request.security()`."* The code did the opposite. The disagreement between the stated
contract and the behaviour is the bug — not the aggregation.

**What changed.**
- `resample()` emits `close_ts = bar_open + target_seconds` — gap-safe (uses the floored `bo[starts]`, not
  `ts[starts]`, which can exceed the bar open when 5s bars are missing).
- `align_to_base()` aligns on `close_ts` when `IndicatorComputer.ALIGN_CLOSE_STAMP` is set, else legacy
  `timestamp`. **Default `False` ⇒ bit-identical.** Suite green (191 pass; 2 `analyze_manager` centroid
  failures pre-exist on `main`).
- `IndicatorComputer` stays I/O-free by contract — the flag is **injected**, never read from the DB inside it.

**Not the fault:** `'close': c[last]` is the *correct* close of an HTF bar. Changing it would break the
definition of a closed bar. The fault is pairing that whole-window aggregate with a bar-**open** stamp.

**Evidence.** Synthetic 5s tape → two 60s windows:

| `base_ts` | OFF | ON |
|---|---|---|
| 0 | 11.0 ← close of a bar ending at `ts=55000` (**11 bars of future**) | `NaN` — nothing has closed yet |
| 60000 | 23.0 | 11.0 — the last **completed** bar |

**SRP note.** Three scripts already hand-rolled this stamp (`bias_pk_worst.py:37`,
`bias_pk_emit_weeks.py:41`, `bias_pk_validate.py:45` all do `timestamp + tf_ms`). `close_ts` belongs in
`resample`, which owns the timeframe.

**A/B snapshot (`v2_walk_snapshot.py`, 42d, window pinned 1h back so the collector can't move the tape).**
Prediction stated before running: *zero delta, because every cascade line is `emerging` and never touches
`resample`+`align_to_base`.* Result:

```
BEFORE ALIGN_CLOSE_STAMP=False  bars=760320  entries=2632
AFTER  ALIGN_CLOSE_STAMP=True   bars=760320  entries=2632
1. LINE ARRAYS: all 21 cascade lines BIT-IDENTICAL
2. ENTRIES:     identical 2632 | only-BEFORE 0 | only-AFTER 0 | side flips 0
```

**A4 is confirmed gate-mask-only.** The lr book does not depend on the closed path. Flipping the stamp is
therefore safe for the cascade — and the bny30M/bny30p gate-sweep numbers, which were tuned on the leaked
masks, still owe an A/B.

*First attempt raced:* with a live `now`, the collector inserted a 5s bar between the two window builds
(760319 vs 760320 bars) and the shape check fired a phantom "CHANGE DETECTED". Entries agreed even then.
Pin the window when A/B-ing anything against a growing tape.

### 2026-07-09 · `optimus9/compute/compute_flags.py` — DB → compute flag injection (bootstrap)

**Reason.** `IndicatorComputer` is `"Pure computation. No I/O."` by contract, so it cannot read its own knobs;
and `lr_config()` is a config *reader*, so putting a global side-effect in it would fuse two jobs. One module,
one job: read `lp_config`, set the flag. Joe chose bootstrap over per-entry-point and over threading a param
through ~30 callers, accepting the known cost: **a fresh script that forgets to call `load(db)` silently
inherits the legacy leak.**

**Status.** Module written. `lp_align_close_stamp` **not yet seeded**; `load(db)` **not yet called** from any
entry point. Call sites to be agreed before wiring — that is where the silent-inherit risk actually lands.

---

## Ideas dropped, and why

| Idea | Dropped because |
|---|---|
| "Mangle the kline feed so backtest reads the previous bar's close" | Right *what*, wrong *where*. The tape is read by the sanitiser, bar builder, o9-live collector and TV compare. Worse: the **emerging** path is already causal, so a feed-level shift would shift it too and make a correct path wrong. The leak has one source — the HTF→base mapping. Fix it there. |
| "The whole validated book is suspect" (my claim, ~0709) | Over-called. Pattern-matched on `range(i+1, cap)` without reading what each loop *does* with it. Most are faithful forward simulations. The damage is A1–A4, and it is specific. |
| "73.3% of entries are look-ahead" (my metric) | Measured against the **trade bar** `tk`, which is itself *produced by* the rewritten arm — circular. It scored the harmless branch 99.8% and the damaging branch 0%. Backwards as a damage indicator. The correct yardstick is the **arm bar `i`**, where live must commit. |
| "Remove one clamp and it's a live look-ahead bug" | True but not actionable. A hedge, not a finding. |
