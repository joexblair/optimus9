"""THE OPEN VOTE. 1017. JOE'S MECH.

THE FILE NAME IS A PLACEHOLDER. He has not named this mech, and nothing in this file's OUTPUT
coins a name for it - the rows say "the vote" and name each voter by HIS word for it (`lin-exh`,
`mage-cascade`; voter 1 has no name yet either). Rename on his word.

HIS SPEC, 1017 verbatim:
    *"these 3 (and more as I think about them) will form a voting based mech that need to validate
     OPEN signals. I'm not yet sure if it will extend to END signals"*
    *"1) 2 of 3 {knob}"*  - the threshold
    *"B"*  - the polarity, asked and ruled: **a vote says the OPEN IS WRONG**. 2 objections kill the
     open; fewer and it fires. Option A, where a vote says the open is valid and silence blocks it,
     was put to him beside B and rejected.
    *"I'll stop using EXHAUSTION to describe an event ... lineage exhaustion is now lin-exh"*

THE dr FRAME IS HIS AND IT IS THE OPPOSITE OF THE BANKED ONE. READ THIS BEFORE TOUCHING ANYTHING.
Joe 1017: *"I've chosen -dr because the trade is SHORT, so it needs to be guided by low side
calculations. a LONG signal would refer to high side"* / *"NOTE all of these mechs use the same dr
logic"*. So in THIS mech:
        a SHORT trade -> dr -1          a LONG trade -> dr +1
The banked machine-wide convention is the reverse - `dr +1` is SHORT, `dr -1` is LONG
(`memory/dr-plus-one-is-short`). The two live side by side ON PURPOSE because he ruled this frame
for this family of mechs. `vote()` takes the TRADE SIDE in the banked frame and converts once, in
one place, with an assert - no caller ever passes a raw dr into a voter.

THE THREE VOTERS
  1  no name yet. Joe 1017: *"a trade can only fire if ws1-3r agree with the direction of the
     trade. eg for a short, 2 of the 3 `r`'s need to be high side of 50 and showing downward
     trajectory"*. OBJECTS when fewer than VOTER1_MIN of the three agree.
       the trajectory is `_trajmech.traj`, Joe 1017: *"base it on the `traj` mech that we have in an
       earlier mech. the samples were for HTF lines - I think the sampling gap for our new lower-TF
       based mech should remain as 2 * TF width"*. So block = 2 x the line's own TF width.
       `tail` and `look` keep traj's banked 2 and 24 - MINE BY INHERITANCE, he named neither.
  2  `lin-exh`, rider TF 0. Joe 1017: *"the beginning of the mech's walk sets rider TF to 0 / from
     TF0, the walk looks for 'the 2 tfs above are in fence' / at 02:15, there are TF1 and TF2 in
     fence - lin-exh is immediately qualified"*. OBJECTS when it QUALIFIES.
       NOT RE-IMPLEMENTED: `_chain10.exhausted(0, j, d, LIN_CEIL)` is called, so the voter and
       lineage can never drift apart. Rider 0 is this file's constant, never an argument.
  3  `mage-cascade`. Joe 1017 rebuilt this one from the end-to-end diff into a CLUSTER verdict:
     *"so long as there are 4 or more consecutive TFs printing a rising or falling pattern, at the
     lower end or higher end of wsf range (eg ws1 to ws4), then the cascade's verdict is true"* /
     *"lower TF runs always outrank the higher TFs"* / *"a wider zoom is needed"*. The end-to-end
     diff did not go: *"no, it sits beside"*.
       THE MECH EMITS A DIRECTION, NOT AN OBJECTION. Joe 1017: *"dr isn't involved. we're taking a
       snapshot on one bar, making a direction verdict (up, down, neither), and providing the
       verdict for consumption"*. So `jig.mage_cascade` returns 'up' / 'down' / 'neither' and THIS
       voter does the mapping: a falling ladder is a SHORT, a rising one is a LONG, and the voter
       objects only when that disagrees with the trade.
       'neither' DOES NOT OBJECT. MINE AND STATED: under his polarity B a vote says the open is
       WRONG, and no qualifying cluster is no information rather than a disagreement.
       NOT RE-IMPLEMENTED: the walk, the zoom, the anchors and the tie-break are all
       `jig.mage_cascade`. `ride_to_max.cascade` is no longer called from here and is untouched -
       `ride_to_max.ride` still calls it.

EVERY VOTER READS ONE BAR, Joe 1017: *"yes: one bar for both mage cascade and voter 1"* /
*"we sample on a single bar, not many bars"* / on voter 1's trajectory, *"sample at the same 5s bar
as the mage cascade"*. `jig.mage_cascade_bar` picks that bar and every voter reads it.
  WHAT THIS REPLACES, kept because it was MINE AND UNRULED: a `_bucket_close` here read each line
  at its own timeframe's close, so one verdict spanned up to 9 minutes of tape and the lag was not
  even monotone in TF - at 2026-08-23 18:55:15 ws5Mage was 20 s old while ws4Mage below it was
  200 s old. Joe asked *"why is the `bar read` timestamp different for each TF? is this in the
  mech's spec?"* It was not. The spec had always read one bar.
  THE SEAM EVIDENCE THAT MOTIVATED IT STILL STANDS and is recorded, not acted on: measured 1017
  over 1,632,960 bars, the r step at a line's `:00` bar is 6.267 against 0.573 at its last bar -
  10.9x - while the 5 s price range is only 1.59x. Joe's answer to it is the extrema bar, not a
  per-line grid, and he kept the grid mode for his own later testing.

THE CLUSTER WALK AND THE BAR SEARCH ARE BOTH IN THE JIG, Joe 1017: *"produce this on the jig (and
use the jig's output) so it can't be mangled in the future"* / *"ensure this clustering logic is in
the jig"*. This file holds no ladder logic and no bar search - it reads `jig.mage_cascade`'s output.

SRP: this file answers one question - does the vote object to an open at this bar. It opens no
trade, closes none, holds no trade state and scores nothing.
CAUSAL: every bar read is at or before the event bar. Asserted in `jig.mage_cascade_bar`.
"""
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optimus9.analysis.jig import (mage_cascade, mage_cascade_bar, r_matryoshka,
                                   anchor_floater, MC_GAP, MC_MIN, MC_ZOOM)
