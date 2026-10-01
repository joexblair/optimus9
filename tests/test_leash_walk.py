"""test_leash_walk — holds the two equivalences `leash_walk.py`'s docstring claims.

    Q1  THE QUALIFY COUNTER MATCHES THE SORTED FORM. The offline form collects every departure in
        an episode, sorts them, and takes index `fall - 1`, which reads like an end-of-episode
        computation. `LeashWalk` carries a live counter instead. This holds the two against each
        other on random departure orders, including ties on one bar.
    Q2  `rev_lookback_mask` MATCHES `coil_exit._knowable` bar for bar. The mask is a vectorised
        restatement of `_knowable(legs, k - lookback, k, k)` being non-empty, and Joe's own
        function is the reference.

Two more, because they are the rules a port is most likely to get wrong:
    Q3  no per-episode state crosses an arm. A departure or a flat-run start from episode 1 must
        not count toward episode 2
    Q4  the race lookback is TRAILING and inclusive of k

    python3 -m pytest tests/test_leash_walk.py -q
    python3 tests/test_leash_walk.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimus9.compute.coil_exit import _knowable  # noqa: E402
from optimus9.compute.leash_walk import LeashWalk, rev_lookback_mask  # noqa: E402

LADDER = list(range(4, 24))          # ws4..ws23, the mech's ladder
KNOBS = dict(arm_fence=(25.0, 75.0), arm_wob=6, min_tf=7, fall=3, race=1, frmin=4,
             lb_bars=48, rev_lookback=48)


def _armed_walk(n, **over):
    """A walk whose arm is live from bar `arm_wob` onward: Mage pinned oob on the dr +1 side."""
    kn = dict(KNOBS); kn.update(over)
    w = LeashWalk(LADDER, **kn)
    mage = np.full(n, 80.0); mage[0] = 60.0        # start IB, no MID cross, run begins at bar 1
    dr = np.ones(n, np.int8)
    return w, mage, dr


def test_q1_qualify_counter_matches_the_sorted_form():
    """For random departure schedules, the live counter's qualify bar == sorted(deps)[fall-1]."""
    rng = np.random.default_rng(5)
    elig = [t for t in LADDER if t >= KNOBS['min_tf']]
    checked = 0
    for trial in range(200):
        n = 120
        fall = int(rng.integers(1, 6))
        # each eligible tf is momentum-true from bar 10, then departs on its own bar (or never)
        depart = {}
        for t in elig:
            depart[t] = int(rng.integers(12, n)) if rng.random() < 0.7 else None
        w, mage, dr = _armed_walk(n, fall=fall)
        got = None
        for k in range(n):
            mom = (lambda t, _k=k: 10 <= _k and (depart[t] is None or _k < depart[t]))
            fr = (lambda t: False)
            w.step(k, float(mage[k]), None if k == 0 else float(mage[k - 1]),
                   int(dr[k]), None if k == 0 else int(dr[k - 1]),
                   0.0, None if k == 0 else 0.0, mom, fr, False)
            if got is None and w.state['qualify'] is not None:
                got = w.state['qualify']
        deps = sorted(v for v in depart.values() if v is not None)
        exp = deps[fall - 1] if len(deps) >= fall else None
        assert got == exp, ('Q1 trial %d fall %d: counter gave %r, sorted form gave %r'
                            % (trial, fall, got, exp))
        checked += 1
    assert checked == 200
    return checked


def test_q2_rev_mask_matches_knowable():
    """rev_lookback_mask(k) == bool(_knowable(legs, k-lookback, k, k)) on every bar."""
    rng = np.random.default_rng(9)
    n = 3000
    lookback = KNOBS['rev_lookback']
    hold = 4                                  # boundary_xwob 4 -> sig_conf = sig + 3
    sig = np.sort(rng.choice(np.arange(5, n - 10), size=180, replace=False)).astype(np.int64)
    sig_conf = sig + (hold - 1)
    legs = {'sig': sig, 'sig_conf': sig_conf}
    mask = rev_lookback_mask(sig, sig_conf, n, lookback)
    bad = 0
    for k in range(0, n):
        ref = bool(_knowable(legs, k - lookback, k, k))
        if bool(mask[k]) != ref:
            bad += 1
    assert bad == 0, 'Q2: %d of %d bars disagree with coil_exit._knowable' % (bad, n)
    return n


