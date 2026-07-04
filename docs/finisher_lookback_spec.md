# Finisher lookback on arm unlatch — spec (#53, Joe 0704)

Fixes the misunderstanding where the finisher check was pinned to the **s3s4 gate** instead of the
**arm unlatch**, so late-qualifying finishers were missed (the 09:34 LONG episode never traded).

## Label glossary (0704)
- **finisher lookback on arm unlatch** — the check that hunts for qualified finishers (s15a + s30a). *(was "finisher window")*
- **arm-delay-s7r** — the arm-delay mechanism; the big-leg condition is gated on s7r. *(was "arm-delay")*
- **s3s4 gate** — the arm→gate lifecycle gate (opens via path a/b/c off s3/s4). *(was "gate")*
- **arm unlatch** — the s5Mage reversal that releases the delayed arm (the arm-delay-s7r re-time bar).

## BRD (Joe, verbatim)
> Because the qualifiers that create a trade (the "finishers") might qualify in the moments before the arm
> is unlatched, we look back 7 bars to hunt for that qualification. If we find the qualifiers in a qualified
> state, inside the 7×30s bars prior to arm unlatch, then we place a trade on the **next same-side s15a**.

## Flow (the fix — replaces the single gate-pinned box)
1. **Arm unlatch** fires (the s5Mage reversal / arm-delay-s7r re-time bar).
2. **Proximal check** — look **back 7×30s** from the unlatch: are **s15a AND s30a** both in a qualified state?
3. **If yes → place the trade on the NEXT same-side s15a.** *(the s15a is the trade-placement mechanism, not optional.)*
4. **If no → proceed to s3s4 gate testing** → if the s3s4 gate opens, the finishers get **a chance** (NO time
   limit) to qualify → **place the trade on the NEXT same-side s15a** when they do. The chance runs until the
   **arm cancels**.

The trade is **always** placed on the next same-side s15a (both the proximal path and the gate path).

## Arm cancel (resolved: option a, Joe 0704)
- The arm cancels on an **opposite-side s5m breach** — a hi-breach cancels a long arm (from a lo-breach), and vice-versa.
- This is the sole time-limit on the gate-path chance (step 4): the finishers can qualify any time until the opposite breach.
- Build: `v2_arm` cap = `min(opposite-side-s5m-breach, i + horizon)` — the opposite breach cancels; the 1.5h
  **horizon stays as a backstop** for now (full horizon removal per the spec is a *separate* change, not this build).

## Knobs (DB-sourced, lp_config)
- **arm_wob** (=2) — s5Mage reversal wobslay for the arm unlatch. Higher → unlatch lands later / on the truer swing.
- **fin_lb** (=7×30s) / **fin_fwd** (=2×30s) — **belong ONLY to the finisher lookback on arm unlatch** (step 2):
  the proximal box is `[unlatch − fin_lb, unlatch + fin_fwd]`. `fin_fwd` is that check's late-line tolerance —
  it does NOT bound the step-4 gate-path chance (which has no time limit; see Arm cancel).

## Sweep
- **2-D combo: `arm_wob` × `fin_fwd`**, across the **full set of windows** (worst-window minimax). They overlap
  (both bridge the unlatch→swing gap) → sweep together, not two 1-D sweeps.

## Current-code divergence (finisher_v2 today)
- Anchor: **s3s4 gate**, not the **arm unlatch**.
- Shape: a box `[gate−fin_lb, gate+fin_fwd]` requiring both finishers inside — vs the BRD's **back-lookback at
  the unlatch** + **forward chance after the gate**, firing on the next same-side s15a.
- Trigger: a **gcs5M reversal** after Q1 — vs the BRD's **next same-side s15a**.

Related: [[project_o9live_forward_live]] · the r_lb TF-bar fix (commit 81293a6) already lets the finishers
qualify properly, so this episode now trades via the proximal path — re-scope during the build.