from _trajmech import traj

ON = os.environ.get('W_VOTE_ON', '1') == '1'
# W_VOTE_MIN - how many voters must object before the open is killed. Joe 1017: *"2 of 3 {knob}"*.
# BANKED 2 OF 4, Joe 1018: *"add divergence as the 4th voter for `4-voters-against`. minimum
# 2 of 4"*. It was 2 of 3 from his 1017 *"1) 2 of 3 {knob}"*; the count of voters moved, the
# threshold did not.
MIN_OBJ = int(os.environ.get('W_VOTE_MIN', 2))
# ---- voter 1
VOTER1_TFS = tuple(int(z) for z in os.environ.get('W_VOTE_V1_TFS', '1,2,3').split(','))
VOTER1_MIN = int(os.environ.get('W_VOTE_V1_MIN', 2))     # *"2 of the 3 `r`'s"*
VOTER1_MID = float(os.environ.get('W_VOTE_V1_MID', 50))  # *"high side of 50"*
TRAJ_MULT = int(os.environ.get('W_VOTE_TRAJ_MULT', 2))   # *"2 * TF width"*, his 1008 knob's value
TRAJ_TAIL = int(os.environ.get('W_VOTE_TRAJ_TAIL', 2))   # traj's banked tail. MINE by inheritance
TRAJ_LOOK = int(os.environ.get('W_VOTE_TRAJ_LOOK', 24))  # traj's banked look. MINE by inheritance
TRAJ_KIND = os.environ.get('W_VOTE_TRAJ_KIND', 'close')
# ---- voter 2. RIDER 0 IS A CONSTANT, not a knob and not an argument - Joe 1017 asked for exactly
# that so it cannot be confused later.
VOTER2_RIDER = 0
# ---- voter 3. the cluster rules live in the jig; these only say which jig knobs to use.
CASC_LO = int(os.environ.get('W_VOTE_CASC_LO', 1))       # wsf's floor, Joe 1017
CASC_HI = int(os.environ.get('W_VOTE_CASC_HI', 12))      # wsf's ceiling, Joe 1017
CASC_ZOOM = int(os.environ.get('W_VOTE_CASC_ZOOM', MC_ZOOM))
CASC_MIN = int(os.environ.get('W_VOTE_CASC_MIN', MC_MIN))
# ---- TEST 2, Joe 1017's *"the matryoshka effect"*. It FOLLOWS the first r test and is not a
# fourth voter - his words: *"ws1r is penalised in the first 'r test', but in the new second test
# ws1r has served to prove the entire r line is reversing"*. So it can only WITHDRAW voter 1's
# objection, never add one, and MIN_OBJ does not move.
#   `not yet` CHANGES NOTHING. STRUCTURAL AND STATED: he deleted the only negative branch test 2
#   had - *"drop ... it doesn't work well when the market is voliatile (23:37 and 08:22)"* - so the
#   test has no way to say no. `not yet` is the absence of a yes, and the objection stands.
MAT_ON = os.environ.get('W_VOTE_MAT', '1') == '1'
MAT_LO = int(os.environ.get('W_VOTE_MAT_LO', 1))   # the FINE line - ws1r, which starts the walk
MAT_HI = int(os.environ.get('W_VOTE_MAT_HI', 2))   # the COARSE line - ws2r, which follows it
# ---- VOTER 4, the divergence. Joe 1017: *"add a divergence test to the suite: using ws1, ws2,
# ws3 (6 lines). divergence qualifies on >=1 line showing div / --the divergence test is bound to
# the side that printed the last oob Mage"*.
#   THE MAGE LINES ARE DROPPED, Joe 1018: *"I think the Mages are too fickle for divergence - we'll
#   drop them and use the 3 aaaarrr`s"*. So it is 3 lines, not his original 6. WHY, measured at the
#   2026-08-26 04:00:45 anchor: all three r lines fire BULLISH -1 and none of the three Mage lines
#   do - ws1Mage d_osc -7.17, ws2Mage -29.41, both making a LOWER low with price. And `mid` 50 and
#   AF_PIVOT_DEPTH 2.0 are r-SCALE numbers: ws3Mage's walk under them reached a pivot of 141.88 and
#   a floater of -5.87 nearly four hours back, because Mage is unbounded.
#   THE MACHINE IS `jig.anchor_floater`, not `jig.divergence`. Joe 1017 settled which: *"you're
#   right - anchor_floater is the correct divergence machine"*. The episode machine needs BOTH ends
#   oob by construction, which he rejected: *"it's completely illogical for them both to be oob -
#   most r divergences print an ib anchor"*.
DIV_ON = os.environ.get('W_VOTE_DIV', '1') == '1'
DIV_TFS = tuple(int(z) for z in os.environ.get('W_VOTE_DIV_TFS', '1,2,3').split(','))
DIV_MIN = int(os.environ.get('W_VOTE_DIV_MIN', 1))       # *"qualifies on >=1 line showing div"*
# W_VOTE_DIV_WEIGHT - the votes this voter casts when ALL of DIV_TFS read the same side.
#   Joe 1018: *"I'm also leaning to giving 2 votes when all 3 lines are in agreeance. that will
#   need a knob which we will have to sweep earlier than later"*. LEANING, NOT RULED - so the
#   default is 1, today's behaviour, and the value is the sweep's to settle, not mine.
DIV_WEIGHT = int(os.environ.get('W_VOTE_DIV_WEIGHT', 1))
# ---- the one bar every voter reads
# BANKED 'event' 1017, SUPERSEDING 'extrema'. Joe: *"all tests fires at the event: 04:00"*.
# His earlier 1017 preference was the extrema - *"I'd prefer the cascade to test from a single
# timestamp taken at the most recent mage extrema"* - and the extrema walk he specified is still
# built and still selectable; it is no longer the default. WHAT MOVED: on the 2026-08-26 04:00:35
# event the extrema bar is 03:53:40, 415 s earlier, where ws1r reads 13.58 against 69.49 at the
# event. Every voter was reading a different market.
BAR_MODE = os.environ.get('W_VOTE_BAR', 'event')         # event | extrema | grid. Joe 1017
BAR_GAP = int(os.environ.get('W_VOTE_BAR_GAP', MC_GAP))  # 48 bars = 4 min, Joe's own number
BAR_TF = int(os.environ.get('W_VOTE_BAR_TF', 1))         # the extrema source line's TF, ws1Mage.
#   A PARAMETER, NOT A LITERAL - Joe 1017: *"there is a future where the TF will need to be
#   dynamic, so a mode must be baked in the jig"*.


