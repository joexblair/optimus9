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

## THE REASON (Joe, 0709) — applies to every change on this branch

> **The backtest's components are not 100% aligned with the o9-live state events.**

## THE ARBITER (Joe, 0709)

> **Align the backtest's components 100% with the o9-live state events.**

Not PnL. **Alignment.** o9-live is the reference implementation *because it is physically incapable of
look-ahead* — its window ends at now. So the arbiter does not RANK the candidate arms; it says which arm is
**admissible**. Every causal repair wins by definition, because live can only ever do the causal thing.

PnL is therefore a **consequence**, not a criterion: it measures what alignment *costs*. (For A1 it cost
`-11.46%` — i.e. alignment **paid**. See the changelog.)

**Operationally:** the backtest's `v2_mech_events` (arm / stale_exit / rtr / s3s4_gate / trade) replayed over a
window must equal o9-live's logged `o9_state_log` events bar-for-bar. Every disagreement is a defect in the
backtest, not in live.

## BUILD-AS-SHIPPED vs SPEC-AS-WRITTEN

This is the frame for the whole document. `fin_lb=42` bars = **7×30s** and `fin_fwd=12` bars = **2×30s** —
exactly spec §4's lookback and forward tolerance. **The knobs conform. The behaviour does not.**

- **Entry placement.** `fin_unlatch` enters at the *first* `s15a`, where spec §4 says to *walk forward with
  2×30s tolerance for a late line* — i.e. wait for it. Its sibling `fin_gate` already does exactly that with
  `max(j15, j30)`. **The two finishers disagree with each other**, and one of them disagrees with the spec.
- **Gate bypass (deeper).** Spec §4 opens *"Gate open → FINISHERS."* The gate can only open on an arm. But
  `v2_cascade` tries `fin_unlatch` **first, off the arm bar, with no gate reference at all**, and only falls
  through to the gate-dependent `fin_gate` if M1 returns `None`. So **M1 both bypasses and pre-empts the gate.**

So D3 is not "a repair vs the build." It is **build-as-shipped vs spec-as-written**, and the build has been
quietly disagreeing with the spec since 0704. The 20–50s `s15a` lag is understood and correct by design — but
**it is not yet unpacked**, and it will be, after the remaining tests land. Do not close A1 before then.

**Open, and bigger than entry placement:** *should M1 exist at all?* Spec has one finisher mechanism
(post-gate). The build has two, one gate-independent, and it fires first.

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
| B3 | `lr_v2.py:780` `strand_rescue` | ~~Off the live exit path.~~ **CORRECTED 0709: it IS on the live path.** `strategy.py:81` wraps `lr_exit_v2` in `strand_rescue`, and `:92` treats `'strand'` as a real exit. It is not *inside* `lr_exit_v2`, which is what I read, and I stated "off the live path" with confidence on that basis. Whether a rescue can be *executed* live (the SL order already went out at bar `k < T`) is **open and unexamined**. |
| B4 | `lr.py:161` `lr_setups` | Closed `_line` read. v1 machine, not on the `ad` path. Off-path, not wrong. |

### C. Settled — verified clean, do not re-litigate

- **All 21 cascade lines are `value_mode='emerging'`** (DB check, 0709). The closed path does not touch the lr book.
- **The RSI 70/30 rescale is per-bar with fixed constant endpoints** — not a full-series normalisation. Long-standing suspect, cleared.
- **`f_bb_lookahead` / `lookahead_resample` are causal** despite the names — `cummax`/`cummin` *within* the window. The name is a lie in the safe direction.
- **No `.shift(-n)`, `[::-1]`, `center=True`, `bfill`, or `interpolate` anywhere in `compute/`.**
- **Causal forward loops** (act at the first fire, or at `max()` of both fires): `gate_open`, `_finish`, `fin_gate`, `q1_gate`, `lr_exit_v2`, `v2_arm`'s `[::-1]` cap builder.
- **Harness-by-design, forward on purpose**: `lr_walk` (MFE/MAE), `bracket_walk`, `bl_grind` scoring, `find_pivots`, `outcome_walker`, `profit_partition`. Correctly quarantined under `jig.score.*`.
- **`closed` mode is not "future" at the live edge** — it is *stale*. It leaks only in the vectorized backtest, via A4. So the `emerging` mandate buys **backtest honesty**, not live safety.

### E. Execution-layer misalignment — found 0709 while hunting "the bleed"

The arbiter (align components with o9-live) is **necessary but not sufficient**: the backtest and live can agree
on every arm/gate/trade event and still produce opposite PnL, because the divergence lives *downstream* of the
producer. Live nets **−$144 over 13 trades**; `v2_walk` nets **+133.97% over 42d**.

