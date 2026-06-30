# lr cascade — the latch-release reversal cascade (decoupled, configurable)

Status: BUILT + decoupled (0628→29). The SHAPE is code, everything else is data. **Re-spec'd 0629** off the
stale cf15 snapshot: **bias dropped from the cascade** (set upstream, no place here), **s2r restored** as a
clearance gate. This is the raw pl-cascade.

**v2 TARGET (0630):** the *prediction-gated* pl-cascade — s5m/s5r arm, s3r/s4r prediction gates, s2Mage
ready-to-reverse, s30M finisher (§v2). The entry-timing **KERNEL is proven** (§Build progress); the finishers
+ the full latch-flow are the build ahead. AB results **stashed** (§AB), NOT locked — **all theory until proven.**

## The mechanic
**Slow arm → reversal → fast finisher, cleared by gate(s):**
1. **ARM** — an arm gate's line breaches OOB (closed) → armed, side = breach side. (seed: `s6m`, TF6.)
2. **REVERSAL** — the arm line's *emerging* value wobslay-reverses by ≥ `floor`.
3. **FINISHER** — any active finisher gate re-breaches on the same side. (seed: `s30a` = s30M&s30m OOB + s30r lookback-19, TF30s.)
4. **GATE** — all active gate clearances must pass to fire. (seed: `s2r` lookback-11, TF2 — same side; prevents the finisher triggering early.)

NO bias in pl-cascade — bias is set upstream. (The old `s14M` mid-vs-50 was a trial Joe disabled weeks ago that lingered in cf15 and got faithfully reproduced — the drift that triggered this re-spec.)

