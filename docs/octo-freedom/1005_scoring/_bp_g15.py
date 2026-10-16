"""`bounce-pred` on the g15Mage ib-cross grid. 1016. BANKED, Joe 1016.

THE BANK: *"g15 ws5/fwd/ex/xwob1/step1 +173.9969% / bank this as our state and make the machine
live. no mom-xfer"*. So the defaults below ARE his ruled state and an off-ruled run is reported by
`_ruled.check`. Net +173.9969% over the 94 built days on the banked drag of 0.1975% per trade -
gross +399.7394%, 1143 trades, drag 225.7425% = 56.5% of gross - against the superseded fixed
grid's +125.7001%.

JOE'S IDEA, 1016 verbatim: *"I have a further idea - instead of a fixed width, collect samples on
each g15Mage crossing back to ib (on the target side). the logic: we're sampling at locations that
are consistent within the market's cycles -this needs an arm - it can come from ws5Mage crossing to
target-side oob"*. Then: *"it's not clear if my g15Mage idea added value"* — so this file exists to
answer that, not to replace anything. `_bouncepred.py` is untouched and stays the default.

WHY HIS IDEA IS WORTH SCORING, measured before any of this was written: armed at the ws5Mage
HIGH-oob entry 2026-07-22 00:02:10, at the oob fence 85/15 with xwob 4 bars, his two named
continuance bars ARE g15Mage HIGH->ib crosses, exact to the second — cross 8 is 00:35:00 and cross 9
is 00:55:00. The ex-fence 83/17 gives 00:35:20 instead.

SIX GAPS ARE OPEN AND ARE JOE'S. Each is a knob here so every reading can be scored rather than
chosen:
    W_G15_SIDE   'ws5'   the g15Mage cross is on the side ws5Mage crossed to  (both his bars are
                         HIGH->ib crosses, and ws5Mage crossed to HIGH)
                 'opp'   THE OPPOSING SIDE. Joe 1016 verbatim: *"the other option I want to share:
                         sample on the opposing-side g15MAge crossing to ib - ie for a high
                         target-side (like our example 00:23), test on low oob g15Mage's crossing
                         to ib"*. So at 00:23, where ws5Mage went to HIGH oob, the samples come
                         from g15Mage crossing LOW oob -> ib.
                         'board' is accepted as the same value. It was the name I gave this option
                         before he described it, and the mechanic is identical - the side opposite
                         the arm. HIS WORD IS 'opposing'; mine was a guess at his reasoning.
    W_G15_PAIR   'fwd'   the pair is THIS cross and the NEXT cross. Matches BOTH his named bars
                 'back'  the pair is the PREVIOUS cross and THIS cross. Matches one of two
    W_G15_FENCE  the fence the g15Mage cross is measured against. 'oob' = 85/15 reproduces
                 00:35:00 exactly; 'ex' = 83/17 gives 00:35:20
    W_G15_XWOB   bars IB must hold for the cross to confirm. 4 reproduces both his bars; 1 adds 12
                 extra crosses in that 2-hour window
    W_G15_STEP   how many crosses forward the pair spans. 1 = the next cross
    W_G15_REARM  1 = every ws5Mage oob entry re-arms. 0 = the first arm holds until the verdict

WHAT IS NOT A GAP, because it carries over from the banked mech unchanged: the ws30->ws1 Mage
ladder, the median second difference in points, and W_BP_MIN_LINES.

THE WAIT IS UNBOUNDED, AND THAT IS NOT A DEFECT I MAY CAP. Joe has specified no cap. Measured on his
own window: 00:56:30 to 01:09:40 is 13.2 min and 01:09:40 to 01:29:15 is 19.6 min, against the
banked mech's fixed +10 min. `known_at` is the later of the two crosses' confirmation bars, so the
mech stays causal however long the wait runs.

SRP: this file emits a verdict on his grid. It opens no trade, closes none, holds no trade state.
"""
import os
import numpy as np

from optimus9.analysis.jig import oob_ib_cross, mage_ladder_diff
import _bouncepred as BP

SIDE = os.environ.get('W_G15_SIDE', 'ws5')
PAIR = os.environ.get('W_G15_PAIR', 'fwd')
FENCE = os.environ.get('W_G15_FENCE', 'ex')      # BANKED 'ex' = 83/17, Joe 1016
XWOB = int(os.environ.get('W_G15_XWOB', 1))      # BANKED 1 bar = 5 s, Joe 1016
STEP = int(os.environ.get('W_G15_STEP', 1))
REARM = os.environ.get('W_G15_REARM', '1') == '1'
SAMPLE_TF = int(os.environ.get('W_G15_SAMPLE_TF', 15))    # g15Mage. LD's first arg is SECONDS
EX_HI, EX_LO = 83.0, 17.0                                 # the ex-fence, momo_fence_r 17

