"""stack_model must mirror services.fakeapi.engine.MatchingEngine exactly (register E5)."""
import pytest

from optimus9.live.risk import leg_further_along
from optimus9.live.stack_model import PositionStack


def test_add_reweights_avg_entry_like_engine():
    s = PositionStack(fee_bps=0.0)
    s.add(-1, 0.1000, 100)
    s.add(-1, 0.1010, 100)
    p = s.get(-1)
    assert p.size == 200
    assert p.avg_entry == pytest.approx((0.1000 * 100 + 0.1010 * 100) / 200)   # engine.py:55
    assert p.first_px == 0.1000                                                # governor reference
    assert p.n_adds == 2


def test_close_realized_matches_engine_formula():
    s = PositionStack(fee_bps=0.0)
    s.add(1, 0.1000, 100)
    pnl = s.close(1, 0.1050)
    assert pnl == pytest.approx(1 * (0.1050 - 0.1000) * 100)                   # engine.py:64
    assert s.get(1) is None


def test_short_profits_when_price_falls():
    s = PositionStack(fee_bps=0.0)
    s.add(-1, 0.1000, 100)
    assert s.close(-1, 0.0950) == pytest.approx(-1 * (0.0950 - 0.1000) * 100)


def test_close_takes_whole_averaged_stack_not_one_leg():
    """The exchange holds ONE position per side. A reversal exit closes all of it (register E1)."""
    s = PositionStack(fee_bps=0.0)
    s.add(-1, 0.1000, 100)
    s.add(-1, 0.0990, 100)              # further along -> a good add
    pnl = s.close(-1, 0.0980)
    assert pnl == pytest.approx(-1 * (0.0980 - 0.0995) * 200)                  # avg 0.0995, size 200
    assert s.get(-1) is None


def test_fees_charged_per_side_and_reduce_realized():
    s = PositionStack(fee_bps=10.0)                                            # 0.1% per side
    s.add(1, 100.0, 1)
    assert s.realized == pytest.approx(-0.1)                                   # entry fee only
    s.close(1, 100.0)
    assert s.realized == pytest.approx(-0.2)                                   # + exit fee, flat price


def test_partial_close_leaves_avg_entry_untouched():
    s = PositionStack(fee_bps=0.0)
    s.add(1, 0.1000, 100)
    s.close(1, 0.1100, qty=40)
    p = s.get(1)
    assert p.size == 60 and p.avg_entry == pytest.approx(0.1000)


def test_close_flat_side_is_noop():
    assert PositionStack().close(1, 0.1) == 0.0


def test_gross_exposure_does_not_net_hedged_sides():
    s = PositionStack(fee_bps=0.0)
    s.add(1, 0.1, 100)
    s.add(-1, 0.1, 100)
    assert s.gross_exposure(0.1) == pytest.approx(200 * 0.1)                   # hedge mode: legs don't net


def test_reopen_after_flat_resets_the_governor_reference():
    s = PositionStack(fee_bps=0.0)
    s.add(-1, 0.1000, 100)
    s.close(-1, 0.0990)
    s.add(-1, 0.0900, 100)
    assert s.get(-1).first_px == 0.0900


# ── the first-leg pyramid gate ────────────────────────────────────────────────
def test_governor_blocks_the_0709_short_pyramid():
    """The five live shorts: each added at a WORSE price than the first. All four adds must be blocked."""
    first = 0.14344
    for px in (0.14355, 0.14374, 0.14386, 0.14390):
        assert not leg_further_along(-1, first, px, tol_pct=0.0)


def test_governor_allows_adds_further_along_the_leg():
    assert leg_further_along(-1, 0.1000, 0.0990, tol_pct=0.0)                  # short, price fell
    assert leg_further_along(1, 0.1000, 0.1010, tol_pct=0.0)                   # long, price rose


def test_governor_tolerance_admits_a_retest():
    assert not leg_further_along(-1, 0.1000, 0.1004, tol_pct=0.0)              # 0.4% worse, no tolerance
    assert leg_further_along(-1, 0.1000, 0.1004, tol_pct=0.5)                  # inside a 0.5% retest
    assert leg_further_along(1, 0.1000, 0.0996, tol_pct=0.5)
    assert not leg_further_along(-1, 0.1000, 0.1005, tol_pct=0.4)              # outside it


def test_governor_boundary_is_float_fragile_and_that_is_fine():
    """entry_px EXACTLY on first_px*(1+tol) is not decidable in binary floats: 0.1*1.005 = 0.10049999...
    We do not epsilon-pad the predicate — a leg one ULP from the tolerance edge is a coin flip either way,
    and the swept `tol` values are chosen well away from any entry price. Documented, not defended."""
    assert not leg_further_along(-1, 0.1000, 0.1005, tol_pct=0.5)              # boundary lands BLOCKED here


def test_governor_reference_is_the_first_leg_not_the_best():
    """Joe chose (a): the reference is the FIRST leg. An add above leg 2 but below leg 1 is ALLOWED."""
    first = 0.1000
    assert leg_further_along(-1, first, 0.0990, tol_pct=0.0)                   # leg 2
    assert leg_further_along(-1, first, 0.0995, tol_pct=0.0)                   # leg 3: worse than leg2, ok vs leg1