class OpenVote:
    """The vote over one tape. Build once, then `vote(bar, trade_side, event_side)`."""

    def __init__(self, sc):
        self.sc = sc
        n = len(sc.ts)
        self.n = n
        self.ts = np.asarray(sc.ts, np.int64)[:n]
        self.exl = float(sc.LG['momo_fence_r'])
        self.exh = 100.0 - self.exl
        self.r = {t: np.asarray(sc.LD(t * 60, 'r'), float)[:n] for t in VOTER1_TFS}
        # the wsf ladder the cluster walk reads. ws1..ws12, Joe 1017: *"wsf is ws1 to ws12"*.
        self.lad = {t: np.asarray(sc.LD(t * 60, 'Mage'), float)[:n]
                    for t in range(CASC_LO, CASC_HI + 1)}
        # g30Mage is sub-wsf. Joe 1017: *"printed in the table, not a rung in the cluster walk
        # -confirmed"*. It goes to the jig as `extra`, which the jig never walks.
        self.extra = {'g30Mage': np.asarray(sc.LD(30, 'Mage'), float)[:n]}
        # the extrema source line for the bar search. A PARAMETER - its TF is BAR_TF.
        self.bar_line = (self.lad[BAR_TF] if BAR_TF in self.lad
                         else np.asarray(sc.LD(BAR_TF * 60, 'Mage'), float)[:n])
        # voter 4's lines. r ONLY - the Mage lines are dropped, Joe 1018.
        self.div_r = {t: np.asarray(sc.LD(t * 60, 'r'), float)[:n] for t in DIV_TFS}
        self.div_mg = {t: np.asarray(sc.LD(t * 60, 'Mage'), float)[:n] for t in DIV_TFS}
        self.div_px = (np.asarray(sc.CLOSE, float)[:n] if sc.CLOSE is not None else self.sc.PX)
        # voter 2's lines come from lineage's own reach formula, never from a literal
        import _chain10 as C
        self._C = C
        self.lin_ceil = C.LIN_CEIL

    # ---- the one bar
    def bar_for(self, bar, event_side, mode=None, gap=None):
        """The single bar every voter reads. -> (bar, why) or None. DELEGATES to the jig.

        `event_side` is the EVENT'S side, +1 high / -1 low - Joe 1017: *"extrema must be same-side
        as the event's side (not the events' SHORT or LONG verdict)"*. It is NOT derivable from the
        trade side here and is never guessed: the caller owns it.
        """
        return mage_cascade_bar(self.bar_line, int(bar), int(event_side),
                                mode=(BAR_MODE if mode is None else mode),
                                gap=(BAR_GAP if gap is None else gap))

    # ---- test 2
    def _tdir(self, t, j):
        """ws{t}r's trajectory direction at bar `j`, voter 1's own knobs. Reads only backwards."""
        blk = TRAJ_MULT * t * 12
        return int(traj(self.r[t], int(j) + 1, blk, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND, 0)['dir'])

    def matryoshka(self, k):
        """Test 2 at bar `k`. -> `jig.r_matryoshka`'s dict, or None.

        Walks BACK from `k` on the fine line until its trajectory direction changes - that bend is
        the walk's own start and the only span the test needs. UNBOUNDED: the walk runs to the
        start of the tape if it must, because Joe has set no cap and I will not invent one.
        """
        k = int(k)
        d0 = self._tdir(MAT_LO, k)
        if d0 == 0:
            return None
        j, a = k, None
        while j > 0:
            j -= 1
            d = self._tdir(MAT_LO, j)
            if d != 0 and d != d0:
                a = j
                break
        if a is None:
            return None
        n = k - a + 1
        dl = np.zeros(n, np.int8)
        dh = np.zeros(n, np.int8)
        for i in range(n):
            dl[i] = self._tdir(MAT_LO, a + i)
            dh[i] = self._tdir(MAT_HI, a + i)
        r = r_matryoshka(dl, dh, k - a)
        for key in ('walk_bar', 'hi_bar'):          # back onto the tape's own bar numbers
            if r[key] is not None:
                r[key] += a
        return r

    # ---- voter 1
    def voter1(self, k, dr):
        """Do fewer than VOTER1_MIN of ws1-3r agree with the trade. -> (objects, why).

        `k` is the ONE bar, Joe 1017: *"sample at the same 5s bar as the mage cascade"*. Both the
        level read and the trajectory anchor sit on it.
        dr is HIS frame: -1 for a SHORT, +1 for a LONG. A SHORT wants each line high side of 50 and
        travelling DOWN; a LONG wants low side of 50 and travelling UP.
        """
        want_high = dr < 0                       # a SHORT, in his frame
        want_dir = +1 if dr > 0 else -1
        agree, rows = 0, []
        for t in VOTER1_TFS:
            v = float(self.r[t][k])
            blk = TRAJ_MULT * t * 12             # 2 x TF width, in 5 s bars
            tr = traj(self.r[t], k + 1, blk, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND, 0)
            lvl = (v > VOTER1_MID) if want_high else (v < VOTER1_MID)
            ok = lvl and tr['dir'] == want_dir
            agree += 1 if ok else 0
            rows.append('ws%dr %.2f %s 50, traj %+d, %s'
                        % (t, v, 'above' if v > VOTER1_MID else 'below', tr['dir'],
                           'agrees' if ok else 'does not agree'))
        objects = agree < VOTER1_MIN
        return objects, ('%d of %d agree, min %d | %s'
                         % (agree, len(VOTER1_TFS), VOTER1_MIN, '; '.join(rows)))

    # ---- voter 2
    def voter2(self, k, dr, trade_side=None, event_side=None):
        """Does `lin-exh` qualify at rider 0, and does that COUNT AGAINST this trade. -> (obj, why).

        THE POLARITY IS JOE'S, 1017, CONFIRMED. Qualifying means no lin-hop TF can take the baton -
        no momentum left on the side being measured. Whether that is an objection or a confluence
        depends on which way the trade runs relative to the EVENT's side:
            the event side low,  a SHORT runs TOWARD the low  -> nothing can carry it further down
                                                                 -> OBJECTS
            the event side low,  a LONG  runs AWAY from it    -> nothing is pulling it down
                                                                 -> CONFLUENCES, no objection
        and the mirror on the high side. His two calls that fix it:
          2026-08-22 02:15 SHORT off a low  - *"lin-exh is immediately qualified"*, given as the
                                              reason to block
          2026-08-22 02:07 LONG off the same low - *"my view is lin-exh confluencing, not
                                              objecting"* / *"the event is saying 'there is no
                                              DOWNWARD momentum, so a LONG is valid'"*
        TOWARD is `event_side * trade_side < 0` in the BANKED frame, where +1 is SHORT. Both of his
        calls check out against that one line.
          WHAT THIS REPLACES: the voter objected whenever lin-exh qualified, on either side. Joe
          caught it on the 2026-08-26 04:00:35 LONG: *"if it qualifies at rider 0, why does it
          object to LONG?"*. Inverting it on the 41 signals of 2026-08-22..24 moved 27 verdicts.

        UNRULED AND DISCLOSED, SEPARATELY: `_chain10.bnd` is one-sided, so at d = -1 a `.` means
        only `v > 17` with no upper bound. I told Joe it was side-independent and that was wrong.
        Which reading of his *"the 2 tfs above are in fence"* applies is still his to rule.
        """
        txt = self._C.exhausted(VOTER2_RIDER, k, +1 if dr > 0 else -1, self.lin_ceil)
        if txt is None:
            return False, 'lin-exh does not qualify at rider %d' % VOTER2_RIDER
        if trade_side is None or event_side is None:
            return True, ('lin-exh QUALIFIES at rider %d, polarity UNTESTED - no sides passed - %s'
                          % (VOTER2_RIDER, txt))
        toward = int(event_side) * int(trade_side) < 0
        word = ('the trade runs TOWARD the %s side the test measures, so nothing is left to carry '
                'it - OBJECTS' if toward else
                'the trade runs AWAY from the %s side the test measures, so nothing opposes it - '
                'CONFLUENCE, no objection') % ('high' if int(event_side) > 0 else 'low')
        return bool(toward), ('lin-exh QUALIFIES at rider %d | %s | %s'
                              % (VOTER2_RIDER, word, txt))

    # ---- voter 3
    def voter3(self, k, dr):
        """Does the mage-cascade's direction disagree with the trade. -> (objects, why).

        `jig.mage_cascade` owns the ladder, the zoom, the anchors and the tie-break, and returns a
        DIRECTION with no dr in it. The mapping onto a trade side is this voter's job and only
        this voter's: a falling ladder is a SHORT, a rising one is a LONG.
        """
        c = self.cascade(k)
        if c is None:
            return False, 'a wsf Mage line was not finite at the bar'
        if c['verdict'] == 'neither':
            return False, 'no qualifying cluster | %s' % c['why']
        casc_dr = -1 if c['verdict'] == 'down' else +1       # down = SHORT = dr -1 in his frame
        objects = casc_dr != int(dr)
        return bool(objects), ('the cascade reads %s = %s, the trade is %s - %s | %s'
                               % (c['verdict'], 'SHORT' if casc_dr < 0 else 'LONG',
                                  'SHORT' if dr < 0 else 'LONG',
                                  'DISAGREES' if objects else 'agrees', c['why']))

    def cascade(self, k):
        """The jig's mage-cascade at bar `k`. -> the jig's dict, or None. Adds nothing to it."""
        return mage_cascade(self.lad, int(k), CASC_LO, CASC_HI, CASC_ZOOM, CASC_MIN,
                            extra=self.extra)

    # ---- voter 4
    def div_side(self, k):
        """The side the LAST oob Mage printed at or before `k`. -> (+1 high, -1 low, bar) or None.

        NO LONGER READ BY `voter4`. Joe 1017's rule was *"the divergence test is bound to the side
        that printed the last oob Mage (eg, low oob at 04:00:35)"*, and it is SUPERSEDED for this
        voter - see `voter4`. Kept because it is a clean read of a real thing and the trace still
        prints it, so a reader can see what the bound side WOULD have been.
        """
        k = int(k)
        out = None
        for t in DIV_TFS:
            v = self.div_mg[t][:k + 1]
            w = np.flatnonzero((v >= self.sc.HI) | (v <= self.sc.LO))
            if not len(w):
                continue
            b = int(w[-1])
            if out is None or b > out[1]:
                out = (+1 if float(v[b]) >= self.sc.HI else -1, b, t)
        return out

    def voter4(self, k, trade_side):
        """Does the divergence fail to support this trade. -> (objects, why).

        `trade_side` is the BANKED frame: +1 SHORT, -1 LONG, AND IT IS THE dr HANDED TO THE
        DIVERGENCE MACHINE. Joe 1018, asked to confirm: *"1. confirm your `dr` is the byproduct of
        SHORT or LONG"* - it is.
            a SHORT, +1 -> dr +1 -> a high anchor  -> BEARISH +1 fires
            a LONG,  -1 -> dr -1 -> a low anchor   -> BULLISH -1 fires
        so `fired == trade_side` is the support test with no conversion. THIS IS THE BANKED FRAME,
        not his 1017 voter frame that voters 1-3 use - `anchor_floater`'s own dr is the banked one.

        WHAT THIS REPLACES, and it was a real fault: the dr came from the BOUND SIDE - the side the
        last oob Mage printed - per his 1017 *"the divergence test is bound to the side that printed
        the last oob Mage"*. `anchor_floater` can only ever fire in the direction of the dr it is
        given, so whenever the bound side disagreed with the trade under test the voter objected
        AUTOMATICALLY, whatever the data said. Measured over the 13 MAE-cap stops of 2026-08-26:
        the bound side disagreed on 10, the voter objected on all 10, and it was never once silent
        when they disagreed. On 2026-08-26 10:43:35, 17:35:35 and 21:48:20 all three r lines fired
        a unanimous +1 and the voter still objected to the LONG. Joe caught it: *"is the divergence
        correctly faced? the votes are objections, but divergence results are allowing"*, and ruled
        the fix: the trade's own direction.
          SO THE BOUND SIDE IS SUPERSEDED HERE. `div_side` still exists and the trace still prints
          what it would have said, but it decides nothing.

        THE POLARITY MATCHES THE OTHER THREE: every voter in this suite objects when the evidence
        runs AGAINST the trade. A divergence that supports the trade is silence, not an objection.
        """
        if not DIV_ON:
            return False, 'the divergence voter is off'
        ts = int(trade_side)
        assert ts in (+1, -1), 'trade_side is the banked dr: +1 SHORT, -1 LONG'
        rows, hits, signs = [], 0, []
        for t in DIV_TFS:
            d = anchor_floater(self.div_r[t], self.div_px, ts, int(k))
            if d is None:
                rows.append('ws%dr no anchor/floater at dr %+d' % (t, ts))
                signs.append(0)
                continue
            st = int(d['state'])
            # SHAPE A, Joe 1018: *"I'm choosing A because the 2 examples make sense and both return
            # a profit"*. ONE call at the trade's own dr, and `state`'s SIGN decides - so a PM
            # whose sign matches the tested side COUNTS AS SUPPORT, not as an absence of evidence.
            # The magnitude is carried in the trace and gates nothing: 1 is a divergence, 2 a PM.
            #   WHAT A DOES NOT SEE, stated because it is a real limit: a divergence that exists
            #   only at the OPPOSITE dr. At 2026-08-26 10:35:05 ws1r and ws2r both read +1 at
            #   dr +1 - divergences for the SHORT - and A, testing the LONG, reads their -2 PM
            #   instead. Joe took A knowing that.
            signs.append(0 if st == 0 else (1 if st > 0 else -1))
            if st != 0 and (1 if st > 0 else -1) == ts:
                hits += 1
            rows.append('ws%dr anchor %.2f, floater %.2f at %s, d_osc %+.2f, d_px %+.5f, state %+d%s'
                        % (t, d['anchor'][1], d['floater'][1], self.sc.U(d['floater'][0]),
                           d['d_osc'], d['d_px'], st, ' PM' if d['pm'] else ' div'))
        sd = self.div_side(k)
        note = ('the bound side would have been %s oob from ws%dMage at %s, NOT READ'
                % ('high' if sd[0] > 0 else 'low', sd[2], self.sc.U(sd[1]))) if sd else \
               'no oob Mage has printed yet'
        objects = hits < DIV_MIN
        # UNANIMITY. All of DIV_TFS reading the SAME non-zero side casts DIV_WEIGHT votes instead
        # of one. It only ever amplifies an OBJECTION - a unanimous reading that SUPPORTS the trade
        # raises no objection to weight.
        unan = len(set(signs)) == 1 and signs[0] != 0
        w = int(DIV_WEIGHT) if (objects and unan) else 1
        return bool(objects), ('%d of %d lines support the %s at dr %+d, min %d%s | %s | %s'
                               % (hits, len(DIV_TFS), 'SHORT' if ts > 0 else 'LONG', ts, DIV_MIN,
                                  ' | UNANIMOUS %+d, so %d vote%s' % (signs[0], w,
                                                                      '' if w == 1 else 's')
                                  if unan else '',
                                  note, '; '.join(rows))), w

    # ---- the vote
    def vote(self, bar, trade_side, event_side, mode=None):
        """Does the vote KILL this open. -> (kills, objections, [(name, objects, why)], bar, why).

        `trade_side` is the BANKED frame: +1 SHORT, -1 LONG. It is converted to Joe's 1017 frame
        for these mechs ONCE, here, and never passed raw into a voter.
        `event_side` is the EVENT'S side, +1 high / -1 low - the ws1cp's oob side, which Joe 1017
        separated from the trade verdict: *"extrema must be same-side as the event's side (not the
        events' SHORT or LONG verdict)"*. REQUIRED, NOT DEFAULTED: deriving it from `trade_side`
        would be exactly the thing he ruled out. STRUCTURAL AND STATED - the caller owns it.
        The returned bar is the ONE bar all three voters read.
        """
        if not ON:
            return False, 0, [], None, 'the vote is off'
        ts = int(trade_side)
        assert ts in (+1, -1), 'trade_side is the banked dr: +1 SHORT, -1 LONG'
        dr = -ts                       # Joe 1017: a SHORT is dr -1 in this family of mechs
        got = self.bar_for(bar, event_side, mode=mode)
        if got is None:
            return False, 0, [], None, 'no same-side extrema before the tape starts'
        k, bwhy = got
        rows = []
        for nm, fn in (('ws1-3r agreement', self.voter1), ('lin-exh', self.voter2),
                       ('mage-cascade', self.voter3), ('divergence', self.voter4)):
            if nm == 'lin-exh':
                o, why = fn(k, dr, ts, int(event_side))
            elif nm == 'divergence':
                o, why, dw = fn(k, ts)               # the BANKED side, not his 1017 voter frame
            else:
                o, why = fn(k, dr)
            if nm == 'ws1-3r agreement' and o and MAT_ON:
                # TEST 2 FOLLOWS THE FIRST r TEST. It is called only when that test objects,
                # because it can only withdraw an objection - see the block at the top.
                mat = self.matryoshka(k)
                if mat is not None and mat['state'] == 'follows':
                    o = False
                    why = 'WITHDRAWN by test 2 - %s | the first r test said: %s' % (mat['why'], why)
                else:
                    why = '%s | test 2: %s' % (why, 'no walk' if mat is None else mat['why'])
            rows.append((nm, bool(o), why))
        # THE TALLY IS WEIGHTED. Every voter casts 1 except the divergence voter under unanimity,
        # which casts W_VOTE_DIV_WEIGHT. `n` is votes, not voters, and MIN_OBJ compares against it.
        n = sum((dw if nm == 'divergence' else 1) for nm, o, _w in rows if o)
        return n >= MIN_OBJ, n, rows, k, bwhy
