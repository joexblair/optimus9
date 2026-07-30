"""
constants.py — system-wide names, and the optimus9_system boundary client.

Two distinct concepts share the magic numbers 70/30 and 85/15 and were
historically conflated under one ambiguous `high_b/low_b` name:

  • RSI OB/OS  — the endpoints the BB %B is rescaled into (oscillator units).
                 This is what makes a BB/K line read like TradingView. 70 / 30.
  • OOB        — "out of boundary": when a (rescaled) line is breached. 85 / 15.

A line is rescaled to [RSI_OVERSOLD, RSI_OVERBOUGHT], THEN OOB-detected at
[BOUNDARY_LO, BOUNDARY_HI]. Keep the two straight — never feed an OOB boundary
into a rescale slot (that was the f_bb_lookahead default bug).

The OOB boundary pair is NOT a literal here: it is read from the DB
(optimus9_system.hi_boundary / .lo_boundary) at import, same source rpl_walk
reads. The 85/15 below is an unreachable-DB fallback only, so that importing
this module can never hard-fail.
"""

# ── Indicator thresholds ──────────────────────────────────────────────
# RSI OB/OS — BB %B rescale endpoints (oscillator units; matches TV).
# Literal by design: these are rescale endpoints, not boundaries.
RSI_OVERBOUGHT = 70.0
RSI_OVERSOLD   = 30.0

# ── OOB boundary (DB client) ──────────────────────────────────────────
# Authoritative source: optimus9_system.hi_boundary / .lo_boundary (one row).
_BOUNDARY_FALLBACK = (85.0, 15.0)    # used ONLY when the DB is unreachable


def read_boundaries():
    """Return (hi, lo) from optimus9_system, or _BOUNDARY_FALLBACK if unreachable.

    Imports are deferred into the call so this module stays leaf-level: nothing
    in the DB/config path imports constants, and nothing here runs at the time
    optimus9/__init__ is still wiring itself up.
    """
    try:
        from .config import get_db_config
        from .db.database_manager import DatabaseManager
        db = DatabaseManager(**get_db_config())
        db.connect()
        try:
            row = db.execute(
                "SELECT hi_boundary, lo_boundary FROM optimus9_system LIMIT 1", fetch=True)
        finally:
            db.disconnect()
        if row:
            return float(row[0]['hi_boundary']), float(row[0]['lo_boundary'])
    except Exception:
        pass
    return _BOUNDARY_FALLBACK


# OOB detection — line is "out of boundary" / breached
BOUNDARY_HI, BOUNDARY_LO = read_boundaries()

# ── BL no-engagement fence ────────────────────────────────────────────
# Base K band inside which a breach is NOT predicted/engaged. Independent of the
# RSI rescale above (equal by default, but a separate tuning concern). bl_detect
# widens it symmetrically via --fence_pad (upper += pad, lower -= pad).
# Being homed into rpl_config separately — left literal here for now.
FENCE_HI = 70.0
FENCE_LO = 30.0