| # | Site | Finding |
|---|---|---|
| E1 | `strategy.py:92` | **Stack-close.** One reversal exit for a side closes that side's **whole stack**. The backtest gives every entry its **own** exit bar. Evidence: `0709_02/03/04` (Buy) all exit at `0.14365786`; `0709_10/11/12` (Sell) all exit at `0.14496807`. **This is not a live bug — Bybit hedge mode has ONE position per `positionIdx`.** You cannot exit leg 3 and hold leg 1. So `v2_walk`'s +133.97% is priced on 2,628 independent exits a real account cannot take. Same family as the ~18% pseudo-hedge premium, different mechanism, on the exit. |
| E2 | `replay.py:35` | Replayed **`v2_walk`**, not `v2_walk_ad`. Live runs `O9_PRODUCER=ad`. Every conclusion ever drawn from `replay.py` described a machine we do not run. **FIXED 0709** (Joe: *"referring to v2_walk is an error on my side"*). |
| E3 | `replay.py:31,46` | `truncate=True` **by default** → `TRUNCATE`s `fx_fill`/`fx_order`/`fx_position`. **Its own `__main__` sets `cfg["database"]="o9_live"`**, so `python3 optimus9/live/replay.py` wipes the live paper account's exchange books. `o9_ledger` survives ⇒ the loop reads *flat* from the (authoritative) exchange and opens on top of trades it still believes it holds; sizing runs off a fictional equity; orphaned ledger rows never close or archive; the recon guardrail reports a mismatch it can never resolve. **Fails silently.** OPEN — needs Joe. |
| E4 | `o9_trade_archive.mae` | `NULL` on all 13 rows. The column exists; the loop never fills it. Blocks any MAE analysis on **live** data. |
| E5 | stack arithmetic | ~~Duplicated in `replay.py` and `risk_stack_dist.py`.~~ **CORRECTED 0709:** `replay.py` does **not** duplicate it — it *calls* `MatchingEngine`. I listed it as a copy from a skim of its docstring. The only hand-rolled mirror is **`risk_stack_dist.py`**. Resolution: `stack_model` extracted (`3004d33`); repoint `risk_stack_dist.py` at it. **Deeper, unresolved:** should `MatchingEngine` itself call `stack_model`, so there is truly one implementation? Touches the paper exchange. |
| E6 | `replay.py:58` | **One-way harness** (`store.open_leg(symbol)`, `idx=None`; *"opposite side while holding — skip"*). Live is **hedge mode** since 0709 and holds two independent legs. `replay.py` cannot represent the machine it is meant to validate. |

**Ownership, for the record** (`app.py:52`, `ledger.py:1`, `store.py:3`): `fx_order`/`fx_fill`/`fx_position` are
**the exchange's truth** and are **authoritative** for the live position — the loop reads its position back from
them. `o9_ledger` is **o9-live's own bookkeeping** (what our bot observed) and drives the UI + sizing. Two
independent books, reconciled against each other. That is the whole point, and it is what E3 destroys.

**The bleed, localised.** Losers match (live −0.94% vs backtest stop 0.90%, SL rates 46% vs 40%). **Winners do
not**: backtest signal-exits average **+1.060%** (MFE p50 1.225%); live's best of 13 is **+0.36%**. Live gives up
≈0.8% per winner — and E1 is the mechanism.

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

### 2026-07-09 · A1 MEASURED — `fin_unlatch` look-ahead **costs** money; the spec placement wins

`fin_unlatch_damage.py` → **217 of 1897 M1 trades (11.4%)** are authorised by a `q30` that fires *after* the
entry bar. Lag: min 1, p50 4, p90 8, max 10 bars (`fin_fwd`=12). Median **20 seconds**. These are the exact
trades o9-live structurally cannot fire (`tk != T` when the late `q30` lands ⇒ `strategy.py:106` never acts).

`fin_unlatch_ab.py` → build vs **spec §4** ("walk forward with 2×30s tolerance for a late line" = enter at the
first `s15a` at/after the authorising `s30a`, i.e. what `fin_gate` already does with `max(j15,j30)`). 42d,
0.20% RT, `lr_exit_v2` raw — **`strand_rescue` deliberately excluded** (register B3: gated on the completed
`SL`, cannot run live, would launder the experiment).

```
ARM A  BUILD  n=2592  net=+122.71%  mean=+0.0473%  win=51.3%
ARM B  SPEC   n=2512  net=+134.17%  mean=+0.0534%  win=51.4%

cohort (ARM A): causal n=2414 mean=+0.0527%  |  CONTAMINATED n=178 net=-4.51% mean=-0.0253%
matched 197:    early  net=-3.99%  mean=-0.0203%  win=51.3%
                late   net=+25.45% mean=+0.1292%  win=57.4%   delta +0.1495%/trade
```

