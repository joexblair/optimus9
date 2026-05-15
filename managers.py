"""
260514_managers_additions.py — code to add to managers.py for the 5s PK gate
                               + p-rev round.

Two pieces, both for managers.py:

  Piece A — IndicatorComputer additions:
            Three new @staticmethod entries on the existing IndicatorComputer
            class. Insert anywhere inside the class body (suggest immediately
            after the existing `_stoch` method, before the close-brace).

  Piece B — Pk5sGateComputer class:
            New top-level class. Insert immediately AFTER PKDetector and
            BEFORE SwingAnalyzer (around line 770 in the current file).

Documentation conventions per the round spec:
  • Module-level header (above) — what this file delivers and why
  • Class docstrings in three sections: Purpose, Pine alignment, Design notes
  • Method docstrings: purpose + non-obvious params + return shape
  • Inline comments: only "this looks weird but here's why" moments
  • Pine references: `# Pine: <symbol>, bbstr.pine line N` for transposition audits

Round spec: 260514_pk5s_spec.md
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


# ─────────────────────────────────────────────────────────────────────────────
# DatabaseManager
# ─────────────────────────────────────────────────────────────────────────────

class DatabaseManager:
    """Owns the MySQL connection lifecycle and raw query execution."""

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self._cfg  = dict(host=host, user=user, password=password, database=database, port=port)
        self._conn = None
        self._log  = get_logger(self.__class__.__name__)

    def connect(self) -> None:
        self._conn = mysql.connector.connect(**self._cfg, autocommit=True)
        self._log.info('MySQL connected')

    def disconnect(self) -> None:
        if self._conn and self._conn.is_connected():
            self._conn.close()
            self._log.info('MySQL disconnected')

    def execute(self, sql: str, params: tuple = (), *, fetch: bool = False):
        cursor = self._conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        last_id = cursor.lastrowid
        cursor.close()
        return last_id

    def executemany(self, sql: str, rows: list) -> int:
        """Batch insert — returns first auto-increment ID of the batch."""
        if not rows:
            return 0
        cursor = self._conn.cursor()
        cursor.executemany(sql, rows)
        first_id = cursor.lastrowid
        cursor.close()
        return first_id


# ─────────────────────────────────────────────────────────────────────────────
# BinanceClient
# ─────────────────────────────────────────────────────────────────────────────

class BinanceClient:
    """
    Fetches klines from Binance Spot REST API.
    5s interval supported on spot (FARTCOINUSDT is futures-only — kept for other pairs).
    """

    _BASE        = 'https://api.binance.com'
    _KLINES_PATH = '/api/v3/klines'
    _BATCH_LIMIT = 1500
    _RATE_DELAY  = 0.12

    _VALID_INTERVALS = frozenset({
        '1s', '5s', '15s', '30s',
        '1m', '3m', '5m', '15m', '30m',
        '1h', '2h', '4h', '6h', '8h', '12h',
        '1d', '3d', '1w', '1M',
    })

    def __init__(self) -> None:
        self._session = requests.Session()
        self._log     = get_logger(self.__class__.__name__)

    def fetch_klines(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        if interval not in self._VALID_INTERVALS:
            raise ValueError(f'Interval {interval!r} not supported')

        all_candles = []
        cursor = start_ms
        while cursor < end_ms:
            batch = self._fetch_batch(symbol, interval, cursor, end_ms)
            if not batch:
                break
            all_candles.extend(batch)
            last_ts = batch[-1]['timestamp']
            if last_ts >= end_ms or len(batch) < self._BATCH_LIMIT:
                break
            cursor = last_ts + 1
            time.sleep(self._RATE_DELAY)

        self._log.info(f'Fetched {len(all_candles)} candles ({symbol} {interval})')
        return all_candles

    def _fetch_batch(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        params = {'symbol': symbol, 'interval': interval,
                  'startTime': start_ms, 'endTime': end_ms, 'limit': self._BATCH_LIMIT}
        resp = self._session.get(self._BASE + self._KLINES_PATH, params=params, timeout=10)
        if not resp.ok:
            self._log.error(f'Binance {resp.status_code}: {resp.text}')
            resp.raise_for_status()
        return [{'timestamp': int(r[0]), 'open': float(r[1]), 'high': float(r[2]),
                 'low': float(r[3]), 'close': float(r[4]), 'volume': float(r[5])}
                for r in resp.json()]


# ─────────────────────────────────────────────────────────────────────────────
# BinanceBackfiller
# ─────────────────────────────────────────────────────────────────────────────

class BinanceBackfiller:
    """Fills kline_collection gaps from Binance Spot REST. Kept for non-futures pairs."""

    _LOOKBACK_WEEKS   = 5
    _DEFAULT_INTERVAL = '5s'

    def __init__(self, db: DatabaseManager, client: BinanceClient) -> None:
        self._db     = db
        self._client = client
        self._log    = get_logger(self.__class__.__name__)

    def backfill(self, tp_pk: int, symbol: str, interval: str = _DEFAULT_INTERVAL) -> int:
        start_ms = self._gap_start(tp_pk)
        end_ms   = int(datetime.now(timezone.utc).timestamp() * 1000)
        if end_ms - start_ms < 5_000:
            self._log.info('kline_collection is current')
            return 0
        self._log.info(f'Backfilling {symbol} {interval} from {_ms_to_iso(start_ms)}')
        candles = self._client.fetch_klines(symbol, interval, start_ms, end_ms)
        if not candles:
            self._log.error('Binance returned no candles')
            return 0
        self._db.executemany(
            '''INSERT IGNORE INTO kline_collection
                   (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
               VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            [(tp_pk, c['timestamp'], c['open'], c['high'], c['low'], c['close'], c['volume'])
             for c in candles],
        )
        self._log.info(f'Stored {len(candles)} candles')
        return len(candles)

    def run_loop(self, tp_pk: int, symbol: str, interval: str = _DEFAULT_INTERVAL) -> None:
        self.backfill(tp_pk, symbol, interval)

    def _gap_start(self, tp_pk: int) -> int:
        rows = self._db.execute(
            'SELECT MAX(kc_timestamp) AS latest FROM kline_collection WHERE kc_tp_pk = %s',
            (tp_pk,), fetch=True,
        )
        latest = rows[0]['latest'] if rows and rows[0]['latest'] is not None else None
        if latest is not None:
            return int(latest) + 1
        return int((datetime.now(timezone.utc) - timedelta(weeks=self._LOOKBACK_WEEKS)).timestamp() * 1000)


# ─────────────────────────────────────────────────────────────────────────────
# BybitKlineClient
# ─────────────────────────────────────────────────────────────────────────────

class BybitKlineClient:
    """Fetches OHLCV klines from Bybit Futures REST API (v5) for synthetic backfill."""

    _BASE        = 'https://api.bybit.com'
    _PATH        = '/v5/market/kline'
    _BATCH_LIMIT = 200
    _RATE_DELAY  = 0.12

    def __init__(self) -> None:
        self._session = requests.Session()
        self._log     = get_logger(self.__class__.__name__)

    def fetch_klines(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        all_candles: list = []
        cursor_end = end_ms
        while cursor_end > start_ms:
            batch = self._fetch_batch(symbol, interval, start_ms, cursor_end)
            if not batch:
                break
            all_candles.extend(batch)
            earliest = batch[-1]['timestamp']
            self._log.info(
                f'  fetched {len(batch)} bars  '
                f'[{_ms_to_iso(earliest)}  →  {_ms_to_iso(batch[0]["timestamp"])}]'
                f'  total: {len(all_candles)}'
            )
            if earliest <= start_ms or len(batch) < self._BATCH_LIMIT:
                break
            cursor_end = earliest - 1
            time.sleep(self._RATE_DELAY)

        all_candles.sort(key=lambda x: x['timestamp'])
        self._log.info(f'Fetched {len(all_candles)} candles ({symbol} {interval}m)')
        return all_candles

    def _fetch_batch(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        params = {'category': 'linear', 'symbol': symbol, 'interval': interval,
                  'start': start_ms, 'end': end_ms, 'limit': self._BATCH_LIMIT}
        resp = self._session.get(self._BASE + self._PATH, params=params, timeout=10)
        if not resp.ok:
            self._log.error(f'Bybit {resp.status_code}: {resp.text}')
            resp.raise_for_status()
        data = resp.json()
        if data.get('retCode') != 0:
            self._log.error(f'Bybit API error: {data}')
            return []
        return [{'timestamp': int(r[0]), 'open': float(r[1]), 'high': float(r[2]),
                 'low': float(r[3]), 'close': float(r[4]), 'volume': float(r[5])}
                for r in data['result']['list']]


# ─────────────────────────────────────────────────────────────────────────────
# SyntheticBarBuilder
# ─────────────────────────────────────────────────────────────────────────────

class SyntheticBarBuilder:
    """
    Splits 1m OHLCV bars into 12 × 5s bars using linear price interpolation.
    Assigns the 1m H to the bar where the path peaks, L to where it troughs.
    Bullish (C >= O): low in first bar, high in last bar.
    Bearish (C < O):  high in first bar, low in last bar.
    """

    _N       = 12
    _STEP_MS = 5_000

    @staticmethod
    def split(bar: dict) -> list:
        T = int(bar['timestamp'])
        O, H, L, C = float(bar['open']), float(bar['high']), float(bar['low']), float(bar['close'])
        V      = float(bar['volume'])
        n      = SyntheticBarBuilder._N
        unit_v = round(V / n, 8)
        prices = [O + i * (C - O) / n for i in range(n + 1)]
        h_bar  = n - 1 if C >= O else 0
        l_bar  = 0     if C >= O else n - 1

        bars = []
        for i in range(n):
            o_i = prices[i]
            c_i = prices[i + 1]
            h_i = max(o_i, c_i)
            l_i = min(o_i, c_i)
            if i == h_bar:
                h_i = max(h_i, H)
            if i == l_bar:
                l_i = min(l_i, L)
            bars.append(dict(
                timestamp = T + i * SyntheticBarBuilder._STEP_MS,
                open=round(o_i, 8), high=round(h_i, 8),
                low=round(l_i, 8),  close=round(c_i, 8), volume=unit_v,
            ))
        return bars

    @staticmethod
    def split_batch(bars_1m: list) -> list:
        out = []
        for bar in bars_1m:
            out.extend(SyntheticBarBuilder.split(bar))
        return out


# ─────────────────────────────────────────────────────────────────────────────
# SyntheticBackfiller
# ─────────────────────────────────────────────────────────────────────────────

class SyntheticBackfiller:
    """
    Fetches Bybit 1m futures history, splits to 12 × 5s, writes to kline_collection.
    Provides synthetic 5s bar history before live tick collection has accumulated.
    Live tick-derived bars overwrite synthetic ones (ON DUPLICATE KEY UPDATE in BarBuilder).
    """

    _LOOKBACK_WEEKS = 5

    def __init__(self, db: DatabaseManager, client: BybitKlineClient) -> None:
        self._db     = db
        self._client = client
        self._log    = get_logger(self.__class__.__name__)

    def backfill(self, tp_pk: int, symbol: str) -> int:
        start_ms  = self._gap_start(tp_pk)
        end_ms    = int(datetime.now(timezone.utc).timestamp() * 1000)
        if end_ms - start_ms < 30_000:
            self._log.info('kline_collection is current — no backfill needed')
            return 0

        span_days = (end_ms - start_ms) / 86_400_000
        self._log.info(
            f'Backfilling {symbol} synthetic 5s bars'
            f' — {span_days:.1f} days from {_ms_to_iso(start_ms)}'
        )
        bars_1m = self._client.fetch_klines(symbol, '1', start_ms, end_ms)
        if not bars_1m:
            self._log.error('No 1m bars returned from Bybit')
            return 0

        self._log.info(
            f'Splitting {len(bars_1m)} × 1m bars into {SyntheticBarBuilder._N} × 5s bars...'
        )
        bars_5s = SyntheticBarBuilder.split_batch(bars_1m)

        self._log.info(f'Writing {len(bars_5s)} bars to kline_collection...')
        self._persist(tp_pk, bars_5s)

        self._log.info(
            f'Done — {len(bars_5s)} synthetic 5s bars stored'
            f'  [{_ms_to_iso(bars_5s[0]["timestamp"])}  →  {_ms_to_iso(bars_5s[-1]["timestamp"])}]'
        )
        return len(bars_5s)

    def _gap_start(self, tp_pk: int) -> int:
        rows = self._db.execute(
            'SELECT MAX(kc_timestamp) AS latest FROM kline_collection WHERE kc_tp_pk = %s',
            (tp_pk,), fetch=True,
        )
        latest = rows[0]['latest'] if rows and rows[0]['latest'] is not None else None
        if latest is not None:
            return int(latest) + 1
        return int((datetime.now(timezone.utc) - timedelta(weeks=self._LOOKBACK_WEEKS)).timestamp() * 1000)

    def _persist(self, tp_pk: int, bars: list) -> None:
        self._db.executemany(
            '''INSERT IGNORE INTO kline_collection
                   (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
               VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            [(tp_pk, b['timestamp'], b['open'], b['high'], b['low'], b['close'], b['volume'])
             for b in bars],
        )


# ─────────────────────────────────────────────────────────────────────────────
# BybitWebSocketClient
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# TickCollector
# ─────────────────────────────────────────────────────────────────────────────

class TickCollector:
    """
    Subscribes to Bybit public trade stream.
    Commits each WebSocket message to the ticks table immediately — no buffering.
    Prunes ticks older than 7 days hourly.
    """

    _TOPIC_PREFIX    = 'publicTrade'
    _PRUNE_KEEP_DAYS = 7

    def __init__(self, db: DatabaseManager) -> None:
        self._db         = db
        self._ws         = BybitWebSocketClient()
        self._log        = get_logger(self.__class__.__name__)
        self._last_prune = time.time()

    def run(self, tp_pk: int, symbol: str) -> None:
        self._log.info(f'Collecting ticks: {symbol}')
        self._ws.stream(
            f'{self._TOPIC_PREFIX}.{symbol}',
            lambda msg: self._on_message(tp_pk, msg),
        )

    def _on_message(self, tp_pk: int, msg: dict) -> None:
        trades = msg.get('data', [])
        if not trades:
            return
        self._db.executemany(
            '''INSERT IGNORE INTO ticks (tk_tp_pk, tk_timestamp, tk_price, tk_volume, tk_side)
               VALUES (%s,%s,%s,%s,%s)''',
            [(tp_pk, int(t['T']), float(t['p']), float(t['v']),
              'buy' if t['S'] == 'Buy' else 'sell')
             for t in trades],
        )
        for t in trades:
            self._log.debug(
                f'{t["s"]:16s}  {"BUY " if t["S"] == "Buy" else "SELL"}'
                f'  p={float(t["p"]):>14.8f}  v={float(t["v"]):>12.4f}'
                f'  {_ms_to_iso(int(t["T"]))}'
            )
        now = time.time()
        if now - self._last_prune >= 3600:
            self._prune(tp_pk)
            self._last_prune = now

    def _prune(self, tp_pk: int) -> None:
        cutoff = int((datetime.now(timezone.utc) - timedelta(days=self._PRUNE_KEEP_DAYS)).timestamp() * 1000)
        self._db.execute(
            'DELETE FROM ticks WHERE tk_tp_pk = %s AND tk_timestamp < %s', (tp_pk, cutoff),
        )
        self._log.info(f'Ticks pruned — keeping last {self._PRUNE_KEEP_DAYS} days')


# ─────────────────────────────────────────────────────────────────────────────
# BarBuilder
# ─────────────────────────────────────────────────────────────────────────────

class BarBuilder:
    """
    Wakes at each 5s wall-clock boundary.
    Builds the bar that ended one interval ago — guarantees TickCollector has committed.
    Tick-derived bars overwrite synthetic ones via ON DUPLICATE KEY UPDATE.
    """

    _BAR_S = 5

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self, tp_pk: int) -> None:
        self._log.info('BarBuilder started')
        while True:
            self._sleep_to_boundary()
            boundary_ms = int(time.time() * 1000)
            bar_end     = boundary_ms - self._BAR_S * 1000
            bar_start   = bar_end     - self._BAR_S * 1000
            self._build(tp_pk, bar_start, bar_end)

    def _sleep_to_boundary(self) -> None:
        now = time.time()
        time.sleep(max(0.0, math.ceil(now / self._BAR_S) * self._BAR_S - now))

    def _build(self, tp_pk: int, start_ms: int, end_ms: int) -> None:
        rows = self._db.execute(
            '''SELECT tk_price, tk_volume FROM ticks
               WHERE tk_tp_pk = %s AND tk_timestamp >= %s AND tk_timestamp < %s
               ORDER BY tk_timestamp ASC''',
            (tp_pk, start_ms, end_ms), fetch=True,
        )
        if not rows:
            self._log.debug(f'No ticks for bar {start_ms}')
            return

        prices  = [float(r['tk_price'])  for r in rows]
        volumes = [float(r['tk_volume']) for r in rows]

        self._db.execute(
            '''INSERT INTO kline_collection
                   (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
               VALUES (%s,%s,%s,%s,%s,%s,%s)
               ON DUPLICATE KEY UPDATE
                   kc_open=VALUES(kc_open), kc_high=VALUES(kc_high),
                   kc_low=VALUES(kc_low),   kc_close=VALUES(kc_close),
                   kc_volume=VALUES(kc_volume)''',
            (tp_pk, start_ms, prices[0], max(prices), min(prices), prices[-1], sum(volumes)),
        )
        self._log.debug(
            f'Bar ts={start_ms}  o={prices[0]}  h={max(prices)}'
            f'  l={min(prices)}  c={prices[-1]}  v={sum(volumes):.4f}'
        )


# ─────────────────────────────────────────────────────────────────────────────
# IndicatorComputer
# ─────────────────────────────────────────────────────────────────────────────

class IndicatorComputer:
    """Pure computation. Replicates Pine Script f_bb, f_k, DEMA. No I/O."""

    @staticmethod
    def resample(df: pd.DataFrame, target_seconds: int) -> pd.DataFrame:
        """Aggregate a 5s OHLCV DataFrame into target_seconds bars."""
        tmp = df.copy()
        tmp['dt'] = pd.to_datetime(tmp['timestamp'], unit='ms', utc=True)
        tmp = tmp.set_index('dt').sort_index()
        agg = tmp.resample(f'{target_seconds}s').agg(
            timestamp=('timestamp', 'first'), open=('open', 'first'),
            high=('high', 'max'), low=('low', 'min'),
            close=('close', 'last'), volume=('volume', 'sum'),
        ).dropna(subset=['open'])
        return agg.reset_index(drop=True)

    @staticmethod
    def align_to_base(values: np.ndarray,
                      source_df: pd.DataFrame,
                      base_df:   pd.DataFrame) -> np.ndarray:
        """
        Forward-fill indicator values from source_df timestamps to base_df timestamps.
        Uses searchsorted for O(n log m) vectorised alignment.
        Mimics Pine Script request.security() — each base bar sees the last completed source bar.
        """
        src_ts  = source_df['timestamp'].to_numpy()
        base_ts = base_df['timestamp'].to_numpy()
        idx     = np.searchsorted(src_ts, base_ts, side='right') - 1
        out     = np.full(len(base_ts), np.nan)
        valid   = idx >= 0
        out[valid] = values[idx[valid]]
        return out

    @staticmethod
    def fold_gates(sides: list) -> np.ndarray:
        """
        Combine N OOB side arrays with OR logic.
          Both non-zero and agree → that direction.
          Both non-zero and oppose → 0 (gate closed).
          One non-zero, one zero → non-zero direction (OR).
          Both zero → 0 (IB, gate closed).
        """
        if not sides:
            return np.zeros(0, dtype=np.int8)
        result = sides[0].copy().astype(np.int8)
        for s in sides[1:]:
            s        = s.astype(np.int8)
            opposing = (result != 0) & (s != 0) & (result != s)
            s_only   = (result == 0) & (s != 0)
            result   = np.where(opposing, np.int8(0),
                       np.where(s_only, s, result)).astype(np.int8)
        return result

    @staticmethod
    def compute_oob_side(cfg: dict, df: pd.DataFrame) -> np.ndarray:
        """
        Compute OOB side array for one indicator config row.
        Returns +1 (HI OOB), -1 (LO OOB), 0 (IB) for each bar.
        Dispatches to f_bb or f_k based on ic_line_type.
        """
        src    = IndicatorComputer.build_source(df, cfg['ic_src'])
        high_b = float(cfg['ic_high_boundary'])
        low_b  = float(cfg['ic_low_boundary'])

        if cfg['ic_line_type'] == 'bb':
            vals = IndicatorComputer.f_bb(src, int(cfg['ic_bb_len']), float(cfg['ic_bb_mult']))
        else:
            vals = IndicatorComputer.f_k(
                src, int(cfg['ic_rsi_len']), int(cfg['ic_stc_len']), int(cfg['ic_k_len'])
            )

        result = np.zeros(len(vals), dtype=np.int8)
        with np.errstate(invalid='ignore'):
            result[vals >= high_b] =  1
            result[vals <= low_b]  = -1
        return result

    @staticmethod
    def build_source(df: pd.DataFrame, src: str) -> np.ndarray:
        o, h, l, c = (df[col].to_numpy(dtype=float) for col in ('open', 'high', 'low', 'close'))
        mapping = {
            'close': c, 'open': o, 'high': h, 'low': l,
            'hl2':   (h + l) / 2,
            'hlc3':  (h + l + c) / 3,
            'ohlc4': (o + h + l + c) / 4,
            'hlcc4': (h + l + c + c) / 4,
        }
        if src not in mapping:
            raise ValueError(f'Unknown source {src!r}')
        return mapping[src]

    @staticmethod
    def f_bb(src: np.ndarray, length: int, mult: float,
             high_b: float = 70.0, low_b: float = 30.0) -> np.ndarray:
        basis = IndicatorComputer._sma(src, length)
        dev   = mult * IndicatorComputer._stdev(src, length)
        span  = (basis + dev) - (basis - dev)
        with np.errstate(invalid='ignore', divide='ignore'):
            pct = np.where(span != 0.0, (src - (basis - dev)) / span, np.nan)
        return (high_b - low_b) * pct + low_b

    @staticmethod
    def f_k(src: np.ndarray, rsi_len: int, stc_len: int, k_len: int) -> np.ndarray:
        return IndicatorComputer._sma(
            IndicatorComputer._stoch(IndicatorComputer._rsi(src, rsi_len), stc_len),
            k_len,
        )

    @staticmethod
    def dema(src: np.ndarray, length: int) -> np.ndarray:
        e1 = IndicatorComputer._ema(src, length)
        return 2.0 * e1 - IndicatorComputer._ema(e1, length)

    @staticmethod
    def _sma(src: np.ndarray, n: int) -> np.ndarray:
        return pd.Series(src).rolling(n, min_periods=n).mean().to_numpy()

    @staticmethod
    def _stdev(src: np.ndarray, n: int) -> np.ndarray:
        return pd.Series(src).rolling(n, min_periods=n).std(ddof=0).to_numpy()

    @staticmethod
    def _ema(src: np.ndarray, n: int) -> np.ndarray:
        alpha = 2.0 / (n + 1)
        out   = np.full_like(src, np.nan, dtype=float)
        valid = np.where(~np.isnan(src))[0]
        if len(valid) < n:
            return out
        seed      = valid[n - 1]
        out[seed] = float(np.nanmean(src[valid[0] : seed + 1]))
        for i in range(seed + 1, len(src)):
            out[i] = alpha * src[i] + (1.0 - alpha) * out[i - 1] if not np.isnan(src[i]) else out[i - 1]
        return out

    @staticmethod
    def _rsi(src: np.ndarray, n: int) -> np.ndarray:
        delta = np.diff(src, prepend=np.nan)
        avg_g = IndicatorComputer._ema(np.where(delta > 0,  delta, 0.0), n)
        avg_l = IndicatorComputer._ema(np.where(delta < 0, -delta, 0.0), n)
        with np.errstate(invalid='ignore', divide='ignore'):
            rs = np.where(avg_l != 0, avg_g / avg_l, np.inf)
        return 100.0 - (100.0 / (1.0 + rs))

    @staticmethod
    def _stoch(src: np.ndarray, n: int) -> np.ndarray:
        s   = pd.Series(src)
        lo  = s.rolling(n, min_periods=n).min()
        hi  = s.rolling(n, min_periods=n).max()
        rng = hi - lo
        out = np.where(rng != 0, 100.0 * (s - lo) / rng, 50.0)
        out = np.where(rng.isna(), np.nan, out)
        return out.astype(float)

# ═══════════════════════════════════════════════════════════════════════════
# PIECE A — IndicatorComputer additions
#
# Three new @staticmethod entries. Adds lookahead (Pine barmerge.lookahead_on)
# equivalents for resampling and BB/K computation. Used when --p_rev is on.
# ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def lookahead_resample(base_df: pd.DataFrame, target_seconds: int) -> pd.DataFrame:
        """
        Produce a 5s-aligned 'developing' OHLC view of a higher-TF.

        Each row in the returned DataFrame corresponds to a 5s timestamp in
        base_df. The OHLC at that row reflects the in-progress higher-TF bar
        that contains the timestamp:

            O = first 5s open in the higher-TF window (constant across window)
            H = cumulative max of 5s highs from window start through t
            L = cumulative min of 5s lows  from window start through t
            C = current 5s close at t

        Pine equivalent:
            request.security(syminfo.tickerid, "<target>S",
                             line, barmerge.gaps_off, barmerge.lookahead_on)

        Volume is intentionally excluded — BB/K chains don't consume it.

        Parameters
        ----------
        base_df : 5s OHLCV DataFrame with columns timestamp, open, high, low, close
        target_seconds : higher TF in seconds (e.g. 30, 60, 360)

        Returns
        -------
        DataFrame parallel to base_df (same length, same timestamps) with
        columns: timestamp, open, high, low, close.
        """
        """[docstring unchanged]"""
        ts        = base_df['timestamp'].to_numpy()
        window_id = (ts // (target_seconds * 1000)).astype(np.int64)

        # kline_collection columns are DECIMAL → object dtype via pymysql.
        # Cast to float64 up front so groupby cython ops (transform/cummax/cummin)
        # can run. Without this we hit "function is not implemented for dtype:object".
        tmp = pd.DataFrame({
            'open':  base_df['open'].to_numpy(dtype=float),
            'high':  base_df['high'].to_numpy(dtype=float),
            'low':   base_df['low'].to_numpy(dtype=float),
            'close': base_df['close'].to_numpy(dtype=float),
        })

        g = tmp.groupby(window_id, sort=False)
        return pd.DataFrame({
            'timestamp': ts,
            'open':      g['open'].transform('first').to_numpy(),
            'high':      g['high'].cummax().to_numpy(),
            'low':       g['low'].cummin().to_numpy(),
            'close':     tmp['close'].to_numpy(),
        })
        
    @staticmethod
    def f_bb_lookahead(base_df: pd.DataFrame, target_seconds: int,
                       length: int, mult: float, src: str,
                       high_b: float = 85.0, low_b: float = 15.0) -> np.ndarray:
        """
        BB(length, mult) at each 5s bar against the developing higher-TF bar.

        Pine equivalent:
            bb_value = request.security(..., "<target>S",
                                        bb_calc(src, length, mult),
                                        barmerge.gaps_off, barmerge.lookahead_on)

        At each 5s bar t in developing window w, the BB sees:
          • (length-1) source values from the closed windows: w-(length-1) .. w-1
          • 1 developing source value: the lookahead-resampled source at t

        Mean and stdev are closed-form: pre-compute rolling sum and rolling
        sum-of-squares over the closed source series at window length (length-1),
        then combine with the developing value at each 5s.

        Returns a 1D float array parallel to base_df (NaN where insufficient
        history). Same return shape and scaling as f_bb.
        """
        # ── closed higher-TF source series ────────────────────────────────
        closed     = IndicatorComputer.resample(base_df, target_seconds)
        closed_src = IndicatorComputer.build_source(closed, src)
        closed_ts  = closed['timestamp'].to_numpy()

        # Rolling sums over the prior (length-1) closed bars.
        # roll_sum[i] = sum of closed_src[i-(length-2) .. i]  (window length-1)
        s    = pd.Series(closed_src)
        roll_sum   = s.rolling(length - 1, min_periods=length - 1).sum().to_numpy()
        roll_sumsq = (s ** 2).rolling(length - 1, min_periods=length - 1).sum().to_numpy()

        # ── developing source values at every 5s ──────────────────────────
        dev_df  = IndicatorComputer.lookahead_resample(base_df, target_seconds)
        dev_src = IndicatorComputer.build_source(dev_df, src)

        # ── map each 5s timestamp to its developing-window index in closed ─
        base_ts = base_df['timestamp'].to_numpy()
        # searchsorted(right) - 1 = last closed bar whose timestamp <= base_ts.
        # Since closed bars are at window-start timestamps, this gives the
        # closed-array index of the CURRENT developing window.
        idx = np.searchsorted(closed_ts, base_ts, side='right') - 1

        # Lookback uses closed bars 0..idx-1 (length-1 of them ending at idx-1).
        # Safe-index trick: clamp to 0 for invalid rows, mask result via np.where.
        valid_idx    = idx >= 1
        lookback_idx = np.where(valid_idx, idx - 1, 0)
        lb_sum   = np.where(valid_idx, roll_sum  [lookback_idx], np.nan)
        lb_sumsq = np.where(valid_idx, roll_sumsq[lookback_idx], np.nan)

        full_sum   = lb_sum   + dev_src
        full_sumsq = lb_sumsq + dev_src * dev_src

        mean = full_sum / length
        var  = full_sumsq / length - mean * mean
        with np.errstate(invalid='ignore'):
            var = np.where(var < 0.0, 0.0, var)   # numerical guard
        std = np.sqrt(var)

        # Same final scaling as f_bb: position of src within [basis-dev, basis+dev]
        # mapped to [low_b, high_b].
        dev_band = mult * std
        span     = 2.0 * dev_band
        with np.errstate(invalid='ignore', divide='ignore'):
            pct = np.where(span != 0.0, (dev_src - (mean - dev_band)) / span, np.nan)
        return (high_b - low_b) * pct + low_b

    @staticmethod
    def f_k_lookahead(base_df: pd.DataFrame, target_seconds: int,
                      k_len: int, rsi_len: int, stc_len: int, src: str) -> np.ndarray:
        """
        K chain (RSI → Stoch → SMA) at each 5s bar against the developing
        higher-TF bar.

        Pine equivalent:
            k_value = request.security(..., "<target>S",
                                       sma(stoch(rsi(src, rsi_len), stc_len), k_len),
                                       barmerge.gaps_off, barmerge.lookahead_on)

        Not exercised by the 5s gate round (b6M is BB, all six 5s vote
        contributors are 5s-native). Provided as forward-looking infrastructure
        for when a K-line target is calibrated on a higher TF — pre-built so
        we don't have to think about it under pressure later.

        Implementation parallels f_bb_lookahead: rolling state on the closed
        series, single-step update at each 5s using developing values. RSI uses
        the same _ema as IndicatorComputer._rsi (alpha = 2/(n+1)) for consistency
        with the non-lookahead path — known to deviate slightly from Pine's
        Wilder smoothing, same way the non-lookahead version does.

        Returns a 1D float array parallel to base_df.
        """
        # ── closed higher-TF chain ────────────────────────────────────────
        closed     = IndicatorComputer.resample(base_df, target_seconds)
        closed_src = IndicatorComputer.build_source(closed, src)
        closed_ts  = closed['timestamp'].to_numpy()

        # RSI components on closed series
        delta_c = np.diff(closed_src, prepend=np.nan)
        g_c     = np.where(delta_c > 0,  delta_c, 0.0)
        l_c     = np.where(delta_c < 0, -delta_c, 0.0)
        avg_g_c = IndicatorComputer._ema(g_c, rsi_len)
        avg_l_c = IndicatorComputer._ema(l_c, rsi_len)

        # Stoch needs rolling min/max of RSI — but we'll compute developing RSI
        # at each 5s, then do windowed min/max combining closed and developing.
        rsi_c   = IndicatorComputer._rsi(closed_src, rsi_len)  # consistent with the non-lookahead path

        # Stoch denominator components over previous (stc_len-1) closed RSI values
        rsi_c_s        = pd.Series(rsi_c)
        roll_rsi_min   = rsi_c_s.rolling(stc_len - 1, min_periods=stc_len - 1).min().to_numpy()
        roll_rsi_max   = rsi_c_s.rolling(stc_len - 1, min_periods=stc_len - 1).max().to_numpy()

        # SMA(k_len) at developing position uses (k_len-1) closed Stoch values
        # + 1 developing Stoch value. Need closed stoch series first.
        stoch_c        = IndicatorComputer._stoch(rsi_c, stc_len)
        stoch_c_s      = pd.Series(stoch_c)
        roll_stoch_sum = stoch_c_s.rolling(k_len - 1, min_periods=k_len - 1).sum().to_numpy()

        # ── developing source at every 5s ─────────────────────────────────
        dev_df  = IndicatorComputer.lookahead_resample(base_df, target_seconds)
        dev_src = IndicatorComputer.build_source(dev_df, src)

        base_ts = base_df['timestamp'].to_numpy()
        idx     = np.searchsorted(closed_ts, base_ts, side='right') - 1

        # Need at least one closed window prior for RSI's smoothing reference.
        valid    = idx >= 1
        lb_idx   = np.where(valid, idx - 1, 0)

        # ── developing RSI: single-step update from last-closed RSI state ──
        # alpha = 2/(n+1) update: avg_new = alpha*x + (1-alpha)*avg_prev
        alpha   = 2.0 / (rsi_len + 1.0)
        prev_src = np.where(valid, closed_src[lb_idx], np.nan)
        delta_d  = dev_src - prev_src
        g_d      = np.where(delta_d > 0,  delta_d, 0.0)
        l_d      = np.where(delta_d < 0, -delta_d, 0.0)
        avg_g_d  = alpha * g_d + (1.0 - alpha) * np.where(valid, avg_g_c[lb_idx], np.nan)
        avg_l_d  = alpha * l_d + (1.0 - alpha) * np.where(valid, avg_l_c[lb_idx], np.nan)
        with np.errstate(invalid='ignore', divide='ignore'):
            rs       = np.where(avg_l_d != 0.0, avg_g_d / avg_l_d, np.inf)
        rsi_d    = 100.0 - (100.0 / (1.0 + rs))

        # ── developing Stoch ──────────────────────────────────────────────
        lb_rsi_min = np.where(valid, roll_rsi_min[lb_idx], np.nan)
        lb_rsi_max = np.where(valid, roll_rsi_max[lb_idx], np.nan)
        stoch_min  = np.minimum(lb_rsi_min, rsi_d)
        stoch_max  = np.maximum(lb_rsi_max, rsi_d)
        rng        = stoch_max - stoch_min
        with np.errstate(invalid='ignore', divide='ignore'):
            stoch_d = np.where(rng != 0.0, 100.0 * (rsi_d - stoch_min) / rng, 50.0)

        # ── developing SMA of Stoch ───────────────────────────────────────
        lb_stoch_sum = np.where(valid, roll_stoch_sum[lb_idx], np.nan)
        return (lb_stoch_sum + stoch_d) / k_len


# ─────────────────────────────────────────────────────────────────────────────
# PKDetector
# ─────────────────────────────────────────────────────────────────────────────

class PKDetector:
    """
    Applies f_pk_state logic across a pre-computed indicator line + DEMA.
    Only emits signals when the combined gate oob_side is non-zero and
    the PK direction matches the gate direction.

    Pine alignment note (260514)
    ---------------------------
    This class's peak-search window is one bar wider than Pine's f_pk_state
    (uses pool_range+1 bars where Pine uses pool_range). Intentionally
    preserved for continuity with the 30-day grind dataset that produced
    the b6M centroid (or_pk=1).

    The newer Pk5sGateComputer matches Pine exactly — its f_pk_state covers
    line[i - upper + 1 : i - lower + 1]. The two classes coexist in this
    round; the discrepancy here will be patched once the next clean centroid
    is locked. See round spec 260514_pk5s_spec.md.
    """

    _PM_LONG  =  2.0
    _PM_SHORT = -2.0

    def __init__(self, high_b: float = 70.0, low_b: float = 30.0) -> None:
        self._midpoint = (high_b + low_b) / 2.0
        self._log      = get_logger(self.__class__.__name__)

    def detect(self, line: np.ndarray, dema: np.ndarray,
               pool_c: int, pool_w: int, pool_range: int,
               multiplier: int, slope_floor: float,
               oob_side: np.ndarray, params: dict) -> list:

        # pool_range=0 means disabled — skip
        if pool_range == 0:
            return []

        signals = []
        half    = pool_range // 2

        for label, bars in (('close', pool_c), ('wide', pool_w)):
            lower  = (bars - half) * multiplier
            upper  = (bars + half) * multiplier
            center = bars * multiplier

            for i in range(upper + 1, len(line)):
                if np.isnan(line[i]) or np.isnan(dema[i]) or np.isnan(dema[i - center]):
                    continue
                side = int(oob_side[i])
                if side == 0:
                    continue

                window = line[i - upper : i - lower + 1]
                if not len(window):
                    continue
                peak = np.max(window) if line[i] > self._midpoint else np.min(window)

                line_slope  = float(line[i] - peak)
                price_slope = float(dema[i] - dema[i - center])
                slope_diff  = abs(line_slope - price_slope)

                if slope_diff <= slope_floor:
                    continue

                pk_state = (
                    (1.0 if line_slope > 0 else -1.0)
                    if np.sign(line_slope) != np.sign(price_slope)
                    else (self._PM_LONG if line_slope > 0 else self._PM_SHORT)
                )

                expected = -side
                if pk_state not in (float(expected), float(expected) * 2.0):
                    continue

                signals.append({
                    'bar_index':   i,
                    'direction':   expected,
                    'pk_state':    pk_state,
                    'line_value':  float(line[i]),
                    'slope':       line_slope,
                    'slope_diff':  slope_diff,
                    'dema_slope':  price_slope,
                    'dema_value':  float(dema[i]),
                    'pool':        label,
                    'len':         params['len'],
                    'mult':        params['mult'],
                    'src':         params['src'],
                    'pool_c':      pool_c,
                    'pool_w':      pool_w,
                    'pool_range':  pool_range,
                    'slope_floor': slope_floor,
                    'multiplier':  multiplier,
                })

        return signals

# ═══════════════════════════════════════════════════════════════════════════
# PIECE B — Pk5sGateComputer class
#
# Insert as a new top-level class in managers.py, immediately after
# PKDetector and before SwingAnalyzer (around line 770 in the current file).
# ═══════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# Pk5sGateComputer
# ─────────────────────────────────────────────────────────────────────────────

class Pk5sGateComputer:
    """
    The 5s PK vote machine. Pine s5_pk_final equivalent, replicated in Python.

    Purpose
    -------
    Produces a directional gate from a multi-line weighted PK vote, evaluated
    every 5s bar. Each contributing line votes 'long', 'short', or 'neutral'
    based on its slope vs DEMA slope; votes accumulate with per-line weights;
    PM (price-matched) votes suppress the opposing bucket; ratios are
    thresholded; a decision-delay countdown gates final fires.

    Output is sign-inverted from Pine s5_pk_final (Pine +1=long → Python -1)
    so it plugs into IndicatorComputer.fold_gates alongside bny30M/p as a
    third OOB-equivalent gate. After folding, PKDetector consumes oob_side
    and emits/suppresses per-line PK signals.

    Pine alignment
    --------------
    Mirrors bbstr.pine sections (line numbers may drift; concept-stable):
      • f_pk_state      → per-line state (±1 divergence, ±2 PM, 0 neutral)
                          (Pine line 1368, replicated here in _states_standard)
      • f_vote          → state → long/short/neutral buckets at full weight
                          (Pine line 1508)
      • PM suppression  → adj_long  = max(0, long_pts  − pm_short_wt × pm_supp)
                          adj_short = max(0, short_pts − pm_long_wt  × pm_supp)
                          (Pine line 1613-1614)
      • ratio scaling   → (adj_x / active_w) × 10
                          denominator includes neutrals (Pine pm_option_a=false)
                          (Pine line 1616-1618)
      • decision delay  → N-bar persistence before fire; gate-open check only
                          at countdown start, in-progress countdowns run to
                          completion. At the 5s level there is no upstream gate
                          to check.
                          (Pine line 1624-1648)

    Pk5sGateComputer's f_pk_state window matches Pine exactly: covers
    line[i - upper + 1 : i - lower + 1] of length pool_range bars. The
    existing PKDetector carries a 1-bar wider window — intentionally left
    as-is for continuity with the 30-day grind dataset. See PKDetector
    docstring and round spec 260514 for rationale.

    Design notes
    ------------
    PM divergence (captured for the codebase, not just chat):

        PM_LONG means "the bullish lines and the price proxy are organically
        aligned — no visible divergence here." That alignment is the opposite
        of divergence; it's evidence of ongoing directional strength. The 0.4
        suppression weight lets that evidence reduce opposing votes by 40% of
        its own weight, without itself voting directionally. Gating the
        verdict out when PM did the heavy lifting would contradict trusting
        PM evidence at all.

    Dead zone: not implemented. With the ×10 ratio scaling, threshold 7.5
    mathematically forces a ≥5-point ratio gap — already a strong condition.

    Trigger modes (per-line, via tcev_trigger_mode):
      • 'standard_pk' — f_pk_state evaluates every history-valid bar.
      • 'roc_curl'    — evaluates only on bars where line slope changed by
                        more than tcev_roc_threshold° from the prior bar.
                        Peak = line[i-1] (the spike); DEMA anchor = dema[i-1].
                        Used by b30M / b30b in the future trend machine.
                        No seed rows use this mode in the 5s gate round.

    Round spec: 260514_pk5s_spec.md
    """

    _PM_LONG  =  2.0
    _PM_SHORT = -2.0

    def __init__(self, db: 'DatabaseManager') -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    # ── public ──────────────────────────────────────────────────────────────
    def compute(self, tce_pk: int,
                base_df:  pd.DataFrame,
                dema:     np.ndarray,
                params:   dict,
                midpoint: float = 50.0) -> np.ndarray:
        """
        Build the OOB-equivalent gate array for one pk_5s tce row.

        Parameters
        ----------
        tce_pk : the pk_5s test_config_extensions row PK
        base_df : 5s OHLCV
        dema : DEMA series on the base 5s (same dema as PKDetector consumes)
        params : tce_params dict (pool_c, pool_w, pool_slope, pool_range,
                 threshold_long, threshold_short, pm_suppression,
                 decision_delay)
        midpoint : f_pk_state midpoint, default 50

        Returns
        -------
        int8 array length len(base_df), sign-inverted vs Pine s5_pk_final:
          -1 = long PK fired (oob_side equivalent: LO OOB → expected = +1 long)
          +1 = short PK fired (oob_side equivalent: HI OOB → expected = -1 short)
           0 = idle / suppressed by decision delay / no verdict
        """
        votes = self._load_votes(tce_pk)
        n     = len(base_df)
        if not votes:
            self._log.warning(f'pk_5s tce_pk={tce_pk}: no active vote lines')
            return np.zeros(n, dtype=np.int8)

        pool_c       = int(params['pool_c'])
        pool_w       = int(params['pool_w'])
        pool_range   = int(params['pool_range'])
        slope_floor  = float(params['pool_slope'])
        thr_long     = float(params['threshold_long'])
        thr_short    = float(params['threshold_short'])
        pm_supp      = float(params['pm_suppression'])
        decision_dly = int(params['decision_delay'])

        long_pts    = np.zeros(n, dtype=np.float64)
        short_pts   = np.zeros(n, dtype=np.float64)
        neutral_pts = np.zeros(n, dtype=np.float64)
        pm_long_wt  = np.zeros(n, dtype=np.float64)
        pm_short_wt = np.zeros(n, dtype=np.float64)

        for v in votes:
            line = self._compute_line(v, base_df)

            # Trigger-mode dispatch. roc_curl produces a single state array
            # used for both pool labels — pool_c/pool_w don't define different
            # evaluations in that mode, only how much weight contributes.
            if v['tcev_trigger_mode'] == 'roc_curl':
                threshold = float(v.get('tcev_roc_threshold') or 45.0)
                s_curl    = self._states_roc_curl(line, dema, threshold, midpoint)
                pool_states = {'close': s_curl, 'wide': s_curl}
            else:
                pool_states = {
                    'close': self._states_standard(line, dema, pool_c, pool_range, slope_floor, midpoint),
                    'wide':  self._states_standard(line, dema, pool_w, pool_range, slope_floor, midpoint),
                }

            for pool_label in ('close', 'wide'):
                weight = int(v[f'tcev_weight_{pool_label}'])
                if weight == 0:
                    continue
                states = pool_states[pool_label]

                # Pine: f_vote — PM sentinels route to neutral at full weight
                long_pts    += np.where(states ==  1.0, weight, 0.0)
                short_pts   += np.where(states == -1.0, weight, 0.0)
                neutral_pts += np.where(
                    (states == 0.0) | (states == self._PM_LONG) | (states == self._PM_SHORT),
                    weight, 0.0
                )
                pm_long_wt  += np.where(states == self._PM_LONG,  weight, 0.0)
                pm_short_wt += np.where(states == self._PM_SHORT, weight, 0.0)

        # Pine: PM suppression post-processing
        adj_long  = np.maximum(0.0, long_pts  - pm_short_wt * pm_supp)
        adj_short = np.maximum(0.0, short_pts - pm_long_wt  * pm_supp)
        active_w  = adj_long + adj_short + neutral_pts        # pm_option_a=false

        with np.errstate(invalid='ignore', divide='ignore'):
            long_ratio  = np.where(active_w > 0, (adj_long  / active_w) * 10.0, 0.0)
            short_ratio = np.where(active_w > 0, (adj_short / active_w) * 10.0, 0.0)

        pk_raw = np.where(long_ratio  > thr_long,   1,
                 np.where(short_ratio > thr_short, -1, 0)).astype(np.int8)

        s5_pk_final = self._apply_decision_delay(pk_raw, decision_dly)

        fires_long  = int((s5_pk_final ==  1).sum())
        fires_short = int((s5_pk_final == -1).sum())
        self._log.info(
            f'pk_5s tce_pk={tce_pk}: raw fires {int((pk_raw != 0).sum())}, '
            f'after {decision_dly}-bar delay {fires_long + fires_short} '
            f'({fires_long}L / {fires_short}S)'
        )

        # Sign-invert for oob_side convention (Pine s5_pk_final +1 = long
        # → here -1, so PKDetector's `expected = -side` yields +1 long).
        return (-s5_pk_final).astype(np.int8)

    # ── data loading ────────────────────────────────────────────────────────
    def _load_votes(self, tce_pk: int) -> list:
        """Active vote rows joined with their indicator_configs context."""
        return self._db.execute(
            '''SELECT tcev.tcev_pk, tcev.tcev_weight_close, tcev.tcev_weight_wide,
                      tcev.tcev_trigger_mode, tcev.tcev_roc_threshold,
                      ic.ic_pk, ic.ic_line_type, ic.ic_src,
                      ic.ic_bb_len, ic.ic_bb_mult,
                      ic.ic_k_len,  ic.ic_rsi_len, ic.ic_stc_len,
                      itf.itf_seconds AS ic_itf_seconds,
                      s.is_prefix, itf.itf_label, il.il_suffix
               FROM test_config_ext_votes tcev
               JOIN indicator_configs    ic  ON ic.ic_pk    = tcev.tcev_ic_pk
               JOIN indicator_timeframes itf ON itf.itf_pk  = ic.ic_itf_pk
               JOIN indicator_series     s   ON s.is_pk     = ic.ic_is_pk
               JOIN indicator_lines      il  ON il.il_pk    = ic.ic_il_pk
               WHERE tcev.tcev_tce_pk    = %s
                 AND tcev.tcev_is_active = 1
                 AND (tcev.tcev_weight_close > 0 OR tcev.tcev_weight_wide > 0)''',
            (tce_pk,), fetch=True,
        )

    @staticmethod
    def _compute_line(v: dict, base_df: pd.DataFrame) -> np.ndarray:
        """
        Compute one indicator line on the base 5s timeline.

        For 5s-native lines: direct compute, no resampling. For higher-TF
        lines: forward-fill resample (matches Pine request.security without
        lookahead). This method is called by the 5s gate; for the 5s seed
        all six contributors are 5s-native so the forward-fill path is unused.
        """
        line_seconds = int(v['ic_itf_seconds'])
        src_df = base_df if line_seconds == 5 else IndicatorComputer.resample(base_df, line_seconds)
        src    = IndicatorComputer.build_source(src_df, v['ic_src'])
        if v['ic_line_type'] == 'bb':
            raw = IndicatorComputer.f_bb(src, int(v['ic_bb_len']), float(v['ic_bb_mult']))
        else:
            raw = IndicatorComputer.f_k(src, int(v['ic_rsi_len']),
                                        int(v['ic_stc_len']), int(v['ic_k_len']))
        return raw if line_seconds == 5 else IndicatorComputer.align_to_base(raw, src_df, base_df)

    # ── per-line state evaluators ──────────────────────────────────────────
    @staticmethod
    def _states_standard(line: np.ndarray, dema: np.ndarray,
                         bars: int, pool_range: int, slope_floor: float,
                         midpoint: float) -> np.ndarray:
        """
        Vectorised f_pk_state for one line at one pool depth (standard_pk mode).

        Pine: f_pk_state, bbstr.pine line 1368. Multiplier fixed at 1 (5s
        native — higher-TF lines forward-fill before reaching this function).

        Window matches Pine `ta.highest(line[lower], window)` exactly: covers
        line[i - upper + 1 : i - lower + 1], length = pool_range bars.

        Returns float (n,) of {NaN, 0.0, ±1.0, ±2.0}.
        """
        n      = len(line)
        half   = pool_range // 2
        lower  = bars - half
        upper  = bars + half
        center = bars
        win    = upper - lower             # = pool_range

        if upper + 1 >= n or win <= 0:
            return np.full(n, np.nan)

        s        = pd.Series(line)
        shifted  = s.shift(lower)          # shifted[i] = line[i - lower]
        roll_hi  = shifted.rolling(win, min_periods=win).max().to_numpy()
        roll_lo  = shifted.rolling(win, min_periods=win).min().to_numpy()
        # Net effect: roll_hi[i] = max(line[i - upper + 1 .. i - lower])

        # DEMA anchor at i - center
        dema_anchor = np.full(n, np.nan)
        if center < n:
            dema_anchor[center:] = dema[:n - center]

        peak        = np.where(line > midpoint, roll_hi, roll_lo)
        line_slope  = line - peak
        price_slope = dema - dema_anchor
        slope_diff  = np.abs(line_slope - price_slope)

        with np.errstate(invalid='ignore'):
            diverge = np.sign(line_slope) != np.sign(price_slope)
            noise   = slope_diff <= slope_floor
            result  = np.where(
                diverge,
                np.where(line_slope > 0,  1.0, -1.0),
                np.where(line_slope > 0,  Pk5sGateComputer._PM_LONG,
                                          Pk5sGateComputer._PM_SHORT),
            )
            result = np.where(noise, 0.0, result)

        invalid = (
            np.isnan(line) | np.isnan(dema) | np.isnan(dema_anchor)
            | np.isnan(roll_hi) | np.isnan(roll_lo)
        )
        return np.where(invalid, np.nan, result)

    @staticmethod
    def _states_roc_curl(line: np.ndarray, dema: np.ndarray,
                         threshold_deg: float, midpoint: float) -> np.ndarray:
        """
        Vectorised f_pk_state for one line in roc_curl trigger mode.

        Triggers only on bars where the line's slope changed by more than
        threshold_deg from the prior bar. On a curl bar i:
          peak       = line[i-1]       (the spike — the bar before the curl)
          dema_anchor = dema[i-1]      (paired with the prior-bar peak)
          line_slope  = line[i] - line[i-1]
          price_slope = dema[i] - dema[i-1]
          pk_state    = ±1 divergence / ±2 PM via sign comparison

        slope_floor is not applied — the ROC trigger itself is the noise
        filter (only non-subtle moves reach evaluation).

        Returns float (n,) of {NaN, 0.0, ±1.0, ±2.0}. Bars below the curl
        threshold return NaN (no vote contribution).

        Not exercised by the 5s gate seed (all six contributors use
        standard_pk). Pre-built for b30M / b30b in the future trend machine.
        """
        n = len(line)
        if n < 3:
            return np.full(n, np.nan)

        # ROC curl trigger: change in 1-bar slope angle from i-1 to i.
        slope_prev = np.diff(line, prepend=np.nan)          # slope_prev[i] = line[i] - line[i-1]
        slope_curr = slope_prev                              # at i, "current" slope is the i-1→i delta
        slope_back = np.roll(slope_prev, 1)                  # at i, prior slope is i-2→i-1 delta
        slope_back[0] = np.nan
        with np.errstate(invalid='ignore'):
            curl_deg = np.abs(
                np.arctan(slope_curr) - np.arctan(slope_back)
            ) * (180.0 / np.pi)
        fires = curl_deg > threshold_deg

        # 1-bar slopes for the PK decision
        line_slope  = slope_prev                             # line[i] - line[i-1]
        dema_anchor = np.roll(dema, 1); dema_anchor[0] = np.nan
        price_slope = dema - dema_anchor

        out = np.full(n, np.nan)
        with np.errstate(invalid='ignore'):
            diverge = np.sign(line_slope) != np.sign(price_slope)
            states  = np.where(
                diverge,
                np.where(line_slope > 0,  1.0, -1.0),
                np.where(line_slope > 0,  Pk5sGateComputer._PM_LONG,
                                          Pk5sGateComputer._PM_SHORT),
            )
            # If both slopes are exactly zero, mark neutral (no signal)
            both_zero = (line_slope == 0.0) & (price_slope == 0.0)
            states    = np.where(both_zero, 0.0, states)

        valid = fires & ~np.isnan(line_slope) & ~np.isnan(price_slope)
        out   = np.where(valid, states, np.nan)
        return out

    # ── decision-delay state machine ───────────────────────────────────────
    @staticmethod
    def _apply_decision_delay(pk_raw: np.ndarray, delay: int) -> np.ndarray:
        """
        Pine: bbstr.pine line 1624-1648.

        State machine (no upstream gate at the 5s level, so the Pine
        `_gate_open` branch collapses):

            if pk_raw != 0:
                if pk_raw == pending:
                    countdown -= 1
                    if countdown == 0: fire = pk_raw
                else:
                    pending   = pk_raw
                    countdown = delay
                    fire      = 0
            else:
                pending = 0; countdown = 0; fire = 0

        Sequential by necessity — the state machine doesn't vectorise cleanly.
        Loop is in plain Python; n is typically a few hundred thousand 5s bars
        for a 30-day grind, well within tolerable single-pass loop time.
        """
        n         = len(pk_raw)
        out       = np.zeros(n, dtype=np.int8)
        pending   = 0
        countdown = 0
        for i in range(n):
            d = int(pk_raw[i])
            if d != 0:
                if d == pending:
                    countdown = max(0, countdown - 1)
                    if countdown == 0:
                        out[i] = d
                else:
                    pending   = d
                    countdown = delay
            else:
                pending   = 0
                countdown = 0
        return out

# ─────────────────────────────────────────────────────────────────────────────
# SwingAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class SwingAnalyzer:
    """
    Walks forward from each PK signal using close prices.

    Exit logic:
      - Stop is fixed at entry ± stop_pct% — never moves.
      - Profit zone starts when price travels at least (stop_pct + drag_pct)%
        in the trade direction. Below that threshold the position hasn't covered
        its risk + drag and max_profit is not tracked.
      - won        = stop breached after entering profit zone.
      - stopped    = stop breached before entering profit zone.
      - inconclusive = max_bars cap reached without stop breach.
    """

    def __init__(self, stop_pct: float = 0.33, max_bars: int = 1080,
                 drag_pct: float = 0.0) -> None:
        self._stop_long    = 1.0 - stop_pct / 100.0
        self._stop_short   = 1.0 + stop_pct / 100.0
        self._profit_long  = 1.0 + (stop_pct + drag_pct) / 100.0
        self._profit_short = 1.0 - (stop_pct + drag_pct) / 100.0
        self._stop_pct     = stop_pct
        self._drag_pct     = drag_pct
        self._max_bars     = max_bars
        self._log          = get_logger(self.__class__.__name__)

    def analyze(self, signals: list, close: np.ndarray) -> list:
        return [self._evaluate(sig, close) for sig in signals]

    def _evaluate(self, sig: dict, close: np.ndarray) -> dict:
        i, direction = sig['bar_index'], sig['direction']
        entry        = close[i]
        cap          = min(i + self._max_bars, len(close) - 1)

        stop_level       = entry * (self._stop_long  if direction == 1 else self._stop_short)
        profit_threshold = entry * (self._profit_long if direction == 1 else self._profit_short)

        best_price         = entry
        in_profit_zone     = False
        max_profit_pct     = 0.0
        bars_to_max_profit = None
        bars_to_stop       = None
        result             = 'inconclusive'

        for j in range(i + 1, cap + 1):
            c = close[j]

            if direction == 1:
                if not in_profit_zone and c >= profit_threshold:
                    in_profit_zone = True
                if in_profit_zone and c > best_price:
                    best_price         = c
                    max_profit_pct     = (best_price / entry - 1.0) * 100.0
                    bars_to_max_profit = j - i
                if c <= stop_level:
                    bars_to_stop = j - i
                    result       = 'won' if in_profit_zone else 'stopped'
                    break
            else:
                if not in_profit_zone and c <= profit_threshold:
                    in_profit_zone = True
                if in_profit_zone and c < best_price:
                    best_price         = c
                    max_profit_pct     = (entry / best_price - 1.0) * 100.0
                    bars_to_max_profit = j - i
                if c >= stop_level:
                    bars_to_stop = j - i
                    result       = 'won' if in_profit_zone else 'stopped'
                    break

        return {
            **sig,
            'max_profit_pct':     round(max_profit_pct, 6),
            'bars_to_stop':       bars_to_stop,
            'bars_to_max_profit': bars_to_max_profit,
            'result':             result,
            'stop_pct':           self._stop_pct,
        }


# ─────────────────────────────────────────────────────────────────────────────
# ParameterGridBuilder
# ─────────────────────────────────────────────────────────────────────────────

class ParameterGridBuilder:
    """Reads test_param_ranges for a tc_pk and expands all parameter combinations."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def build(self, tc_pk: int) -> list:
        rows = self._db.execute(
            '''SELECT tpr_param_name, tpr_current_value, tpr_step,
                      tpr_range, tpr_enum_values, tpr_param_type
               FROM test_param_ranges WHERE tpr_tc_pk = %s ORDER BY tpr_param_name''',
            (tc_pk,), fetch=True,
        )
        if not rows:
            raise ValueError(f'No param ranges for tc_pk={tc_pk}')

        param_lists = {}
        for row in rows:
            name  = row['tpr_param_name']
            ptype = row['tpr_param_type']

            if ptype == 'enum':
                param_lists[name] = [v.strip() for v in row['tpr_enum_values'].split(',')]
                continue

            current = float(row['tpr_current_value'])
            step    = float(row['tpr_step'])
            rng     = float(row['tpr_range'])
            n       = int(round(rng / step)) if step else 0
            half    = n // 2
            values  = [round(current - half * step + k * step, 8) for k in range(n + 1)]

            if ptype == 'int':
                values = sorted(set(int(round(v)) for v in values))
                # pool_range=0 means disabled — exclude
                if name == 'pool_range':
                    values = [v for v in values if v > 0]

            param_lists[name] = values

        keys   = list(param_lists.keys())
        combos = list(itertools.product(*[param_lists[k] for k in keys]))
        self._log.info(f'Grid: {len(combos)} combinations from {len(keys)} params')
        return [dict(zip(keys, combo)) for combo in combos]


