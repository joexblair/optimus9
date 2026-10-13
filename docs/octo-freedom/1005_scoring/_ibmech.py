"""THE ws1Mage IB-CROSS MECH. 1012. Joe's design, built from his rulings only.

SRP: this file owns the IB-cross mech and nothing else. The lineage walk lives in `_chain10.py` and
is not touched here. Joe 1012: *"we're heading to a machine that relies on lineage plus this new
Mage based mech. I don't have a roadmap yet"* - so the two stay separate until he joins them.

THE ENTRY
  a ws1-cp's ws1Mage oob -> IB cross. Joe 1012: *"the 03:45 signal was created by a high oob
  ws1Mage to IB cross. it is absolutely a SHORT position"*.
    HIGH-side cp -> SHORT, target board LOW.   LOW-side cp -> LONG, target board HIGH.
  The trade heads AWAY from the board its own cp fired on.

THE cp, TWO QUALIFIERS
  MODE 1  ws1r AND ws1Mage both oob the same side, held W_IB_DWELL bars.
  THE SUB-wsf RETROFIT IS DROPPED. Joe 1012: *"drop the sub-wsf retrofit"*. It qualified a cp from
    ws1r oob + ws1Mage near the boundary + 2 of g5/g15/g30Mage oob-and-beyond. Measured over
    07-10 to 07-24 the scenario it targets - ws1r oob while ws1Mage falls short - occurs 1641 times
    and reverses 635 of them, 38.7%; with the g 2-of-3 filter 228 of 560, 40.7%, against 37.7%
    without it. 3.0 points of separation and a median forward move of -0.0827%. Retrofitting it
    also cut the 07-18 02:31 SHORT from +4.7330% to +0.3081% by filling the silences that carried
    it. No W_IB_BND, no W_IB_NEAR, no W_IB_GN, no g-line reads. Nothing here to re-enable.

THE g30Mage DELEGATION, Joe 1012: *"I want to use g30Mage's oob cross to ib to bring the
  ws1-cp-ib event closer to the peak. the delegation to g30 would happen as soon as ws1Mage has
  reversed by 6 bars. I feel that it's safe, because if ws1Mage turns back away from 50, g30 will
  also feel the same adversion from IB"*, and after the three legs: *"I'm happy with it"*.
  THE DELEGATION MOMENT is W_IB_G30_BARS bars past the bar that set ws1Mage's RUNNING extreme on the
  cp side, tracked forward from the cp. Causal - the running extreme only ever looks back.
  FROM THERE the decision bar is the first g30Mage oob -> IB cross.
  FALLBACK: when g30Mage is already in-fence at the delegation moment there is no cross to take, so
  the decision bar stays the ws1Mage IB bar. That fired once in the three legs, at the 07-18
  04:11:40 cp, and it preserved the -1.54 RIDE that carried the SHORT.
  HIS SAFETY ARGUMENT IS MEASURED: on every firing g30Mage crossed into the fence while ws1Mage was
  still oob, 3.4 to 6.8 min ahead of it. Nothing moved later.
  THE READING THAT LOST. "reversed by 6 bars" could also mean the first adverse 6-bar 2-point diff.
  On the 07-18 12:02:15 cp that fires at 12:03:00 on a -1.95 blip while ws1Mage is still climbing to
  135.73, 4.25 min before the extreme. Both readings reached the same g30 cross there, but the diff
  reading triggers on noise. Reading A is what is built.

THE DECISION, at TARGET-side cps only
  Joe 1012: *"03:45 is same-side as 02:17, so it can't be the exit because it is not on the target
  side"*. At a target-side cp, walk to the bar ws1Mage reaches in-fence held W_IB_WOB bars - the
  decision bar - and read the FIRST in-fence ws{T}Mage above ws1, chosen AT THE cp BAR:
    moving TOWARD the target board -> RIDE.   AWAY from it -> REVERSE.
  THE REFERENCE IS THE cp, Joe 1012: *"the reference is the cp"*. He tried the line's own window
  extreme and rolled it back: it reversed every leg on its first decision, 0 rides in 3 legs.
  NO DELAY WHEN ws1Mage IS ALREADY IB, Joe 1012: *"because ws1Mage is already IB at ~14:53, there
  is no delay in creating the SHORT position"*. The decision bar is then the cp bar itself.

THE 5-MINUTE GRACE, WHICH *IS* THE VERDICT
  Joe 1012: *"each signal has 5 minutes grace to decide on a REVERSE verdict"*, and earlier
  *"a verdict can only be flipped to REVERSE - a RIDE verdict at the ws1cp-ib allows us the option
  to REVERSE, the same is not true for the inverse"*.
  So the decision bar does NOT carry a snapshot verdict. It OPENS a W_IB_REVWALK-bar window, and
  the verdict is whether a REVERSE prints inside it:
      a REVERSE anywhere in the window -> REVERSE, at that bar. The trade closes.
      no REVERSE in the whole window   -> RIDE. The trade continues.
  THE RATCHET IS INHERENT: the first REVERSE bar ends the window, so nothing after it can read back
  to a RIDE. A RIDE is only ever declared by the window ending without one.
  THIS REPLACED A SNAPSHOT VERDICT AT THE DECISION BAR, which was mine and which broke on the
  no-delay case: when ws1Mage is already IB the decision bar IS the cp bar, so the line's move from
  the cp is 0.00 by construction and a strict "toward" test read it as REVERSE every time. The
  window has no such degenerate bar.

SILENCE RIDES, Joe 1012: *"silence rides. the logic: we're hunting for actionable data that
  eventually must print ... that weakness shows up on the Mage scan at at least one ws1-cp-ib event
  per leg"*.

THE LADDER, Joe 1012: *"the lines run from g5 to ws24, then 30,45,60,90"*. Above ws1 the scan is
  ws2..ws24 then ws30, ws45, ws60, ws90, cut at W_IB_CEIL. ws25-ws29 and ws120 are in the cache but
  NOT in the design and are excluded - an earlier run reached ws27 and closed a leg on it.

CAUSAL: every value a decision reads sits at or before its own decision bar. The pxs figures a
  caller prints afterwards are backtest validation and are not inputs.
"""
import os
import numpy as np

