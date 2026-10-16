"""`bounce-pred`. 1016. JOE'S NAME, JOE'S MECH.

HIS SPEC, 1016 verbatim: *"bake the `bounce-pred` mech - it's a last mile improvment that needs to
slot in directly after ws5Mage oob. -it will only fire when ws5Mage is oob, and will fire on each
ws5Mage reversing until `continuance` is no longer printed, ie `continuance` will flip to `reverse`
--in our 07-22 00:23 to 01:08 EXAMPLE, the `continuance` events are 00:35, 00:55, and the `reverse`
event prints at ~01:08:45 -`bounce-pred` is not applied to a `turn-detection` event"*.

WHAT THE TWO VERDICTS MEAN, from his own description of the two reference bars:
    *"T23 is when ws5Mage is oob and starts bouncing on high oob while it has to wait for a higher
     TF to complete its journey to ws5Mage oob side / T50 is when that bouncing stops - it's the
     pivot"*
  continuance  the bouncing is still running. A higher TF has not finished its journey. WAIT
  reverse      the bouncing has stopped. This is the pivot. The entry is good
I HAD THESE THE WRONG WAY ROUND once and it inverted the whole result; the meaning is recorded
here so it cannot happen again.

THE MEASURE. Joe 1016: *"can you see that T23's 10 diff is noticably higher the its 7.5 diff, while
the T50's 10 diff is near or slightly lower than its 7.5 diff?"* - so the SECOND DIFFERENCE across
the Mage ladder, in points.
  A RATIO WAS MINE AND IS REJECTED. It divides by the earlier diff, so a near-zero denominator
  blows it up: at the ws5Mage reversals it spanned -6.12 to +10.37 and separated nothing. Joe:
  *"could ratio be the wrong way to measure this?"* - it is.

THE OFFSETS ARE SEAM-ALIGNED, Joe 1016: *"landing on the 5TF seam gives us the most accurate
picture of the lines, and keeps us clear of the 'emerging bar jump at TF seam' issue / this leans
us towards using clean 5 minute bars"*. His own +7.5 min is not a 5-minute multiple, so the pair
became +5 / +10.

MY CLAIM THAT +7.5/+10 "DOES NOT SEPARATE" WAS WRONG AND IS WITHDRAWN. I wrote that T50 reads 24 of
30 under his pair and so fails to separate from T23's 30 of 30. I measured T50 at 01:08:00. The bar
Joe named for the reverse is 01:08:45, where his pair reads 0 of 30, median -4.03. So his own pair
separates 30 of 30 against 0 of 30. The swap rested on the wrong bar of T50.

RE-MEASURED 1016 AT HIS FOUR NAMED BARS, after he asked *"is this a byproduct of me suggesting to
use TF5 seams, instead of raw timestamps?"*
    his bar              his +7.5/+10          the seam +5/+10       his own call
    00:23:00             continuance 30 of 30  continuance 30 of 30  continuance - both agree
    ~00:35               reverse     1 of 30   reverse     0 of 30   continuance - NEITHER agrees
    ~00:55               continuance 30 of 30  reverse     0 of 30   continuance - HIS PAIR ONLY
    ~01:08:45            reverse     0 of 30   reverse     0 of 30   reverse - both agree
  So the seam swap is what destroyed his named 00:55 continuance. It is NOT what moved 00:35 -
  that bar reads reverse under his own offsets too, and remains unexplained.
  W_BP_MIN_LINES is not load-bearing at any of these bars: every reading is 0-1 of 30 or 30 of 30.

THE DAY, both pairs, octo2 over 2026-07-22 00:00:00 to 23:59:55
    his +7.5/+10     +9.2942%, 97 events, 21 closed, 17 positive, the last exit 23:28:35
    the seam +5/+10  +9.7570%, 92 events, 21 closed, 17 positive, the last exit 23:22:05
  At 22:10:35 his pair reads continuance 25 of 30 and the seam reads reverse 1 of 30, so that
  half of my original note holds. The 23:22:05 exit is the bar that matched his named ~23:21;
  his own pair pushes it to 23:28:35.

THE DEFAULT STAYS AT THE SEAM PAIR UNTIL JOE RULES. Both pairs match three of his four named bars
and they are different threes, so there is no measurement that picks one. REPORTED TO HIM.

WHAT STAYS WITH THE 5-MINUTE SEAM AND WHAT DOES NOT. Joe asked whether to drive everything off a
5-minute clock. MEASURED AGAINST IT, and reported to him: a 5-minute trigger flips state 0.33
times per sample against the reversal trigger's 0.20, and on 5 of the 13 seams in his own window
ws5Mage is NOT oob, so a fixed clock would skip the mech's own firing condition. So the OFFSETS are
seam-aligned and the TRIGGER stays the ws5Mage reversal.

SRP: this file emits a verdict. It opens no trade, closes none, and holds no trade state.
CAUSAL WITH A STATED DELAY: a verdict about bar T reads T+10 min, so it is knowable at T+10 and
`verdict()` returns that bar. A caller must not act on it before `known_at`.
"""
import os
import numpy as np

from optimus9.analysis.jig import mage_ladder_diff
from optimus9.analysis.lr_v2 import _mage_rev