# ─────────────────────────────────────────────────────────────────────────────
# OptimizerRunner
# ─────────────────────────────────────────────────────────────────────────────

class OptimizerRunner:
    """Drives the parameter grid. Per combo: compute, detect, analyze, persist."""

    def __init__(self, db: DatabaseManager, detector: PKDetector, analyzer: SwingAnalyzer) -> None:
        self._db       = db
        self._detector = detector
        self._analyzer = analyzer
        self._log      = get_logger(self.__class__.__name__)

    def run(self, or_pk: int,
            base_df:  pd.DataFrame,
            ind_df:   pd.DataFrame,
            dema:     np.ndarray,
            oob_side: np.ndarray,
            param_grid: list,
            config: dict,
            p_rev_enabled: bool = False) -> None:
        """
        Drive the parameter grid for one calibration target.

        Round 260514: when p_rev_enabled and the calibration line's TF > 5s,
        compute the indicator line via IndicatorComputer.f_bb_lookahead
        (Pine barmerge.lookahead_on equivalent) instead of the resample +
        forward-fill chain. Returns values that resolve at 5s precision
        against the developing higher-TF bar.

        For 5s-native targets (ind_seconds == 5) p_rev is a no-op — the
        flag is honoured by collapsing to the regular f_bb path since there
        is no higher TF to look ahead on.
        """
        
        close = base_df['close'].to_numpy(dtype=float)
        total = len(param_grid)

        ind_seconds = int(config['ic_itf_seconds'])
        use_lookahead = bool(p_rev_enabled and ind_seconds > 5)
        if use_lookahead:
            self._log.info(f'p_rev active: indicator line via f_bb_lookahead '
                           f'(TF={ind_seconds}s)')

        for idx, params in enumerate(param_grid, 1):
            self._log.info(f'[{idx}/{total}]  {params}')
            if use_lookahead:
                # Pine: request.security(..., barmerge.lookahead_on)
                line = IndicatorComputer.f_bb_lookahead(
                    base_df, ind_seconds,
                    int(params['len']), float(params['mult']), params['src'],
                    float(config['ic_high_boundary']),
                    float(config['ic_low_boundary']),
                )
            else:
                line_src = IndicatorComputer.build_source(ind_df, params['src'])
                line_raw = IndicatorComputer.f_bb(line_src, int(params['len']),
                                                   float(params['mult']))
                line     = IndicatorComputer.align_to_base(line_raw, ind_df, base_df)
            signals  = self._detector.detect(
                line, dema,
                int(params['pool_c']), int(params['pool_w']),
                int(params['pool_range']), int(params['multiplier']),
                float(params['slope_floor']), oob_side, params,
            )
            outcomes = self._analyzer.analyze(signals, close)
            self._persist(or_pk, base_df['timestamp'].to_numpy(), outcomes)

    @staticmethod
    def _db_val(v):
        """Convert NaN/inf to None so MySQL receives NULL rather than a literal string."""
        if isinstance(v, float) and not math.isfinite(v):
            return None
        return v

    def _persist(self, or_pk: int, timestamps: np.ndarray, outcomes: list) -> None:
        if not outcomes:
            return

        dv = self._db_val
        sig_sql = '''INSERT INTO pk_signals
            (pks_or_pk, pks_timestamp, pks_dir, pks_state, pks_line_value,
             pks_slope, pks_slope_diff, pks_dema_slope, pks_dema_value, pks_pool,
             pks_len, pks_mult, pks_src,
             pks_pool_c, pks_pool_w, pks_pool_range, pks_slope_floor, pks_multiplier)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        out_sql = '''INSERT INTO pk_outcomes
            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop,
             pko_bars_to_max_profit, pko_result, pko_stop_pct)
            VALUES (%s,%s,%s,%s,%s,%s)'''

        sig_rows = [
            (or_pk, int(timestamps[o['bar_index']]),
             o['direction'], dv(o['pk_state']), dv(o['line_value']),
             dv(o['slope']), dv(o['slope_diff']), dv(o['dema_slope']), dv(o['dema_value']), o['pool'],
             o['len'], o['mult'], o['src'],
             o['pool_c'], o['pool_w'], o['pool_range'], o['slope_floor'], o['multiplier'])
            for o in outcomes
        ]

        first_id = self._db.executemany(sig_sql, sig_rows)

        self._db.executemany(out_sql, [
            (first_id + i,
             dv(o['max_profit_pct']), o['bars_to_stop'],
             o['bars_to_max_profit'], o['result'], o['stop_pct'])
            for i, o in enumerate(outcomes)
        ])


# ─────────────────────────────────────────────────────────────────────────────
# ReportExporter
# ─────────────────────────────────────────────────────────────────────────────

class ReportExporter:
    """Exports a completed optimizer run to CSV."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def export(self, or_pk: int, output_dir: str = '.') -> str:
        rows = self._db.execute(
            '''SELECT s.pks_timestamp, s.pks_dir, s.pks_state, s.pks_pool,
                      s.pks_line_value, s.pks_slope, s.pks_slope_diff,
                      s.pks_dema_slope, s.pks_dema_value,
                      s.pks_len, s.pks_mult, s.pks_src,
                      s.pks_pool_c, s.pks_pool_w, s.pks_pool_range,
                      s.pks_slope_floor, s.pks_multiplier,
                      o.pko_max_profit_pct, o.pko_bars_to_stop,
                      o.pko_bars_to_max_profit, o.pko_result, o.pko_stop_pct
               FROM pk_signals s JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
               WHERE s.pks_or_pk = %s ORDER BY s.pks_timestamp ASC''',
            (or_pk,), fetch=True,
        )
        path = f'{output_dir}/optimizer_run_{or_pk}.csv'
        pd.DataFrame(rows).to_csv(path, index=False)
        self._log.info(f'Exported {len(rows)} rows → {path}')
        return path


# ─────────────────────────────────────────────────────────────────────────────
# ReportManager
# ─────────────────────────────────────────────────────────────────────────────

class ReportManager:
    """Top-level grind coordinator. Entry point: run(tc_pk)."""

    _LOOKBACK_WEEKS = 5

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self, tc_pk: int,
            export_csv: bool = True, output_dir: str = '.',
            lookback_days: int = None,
            p_rev_enabled: bool = True,
            pk5s_gate_enabled: bool = True) -> Optional[str]:
        """
        Drive a full optimizer run for a test_config.

        Round 260514 changes:
          • p_rev_enabled — when True and the calibration line's TF > 5s,
            OptimizerRunner uses f_bb_lookahead (Pine barmerge.lookahead_on
            equivalent) instead of resample-and-forward-fill. Recorded on
            the optimizer_runs row.
          • pk5s_gate_enabled — when True, active pk_5s test_config_extensions
            rows produce gate arrays via Pk5sGateComputer that fold with
            bny30M/p as a third OOB-equivalent gate. Recorded on the run.

        Both flags default True for production. Toggle for the comparison
        matrix in 260514_pk5s_spec.md.
        """
        
        config = self._load_config(tc_pk)
        self._log.info(f'Config: {config["tc_indicator_label"]}')

        or_pk = self._db.execute(
            '''INSERT INTO optimizer_runs
                 (or_tc_pk, or_tp_pk, or_timestamp, or_dema_len, or_dema_src,
                  or_p_rev_enabled, or_pk5s_gate_enabled)
               VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            (tc_pk, int(config['tc_tp_pk']),
             int(datetime.now(timezone.utc).timestamp() * 1000),
             int(config['tc_dema_len']), config['tc_dema_src'],
             1 if p_rev_enabled else 0,
             1 if pk5s_gate_enabled else 0),
        )
        self._log.info(f'Run config: p_rev={"on" if p_rev_enabled else "off"}, '
                       f'pk5s_gate={"on" if pk5s_gate_enabled else "off"}')
        self._log.info(f'Run created: or_pk={or_pk}')

        base_df = self._load_klines(int(config['tc_tp_pk']), lookback_days)
        self._log.info(f'Base: {len(base_df)} × 5s bars')

        # DEMA on native 5s
        dema_src = IndicatorComputer.build_source(base_df, config['tc_dema_src'])
        dema     = IndicatorComputer.dema(dema_src, int(config['tc_dema_len']))

        # Gate: load active extensions, compute oob_side per gate, fold
        # Gates: bny30M/p (existing OOB gates) + optional pk_5s vote machines.
        # All gates fold via OR semantics in IndicatorComputer.fold_gates.
        gate_cfgs = self._load_gate_configs(tc_pk)
        gate_sides = []

        for gcfg in gate_cfgs:
            gate_df   = IndicatorComputer.resample(base_df, int(gcfg['ic_itf_seconds']))
            oob_raw   = IndicatorComputer.compute_oob_side(gcfg, gate_df)
            oob_align = IndicatorComputer.align_to_base(oob_raw, gate_df, base_df)
            gate_sides.append(oob_align)
            name = f'{gcfg["is_prefix"]}{gcfg["itf_label"]}{gcfg["il_suffix"]}'
            self._log.info(
                f'Gate {name}: {int((oob_align != 0).sum())} OOB bars'
                f' ({int((oob_align == 1).sum())} HI / {int((oob_align == -1).sum())} LO)'
            )

        # pk_5s gate extensions
        if pk5s_gate_enabled:
            pk5s_cfgs = self._load_pk5s_extensions(tc_pk)
            for pcfg in pk5s_cfgs:
                pk5s_arr = Pk5sGateComputer(self._db).compute(
                    int(pcfg['tce_pk']), base_df, dema, pcfg['tce_params'],
                    midpoint=(float(config['ic_high_boundary']) +
                              float(config['ic_low_boundary'])) / 2.0,
                )
                gate_sides.append(pk5s_arr.astype(float))
        else:
            self._log.info('pk_5s gate disabled by flag')

        if gate_sides:
            oob_side = IndicatorComputer.fold_gates(gate_sides)
            self._log.info(
                f'Combined gate: {int((oob_side != 0).sum())} OOB bars of {len(base_df)}'
            )
        else:
            self._log.warning('No active gates — all bars valid (no direction constraint)')
            oob_side = np.zeros(len(base_df), dtype=np.int8)

        # Indicator resampled to its TF (b6M → 5s → 360s)
        ind_seconds = int(config['ic_itf_seconds'])
        ind_df      = IndicatorComputer.resample(base_df, ind_seconds)
        self._log.info(f'Indicator: {len(ind_df)} × {ind_seconds}s bars')

        grid = ParameterGridBuilder(self._db).build(tc_pk)

        OptimizerRunner(
            self._db,
            PKDetector(float(config['ic_high_boundary']), float(config['ic_low_boundary'])),
            SwingAnalyzer(float(config['tc_stop_pct']), int(config['tc_max_bars']),
                          float(config.get('tc_drag_pct', 0.0))),
        ).run(or_pk, base_df, ind_df, dema, oob_side, grid, config,
              p_rev_enabled=p_rev_enabled)
              
        return ReportExporter(self._db).export(or_pk, output_dir) if export_csv else None

    def _load_config(self, tc_pk: int) -> dict:
        """Load test_config joined with its calibration indicator_config."""
        rows = self._db.execute(
            '''SELECT tc.*,
                      ic.ic_line_type, ic.ic_src, ic.ic_high_boundary, ic.ic_low_boundary,
                      ic.ic_bb_len, ic.ic_bb_mult, ic.ic_k_len, ic.ic_rsi_len, ic.ic_stc_len,
                      itf.itf_seconds  AS ic_itf_seconds,
                      s.is_prefix,
                      itf.itf_label,
                      il.il_suffix
               FROM test_configs tc
               JOIN indicator_configs    ic  ON ic.ic_pk      = tc.tc_ic_pk
               JOIN indicator_timeframes itf ON itf.itf_pk    = ic.ic_itf_pk
               JOIN indicator_series     s   ON s.is_pk       = ic.ic_is_pk
               JOIN indicator_lines      il  ON il.il_pk      = ic.ic_il_pk
               WHERE tc.tc_pk = %s''',
            (tc_pk,), fetch=True,
        )
        if not rows:
            raise ValueError(f'No test_config for tc_pk={tc_pk}')
        return rows[0]

    def _load_gate_configs(self, tc_pk: int) -> list:
        """Load active gate extension configs, ordered by sort_order."""
        return self._db.execute(
            '''SELECT ic.*,
                      itf.itf_seconds AS ic_itf_seconds,
                      s.is_prefix,
                      itf.itf_label,
                      il.il_suffix
               FROM test_config_extensions tce
               JOIN indicator_configs    ic  ON ic.ic_pk      = tce.tce_ic_pk
               JOIN indicator_timeframes itf ON itf.itf_pk    = ic.ic_itf_pk
               JOIN indicator_series     s   ON s.is_pk       = ic.ic_is_pk
               JOIN indicator_lines      il  ON il.il_pk      = ic.ic_il_pk
               WHERE tce.tce_tc_pk    = %s
                 AND tce.tce_type     = 'gate'
                 AND tce.tce_is_active = 1
               ORDER BY tce.tce_sort_order''',
            (tc_pk,), fetch=True,
        )
    
    def _load_pk5s_extensions(self, tc_pk: int) -> list:
        """
        Active pk_5s tce rows for this test_config, with tce_params parsed
        from JSON. Each row has a tce_pk and a tce_params dict ready to feed
        into Pk5sGateComputer.compute(...).

        Returns [] if no active pk_5s extensions exist (gate folding falls
        back to bny30M/p only — the existing OOB-gate-only behaviour).
        """
        rows = self._db.execute(
            '''SELECT tce_pk, tce_params
               FROM test_config_extensions
               WHERE tce_tc_pk     = %s
                 AND tce_type      = 'pk_5s'
                 AND tce_is_active = 1
               ORDER BY tce_sort_order''',
            (tc_pk,), fetch=True,
        )
        # JSON column comes back as str on most pymysql configs; parse if so.
        for r in rows:
            if isinstance(r['tce_params'], (str, bytes)):
                r['tce_params'] = json.loads(r['tce_params'])
        return rows
        
        
    def _load_klines(self, tp_pk: int, lookback_days: int = None) -> pd.DataFrame:
        if lookback_days:
            cutoff = int((datetime.now(timezone.utc) - timedelta(days=lookback_days)).timestamp() * 1000)
            where, params = 'kc_tp_pk = %s AND kc_timestamp >= %s', (tp_pk, cutoff)
        else:
            where, params = 'kc_tp_pk = %s', (tp_pk,)
        rows = self._db.execute(
            f'''SELECT kc_timestamp AS timestamp, kc_open AS open, kc_high AS high,
                       kc_low AS low, kc_close AS close, kc_volume AS volume
                FROM kline_collection WHERE {where} ORDER BY kc_timestamp ASC''',
            params, fetch=True,
        )
        if not rows:
            raise RuntimeError(f'No klines for tp_pk={tp_pk}')
        return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# IndicatorMonitor
