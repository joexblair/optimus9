# Arm mode: s5Mage first-OOB-reversal (Joe 0705)

**Why:** troubleshooting the v2_walk ⇄ o9-live mismatch. The current arm (`s5m` straight-breach) is twitchy
and hard to reason about; Joe's model is the **s5Mage reversal off an OOB extreme**. Wiring it as a
config-selectable arm lets both the backtest (`v2_walk`) and o9-live (`v2_walk_ad`) run the *same*,
readable arm, and a Pine (from the engine) marks exactly what the engine arms on.

## The mechanic (`s5Mage_arm` in `lr_v2.py`) — **TWO-wob latch** (Joe 0705 spec)
Two wob gates: a **wob_breach** confirms the OOB entry is real (filters boundary chop), then a **wob_signal**
confirms the reversal and fires the arm.
1. an emerging s5Mage bar **crosses** the boundary (≥85 / ≤15) → start the breach-confirm count.
2. **wob_breach (opens the latch):** `arm_wob` consecutive bars that **STAY OOB** (hi-breach: value **≥ hi**;
   lo: ≤ lo) **AND** print NOT-**lower** (hi → non-decreasing) / NOT-higher (lo). A lower-than-prior print
   *while still OOB* resets-and-resumes. **If the value falls back IB before the count completes, the hunt is
   ENDED** — abandon → idle, a fresh IB→OOB cross is required to retry (Joe 0706). This is what kills the
   boundary-chop false arm: a wiggle that pokes over the line, dips IB, then pushes back up **cannot** confirm
   (its climb-back is on IB bars). Fixed the false 07-05 20:18:35 arm (cross 20:15:05 → IB at 20:15:35 before
   7 → hunt ended). Arm rate 22.9 → 13.4/day; filler-bar arms 27 → 12.
3. **wob_signal (closes the latch → ARM):** `arm_wob` consecutive bars NOT printing a **higher** value
   (hi-breach → non-increasing / the reversal) / NOT **lower** (lo-breach).
- **Same value COUNTS** in both gates; **only a contrary print resets** the count to 0 and it **RESUMES**
  (unbroken any time, not from the cross). hi-breach → **SHORT** (es=+1, bd=−1); lo-breach → **LONG** (es=−1, bd=+1).
- **wob is in 5s bars** (intended). Replaces the old `_mage_rev` sign-run detector (mis-timed the fire) and the
  single-gate version (boundary chop re-armed it).
- **`arm_wob` (lp_arm_wob) = 7** — baked from the 14d wob sweep (`s5Mage_wob_sweep.py`), where MFE/|MAE| first
  crosses 1. Held lightly (ride-to-next-pivot metric); the on-chart Pine (`s5Mage_arm.pine`) is the truer check.
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
- **Filler-shift (display-only, Joe 0706):** if an arm fires on a **no-trade filler bar** (`volume==0`), the
  Pine timestamp walks FORWARD to the next real (V>0) bar. TV omits no-trade bars, so a marker on a filler bar
  has no chart bar to paint → invisible. The shift lands it on the first bar TV actually draws. The **engine
  arm time is unchanged** — this is purely so the on-chart marker is visible. ~27/366 arms shift (14d).
  - **Root note:** filler bars are carry-forward FLAT, and the wob "same value counts" rule means a flat
    filler run of `arm_wob` bars can tick the wob on its own → a **spurious arm on a dead tape**. The display
    shift makes these visible but does NOT suppress them; the real fix (count only V>0 bars in the arm/wob) is
    a separate, open decision. See `pk_optimizer.s5Mage_arm_events` (`arm_bar_filler=1`) and [[project_filler_invisible]].

## Initial result (raw, untuned — HOLD LIGHTLY)
- `v2_walk` on the s5Mage arm (7d): **$500 → $178 (0.4×) — loses.** But the gate/finisher/exit are still
  tuned for the s5m-breach arm, and every gate reversal is wob-0. This is the **starting point to
  troubleshoot + re-sweep from**, not a verdict on the arm.
- Arms: **24.3/day**. o9-live restarted on it (arm_mode=1).

## Status: **TEMPORARY — run on this until the v2_walk⇄o9-live mismatch is found**, then decide (revert to
s5m, or keep + re-sweep the whole cascade for the s5Mage arm). See [[project_o9live_forward_live]], #57.