# ---- THE KNOBS. the names are mine; the values are Joe's where marked.
LADDER_HI = int(os.environ.get('W_BP_LADDER_HI', 30))   # ws30 down to ws1, the ladder he asked for
LADDER_LO = int(os.environ.get('W_BP_LADDER_LO', 1))
OFF_A = int(os.environ.get('W_BP_OFF_A', 60))           # +5 min. seam-aligned, Joe 1016
OFF_B = int(os.environ.get('W_BP_OFF_B', 120))          # +10 min. Joe's own second offset
# W_BP_MIN_LINES - how many of the ladder must be positive for `continuance`. MINE AND STATED:
# it is the only number in the mech Joe did not give. The data does not force it - every reading
# measured is 0 to 2 or 25 to 30, so anything from 3 to 24 gives the same verdicts on this
# evidence. 15 of 30 is the majority, which is the one defensible choice with no knee to anchor to.
MIN_LINES = int(os.environ.get('W_BP_MIN_LINES', 15))
# W_BP_SEAM - FORCED SEAM. 0 reads at the raw bar j+off, which is the banked behaviour. 1 snaps
# each read bar DOWN to the clean 5-minute bar, so both reads land on a 5TF seam. Joe 1016:
# *"landing on the 5TF seam gives us the most accurate picture of the lines, and keeps us clear of
# the 'emerging bar jump at TF seam' issue"*.
#   SNAP DOWN, NOT NEAREST. STRUCTURAL AND STATED: snapping up would read a bar later than
#   j + OFF_B, which is the bar `known_at` promises the verdict is readable at, so it would break
#   the mech's causality. Snapping down keeps every read at or before `known_at`.
#   THE COST OF SNAP-DOWN: when j+OFF_A and j+OFF_B fall in the same 5-minute block both reads
#   collapse to the same bar and the second difference is identically 0, which reads `reverse`.
#   The sweep counts these.
SEAM = os.environ.get('W_BP_SEAM', '0') == '1'
SEAM_BARS = int(os.environ.get('W_BP_SEAM_BARS', 60))     # 5 min at the 5 s grid
TRIG_TF = int(os.environ.get('W_BP_TRIG_TF', 5))        # ws5Mage, Joe's trigger line
ON = os.environ.get('W_BP_ON', '1') == '1'

CONTINUANCE = 'continuance'
REVERSE = 'reverse'


def read_bars(j):
    """The two bars a verdict about bar `j` reads. -> (the +OFF_A bar, the +OFF_B bar).

    Raw: j+OFF_A and j+OFF_B. Forced seam: each snapped DOWN to the 5-minute grid.
    """
    a, b = int(j) + OFF_A, int(j) + OFF_B
    if SEAM:
        a = (a // SEAM_BARS) * SEAM_BARS
        b = (b // SEAM_BARS) * SEAM_BARS
    assert a <= int(j) + OFF_B and b <= int(j) + OFF_B, \
        'a read bar may never exceed known_at = j + OFF_B'
    return a, b


class BouncePred:
    """`bounce-pred` over one tape. Build once, then `verdict` and `walk`."""

    def __init__(self, sc, rev_wob=None):
        n = len(sc.ts)
        self.n = n
        self.hi, self.lo = float(sc.HI), float(sc.LO)
        self.tfs = list(range(LADDER_HI, LADDER_LO - 1, -1))
        self.mg = {t: np.asarray(sc.LD(t * 60, 'Mage'), float)[:n] for t in self.tfs}
        self.trig = self.mg[TRIG_TF] if TRIG_TF in self.mg else \
            np.asarray(sc.LD(TRIG_TF * 60, 'Mage'), float)[:n]
        self.rev_wob = int(sc.LG['rev_wob'] if rev_wob is None else rev_wob)
        self.rev = _mage_rev(self.trig, self.rev_wob)
        self.ladder_n = len(self.tfs)

    def trig_oob(self, j, side=None):
        """Is the trigger line oob at bar `j`? `side` +1 high only, -1 low only, None either."""
        v = float(self.trig[j])
        if side is None:
            return v >= self.hi or v <= self.lo
        return (v >= self.hi) if side > 0 else (v <= self.lo)

    def verdict(self, j, side=None):
        """-> (verdict, known_at, median second diff, lines positive, why) or None.

        None when the trigger line is not oob at `j` - Joe 1016: *"it will only fire when ws5Mage
        is oob"*. `known_at` is j + OFF_B, the bar the verdict becomes readable.
        """
        if not ON:
            return None
        j = int(j)
        if j + OFF_B >= self.n:
            return None
        if not self.trig_oob(j, side):
            return None
        # THE PRODUCER IS IN THE JIG, Joe 1016: *"any producers need to be in the jig"*.
        a, b = read_bars(j)
        med, pos, _d = mage_ladder_diff(self.mg, j, a - j, b - j, self.tfs)
        v = CONTINUANCE if pos >= MIN_LINES else REVERSE
        why = ('%d of %d lines positive, median %+.2f over +%d to +%d bars%s'
               % (pos, self.ladder_n, med, OFF_A, OFF_B,
                  '' if not SEAM else
                  (' | seam-snapped to +%d/+%d%s' % (a - j, b - j,
                                                     ', COLLAPSED' if a == b else ''))))
        return v, j + OFF_B, med, pos, why

    def walk(self, frm, side=None, until=None):
        """Every verdict from `frm`, one per trigger-line reversal, until the first REVERSE.

        Joe 1016: *"will fire on each ws5Mage reversing until `continuance` is no longer printed,
        ie `continuance` will flip to `reverse`"*. So the walk STOPS on the first REVERSE and that
        row is the last one - it is the pivot the caller was waiting for.
        -> [(the reversal bar, verdict, known_at, median, lines positive, why)]
        """
        frm = int(frm)
        end = int(self.n - 1 - OFF_B if until is None else min(until, self.n - 1 - OFF_B))
        out = []
        for j in range(frm, end + 1):
            if self.rev[j] == 0:
                continue
            r = self.verdict(j, side)
            if r is None:
                continue
            v, ka, med, pos, why = r
            out.append((j, v, ka, med, pos, why))
            if v == REVERSE:
                break
        return out
