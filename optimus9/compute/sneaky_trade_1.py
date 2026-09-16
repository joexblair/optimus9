"""sneaky_trade_1 — Joe 0916 named it. The signal producer.

ONE JOB: given a test-point and the lines, say whether sneaky-trade-1 opens, where it opens, where
it closes, and which way. It owns no threshold — every gate arrives as an argument — and it does
not walk the tape, produce test-points, size a position, or place an order.

THE DIRECTION IS HIS, AND IT DOES NOT FOLLOW THE dr-BIAS RULE
    "when you reach a test-point (the moment when the sneaky trade signals), you will enter a long
     position if dr is +1, and short if dr is -1. this is all you need to consider - don't be
     swayed by the other potential activities that might be reliant on dr"
  dr +1 -> LONG, dr -1 -> SHORT. Scored `* dr`. Spec 17.2's dr-bias rule (dr +1 = SHORT) governs
  OTHER mechanics. Applying it here inverts every row — I did that twice and Joe caught it twice.

THE OPEN IS HIS
    "start calculating from the moment after 'test-point' when ws1x has crossed from
     opposing-dr-side oob, to ib"
  The first bar after the test-point where ws1x, having been out of bounds on the OPPOSING dr side,
  returns in bounds. Bounded by the dr flip. It depends on NOTHING downstream — an earlier build
  searched it up to the close, which let the close leak backwards into the open.

THE CLOSE IS CAUSAL, AND WAS NOT
  The FIRST gcws30mage-rev at or after the carrying line's r-momo-fence exit. The open must land
  BEFORE it, otherwise there is no trade.
  It used to be the leash's MAXIMUM COIL — argmax over every rev in the window. That is the global
  maximum of an oscillating series (60.1% of windows carry 2+ local peaks), knowable only once the
  window has ended. A causal peak detector agrees with it on 0.7% of rows. Joe 0915 asked for three
  picks — "test all 3: filter, time, size" — and SIZE is the one that cannot be built.

THE GATE IS THE ENTRY CONDITION, NOT A FILTER
  Ungated the mechanic loses: the drag is a flat cost per trade and the median move does not clear
  it. Chosen on the first of three time blocks and held out on the other two.

CAUSAL. Every test reads bars at or before the bar it fires on.
"""
import numpy as np


def open_bar(x_line, dr, tp, limit, oob_lo, oob_hi):
    """The ws1x crossing. -> bar, or None.

    The first bar in (tp, limit) where `x_line`, having been out of bounds on the OPPOSING dr side,
    is back in bounds. `limit` is the dr flip that ends the frame — the only bound. Joe 0916.
    """
    was = False
    for i in range(int(tp) + 1, int(limit)):
        v = x_line[i]
        if not np.isfinite(v):
            continue
        if (v <= float(oob_lo)) if dr > 0 else (v >= float(oob_hi)):
            was = True
            continue
        if was:
            return i
    return None


def fence_exit(r_line, dr, k, fence, limit):
    """The carrying line's r-momo-fence exit at or after `k`, before `limit`. -> bar, or None."""
    f_lo, f_hi = float(fence[0]), float(fence[1])
    for i in range(int(k), int(limit)):
        v = r_line[i]
        if not np.isfinite(v):
            continue
        if (v >= f_hi) if dr > 0 else (v <= f_lo):
            return i
    return None


def close_bar(rev_bars, fx, limit):
    """The FIRST gcws30mage-rev at or after the fence exit, before `limit`. -> bar, or None.

    `rev_bars` is the rev producer's own causal signal (jig.causal.ws1mage_rev sig_conf). Taking
    the first is what makes this reproducible bar by bar; any selection AMONG the revs in the
    window needs the window's end and is not causal.
    """
    c = [int(b) for b in rev_bars if int(fx) <= int(b) < int(limit)]
    return c[0] if c else None


def gate(climb, drop, src, hi, drop_min, src_set, hi_set, need_climb=False):
    """The entry condition. -> (bool, reason).

    climb     the ladder climbed: the carrying line is higher than the sourcing one
    drop      the dr-signed Mage cascade drop at the test-point, ws1Mage minus ws12Mage
    src, hi   the sourcing and carrying timeframes
    Each argument is a value Joe set; this function holds none of them.
    """
    if need_climb and not climb:
        return False, 'no climb'
    if drop is None or drop < float(drop_min):
        return False, 'drop %s' % ('none' if drop is None else '%.1f' % drop)
    if src not in src_set:
        return False, 'src ws%d' % src
    if hi not in hi_set:
        return False, 'hi ws%d' % hi
    return True, ''


def signal(tp, dr, src, hi, mx, drop, x_line, r_hi_line, rev_bars, flip,
           fence, oob_lo, oob_hi, drop_min, src_set, hi_set, need_climb=False):
    """The whole mechanic for one test-point. -> dict, or None when nothing opens.

    tp        the test-point bar
    dr        the dr stretch's direction. +1 -> LONG, -1 -> SHORT
    src, hi   sourcing and carrying timeframes; `mx` is the carrying line's own test-point bar
    flip      the dr latch change that ends the frame — the bound on every forward search
    -> {'tp','dr','side','src','hi','fx','ob','eb','drop','taken','why'}
       `taken` is the gate verdict; a row with taken False still reports its bars so a caller can
       reconcile a live fill that should not have happened.
    """
    fx = fence_exit(r_hi_line, dr, mx, fence, flip)
    if fx is None:
        return None
    eb = close_bar(rev_bars, fx, flip)
    if eb is None:
        return None
    ob = open_bar(x_line, dr, tp, eb, oob_lo, oob_hi)
    if ob is None:
        return None
    ok, why = gate(hi > src, drop, src, hi, drop_min, src_set, hi_set, need_climb)
    return {'tp': int(tp), 'dr': int(dr), 'side': 'LONG' if dr > 0 else 'SHORT',
            'src': int(src), 'hi': int(hi), 'fx': int(fx), 'ob': int(ob), 'eb': int(eb),
            'drop': None if drop is None else float(drop), 'taken': bool(ok), 'why': why}
