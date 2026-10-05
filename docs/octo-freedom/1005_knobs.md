# 1005 — the knob register for the lazy-g routing + scoring chain

Every number the 1005 chain depends on, with where it came from and who owns it. Results and the
measurements behind each choice: `1005_scored_outcomes.md`. Runnable chain: `1005_scoring/`.

Read the OWNER column before changing anything. **JOE** = his ruling, do not move it. **MINE** = a
decision I made and named; it is a proposal, not a fact. **BANKED** = already in the machine.

## 1. ROUTING — mtd, then branch D

| knob | value | owner | source |
|---|---|---|---|
| mtd lines | g5 / g15 / g30 / ws1 Mage | JOE | 1004 mtd spec |
| mtd step-1 lookback | **48 bars = 4 min** | MINE | measured knee, 09-25: 4 min captures 39 of 39 signals, nothing past it adds one; 2 min caught 29 of 39. `1003_lazy_g_spec.md` |
| mtd extrema test | **same-dr**, both the lookback and the forward walk | JOE | 1004, *"that's my mistake - the extrema test is same-dr"* + *"yes same-dr for the forward walk too"* |
| mtd step-2 read bar | the step-1 extrema | JOE | 1004 rollback, *"you're absolutely right. rollback"* |
| mtd per-line tolerance | g5 0 · g15 **3** · g30 **6** · ws1 0 bars (= 0 s / 15 s / 30 s / 0 s) | MINE | Joe 1004 *"your call on the #2 window size"*. Anchored to CONSTRUCTION — each line's own bar width, the most its close can lag a 5 s close. A 5-120 s sweep showed no stability knee |
| mtd forward-walk reversal | `lr_v2._mage_rev`, rev_wob **2** | BANKED | v3_config |
| `LAZY_G_D_GAP_MAX` | **4** skipped TFs in the ex-fence block | JOE | 1004, explicitly arbitrary, *"I'm choosing 4 as an arbitrary knob (add to spec for sweeping)"* — NOT YET SWEPT |
| branch D ladder | ws1..ws12 r, ws1 claims its floater value when the divergence test fires | JOE | 1004, *"the floater, ie the moment when ws1r completed its purpose"* |
| branch D band test | higher TFs have no claim unless they print between ws1r and the weakest ex-fence r | JOE | 1004 answer 3 |
| branch D grade | Mage net ws1->ws12. AWAY from dr = with-trend · TOWARDS = against-trend | JOE | 1004 |
| warm-up | **2160 bars = 3 h** before any printed span | JOE | 1004 ruling |
| `rig.DR` | per bar, rebuilt from `sweep_v3_signal.Rig.__init__:99-106` | JOE | 1004, *"the report's rows must honour rig.DR"* |
| `STALL_N` | 6 | BANKED | Joe 0814 |
| traj | `rule2_trajectory.trajectory`, block 60 bars, min_bars 24, min_travel 0.0 | BANKED | wsf_dtf_v3_spec s22, Joe 0924 |
| fences | oob **15/85** · Mage 25/75 · rule#1 27/73 · r-momo 17/83 | BANKED | four separate fences, not one |

## 2. SCORING

| knob | value | owner | source |
|---|---|---|---|
| side rule | **dr-bias** (dr +1 = SHORT, dr -1 = LONG). The stage-2 flip is OFF | MEASURED | the flip costs **-2.508 pp over 9 days** / -0.021 per trade. Wins 4 days, loses 5. `1005_scored_outcomes.md` s5 |
| swing_detect | **0.70 %** | MINE | the separation knee: CONF vs NOT-CONF MAE median 0.258 / 1.622 = 6.3x, widest of ten points. **DEPARTS from the banked 1 %** (`docs/linelab_spec.md` s0, "Locked by Joe") |
| exit | the next favourable swing pivot, swing-to-pivot | BANKED | `docs/linelab_spec.md` s0 |
| MAE / MFE | `max(0, adverse)` over entry -> that pivot. Pre-entry adverse belongs to a different leg | BANKED | same |
| stop | **0.80 %** of entry | JOE | 1005, *"apply a 0.7% and 0.8% stop"*. 0.80 beats 0.70 by **+9.186 pp** on the dr-bias set. **The LIVE machine still runs `mae_cap` 0.70** (`wsf_trade_config` v3) — the two differ |
| drag | **0.1975 %** per trade = 2 x 5.50 bps taker + 8.75 bps slippage at 22,000 coins | BANKED | `docs/strat-3-r-oob/spec.md:77`. ONE orderbook measurement applied flat |

