"""test_arm_state — proves the two properties `arm_state.py`'s docstring claims.

Written because the docstring claimed them. `fastverdict.py` claims a `verify()` that does not
exist, and that gap is item 13 in `docs/o9-live-recon/OPEN.md`; this file is here so `arm_state.py`
does not repeat it.

    P1  THE WARMUP IS BOUNDED. A walk seeded at `warmup_from(mage, k)` reproduces the state at `k`
        that a walk seeded at bar 0 gives. This is what makes the arm live-safe on a bounded
        window, and it is the property `dr_latch.latch_wob` does NOT have.
    P2  THE ARM IS SET ON THE FIRST BAR THE RUN REACHES `wob`, never a later bar inside the same
        run. Joe 0930 caught that defect twice, in `update_ws5mage_sig_backing_latch.py` and in
        `twowin.py`.

P3 and P4 are the mech's own rules, tested on synthetic series so a failure names the rule:
    P3  a MID cross cancels, from EITHER direction, and resets the run
    P4  a dr change inside an oob run restarts the run

    python3 -m pytest tests/test_arm_state.py -q
    python3 tests/test_arm_state.py              # same checks, no pytest needed
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimus9.compute.arm_state import ArmState, episodes, run, warmup_from  # noqa: E402

FENCE = (25.0, 75.0)     # Joe 1001, the Mage fence for this mech
WOB = 6                  # Joe 1001, 6 bars = 30 s at the 5 s grid


def _seeded(mage, dr, seed, k, fence=FENCE, wob=WOB):
    """The state at bar `k` from a walk that started at `seed`. -> (live, arm, arm_dr)."""
    st = ArmState(fence, wob)
    out = (False, -1, 0)
    for j in range(seed, k + 1):
        out = st.step(j, float(mage[j]), None if j == seed else float(mage[j - 1]),
                      int(dr[j]), None if j == seed else int(dr[j - 1]))
    return out


def _series(n=4000, seed=11):
    """A Mage series that crosses MID often, and a dr that flips independently."""
    rng = np.random.default_rng(seed)
    mage = 50.0 + np.cumsum(rng.normal(0, 4.0, n))
    mage = 50.0 + 45.0 * np.tanh((mage - 50.0) / 40.0)       # keep it inside 5..95
    dr = np.where(np.cumsum(rng.normal(0, 1.0, n)) > 0, 1, -1).astype(np.int8)
    return mage, dr


def test_p1_warmup_is_bounded():
    """Seeding at `warmup_from(k)` gives the same state at `k` as seeding at bar 0."""
    mage, dr = _series()
    full = run(mage, dr, 0, len(mage) - 1, FENCE, WOB)
    checked = 0
    for k in range(50, len(mage), 7):
        s = warmup_from(mage, k, floor=0)
        got = _seeded(mage, dr, s, k)
        exp = (bool(full[0][k]), int(full[1][k]), int(full[2][k]))
        assert got == exp, 'P1 failed at bar %d: seed %d gave %r, full walk gave %r' % (k, s, got, exp)
        checked += 1
    assert checked > 100, 'P1 checked too few bars: %d' % checked
    return checked


def test_p2_arm_is_the_first_bar_the_run_reaches_wob():
    """One long oob run: the arm sits on the wob-th bar, and does not move for the rest of the run."""
    n = 40
    mage = np.full(n, 80.0)        # oob on the dr +1 side for the whole series
    mage[0] = 60.0                 # start IB so the run begins at bar 1, no MID cross
    dr = np.ones(n, np.int8)
    live, arm, adr = run(mage, dr, 0, n - 1, FENCE, WOB)
    first = 1 + WOB - 1            # the run starts at bar 1 and reaches WOB here
    assert not live[first - 1], 'P2: armed too early, at bar %d' % (first - 1)
    assert live[first], 'P2: not armed at the bar the run reaches wob, %d' % first
    assert set(int(a) for a in arm[first:]) == {first}, \
        'P2: the arm bar moved inside one run: %r' % sorted(set(int(a) for a in arm[first:]))
    assert set(int(a) for a in adr[first:]) == {1}, 'P2: arm_dr moved inside one run'
    return first


def test_p3_mid_cross_cancels_from_either_direction():
    """An armed state is cleared by a MID cross, up or down, and the run restarts after it."""
    for side, oobv, ibv, crossv, d in ((+1, 80.0, 60.0, 20.0, 1), (-1, 20.0, 40.0, 80.0, -1)):
        n = 30
        mage = np.full(n, float(oobv))
        mage[0] = float(ibv)
        mage[20] = float(crossv)          # crosses MID at bar 20
        dr = np.full(n, d, np.int8)
        live, arm, _ = run(mage, dr, 0, n - 1, FENCE, WOB)
        assert live[19], 'P3 dr %+d: should be armed before the cross' % d
        assert not live[20], 'P3 dr %+d: the MID cross did not cancel' % d
        assert arm[20] == -1, 'P3 dr %+d: arm bar not cleared on cancel' % d
        # bar 20 is IB-or-opposite, so the run restarts at 21 and re-arms WOB bars later
        assert live[21 + WOB - 1], 'P3 dr %+d: did not re-arm after the cross' % d
    return True


def test_p4_dr_change_restarts_the_run():
    """A dr flip part-way through an oob run restarts the run rather than carrying it."""
    n = 30
    mage = np.full(n, 80.0)        # oob on the +1 side throughout; never crosses MID
    mage[0] = 60.0
    dr = np.ones(n, np.int8)
    dr[4:] = 1                     # control: no flip -> arms at bar 1+WOB-1
    live_a, _, _ = run(mage, dr, 0, n - 1, FENCE, WOB)
    dr2 = np.ones(n, np.int8)
    dr2[3] = -1                    # a one-bar flip at bar 3, inside the run
    live_b, arm_b, _ = run(mage, dr2, 0, n - 1, FENCE, WOB)
    assert live_a[1 + WOB - 1], 'P4 control: should arm at bar %d' % (1 + WOB - 1)
    assert not live_b[1 + WOB - 1], 'P4: the dr flip did not restart the run'
    assert live_b[4 + WOB - 1], 'P4: did not arm %d bars after the run restarted' % WOB
    return int(arm_b[4 + WOB - 1])


def test_episodes_match_the_live_array():
    """`episodes` reports exactly the spans where `live` is True, with the arm's own dr."""
    mage, dr = _series()
    live, arm, adr = run(mage, dr, 0, len(mage) - 1, FENCE, WOB)
    n = len(mage)
    eps = episodes(live, arm, adr, 0, n - 1)
    covered = np.zeros(n, bool)
    for a, b, d, cancelled in eps:
        assert live[a], 'episode starts at a bar that is not live: %d' % a
        assert int(arm[a]) == a, 'episode arm bar %d does not match arm[%d]=%d' % (a, a, arm[a])
        assert int(adr[a]) == d, 'episode dr %+d does not match arm_dr[%d]=%+d' % (d, a, adr[a])
        # end_bar has ONE meaning: the first bar NOT live. [a, b) is the live span.
        assert b > a, 'episode end %d is not after its arm %d' % (b, a)
        if cancelled:
            assert b <= n - 1 and not live[b], \
                'cancelled episode ends at %d but live[%d] is True' % (b, b)
        else:
            assert b == n, 'uncancelled episode should end at i1+1 = %d, got %d' % (n, b)
        covered[a:b] = True
    assert np.array_equal(covered, live), \
        'episodes do not cover `live` exactly: %d bars differ' % int((covered != live).sum())
    return len(eps)


