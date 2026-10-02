"""
BybitWebSocketClient — see class docstring for purpose, Pine alignment, and design notes.
"""


"""
managers.py — PK Optimizer
All process classes. One responsibility per class.
Every class calls get_logger(self.__class__.__name__).

Terminology:
  OOB  = out of boundary (indicator has crossed high/low threshold)
  IB   = in boundary (indicator is within thresholds)
  OS/OB remain only in RSI/K oscillator context where they are technically correct.
"""

import asyncio
import itertools
import json
import math
import multiprocessing
import signal
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

import mysql.connector
import numpy as np
import pandas as pd
import requests
import websockets

from logger import get_logger


class BybitWebSocketClient:
    """Bybit V5 public WebSocket. Handles subscription, heartbeat, auto-reconnect."""

    _WS_URL              = 'wss://stream.bybit.com/v5/public/linear'
    _PING_INTERVAL_S     = 20
    _MAX_RECONNECT_DELAY = 60

    def __init__(self, url: Optional[str] = None, liveness=None, stall_s: Optional[float] = None,
                 on_connect: Optional[Callable] = None, restart_gate=None) -> None:
        # url: None = _WS_URL. liveness: an optional ws_liveness.WsLiveness that RECORDS what this
        # connection receives (Joe 1002 outage item #1).
        # stall_s: AUTO-RESTART. Joe 1002: "tick collect should auto restart on any tick freeze that
        #   dwells more than 60 seconds". When no TOPIC message (trades / book) has arrived for stall_s,
        #   the socket is aborted and reconnected at once. Ping replies do not count: on 1002 22:06 the
        #   socket stayed open, sent pings and received nothing for 16+ min without raising. None = off.
        # restart_gate: a shared RestartGate - parallel sockets never restart within its offset of each
        #   other (Joe 1002: "an offset is needed for the second, in case the stream is still live").
        # on_connect(reconnect: bool): called after each subscribe; reconnect is False the first time.
        #   The tick collector runs its REST gap-fill there (Joe 1002: gap-fill after reconnect).
        self._log = get_logger(self.__class__.__name__)
        self._url = url or self._WS_URL
        self._live = liveness
        self._stall_s = None if stall_s is None else float(stall_s)
        self._on_connect = on_connect
        self._gate = restart_gate
        self._n_connects = 0

    def stream(self, topic: str, on_message: Callable) -> None:
        asyncio.run(self._stream_loop(topic, on_message))

    async def _stream_loop(self, topic: str, on_message: Callable) -> None:
        delay = 1
        while True:
            try:
                await self._connect(topic, on_message)
                delay = 1
            except Exception as exc:
                self._log.error(f'WebSocket error: {exc} — reconnecting in {delay}s')
                if self._live is not None:
                    self._live.error(f'{exc} — reconnecting in {delay}s')
                await asyncio.sleep(delay)
                delay = min(delay * 2, self._MAX_RECONNECT_DELAY)

    async def _connect(self, topic: str, on_message: Callable) -> None:
        async with websockets.connect(self._url, ping_interval=None) as ws:
            self._log.info(f'Connected → subscribing to {topic}')
            if self._live is not None:
                self._live.connected(self._url)
            await ws.send(json.dumps({'op': 'subscribe', 'args': [topic]}))
            self._n_connects += 1
            if self._on_connect is not None:
                try:
                    self._on_connect(self._n_connects > 1)
                except Exception as exc:
                    self._log.error(f'on_connect failed: {exc}')
            ping_task = asyncio.create_task(self._heartbeat(ws))
            stall = {'last': time.monotonic(), 'hit': False}
            dog = asyncio.create_task(self._watchdog(ws, stall, topic)) if self._stall_s else None
            try:
                async for raw in ws:
                    msg = json.loads(raw)
                    if self._live is not None:
                        self._live.message(msg)
                    if msg.get('op') == 'ping':
                        await ws.send(json.dumps({'op': 'pong', 'req_id': msg.get('req_id', '')}))
                    elif 'topic' in msg:
                        stall['last'] = time.monotonic()
                        on_message(msg)
            except websockets.ConnectionClosed:
                if not stall['hit']:
                    raise                       # a real error: the existing reconnect path and its wait
            finally:
                ping_task.cancel()
                if dog is not None:
                    dog.cancel()
            # a stall restart returns cleanly, so _stream_loop reconnects at once (delay reset to 1 s)

    async def _watchdog(self, ws, stall, topic) -> None:
        """Abort the socket after `_stall_s` with no topic message. The gate staggers parallel sockets."""
        while True:
            await asyncio.sleep(1.0)
            idle = time.monotonic() - stall['last']
            if idle <= self._stall_s:
                continue
            if self._gate is not None and not self._gate.claim():
                continue                        # another socket restarted within the offset: wait
            stall['hit'] = True
            self._log.error(f'STALL: no {topic} message for {idle:.0f}s on {self._url} - restarting the socket')
            if self._live is not None:
                self._live.stalled(idle)
            ws.transport.abort()
            return

    async def _heartbeat(self, ws) -> None:
        while True:
            await asyncio.sleep(self._PING_INTERVAL_S)
            await ws.send(json.dumps({'op': 'ping'}))
            if self._live is not None:
                self._live.ping_sent()


class RestartGate:
    """Parallel sockets share one: a socket may auto-restart only if no other did within `offset_s`.

    Joe 1002: *"there's 2 websockets in parallel so an offset is needed for the second, in case the
    stream is still live and a signal is missed during reset"*. Offset 10 s - Joe: *"I'm sure 10s is
    enough, but your call"*; the measured in-process reset (connect + subscribe) is ~0.4 s.
    """

    def __init__(self, offset_s: float = 10.0) -> None:
        import threading
        self.offset_s = float(offset_s)
        self._lock = threading.Lock()
        self._last = None

    def claim(self) -> bool:
        with self._lock:
            now = time.monotonic()
            if self._last is not None and now - self._last < self.offset_s:
                return False
            self._last = now
            return True
