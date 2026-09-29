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

  AND THE BAR THIS MODULE EMITS IS THE `sig_conf`, NOT THE CROSS. Joe 0929, ruling it: *"sig_conf
  is unconditional - it has to happen"*, after reading the defect himself: *"sig has already
  qualified the wob in code, but the wrong field was presented. every change will be exactly
  15sec"*. He is right about the producer - `jig.oob_ib_cross` only emits a cross once IB has held
  `boundary_xwob` bars, and hands back BOTH bars as (cross_idx, conf_idx, side). This module used
  to take the cross and drop the conf, which named the event correctly and acted on it 15 s before
  the evidence existed. `jig.py`'s own docstring already said so: "Carry sig_conf wherever a
  consumer needs to act on the event."

  THE CROSS STILL IDENTIFIES THE EVENT; THE CONF IS WHEN YOU MAY ACT ON IT. Every SELECTION below
  is still made on the cross bar - which sig is first, which sits inside the lookback - and only
  the bar handed back moves. `boundary_xwob` is 4, so every move is exactly 3 bars = 15 s.

  WHERE IT LANDS, per branch:
    CONFIRMED  `rev` moves. `actionable` is the release bar + confirm_lag_s, not a mage-rev - unchanged
    LOOKBACK   nothing moves. `_knowable` already required sig_conf <= named, so `named` is at or
               after the conf bar by construction
    GAP        `rev` AND `actionable` move. The cross was `_knowable` by `base`, but acting ON the
               cross bar is still 15 s before that cross's own confirmation
    FORWARD    `rev` moves. `actionable` is `base` - unchanged
"""
import numpy as np

LOOKBACK, GAP, FORWARD, CONFIRMED = 'lookback', 'gap', 'forward', 'confirmed'


def _knowable(legs, lo, hi, by):
    """ws1mage-rev events whose CROSS sits in [lo, hi] and whose sig_conf is at or before `by`.

    -> [(cross, conf)], ascending by cross. The cross is what the window test is made on; the conf
    is the bar a consumer may act on. See the module docstring.
    """
    return [(int(a), int(b)) for a, b in zip(legs['sig'], legs['sig_conf'])
            if lo <= a <= hi and int(b) <= by]


def first_forward(legs, bar):
    """The producer's own consumer walk from `bar`: first dwell_ok at or after it, then the first
    rev at or after that, then the first sig STRICTLY after that anchor. -> bar or None.

    The SELECTION is on the cross bar - `sg[k]` is the first cross after the anchor - and the bar
    RETURNED is that cross's `sig_conf`. Joe 0929: *"sig_conf is unconditional - it has to happen"*.
    """
    dk, rv, sg, sc = legs['dwell_ok'], legs['rev'], legs['sig'], legs['sig_conf']
    i = np.searchsorted(dk, bar, 'left')
    if i >= len(dk):
        return None
    j = np.searchsorted(rv, int(dk[i]), 'left')
    if j >= len(rv):
        return None
    k = np.searchsorted(sg, int(rv[j]) + 1, 'left')
    return int(sc[k]) if k < len(sg) else None


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
            first = inside[0][1]              # the FIRST cross after `named`, at ITS conf bar
            return dict(named=named, base=base, actionable=first, rev=first, via=GAP)

    return dict(named=named, base=base, actionable=base,
                rev=first_forward(legs, base), via=FORWARD)