def test_q3_no_state_crosses_an_arm():
    """A departure and a flat-run start in episode 1 must not count toward episode 2."""
    n = 60
    w = LeashWalk(LADDER, **KNOBS)
    # oob +1 for bars 1..19, MID cross at 20, oob again from 21
    mage = np.full(n, 80.0); mage[0] = 60.0; mage[20] = 20.0
    dr = np.ones(n, np.int8)
    # every eligible tf is mom-true at bars 1..9 then departs at 10 — all inside episode 1
    seen2 = None
    for k in range(n):
        mom = (lambda t, _k=k: 1 <= _k < 10)
        fr = (lambda t, _k=k: _k == 11)
        w.step(k, float(mage[k]), None if k == 0 else float(mage[k - 1]),
               int(dr[k]), None if k == 0 else int(dr[k - 1]),
               0.0, None if k == 0 else 0.0, mom, fr, True)
        if k == 19:
            assert w.state['qualify'] is not None, 'Q3 setup: episode 1 never qualified'
        if k == n - 1:
            seen2 = dict(w.state)
    assert seen2['arm'] == 21 + KNOBS['arm_wob'] - 1, \
        'Q3 setup: episode 2 armed at %r' % (seen2['arm'],)
    assert seen2['qualify'] is None, 'Q3: episode 1 departures leaked into episode 2'
    assert seen2['departed'] == [], 'Q3: departed set leaked: %r' % (seen2['departed'],)
    return seen2['arm']


def test_q4_race_lookback_is_trailing_and_inclusive():
    """One flat-run start at bar S fires the race at S and at S+lb, and not at S+lb+1."""
    lb = 10
    n = 80
    w, mage, dr = _armed_walk(n, lb_bars=lb, fall=1, race=1, min_tf=7, frmin=4)
    S = 30
    fires = []
    for k in range(n):
        # one eligible tf departs at bar 12 so qualify and turn are both long past
        mom = (lambda t, _k=k: 5 <= _k < 12)
        fr = (lambda t, _k=k: t == 4 and _k == S)
        hit = w.step(k, float(mage[k]), None if k == 0 else float(mage[k - 1]),
                     int(dr[k]), None if k == 0 else int(dr[k - 1]),
                     1.0 if k == 0 else 1.0 - k * 1e-6,      # coil ticks down every bar
                     None if k == 0 else 1.0 - (k - 1) * 1e-6,
                     mom, fr, True)
        if hit:
            fires.append(k)
    assert S in fires, 'Q4: the race did not fire on the start bar %d' % S
    assert S + lb in fires, 'Q4: the race did not fire at the end of the lookback, %d' % (S + lb)
    assert S + lb + 1 not in fires, 'Q4: the race fired one bar past the lookback, %d' % (S + lb + 1)
    return len(fires)


def test_step_refuses_non_consecutive_bars():
    w = LeashWalk(LADDER, **KNOBS)
    w.step(10, 80.0, None, 1, None, 0.0, None, lambda t: False, lambda t: False, False)
    try:
        w.step(12, 80.0, 80.0, 1, 1, 0.0, 0.0, lambda t: False, lambda t: False, False)
    except ValueError:
        return True
    raise AssertionError('step accepted a skipped bar')


if __name__ == '__main__':
    print('Q1 qualify counter == sorted form        OK  %d trials' % test_q1_qualify_counter_matches_the_sorted_form())
    print('Q2 rev mask == coil_exit._knowable       OK  %d bars, 0 disagree' % test_q2_rev_mask_matches_knowable())
    print('Q3 no state crosses an arm               OK  episode 2 arm at bar %d' % test_q3_no_state_crosses_an_arm())
    print('Q4 race lookback trailing + inclusive    OK  %d fires' % test_q4_race_lookback_is_trailing_and_inclusive())
    print('step refuses non-consecutive bars        OK' if test_step_refuses_non_consecutive_bars() else 'FAIL')
