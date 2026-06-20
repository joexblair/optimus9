"""
test_bias_machine.py — coverage for the bias_machine engine (SRP split, Joe 0619).

Two tiers:
  • golden-master — frozen window 1781753040000 (tests/fixtures/), asserts the post-split
    pk_events → verdict_magnitude (ups) reproduces the accepted outputs across 12 config keys.
    Reconstructs engine state from the fixture → NO live DB. Regenerate via tests/_gen_bias_golden.py.
  • units — synthetic, deterministic: verdict_magnitude band, _floater_extreme window, pk-state seam.
"""
import json, pathlib
import numpy as np
import pytest
import bias_machine as bm

FIX = pathlib.Path(__file__).parent / 'fixtures'


@pytest.fixture(scope='module')
def frozen_window():
    """A BiasWindow with engine arrays injected from the fixture — no DB, no __init__."""
    if not (FIX / 'bias_pk_golden.json').exists():
        pytest.skip('golden fixture missing — run tests/_gen_bias_golden.py')
    meta = json.load(open(FIX / 'bias_pk_golden.json'))
    arr = np.load(FIX / 'bias_pk_arrays.npz')
    w = object.__new__(bm.BiasWindow)
    w._osc, w.px = arr['osc'], arr['px']
    w.s14M_sign, w.s14r_sign, w.s14M = arr['s14M_sign'], arr['s14r_sign'], arr['s14M']
    w._bpt, w.W0, w.W1 = meta['bpt'], meta['W0'], meta['W1']
    return w, meta


@pytest.mark.parametrize('key', [f'{t}|{g}|{f}' for t in (6, 12) for g in ('oob', 'mid') for f in (2, 0, None)])
def test_ups_golden_master(frozen_window, key):
    """post-split ups() == frozen accepted output, byte-for-byte, per config key."""
    w, meta = frozen_window
    trig, gate, fh = key.split('|')
    fh = None if fh == 'None' else int(fh)
    out = w.ups(meta['trigs'][trig], gate, flt_half=fh)
    # normalise both through json so numpy/py scalar types compare cleanly
    assert json.loads(json.dumps(out)) == meta['golden'][key]


def test_pk_events_carries_no_verdict(frozen_window):
    """SRP: the event stream must NOT contain a call — verdict is a downstream responsibility."""
    w, meta = frozen_window
    events = w.pk_events(meta['trigs']['12'], 'oob')
    assert events and all('call' not in e for e in events)
    assert all({'t', 'side', 'anc', 'flt', 'anc_bar', 'flt_bar'} <= set(e) for e in events)


def test_verdict_magnitude_band():
    """NEUT strictly within ±NEUTRAL_BAND of the floater; else BULL/BEAR by which is higher."""
    w = object.__new__(bm.BiasWindow)
    b = bm.NEUTRAL_BAND
    ev = [dict(t=0, side=1, anc=50 + b + 0.5, flt=50.0, anc_bar=0, flt_bar=0),    # clear of band → BULL
          dict(t=1, side=-1, anc=50 - b - 0.5, flt=50.0, anc_bar=0, flt_bar=0),   # clear of band → BEAR
          dict(t=2, side=1, anc=50 + b - 0.5, flt=50.0, anc_bar=0, flt_bar=0)]    # inside band   → NEUT
    calls = [e['call'] for e in w.verdict_magnitude(ev)]
    assert calls == ['BULL', 'BEAR', 'NEUT']


def test_floater_extreme_window_and_disable():
    """±half scan returns the side-extreme in-window; half=0 ⇒ single bar = raw osc at the source."""
    w = object.__new__(bm.BiasWindow)
    w._osc = np.array([10.0, 80.0, 30.0, 90.0, 20.0])      # center=2; ±1 window = idx 1,2,3 = [80,30,90]
    assert w._floater_extreme(2, 1, 1) == (90.0, 3)        # S=+1 → max in window = 90@3
    assert w._floater_extreme(2, -1, 1) == (30.0, 2)       # S=-1 → min in window = 30@2
    assert w._floater_extreme(2, 1, 0) == (30.0, 2)        # half=0 ⇒ just the center bar (no scan)


def test_pk_state_seam_pm_vs_divergence():
    """The shared kernel: same-sign slopes → PM (±2), opposite → divergence (±1)."""
    from optimus9.compute.pk5s_gate_computer import Pk5sGateComputer as PKG
    assert float(PKG._pk_state_from_slopes(+10.0, +0.5, 0.0)) == PKG._PM_LONG    # same sign → PM
    assert float(PKG._pk_state_from_slopes(-10.0, -0.5, 0.0)) == PKG._PM_SHORT
    assert float(PKG._pk_state_from_slopes(+10.0, -0.5, 0.0)) == 1.0             # opp sign → DIV+
    assert float(PKG._pk_state_from_slopes(-10.0, +0.5, 0.0)) == -1.0
