"""
constants.py — Optimus9 system gospel.

Immutable, system-wide constants. NOT env-tunable (that is config.py's job).

Two distinct concepts share the magic numbers 70/30 and 85/15 and were
historically conflated under one ambiguous `high_b/low_b` name:

  • RSI OB/OS  — the endpoints the BB %B is rescaled into (oscillator units).
                 This is what makes a BB/K line read like TradingView. 70 / 30.
  • OOB        — "out of boundary": when a (rescaled) line is breached. 85 / 15.

A line is rescaled to [RSI_OVERSOLD, RSI_OVERBOUGHT], THEN OOB-detected at
[BOUNDARY_LO, BOUNDARY_HI]. Keep the two straight — never feed an OOB boundary
into a rescale slot (that was the f_bb_lookahead default bug).

Future constant groups slot in below their own header. If a group grows large,
promote it to a namespace class in this same file — consumers import by name,
so there is no churn.
"""

# ── Indicator thresholds ──────────────────────────────────────────────
# RSI OB/OS — BB %B rescale endpoints (oscillator units; matches TV)
RSI_OVERBOUGHT = 70.0
RSI_OVERSOLD   = 30.0

# OOB detection — line is "out of boundary" / breached
BOUNDARY_HI = 85.0
BOUNDARY_LO = 15.0