# ─────────────────────────────────────────────────────────────────────────────

class IndicatorMonitor:
    """
    Runs once per invocation — computes and logs current indicator values
    for live validation against TradingView.
    Scheduled inline worker (interval_s=10) in ProcessManager.
    Shows each gate line independently plus combined OOB status.
    """

    _LOOKBACK = 2000

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self, tp_pk: int, tc_pk: int) -> None:
        try:
            self._report(tp_pk, tc_pk)
        except Exception as exc:
            self._log.error(f'Monitor error: {exc}')

    def _report(self, tp_pk: int, tc_pk: int) -> None:
        cfg = self._load_cfg(tc_pk)
        if not cfg:
            return

        ind_name = f'{cfg["is_prefix"]}{cfg["itf_label"]}{cfg["il_suffix"]}'

        base_df = self._load_klines(tp_pk)
        if base_df.empty:
            self._log.info('── no klines yet — run backfill_synthetic ──')
            return

        # Indicator line
        ind_df  = IndicatorComputer.resample(base_df, int(cfg['ic_itf_seconds']))
        ind_src = IndicatorComputer.build_source(ind_df, cfg['ic_src'])
        bb      = IndicatorComputer.f_bb(
            ind_src, int(cfg['ic_bb_len']), float(cfg['ic_bb_mult']),
            float(cfg['ic_high_boundary']), float(cfg['ic_low_boundary']),
        )
        bb_val = float(bb[-1]) if len(bb) and not np.isnan(bb[-1]) else None

        # Gate lines
        gate_cfgs  = self._load_gate_cfgs(tc_pk)
        gate_lines = []
        gate_sides = []
        for gcfg in gate_cfgs:
            gname    = f'{gcfg["is_prefix"]}{gcfg["itf_label"]}{gcfg["il_suffix"]}'
            gate_df  = IndicatorComputer.resample(base_df, int(gcfg['ic_itf_seconds']))
            oob_raw  = IndicatorComputer.compute_oob_side(gcfg, gate_df)
            oob_aln  = IndicatorComputer.align_to_base(oob_raw, gate_df, base_df)
            gate_sides.append(oob_aln)

            # Latest value for display
            gsrc = IndicatorComputer.build_source(gate_df, gcfg['ic_src'])
            if gcfg['ic_line_type'] == 'bb':
                gvals = IndicatorComputer.f_bb(gsrc, int(gcfg['ic_bb_len']), float(gcfg['ic_bb_mult']))
            else:
                gvals = IndicatorComputer.f_k(gsrc, int(gcfg['ic_rsi_len']),
                                               int(gcfg['ic_stc_len']), int(gcfg['ic_k_len']))
            gval  = float(gvals[-1]) if len(gvals) and not np.isnan(gvals[-1]) else None
            side  = int(oob_aln[-1]) if len(oob_aln) else 0
            label = 'HI OOB' if side == 1 else ('LO OOB' if side == -1 else 'IB    ')
            gate_lines.append((gname, label, gval, gcfg['ic_line_type']))

        combined_side = int(IndicatorComputer.fold_gates(gate_sides)[-1]) if gate_sides else 0
        combined_str  = 'HI OOB' if combined_side == 1 else ('LO OOB' if combined_side == -1 else 'IB    ')

        # DEMA
        dema_src = IndicatorComputer.build_source(base_df, cfg['tc_dema_src'])
        dema     = IndicatorComputer.dema(dema_src, int(cfg['tc_dema_len']))
        dema_val = float(dema[-1]) if len(dema) and not np.isnan(dema[-1]) else None

        last_close = float(base_df['close'].iloc[-1])
        last_ts    = _ms_to_iso(int(base_df['timestamp'].iloc[-1]))

        sep = '─' * 64
        self._log.info(sep)
        self._log.info(
            f'  {last_ts}   close={last_close:.8f}'
            f'   5s bars={len(base_df)}   {int(ind_df.shape[0])} × {cfg["ic_itf_seconds"]}s bars'
        )
        self._log.info(
            f'  {ind_name:8s}  bb%b={ f"{bb_val:6.2f}" if bb_val is not None else "   --"}'
            f'   src({cfg["ic_src"]})={float(ind_src[-1]):.8f}'
        )
        for gname, label, gval, gtype in gate_lines:
            metric = 'bb%b' if gtype == 'bb' else 'k   '
            self._log.info(
                f'  {gname:8s}  {label}  {metric}={ f"{gval:6.2f}" if gval is not None else "   --"}'
            )
        self._log.info(f'  gate      {combined_str}  (combined)')
        self._log.info(
            f'  DEMA      { f"{dema_val:.8f}" if dema_val is not None else "--"}'
        )
        self._log.info(sep)

    def _load_cfg(self, tc_pk: int) -> Optional[dict]:
        rows = self._db.execute(
            '''SELECT tc.*,
                      ic.ic_line_type, ic.ic_src, ic.ic_high_boundary, ic.ic_low_boundary,
                      ic.ic_bb_len, ic.ic_bb_mult, ic.ic_k_len, ic.ic_rsi_len, ic.ic_stc_len,
                      itf.itf_seconds AS ic_itf_seconds,
                      s.is_prefix, itf.itf_label, il.il_suffix
               FROM test_configs tc
               JOIN indicator_configs    ic  ON ic.ic_pk   = tc.tc_ic_pk
               JOIN indicator_timeframes itf ON itf.itf_pk = ic.ic_itf_pk
               JOIN indicator_series     s   ON s.is_pk    = ic.ic_is_pk
               JOIN indicator_lines      il  ON il.il_pk   = ic.ic_il_pk
               WHERE tc.tc_pk = %s''',
            (tc_pk,), fetch=True,
        )
        return rows[0] if rows else None

    def _load_gate_cfgs(self, tc_pk: int) -> list:
        return self._db.execute(
            '''SELECT ic.*,
                      itf.itf_seconds AS ic_itf_seconds,
                      s.is_prefix, itf.itf_label, il.il_suffix
               FROM test_config_extensions tce
               JOIN indicator_configs    ic  ON ic.ic_pk      = tce.tce_ic_pk
               JOIN indicator_timeframes itf ON itf.itf_pk    = ic.ic_itf_pk
               JOIN indicator_series     s   ON s.is_pk       = ic.ic_is_pk
               JOIN indicator_lines      il  ON il.il_pk      = ic.ic_il_pk
               WHERE tce.tce_tc_pk     = %s
                 AND tce.tce_type      = 'gate'
                 AND tce.tce_is_active = 1
               ORDER BY tce.tce_sort_order''',
            (tc_pk,), fetch=True,
        )

    def _load_klines(self, tp_pk: int) -> pd.DataFrame:
        rows = self._db.execute(
            '''SELECT kc_timestamp AS timestamp, kc_open AS open, kc_high AS high,
                      kc_low AS low, kc_close AS close, kc_volume AS volume
               FROM kline_collection WHERE kc_tp_pk = %s
               ORDER BY kc_timestamp DESC LIMIT %s''',
            (tp_pk, self._LOOKBACK), fetch=True,
        )
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# OutlierReporter
# ─────────────────────────────────────────────────────────────────────────────