**The mechanism, and it inverts the usual story.** Look-ahead normally inflates a backtest by stealing future
profit. Here the forward `.any()` doesn't buy information — it grants **permission to enter before the
confirmation exists**. It fires on the `s15a` while the `s30a` is still in the future. Those premature entries
are **net-negative**. Wait the 20s for the `s30a` to actually print and the same setups pay +0.1292%/trade at
57.4% win. *The bug wasn't stealing profit; it was entering unconfirmed.*

**Caveats, not to be dropped when this is quoted.**
- The `+11.46%` net gain ≠ the `+29.44%` on the 197. Arm B has **80 fewer trades** (repaired entries either
  dedup into an existing entry bar, or find no `s15a` after `j30` inside `cap`). Both are legitimate
  consequences of the repair, and together they give back ≈+18%.
- Counts differ by basis: 217 raw dirty M1 → 197 matched pairs → 178 surviving A's dedup. Reported separately,
  never blended.
- **One window (42d), one arbiter (per-trade net %).** Worst-window minimax may rank differently. Arbiter is
  Joe's call and is still open.

**Live implication.** o9-live drops all 217 → it has been silently *avoiding* a net-negative cohort. But it is
also forfeiting the **+25.45%** the spec placement captures: ≈5 trades/day at +0.129%/trade, causal, reachable.

### 2026-07-09 · `optimus9/compute/compute_flags.py` — DB → compute flag injection (bootstrap)

**Reason.** `IndicatorComputer` is `"Pure computation. No I/O."` by contract, so it cannot read its own knobs;
and `lr_config()` is a config *reader*, so putting a global side-effect in it would fuse two jobs. One module,
one job: read `lp_config`, set the flag. Joe chose bootstrap over per-entry-point and over threading a param
through ~30 callers, accepting the known cost: **a fresh script that forgets to call `load(db)` silently
inherits the legacy leak.**

**Status.** Module written. `lp_align_close_stamp` **not yet seeded**; `load(db)` **not yet called** from any
entry point. Call sites to be agreed before wiring — that is where the silent-inherit risk actually lands.

---

---

## Part 3 — Experiment log (thesis BEFORE, outcome AFTER)

Process rule (Joe, 0709): **write the thesis before running, write the outcome after.** A prediction recorded
after the fact is not a prediction. This section exists because five findings accumulated across a stretch of
turns without reaching the register — the failure mode that loses a session's knowledge.

### X1 · Q2 — "is `fin_unlatch` harmful?" · RUN 0709

**Thesis (Joe):** *if there is a grouping of high MAE in M1, it might be.* My prior: M1 is the off-spec path, so
I expected it to look worse.

**Outcome — REFUTED, and inverted.**
```
M1 (arm-gated)   n=1747  net=+150.94%  win=52.3%  MAE p50=0.640% p90=0.994%  stopped 39.9%
M2 (post-gate)   n= 881  net= -16.97%  win=50.1%  MAE p50=0.639% p90=1.005%  stopped 40.1%
```
**No MAE grouping.** Distributions identical to 3 d.p.; stop rates match. And the sign inverts: **M1 carries the
entire book; M2 is net-negative.** Joe's premise — *"if the arm is late, we don't want to miss a trade"* — is the
edge. My "should M1 exist" instinct would have deleted the profitable half of the machine. **Do not revisit
without new evidence.**

### X2 · Q1 — where is the bleed? · RUN 0709

**Thesis:** the exit surrenders excursion. **Outcome — CONFIRMED, and localised to E1** (see section E). The
losers match; the winners are cut to ~1/4 by the stack-close.

### X3 · stack-close × governor 2×2 · PRE-REGISTERED, NOT YET RUN

**Design.** One replay, two flags, over 42d on `v2_walk_ad` (the shipping producer):

|  | per-leg exit | stack-close |
|---|---|---|
| **no governor** | current backtest baseline | what live does today |
| **governor (first-leg)** | isolates the governor | the proposed live machine |

`tol` swept `{0, 0.05%, 0.10%, 0.20%, 0.30%}` → winner lands in `risk_config`. Never hardcoded.

**Governor rule (Joe, reference = (a) FIRST leg).** A new leg is allowed iff
`entry_px <= first_leg_px * (1 + tol)` (short) / `>= first_leg_px * (1 - tol)` (long). Per side
(`positionIdx`). Reference resets when the side goes flat.

**My thesis, before running:** the governor matters **more** under stack-close.

