"""s46_momo — item 13 of the s46 flow. Joe 0805.

PURE LOGIC. No DB, no file IO — the builder writes s46_event. Reads the momo indicator from
optimus9.compute.momo_gated, which is build_exhv2.momo() with Joe's three curl gates applied.

JOE'S SPEC, 0805, verbatim structure:

  momo activated   tested PER EACH BAR OF THE WALK. The gate is open at a bar when the indicator
                   returns `momo` OR `curl`, same bias, on s15 OR s22. momo is an INDICATOR here;
                   s46 builds its own gate from it (Joe 0805).

  when activated   the trade stays open until momo_exit. "IF momo_exit == true (not WHEN)".

  momo_exit  1)    s15r AND s22r are both beyond the fence, in the trade's direction.
             2)    (s15r OR s22r) beyond the same fence.

  BOTH ARE LATCHED (Joe 0805: "create a latch to handle this. no cap - there is always another s6x
  cross"). The first build required 2)'s fence test and an s6x cross on the SAME BAR; that
  coincidence is rare, so armed trades ran for hours or days — n=7 held 15h32m against 1m55s, and
  eight trades collapsed onto the single exit bar 07-30 07:20:20. Latching removes the coincidence:
  once a condition is true it STAYS true, and the trade closes at the NEXT gated s6x cross.

  CONSEQUENCE, stated not buried: 2)'s test (EITHER beyond) is weaker than 1)'s (BOTH beyond), so 2)
  always latches at or before 1). The exit bar is therefore always set by 2). 1) is still recorded
  as its own event row when it occurs, so the distinction stays visible in s46_event.

  No cap is applied anywhere — the walk runs to the end of the tape if no cross arrives.

  OPPOSING CURL (Joe 0805) — "a curl that disagrees with the current trade ... the same momo
  mechanic's 'curl' state, but the curl signal opposing our current trade's direction".
    detect   momo_g(r, -dr, w) == 'curl' on s15r AND s22r, SAME BAR. Joe: "the nature of K lines
             says the smaller TF will curl before the higher TF does. when s22r matches s15r curl,
             then market has reversed enough to impact s22r's direction".
             Because gate 2 for +1 requires qa > 0 (a minimum: falls then RISES), an opposing curl
             on a short is an up-curl BEGINNING — the reversal starting, not ending.
    exit     the next s6x cross (Joe 0805, point 3 corrected to s6x), at the swept xwob.
    scope    contained, not a gate — it ignores every other momo signal.
    latch    runs ALONGSIDE a latched r; when it signals, the fence latch is CANCELLED.

  ATTRIBUTION, NOT TIMING: every path — latch1, latch2, opposing curl — exits at the next s6x cross
  after it latches. So cancelling the fence latch changes WHICH mechanism owns the exit, not the
  exit bar, unless the opposing curl latches EARLIER than the fence did. Stated rather than buried.

  THE FENCE        swept as a symmetric pair off LO. Joe 0805: "hi boundary minus {sweep} and lo
                   boundary plus {same sweep} ... boundaries are swept as a pair, ie as 100 - sweep
                   value ... in this case the value is 100 - 15 - {sweep 3}".
                     fence_lo = LO + s          dr -1 needs r <= fence_lo
                     fence_hi = 100 - LO - s    dr +1 needs r >= fence_hi
                   At s = 3 that is 18 / 82, and 82 == 100 - 18, so the pair stays symmetric.

  XWOB             while the trade is momo-held, the swept xwob REPLACES EXIT_WOB 3 (Joe 0805:
                   "replacement to be swept"). Unarmed trades keep EXIT_WOB 3.

  NEVER ACTIVATED  item 15 unchanged — the next bias-side gated s6x cross closes the trade
                   (Joe 0805, confirmed).

CAUSAL. Every test reads the current bar and earlier only. The walk never looks past w.
"""
import numpy as np

from optimus9.compute.momo_gated import momo_g

LO = 15.0                      # the strategy's low level; HI is 100 - LO = 85
FENCE_SWEEP = (2, 3, 4, 5, 6, 7, 8)          # Joe 0805 — fence width in board points
XWOB_SWEEP = (3, 4, 5, 6, 7, 8, 9)           # Joe 0805 — replaces EXIT_WOB 3 while momo-held