## 3. SIZING

| knob | value | owner | source |
|---|---|---|---|
| pyramid | **NO CAP** | JOE | 1005, *"drop the pyramid max"*. Measured max **4** concurrent legs over 9 days |
| start balance | **888.00 USD** | JOE | 1005 |
| risk budget | **2.0 % of equity per entry** | MINE | the classic 2 %-risk convention. Return and drawdown are both near-linear in it — **no knee**, so it is a convention, not an optimum. Swept 0.5 to 10.0 in s7 |
| worst case per trade | **0.9975 % of notional** = stop 0.80 + drag 0.1975. Known BEFORE entry | DERIVED | it is the stop, not an estimate |
| leverage | `risk_i = 2.0 / (n_live + 1)` · `lev_i = risk_i / 0.9975` | MINE | alone 2.00x · 1 live 1.00x · 2 live 0.67x · 3 live 0.50x. Holds total open risk at 2 % with concurrency unbounded |
| alternative sizing | constant 2 % per leg, the sneaky-1 precedent (`sneaky_trade_1_handover.md:174`) | BANKED | banked in `lazyg_compound` as `lc_size_mode='constant'` |
| position size in coins | **NOT SET** | JOE | MVP2 item 4. Every figure is a percentage or a dollar derived from the $888 start |

## 4. WHERE IT IS BANKED

| what | where |
|---|---|
| per-trade compound P&L, both sizing modes | MySQL **`lazyg_compound`**, 151 rows x 2 modes. Unique key `uq_lc` carries side_rule, stop, swing, cost, pyr_max, risk_pct, size_mode, start_usd, open_ms — every knob that changes a row |
| the runnable chain | `1005_scoring/` — `score39.py` (mtd + D + scoring), `flip39.py`, `ninedays.py`, `fc7.py` (bootstrap), `stops_pyr.py`, `compound_db.py` (the DB bank), `lineage.py` (the baton defect) |
| the 298 octo-sig inputs | `1005_scoring/octosig/2026-09-{25..30}.out`, `2026-10-0{1,2,3}.out` + `run.sh` |
| results and every measurement | `1005_scored_outcomes.md` |

## 5. OPEN — NOT RULED

| item | state |
|---|---|
| `neither` = BLOCK | +3 on 09-25, **-1** on 09-26. Does not hold |
| `no fire` = BLOCK | 0 on both days |
| D empty ex-fence block = BLOCK | +1 on 09-25, **-5** on 09-26. Inverts hardest |
| the stall-contiguity gate | Joe's own 07:57 verdict mechanism. He has not been able to name the knob: *"3 TFs stalled inside of a 4 TF window to be contiguous ... this needs a sweep - I can't think how to describe the knob(s)"*. UNBUILT |
| the baton lineage rule | `baton.py:125` is `rider = max(c)` — NO lineage. 61 of 139 passes are illegal at +-3 TF, 41 have no legal successor at all. Three values open: the hop window, what happens with no legal successor, whether a downward pass is a pass. `1005_scored_outcomes.md` s5 |
| `LAZY_G_D_GAP_MAX` 4 | Joe's, explicitly arbitrary, flagged for sweeping |
| the stop sweep | 0.70 vs 0.80 is **two points, not a sweep**. The direction says the live 0.70 may bind early; it does not locate a knee |
| branch B and C agree/disagree direction | unruled |
| mtd population B | the ws1mage-rev + ws1r oob events walked bar by bar. NEVER RUN |
| held-out days | **NONE.** All 9 days are in-sample for every knob above |

---

## 6. 1005 OOS — 10-04, THE FIRST HELD-OUT DAY. IT MOVES TWO CONCLUSIONS.

