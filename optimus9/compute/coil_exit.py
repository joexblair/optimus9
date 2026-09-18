"""coil_exit — which bar an exit becomes ACTIONABLE, and the ws1mage-rev that validates it.

ONE JOB: apply Joe's rule. The coil comes from stretchy_leash.py, the moments and releases from
coil_moment.py, and the `ws1mage-rev` legs from jig.ws1mage_rev - which is NOT re-implemented here.

JOE 0917, THE RULE
  a moment with a CONFIRMED coil release:
      ACTIONABLE = the release bar + confirm_lag_s.
      "that 180s is required to provide the targeted results - it's not negotiable"
      The lookback never touches these rows: "the lookback and setting of actionable timestamps is
      a bolt-on, not an overwrite".

  a moment with NO confirmed release - its `named bar` is the moment's end row:
      1. LOOKBACK - a ws1mage-rev whose cross sits in [named bar - lookback_s, named bar]
         -> ACTIONABLE = the named bar. "when you find ws1mage-rev in the 4 minute lookback that
            is anchored on 'named bar', 'named bar''s timestamp become the actionable time"
      2. GAP - else, a ws1mage-rev strictly after the named bar and at or before the bar the
         moment's `end` becomes knowable
         -> ACTIONABLE = THE FIRST of them. "the events in between are all perfect. use the first
            timestamp"
      3. else ACTIONABLE = the bar the `end` becomes knowable, unchanged.

CAUSALITY
  a ws1mage-rev counts only when its `sig_conf` - the bar it becomes KNOWABLE - is at or before
  the bar being tested. The cross bar alone is not enough; `sig_conf` = cross + boundary_xwob - 1.
  Joe 0917: "keep it causal".
"""
import numpy as np

LOOKBACK, GAP, FORWARD, CONFIRMED = 'lookback', 'gap', 'forward', 'confirmed'


def _knowable(legs, lo, hi, by):
    """ws1mage-rev cross bars in [lo, hi] whose sig_conf is at or before `by`. Ascending."""
    return [int(a) for a, b in zip(legs['sig'], legs['sig_conf']) if lo <= a <= hi and int(b) <= by]


def first_forward(legs, bar):
    """The producer's own consumer walk from `bar`: first dwell_ok at or after it, then the first
    rev at or after that, then the first sig STRICTLY after that anchor. -> bar or None."""
    dk, rv, sg = legs['dwell_ok'], legs['rev'], legs['sig']
    i = np.searchsorted(dk, bar, 'left')
    if i >= len(dk):
        return None
    j = np.searchsorted(rv, int(dk[i]), 'left')
    if j >= len(rv):
        return None
    k = np.searchsorted(sg, int(rv[j]) + 1, 'left')
    return int(sg[k]) if k < len(sg) else None


def resolve(moment, pick, confirmed, legs, lag_bars, lookback_bars, gap_fill=True):
    """Where this moment's exit becomes actionable, and the ws1mage-rev that validates it.

    `pick`/`confirmed` come from coil_moment.release. `legs` is jig.ws1mage_rev()[dr].
    -> dict: named (the bar the rule anchors on), base (the actionable before the bolt-on),
             actionable, rev (the validating bar, or None), via.
    """
    if confirmed:
        named = pick
        base = pick + lag_bars
        return dict(named=named, base=base, actionable=base,
                    rev=first_forward(legs, base), via=CONFIRMED)

    named = moment['i1']
    base = moment['brk'] if moment['brk'] is not None else moment['i1']

    hit = _knowable(legs, named - lookback_bars, named, named)
    if hit:
        return dict(named=named, base=base, actionable=named, rev=named, via=LOOKBACK)

    if gap_fill:
        inside = _knowable(legs, named + 1, base, base)
        if inside:
            first = inside[0]
            return dict(named=named, base=base, actionable=first, rev=first, via=GAP)

    return dict(named=named, base=base, actionable=base,
                rev=first_forward(legs, base), via=FORWARD)
