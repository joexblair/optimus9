"""ride_to_max — ride the momentum-true lines to their max test-point, then test the cascade.

Joe 0915: *"let's build a mech that rides the evolving ws1,2,3,4 momentum-true lines to their max
test-point, test for the slopey Mages, and create a trade signal if valid. in essence, this mech
is what would move the trade from ~11:29 to its ws4r sideways event at ~11:49"*

THE LADDER IS HIS, 0915:
    "wsf will attempt to reach all of the test-points (ws1, ws2, ws3).
     -if ws1 finds momentum in ws2, the walk walks to the ws2 test-point. if ws1 finds momentum in
      ws3, the walk will walk to ws3 test-point
     -same for ws2 - it reaches it's test-point and tests for momentum in ws3 and ws4, and walks to
      whichever has claimed momentum
     -if momentum is not found in ws2 or ws3 or ws4 (at ws1 test-point), then we test for a route
      condition at ws1 test-point"

SRP: this module WALKS THE LADDER AND REPORTS WHAT IT FINDS. It does not compute the momentum
verdict (momo_core), it does not find a flat-run (jig.sideways_reversal), it does not size or place
a trade, and it owns no threshold - every gate arrives as an argument.

FOUR READINGS, DERIVED FROM JOE'S OWN ANSWERS, NOT NEW DECISIONS:
  MAX TEST-POINT   the rung whose test-point finds NO line above it, up to `ride_hi`, momentum-true.
                   ws`ride_hi` is terminal by construction - nothing above it is inside wsf.
                   THE RIDDEN LINE REACHES FOR A TEST-POINT OF ITS OWN - Joe 0915 confirmed this
                   was implied but never written: ws4r's flat-run is a ws4 test-point, read with
                   the same producer and the same rule as ws1's.
  WHICH LINE RIDES when several claim momentum, the HIGHEST. Joe 0913: "the highest TF printing
                   momentum is the line we ride until its flat-run signal".
  dr               fixed for the whole climb. Spec 17.2.
  THE CASCADE      route 3's own cut, unchanged: the ws1..ws12 Mage drop and its crookedness.
  THE FENCE        the r-momo-fence, 83/17, on EVERY test-point. Joe 0915: *"apply r-momo-fence to
                   the test-points"*. It replaces the 40/60 mid-zone fence the flat-run shipped
                   with. This re-cuts the ws1 population too, not only the ride.

WHEN THE CASCADE FAILS AT THE MAX TEST-POINT, IT GOES TO DTF. Joe 0915, ruling the last open
fork: *"handoff to DTF. that means that for our current science activities, we would drop it from
the list"*. So `on_fail` defaults to 'handoff', and a caller running the science set DROPS the row
rather than trading it. 'none' is kept only for a caller that wants the ride without the routing.

CAUSAL, with one stated delay. Every verdict is read at its own bar from bars <= it, and the climb
only moves forward. The EXCEPTION is the divergence, whose anchors are the 24 bars AFTER a
test-point (spec 17.1 step 6): a rung carried by a divergence is knowable up to 120 s later, and
`known_at` carries that bar so a caller never acts earlier than it may.
"""
import numpy as np

import optimus9.compute.momo_core as X
from optimus9.compute.momo_config import momo_config
from optimus9.compute.momo_gated import momo_window, curl_gates
from optimus9.analysis.jig import sideways_reversal


def momentum_true(r, bank, cfg, k, dr, seam_dr, span_min=10):
    """The spec 17.1 step 10 verdict. `momo`, or a curl facing dr. Delegates; decides nothing."""
    b = dict(bank)
    b.update({q: cfg[q] for q in ('momo_slope_min', 'momo_slack_ref', 'momo_r2_min',
                                  'level_slack', 'momo_seam')})
    with momo_config(b), momo_window(span_min):
        f = X.momo_fit(r, dr, k, quad=True)
        f['seam_dr'] = bool(seam_dr)
        st, _ = X.verdict(f)
        if st == 'curl':
            ok, _ = curl_gates(f, gate2=True)
            st = 'curl' if ok else 'none'
    return st in ('momo', 'curl'), st


def cascade(M, k, dr, tf_lo=1, tf_hi=12):
    """The slopey-Mage measurement, route 3's own. Reports; gates nothing.

    drop   dr * (M[tf_lo] - M[tf_hi]) at bar k. Positive = the cascade falls AWAY from dr as the
           timeframe rises, which is the cycle-87 shape.
    wrong  of the tf_hi-tf_lo steps, how many run against the cascade. 0 = perfectly ordered.
    """
    v = np.array([M[tf][k] for tf in range(tf_lo, tf_hi + 1)], float)
    if not np.isfinite(v).all():
        return None
    steps = dr * -np.diff(v)
    return {'v': v, 'drop': float(dr * (v[0] - v[-1])), 'wrong': int((steps < 0).sum()),
            'spread': float(v.max() - v.min())}


