"""
kline_auditor — an independent REST cross-check of kline_collection. The "100% sure
of our OHLC" service.

WHY
  kline_collection is built by BarBuilder from the websocket tick stream. If that
  stream freezes or the tick→bar build is lossy, our tape drifts from the exchange and
  nothing notices. This service is a SECOND, INDEPENDENT data path — Bybit's REST kline
  API — that rebuilds the bars and records how far they diverge.

  And it matters more than it looks: a 1-tick error in ONE bar's close swings the
  short BB lines ~8 points on the 0-100 scale (the BB band is ~2 ticks wide on a quiet
  symbol; it's shift-invariant, so only PER-BAR errors bite). Near a boundary that flips
  a gate. So tick-level tape faithfulness is load-bearing — hence we measure it.

HOW (verified live: REST /v5/market/kline returns the DEVELOPING 1m bar with a close
that updates per trade — so "poll every second" reads the running price)
  Poll the developing 1m bar every 1s → the close is the price sample. Build 5s bars
  the EXACT same way BarBuilder does (gapless), just fed from REST 1s samples.

OBSERVE MODE (Joe 2026-06-06)
  We don't yet know the right tolerance, so we OBSERVE: each bar records the per-field
  O/H/L/C variance IN TICKS (no volume) — `ka_var_o/h/l/c`. The distribution of those
  counts drives the next move (zero-tolerance / freeze-check / close-only / …).
    5s tier: kc vs the REST-built bar, every 5s boundary.
    1m tier: a few seconds after the minute, the official CLOSED 1m bar vs kc's 1m
             aggregate (gold standard) AND the auditor's 1m aggregate (REST sanity).
  Only STRUCTURAL faults (missing kc bar / incomplete minute) ERROR-log; tick variance
  is recorded, not alarmed.

The PURE CORE (bar construction + 1m aggregate + tick-variance) is below and is the
testable heart (tests/test_kline_auditor.py); the KlineAuditor service wraps it.
"""

import math
import time
import requests
from datetime import datetime, timedelta, timezone

from logger import get_logger
from ..db.database_manager import DatabaseManager
from .bybit_kline_client import BybitKlineClient

_OHLC = ('o', 'h', 'l', 'c')


# ═══════════════════════════════════════════════════════════════════════════
# PURE CORE (tested by tests/test_kline_auditor.py)
# ═══════════════════════════════════════════════════════════════════════════
def build_5s_bar(prior_close, samples):
    """One 5s bar from the REST 1s samples, MIRRORING BarBuilder._build_one exactly:
      O = prior_close (gapless) when known, else the first sample
      C = last sample   ·   H = max([O] + samples)   ·   L = min([O] + samples)
      no samples + known prior_close → doji at prior_close   ·   neither → None (cold start)
    `samples` are prices — the developing-bar close sampled each second in the window.
    Returns (o, h, l, c) floats, or None."""
    if samples:
        s = [float(x) for x in samples]
        o = float(prior_close) if prior_close is not None else s[0]
        return (o, max([o] + s), min([o] + s), s[-1])
    if prior_close is not None:
        pc = float(prior_close)
        return (pc, pc, pc, pc)
    return None


def aggregate_1m(bars):
    """Roll a minute's (o, h, l, c, v) 5s bars into one 1m bar:
    O = first.o · C = last.c · H = max h · L = min l · V = sum v."""
    return (bars[0][0], max(b[1] for b in bars), min(b[2] for b in bars),
            bars[-1][3], sum(b[4] for b in bars))


def tick_variance(a, b, tick_size):
    """Per-field O/H/L/C variance IN TICKS between two bars (each (o, h, l, c[, …])):
    round((a[i] − b[i]) / tick_size). Returns {'o','h','l','c'} ints, or None if either
    bar is absent. The observe-mode signal — the DISTRIBUTION of these counts (per bar)
    drives the tolerance/role call. (Volume excluded by design.)"""
    if a is None or b is None:
        return None
    return {f: int(round((float(a[i]) - float(b[i])) / tick_size)) for i, f in enumerate(_OHLC)}


def _iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%H:%M:%S')


