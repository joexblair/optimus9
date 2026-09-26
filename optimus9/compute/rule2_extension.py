"""rule2_extension — ride a lower r line on from the signal bar. Joe 0925.

ONE JOB: at the bar a trade signal would fire, ask whether a lower r line is itself still
travelling towards dr, and if it is, walk THAT line to its own reversal and take the later of the
reversal and its ws{tf}Mage-rev. It owns no threshold, reads no DB, and decides no trade. Every
single-line mechanic is `rule2_trajectory`'s; this module composes, it never duplicates.

JOE'S VERBATIM, 0925, in the order he said it:
  "can you see that ws1 has come full cycle and is now printing trajectory at 17:08?"
  "because ws1 has trajectory when ws3 signals, walk ws1 from the beginning of the next 1min bar
   (17:09) and print the reversal. there won't be a split with ws2r because ws2r is travelling
   away from dr, ie anti-trajectory"
  "I feel like your forcing the extension on every row, instead of _utilising_ it when (ws3r
   reverses AND ws1r is printing trajectory) -`trajectory` can only print when a line is heading
   towards dr"
  "SIGNAL bar is the only time when you can test for ws1r trajectory"
  "the end result of 17:14 is good. bank it"

THE TRIGGER IS A SINGLE BAR. `trajectory` is read at `sig_bar` and nowhere else. Joe ruled that
directly after seeing the mech fire on every row: the extension is UTILISED when the trigger holds,
not applied as a stage.

THE dr FRAME. Joe 0925 on a mismatch he spotted in an earlier run: *"we're working in a +dr state,
so ws1's trajectory is measured from -dr side. ie, the same logic that we're already using"*. So
the extension line reads the SAME `dr` as the signal it extends. There is no second frame.

THE REVERSE IS BOUNDED. `reverse`'s `stop` is the extension line's own trajectory extrema at the
walk start, so the backward block walk cannot reach the previous cycle's extreme. That bound is
mine, taken from Joe's dr-mismatch call; §22.9 and §22.14 stage 2 carry it.

VERIFIED AGAINST JOE'S OWN WALK, #14, 09-05, dr +1, trigger 17:08:00:
    ws1r trajectory at the trigger   2.6 min  +32.82   -> fires
    walk start                       17:09:00
    trajectory extrema               17:05:25  9.90    -> the `stop` bound
    ws1r reverse                     17:14:05
    ws1Mage-rev from the walk start  17:12:55
    SIGNAL                           17:14:05          <- Joe's banked 17:14

`sig_lookback` CHANGES NOTHING ON THAT ROW. Measured: the walk returns 17:12:55 at both 0 and 24
bars, so the signal is 17:14:05 either way. The parameter is exposed and DEFAULTS TO 0, which is
what the banked result was taken under. Whether the extension's mage-rev walk should carry the
2 minute allowance of §22.17 is UNRULED.

THREE THINGS ARE OPEN AND NOT IN THIS MODULE
  every r line as the extension line   Joe 0925: "all 3 r lines are approved for extension
                                       handoffs". Granted, never measured. This module takes one
                                       line, so a caller may pass any of them, but nothing here
                                       picks between them.
  more than one handoff                Joe 0925: "this needs >1 iteration of handoffs between the
                                       ws1,2,3 lines". Granted, never measured. `extend` fires once.
  the `sig_lookback` question above

CAUSAL. The trigger reads bars at or before `sig_bar`. The forward walk starts at the next whole
minute AFTER the trigger and every bar it reads it reads as that bar arrives. `end` is the caller's
dr flip — the backstop, not a cap.
"""
import numpy as np

from .rule2_trajectory import trajectory, reverse


def next_minute(ts, k):
    """The first bar at or after the whole minute FOLLOWING `ts[k]`. -> bar or None.

    Joe 0925: "walk ws1 from the beginning of the next 1min bar (17:09)". `ts` is the tape's ms
    timestamp array. A trigger already on a minute boundary still moves to the next one, which is
    what "the next 1min bar" says and what the 17:08 -> 17:09 walk did.
    """
    ts = np.asarray(ts)
    k = int(k)
    nxt = (int(ts[k]) // 60000 + 1) * 60000
    i = int(np.searchsorted(ts, nxt))
    return i if i < len(ts) else None


def extend(line, dr, sig_bar, ts, block, min_bars, mage_rev, end,
           sig_lookback=0, min_travel=0.0):
    """The extension at `sig_bar`. -> a dict, never None.

    line          the extension line's r — ws1r on every measurement taken
    dr            +1 or -1, the SAME frame as the signal being extended
    sig_bar       the bar the trade signal would fire on. The only bar the trigger is read at
    ts           the tape's ms timestamps, for the next-whole-minute walk start
    block         `anchor_floater.block`, 60 bars = 300 s at the 5 s grid
    min_bars      `trajectory`/`reverse` threshold, 24 bars = 2 min
    mage_rev      a callable (dr, from_bar, sig_lookback) -> bar or None. The ws{tf}Mage-rev walk
                  for THIS line's Mage. Passed in so this module stays clear of the jig
    end           the dr flip bar. The forward walk reads no bar past it
    sig_lookback  handed to `mage_rev`. 0 is what the banked result was taken under

    keys: fires, trigger, walk_start, stop_bar, reverse_bar, mage_rev_raw, mage_rev_bar, signal
      fires         False when the trigger does not hold, or the walk start is past `end`
      trigger       the `trajectory` dict at `sig_bar`, present whether it fires or not
      mage_rev_raw  what `mage_rev` returned, unbounded, so a print past `end` stays visible
      mage_rev_bar  mage_rev_raw, or None when it lands past `end`
      signal        the LATER of reverse_bar and mage_rev_bar, or None when either is missing

    BOTH LEGS ARE BOUND BY `end`. Measured 09-05 #11, dr -1, trigger 04:15:25: the ws1Mage-rev
    walk returns 05:50:45 and the dr flip is 04:53:50, so the signal is None, not 05:50:45.
    """
    line = np.asarray(line, float)
    dr = int(dr); sig_bar = int(sig_bar); end = int(end)
    block = int(block); min_bars = int(min_bars)

    trig = trajectory(line, dr, sig_bar, block, min_bars, min_travel)
    out = {'fires': False, 'trigger': trig, 'walk_start': None, 'stop_bar': None,
           'reverse_bar': None, 'mage_rev_raw': None, 'mage_rev_bar': None, 'signal': None}
    if not trig['has']:
        return out

    w0 = next_minute(ts, sig_bar)
    if w0 is None or w0 > end:
        return out
    out['fires'] = True
    out['walk_start'] = w0
    out['stop_bar'] = trajectory(line, dr, w0, block, min_bars, min_travel)['bar']

    rv = next((i for i in range(w0, end + 1)
               if reverse(line, dr, i, block, min_bars, min_travel,
                          stop=out['stop_bar'])['has']), None)
    out['reverse_bar'] = rv
    mr = mage_rev(dr, w0, int(sig_lookback))
    out['mage_rev_raw'] = mr
    if mr is not None and mr > end:
        mr = None
    out['mage_rev_bar'] = mr
    if rv is not None and mr is not None:
        out['signal'] = max(rv, mr)
    return out
