"""rule2_trajectory — is a line still travelling towards dr. Joe 0924. THE FIRST rule#2 mechanism.

ONE JOB: given one line and a bar, find that line's dr-OPPOSED extrema and say how long it has
been travelling away from it. It owns no threshold, reads no DB, and decides no trade.

RULE#2, JOE VERBATIM 0924:
  "the general premise of #2 is this: if a signal prints when ws[1,2,3]r has not completed its
   cycle, we walk them to completion if they are showing trajectory towards dr
   -"trajectory" is detected when any of the 3 lines are travelling towards dr, for more than 2
    minutes. this can be measured by looking back across the line to find its dr-opposed extrema"

THE LOOK-BACK, JOE 0924: "use the same mech the divergence uses to discover an extrema - look back
in 5 minute windows". That is `anchor_floater` step 3's block walk, and this module mirrors it:

    block n covers [k - n*block, k - (n-1)*block), so the test bar itself is excluded, exactly as
    step 3 excludes the pivot bar. Each block yields its extreme. An EMPTY block is SKIPPED, not a
    stop — Joe 0921. The walk ends at the first block that does not improve the running best.

TWO THINGS DIFFER FROM STEP 3, AND BOTH ARE JOE'S
  the extreme    step 3 hunts the dr-SIDE extreme for a floater; this hunts the dr-OPPOSED one.
                 dr +1 -> the block minimum, dr -1 -> the block maximum
  no 50 filter   step 3 masks to bars on the dr side of 50. Joe 0924, asked directly: "yes: there
                 is no 50 filter"

WHY THE BAR-TO-BAR READING WAS WRONG. Measured at 09-03 02:52:20 before Joe ruled: all three of
ws1r, ws2r, ws3r tick DOWN on that bar by 8.18, 8.63 and 9.91 r-points, so an unbroken-climb test
returns 0 bars on every line. Travel measured extrema-to-bar does not care — Joe 0924: "gap2 might
not be a gap if you have the correct extrema". It was not.

MEASURED, 09-03 02:52:20, dr +1, block 60 bars, threshold 2 minutes — Joe's own read matches:
    ws1r  extrema 02:42:35  11.02  117 bars =  9.8 min  travel +68.70  TRAJECTORY
    ws2r  extrema 02:46:30  25.21   70 bars =  5.8 min  travel +19.63  TRAJECTORY
    ws3r  extrema 02:51:20  54.72   12 bars =  1.0 min  travel  +1.69  no

CAUSAL. Every bar read is strictly before `k`. Nothing looks forward.

`min_travel` GATES THE MAGNITUDE, AND IT IS UNSET. Every mechanic built on this module fires on
a travel of any size, including floating-point dust: measured 09-02 23:54:15, ws1r sat at the
100.00 StochRSI ceiling and `travel` read -7.105427357601002e-14, which passed. Joe 0924, asked
to set a threshold: *"I would say the true threshold is in the OOS data"*. So the parameter exists
and DEFAULTS TO 0.0, which is exactly the behaviour every number measured on 0924 was taken under.
Real travels measured on the same day, for scale: -19.87, -14.29, -8.79, -3.81.

NOT IN `wsf_dtf_v3_config`: the 2 minute threshold is Joe's value, said in chat. `block` is
banked — `anchor_floater.block` 60 bars, config v9. See the wsf-dtf-v3 spec for why a new config
version has not been written.
"""
import numpy as np


def opposed_extrema(r, dr, k, block, stop=None):
    """The dr-OPPOSED extrema behind bar `k`, by the divergence's 5 minute block walk.

    `stop` is the EARLIEST bar the walk may read. None lets it run back to the tape start, which
    is what `trajectory` wants. `reverse` needs it — see that function.

    -> (bar, value, blocks) or (None, nan, blocks) when no block holds a finite value.
    `blocks` is [(from, to, block best, its bar, new_best)] in walk order, for the trace.
    """
    r = np.asarray(r, float)
    k = int(k); dr = int(dr); block = max(1, int(block))
    floor = 0 if stop is None else max(0, int(stop))
    best, bi, blocks, n = np.nan, None, [], 0
    while True:
        n += 1
        hi = k - (n - 1) * block
        lo = max(floor, k - n * block)
        if hi <= floor or lo >= hi:
            break
        cand = r[lo:hi]
        if np.all(np.isnan(cand)):
            blocks.append((lo, hi, float('nan'), None, 0))
            continue                                    # Joe 0921: skip, do not stop
        m = lo + int(np.nanargmin(cand) if dr > 0 else np.nanargmax(cand))
        new = (bi is None) or ((r[m] < best) if dr > 0 else (r[m] > best))
        if new:
            best, bi = float(r[m]), m
        blocks.append((lo, hi, float(r[m]), int(m), int(new)))
        if not new:
            break
    return bi, best, blocks


