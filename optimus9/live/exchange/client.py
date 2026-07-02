"""BybitV5Client — thin `requests` wrapper (SRP: transport + auth headers + envelope parse).

The ONE seam between fake-API and real Bybit: `base_url` (ctor) and `signer` (strategy). Nothing
above this class knows which exchange it's talking to. Not pybit — we build the signed request
ourselves so the auth path is identical to prod. `recv_window` and `base_url` are config-sourced.
The signed string MUST equal the sent string, so POST bodies are serialized once and sent raw.
"""
from __future__ import annotations

import json
import time
from urllib.parse import urlencode

import requests

from .signer import Signer


class BybitError(Exception):
    """Non-zero retCode from the (fake or real) exchange. Carries the code for callers to branch."""

    def __init__(self, ret_code: int, ret_msg: str, path: str):
        super().__init__(f"[{ret_code}] {ret_msg} ({path})")
        self.ret_code = ret_code
        self.ret_msg = ret_msg


class BybitV5Client:
    def __init__(
        self,
        base_url: str,
        signer: Signer,
        recv_window: int = 5000,
        timeout: float = 10.0,
        session: requests.Session | None = None,
        clock=None,
    ):
        self._base = base_url.rstrip("/")
        self._signer = signer
        self._recv = int(recv_window)
        self._timeout = timeout
        self._session = session or requests.Session()
        self._now_ms = clock or (lambda: int(time.time() * 1000))  # injectable for tests

    def get(self, path: str, params: dict | None = None) -> dict:
        # sorted for a deterministic query string; the signed string == the sent string
        query = urlencode(sorted((params or {}).items()))
        ts = self._now_ms()
        headers = self._signer.auth_headers(ts, self._recv, query)
        url = f"{self._base}{path}" + (f"?{query}" if query else "")
        resp = self._session.get(url, headers=headers, timeout=self._timeout)
        return self._envelope(resp, path)

    def post(self, path: str, body: dict | None = None) -> dict:
        raw = json.dumps(body or {}, separators=(",", ":"))  # serialize ONCE; sign + send the same bytes
        ts = self._now_ms()
        headers = self._signer.auth_headers(ts, self._recv, raw)
        headers["Content-Type"] = "application/json"
        resp = self._session.post(f"{self._base}{path}", data=raw, headers=headers, timeout=self._timeout)
        return self._envelope(resp, path)

    def _envelope(self, resp: requests.Response, path: str) -> dict:
        """Parse the Bybit universal envelope {retCode, retMsg, result, ...}; raise on non-zero."""
        resp.raise_for_status()
        data = resp.json()
        if data.get("retCode", 0) != 0:
            raise BybitError(data.get("retCode"), data.get("retMsg", ""), path)
        return data.get("result", {})