def test_step_refuses_non_consecutive_bars():
    """The stepper rejects a skipped bar rather than silently carrying stale state."""
    st = ArmState(FENCE, WOB)
    st.step(10, 80.0, None, 1, None)
    try:
        st.step(12, 80.0, 80.0, 1, 1)
    except ValueError:
        return True
    raise AssertionError('step accepted a skipped bar')


def test_p5_dr_zero_cannot_arm():
    """dr 0 has no side, so the arm must not fire on it — from EITHER side of the fence.

    `dr_latch` returns 0 until both lines first agree, so a live walk on a cold window carries 0 for
    its opening bars. Before the 1001 guard, `oob = (mage >= hi) if d > 0 else (mage <= lo)` read 0
    as the LOW side: dr 0 with the Mage pinned at 20 armed at bar 6 carrying arm_dr 0, which then
    flowed into momentum_true and flat_run_at as a direction.
    """
    for pin, label in ((20.0, 'low side'), (80.0, 'high side'), (50.0, 'at MID')):
        n = 30
        mage = np.full(n, float(pin))
        mage[0] = 50.5
        dr = np.zeros(n, np.int8)
        live, arm, adr = run(mage, dr, 0, n - 1, FENCE, WOB)
        assert not live.any(), 'P5 %s: armed on dr 0 at bar %d' % (label, int(np.argmax(live)))
        assert set(int(x) for x in arm) == {-1}, 'P5 %s: an arm bar was set on dr 0' % label
        assert set(int(x) for x in adr) == {0}, 'P5 %s: a non-zero arm_dr on dr 0' % label
    # and a dr that ARRIVES after a cold start still arms normally
    n = 30
    mage = np.full(n, 80.0)
    mage[0] = 60.0
    dr = np.zeros(n, np.int8)
    dr[3:] = 1                      # dr arrives at bar 3
    live, arm, _ = run(mage, dr, 0, n - 1, FENCE, WOB)
    assert live[3 + WOB - 1], 'P5: did not arm %d bars after the dr arrived' % WOB
    assert not live[3 + WOB - 2], 'P5: armed before the run reached wob'
    return int(arm[3 + WOB - 1])


if __name__ == '__main__':
    n1 = test_p1_warmup_is_bounded()
    print('P1 warmup is bounded                     OK  %d bars checked' % n1)
    print('P2 arm = first bar the run reaches wob   OK  arm at bar %d' % test_p2_arm_is_the_first_bar_the_run_reaches_wob())
    print('P3 MID cross cancels either direction    OK' if test_p3_mid_cross_cancels_from_either_direction() else 'P3 FAIL')
    print('P4 dr change restarts the run            OK  re-arm at bar %d' % test_p4_dr_change_restarts_the_run())
    print('P5 dr 0 cannot arm                       OK  arm at bar %d once dr arrives' % test_p5_dr_zero_cannot_arm())
    print('episodes match the live array            OK  %d episodes' % test_episodes_match_the_live_array())
    print('step refuses non-consecutive bars        OK' if test_step_refuses_non_consecutive_bars() else 'FAIL')