class OutlierReporter:
    """Queries pk_outcomes and logs param sets with unusual win-rate distributions."""

    _WIN_RATE_HI = 70.0
    _WIN_RATE_LO = 30.0
    _MIN_SAMPLES = 20

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self) -> None:
        self._log.info('Generating outlier report')
        stats = self._db.execute(
            '''SELECT pks_len, pks_mult, pks_src,
                      COUNT(*) AS total,
                      SUM(pko_result = 'won') AS won,
                      AVG(pko_max_profit_pct) AS avg_profit
               FROM pk_signals s JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
               GROUP BY pks_len, pks_mult, pks_src
               HAVING COUNT(*) >= %s
               ORDER BY won / COUNT(*) DESC''',
            (self._MIN_SAMPLES,), fetch=True,
        )
        if not stats:
            self._log.info('No results to report')
            return
        for row in stats:
            win_rate = int(row['won']) / max(int(row['total']), 1) * 100
            if win_rate >= self._WIN_RATE_HI or win_rate <= self._WIN_RATE_LO:
                flag = 'HIGH' if win_rate >= self._WIN_RATE_HI else 'LOW'
                self._log.info(
                    f'OUTLIER [{flag}]  len={row["pks_len"]}  mult={row["pks_mult"]}'
                    f'  src={row["pks_src"]}  win={win_rate:.1f}%  n={row["total"]}'
                    f'  avg_profit={float(row["avg_profit"]):.4f}%'
                )
        self._log.info('Outlier report complete')


