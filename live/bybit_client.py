"""
bybit_client.py (Joe 0628) — thin Bybit V5 client (the o9-live trade machine's exchange adapter). Two seams
so the SAME client is a drop-in for the real exchange OR the fake-API:
  • base_url   = constructor arg          (point at the mock now, real Bybit later)
  • signing    = a Signer strategy        (real HMAC live / pass-through for the mock)
NOT pybit (it computes its own URL + hardcodes signing — fights the mock).

SRP: Signer = sign one request · BybitClient = transport + envelope (one _request; thin endpoint methods,
each just builds params). The strategy/adapter that USES this never sees HTTP or signing.
"""
import time
import hmac
import hashlib
import json
import requests


class Signer:
    """Strategy: turn (timestamp, payload) → auth headers. Base = no-op (overridden)."""
    def headers(self, ts, payload):
        return {}


class HmacSigner(Signer):
    """Real Bybit V5 auth: HMAC-SHA256 over `ts + apiKey + recvWindow + payload` (raw query/body)."""
    def __init__(self, api_key, api_secret, recv_window=5000):
        self._key = api_key
        self._secret = api_secret.encode()
        self._rw = recv_window

    def headers(self, ts, payload):
        pre = f"{ts}{self._key}{self._rw}{payload}"
        sign = hmac.new(self._secret, pre.encode(), hashlib.sha256).hexdigest()
        return {'X-BAPI-API-KEY': self._key, 'X-BAPI-TIMESTAMP': str(ts), 'X-BAPI-RECV-WINDOW': str(self._rw),
                'X-BAPI-SIGN': sign, 'X-BAPI-SIGN-TYPE': '2'}


class PassthroughSigner(Signer):
    """Mock auth: well-formed headers, no real signature (the fake-API stubs the key→account lookup)."""
    def __init__(self, api_key='mock'):
        self._key = api_key

    def headers(self, ts, payload):
        return {'X-BAPI-API-KEY': self._key, 'X-BAPI-TIMESTAMP': str(ts), 'X-BAPI-RECV-WINDOW': '5000'}


class BybitError(Exception):
    def __init__(self, code, msg):
        super().__init__(f'[{code}] {msg}')
        self.code = code


class BybitClient:
    """The transport: sign → send → unwrap the V5 envelope → raise on retCode != 0. Endpoint methods are thin."""
    def __init__(self, base_url, signer, category='linear', session=None):
        self._base = base_url.rstrip('/')
        self._signer = signer
        self._cat = category
        self._s = session or requests.Session()

    def _request(self, method, path, params):
        ts = int(time.time() * 1000)
        if method == 'GET':
            query = '&'.join(f'{k}={v}' for k, v in params.items())
            url = f'{self._base}{path}' + (f'?{query}' if query else '')
            r = self._s.get(url, headers=self._signer.headers(ts, query), timeout=10)
        else:
            body = json.dumps(params, separators=(',', ':'))
            headers = {'Content-Type': 'application/json', **self._signer.headers(ts, body)}
            r = self._s.post(f'{self._base}{path}', data=body, headers=headers, timeout=10)
        env = r.json()
        if env.get('retCode') != 0:
            raise BybitError(env.get('retCode'), env.get('retMsg'))
        return env['result']

    # ── endpoint methods (thin — one job: build params, call _request) ──────────────────────────────
    def place_order(self, symbol, side, order_type, qty, **kw):
        return self._request('POST', '/v5/order/create', {
            'category': self._cat, 'symbol': symbol, 'side': side, 'orderType': order_type, 'qty': str(qty), **kw})

    def set_leverage(self, symbol, leverage):
        return self._request('POST', '/v5/position/set-leverage', {
            'category': self._cat, 'symbol': symbol, 'buyLeverage': str(leverage), 'sellLeverage': str(leverage)})

    def get_positions(self, symbol=None):
        p = {'category': self._cat}
        p['symbol' if symbol else 'settleCoin'] = symbol or 'USDT'
        return self._request('GET', '/v5/position/list', p)['list']

    def get_executions(self, symbol, **kw):
        return self._request('GET', '/v5/execution/list', {'category': self._cat, 'symbol': symbol, **kw})['list']

    def set_trading_stop(self, symbol, **kw):
        return self._request('POST', '/v5/position/trading-stop', {'category': self._cat, 'symbol': symbol, **kw})