## SHAPE (code) vs DATA (config)
`optimus9/analysis/lr.py`:
- **`lr_detect(W, cfg)`** — THE STRATEGY = the state machine. Walks the gate-sets; emits entries only (SRP: no verdict baked in). Helpers: `_gate_side` (a gate's lines × `check`, combined by `op`) · `_finisher_active` (OR across finishers) · `_gate_ok` (AND across gate-role clearances).
- **`lr_walk(W, entries, cfg)`** — the BACKTEST verdict (MAE/MFE). Separate concern.
- **`lr_config(db) → LRConfig`** — the ONE loader: gate-sets + knobs + OOB. No hardcode.

**Data:**
- `lr_gate` (role[`arm`|`finisher`|`gate`] · name · op[AND|OR] · active) + `lr_gate_line` (ic_pk · check[`oob`|`lookback`|`mid`] · per-line `lrgl_lookback`). Lines by **ic_pk**. The `lookback` window auto-scales per line TF.
- **Per-line lookbacks** on `lr_gate_line.lrgl_lookback` (s2r 11 · s30r 19 · s15r 19; null → falls back to `lp_s30r_lb`). The exit overrides all to `lp_lr_exit_rlb`.
- knobs → `lp_config` (`lp_lr_floor/wob_n/horizon/target/swing_ms/swing_pct` + `lp_s30r_lb` default).
- OOB → `optimus9_system.hi/lo_boundary`. Every gate line read via `W.line` (value_mode-honoured, #42).

## One detect, three consumers (the event-stream discipline)
- **strat_review** — `lr_detect` IS the cascade producer (replaced the gate-chain TradeGateWalker). Reports the entries.
- **superscope / rig** — `lr_detect` + `lr_walk` (the MAE/MFE verdict).
- **o9-live** — `lr_detect` per 5s kline → the exchange (fills = the verdict).
`live == prod == backtest` by construction (same `lr_detect`).

## Configurable from the UI (no code)
The strategy page's cascade unfold renders the live `lr_gate` gate-sets (by role, active-toggle + op + lines) + the 8 knobs (edit-in-place). **Add a finisher = a row + a tick.** Proven: ticking the seeded-disabled `s15a` (TF15s finisher) → cascade fires s30a OR s15a (more entries); untick → back. Same for the `s2r` gate (tick to clear-gate the finisher).

## v2 — the prediction-gated pl-cascade (TARGET, in build; all theory until proven)

The evolved spec (Joe 0630). Replaces the s6m-arm / s30a-finisher baseline above with a richer arm + a
prediction/reversal gate ahead of the finisher. **Pre-reqs** (◐ = partial / owed):
- ✗ **s5m stays 0.4** — #45 RESOLVED (0630): the 0.4→0.65 widen was NEUTRAL on entries (gate+finisher subsume the small-breach noise; validates the 0.30 as robust) AND **worse on the s7 exit** (s5m feeds the exit's s5r prediction; 0.4 predicts better: 0.40 net +44.0% vs 0.65 +37.2% on s7·s30a_s15a·pg). **Test rejects the pre-req → keep 0.4.**
- s6m left at **0.4** — baseline (lr_detect/strat_review) + AB fallback only.
- ✓ clone s2 → **s4** (240s) + **s3** (180s); s2/s3/s4 min-mult **0.56**.
- ✓ clone hbhl6 / hblo16 / hbhi16 → **hb33** (1980s).

**Lines & purposes:**
- **s5m** — THE v2 arm (replaces s6m; s6 is only used if an AB picks it). s5m OR s5r arms the cascade.
- **s5r** — a **divergence** arm on the side *opposing* the breach. Stoch-RSI veers off a leg as its momentum slows; we wait for **s4m to breach OOB on the side opposite s5r**, and s4m's OOB travel *pulls s5r back to the leg* — that pull is the signal. Fires when s5r is OOB-opposing (**OOB-slip 15** → its fence is 70/30, so "OOB" = outside 30–70) AND s4m is OOB on the breach side. e.g. s4m breaches LOW + s5r ≥70 → arms a **LONG**. If s5r & s5m fire **opposite** sides → **s5m wins**.
- **s3r / s4r** — prediction candidates AND gates. Closed-bar, 0 wob. s3min/mage are prediction support for s3r; s4min/mage for s4r.
- **s2Mage reversal** — completes s3Mage/s4Mage when "ready to reverse". Closed-bar, 0 wob, **boundary-agnostic** (reverses anywhere). setup#1 = s3r or s4r OOB *after prediction*; setup#2 = s3r/s4r did NOT breach AND s3m+s4m reversed.
- **s30M** — the trigger that makes the trade. Closed-bar, **2 wob**.
- **hb33 ×3** — bro-cross bias testing ONLY (non-prod, visual; emerging + lp_bro_wob); NO impact on the cascade.

**Flow (per window):**
1. **s5m OR s5r breaches** → armed (s5m is THE arm; s5r the divergence arm above), `es` set, gate(s) latched, taking inputs.
2. **[AB toggle: `stale_exit`]** if s2r/s3r/s4r are in their lookbacks AND all 3 have progressed to IB *when s5m breaches* → **exit the flow, no trade**. *(Tested with/without — Joe 0630; not assumed.)*
3. **The latch** — test s3r predict while s3m OOB, s4r while s4m OOB. The gate opens by ONE of (lifecycle confirmed Joe 0630):
   - **(a) all-IB** — s2/s3/s4 all cross to IB → open **immediately**.
   - **(b) predict → reverse-before-breach** — an r predicted but reverses *before* it breaches (the predicted move aborted) → open **immediately**.
   - **(c) ready-to-reverse → s2Mage reverse** (boundary-agnostic). Reached two ways: **setup#1** = an r predicted **then breached** → ready-to-reverse; **setup#2** = no prediction + s3m/s4m reversed. A 2nd r predicting just extends the latched wait.
4. Gate open → **FINISHER DELATCH**: the finishers **latch s30a AND s15a breaches from the ARM onward** (s15a = ic 84/85/86, the TF15 twin of s30a; each honouring its r-lookback) and breach at their OWN times — s15a can lead s30a by minutes, the latch carries each. Trade fires once **both have latched**, never before the gate-open → **trade_k = max(latched, gate-open)**: both pre-latched ⇒ trade AT the gate-open ("trade immediately"); a late finisher ⇒ trade when it latches (forward). **No drop — every gate-open trades once both latch.**
5. **s30M is a *component* of the s30a latch** — no separate wobslay trigger; the delatch (gate-open) IS the entry.
6. **Bias (deferred):** while curating, trade at ⑤ WITHOUT a bias check; when the spec locks, consult the upstream/bro-cross bias and **adhere** (block counter-bias).

## Build progress — the KERNEL (a proven subset of v2)

- **Entry-timing kernel:** arm (s6m) → reversal → **s3r OR s4r predict-then-breach** (arms) → **s2M slope-flip** = entry. Stands in for steps 3–4 (no s5m arm, no s2r/s3r/s4r lookback gates, no s30M finisher yet).
- **Proven:** vs the s30a-finisher baseline (medMAE 0.67, %<0.5 43%), the kernel gives medMAE **0.46**, %<0.5 **55%** (n=77, valid setup window). The prediction→reversal timing sharpens entries.
- **Engine (SRP):** `lr_setups` (producer: arm-breach+wobslay events) / `lr_detect` (finisher+gate verdict). `bro_cross_events` / `bro_cross_flips` (verdict; `N` + `require_oob` params). Harnesses: `lr_kernel_walk.py`, `lr_kernel_ab.py`.
- **Seeds:** s2m/s2M, s3, s4, s5 (off the 0.4 s6 — re-clone owed), hb33.
- **Anchor fix (0630):** bias closed lines epoch→midnight (TV grid) — see `docs/epoch_anchor_spec.md`.
- **bro-cross:** split + `require_oob` A/B — no-OOB whipsaws (301 vs 69/window) + same-bar set conflicts → OOB stays the stabiliser, IB crosses → grav-bias-flip.

## v2 BUILD — `optimus9/analysis/lr_v2.py` (alongside the untouched baseline; integrate when proven)
SRP nodes, plumbed: `arm (s5m OR s5r) → gate_open (predict/reverse/ib-clear → verdict) → finisher (qualify + trigger) → entries`.
- ✓ **[1] `s5r_arm`** — divergence arm producer (59 arms/5d verified; slip=15 a param, **DB-knob owed**).
- ✓ **[2] arm unify** (`s5m_arm` + `v2_arm`) — s5m straight-breach OR s5r, same-bar conflict → s5m wins, + window cap. **635 raw setups on the current 0.4 s5m** (586 are small-breach noise — the 0.65 re-clone + s7-exit test, task #45, tames that; gate+finisher filter the rest).
- ✓ **[3] `gate_open`** (`gate_signals` producer + verdict) — the latch lifecycle, reasons a/b/c. Gate-open entry-proxy (pre-finisher) = **medMAE 0.27% / %<0.5 61%** (a=55 cleanest 0.18/90%, c=403 the bulk 0.26, b=177 0.48). The verify caught a `'a'` bug — it must be the OOB→IB **cross** (transition), not the static all-IB (which fired 544/635). MECHANISM CHOICES still to confirm: reverses = closed slope-flip · setup#2 "m reversed" = s3m/s4m slope-flip toward the trade · predict gated by s{n}m OOB. `stale_exit` (flow-2) is an **AB toggle**, not baked in.
- ✓ **[4] finisher** (LATCH model, 0630 — 3 iterations, each caught by Joe's eye on a missing trade): the finishers **LATCH s30a + s15a breaches from the ARM (i) onward** and **DELATCH at the gate-open**; trade_k = **max(latched, gate-open)**. Two earlier builds were wrong — a 3-min AND-drop filter (killed ~79%, accidentally quality-selected) and a simultaneous/cumulative *fixed-window* gate (mistimed trades by up-to-90min: s15a fires minutes apart from s30a, the `gate_open−24bar` window clipped it). The latch carries each finisher's breach across `[arm→gate-open]` so a lead/lag pair both count. **No drop — every gate-open trades once both latch.** s30M is just a *component* of the s30a latch (no separate wob trigger). Verified: the 18:46 case lands at 18:46 (s15a latched 18:43, s30a 18:44, delatch 18:46). The arm→gate-open wait is **by design** (the setup maturing, not lag) — Joe confirmed the 14:55-arm→15:12-delatch lands a 2% MFE.
- ✓ **[5] wire + measure** (`v2_walk`) — **end-to-end: n=156, medMAE 0.30% / %<0.5 58% / %MFE≥.7 67%** (cleanest of the build; ref baseline 0.67, kernel 0.46). On the noisy 0.4 arm; no SL'd PnL.

**`stale_exit` AB (flow-2):** OFF n=156/0.30 · ON n=49/0.48 — the stale-exit (as built = s2r/s3r/s4r all IB at the arm) **removes the good setups → keep it OFF**. (My stale is a simplification of the spec's lookback version — revisit.) All v2 numbers are **theory until proven** (inferred finisher mechanisms).

**v2 EXIT (`lr_v2_exit_ab.py`):** v2 entries → `lr_exit` (s7·`exit_on=s30a_s15a`·predict_gate=on·s5m=0.4, NO bias). With the **LATCH finisher** (every breach trades, timed at the delatch): **266 trades, medMAE 0.33%, 75% win, avg +0.225%/trade, +59.8% net** (SL-floored). **Net-of-~0.20% RT cost ≈ +0.025%/trade — thin but POSITIVE, before any bias.** This CORRECTS the prior "net-negative / trades too much" finding: that was the FINISHER-TIMING bug (cumulative/window gate mistimed entries to late/bad fills), NOT over-trading. Correct latch timing recovers 75% win + medMAE 0.33 across all 266 — so timing IS the quality lever, and **the bias is now UPSIDE (push the +0.025% higher), not the rescue.** AB verdict (0.4>0.65 · `s30a_s15a`≫`curl` · `predict_gate=on`) holds. Table = `v2_walk` (cf15 cols + exit_pct/reason); pine = `v2_trades.pine`.

## AB results — STASHED, theory only (NOT locked)

Combo sweep (`lr_kernel_ab.py`): arm (s6m/s5m) × trigger (s3r/s4r/OR) × s2M-debounce (1/2/3 bd-closes) × arm wob-n. Entry quality only (no SL'd PnL):
```
baseline  s6m·OR·deb1·wob4:  n=77  medMAE 0.46  %<0.5 55  %MFE≥.7 70
winner    s5m·OR·deb3·wob4:  n=83  medMAE 0.35  %<0.5 55  %MFE≥.7 69
```
- s2M **debounce is the biggest lever** (deb1→3: medMAE 0.46→0.35); s5m arm pays off WITH it; higher wob-n (7) worse everywhere; s4r-only weak; s3-only posts the highest %MFE≥.7 (76–78).
- **KEY CAVEAT (Joe 0630):** the deb2/3 win likely **proxies the unbuilt finishers** — s30M-wob + s30a/s15a lookback-4 / tolerance-2 are themselves a confirm delay. **Not a standalone lever; re-test once the finishers are plumbed** (the debounce may be subsumed). And the ABs ran on the **pre-pre-req configs** (s6m multi 0.4, s5 off 0.4) — expect a shift after the 0.65 pre-req.

## Notes / open
- **PnL ground rule (0629):** no $ / PnL figures discussed without a stop loss applied — winners-only ceilings are banned (they're what masked the entry problem). So this doc carries counts, not $.
- **s2r role:** a `gate` (clearance) *for now* — Joe's open question is gate vs arming mechanism. Same-side `lookback`-11.
- **Structural constants** (not knobs): `//5` base-kline (5s), `×100` %-conv.
- **Follow-ups:** line-membership editor (add/remove lines + swap ic_pk per gate — UI shows lines read-only); `trade_gate` dead → sunset (#30); add `lr_gate`/`lr_gate_line` to `o9_live_schema.sql` when wiring o9-live; `seed_lr_gate.py` to be reconciled with the 0629 re-spec (migration in `migrate_lr_pl_cascade.py`).

Build: `seed_lr_gate.py` (tables + seed) · `seed_lr_config.py` (knobs).