Added 2026-10-05 after Joe reassigned the OOS run to this session. Built: `build_tape.py 2026-10-05`
(98 override lines, 63.4 s, the tape reused from the recon session's build) ->
`report_leash_walk.py --day 2026-10-04 --tape-end 2026-10-05` -> 30 `R|` rows, 27 in the day window.

Every knob in sections 1-3 UNCHANGED. The chain is now parameterised so the OOS runs the identical
code path: `LG_DAYS`, `LG_TAPE_END`, `LG_TABLE`.

| basis | trades | total net % | mean net % | winners | stopped |
|---|---|---|---|---|---|
| 10-04 confluences, FLIPPED (ninedays `net`) | 11 | **+10.398** | **+0.945** | 10 of 11 | 1 |
| 10-04, every octo-sig ungated | 27 | — | +0.465 | — | — |

- +0.945 mean is the **best of any day in the set**. n = 11. One day.
- banked to **`lazyg_compound_oos`** (11 rows x 2 sizing modes). `lazyg_compound` stays in-sample
  only and was verified unchanged at 302 rows before and after.

### ON THE RECOMMENDED dr-bias BASIS THE HELD-OUT DAY LOSES MONEY

| sizing | trades | start $ | final $ | return % | max DD % |
|---|---|---|---|---|---|
| shared budget | 11 | 888.00 | **885.27** | **-0.31** | 4.03 |
| constant per leg | 11 | 888.00 | 911.85 | +2.69 | 6.27 |

| 10-04 | notional traded $ | gross P&L $ | drag paid $ | net P&L $ | drag as % of gross |
|---|---|---|---|---|---|
| 11 trades | 12,667.36 | +22.29 | **-25.02** | **-2.73** | **112.2 %** |

**The day's gross edge did not clear its own drag.** $25.02 paid against $22.29 of gross.

### THE FLIP IS NOT DECIDED — section 5's correction was itself an over-read

| day | wt rows | dr-bias total net % | flipped total net % | delta |
|---|---|---|---|---|
| 09-25 | 12 | +0.800 | +10.378 | **+9.578** |
| 09-26 | 11 | -0.787 | +5.756 | **+6.543** |
| 09-27 | 15 | +0.816 | +4.690 | **+3.873** |
| 09-28 | 5 | +3.702 | -0.895 | **-4.597** |
| 09-29 | 20 | +4.055 | +7.945 | **+3.891** |
| 09-30 | 10 | +2.629 | -0.623 | **-3.252** |
| 10-01 | 13 | +7.066 | -1.232 | **-8.298** |
| 10-02 | 17 | +8.748 | +4.242 | **-4.506** |
| 10-03 | 14 | +5.353 | -0.387 | **-5.740** |
| **10-04 HELD OUT** | 7 | **-1.066** | **+7.146** | **+8.212** |
| **10 days** | 124 | +31.316 | **+37.020** | **+5.704** (+0.046/trade) |

- **the flip wins 5 days and loses 5.** Over 9 days it totalled **-2.508**; adding one held-out day
  flips the total to **+5.704**.
- single-day deltas run **-8.298 to +9.578**. The 10-day total is inside one day's swing of zero.
- so: NOT "the flip holds" (my 2-day read) and NOT "the flip costs 2.5 pp" (my 9-day read). The
  quantity's day-to-day spread exceeds its own total. **Undecided, and it needs more days, not a
  verdict.** See [[day-is-the-block-unit]].

### THE TEN DAYS TOGETHER — 9 in-sample + 1 held out, labelled as such

| | octo-sig | CONF | BLOCKED | OPEN | CONF total net % | CONF mean | winners | stopped | ungated mean |
|---|---|---|---|---|---|---|---|---|---|
| 9 in-sample | 298 | 151 | 31 | 116 | +37.148 | +0.246 | 97 of 151 | 44 | +0.206 |
| **10 days** | **325** | **162** | 36 | 127 | **+47.546** | **+0.293** | 107 of 162 | 45 | **+0.227** |

The 9 in-sample days reproduce BYTE-IDENTICALLY on the 10-05 tape (checked row by row), so the
tape-end shift does not move the lines and the 10-day aggregate is legitimate.

### TWO CORRECTIONS TO SECTION 5

1. **the longest consecutive losing run is 6, not 3.** The 3 was the FLIPPED basis over 9 days. On
   the dr-bias basis over 10 days it is **6**. At 2.228x that is 11.42 % of equity; at the live
   13.595x it is **54.19 %**.
2. a new boundary case now handled: **UNRESOLVED** rows, where no favourable swing pivot exists after
   the entry inside the tape. 3 of them on 10-04 (23:04:15, 23:15:00, 23:16:30) because the tape ends
   10-04 23:59:55. They are EXCLUDED and COUNTED, never scored 0 — inventing an exit at the tape end
   would be a truncation. The 9 in-sample days have 0, because that tape ran a day past 10-03.

---

## 7. BAKED 1005 — JOE'S SIZING AND STOP RULINGS

These were MINE as proposals. Joe ruled on both, so they are now **JOE** and not to be moved by a
sweep.

| knob | OLD | **BAKED** | Joe's words |
|---|---|---|---|
| risk per trade | 2.0 % (mine, a convention) | **1.5 %** | *"I agree with you"* to the 1.5 % / 1.67x recommendation |
| stop | 0.80 (scoring) / 0.70 (live) | **0.95** | *"bake the 0.95"* after the 0.70->1.40 scan |
| leverage | derived | **1.31x** = 1.5 / (0.95 + 0.1975) | the two are COUPLED: `lev = risk / (stop + drag)`. Move one, recompute the other |

Baked into `1005_scoring/compound_db.py`, `ninedays.py`, `sweep.py`, `upstream_run.py`.

### WHY 0.95 — the scan, 0.70 to 1.40 at 0.05, risk 1.5 %

| basis | best stop | figure |
|---|---|---|
| **held-out dollars (7 random days)** | **0.95** | **$1,186.07** |
| **robust per-day growth** | **0.95** | **1.042213** |
| in-sample dollars | 0.80 | $1,655.73 — overfit |
| raw total net % | 1.20-1.40 | keeps climbing, paid for with leverage you must give up |

Against the live 0.70, 0.95 is better on every axis at once: FIT +41.842 -> +51.933 %, TEST +14.608
-> **+31.339 %** (more than double), TEST DD 13.36 -> **7.38 %**, stop-outs 51 -> 36 (FIT) and 44 ->
27 (TEST), and **zero trades lost** - n is 162/110 at every stop, because the stop changes outcomes,
never which signals fire.

Dollars peak at 0.95 while total % climbs to 1.40 because at fixed risk a wider stop forces LOWER
leverage (1.67x -> 0.95x). Past ~1.00 you buy total with position size and lose on net.

### THE RESULT AT THE BAKED CONFIG — `lazyg_compound_v095`, 10 FIT days

| sizing | trades | start $ | final $ | return % | max DD % | peak lev | min lev | mean lev |
|---|---|---|---|---|---|---|---|---|
| shared budget | 155 | 888.00 | **1,517.84** | **+70.93** | **7.52** | 1.31x | 0.33x | 1.11x |
| constant per leg | 155 | 888.00 | 1,677.95 | +88.96 | 8.89 | 1.31x | 1.31x | 1.31x |

Drag: **$384.00 on $1,013.84 gross = 37.9 %**, against $629.84 of net growth.

### THE LEVERAGE LADDER — tied to held-out evidence, not to equity

| held-out days cumulatively positive | risk/trade | leverage at stop 0.95 |
|---|---|---|
| now (7 days, +0.1328 %/trade pre-bake) | **1.5 %** | **1.31x** |
| 20 | 2.0 % | 1.74x |
| 40 | 2.5 % | 2.18x |
| 60+ | 3.0 % | 2.61x |

What would move it DOWN: OOS mean below +0.05 %/trade -> 1.0 %. A losing run longer than 8 -> recut
from the new run length. A measured slippage worse than 0.1975 % at real size -> it eats the edge
directly, drag already being 37.9 % of gross.

### THE LIVE CONFIG IS NOT CHANGED BY THIS

`wsf_trade_config` v3 still carries `mae_cap` **0.70** and `o9_control` still carries fixed 66,000
coins. Both are the o9-live session's to deploy, and the one-line change plus Joe's ruling have been
handed to them. **At the live 13.595x, five consecutive worst-case stops halve the account** - that
is the number to fix first, ahead of anything in this document.

## 8. THE REFERENCE DIFF — the recon session's optimisation is clean, and MY data had a hole

Run after `39e421d` landed: re-walked all 17 days at the current knobs and byte-compared the `R|`
rows against the signals banked before it.

| result | days |
|---|---|
| IDENTICAL | **16 of 17** |
| differed | 10-03 only: old 27 rows, new 32 |

**The 5 extra rows are MY tape boundary, not their code.** Proved by walking 10-03 on the NEW code at
the OLD `--tape-end 2026-10-04`: **27 rows, matching the banked file exactly.** Their bit-identical
claim is verified on 17 of 17 days once the tape end is held constant.

**THE HOLE IT EXPOSED IN MY OWN DATA:** `octosig/2026-10-03.out` was built on the 10-04 tape, where
10-03 was the tape's LAST day. Five signals after 21:07 never emitted for want of forward bars to
resolve. Every figure published before this that includes 10-03 was built on **27 signals when there
are 32**. 10-03 has been rebuilt on the 10-05 tape and the trade count moves 151 -> 155.

**AND IT IS STILL TRUE OF 10-04.** 10-04 is the last day of the 10-05 tape, so it is truncated the
same way - the 3 UNRESOLVED rows in section 6 are the symptom. 10-04 cannot be made whole until
10-05 closes and a 10-06 tape is built. Stated, not corrected.

## 9. WHERE THE UPSTREAM KNOBS ACTUALLY LIVE — my census was looking in the wrong place

`rig.C` holds **39 numeric knobs** and it is what the Rig AND the walk both read. The Jig module
constants I censused in `1005_knob_census.md` are mostly NOT on the octo-sig path:

    band_dtf_hi 23      band_dtf_lo 13     band_wsf_hi 12    band_wsf_lo 1     block 60
    boundary_xwob 4     confirm_lag_s 180  count_min 2        dr_latched 1      dwell 3
    dwell_min_per_tf 1  fence 50           fence_hi 75.0      fence_lo 25.0     gap_fill 1
    grid_s 5            lookback_s 240     mage_dwell 12      momo_bank_version 1
    momo_fence_r 17     momo_slope_min 0.4 momo_span_min 10   momo_xwob 4       oob_hi 85.0
    oob_lo 15.0         r_wob 3            return_bars 3      rev_wob 2         ride_tf_hi 4
    stall_n 6           support_min 23     tf_hi 23           tf_lo 1           threemage_dr 0
    tp_lookback_min 4   wmt_tf_hi 12       wmt_tf_lo 2        xrace_hold 5      xwob 5

- the walk passes `dwell=int(rig.C['dwell'])`, `rev_wob=int(rig.C['rev_wob'])`,
  `hold=int(rig.C['boundary_xwob'])` EXPLICITLY, so neither the jig module constants nor the
  function's `__defaults__` reach them. Two failed patch attempts before this was found.
- `rig.C` is a plain dict on the CACHED Rig, so a cell mutates it with no reload. Per cell stays
  17 days x 17.4 s = 5.1 min.
- `momo_slope_min` appears in BOTH `rig.C` (0.4) and `momo_config` v1 (1.2). Which one the walk
  honours is **unmeasured** and must be settled before either is swept.

## 10. MOMENTUM — WHICH VALUE IS IN EFFECT. Joe 1005: "we're only using momentum in octo-freedom and lazy-g"

**0.4 is in effect. The 1.2 in `momo_config` v1 is overwritten before every verdict.**

`walk_mom_models.momentum_true` (the only momentum entry the walk calls, via `mom_at`):

```python
b = dict(bank); b.update({q: cfg[q] for q in
        ('momo_slope_min', 'momo_slack_ref', 'momo_r2_min', 'level_slack', 'momo_seam')})
with momo_config(b), momo_window(SPAN_MIN):
```

- `bank` is `rig.BK[tf]` = `momo_bank(db, tf, version=1)` (`sweep_v3_signal.py:91`)
- `cfg` is **`walk_mom_models.WS1_CFG`** = `{momo_slope_min: 0.4, momo_slack_ref: 0.4, momo_r2_min: 0.7, level_slack: 13.9, momo_seam: 'off'}`
- so those 5 keys come from WS1_CFG and the bank's values for them are discarded
- `momo_window(SPAN_MIN)` with **`SPAN_MIN = 10`** (`walk_mom_models.py:60`) also overrides the bank's `momo_window_min` 60

### MEASURED, not read — the A/B that settles it, 10-02

| what was moved | 10-02 signals | verdict |
|---|---|---|
| baseline | 43 | — |
| `rig.C['momo_slope_min']` 0.4 -> 99.0 | 43 | **UNCHANGED — never read by the walk** |
| `rig.BK[t]['momo_slope_min']` 1.2 -> 99.0, every TF | 43 | **UNCHANGED — overwritten by WS1_CFG** |
| `WS1_CFG['momo_slope_min']` 0.4 -> 0.1 | **44** | **MOVED** |
| `WS1_CFG['momo_slope_min']` 0.4 -> 1.2 | **39** | **MOVED — adopting momo_config's value LOSES 4 signals** |
| `WS1_CFG['momo_slope_min']` 0.4 -> 3.0 | **38** | **MOVED** |

And momentum is load-bearing, not decorative: forcing `momentum_true` to a constant kills the day
entirely — True -> 0 signals, False -> 0 signals, both with 0 MECH bars. The mechanic needs a MIX of
verdicts across timeframes, so it is a relationship between TFs, not a threshold on one.

### THE MOMENTUM KNOB CENSUS FOR octo-freedom, corrected

| knob | value | store | status |
|---|---|---|---|
| `momo_slope_min` | **0.4** | `WS1_CFG` | LIVE, swept |
| `momo_slack_ref` | **0.4** | `WS1_CFG` | LIVE, swept |
| `momo_r2_min` | 0.7 | `WS1_CFG` | LIVE, swept (same value as the bank's, so no conflict) |
| `level_slack` | 13.9 | `WS1_CFG` | LIVE, swept (same as the bank's) |
| `momo_seam` | 'off' | `WS1_CFG` | LIVE (same as the bank's) |
| `SPAN_MIN` | **10** | `walk_mom_models` | LIVE, overrides the bank's `momo_window_min` 60 |
| `momo_step_min` | 5 | bank | LIVE, from `momo_config` v1 |
| `momo_fixed_samples` | 21 | bank | LIVE |
| `k_window` | 6 | bank | LIVE |
| `curl_arc_min` | 4.0 | bank | LIVE |
| `curl_vtx_lo` / `curl_vtx_hi` | 0.05 / 0.95 | bank | LIVE |
| `curl_r2_min` | 0.4 | bank | LIVE |
| `momo_config.momo_slope_min` | 1.2 | DB | **DEAD for octo-freedom** — overwritten |
| `momo_config.momo_slack_ref` | 1.2 | DB | **DEAD for octo-freedom** — overwritten |
| `momo_config.momo_window_min` | 60 | DB | **DEAD for octo-freedom** — overridden by SPAN_MIN 10 |
| `rig.C['momo_slope_min']` | 0.4 | v3 config row | **DEAD for the walk** — never read. It is `build_wsf_dtf_v3.py:88 SLOPE = 0.4 # FITTED`, applied only inside that report |

So the practical divergence is exactly two numbers — **slope_min and slack_ref, 0.4 vs 1.2** — and
WS1_CFG's 0.4 wins. The other three WS1_CFG keys already match the bank.

**THE SWEEP TARGET IS `walk_mom_models.WS1_CFG` + `SPAN_MIN`, not `momo_config`.** Sweeping
`momo_config` would have produced identical cells for slope, slack and window — the third time this
class of bug would have burned the budget.

CARRIED FORWARD, unmeasured: whether lazy-g reads momentum through the same WS1_CFG path. Joe named
octo-freedom AND lazy-g as the two users; only octo-freedom's path has been traced.

## 11. ws1mage-rev DOES NOT READ ws1Mage IN THE WALK — Joe's swap idea, and what it uncovered

Joe 1005, overnight: *"I have an idea to swap ws1mage-rev with ws2 or ws3"*. The swap he meant
(the `g1` line) moves nothing, and finding out why is the real result.

`jig.ws1mage_rev(g1, sig_mage, hi, lo, dwell, rev_wob, hold, gate)` returns THREE legs. The walk
consumes TWO of them (`report_leash_walk.py:200`):

```python
rev = {d: rev_lookback_mask(legs[d]['sig'], legs[d]['sig_conf'], rig.n, knobs['rev_lookback'])
       for d in (1, -1)}
```

| leg | derives from | consumed by the walk |
|---|---|---|
| `dwell_ok` | **g1 = ws1Mage**, gated by `dwell` | **NO — computed and discarded** |
| `rev` | **g1 = ws1Mage** via `_mage_rev(g1, rev_wob)` | **NO — computed and discarded** |
| `sig` / `sig_conf` | **`sig_mage` = gcws30Mage**, oob -> ib cross | YES, only these |

**So inside the octo-sig walk, "ws1mage-rev" never touches ws1Mage.** It is a gcws30Mage
out-of-bounds-to-in-bounds cross. Three knobs are inert for that one reason: `dwell`, `rev_wob`, and
the identity of the g1 line itself.

**THIS IS A SPEC-LEVEL FINDING, NOT A TUNING ONE.** Joe's off-book rule (1003 spec, batch 2) is that
those trades *"must qualify with a same-dr ws1mage-rev event + ws1r oob"*. The walk's `rev` carries
only the gcws30Mage cross, so the ws1Mage half of that qualifier is not being applied. **Joe's to
rule: is the discard intended, or should `dwell_ok` and `rev` gate the signal too?**

### MEASURED — g1 and dwell, 12 walks on 10-02, all 43 signals

| g1 line | dwell 1 | dwell 3 | dwell 6 | dwell 12 |
|---|---|---|---|---|
| ws1Mage | 43 | 43 | 43 | 43 |
| ws2Mage | 43 | 43 | 43 | 43 |
| ws3Mage | 43 | 43 | 43 | 43 |

My first explanation for the inertness was WRONG and is corrected here: I guessed ws1Mage's oob runs
were all longer than `dwell`. They are not — median 4 bars and **73.8 % of hi runs are <= 12 bars**,
so `dwell` 12 should bind on three quarters of them. The cause is the discard, not the run lengths.

### THE SWAP WITH TEETH IS `sig_mage`, AND IT IS LIVE

| `sig_mage` line | 10-02 signals | vs baseline |
|---|---|---|
| **gcws30Mage (current)** | **43** | baseline |
| ws1Mage | 38 | **-5** |
| ws2Mage | 30 | **-13** |
| ws3Mage | 21 | **-22** |
| ws4Mage | 19 | **-24** |
| gcws15Mage (`rig.C['sig_line_surgical']`) | — | **NOT IN THE CACHE** — needs a line build before it can be tested |

Monotonic: the higher the TF carrying the cross, the fewer signals. Under Joe's objective that is a
LOSS OF TRADES of 30 % to 56 %, so it only pays if net per trade rises enough to cover it. Scored
across all 17 days separately - signal count is not the objective.

### `boundary_xwob` IS live — it sets `sig_conf` = cross + hold - 1

| `boundary_xwob` | 10-02 signals |
|---|---|
| 1 | 41 |
| **4 (current)** | **43** |
| 8 | 40 |
| 12 | 36 |

The current 4 is the peak of the four sampled. First knob found with a local maximum at its banked
value rather than at an edge.

## 12. THE MISSING HIGHER-TF MOM-TRUE GATE — found by Joe's eyes on 10-04 14:30

Joe 1005: *"something's wrong with 10-04 14:30 ... I can see that ws4,5,6,7 are showing momentum"*.

**His read was right.** Measured at the signal bar, dr +1, r-momo fence 17/83:

| TF | Mage @extrema | r @signal | mom-true @signal | state |
|---|---|---|---|---|
| ws1 | 117.86 | 56.42 | false | none |
| ws2 | 107.44 | 65.93 | false | none |
| ws3 | 116.55 | 88.10 | false | none |
| **ws4** | 111.41 | 76.16 | **TRUE** | momo |
| **ws5** | 98.77 | 80.55 | **TRUE** | momo |
| **ws6** | 85.32 | 59.97 | **TRUE** | momo |
| ws7 | 66.20 | 49.47 | false | none |
| **ws8** | 53.36 | 45.80 | **TRUE** | momo |
| ws9..ws12 | 49.60..40.02 | — | false | sideways |

He called ws4,5,6,7. The mech says **ws4, ws5, ws6, ws8** — three of his four exact, plus ws8 he did
not name, and ws7 reads as momentum on the chart but is `none` to the mech.

**AND 10-04 14:30:20's D ex-fence block is ws2 ALONE.** So four higher TFs carry momentum above a
one-member block, and my build confluenced it anyway.

### THE GATE WAS RULED AND NEVER BUILT — two failures, both mine

Joe's 1004 batch-1 ruling, verbatim from the conversation: *"02:42,02:48,02:50 are gated by higher
TF mom-true"*. It is **not in this spec, not in the chat log, and not in the code**:

```
grep -c momentum_true|mom_at|mom-true   branchD.py -> 0 | sweep.py -> 0
```

So I neither banked his ruling nor implemented it. Measured against his own calls:

| octo-sig | his ruling | dr | D ex-fence block | mom-true TFs | above the block | my build decided |
|---|---|---|---|---|---|---|
| 09-25 02:12:10 | confluenced | +1 | ws2 | ws5,6,7,8 | **ws5,6,7,8** | CONFLUENCE — agrees |
| 09-25 02:13:10 | pyramid candidate | +1 | ws2 | ws5,6,7,8 | **ws5,6,7,8** | CONFLUENCE — agrees |
| 09-25 02:42:35 | **GATED** | -1 | ws1..ws4 | ws5,6,8 | ws5,6,8 | BLOCKED, but by mtd.r2 — not by momentum |
| 09-25 02:48:50 | **GATED** | -1 | ws3,ws4 | ws5,6 | **ws5,ws6** | **CONFLUENCE — CONTRADICTS HIM** |
| 09-25 02:50:45 | **GATED** | -1 | ws3,ws4 | ws6 | **ws6** | **CONFLUENCE — CONTRADICTS HIM** |
| 09-25 03:30:05 | confluenced | -1 | ws10 | ws3,ws12 | ws12 | OPEN `neither` — contradicts him, separate gap |
| 10-04 14:30:20 | *(he flagged it)* | +1 | **ws2** | **ws4,5,6,8** | **ws4,5,6,8** | **CONFLUENCE with-trend** |

### THE GATE CANNOT BE "ANY HIGHER TF MOM-TRUE" — his own calls forbid it

02:12 and 02:13 are **confluenced** by Joe and carry mom-true at ws5,6,7,8 above a ws2 block. A
blanket "any mom-true above the block gates it" would wrongly block the two signals he approved.

What separates them, measured — the GAP between the block top and the lowest mom-true TF:

| octo-sig | block top | lowest mom-true above | gap | his ruling |
|---|---|---|---|---|
| 02:12:10 | ws2 | ws5 | **2** (ws3, ws4 quiet) | confluenced |
| 02:13:10 | ws2 | ws5 | **2** | confluenced |
| 02:48:50 | ws4 | ws5 | **0 — adjacent** | GATED |
| 02:50:45 | ws4 | ws6 | **1** | GATED |
| 10-04 14:30:20 | ws2 | ws4 | **1** | he flagged it as wrong |

**ADJACENCY is the candidate discriminator: gap 0 or 1 gates, gap 2 confluences.** That is MY
hypothesis from five data points, NOT his rule, and it is not implemented. He names it or rejects it.

### WHAT THIS EXPLAINS

- 10-04 14:30:20 shorted into a rise that ran a further **+0.427 %** over the next hour, took 0.906 %
  of heat for 0.356 % of gain. With momentum live on ws4, ws5, ws6 and ws8 just above a one-member
  block, the gate he ruled for would have stopped it.
- **19 of the 32 trades the 0.95 stop rescues sit on a one-member D block** (section 11). The wider
  stop has been partly compensating for a band test that cannot fire AND a momentum gate that was
  never built.

OPEN, for Joe: (1) the gap rule above - his to name; (2) whether the gate reads momentum at the
SIGNAL bar or at the mtd extrema - both measured above and they differ at ws8 (false at the extrema,
true at the signal); (3) whether `mom-true` here means `momentum_true` with `strip_mom_at_fence`, as
measured, or the raw verdict.
