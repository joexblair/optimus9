"""OrderBookWalker fill-model tests — VWAP fill, adverse slippage, taker fee, thin-book truth."""
import sys

sys.path.insert(0, '/home/joe/thecodes')
from services.fakeapi.fill import OrderBookWalker

BOOK = {
    'bids': [['0.1380', '40000'], ['0.1379', '80000'], ['0.1378', '120000']],
    'asks': [['0.1382', '40000'], ['0.1383', '90000'], ['0.1384', '150000']],
}


def test_buy_vwap_and_fee():
    f = OrderBookWalker(taker_bps=5.5).walk(BOOK, 'Buy', 66000)
    assert abs(f.avg_px - (40000 * 0.1382 + 26000 * 0.1383) / 66000) < 1e-7  # avg_px rounded to 8dp
    assert not f.exhausted
    assert abs(f.fee - f.avg_px * f.filled_qty * 5.5 / 10000) < 1e-6


def test_slippage_is_adverse_both_sides():
    w = OrderBookWalker()
    assert w.walk(BOOK, 'Buy', 66000).slip_bps > 0   # buy fills above mid
    assert w.walk(BOOK, 'Sell', 66000).slip_bps > 0  # sell fills below mid — still a cost


def test_tiny_order_pays_half_spread():
    # best-ask 0.1382 vs mid 0.1381 → ~7.24 bps
    assert abs(OrderBookWalker().walk(BOOK, 'Buy', 1).slip_bps - 7.24) < 0.2


def test_thin_book_exhausts():
    f = OrderBookWalker().walk(BOOK, 'Buy', 300000)  # asks total 280k
    assert f.exhausted and abs(f.filled_qty - 280000) < 1e-6


def test_empty_book_returns_none():
    assert OrderBookWalker().walk({'bids': [], 'asks': []}, 'Buy', 100) is None