# ITEM 10 EXTENSION — s4Mage breach-duration floor. OFF by default (Joe 0805).
#   item 10 today:  sr_ib_bars > 24  AND  sr_s1hold > 24
#   with this ON:   ... AND sr_s4hold >= S4HOLD_MIN
# sr_s4hold = 5 s bars s4Mage has held OOB AT the test bar. Named to parallel sr_s1hold.
#
# WHY. 07-29 09:40:20 opened on a ONE-BAR stretch: s4Mage reached 85.17 (0.17 past the 85 level) and
# fell back next bar. Both existing counts passed easily — sr_ib_bars 475 = 39.6 min, sr_s1hold 109
# = 9.1 min — because they measure the RUN-UP, not the breach. 206 of the 854 gated trades (24.1%)
# open on a one-bar breach, and the gate barely selects: 22.0% of ALL stretches are one bar.
# Joe 0805: "s4M cannot be considered trade worthy if it only dwells for 5 seconds."
#
# TURNING IT ON MODIFIES ITEM 11. At the entry bar s4Mage has been OOB for exactly 1 bar, because
# item 11 opens on the stretch's FIRST bar. Any floor > 1 is met only by DELAYING entry to bar
# S4HOLD_MIN of the stretch. That is causal — it waits, it does not peek — but it contradicts item
# 11's "no waiting, no confirmation".
#
# DO NOT SUBSTITUTE sr_dwell_bars. That is int(b - a + 1), the run's TOTAL length measured forward
# to its end: lookahead. sr_s4hold counts only bars at or before the test bar.
S4HOLD_MIN = 0                               # 0 = OFF. Sweep: 0, 6, 12, 24

ACT, EXIT, CROSS, OPP = 'momo_act', 'momo_exit', 's6x_cross', 'opp_curl'


def s4hold_entry(a, oob, n=None):
    """Entry bar under the sr_s4hold floor. Returns None if the stretch never reaches it.

    a    the stretch's first OOB bar — item 11's entry bar
    oob  bool per bar, True while s4Mage is out of bounds on this stretch's side
    n    the floor; defaults to S4HOLD_MIN. n <= 1 returns `a` unchanged (the knob is OFF).

    Causal: reads bars a .. a+n-1 and returns a+n-1, which is a DELAY, not a peek."""
    n = S4HOLD_MIN if n is None else n
    if n <= 1:
        return a
    b = a + n - 1
    if b >= len(oob) or not oob[a:b + 1].all():
        return None
    return b


def fence(s):
    """(fence_lo, fence_hi) for sweep width s. Symmetric pair off LO."""
    return LO + s, 100.0 - LO - s


def beyond(v, dr, f_lo, f_hi):
    """is r beyond the fence IN THE TRADE'S DIRECTION (Joe 0805)."""
    if not np.isfinite(v):
        return False
    return (v <= f_lo) if dr < 0 else (v >= f_hi)


def gate_open(r15, r22, dr, w):
    """momo activated at bar w: indicator returns momo or curl, same bias, on s15 OR s22."""
    for r in (r15, r22):
        if momo_g(r, dr, w)[0] in ('momo', 'curl'):
            return True
    return False


def walk(r15, r22, dr, a, b_max, sx_held, sx_plain, s, gate=None, opp=None):
    """Resolve item 13 over bars (a, b_max]. Returns the event list, in time order.

    a         the entry bar index
    b_max     last bar available; the walk stops there if nothing fires
    sx_held   bool per bar — gated s6x cross at the SWEPT xwob, used once momo has armed
    sx_plain  bool per bar — gated s6x cross at EXIT_WOB 3, used while unarmed
    s         fence sweep width

    Each event is (kind, bar, branch). branch is '1' or '2' on momo_exit, else None.
    """
    f_lo, f_hi = fence(s)
    armed = False
    latch1 = False                 # Joe's 1) — BOTH r beyond the fence. Latched.
    latch2 = False                 # Joe's 2) — EITHER r beyond the fence. Latched.
    opp_latched = False            # opposing curl on BOTH lines. Latched. Cancels the fence latch.
    out = []
    for w in range(a + 1, b_max + 1):
        if not armed and (gate[w] if gate is not None else gate_open(r15, r22, dr, w)):
            armed = True
            out.append((ACT, w, None))
        if not armed:
            # never activated -> item 15 unchanged, plain xwob
            if sx_plain[w]:
                out.append((CROSS, w, None))
                return out
            continue
        b15 = beyond(r15[w], dr, f_lo, f_hi)
        b22 = beyond(r22[w], dr, f_lo, f_hi)
        if not latch2 and (b15 or b22):
            latch2 = True
            out.append((EXIT, w, '2'))
        if not latch1 and (b15 and b22):
            latch1 = True
            out.append((EXIT, w, '1'))
        if not opp_latched and opp is not None and opp[w]:
            opp_latched = True
            latch1 = latch2 = False          # Joe 0805: "the latch is cancelled"
            out.append((OPP, w, None))
        if (latch1 or latch2 or opp_latched) and sx_held[w]:
            out.append((CROSS, w, None))
            return out
    return out
