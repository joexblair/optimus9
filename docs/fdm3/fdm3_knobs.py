"""fdm3's knobs. BANKED MEANS THE DEFAULT MOVES AND AN OFF-RULED RUN REFUSES - Joe's standing rule.

Every value here is HIS, and every NAME here is his too: he wrote `fdm3-sideways-trigger`,
`fdm3-sideways-retest-scan-window` and `fdm3-sideways-retest-diff-pct` into the spec himself.

fdm3 IS A NEW GENERATION, not an addition to fdm2 - Joe 1114 confirmed the prefix. Its knobs live
here and NOT in v4_knobs, so a v4 run cannot be changed by an fdm3 ruling and vice versa. The
env override is W_FDM3_<NAME>.

An off-ruled run raises at import unless W_FDM3_EXPERIMENT=1.
"""
import os
import sys

EXPERIMENT = os.environ.get('W_FDM3_EXPERIMENT', '0') == '1'


def _knob(name, default, cast=float):
    return cast(os.environ.get('W_FDM3_' + name, str(default)))


#   ── fdm3-sideways ─────────────────────────────────────────────────────────────────────────────
#   HIS SPEC LINE: *"(ws{knob:5,`fdm3-sideways-trigger`}}b is not oob OR ws{`fdm3-sideways-trigger`}r
#   is not oob (both on closed-prev))"*. ONE timeframe, not a set - his 1114 clarification. Both
#   lines are read at that timeframe: ws{N}b and ws{N}r, closed-prev at N*60 s.
SIDEWAYS_TRIGGER = _knob('SIDEWAYS_TRIGGER', 5, int)      # his `fdm3-sideways-trigger`

#   HIS SPEC LINE: *"create a +/-12.5 minute window centered on"* each of the two retest bars, and
#   he named it on 1114. MINUTES, each side of the centre, so the span is twice this.
SIDEWAYS_RETEST_SCAN_WINDOW = _knob('SIDEWAYS_RETEST_SCAN_WINDOW', 12.5)   # his `...-scan-window`

#   HIS SPEC LINE: *"IF the abs(pxs diff) between pxs-retest-floater's ohlc "open extremum and
#   pxs-retest-anchor's ohlc "open" extermum is <={knob:0.88,`fdm3-sideways-retest-diff-pct`}%"*.
#   THE BASE IS THE EARLIER OF THE TWO OPENS, settled by his own 1114 measurement: he read 0.78%
#   between the 2026-09-23 04:24 and 04:27 ws1 closes with TradingView's price range tool, and of
#   the three candidate bases only the earlier value and the midpoint round to 0.78%. His tool
#   divides by the first price clicked, so the earlier value is the one that matches both.
SIDEWAYS_RETEST_DIFF_PCT = _knob('SIDEWAYS_RETEST_DIFF_PCT', 0.88)   # his `...-retest-diff-pct`

RULED = {
    'SIDEWAYS_TRIGGER': (5, 'his `fdm3-sideways-trigger` - the ONE timeframe whose b and r lines '
                            'the sideways trigger reads, closed-prev'),
    'SIDEWAYS_RETEST_SCAN_WINDOW': (12.5, 'his `fdm3-sideways-retest-scan-window` - minutes each '
                                          'side of the centre, so a 25 minute span'),
    'SIDEWAYS_RETEST_DIFF_PCT': (0.88, 'his `fdm3-sideways-retest-diff-pct` - the open-extremum '
                                       'gap ceiling, as a percent of the EARLIER open'),
}


def live():
    """-> [(name, value)], every knob this module reads. A report prints these beside its rows."""
    return [(k, globals()[k]) for k in sorted(RULED)]


def check(out=None):
    """THE RULED CHECK. Refuses an off-ruled run unless W_FDM3_EXPERIMENT=1. Called at import."""
    out = out or sys.stderr
    off = [(k, globals()[k], v, why) for k, (v, why) in RULED.items() if globals()[k] != v]
    if not off:
        return True
    msg = '; '.join('%s is %r, ruled %r (%s)' % (k, got, want, why) for k, got, want, why in off)
    if not EXPERIMENT:
        raise RuntimeError('OFF-RULED fdm3 run refused. ' + msg
                           + '. Set W_FDM3_EXPERIMENT=1 to run it as an experiment.')
    out.write('# W_FDM3_EXPERIMENT=1 - THIS IS NOT THE MACHINE. %d knob(s) off the bank: %s\n'
              % (len(off), msg))
    return False


RULED_OK = check()
