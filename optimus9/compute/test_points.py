"""test_points — the wsf test-point producer. Joe 0915/0916.

ONE JOB: given a dr stretch and a timeframe, say where that timeframe's test-point is, or that
there isn't one. It owns no threshold — every gate arrives as an argument — and it does not walk
the tape, score anything, or decide a trade.

THE dr STRETCH IS THE FRAME. Joe 0916: *"the dr latch only sets the cycle's dr"* and *"dr is
global: ALL chains should be sharing the dr"*. So a stretch runs from one latch change to the
next, the dr is held across it, and ws1..ws4 each hunt inside it independently.

AT MOST ONE TEST-POINT PER STRETCH PER TIMEFRAME. Joe 0916: *"one test-point per dr cycle, so
long as the code treats this per tf - ie there will be multiple tf's setting test-points inside
of a dr cycle"*.

THE THREE STEPS
  1  THE ANCHOR — the established wsNMage oob. Joe 0916 named it: *"mk == established ws1Mage
     oob"*. The first bar in the stretch where wsNMage's CONSECUTIVE run on the dr side of the
     25/75 fence reaches `mage_dwell` bars. Any bar not out of bounds resets the run.
     Joe 0915 chose this over the bare oob cross: *"dwell"*.
  2  LOOK BACK — from the anchor, back up to `lookback` bars, for a flat run that has ALREADY
     completed. Found means the test-point IS the anchor bar.
       - it hunts a FLAT RUN, not a bare oob run. Joe 0916: *"agreed"*.
       - it requires NOTHING of r at the anchor. Joe 0916: *"at mk, nothing. lookback either
         finds a flat run, or it doesn't"*.
       - it may not read earlier than the stretch's own start. Joe 0916: *"if dr flips while the
         lookback is looking back, then we abandon and continue with the established mech"*.
  3  LOOK FORWARD — the established wsf-dtf-v3 step, unchanged: the first flat run at or after
     the anchor. Joe 0916: *"the established wsf-dtf-v3 mech already looks for the first wsNr
     after `mk`"*. Bounded by the end of the stretch, which is Joe's 0916 ruling and was NOT in
     the code before — `walk_mom_models.py:276` called the producer with no end bar.

A FLAT RUN is `samples` consecutive bars, every one beyond `fence` on the dr side, whose max
minus min is <= `tol`. That is `jig.sideways_reversal`'s own definition and this module reads it
the same way rather than re-implementing it.

WHAT IS NOT HERE, AND WHY
  the r out-of-bounds step   Joe 0916 put r on its own fence, which made this step's 15/85 read
                             wrong. With the look-back hunting a flat run it has no job left
  the give-up rule           spec step 3. Its action was to PLANT a dr flip, which cannot survive
                             "dr is global". Joe 0916 ruled the case directly: *"keep going on
                             dr +1 and set the test-point at 16:32:10"*
  the fence-exit test        spec step 8, which Joe dropped on 0913. It selected lines for the
                             sweep, and the sweep is gone. Joe 0916: *"exit_hi and exit_lo are
                             not needed for this current work"*
  the planted flip           the sweep loop's own advancement, never the walk's

CAUSAL. The anchor counts a run backwards from each bar. The look-back reads bars at or before
the anchor. The look-forward stops at the bar it reports. Nothing reads past the bar it fires on.
"""
import numpy as np


def flat_run_at(r, k, dr, fence, samples, tol):
    """Is a flat run COMPLETE at bar k. -> its span in r-points, or None.

    `samples` consecutive bars ending at k, every one beyond `fence` on the dr side, max-min <=
    `tol`. Matches jig.sideways_reversal: the fence test is STRICT, and the bar the run reaches
    `samples` is the bar it is knowable on.
    """
    lo = int(k) - int(samples) + 1
    if lo < 0:
        return None
    w = np.asarray(r[lo:int(k) + 1], float)
    if len(w) < samples or not np.all(np.isfinite(w)):
        return None
    f_lo, f_hi = float(fence[0]), float(fence[1])
    ok = (w > f_hi).all() if dr > 0 else (w < f_lo).all()
    if not ok:
        return None
    span = float(w.max() - w.min())
    return span if span <= float(tol) else None


def anchor(mage, dr, k0, k1, mage_fence, mage_dwell):
    """The established wsNMage oob inside [k0, k1). -> the bar, or None.

    The bar its CONSECUTIVE run on the dr side of `mage_fence` reaches `mage_dwell`. The run
    resets to 0 on any bar that is not out of bounds, so this is the dwell bar, not the cross.
    """
    m_lo, m_hi = float(mage_fence[0]), float(mage_fence[1])
    oob = (mage >= m_hi) if dr > 0 else (mage <= m_lo)
    run = 0
    for i in range(int(k0), int(k1)):
        run = run + 1 if oob[i] else 0
        if run >= int(mage_dwell):
            return i
    return None


def test_point(r, mage, dr, k0, k1, fence, mage_fence, mage_dwell, lookback,
               samples=3, tol=2.0):
    """This timeframe's test-point inside the dr stretch [k0, k1). -> dict, or None.

    r, mage     this timeframe's r and Mage lines on the 5 s grid
    dr          the stretch's dr, from the latch. Held for the whole stretch
    k0, k1      the stretch: k0 is the latch change bar, k1 the next one
    fence       r's own fence as (lo, hi). momo_fence_r 17 -> (17.0, 83.0)
    mage_fence  the Mage fence as (lo, hi). 25/75
    mage_dwell  bars the Mage oob run must REACH. MAGE_DWELL 6 = 30 s
    lookback    bars the look-back may reach back from the anchor. tp_lookback_min 4 min = 48 bars
    samples     bars in a flat run. 3
    tol         the flat run's max span in r-points. SR_TOL 2.0

    -> {'bar', 'dr', 'anchor', 'how', 'span', 'back', 'clipped'} or None
       how      'lookback' | 'forward'
       back     bars from the flat run's end to the anchor. 0 on a forward find
       clipped  True when the stretch start cut the look-back short of `lookback`
    """
    a = anchor(mage, dr, k0, k1, mage_fence, mage_dwell)
    if a is None:
        return None
    floor = max(int(k0), a - int(lookback), int(samples) - 1)
    clipped = (a - int(lookback)) < int(k0)
    for j in range(a, floor - 1, -1):
        span = flat_run_at(r, j, dr, fence, samples, tol)
        if span is not None:
            return {'bar': a, 'dr': int(dr), 'anchor': a, 'how': 'lookback',
                    'span': span, 'back': a - j, 'clipped': clipped}
    for j in range(a, int(k1)):
        span = flat_run_at(r, j, dr, fence, samples, tol)
        if span is not None:
            return {'bar': j, 'dr': int(dr), 'anchor': a, 'how': 'forward',
                    'span': span, 'back': 0, 'clipped': clipped}
    return None


def stretches(dr_latch, i0, i1):
    """The dr stretches over [i0, i1). -> [(start, end, dr)] with end exclusive.

    A stretch runs from one latch CHANGE to the next. Joe 0916: the latch sets the dr, not the
    start bar of a walk - so this is the frame every timeframe hunts inside, nothing more.
    """
    d = np.asarray(dr_latch)
    ch = np.flatnonzero(np.r_[False, (d[1:] != d[:-1]) & (d[1:] != 0)])
    ch = ch[(ch >= int(i0)) & (ch < int(i1))]
    return [(int(ch[i]), int(ch[i + 1]) if i + 1 < len(ch) else int(i1), int(d[ch[i]]))
            for i in range(len(ch))]