if SIDE == 'board':
    SIDE = 'opp'                      # his word, see W_G15_SIDE above
assert SIDE in ('ws5', 'opp'), SIDE
assert PAIR in ('fwd', 'back'), PAIR
assert FENCE in ('oob', 'ex'), FENCE


class BouncePredG15:
    """His grid over one tape. Build once, then `walk`. Shares the banked ladder."""

    def __init__(self, sc, bp=None):
        n = len(sc.ts)
        self.n = n
        self.sc = sc
        self.bp = bp if bp is not None else BP.BouncePred(sc)
        self.mg, self.tfs = self.bp.mg, self.bp.tfs
        self.ladder_n = self.bp.ladder_n
        self.trig = self.bp.trig                           # ws5Mage, the arming line
        self.hi, self.lo = float(sc.HI), float(sc.LO)
        g = np.asarray(sc.LD(SAMPLE_TF * 60, 'Mage'), float)[:n]
        fh, fl = (self.hi, self.lo) if FENCE == 'oob' else (EX_HI, EX_LO)
        # THE PRODUCER IS THE JIG'S, Joe 0806. conf = the bar the cross becomes KNOWABLE.
        X = oob_ib_cross(g, fh, fl, XWOB)
        self.cross = {+1: sorted((k, c) for k, c, sd in X if sd == +1),
                      -1: sorted((k, c) for k, c, sd in X if sd == -1)}
        self.g15 = g

    def sample_side(self, arm_side):
        """Which side's g15Mage crosses this arm samples. -> +1 or -1."""
        return int(arm_side) if SIDE == 'ws5' else -int(arm_side)   # 'opp' = the opposing side

    def verdict_at(self, i, arm_side):
        """The verdict carried by cross index `i` on this arm's sample side.

        -> (the cross bar, verdict, known_at, median, lines positive, why) or None when the pair
        runs off the end of the cross list.
        """
        X = self.cross[self.sample_side(arm_side)]
        j = i + STEP if PAIR == 'fwd' else i - STEP
        if j < 0 or j >= len(X) or i < 0 or i >= len(X):
            return None
        a, b = (X[i], X[j]) if PAIR == 'fwd' else (X[j], X[i])
        ka, kb = a[0], b[0]
        if ka == kb:
            return None
        med, pos, _d = mage_ladder_diff(self.mg, ka, 0, kb - ka, self.tfs)
        v = BP.CONTINUANCE if pos >= BP.MIN_LINES else BP.REVERSE
        known = max(a[1], b[1])                            # the LATER confirmation bar
        assert known >= kb, 'known_at must not precede the later sample bar'
        why = ('%d of %d lines positive, median %+.2f between the g15Mage ib-crosses %s and %s'
               % (pos, self.ladder_n, med, self.sc.U(ka), self.sc.U(kb)))
        return X[i][0], v, known, med, pos, why

    def walk(self, frm, side=None, until=None):
        """Every verdict from the arm at `frm`, one per g15Mage ib-cross, until the first REVERSE.

        Mirrors `_bouncepred.walk`'s contract so a caller can swap grids: the walk STOPS on the
        first REVERSE and that row is the last one.
        -> [(the cross bar, verdict, known_at, median, lines positive, why)]
        """
        frm = int(frm)
        if side is None:
            v = float(self.trig[frm])
            side = +1 if v >= self.hi else (-1 if v <= self.lo else None)
            if side is None:
                return []
        # HIS ARM, 1016: *"it can come from ws5Mage crossing to target-side oob"*. The caller hands
        # the arm bar; the mech only checks the arming line is oob there, which is his own firing
        # condition for the banked mech too: *"it will only fire when ws5Mage is oob"*.
        if not self.bp.trig_oob(frm, side):
            return []
        end = self.n - 1 if until is None else int(until)
        X = self.cross[self.sample_side(side)]
        out = []
        for i, (k, c) in enumerate(X):
            if k < frm:
                continue
            if k > end:
                break
            r = self.verdict_at(i, side)
            if r is None:
                continue
            if r[2] > end:
                break
            out.append(r)
            if r[1] == BP.REVERSE:
                break
        return out
