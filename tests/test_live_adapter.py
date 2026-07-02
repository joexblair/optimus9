"""BybitAdapter — Order/intent → correct Bybit v5 request shapes (recording client, no network)."""
import sys
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.live.exchange import BybitAdapter
from optimus9.live.sizing import Order


class RecClient:
    def __init__(self): self.calls = []
    def post(self, path, body): self.calls.append(('POST', path, body)); return {'orderId': 'fx-abc'}
    def get(self, path, params): self.calls.append(('GET', path, params)); return {'list': [{'x': 1}]}


def test_place_market_order():
    c = RecClient(); a = BybitAdapter(c, 'FARTCOINUSDT')
    oid = a.place(Order('Sell', 66000.0, order_link_id='o9-1'))
    _, path, b = c.calls[0]
    assert path == '/v5/order/create'
    assert b['symbol'] == 'FARTCOINUSDT' and b['side'] == 'Sell' and b['qty'] == '66000'
    assert 'reduceOnly' not in b and b['orderLinkId'] == 'o9-1'
    assert oid == 'fx-abc'


def test_reduce_only_flag():
    c = RecClient(); BybitAdapter(c, 'FARTCOINUSDT').place(Order('Buy', 111000.0, reduce_only=True))
    assert c.calls[0][2]['reduceOnly'] is True


def test_backstop_triggers_on_mark():
    c = RecClient(); BybitAdapter(c, 'FARTCOINUSDT').set_backstop(0.139, trigger_by='MarkPrice')
    _, path, b = c.calls[0]
    assert path == '/v5/position/trading-stop' and b['stopLoss'] == '0.139' and b['slTriggerBy'] == 'MarkPrice'


def test_set_leverage_and_reads():
    c = RecClient(); a = BybitAdapter(c, 'FARTCOINUSDT')
    a.set_leverage(5)
    assert c.calls[0][2]['buyLeverage'] == '5' and c.calls[0][2]['sellLeverage'] == '5'
    assert a.positions() == [{'x': 1}] and a.executions() == [{'x': 1}]