def next_test_point(r, k, dr, ts_len, fence=None):
    """The line's own flat-run signal, strictly after k. jig.sideways_reversal, not re-implemented.

    `fence` is the band the run must sit on the dr side of. Joe 0915: *"use the r-momo-fence - it
    should give the correct response"*, and then *"apply r-momo-fence to the test-points"* - ALL of
    them, ws1 included, not just the ridden line. Passed as (lo, hi); None keeps the producer's own
    default, which is the 40/60 mid-zone fence.
    """
    kw = {} if fence is None else {'fence': tuple(fence)}
    ev = sideways_reversal(r, np.zeros(ts_len), dr, i0=int(k) + 1, first=True, **kw)
    return int(ev[0][0]) if ev else None


def ride(k, dr, R, M, banks, seams, cfg, ride_hi=4, tf_hi=12, drop_min=39.1, wrong_max=1,
         on_fail='handoff', divergence=None, span_min=10, ts_len=None, fence=None):
    """Walk the ladder from a ws1 test-point to its max test-point, then test the cascade.

    k          the ws1 test-point bar
    R, M       {tf: r line}, {tf: Mage line} on the 5 s grid
    banks      {tf: momo bank}
    seams      {tf: the dr-facing-seam fact at the bar under test}
    cfg        the momentum config
    ride_hi    the highest timeframe wsf rides. `handoff.ride_tf_hi`, banked at 4
    tf_hi      the top of the Mage cascade. `band_wsf_hi`, banked at 12
    drop_min   the cascade's drop gate. Route 3's, anchored to cycle 87
    wrong_max  the cascade's crookedness gate. Route 3's
    fence      the band a test-point's flat run must sit on the dr side of, as (lo, hi). Joe 0915
               moved this to the r-momo-fence: momo_fence_r 17 -> (17.0, 83.0). None keeps the
               producer's 40/60 mid-zone default
    on_fail    what to do when the cascade fails. 'handoff' (the default, Joe 0915) = delegate to
               the handoff routing machine, which for the science set means DROP THE ROW. 'none'
               emits no signal and says nothing about routing
    divergence optional callable(bar, dr) -> firing bar or None. Costs up to 120 s of delay

    -> {'rungs': [...], 'max_bar', 'max_rung', 'cascade', 'valid', 'signal', 'known_at', 'why'}
    """
    n = int(ts_len if ts_len is not None else len(R[1]))
    rungs, rung, bar, known = [], 1, int(k), int(k)
    while True:
        claims, states = [], {}
        for tf in range(rung + 1, int(ride_hi) + 1):
            t, st = momentum_true(R[tf], banks[tf], cfg, bar, dr, seams.get(tf, False), span_min)
            at = int(bar)
            if not t and divergence is not None:
                fired = divergence(bar, dr)
                if fired is not None:
                    t, st, at = True, 'divergence', int(fired)
            states[tf] = st
            if t:
                claims.append((tf, at))
        rec = {'rung': rung, 'bar': int(bar), 'states': states,
               'claims': [tf for tf, _ in claims]}
        if not claims:
            rec['end'] = 'max test-point - nothing above it carries'
            rungs.append(rec)
            break
        if rung >= int(ride_hi):
            rec['end'] = 'ride ceiling ws%d' % ride_hi
            rungs.append(rec)
            break
        nxt = max(tf for tf, _ in claims)
        known = max(known, max(at for _, at in claims))
        rec['end'] = 'climbs to ws%d' % nxt
        rungs.append(rec)
        nb = next_test_point(R[nxt], bar, dr, n, fence)
        if nb is None or nb >= n - 1:
            rungs.append({'rung': nxt, 'bar': None, 'states': {}, 'claims': [],
                          'end': 'no flat-run on ws%d before the tape ends' % nxt})
            return {'rungs': rungs, 'max_bar': None, 'max_rung': nxt, 'cascade': None,
                    'valid': False, 'signal': None, 'known_at': known,
                    'why': 'the ride never reached a max test-point'}
        rung, bar = nxt, nb

    c = cascade(M, bar, dr, 1, int(tf_hi))
    ok = bool(c is not None and c['drop'] >= float(drop_min) and c['wrong'] <= int(wrong_max))
    if ok:
        why = 'the cascade holds at the max test-point'
        sig = {'bar': int(bar), 'dr': int(dr), 'side': 'SHORT' if dr > 0 else 'LONG',
               'rung': int(rung), 'known_at': max(known, int(bar))}
    else:
        why = ('the cascade fails at the max test-point -> ' +
               ('no signal' if on_fail == 'none'
                else 'hand off to dtf; dropped from the science set'))
        sig = None
    return {'rungs': rungs, 'max_bar': int(bar), 'max_rung': int(rung), 'cascade': c,
            'valid': ok, 'signal': sig, 'known_at': max(known, int(bar)), 'why': why,
            'on_fail': on_fail}
