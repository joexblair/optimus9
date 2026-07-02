"""PositionSizer — launch modes (smallest/fixed/dynamic5x) + split, with FARTCOIN instrument limits."""
import sys

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