**Joe's correction, which sharpens it and which I had wrong:** *that is true only for a bad entry.* Adding into
drawdown **amplifies a good entry** — a short at 0.1000 then 0.1010, with price falling to 0.0990, earns *more*
on the later leg. Martingale cuts both ways.

**Therefore the real thesis:** the governor is a **variance-reducer**. It improves expectancy **only if the
drawdown-added legs carry negative expectancy on their own.** It necessarily caps the upside of good entries. So
the 2×2 is not "does the governor help" — it is **"does entry quality survive the legs the governor would
block?"** If the blocked legs are net-positive, the governor is a *cost* we pay for tail safety, and that
trade-off must be named, not hidden inside a PnL number.

**Falsifiable predictions:**
1. Stack-close alone collapses the +133.97% materially (E1 is real).
2. Governor(tol=0) reduces gross exposure and drawdown in both exit columns.
3. **Unknown, and the point of the experiment:** the sign of governor-on-net under stack-close.

**Outcome (RUN 0709, `x3_stack_governor.py`, 42d, 2628 trades, unit notional, fee 5.5bps/side).**

```
exit model     tol%    net(units)  opens  closes  blocked  depth
per-leg        off        0.514     2628    2628       0     16
per-leg        0.00       0.270     1698    1698     930     14   (-47%)
per-leg        0.05       0.277     1807    1807     821     14
per-leg        0.10       0.287     1920    1920     708     14
per-leg        0.20       0.391     2112    2112     516     14
per-leg        0.30       0.402     2239    2239     389     14   (-22%)

stack-close    off        0.334     2628    1179       0     11
stack-close    0.00       0.216     1699    1179     929     11   (-35%)
stack-close    0.30       0.320     2278    1179     350     11   ( -4%)

stack-close COST vs per-leg (governor off): -0.180 units (-35.0%)
```

1. **Prediction 1 CONFIRMED.** Stack-close costs **35%** of net. E1 is real: a third of `v2_walk`'s edge was
   priced on per-leg exits a single averaged position cannot take.
2. **Prediction 2 REFUTED.** The governor does **not** reduce exposure where it matters: max stack depth under
   stack-close is **11 with the governor and 11 without**. It blocks 930 legs and caps nothing.
3. **My thesis REFUTED; Joe's correction CONFIRMED.** The governor was predicted to matter *more* under
   stack-close. It matters **less** (−35% vs −47%). It destroys net at **every** tolerance in **both** columns,
   and performance improves monotonically as the gate approaches doing nothing. **The blocked legs are
   net-positive after the fees they save.** On this producer, over 42d, adding into drawdown amplifies good
   entries more than it deepens bad ones — exactly as Joe said.

**The pre-registered question — "does entry quality survive the legs the governor would block?" — answers YES.**
Entry quality is high enough that averaging in pays.

**WHAT THIS TEST CANNOT SAY.** It measures the **mean**. The governor is a **variance**-reducer. No equity
drawdown, no worst-episode, no risk-of-ruin. `net` can neither convict nor acquit it. The live 0709 pyramid lost
**$108** in a single episode while this book says such pyramids pay on average — both can be true, and the
governor may be a fair price (~35% of the edge) for surviving the episode that ends the account. **Do not cite
X3 as "the governor is bad."** It says: the governor costs 22–47% of the mean and does not cap depth. The risk
side is unmeasured.

**Follow-up (X3b), required before any governor decision:** equity-drawdown path, max adverse excursion on the
averaged position, worst single episode, and depth under a *compounding* sizer. Also: `depth_max=16` under
per-leg vs `11` under stack-close — stack-close self-caps depth because one exit flattens the side.

**Not a live PnL:** no slippage, no order-book walk, no compounding. Stack semantics + governor only.

---

## Ideas dropped, and why

| Idea | Dropped because |
|---|---|
| "Mangle the kline feed so backtest reads the previous bar's close" | Right *what*, wrong *where*. The tape is read by the sanitiser, bar builder, o9-live collector and TV compare. Worse: the **emerging** path is already causal, so a feed-level shift would shift it too and make a correct path wrong. The leak has one source — the HTF→base mapping. Fix it there. |
| "The whole validated book is suspect" (my claim, ~0709) | Over-called. Pattern-matched on `range(i+1, cap)` without reading what each loop *does* with it. Most are faithful forward simulations. The damage is A1–A4, and it is specific. |
| "73.3% of entries are look-ahead" (my metric) | Measured against the **trade bar** `tk`, which is itself *produced by* the rewritten arm — circular. It scored the harmless branch 99.8% and the damaging branch 0%. Backwards as a damage indicator. The correct yardstick is the **arm bar `i`**, where live must commit. |
| "Remove one clamp and it's a live look-ahead bug" | True but not actionable. A hedge, not a finding. |
