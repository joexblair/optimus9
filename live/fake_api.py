"""
fake_api.py (Joe 0628) — the fake Bybit V5 exchange (o9-live forward-test). Fed by REAL mainnet public data
(M2+), it gives real prices + modeled fills + zero risk — the only combination the real test/demo APIs can't
(demo prints test-env prices). M1 = the CONTRACT SKELETON: mirror the V5 envelope + core endpoints so
BybitClient is a true drop-in. State is a minimal in-memory stub; the order-book-walk fill model + fees + the
pyramiding position store come in M3 (a FillModel class, kept out of the routes — SRP).

Flask (the mock needs no async/validation). SRP: _env = the V5 envelope · _STORE = state · each route = one
endpoint. Run: python fake_api.py  (default 127.0.0.1:8788).
"""
import time
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

# in-memory stub (M1). M3 replaces with the FillModel + the fx_* tables.
_STORE = {'orders': {}, 'positions': {}}


def _env(result=None, code=0, msg='OK'):
    """The universal Bybit V5 envelope. retCode 0 = success; all list reads go in result.list[]."""
    return jsonify({'retCode': code, 'retMsg': msg, 'result': result if result is not None else {},
                    'retExtInfo': {}, 'time': int(time.time() * 1000)})


@app.post('/v5/order/create')
def order_create():
    b = request.get_json(force=True)
    oid = uuid.uuid4().hex
    _STORE['orders'][oid] = {**b, 'orderId': oid, 'orderStatus': 'New', 'createdMs': int(time.time() * 1000)}
    return _env({'orderId': oid, 'orderLinkId': b.get('orderLinkId', '')})   # V5: create returns only the IDs


@app.post('/v5/position/set-leverage')
def set_leverage():
    return _env({})


@app.get('/v5/position/list')
def position_list():
    return _env({'category': 'linear', 'list': list(_STORE['positions'].values()), 'nextPageCursor': ''})


@app.get('/v5/execution/list')
def execution_list():
    return _env({'category': 'linear', 'list': [], 'nextPageCursor': ''})   # fills surface here (M3)


@app.post('/v5/position/trading-stop')
def trading_stop():
    return _env({})


@app.get('/health')
def health():
    return _env({'status': 'ok', 'orders': len(_STORE['orders'])})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8788)
