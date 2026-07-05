# Arm mode: s5Mage first-OOB-reversal (Joe 0705)

**Why:** troubleshooting the v2_walk ⇄ o9-live mismatch. The current arm (`s5m` straight-breach) is twitchy
and hard to reason about; Joe's model is the **s5Mage reversal off an OOB extreme**. Wiring it as a
config-selectable arm lets both the backtest (`v2_walk`) and o9-live (`v2_walk_ad`) run the *same*,
readable arm, and a Pine (from the engine) marks exactly what the engine arms on.

## The mechanic (`s5Mage_arm` in `lr_v2.py`) — **wob_no_fire_latch** (Joe 0705 spec)
- **The latch OPENS on an OOB breach and CLOSES (arm fires) on the first wob signal.**
- **wob signal = `arm_wob` sequential 5s bars that do NOT print a higher value** than the prior bar
  (hi-breach → **non-increasing**) / NOT lower (lo-breach → **non-decreasing**).
  - **Same value COUNTS** toward the wob; **only a contrary print resets** the count to 0 — and it **RESUMES**
    counting (unbroken *any time* after the breach, NOT from the breach). One arm per breach.
  - lo-breach (oversold) → **LONG** (es=−1, bd=+1) · hi-breach → **SHORT** (es=+1, bd=−1)
- **wob is in 5s bars** (intended — confirmed by Joe). Replaces the old `_mage_rev` sign-run detector, which
  mis-timed the fire (a flat at the turn was attributed to the prior up-direction): the 20:16 breach fired
  **20:33 under `_mage_rev` vs 20:27 under this spec**.
- **s5Mage = `W.line('s5M')`** — the canonical DB line **37·0.83·ohlc4 @ 300s, emerging/causal**.
  - Mult 0.70 vs 0.83 does **not** change reversal timing (slope-flip), only OOB-breach frequency. 0.83
    gives **24.3/day @ wob-8** (≈ Joe's ~25/day observation); 0.70 gives 28.2/day. Left on the canonical
    0.83 (zero config churn). To try 0.70, change `s5M`'s `ic_bb_mult` in the DB — it's a dial.
- **wob = `cfg.arm_wob`** ("our defined wobble"), set to **8** for this run.
- The reversal **IS the unlatched arm** — `arm_delay` is **skipped** in this mode (no big-leg tide-delay;
  the s5Mage turn already is the delay).

## Config (DB, no hardcode — reversible)
- `lp_config.lp_arm_mode` — **numeric flag** (val column is numeric): `0` = `s5m` (current) · `1` = `s5Mage`. **Set to 1.**
- `lp_config.lp_arm_wob` — the s5Mage reversal wob. **Set to 8.**
- `LRConfig.arm_mode` maps `1→'s5Mage'`, `0→'s5m'` (default `'s5m'`).
- **Revert:** `UPDATE lp_config SET val=0 WHERE name='lp_arm_mode';` → back to the s5m arm, no code change.

## Wiring (`v2_arm`)
- `v2_arm` branches on `cfg.arm_mode`:
  - `'s5Mage'` → `s5Mage_arm` (cap on the opposite **s5Mage** breach + horizon).
  - `'s5m'` → current `s5m_arm` + `s5r_arm` (untouched).
- Both `v2_walk` (backtest) and `v2_walk_ad` (o9-live) route through `v2_arm`, so both honour `arm_mode`.

## Pine (`s5Mage_rev_emit.py` → `s5Mage_arm.pine`)
- Calls the engine's `s5Mage_arm(W, cfg)` directly → the Pine marks **exactly** the engine's arm bars
  (white bgcolor, 5s bar-containment match). `python3 s5Mage_rev_emit.py` regenerates it.

## Initial result (raw, untuned — HOLD LIGHTLY)
- `v2_walk` on the s5Mage arm (7d): **$500 → $178 (0.4×) — loses.** But the gate/finisher/exit are still
  tuned for the s5m-breach arm, and every gate reversal is wob-0. This is the **starting point to
  troubleshoot + re-sweep from**, not a verdict on the arm.
- Arms: **24.3/day**. o9-live restarted on it (arm_mode=1).

## Status: **TEMPORARY — run on this until the v2_walk⇄o9-live mismatch is found**, then decide (revert to
s5m, or keep + re-sweep the whole cascade for the s5Mage arm). See [[project_o9live_forward_live]], #57.
