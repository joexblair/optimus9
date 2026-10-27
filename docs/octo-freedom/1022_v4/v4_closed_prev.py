"""THE CAUSAL CLOSED READ. Joe 1026: *"from memory, I think the best fix was to take the last 5s
bar's close value (eg the xx:xx:55 timestamp). does that help? we absolutely need to be aligned
with the live tape"*.

IT IS THE JIG'S OWN RULE, not a new one. `jig.Jig.closed_prev`:

    Causal 'last CLOSED coarse value': the EMERGING value of `name` at the last 5s bar of the most
    recently COMPLETED bucket - the bar immediately BEFORE the most recent seam (seam-5s). Held
    forward through the next bucket. This is the value TradingView shows as the coarse bar's CLOSE
    (emerging_bar_open.md: emerging@(seam-5s) == TV closed), read causally.

    THREE reads of 'the coarse value', do not confuse them:
      - seam_prev(name, seam_ms)  -> emerging AT the seam = the new bucket's single-candle OPEN
      - value_mode='closed' line  -> the CURRENT forming bucket's eventual close = LOOK-AHEAD
                                      (the o9-live failure, project_v2_lookahead). Never gate on it.
      - closed_prev(name, seam_ms)-> the PREVIOUS completed bucket's close, causal. Use THIS for a
                                      'last closed coarse bar' gate.

WHY lineage2 NEEDS IT. Every lineage2 STATE read was on a `value_mode='closed'` .npy, which is the
middle row of that list: register `docs/causal_lookahead_register.md` A4, *"up to one full TF of
future"*, seam `ALIGN_CLOSE_STAMP` built and OFF. Measured on the 08-30..09-03 window, a closed
line's value inside a bucket equalled THAT bucket's own close on 6773 of 6773 cws1r buckets and
561 of 561 cws12r buckets.

THIS MODULE IS THE ONLY PLACE THE RULE LIVES, so no driver can hold a different version of it.
`series` is a pure function of the emerging array and the timeframe.
"""
import io
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e

TS = np.asarray(ln.ts, np.int64)
_C = {}


def series(emerging, tf_seconds, ts=None):
    """The causal last-closed value of `emerging` at its own timeframe. -> an array, len N.

    `ts` is the 5 s timestamp grid in ms. It defaults to the cached tape's own `ln.ts`, which ends
    2026-10-04, so a LIVE harness passes its own grid - claude-639244ab asked for this on 1026 and
    it changes no existing caller.

    At every 5 s bar the value is the emerging value at the LAST 5 s bar of the most recently
    COMPLETED tf bucket - the `xx:xx:55` bar of the previous minute for a 60 s line. NaN before the
    first bucket has completed.

    The bucket grid is midnight-anchored, which is `IndicatorComputer._bar_open(anchor='midnight')`
    - the grid `line_reader` built these lines on, so the buckets are the producer's own.
    """
    v = np.asarray(emerging, float)
    T = TS if ts is None else np.asarray(ts, np.int64)
    assert len(T) == len(v), 'the timestamp grid and the line are different lengths'
    tf_ms = int(tf_seconds) * 1000
    #   THE MIDNIGHT GRID, for every TF. `line_reader` - the producer that built these lines -
    #   *"reader anchors on `midnight` for every TF: correct on TV for all, identical to epoch
    #   where they coincide"*. On the epoch grid cws7r and cws11r disagreed with the producer on
    #   49800 and 64224 of 86400 bars; 7 and 11 minutes are the only two TFs in 1..12 that do not
    #   divide the day, which is exactly the case the anchor exists for.
    day = (T // 86_400_000) * 86_400_000
    bo = day + ((T - day) // tf_ms) * tf_ms         # this bar's bucket-open, midnight grid
    #   the index of the last 5 s bar of the PREVIOUS bucket: the bar before this bucket's open.
    first = np.searchsorted(T, bo, side='left') - 1
    out = np.full(len(T), np.nan)
    ok = first >= 0
    out[ok] = v[first[ok]]
    #   CAUSALITY, ASSERTED, not claimed in prose: the bar read is strictly before the bar it is
    #   read on, and it is the last bar of a bucket that has already closed.
    idx = np.arange(len(T))
    assert np.all(first[ok] < idx[ok]), 'a closed-prev read is at or after the bar it serves'
    assert np.all(T[first[ok]] < bo[ok]), 'a closed-prev read is inside the forming bucket'
    return out


def line(name, tf_seconds):
    """`series` over the EMERGING line `name`, cached. -> an array."""
    key = (str(name), int(tf_seconds))
    if key not in _C:
        _C[key] = series(ln.line(name), tf_seconds)
    return _C[key]


def ladder(E, tf_minutes=True):
    """The causal closed ladder from an emerging ladder keyed by TF. -> {tf: array}.

    `E` is keyed by the lineage2 TF number, where TF t is t minutes - the same mapping
    `v4_core_arm._line` uses when it builds the override spec from `tf * 60`.
    """
    return {int(t): series(v, int(t) * 60 if tf_minutes else int(t))
            for t, v in E.items()}


def arm_lines(E):
    """The c-set the lineage2 walk reads, every line causally closed. -> {'b', 'r', 'M'}.

    The same shape `v4_core_arm.lines()` returns, so the walk's signature does not move. What
    changes is the source: each line is the last CLOSED value of its EMERGING counterpart, not a
    `value_mode='closed'` .npy.

    `E` is the emerging r ladder from `v4_rcfg_sweep.load`, keyed by TF in minutes.
    """
    return {'b': line('ws1b', 60),
            'r': ladder(E),
            'M': {t: line('ws%dMage' % t, int(t) * 60) for t in (1, 2)}}
