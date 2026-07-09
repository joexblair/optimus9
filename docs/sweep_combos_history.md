# Sweep-combo history — last 2 weeks (2026-06-21 → 07-05)

**Purpose:** input for the **comprehensive causal re-sweep** triggered by #58 (arm+gate producers read
non-causal `_line`; flipping them to `W.line` invalidates every knob tuned against the look-ahead arm).
Compiled from the session transcript. Each entry = the contextual paragraph(s) that defined the combo
space, plus a **validity flag** — most historic sweeps are contaminated (look-ahead `_line`, synthetic
tape, or the malformed `kt5` r-line override) and must be re-run causally.

> **⚠️ Contamination legend**
> - **LA** = scored on look-ahead `_line` arm/gate (#58) — numbers inflated, knob winners suspect.
> - **SYN** = window(s) on synthetic tape (05-25/05-30/06-04/06-09) — invalid.
> - **kt5** = used the malformed `('k',…)` s15r/s30r override — absolute numbers wrong (relative rankings *maybe* survive).

---

## The harness (the reusable mainstay — `sweep_run.py` / `sweep_eval.py`)

- **`sweep_eval.py`** — atomic unit `evaluate(db, end_ms, config, lrcfg, base_cache) → (net_of_cost_total%, n_trades, win%)`.
  Config keys: `line_overrides`, `bias` (BiasConfig knobs), `lrcfg`, `exit{predict,gate_fam,slip}`,
  `bias_filter{tf,lenM,lenm,multM,multm,srcM,srcm,N,oob}`. `RT_COST=0.20`.
  `BASE_BIAS = dict(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False, mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')`.
- **`sweep_run.py`** — orchestrator. `WINDOW_ENDS = ms('2026-05-25 00:00') + i*5*86400000, i in range(7)` (**7 windows, 05-25→06-24, 7-day windows / 2-day overlaps**).
  `KNOB_SPACE`/`KNOB_DEFAULT` for **SL · curl_fam · exit_rlb · predict · slip · gate_fam · bias_on · hb_\* · bro_N**.
  `_vals(base, kind)`: **len ±4 · mult ±0.12 · src [base]+2 others**. `param_to_config` maps flat params → config dict.
  `gen_configs(target, block=6, per_block=32)` — **bounded overlapping-covering blocks** (every setting-pair shares a block → all pairwise + key-triple interactions exercised).
  Pool `cpu_count()-2`, checkpoint `sweep_results` (resumable). **Score = worst-window net (minimax, "the worst best outcome")**.
- **`docs/sweep_harness.md`** — reusability doc (extension points: new filter→KNOB_SPACE+param_to_config+evaluate; new line→automatic; new metric→one line in `_work`; real cost→RT_COST).
- Joe's mandate (06-30): *"tweak all of the moving parts together, or as subsets that you mix and match, so all settings interact with all others by overlapping the subsets… test all 7 windows with 2-day overlaps back to 05-18… metric = worst-window net… scope = just the active configs… bias filter on/off included… this will be our mainstay."*

---

## Sweep log (chronological)

### 06-22 — support-BB src × wobble (grind #26) · kt5-era
- **#26 grind**: support BB src `hb{tf}M` × **{close, hl2, ohlc4, px_smooth}** × **wobble n/strict**, KPI-first via GrindStore.
- `blc_wob_bars × strict` (× tf × src) → the wob that fires closest to the swing without over-firing.

### 06-24 — blp6m line config
- `blp6m`: **len {8,10,13,16,20} × mult {0.3,0.4,0.5,0.6} × src** (5×4×2 = 40) × 9 windows (grind one window first to narrow, then snf_compare across 9).

### 06-25 — group-cross x-offset
- `x` sweep **x = 0..4**, store per-x (group-cross → bias-update MAE metric).

### 06-30 → 07-01 — hb33 bias filter (bro-cross)
- **Slip sweep** (predict=False): net-of-cost peaks at **slip=20** (+0.007, only positive), recovers 35/79 culls.
- **13,750-combo** hb33: `22 × 5⁴` = **TF (11–33) × min-len (5, 13±2) × mage-len (5, 19±2) × hbhl33 min-src (5) × mage-src (5)** (TF/lens shared across the 3 sets; sources sweep hbhl33). *(flag: 11–33 step 1 = 23 not 22.)*
- **84,700-combo** full run (all 28 TFs) → table `hb33_sweep`, ranked avg_ret. Result: bias ≈ **fine-tune lever, ~+0.29/79%**, not the game-changer. **LA**.
- 3 hb33 sets = hbhl33 (swept srcs) · hblo33 (low/low) · hbhi33 (high/high); bro_stream + bro_verdict → reject against-grain.

### 07-01 → 07-02 — the extreme 12h covering-block sweep · **LA + SYN**
- **5500 configs**, covering blocks, 7 windows, worst-window minimax, ~20.2h, 0 errors.
- SL grid **{0.3, 0.5, 0.7, 0.9}**; per-param `_vals` (len±4, mult±0.12, src+2); BB lines len·mult·src, K lines src only.
- **Result: `s5m_len 10→6`** the one robust lever (isolated +33→+68.7 worst-window, OOS 3/3) → shipped ic_pk=115 → v2_walk $500→$15,026. **`bias=False` in all top configs** (bias = quality-vs-volume dial, not net).
- ⚠️ **Later invalidated**: windows 05-25/05-30/06-04/06-09 were **SYN**; and the s5m_len=6 win was **LA** (len=6 fast-breaches early, arms while s3/s4 mid-board). src also wrong (tuned close, TV says ohlc4).

### 07-03 — causal m-line re-sweeps
- **216-combo**: `s3m × s4m × s5m ∈ {6..11}³` over 06-16→06-23, worst-window. Where does look-ahead-era (10/10/6) rank?
- **Enhanced 432-combo**: add **s2M itf {60,120}** → `s2M{60,120} × s3m/s4m/s5m{6-11}` (table via `bikts3jd7`), worst-window over 06-19 + 06-23.
- **s2M reversal wob {0,2,3}** (gate-c timing) — separate trace (`bd94yr7pe`).
- **s5m_len {6,8,10,12}+** multi-window causal len sweep (len=10 prior). Finding: len-6 edge **concentrated in 06-15 window** (−1→+22), leans on one window.

### 07-03 — m-line × wob sweep (`mline_wob_sweep`) · **kt5 + LA**
- **1296 combos × 4 windows** (m-line × itf × wob), results table `mline_wob_sweep`.
- ⚠️ **Used malformed `kt5` s15r/s30r override** → absolute numbers wrong (the "6 beats 8" premise rests on this). Re-establish on correct configs.
- `120 > 60` for s2M was **one-dimensional** (worst-window net doesn't measure the early-detection 60 was chosen for) → fork, not a flip.

### 07-04 — finisher_v2 knob sweep (`finisher_v2_sweep`) · **LA**
- **1440 combos × 6 windows**, worst-window minimax: **Mage wob {0-3} · s30M-OOB {0,1} · s15r_lb · s30r_lb · fin_lb · fin_fwd**. 2.9h.
- **Winner: (wob1, strict, s15r_lb 14, s30r_lb 19, fin_lb 54, fin_fwd 6) → worst-window +14** (up from +1), n=1426. Key shifts: s15r_lb 29→14 · fin_lb 42→54 · fin_fwd 12→6 · Mage wob 0→2 · s30M-OOB strict.

### 07-04 — arm-delay wob sweep · **LA**
- **9 combos × 4 windows** (MAE + n): **s5m wob {2,3,4}** (base arm) **× s5Mage wob {2,3,4}** (big-leg delay).
- **Result: higher s5Mage wob → tighter MAE**; base s5m wob barely matters (all setups big-leg, base arm rarely fires). Provisional (gate-anchored; arm-anchor A/B pending).

### 07-04 → 07-05 — 2D arm_wob × fin_fwd (`sweep_arm_fin`) · **LA**
- `sweep_arm_fin.py`: **arm_wob {2..15} × fin_fwd {2..15 in 30s-bars → ×6 base}**, uses **`v2_walk_ad`** (not v2_walk) + lr_exit_v2(predict=False) + strand_rescue, 7 windows, worst-window minimax, per-worker base-cache with `W._line=W._line_emerging`.
- Smoke: (arm_wob=2, fin_fwd=2) → worst-window **+63.9%** (nets [64,114,146,201,229,220,203]).
- **Winner: arm_wob=7** (confirms wobslay-not-fwd is the axis). ⚠️ **Not applied** — look-ahead-inflated, held for a re-tune.

### 07-05 — fin_dedup toggle
- `fin_dedup` **{0, 6(30s)}** — one-fire-per-s30a-umbrella. Left **off** (sweep decides once cascade PnL is meaningful).

---

## Knob inventory — everything ever swept (for the comprehensive causal space)

**Lines (per BB line: len · mult · src; per K/r line: src only):**
- m-lines: s2m, s3m, s4m, s5m — **len {6..11}** (or ±4 of base), mult ±0.12, src [close/ohlc4/hl2/…]
- Mage/M-lines: s2M(itf **{60,120}**), s3M, s4M, s5M, s7M, s30M, s15M, s1M — len·mult·src; **s5m src close↔ohlc4** (unresolved)
- r-lines: s3r, s4r, s15r, s30r, s5r, s7r — src; **r_lb: s15r_lb, s30r_lb** (+ gcs5r_lb/gcs1r_lb planned)
- support/bias: hb{tf}M × {close,hl2,ohlc4,px_smooth}; hbhl33/hblo33/hbhi33 · TF {11..33} · bro_N

**Wobble (slope-flip confirm N):**
- arm: **s5m wob {2,3,4}**, **s5Mage/arm_wob {2..15}** · finisher Mage wob **{0-3}** · s30M/s15M/gcs5Mage/gcs1Mage wobs · blc_wob_bars · gate-rev wob

**Cascade / gate:**
- gate_rev line (s1M 60 default / s2M 120 alt) · s30M-OOB strict {0,1} · rtr terms · s2M-reversal wob {0,2,3}

**Finisher / entry:**
- fin_lb · **fin_fwd {2..15}** · fin_dedup {0,6} · s15r_lb · s30r_lb · gcs5-in-exit {on,off}

**Exit / sizing / cost:**
- SL **{0.3,0.5,0.7,0.9}** (+0.42?) · curl_fam · exit_rlb · predict {T,F} · slip {…,20} · gate_fam (s5/s6/s7) · leverage (re-derive vs arm-delay 19% DD) · RT_COST 0.20

**Meta:**
- bias filter on/off (confirmed: **off wins worst-window net** everywhere) · s5m_len {6,8,10,12} (isolated, ripples arm+gate+exit — kept out of joint grids)

---

## Read for the re-sweep

1. **Everything LA-flagged is now suspect** — `s5m_len 6`, `arm_wob 7`, the finisher-v2 winner, the wob findings were all scored on the look-ahead arm/gate. Re-run on `W.line`-causal producers.
2. **Drop the synthetic windows** (05-25/05-30/06-04/06-09) or confirm the tape is real for every window used.
3. **kt5 taint** — any result depending on `mline_wob_sweep` needs re-establishment on DB-resolved r-lines.
4. **s5m_len must go back in the grid** (it was pulled for compute; post-flip it's load-bearing and unproven).
5. The harness (`sweep_run`/`sweep_eval`, covering-block, worst-window minimax, 7 windows) is the vehicle — extend `KNOB_SPACE` to the full inventory above.