def trajectory(r, dr, k, block, min_bars, min_travel=0.0, stop=None):
    """Is this line travelling towards dr at bar `k`. -> a dict, never None.

    r           one r line on the 5 s grid
    dr          +1 or -1
    block       the look-back window in bars. `anchor_floater.block` 60 bars = 300 s = 5 min
    min_bars    how long the travel must have run. Joe 0924: "more than 2 minutes" — STRICTLY
                more, so 24 bars at the 5 s grid is not enough
    min_travel  the smallest |travel| that counts, in r-points. UNSET — see the module docstring.
                0.0 accepts any travel with the right sign, dust included
    stop        the earliest bar the block walk may read. None runs back to the tape start

    keys: has, bar, value, bars, travel, blocks
    """
    r = np.asarray(r, float)
    bi, best, blocks = opposed_extrema(r, dr, k, block, stop)
    if bi is None:
        return {'has': False, 'bar': None, 'value': float('nan'), 'bars': 0,
                'travel': float('nan'), 'blocks': blocks}
    travel = float(r[int(k)]) - best
    bars = int(k) - bi
    towards = (travel > 0) if int(dr) > 0 else (travel < 0)
    big = abs(travel) >= float(min_travel)
    return {'has': bool(bars > int(min_bars) and towards and big), 'bar': bi, 'value': best,
            'bars': bars, 'travel': travel, 'blocks': blocks}


def reverse(r, dr, k, block, min_bars, min_travel=0.0, stop=None):
    """Has this line REVERSED at bar `k` — travelling AWAY from dr. -> the same dict.

    Joe 0924 defined it by pointing at this module: *"'reverse' = your 'A single-line reversal is
    trajectory() with the dr inverted'"*. So it is `trajectory` with `-dr`, and nothing else:
    the block walk then hunts the dr-SIDE extreme, which is the line's own peak, and `travel`
    measures the move off it.

    `value` is that peak and `bar` is where it sits. Measured 0924, dr +1:
        09-03 02:54:35  ws1r  peak 02:52:10 87.90  2.4 min  travel -19.87
        09-03 00:00:15  ws2r  peak 23:56:00 100.00 4.2 min  travel -14.29
        09-03 00:05:05  ws3r  peak 00:03:00 99.99  2.1 min  travel  -3.81

    `stop` — PASS THE LINE'S OWN TRAJECTORY EXTREMA BAR. Joe 0925 diagnosed the reason from a
    single timestamp: *"this indicates a dr mismatch in the calculations. we're working in a +dr
    state, so ws1's trajectory is measured from -dr side. ie, the same logic that we're already
    using"*. Unbounded, the walk runs back past the low the trajectory is measured from and
    returns the PREVIOUS cycle's peak.

    MEASURED 09-05 17:09:00, ws1r, dr +1. Trajectory low 17:05:25 at 9.90.
        stop=None   peak 16:56:05 at 96.88 — 112 bars = 9.3 min BEFORE that low — fires at once
        stop=low    peak 17:09:00 at 47.10, travel +0.00 — does not fire, which is correct
    and walking on with stop=low, the reversal is 09-05 17:14:05 off a 17:12:00 peak of 82.19,
    travel -32.8077. Joe 0925: *"the end result of 17:14 is good. bank it"*.

    Across the 13 walked rows the bound moves four reverse bars — #2 +0.9, #6 +3.7, #11 +1.4,
    #12 +2.8 min — and changes NO signal. It defaults to None so every caller that has not been
    told about it keeps the behaviour it was measured under.
    """
    return trajectory(r, -int(dr), k, block, min_bars, min_travel, stop)
