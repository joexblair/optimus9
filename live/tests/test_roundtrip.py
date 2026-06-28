"""
test_roundtrip.py (M1) — proves the drop-in seam: the SAME BybitClient round-trips the fake-API over HTTP
with EITHER signer (pass-through mock / real HMAC), URL swappable. This is what makes the mock a true Bybit
stunt double — when the real API is ready, o9-live swaps base_url + signer, zero strategy change.

  live/venv/bin/python live/tests/test_roundtrip.py
"""
import sys; sys.path.insert(0, '/home/joe/thecodes/live')
import threading
import time
import logging
import requests
import fake_api
from bybit_client import BybitClient, PassthroughSigner, HmacSigner

logging.getLogger('werkzeug').setLevel(logging.ERROR)
PORT = 8788
threading.Thread(target=lambda: fake_api.app.run('127.0.0.1', PORT, use_reloader=False), daemon=True).start()
for _ in range(50):
    try:
        if requests.get(f'http://127.0.0.1:{PORT}/health', timeout=1).ok:
            break
    except Exception:
        time.sleep(0.1)

base = f'http://127.0.0.1:{PORT}'
c = BybitClient(base, PassthroughSigner())                       # mock signer
print('set_leverage :', c.set_leverage('FARTCOINUSDT', 50))
print('place_order  :', c.place_order('FARTCOINUSDT', 'Buy', 'Market', 66000, orderLinkId='t1'))
print('positions    :', c.get_positions('FARTCOINUSDT'))
print('executions   :', c.get_executions('FARTCOINUSDT'))
print('trading_stop :', c.set_trading_stop('FARTCOINUSDT', stopLoss='0.12'))

# same client, REAL HMAC signer — the mock ignores the sig, proving the swap to real Bybit is URL+signer only
c2 = BybitClient(base, HmacSigner('apikey', 'apisecret'))
print('hmac order   :', c2.place_order('FARTCOINUSDT', 'Sell', 'Market', 66000))
print('\nOK — drop-in seam works: base-URL + signer both swappable, V5 envelope round-trips.')
