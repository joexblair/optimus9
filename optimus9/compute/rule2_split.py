"""rule2_split — the split between two r lines, and the handoff it creates. Joe 0924.

ONE JOB: given two r lines and a bar, say whether the lower line is travelling AWAY from dr while
the higher line is still travelling TOWARDS it. It owns no threshold, reads no DB, and decides no
trade. The single-line mechanics live in `rule2_trajectory`; this module never duplicates them.

JOE'S VERBATIM, 0924:
  "here's what we need: a mech that detects that ws2 is still heading towards dr while ws1r is
   travelling away from it. I'm allowing {knob:2 or 3, label:RULE2_TRAJ_CONTINUE} minutes to
   detect. testing on the minute breaks is fine, detecting the split earlier through the use of
   fancy calculations is better"

  and on the handoff, 0924: "at 23:54:15, ws2r can see that ws3r has trajectory - we need to find
  the handoff from ws2 to ws3 (ie the split timestamp between ws2r and ws3r)"

THE ARITHMETIC IS JOE'S OWN TWO PHASES, 0924:
  "phase1: calculate the difference between the current bar and the previous bar individually (the
   vertical), phase2: calculate the diff between the 2 phase1 values"
Integrated over `w` bars, phase 1 is `line[k] - line[k-w]` and phase 2 is their difference. This
module reads phase 1 on each line separately, because the two legs are asked different questions.

WHY A WINDOW AND NOT THE BAR. Measured 09-03 02:49 -> 03:02, 157 bars: the bar-to-bar test fires
on 4 bars, ALL of them minute boundaries, and is silent on the 153 bars between. The windowed test
holds a continuous state across them. It is NOT earlier — the bar test called that split at
02:53:00 and the 3 min window at 02:53:05 — it is the persistence that earns it.

`wob` IS MINE AND UNRULED. Joe set the window and never set how long the state must hold. On the
09-03 02:54 case the run lengths were 1, 1, 3, 1, 44, 3, 2, 1 bars at w=24. A `wob` of 1 fires at
02:53:15 and breaks two bars later.

NO MAGNITUDE. `rule2_trajectory.min_travel` has the same gap and the same reason: Joe 0924,
*"the true threshold is in the OOS data"*. Measured 09-03 00:18:20, ws2r was bit-for-bit unchanged
across the window and `s_hi` read 2.220446049250313e-16, one float64 epsilon, which passed.

CAUSAL. Every bar read is at or before `k`. Proven 0924 by replaying the walk forward-only with an
append-only history: identical fire bars, 09-03 02:54:35 at w=24 and 02:54:00 at w=36.
"""
import numpy as np


def split(lo_line, hi_line, dr, k, w):
    """Is the split true AT bar `k`. -> a dict, never None.

    lo_line   the lower timeframe's r — the one expected to turn away from dr
    hi_line   the higher timeframe's r — the one expected to still run towards dr
    dr        +1 or -1
    w         the window in bars. Joe's `RULE2_TRAJ_CONTINUE`, 2 or 3 minutes = 24 or 36 bars

    keys: is_split, s_lo, s_hi
    """
    lo = np.asarray(lo_line, float); hi = np.asarray(hi_line, float)
    k = int(k); w = max(1, int(w)); dr = int(dr)
    if k - w < 0:
        return {'is_split': False, 's_lo': float('nan'), 's_hi': float('nan')}
    s_lo = float(lo[k] - lo[k - w])
    s_hi = float(hi[k] - hi[k - w])
    away = (s_lo < 0) if dr > 0 else (s_lo > 0)
    towards = (s_hi > 0) if dr > 0 else (s_hi < 0)
    return {'is_split': bool(away and towards), 's_lo': s_lo, 's_hi': s_hi}


def first_split(lo_line, hi_line, dr, k0, k1, w, wob):
    """The first bar in [k0, k1] where the split has held for `wob` consecutive bars. -> bar or None.

    The bar returned is the one the run REACHES `wob` on, not the run's first bar — that is the bar
    the state is knowable on. The counter runs from `k0`, so a run already under way at `k0` starts
    its count there rather than carrying in.
    """
    run = 0
    for i in range(int(k0), int(k1) + 1):
        run = run + 1 if split(lo_line, hi_line, dr, i, w)['is_split'] else 0
        if run >= int(wob):
            return i
    return None
