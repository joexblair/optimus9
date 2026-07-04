# Arm-delay mechanic — research + ideas (0704)

## The mechanic (Joe's spec)
A **dynamic arm-delay** plugged in *before* the gates — a "mini bias" on the arm:
- **base (unconditional):** the arm waits for the **s5m reversal** (≈ the swing reversal) instead of the s5m breach — right-shifts every lp-cascade flow, lowering MAE.
- **big-leg (conditional):** on a strong impulse leg the s5m reversal is premature (the swing faces opposing forces until momentum subsides — a falling knife). So IF
  - **s5Mage travelled directly** to the es side (from the opposite OOB, no return), **AND**
  - **s7Mage travelled directly** to the es side, **AND**
  - **s7r predicted or breached** (== es)
  then **hold the arm to the s5Mage reversal** (s7r momentum waning) before releasing the finishers.
- Reversals detected by **wobslay(n)** on s5m and s5Mage — sweep, **start n=2**.
- s5r lookback (19, reversal-line = s5m) is **SRP'd/prepped**, not gating yet.
- Line updates: s7m **10·0.5·ohlc4**, s7M **37·0.74·ohlc4**.
- Anchor example: **06-16 10:57:45 failed long → arm delays to ~11:40** (all 3 conditions met by 11:33; s5Mage troughs −1.3 @ 11:39:50, turns up). Tape-confirmed.

## What the literature says (this is a known idea, done rigorously)
- **Elder Triple Screen** = the canonical MTF entry filter, ~5× TF ratio per screen. Our **s5/s7 Mages (tide/wave) → s15/s30 (intermediate) → gcs5 (ripple, 5×)** IS Triple-Screen, oscillator-native. The mechanic **adds the s5/s7 "tide" screen** that was implicit — we were entering on the ripple without checking the tide had turned.
- **"Wait for the higher-TF oscillator to *turn* before a counter-trend entry"** (Tradeciety, ChartMini): a micro layer alone signals both directions; high-probability = HTF just turned AND LTF aligns. = our "don't trade the s5m reversal alone; wait for s5Mage to turn."
- **Separate identification from timing** (divergence → wait for crossover, not divergence alone) = our qualify-vs-trigger split, extended up to s5/s7.
- **Falling-knife avoidance** — the stated purpose everywhere; our 10:57 failed long exactly.
- **Regime filter** — the literature uses ADX to gate mean-reversion to non-trending. Our **"travelled directly" is a causal impulse-leg / no-retracement detector** — an ADX substitute built from the lines we already have.

## Three ideas to steal (deferred — see the task)
1. **Divergence confirm on the s5Mage reversal** — price lower-low + s5r/s7r higher-low (the exhaustion tell). s5r is already the "divergence arm"; requiring divergence at the s5Mage turn could sharpen it beyond a raw wobslay.
2. **Crossover trigger vs single-line wobslay** — Elder/Stochastic use a fast×slow crossover (%K/%D). An **s5m × s5Mage crossover** may be a cleaner "reversal" than wobslay-on-one-line. Sweep candidate.
3. **Leg-amplitude strength gate** — add leg amplitude as a second dial for "travelled directly" (only delay on legs > X%), a fuller ADX analogue.

## Sources
- Tradeciety — MTF analysis with oscillators: https://tradeciety.com/multi-time-frame-analysis-with-oscillators-simple-effective
- ChartMini — Stochastic entry timing (2026): https://chartmini.com/blog/stochastic-oscillator-timing-entries-in-overbought-and-oversold-markets-2026
- QuantifiedStrategies — Elder Triple Screen (backtest): https://www.quantifiedstrategies.com/alexander-elder-triple-screen-strategy/
- Collin Seow — momentum + mean-reversion mistakes: https://collinseow.com/mistakes-momentum/
- LuxAlgo — mean reversion, fading extremes: https://www.luxalgo.com/blog/mean-reversion-trading-fading-extremes-with-precision/
