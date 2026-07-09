# Tide-trigger redesign — arm, filter/lock entry, s10r-tracked exit (0707)

**Status: spec LOCKED, UNVALIDATED.** Supersedes the arm_delay/strand era ([[project_causal_retest]],
`exit_v2_design.md`). Causal/emerging ONLY throughout — every element below is present-state; no forward scan.

## 1. Why we're here — arm_delay is look-ahead (confirmed, not theory)
- Window-invariance test on the incumbent `arm_delay` (lr_v2.py:375): **12/12 delayed arms MISMATCH.** Full-window
  scan snaps many breaches onto the SAME future s5Mage reversal (3 breaches → 11:07:50; 6 → 11:58:35). Truncate the
  window to the commit bar → the delay vanishes (da → breach). The delay only exists because the batch can see the
  future reversal.
- Root: `da = first rev5M==bd in [kc, cap]` — a forward scan. The signals are all causal (`_mage_rev` fires at bar k
  from steps ≤k; `bigleg_gate` past-only), but **you can't clamp a forward scan into causality.** The delay decision
  needs "a reversal is coming," which live doesn't have at the breach.
- The r-predict replacement PASSED causality but CHOPPED (timing a noisy turn). So: don't time the tide-turn.

## 2. Decision: tide as TRIGGER, not filter
Elder's tide = higher-TF **MACD-H 2-bar slope** (Triple Screen screen-1); Impulse = EMA-slope ∧ MACD-H-slope
(green/red/blue, blue = release); divergence = his strongest reversal signal. All causal. **Parked** in favour of
Joe's **Mage-tide** — same Elder architecture expressed in the Mage lines we already have, and the finishers are
reliable near the swing, so the tide TRIGGERS (near the swing) rather than merely filters.

## 3. ENTRY — Mage-tide filter + directional lock (Elder Triple Screen in Mage terms)
Long-side (a lo dip bought with an up-tide):
```
when s2m breaches LOW
  if s3r OR s4r proximal to lo boundary (< ~33)          # wave oversold (screen-2)
    if s5Mage AND s7Mage > 50                            # tide still up (screen-1)
      trade HIGH, and LOCK OUT opposing arms until this trade exits
```
- Causal: tide is a present-state filter (Mage>50 *now*), lock is a past-determined latch, unlock = the exit event.
- Short-side is the mirror (s2m hi-breach · s3r/s4r proximal hi · s5/s7Mage < 50 · trade low · lock).
- Lock release fork (**OPEN**): exit-only (Joe's lean) vs also release on Mage crossing 50 (tide-death). Exit-only
  makes the exit load-bearing.
- Knobs → DB, sweepable: the `>50`, the `<33`, OR-vs-AND on s3r/s4r, the s2m trigger-line choice.

## 4. s10r CURL METHOD — the lynchpin (validated vs Joe's eye, 07-06)
```
1. sample EMERGING s10r (src = hl2) at each 5-min seam → c[]
2. curl-up at seam k  ⟺  c[k-1] < c[k]  AND  c[k-1] ≤ c[k-2]   (trough at k-1, fires at k; uses only ≤ k)
```
- **hl2 + 5-min** matched all four eyeballed curls (18:30/18:50/19:50/20:20) within ±1 seam. close-src floor-hugs and
  jitters; 150s re-introduces wiggle. hl2 also matches the r-src convention (s15r/s30r=hl2).
- Detection lag = one seam (≤5 min) — inherent to coarse causal detection.
- Noise filter (to match the eye's selectivity, knobs): trough oversold (< ~15) AND rise clears a delta.

## 5. EXIT — s10r-tracked, favourable-finisher timed (SHORT side; lo breach) — LOCKED
```
when s5m breaches
  when s30a + s15a
    predict s10r using s5m + s5M as anchors            # predict_breach(s10r, s5m, s5M) — the arm's r-predict, reused
      if TRUE:
        wait for s10r to breach
        keep testing s10r-predict on each s5m breach + s30a+s15a
          if s10r NOT advancing toward oob              # higher/flat vs THE LAST COARSE VALUE, tested each 5-min seam
            → exit all shorts on next LO-side s15a       #   (floor knob = the tolerance)
        when s10r curls (5-min hl2 detector)
          → exit all shorts on next LO-side s15a
      if predict NOT true:
        when s5r curls (150s? — post-val sweep)
          → exit on s30a + s15a
```
Resolved forks:
- **Floor baseline + cadence:** "not advancing" = s10r higher/flat vs **the last coarse value**; advance-test at
  **each 5-min seam** (aligns with s10r's coarse update). The whole s10r monitor runs on the 5-min coarse grid.
- **Exit-timer:** wait **indefinitely** for the finisher (no limit). s15a → **gcs1a** (1s clone) once 1s klines exist
  (task).
- **Why s15a not s30a for the exit:** s15a is the URGENT-exit finisher — a reversing r is already moving away from the
  swing; waiting for s30a risks missing the exit. Path C (predict-false) uses s30a+s15a (weaker signal → more confirm).
- **s5r-curl granularity:** 150s vs 5-min → **post-validation sweep**.
- **Unfavourable stop:** unknown → **PARK until the spec is validated** (this is the favourable-exit logic; the stop is
  the separate unfavourable backstop).

## 6. SRP / wiring
Three responsibilities, three producers → rows in the `trade_gate` seam (bias_meld), NOT fused into `v2_arm`:
- **momentum gauge** (s10r predict / advance / curl verdicts)
- **exit-timer** (next favourable-side s15a; later gcs1a)
- **filter + lock** (Mage-tide verdict + trade-state latch)
The gauge emits verdicts (stall / curl / no-fuel); the timer consumes them. Feed the event stream, don't bake a verdict.

## 7. Open / parked
- Unfavourable stop (§5) — park until validated.
- gcs1a exit-finisher swap — needs 1s klines (task).
- s5r-curl granularity — post-validation sweep (task).
- Entry lock-release fork (§3) — exit-only vs tide-death.
- Long-side exit is the mirror of §5.
