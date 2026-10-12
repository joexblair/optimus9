"""THE gc GATE — the two tests that defer an exhaustion verdict. Joe 1011. SRP: gates only.

This module owns ONLY the gc readings. It does not know what a leg is, never decides an exit, and
holds no state across calls. `_chain10` consumes it at the exhaustion site.

Spec: docs/octo-freedom/1011_gc_defer.md, Joe's words quoted against each clause.

  THE LINES. score39's LD takes a timeframe in SECONDS, so gcws15 is the 15-SECOND line and gcws30
  the 30-second line, with ws1 at 60 s. That is why g15r leads g30r leads ws1 - faster lines lead
  slower ones, which is Joe's matryoshka.

  THE 10-SECOND SAMPLING IS LOAD-BEARING. Joe: *"sample every 10 seconds for 4 minutes"*, raised to
  6 minutes. 10 s = every 2nd bar on the 5 s grid; 6 min = 72 bars = 36 samples. The extrema hunt
  and the diff BOTH run on those samples, not on raw bars - otherwise the sampling step would have
  no effect on anything and his instruction would be decorative. MY READING, stated.

  THE 2-MINUTE GAPS. Joe: *"walk backwards in 2 minute gaps to look forward for the counter-side
  extrema"*. 2 min = 24 bars = 12 samples. The 6-minute span holds exactly 3 gaps, so the walk is at
  most 3 steps. The stop rule is the block sampler's: stop at the first gap that adds nothing
  better. His example: *"the g15 high extrema at ~04:12 would be found by a backward walk to
  04:11:30, and validated at 04:09:30"*.

  THE VALIDATION BAR is the oldest bar of the gap that added nothing. Joe: *"the 'validated at' is
  not in divergence machine"*, so this module reports it.

  CAUSAL. Every bar read is at or before `j`. The walk is backward. An assert below enforces it.
"""
import os
import numpy as np

MID = 50.0
STEP = int(os.environ.get('W_GC_STEP', 2))        # 10 s at the 5 s grid
SPAN = int(os.environ.get('W_GC_SPAN', 72))       # 6 min
GAP = int(os.environ.get('W_GC_GAP', 24))         # 2 min
FLIP_HOLD = int(os.environ.get('W_GC_FLIP', 12))  # 1 min, the blip rule


class GC:
    def __init__(self, r15, r30, m15, hi, lo, n):
        self.r15 = np.asarray(r15, float)[:n]
        self.m15 = np.asarray(m15, float)[:n]
        self.r30 = np.asarray(r30, float)[:n]
        self.hi, self.lo, self.n = float(hi), float(lo), int(n)

    # ---- gate 1: position. gcws30r ONLY, on the WRONG side of 50 for the leg side.
    #
    # CHANGED 1012. Joe: *"position gate on g30r only - this example at 14:05 shows that g15r can
    # be anywhere infence"*. At 14:05:00 on 07-17 the gate failed on g15r 50.26 against g30r 24.50
    # while the trajectory gate passed - g15r had already crossed 50 on its way to 84.98 at
    # 14:10:30. Requiring the LEADER to still be on the wrong side meant the gate could only fire
    # before the leader had started moving, which is the opposite of the setup it is meant to catch.
    #
    # g15r's job is the TRAJECTORY gate. g30r's job is the POSITION gate. One line, one test.
    def pos(self, j, d):
        """SHORT (d<0) rides the LOW oob, so ABOVE 50 is the side still to be given up."""
        b = float(self.r30[j])
        if not np.isfinite(b):
            return False
        return (b < MID) if d > 0 else (b > MID)

    # ---- gate 2: the counter-side extrema, then the diff
    def anchor(self, j, d):
        """-> (anchor_bar, validation_bar, diff, gaps_walked) or None.

        The counter-side extreme is the HIGH for a falling SHORT, the LOW for a rising LONG.
        """
        lo_b = j - SPAN
        if lo_b < 0:
            return None
        best = None; best_bar = None; val_bar = None; walked = 0
        for g in range(1, SPAN // GAP + 1):
            hi_i, lo_i = j - (g - 1) * GAP, j - g * GAP
            idx = [i for i in range(lo_i, hi_i) if (j - i) % STEP == 0]
            if not idx:
                continue
            vals = self.r15[idx]
            ok = np.isfinite(vals)
            if not ok.any():
                continue
            walked = g
            m = int(np.nanargmax(vals)) if d < 0 else int(np.nanargmin(vals))
            cand, cand_bar = float(vals[m]), idx[m]
            better = best is None or ((cand > best) if d < 0 else (cand < best))
            if better:
                best, best_bar = cand, cand_bar
            else:
                val_bar = lo_i
                break
        if best_bar is None:
            return None
        if val_bar is None:
            val_bar = lo_b
        assert best_bar <= j and val_bar <= j, 'the gc extrema walk read past its own bar'
        return best_bar, val_bar, float(self.r15[j]) - best, walked

    def raw_sign(self, j, d):
        """sign of the anchor-to-now diff. +1 rising, -1 falling, 0 flat or no anchor."""
        a = self.anchor(j, d)
        if a is None:
            return 0
        _, _, diff, _ = a
        return 0 if diff == 0 else (1 if diff > 0 else -1)

    def qualified_sign(self, j, d, hist):
        """THE BLIP RULE. Joe: a flip in the sign must survive FLIP_HOLD bars before it counts.
        SHORT-CIRCUIT, Joe: *"if the 12 bars follow the line into oob then the qualification is
        automatically given"* - g15r oob alone, NOT g15Mage too. That asymmetry is Joe's POI.

        `hist` is the caller's dict of {bar: raw_sign}; this is a pure function of it.
        """
        s = hist.get(j, 0)
        if s == 0:
            return 0
        k = j
        while k - 1 >= 0 and hist.get(k - 1, 0) == s:
            k -= 1                                   # k = the first bar of this sign run
        if (j - k + 1) >= FLIP_HOLD:
            return s
        for i in range(k, j + 1):                    # the short-circuit, g15r oob only
            v = float(self.r15[i])
            if np.isfinite(v) and (v >= self.hi or v <= self.lo):
                return s
        return 0

    def oob_side(self, j, d):
        """g15Mage AND g15r both oob. -> +1 high, -1 low, 0 not yet.

        THIS ANSWERS ONE QUESTION ONLY: has the walk's momentum arrived on a board. Joe 1012:
        *"both g15r and g15Mage are needed to complete the walk"*. The caller may use it to END a
        gc hold and let the walk carry on. It may NOT be used to close a leg - Joe 1012: *"the only
        banked back stop is dr-flip. I asked you earlier to remove g15 as an exit option"*.
        """
        a, m = float(self.r15[j]), float(self.m15[j])
        if not (np.isfinite(a) and np.isfinite(m)):
            return 0
        if a >= self.hi and m >= self.hi:
            return +1
        if a <= self.lo and m <= self.lo:
            return -1
        return 0