# ─────────────────────────────────────────────────────────────────────────────
# WorkerSpec
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class WorkerSpec:
    """Describes one supervised worker."""
    name:               str
    target_fn:          Callable
    args:               tuple           = field(default_factory=tuple)
    restart_on_failure: bool            = True
    interval_s:         Optional[float] = None   # None=continuous, float=scheduled
    restart_delay_s:    float           = 5.0
    inline:             bool            = False  # True=run in main thread (console visible)


# ─────────────────────────────────────────────────────────────────────────────
# ProcessManager
# ─────────────────────────────────────────────────────────────────────────────

class ProcessManager:
    """
    Supervises WorkerSpecs as child processes or inline main-thread tasks.
    Continuous workers restart on exit. Scheduled workers re-run at interval.
    Inline workers run in the supervisor loop (guaranteed console visibility).
    """

    _POLL_S = 1.0

    def __init__(self) -> None:
        self._specs     = {}
        self._processes = {}
        self._last_run  = {}
        self._shutdown  = multiprocessing.Event()
        self._log       = get_logger(self.__class__.__name__)

    def register(self, spec: WorkerSpec) -> None:
        self._specs[spec.name] = spec
        mode = 'inline' if spec.inline else ('scheduled' if spec.interval_s else 'continuous')
        self._log.info(f'Registered: {spec.name}  [{mode}]'
                       + (f'  interval={spec.interval_s}s' if spec.interval_s else ''))

    def start(self) -> None:
        self._log.info(f'Starting ProcessManager — {len(self._specs)} workers')
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT,  self._handle_signal)
        for spec in self._specs.values():
            if not spec.inline:
                self._start_worker(spec)
        self._supervise()

    def _supervise(self) -> None:
        while not self._shutdown.is_set():
            for name, spec in self._specs.items():
                if spec.inline:
                    self._check_inline(name, spec)
                else:
                    self._check(name, spec)
            time.sleep(self._POLL_S)
        self._stop_all()

    def _check_inline(self, name: str, spec: WorkerSpec) -> None:
        elapsed = time.time() - self._last_run.get(name, 0)
        if elapsed >= (spec.interval_s or 0):
            try:
                spec.target_fn(*spec.args)
            except Exception as exc:
                self._log.error(f'Inline worker {name} error: {exc}')
            self._last_run[name] = time.time()

    def _check(self, name: str, spec: WorkerSpec) -> None:
        proc  = self._processes.get(name)
        alive = proc is not None and proc.is_alive()
        if spec.interval_s is not None:
            elapsed = time.time() - self._last_run.get(name, 0)
            if not alive and elapsed >= spec.interval_s:
                self._start_worker(spec)
                self._last_run[name] = time.time()
        else:
            if not alive and spec.restart_on_failure and not self._shutdown.is_set():
                self._log.warning(f'{name} died — restarting in {spec.restart_delay_s}s')
                time.sleep(spec.restart_delay_s)
                self._start_worker(spec)

    def _start_worker(self, spec: WorkerSpec) -> None:
        proc = multiprocessing.Process(
            target=spec.target_fn, args=spec.args, name=spec.name, daemon=True,
        )
        proc.start()
        self._processes[spec.name] = proc
        self._last_run[spec.name]  = time.time()
        self._log.info(f'Started {spec.name}  pid={proc.pid}')

    def _stop_all(self) -> None:
        for name, proc in self._processes.items():
            if proc.is_alive():
                proc.terminate()
                proc.join(timeout=10)
                self._log.info(f'Stopped {name}')

    def _handle_signal(self, signum: int, _frame) -> None:
        self._log.info(f'Signal {signum} — shutting down')
        self._shutdown.set()