# ---- knobs
CEIL     = int(os.environ.get('W_IB_CEIL', 30))       # the highest TF the in-fence scan may reach
DWELL    = int(os.environ.get('W_IB_DWELL', 4))       # the mode-1 cp hold, bars
WOB      = int(os.environ.get('W_IB_WOB', 24))        # the ws1Mage IB-cross hold, bars
REVWALK  = int(os.environ.get('W_IB_REVWALK', 60))    # the grace window, bars = 5 min
G30     = os.environ.get('W_IB_G30', '1') == '1'      # delegate the decision bar to g30Mage
G30BARS = int(os.environ.get('W_IB_G30_BARS', 6))     # bars past ws1Mage's running extreme
assert DWELL >= 1 and WOB >= 1 and REVWALK >= 0

LADDER_ALL = list(range(1, 25)) + [30, 45, 60, 90]


class IBMech:
    """The mech over one tape. Build once, then `walk()`.

    DOCSTRING CORRECTED 1013: it promised `entries()` and `walk()` and neither existed - the walk
    lived in throwaway drivers, which is how a lineage walk got substituted for it at the
    2026-07-18 18:12:00 bar. `walk()` is now here, the one place that owns it.
    """

    def __init__(self, sc):
        self.sc = sc
        n = len(sc.ts); self.n = n
        self.hi, self.lo = float(sc.HI), float(sc.LO)
        w = sc.LG
        self.xl = float(w['momo_fence_r']); self.xh = 100.0 - self.xl
        self.tfs = [t for t in LADDER_ALL if t <= CEIL]
        self.mg = {}
        for t in self.tfs:
            self.mg[t] = np.asarray(sc.LD(t * 60, 'Mage'), float)[:n]
        self.r1 = np.asarray(sc.LD(60, 'r'), float)[:n]
        m1 = self.mg[1]
        self.ib_now = (m1 > self.xl) & (m1 < self.xh)
        g = np.asarray(sc.LD(30, 'Mage'), float)[:n]
        self.g30 = g
        self.g30_ib = (g > self.xl) & (g < self.xh)

    # ---- the cp qualifier
    def _mode1(self, j, d):
        r, m = self.r1[j], self.mg[1][j]
        return (r >= self.hi and m >= self.hi) if d > 0 else (r <= self.lo and m <= self.lo)

    def cps(self, a, b):
        """-> [(bar, side)] for both sides, in bar order. Mode 1 only."""
        out = []
        for d in (+1, -1):
            run = 0
            for j in range(max(a, 1), b + 1):
                run = run + 1 if self._mode1(j, d) else 0
                if run == DWELL:
                    out.append((j, d))
        out.sort(key=lambda z: (z[0], -z[1]))
        return out

    # ---- the IB cross
    def ib_bar(self, cp):
        """The bar ws1Mage is in-fence held WOB bars. The cp bar itself when it is already IB
        and stays IB for the hold - Joe 1012: *"there is no delay"*. -> bar, or None."""
        run = 0
        for q in range(cp, self.n):
            run = run + 1 if self.ib_now[q] else 0
            if run == WOB:
                return q
        return None

    def ib_bar_nodelay(self, cp):
        """The decision bar for a cp whose ws1Mage is ALREADY in-fence: the cp bar itself."""
        return cp if self.ib_now[cp] else self.ib_bar(cp)

    def g30_deleg(self, cp, d):
        """-> (delegation bar, g30 oob->IB cross bar). Either may be None. CAUSAL.

        The running extreme only looks back, and the cross is found forward of the delegation
        moment, so nothing is read before it is knowable.
        """
        if not G30:
            return None, None
        ext = self.mg1_at(cp); extb = cp
        m1 = self.mg[1]
        for j in range(cp, self.n):
            v = m1[j]
            if (v > ext) if d > 0 else (v < ext):
                ext, extb = v, j
            if j - extb == G30BARS:
                if self.g30_ib[j]:
                    return j, None          # already in-fence: no cross to take
                for q in range(j, self.n):
                    if self.g30_ib[q] and not self.g30_ib[q - 1]:
                        return j, q
                return j, None
        return None, None

    def mg1_at(self, j):
        return float(self.mg[1][j])

    def decision_bar(self, cp, d):
        """-> (bar, via). The g30 cross when the delegation fires, else the ws1Mage IB bar."""
        base = self.ib_bar_nodelay(cp)
        if G30:
            _dm, gx = self.g30_deleg(cp, d)
            if gx is not None:
                return gx, 'g30 cross'
        return base, 'ws1Mage IB'

    # ---- the decision
    def line_at(self, cp):
        """The first in-fence ws{T}Mage above ws1 AT THE cp BAR. -> T, or None for silence."""
        for t in self.tfs[1:]:
            if self.xl < self.mg[t][cp] < self.xh:
                return t
        return None

    def walk(self, k0, dr):
        """THE CLOSE EVENT FOR AN OPEN TRADE. -> (close bar, why, rows). 1013, closing link 2.

            k0   the bar the trade opened on
            dr   the trade's side at its open. +1 a SHORT, -1 a LONG.

        The board is -dr, the end the trade is heading to, set once at the open - the same rule
        `_chain10.run_leg` carries. DECISIONS HAPPEN ONLY AT TARGET-SIDE cps, Joe 1012: *"03:45 is
        same-side as 02:17, so it can't be the exit because it is not on the target side"*. A cp on
        the trade's own side is skipped without a decision.

        At each target-side cp the decision bar is taken (the g30 delegation when it fires, else the
        ws1Mage IB bar) and the 5-minute grace window gives the verdict. The FIRST REVERSE closes
        the trade, at the bar it printed on. RIDE and SILENT carry the walk to the next cp.

        CAUSAL, AND A FORWARD LOOP - Joe's form: the cp dwell is counted forward from `k0`, bar by
        bar, and nothing is read past the bar being decided. `cps()` is not used here because it
        materialises every cp on the tape for both sides; this scans the board's side only, from the
        open, and stops at the close.
        """
        d = -int(dr)
        assert d in (-1, 1), 'the trade side must be +1 SHORT or -1 LONG, got %r' % (dr,)
        rows = []
        run = 0
        j = max(int(k0), 1)
        while j < self.n:
            run = run + 1 if self._mode1(j, d) else 0
            if run != DWELL:
                j += 1
                continue
            cp = j
            dec, via = self.decision_bar(cp, d)
            if dec is None:
                rows.append((cp, 'no decision bar on the tape', None, None))
                break
            kind, t, bar, move = self.verdict(cp, dec, d)
            rows.append((cp, '%s via %s' % (kind, via), dec,
                         None if t is None else ('ws%dMage %+.2f' % (t, move))))
            if kind == 'REVERSE':
                return bar, 'REVERSE at a target-side ws1-cp', rows
            j = max(j, dec) + 1
            run = 0
        return None, 'no REVERSE on the tape after the open', rows

    def verdict(self, cp, dec, tgt):
        """THE 5-MINUTE GRACE IS THE VERDICT. -> (kind, T, bar, move).

        kind 'REVERSE' with the bar it printed on, 'RIDE' when the window closed without one, or
        'SILENT' when no line above ws1 was in-fence at the cp. The reference is the cp - Joe 1012:
        *"the reference is the cp"*. The window is [dec, dec + REVWALK], so the decision bar itself
        is inside it and a line already adverse there reverses immediately.
        """
        t = self.line_at(cp)
        if t is None:
            return 'SILENT', None, None, None
        end = min(dec + REVWALK, self.n - 1)
        for q in range(dec, end + 1):
            mv = self.mg[t][q] - self.mg[t][cp]
            if q == dec and mv == 0.0:
                continue          # the no-delay bar: a zero move is the window opening, not a verdict
            toward = (mv < 0) if tgt < 0 else (mv > 0)
            if not toward:
                return 'REVERSE', t, q, mv
        return 'RIDE', t, end, self.mg[t][end] - self.mg[t][cp]
