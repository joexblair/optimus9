"""AuthEmulator — verify the Bybit v5 HMAC + recv_window/clock rule (SRP: auth only).

Reimplements the recipe INDEPENDENTLY of o9-live's Signer on purpose: if our signer ever drifts
from Bybit's spec, the fake-API rejects it here (in the forward-test) instead of Bybit rejecting it
in prod. Credentials are injected (from env), never hard-coded.
"""
from __future__ import annotations

import hashlib
import hmac
import time

from .errors import FakeApiError, API_KEY_INVALID, SIGN_ERROR, TS_OUT_OF_WINDOW


class AuthEmulator:
    def __init__(self, creds: dict[str, str], clock=None):
        """creds: {api_key: api_secret}. clock: injectable ()->ms for tests."""
        self._creds = creds
        self._now_ms = clock or (lambda: int(time.time() * 1000))

    def verify(self, headers, payload: str) -> str:
        """Return the account (api_key) on success; raise FakeApiError on any auth failure.
        `payload` MUST be the exact query string (GET) or raw body (POST) the client signed."""
        key = headers.get("X-BAPI-API-KEY")
        sign = headers.get("X-BAPI-SIGN")
        ts = headers.get("X-BAPI-TIMESTAMP")
        recv = headers.get("X-BAPI-RECV-WINDOW")
        if not (key and sign and ts and recv):
            raise FakeApiError(SIGN_ERROR, "missing auth headers")
        try:
            ts_i, recv_i = int(ts), int(recv)
        except (TypeError, ValueError):
            raise FakeApiError(TS_OUT_OF_WINDOW, "invalid timestamp / recv_window")
        skew = self._now_ms() - ts_i
        if abs(skew) > recv_i:
            raise FakeApiError(TS_OUT_OF_WINDOW, f"request timestamp outside recv_window ({skew}ms)")
        secret = self._creds.get(key)
        if secret is None:
            raise FakeApiError(API_KEY_INVALID, "api key invalid")
        expect = hmac.new(secret.encode(), f"{ts_i}{key}{recv_i}{payload}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expect, sign):
            raise FakeApiError(SIGN_ERROR, "sign error")
        return key