# ─────────────────────────────────────────────────────────────────────────────
# AnalyzeManager
# ─────────────────────────────────────────────────────────────────────────────

class AnalyzeManager:
    """
    Aggregates grind results from MySQL and produces a structured analysis report.
    All heavy lifting stays in the DB — Python only sees ~3,150 combo summary rows.

    Outputs:
      - Console / info.log: full analysis report
      - CSV: combo summary with all metrics (for further exploration)
    """

    _NUMERIC_PARAMS = ['len', 'mult', 'pool_c', 'pool_w', 'pool_range', 'slope_floor', 'multiplier']
    _CAT_PARAMS     = ['src']
    _DIV_LINE       = '═' * 68
    _SEC_LINE       = '─' * 68

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self, or_pk: int, min_signals: int = 30, top_n: int = 20,
            output_dir: str = '.') -> str:

        run_meta  = self._load_run_meta(or_pk)
        stop_pct  = float(run_meta['tc_stop_pct'])
        raw       = self._load_combo_summaries(or_pk)

        if not raw:
            self._log.error(f'No results found for or_pk={or_pk}')
            return ''

        df = pd.DataFrame(raw)
        df = self._enrich(df, stop_pct)

        # Filter to combos with enough decided trades
        filtered = df[df['decided'] >= min_signals].copy()

        self._report_overview(df, filtered, run_meta)
        self._report_sensitivity(filtered)
        self._report_top_n(filtered, top_n)
        self._report_centroid(filtered, top_n)

        path = f'{output_dir}/analysis_or{or_pk}.csv'
        df.to_csv(path, index=False)
        self._log.info(f'Full combo summary → {path}')
        return path

    # ── data loading ──────────────────────────────────────────────────────────

    def _load_run_meta(self, or_pk: int) -> dict:
        rows = self._db.execute(
            '''SELECT r.*, tc.tc_stop_pct, tc.tc_indicator_label,
                      tc.tc_dema_len, tc.tc_dema_src
               FROM optimizer_runs r
               JOIN test_configs tc ON tc.tc_pk = r.or_tc_pk
               WHERE r.or_pk = %s''',
            (or_pk,), fetch=True,
        )
        if not rows:
            raise ValueError(f'No optimizer_run for or_pk={or_pk}')
        return rows[0]

    def _load_combo_summaries(self, or_pk: int) -> list:
        return self._db.execute(
            '''SELECT
                   s.pks_len        AS len,
                   s.pks_mult       AS mult,
                   s.pks_src        AS src,
                   s.pks_pool_c     AS pool_c,
                   s.pks_pool_w     AS pool_w,
                   s.pks_pool_range AS pool_range,
                   s.pks_slope_floor AS slope_floor,
                   s.pks_multiplier  AS multiplier,
                   COUNT(*)                                                           AS total,
                   SUM(o.pko_result IN ('won','stopped'))                             AS decided,
                   SUM(o.pko_result = 'won')                                         AS won,
                   SUM(o.pko_result = 'stopped')                                     AS stopped_ct,
                   SUM(o.pko_result = 'inconclusive')                                AS inconclusive_ct,
                   AVG(CASE WHEN o.pko_result = 'won' THEN o.pko_max_profit_pct END) AS avg_win_pct,
                   AVG(o.pko_bars_to_stop)                                            AS avg_bars,
                   AVG(o.pko_bars_to_max_profit)                                      AS avg_bars_peak
               FROM pk_signals s
               JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
               WHERE s.pks_or_pk = %s
               GROUP BY s.pks_len, s.pks_mult, s.pks_src,
                        s.pks_pool_c, s.pks_pool_w, s.pks_pool_range,
                        s.pks_slope_floor, s.pks_multiplier''',
            (or_pk,), fetch=True,
        )

    # ── enrichment ────────────────────────────────────────────────────────────

    def _enrich(self, df: pd.DataFrame, stop_pct: float) -> pd.DataFrame:
        df = df.copy()
        for col in ['total', 'decided', 'won', 'stopped_ct', 'inconclusive_ct']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        for col in ['avg_win_pct', 'avg_bars', 'avg_bars_peak']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # When a combo has zero wins, avg_win_pct is NaN (mean over empty subset).
        # Coerce to 0 so expectancy collapses to -stop_pct rather than NaN —
        # the correct value when every signal stops out. Without this, idxmax
        # downstream raises "Encountered all NA values" on a degenerate day.
        df['avg_win_pct'] = df['avg_win_pct'].fillna(0.0)
        
        df['win_rate']         = df['won'] / df['decided'].replace(0, float('nan'))
        df['inconclusive_rate'] = df['inconclusive_ct'] / df['total'].replace(0, float('nan'))
        # expectancy in % per trade: E = win_rate × avg_win - loss_rate × stop
        df['expectancy']       = (
            df['win_rate'] * df['avg_win_pct']
            - (1.0 - df['win_rate']) * stop_pct
        )
        return df

    # ── report sections ───────────────────────────────────────────────────────

    def _report_overview(self, df: pd.DataFrame, filtered: pd.DataFrame, meta: dict) -> None:
        total_signals = int(df['total'].sum())
        days_approx   = total_signals / (17_280 * len(df))  # rough: signals per 5s bar
        baseline_wr   = float(df['won'].sum() / max(df['decided'].sum(), 1) * 100)

        self._log.info(self._DIV_LINE)
        self._log.info(
            f'  PK GRINDER — ANALYSIS   or_pk={meta["or_pk"]}'
            f'   {meta["tc_indicator_label"]}'
        )
        # Round 260514: surface the two new run flags so output is self-
        # describing. Defaults to "?" if columns are absent (pre-260514 runs).
        p_rev = meta.get('or_p_rev_enabled')
        pk5s  = meta.get('or_pk5s_gate_enabled')
        if p_rev is not None or pk5s is not None:
            self._log.info(
                f'  Run config: p_rev={"on" if p_rev else "off"}'
                f'   pk5s_gate={"on" if pk5s else "off"}'
            )
        self._log.info(self._DIV_LINE)
        
        if df['decided'].sum() < 5000:
            self._log.info('  ⚠  Low data volume — results are preliminary')
        self._log.info('')
        self._log.info('OVERVIEW')
        self._log.info(f'  Total signals        : {total_signals:>10,}')
        self._log.info(f'  Combos (all)         : {len(df):>10,}')
        self._log.info(f'  Combos (≥{meta.get("min_signals",30)} decided) : {len(filtered):>10,}')
        self._log.info(f'  Overall win rate     : {baseline_wr:>9.1f}%  ← baseline to beat')

        if not filtered.empty:
            best  = filtered.loc[filtered['expectancy'].idxmax()]
            worst = filtered.loc[filtered['expectancy'].idxmin()]
            self._log.info(
                f'  Best expectancy      : {float(best["expectancy"]):>9.4f}%'
                f'   win={float(best["win_rate"])*100:.1f}%'
                f'   signals={int(best["total"])}'
            )
            self._log.info(
                f'  Worst expectancy     : {float(worst["expectancy"]):>9.4f}%'
                f'   win={float(worst["win_rate"])*100:.1f}%'
                f'   signals={int(worst["total"])}'
            )
        self._log.info('')

    def _report_sensitivity(self, df: pd.DataFrame) -> None:
        if df.empty:
            return
        self._log.info('PER-PARAM SENSITIVITY  (avg expectancy across combos per value)')
        self._log.info(self._SEC_LINE)

        for param in self._NUMERIC_PARAMS + self._CAT_PARAMS:
            if param not in df.columns:
                continue
            grp = (df.groupby(param)['expectancy']
                     .agg(['mean', 'count'])
                     .reset_index()
                     .sort_values(param))
            parts = '   '.join(
                f'{row[param]}={float(row["mean"]):+.4f}%'
                for _, row in grp.iterrows()
            )
            self._log.info(f'  {param:<12}  {parts}')

        self._log.info('')

    def _report_top_n(self, df: pd.DataFrame, n: int) -> None:
        if df.empty:
            return
        top = df.nlargest(n, 'expectancy')
        self._log.info(f'TOP {n} COMBOS BY EXPECTANCY')
        self._log.info(self._SEC_LINE)
        self._log.info(
            f'  {"#":>3}  {"len":>3}  {"mult":>5}  {"src":<6}'
            f'  {"pc":>3}  {"pw":>3}  {"pr":>3}'
            f'  {"exp%":>7}  {"win%":>6}  {"avg_win":>8}  {"sigs":>6}'
        )
        for rank, (_, row) in enumerate(top.iterrows(), 1):
            self._log.info(
                f'  {rank:>3}  {int(row["len"]):>3}  {float(row["mult"]):>5.2f}'
                f'  {str(row["src"]):<6}'
                f'  {int(row["pool_c"]):>3}  {int(row["pool_w"]):>3}  {int(row["pool_range"]):>3}'
                f'  {float(row["expectancy"]):>+7.4f}'
                f'  {float(row["win_rate"])*100:>5.1f}%'
                f'  {float(row["avg_win_pct"]) if pd.notna(row["avg_win_pct"]) else 0.0:>7.4f}%'
                f'  {int(row["total"]):>6}'
            )
        self._log.info('')

    def _report_centroid(self, df: pd.DataFrame, n: int) -> None:
        if df.empty:
            return
        top = df.nlargest(n, 'expectancy').copy()

        # Guard: use uniform weights if all expectancy values are identical or negative
        weights = top['expectancy'].clip(lower=0)
        if weights.sum() == 0:
            weights = pd.Series(1.0, index=top.index)

        self._log.info(f'RECOMMENDED CENTROID  (top {n} combos, weighted by expectancy)')
        self._log.info(self._SEC_LINE)

        centroid = {}
        for param in self._NUMERIC_PARAMS:
            if param not in top.columns:
                continue
            vals = pd.to_numeric(top[param], errors='coerce')
            centroid[param] = round(float((vals * weights).sum() / weights.sum()), 4)

        # Categorical: weighted mode
        for param in self._CAT_PARAMS:
            if param not in top.columns:
                continue
            centroid[param] = (
                top.assign(w=weights)
                   .groupby(param)['w']
                   .sum()
                   .idxmax()
            )

        parts = '   '.join(f'{k}={v}' for k, v in centroid.items())
        self._log.info(f'  {parts}')
        self._log.info(self._DIV_LINE)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ms_to_iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()