def _fmt_var(var) -> str:
    if var is None:
        return 'na'
    nz = ' '.join(f'{f}{v:+d}' for f, v in var.items() if v)
    return nz or 'match'


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════════════════════
class KlineAuditor:
    """Polls the developing 1m bar every 1s, rebuilds 5s bars (mirroring BarBuilder),
    and records the per-field tick variance vs kline_collection at the 5s and 1m tiers.
    Observe mode: structural faults ERROR-log, tick variance is recorded. Permanent,
    fully isolated service (its own systemd unit) — it must survive the collector dying,
    since catching exactly that is its job."""

    _BAR_S        = 5
    _MIN_MS       = 60_000
    _AUDIT        = 'kline_audit'
    _CONFIG       = 'kline_audit_config'
    _PRUNE_DAYS   = 7
    _GC_KEEP_MIN  = 5

    def __init__(self, db: DatabaseManager) -> None:
        self._db     = db
        self._client = BybitKlineClient()
        self._log    = get_logger(self.__class__.__name__)
        self._log.setLevel('INFO')
        import logging
        logging.getLogger('BybitKlineClient').setLevel('WARNING')   # quiet the 1/s poll chatter
        self._kc_lag     = 20         # s to wait for kc to land (BarBuilder build + late-tick rebuild)
        self._tick       = 0.00001    # instrument tick size (FARTCOIN); from config
        self._clock_off  = 0          # ms: Bybit server − local; aligns 5s bucketing to exchange time
        self._last_sync  = 0.0
        self._last_prune = time.time()

    # ── lifecycle ───────────────────────────────────────────────────────────
    def run(self, tp_pk: int, symbol: str) -> None:
        self._ensure_schema()
        self._kc_lag, self._tick = self._load_config()
        self._sync_clock()
        self._log.info(f'kline auditor started: {symbol} (observe mode; kc_lag={self._kc_lag}s, '
                       f'tick={self._tick}, clock_off={self._clock_off:+d}ms)')
        bar_ms = self._BAR_S * 1000
        prior_close = None
        cur_win, samples = None, []
        audit_5s, min_v, done_5s, done_min = {}, {}, set(), set()

        while True:
            try:
                self._sleep_to_next_second()
                if time.time() - self._last_sync > 300:
                    self._sync_clock()
                dev = self._poll_developing(symbol)
                if dev is None:
                    continue
                bar_start, _o, _h, _l, price, cum_v = dev
                now = int(time.time() * 1000) + self._clock_off   # exchange-corrected (kc is exchange-keyed)
                min_v[bar_start] = cum_v
                w = (now // bar_ms) * bar_ms
                if cur_win is None:
                    cur_win = w
                if w != cur_win:                               # a 5s window closed → build + store
                    bar = build_5s_bar(prior_close, samples)
                    if bar is not None:
                        prior_close = bar[3]
                        audit_5s[cur_win] = bar
                    samples, cur_win = [], w
                samples.append(price)

                lag = self._kc_lag * 1000                       # kc lands ~BarBuilder build + rebuild
                for ws in sorted(audit_5s):                     # deferred 5s record
                    if ws not in done_5s and (now - (ws + bar_ms)) >= lag:
                        self._flush_5s(tp_pk, ws, audit_5s[ws])
                        done_5s.add(ws)
                cur_min = (now // self._MIN_MS) * self._MIN_MS
                for m in (cur_min - self._MIN_MS, cur_min - 2 * self._MIN_MS):
                    if m in min_v and m not in done_min and (now - (m + self._MIN_MS)) >= lag:
                        self._reconcile_1m(tp_pk, symbol, m, audit_5s, min_v.get(m))
                        done_min.add(m)
                self._gc(cur_min, audit_5s, min_v, done_5s, done_min)
                self._maybe_prune(tp_pk)
            except Exception as e:                              # never let the permanent loop die
                self._log.error(f'loop error: {e}')
                time.sleep(1.0)

    def _sleep_to_next_second(self) -> None:
        now = time.time()
        time.sleep(max(0.0, math.ceil(now) - now))

    def _sync_clock(self) -> None:
        """RTT-corrected local→Bybit offset so 5s bucketing aligns to the exchange's bar
        boundaries (kc is keyed by exchange tick-time). Joe's misbucketing fix 2026-06-06."""
        try:
            t0  = time.time()
            srv = int(requests.get('https://api.bybit.com/v5/market/time', timeout=5).json()
                      ['result']['timeNano']) / 1e6                 # ms
            t1  = time.time()
            self._clock_off = int(srv - (t0 + t1) / 2 * 1000)
            self._last_sync = t1
            self._log.info(f'clock synced: Bybit offset {self._clock_off:+d} ms')
        except Exception as e:
            self._log.error(f'clock sync failed (keeping offset {self._clock_off:+d}ms): {e}')
            self._last_sync = time.time()                          # don't hammer on failure

    # ── polling ─────────────────────────────────────────────────────────────
    def _poll_developing(self, symbol: str):
        now = int(time.time() * 1000)
        try:
            bars = self._client.fetch_klines(symbol, '1', now - 180_000, now)
        except Exception as e:
            self._log.error(f'poll failed: {e}')
            return None
        if not bars:
            return None
        b = max(bars, key=lambda x: x['timestamp'])
        return (b['timestamp'], b['open'], b['high'], b['low'], b['close'], b['volume'])

    def _official_1m(self, symbol: str, minute_start: int):
        try:
            bars = self._client.fetch_klines(symbol, '1', minute_start, minute_start + 120_000)
        except Exception as e:
            self._log.error(f'official fetch failed: {e}')
            return None
        for b in bars:
            if b['timestamp'] == minute_start:
                return (b['open'], b['high'], b['low'], b['close'], b['volume'])
        return None

    # ── kline_collection reads ──────────────────────────────────────────────
    def _kc_5s(self, tp_pk: int, win_start: int):
        r = self._db.execute(
            '''SELECT kc_open, kc_high, kc_low, kc_close FROM kline_collection
               WHERE kc_tp_pk = %s AND kc_timestamp = %s''', (tp_pk, win_start), fetch=True)
        if not r:
            return None
        x = r[0]
        return (float(x['kc_open']), float(x['kc_high']), float(x['kc_low']), float(x['kc_close']))

    def _kc_minute(self, tp_pk: int, minute_start: int):
        rows = self._db.execute(
            '''SELECT kc_open, kc_high, kc_low, kc_close, kc_volume FROM kline_collection
               WHERE kc_tp_pk = %s AND kc_timestamp >= %s AND kc_timestamp < %s
               ORDER BY kc_timestamp''', (tp_pk, minute_start, minute_start + self._MIN_MS), fetch=True)
        return [(float(x['kc_open']), float(x['kc_high']), float(x['kc_low']),
                 float(x['kc_close']), float(x['kc_volume'])) for x in rows]

    # ── tiers (observe: record variance, alarm only on structural faults) ────
    def _flush_5s(self, tp_pk: int, win_start: int, audit_bar) -> None:
        kc  = self._kc_5s(tp_pk, win_start)
        var = tick_variance(kc, audit_bar, self._tick)
        if var is None:
            self._record(tp_pk, win_start, '5s', 'missing', kc, audit_bar, None, None, 'no kc bar')
            self._log.error(f'5s missing @ {_iso(win_start)}: kline_collection has no bar')
            return
        verdict = 'match' if not any(var.values()) else 'variance'
        self._record(tp_pk, win_start, '5s', verdict, kc, audit_bar, None, var, _fmt_var(var))

    def _reconcile_1m(self, tp_pk: int, symbol: str, minute_start: int, audit_5s: dict, audit_v) -> None:
        n      = self._MIN_MS // (self._BAR_S * 1000)                    # 12 bars/minute
        wins   = [minute_start + i * self._BAR_S * 1000 for i in range(n)]
        abars  = [audit_5s[w] for w in wins if w in audit_5s]
        kcbars = self._kc_minute(tp_pk, minute_start)
        official = self._official_1m(symbol, minute_start)
        if official is None or len(abars) < n or len(kcbars) < n:
            self._record(tp_pk, minute_start, '1m', 'incomplete', None, None, official, None,
                         f'audit={len(abars)}/{n} kc={len(kcbars)}/{n} official={official is not None}')
            self._log.error(f'1m incomplete @ {_iso(minute_start)}: audit {len(abars)}/{n}, '
                            f'kc {len(kcbars)}/{n}, official={official is not None}')
            return
        a_ohlc   = aggregate_1m([(b[0], b[1], b[2], b[3], 0.0) for b in abars])
        audit_1m = (a_ohlc[0], a_ohlc[1], a_ohlc[2], a_ohlc[3], float(audit_v or 0.0))
        kc_1m    = aggregate_1m(kcbars)
        var      = tick_variance(official, kc_1m, self._tick)            # gold standard: tape vs exchange
        var_a    = tick_variance(official, audit_1m, self._tick)         # REST sanity
        verdict  = 'match' if not any(var.values()) else 'variance'
        detail   = (f'off_vs_kc:{_fmt_var(var)} off_vs_audit:{_fmt_var(var_a)} '
                    f'vol off={official[4]} kc={kc_1m[4]}')
        self._record(tp_pk, minute_start, '1m', verdict, kc_1m, audit_1m, official, var, detail)

    # ── persistence ─────────────────────────────────────────────────────────
    def _record(self, tp_pk, ts, tier, verdict, kc, audit, official, var, detail) -> None:
        def u(t):
            return (list(t) + [None] * 5)[:5] if t else [None] * 5
        kco, ao, oo = u(kc), u(audit), u(official)
        v = var or {}
        self._db.execute(
            f'''INSERT INTO {self._AUDIT}
                   (ka_tp_pk, ka_timestamp, ka_tier, ka_verdict, ka_detail,
                    ka_var_o, ka_var_h, ka_var_l, ka_var_c,
                    ka_kc_open, ka_kc_high, ka_kc_low, ka_kc_close, ka_kc_volume,
                    ka_audit_open, ka_audit_high, ka_audit_low, ka_audit_close, ka_audit_volume,
                    ka_official_open, ka_official_high, ka_official_low, ka_official_close, ka_official_volume)
                VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE ka_verdict=VALUES(ka_verdict), ka_detail=VALUES(ka_detail),
                    ka_var_o=VALUES(ka_var_o), ka_var_h=VALUES(ka_var_h),
                    ka_var_l=VALUES(ka_var_l), ka_var_c=VALUES(ka_var_c),
                    ka_kc_close=VALUES(ka_kc_close), ka_audit_close=VALUES(ka_audit_close),
                    ka_official_close=VALUES(ka_official_close)''',
            (tp_pk, ts, tier, verdict, detail,
             v.get('o'), v.get('h'), v.get('l'), v.get('c'),
             *kco, *ao, *oo))

    def _ensure_schema(self) -> None:
        self._db.execute(f'''CREATE TABLE IF NOT EXISTS {self._AUDIT} (
            ka_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
            ka_tp_pk INT, ka_timestamp BIGINT, ka_tier VARCHAR(4), ka_verdict VARCHAR(16),
            ka_detail VARCHAR(255), ka_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            ka_var_o INT, ka_var_h INT, ka_var_l INT, ka_var_c INT,
            ka_kc_open FLOAT, ka_kc_high FLOAT, ka_kc_low FLOAT, ka_kc_close FLOAT, ka_kc_volume FLOAT,
            ka_audit_open FLOAT, ka_audit_high FLOAT, ka_audit_low FLOAT, ka_audit_close FLOAT, ka_audit_volume FLOAT,
            ka_official_open FLOAT, ka_official_high FLOAT, ka_official_low FLOAT, ka_official_close FLOAT, ka_official_volume FLOAT,
            UNIQUE KEY uq_audit (ka_tp_pk, ka_timestamp, ka_tier))''')

    def _load_config(self):
        """kline_audit_config — dialable knobs (config-tables discipline). Seeds a default
        active row if empty. Returns (kc_lag_s, tick_size). volume_tolerance kept for a
        later volume tier."""
        self._db.execute(f'''CREATE TABLE IF NOT EXISTS {self._CONFIG} (
            kac_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
            kac_label VARCHAR(80) DEFAULT '', kac_is_active TINYINT DEFAULT 0,
            kac_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            kac_volume_tolerance FLOAT DEFAULT 0.0,
            kac_kc_lag_s INT DEFAULT 20,
            kac_tick_size FLOAT DEFAULT 0.00001)''')
        sel = f'SELECT * FROM {self._CONFIG} WHERE kac_is_active=1 ORDER BY kac_pk DESC LIMIT 1'
        rows = self._db.execute(sel, fetch=True)
        if not rows:
            self._db.execute(f"INSERT INTO {self._CONFIG} (kac_label, kac_is_active) VALUES ('default', 1)")
            rows = self._db.execute(sel, fetch=True)
        r = rows[0]
        return int(r['kac_kc_lag_s']), float(r['kac_tick_size'])

    # ── housekeeping ────────────────────────────────────────────────────────
    def _gc(self, cur_min: int, audit_5s: dict, min_v: dict, done_5s: set, done_min: set) -> None:
        keep = cur_min - self._GC_KEEP_MIN * self._MIN_MS
        for d in (audit_5s, min_v):
            for k in [k for k in d if k < keep]:
                del d[k]
        for s in (done_5s, done_min):
            for k in [k for k in s if k < keep]:
                s.discard(k)

    def _maybe_prune(self, tp_pk: int) -> None:
        now = time.time()
        if now - self._last_prune < 3600:
            return
        cutoff = int((datetime.now(timezone.utc) - timedelta(days=self._PRUNE_DAYS)).timestamp() * 1000)
        self._db.execute(f'DELETE FROM {self._AUDIT} WHERE ka_tp_pk=%s AND ka_timestamp < %s', (tp_pk, cutoff))
        self._last_prune = now
