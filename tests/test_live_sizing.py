"""PositionSizer — launch modes (smallest/fixed/dynamic5x) + split, with FARTCOIN instrument limits."""
import sys

import pytest

sys.path.insert(0, '/home/joe/thecodes')
from optimus9.live.sizing import PositionSizer, TradeIntent

# FARTCOIN: minOrderQty 1, qtyStep 1, minNotional $5, max_order 66k, 5x
SZ = PositionSizer(min_qty=1, qty_step=1, min_notional=5.0, max_order=66000, leverage=5.0)
OPEN = TradeIntent(action="open", side="Sell")
PRICE = 0.13


def test_smallest_is_five_dollar_floor():
    o = SZ.size(OPEN, equity=500, price=PRICE, mode="smallest")
    assert len(o) == 1
    assert o[0].qty == 39                       # ceil(5/0.13)=39
    assert o[0].qty * PRICE >= 5.0              # notional floor honoured
    assert o[0].side == "Sell" and not o[0].reduce_only


def test_fixed_is_max_order():
    o = SZ.size(OPEN, equity=500, price=PRICE, mode="fixed")
    assert o[0].qty == 66000


def test_dynamic5x_scales_and_caps():
    small = SZ.size(OPEN, equity=500, price=PRICE, mode="dynamic5x")[0].qty
    assert small == int(5 * 500 / PRICE)        # 19230, below the 66k cap
    big = SZ.size(OPEN, equity=5000, price=PRICE, mode="dynamic5x")[0].qty
    assert big == 66000                          # 5*5000/0.13 > 66k → capped


def test_split_divides_and_carries_remainder():
    o = SZ.size(OPEN, equity=500, price=PRICE, mode="fixed", split=3)
    assert len(o) == 3
    assert sum(x.qty for x in o) == 66000        # no coins lost
    assert o[0].qty == 22000


def test_split_too_small_collapses_to_one():
    o = SZ.size(OPEN, equity=500, price=PRICE, mode="smallest", split=10)  # 39/10 below min
    assert len(o) == 1 and o[0].qty == 39


def test_close_uses_intent_qty_and_reduce_only():
    o = SZ.size(TradeIntent(action="close", side="Buy", qty=111000), equity=500, price=PRICE)
    assert o[0].qty == 111000 and o[0].reduce_only and o[0].side == "Buy"


def test_hold_returns_nothing():
    assert SZ.size(TradeIntent(action="hold"), equity=500, price=PRICE) == []


# ── dynamic_leverage (Joe 1005): lev = (risk_pct / (n_live + 1)) / (stop_pct + drag_pct) ──
DL = PositionSizer(min_qty=1, qty_step=1, min_notional=5.0, max_order=66000, leverage=5.0,
                   risk_pct=2.0, stop_pct=0.70, drag_pct=0.1975)


def test_dynamic_leverage_is_risk_over_worst_case():
    assert abs(DL.leverage_for(0) - 2.0 / 0.8975) < 1e-12        # 2.2284x at the live 0.70 stop
    o = DL.size(OPEN, equity=888, price=0.18291, mode="dynamic_leverage")
    assert o[0].qty == 10818                                      # floor(888 x 2.2284 / 0.18291)
    c = DL.last_calc
    assert c["lev_target"] == DL.leverage_for(0) and not c["capped"]
    # the stop actually risked on this size = 2.0 % of equity before drag rounding to whole coins
    risked = o[0].qty * 0.18291 * (0.70 + 0.1975) / 100.0
    assert 17.75 < risked <= 888 * 0.02                           # $17.76 of the $17.76 budget


def test_dynamic_leverage_follows_the_stop():
    s = PositionSizer(max_order=66000, risk_pct=2.0, stop_pct=0.80, drag_pct=0.1975)
    assert abs(s.leverage_for(0) - 2.0 / 0.9975) < 1e-12          # a stop ruling moves leverage with it


def test_dynamic_leverage_shares_the_budget_across_live_legs():
    assert abs(DL.leverage_for(1) - DL.leverage_for(0) / 2) < 1e-12
    assert abs(DL.leverage_for(2) - DL.leverage_for(0) / 3) < 1e-12


def test_dynamic_leverage_compounds_with_equity_and_caps_at_max_order():
    a = DL.size(OPEN, equity=888, price=0.18291, mode="dynamic_leverage")[0].qty
    b = DL.size(OPEN, equity=1776, price=0.18291, mode="dynamic_leverage")[0].qty
    assert b in (2 * a, 2 * a + 1)                                # twice the equity, twice the coins
    big = DL.size(OPEN, equity=10000, price=0.18291, mode="dynamic_leverage")[0].qty
    assert big == 66000 and DL.last_calc["capped"]                # max_order still binds, and says so


def test_dynamic_leverage_refuses_without_a_stop():
    s = PositionSizer(max_order=66000, risk_pct=2.0, stop_pct=None, drag_pct=0.1975)
    with pytest.raises(ValueError):
        s.size(OPEN, equity=888, price=0.18291, mode="dynamic_leverage")


def test_close_is_untouched_by_dynamic_leverage():
    o = DL.size(TradeIntent(action="close", side="Buy", qty=10818), equity=888, price=0.18291,
                mode="dynamic_leverage")
    assert o[0].qty == 10818 and o[0].reduce_only
