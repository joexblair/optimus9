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

    def __init__(self) -> None:
        self._log = get_logger(self.__class__.__name__)

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
                await asyncio.sleep(delay)
                delay = min(delay * 2, self._MAX_RECONNECT_DELAY)

    async def _connect(self, topic: str, on_message: Callable) -> None:
        async with websockets.connect(self._WS_URL, ping_interval=None) as ws:
            self._log.info(f'Connected → subscribing to {topic}')
            await ws.send(json.dumps({'op': 'subscribe', 'args': [topic]}))
            ping_task = asyncio.create_task(self._heartbeat(ws))
            try:
                async for raw in ws:
                    msg = json.loads(raw)
                    if msg.get('op') == 'ping':
                        await ws.send(json.dumps({'op': 'pong', 'req_id': msg.get('req_id', '')}))
                    elif 'topic' in msg:
                        on_message(msg)
            finally:
                ping_task.cancel()

    async def _heartbeat(self, ws) -> None:
        while True:
            await asyncio.sleep(self._PING_INTERVAL_S)
            await ws.send(json.dumps({'op': 'ping'}))
