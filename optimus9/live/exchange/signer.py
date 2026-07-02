"""Request signing — the auth seam (SRP: sign only, no transport).

Bybit v5 recipe: sign_str = timestamp + api_key + recv_window + payload, where payload is the
raw query string (GET) or the exact JSON body (POST). signature = hex(HMAC_SHA256(secret, sign_str)).
The SAME HmacSigner runs on the fake path (with a designated test key the fake-API's AuthEmulator
knows) so auth/clock bugs surface in the forward-test, not in prod. Keys are ctor args — the app
loads them from env/secret store, never hard-coded here.
"""
from __future__ import annotations

import hashlib
import hmac
from abc import ABC, abstractmethod


class Signer(ABC):
    """Produce the Bybit v5 auth headers for one request."""

    @abstractmethod
    def auth_headers(self, timestamp_ms: int, recv_window: int, payload: str) -> dict:
        """`payload` = the raw query string (GET) or exact JSON body (POST) that is ALSO sent."""
        ...


class HmacSigner(Signer):
    """Real Bybit v5 HMAC-SHA256 signing (primary — used on both the fake and real paths)."""

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("HmacSigner needs a non-empty api_key and api_secret")
        self._key = api_key
        self._secret = api_secret.encode()

    def auth_headers(self, timestamp_ms: int, recv_window: int, payload: str) -> dict:
        sign_str = f"{timestamp_ms}{self._key}{recv_window}{payload}"
        signature = hmac.new(self._secret, sign_str.encode(), hashlib.sha256).hexdigest()
        return {
            "X-BAPI-API-KEY": self._key,
            "X-BAPI-SIGN": signature,
            "X-BAPI-SIGN-TYPE": "2",
            "X-BAPI-TIMESTAMP": str(timestamp_ms),
            "X-BAPI-RECV-WINDOW": str(recv_window),
        }


class PassThroughSigner(Signer):
    """Debug bypass ONLY — emits a marker signature the fake-API can wave through. Never for prod;
    it doesn't exercise the HMAC/clock path, so default to HmacSigner even against the fake-API."""

    def __init__(self, api_key: str = "o9-passthrough"):
        self._key = api_key

    def auth_headers(self, timestamp_ms: int, recv_window: int, payload: str) -> dict:
        return {
            "X-BAPI-API-KEY": self._key,
            "X-BAPI-SIGN": "passthrough",
            "X-BAPI-SIGN-TYPE": "2",
            "X-BAPI-TIMESTAMP": str(timestamp_ms),
            "X-BAPI-RECV-WINDOW": str(recv_window),
        }
