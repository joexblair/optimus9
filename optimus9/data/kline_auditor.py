"""
kline_auditor — an independent REST cross-check of kline_collection. The "100% sure
of our OHLC" service.

WHY
  kline_collection is built by BarBuilder from the websocket tick stream. If that
  stream freezes (the 06-04 incident) or the tick→bar build is lossy, our tape drifts
  from the exchange and nothing notices. This service is a SECOND, INDEPENDENT data
  path — Bybit's REST kline API — that rebuilds the bars and validates them, so a
  divergence is caught the instant it happens.

HOW (verified live: REST /v5/market/kline returns the DEVELOPING 1m bar with a close
that updates per trade — so "poll every second" reads the running price)
  Poll the developing 1m bar every 1s → the close is the price sample, the volume is
  the minute's running total. Consume the 1s sample stream like the tick collector
  consumes ticks, building 5s bars the EXACT same way BarBuilder does — so a mismatch
  can only be the two Bybit paths (REST poll vs WS stream) genuinely disagreeing,
  never a construction difference.

TWO TIERS (both zero-tolerance OHLC; volume gets a dialable tolerance, default 0)
  5s  — at each boundary, validate the REST-built 5s bar against kline_collection.
        OHLC only (the developing bar's volume is minute-cumulative, so per-5s volume
        has ≤1s attribution skew — not clean enough for zero-tolerance). Fast catch.
  1m  — a few seconds after the minute closes, fetch the official CLOSED 1m bar and
        reconcile OHLCV against BOTH the auditor's 1m aggregate AND kc's 1m aggregate.
        This is the gold standard: is our tape faithful to the exchange?

PHASING
  Phase 1 (now): record a kline_audit row + ERROR-log on any mismatch. Observe-only —
  the auditor earns trust before it acts.
  Phase 2 (later, task #19): alert / self-heal (backfill the bad bar from REST).

The PURE CORE (bar construction + verdicts + 1m reconcile) is below and is the testable
heart (tests/test_kline_auditor.py); the KlineAuditor service wraps it. No separate
design doc (infra build; korero's design-doc ritual is milestone-scoped).
"""

import logging
import math
import time
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
    `samples` are prices — the developing-bar close sampled each second in the window
    (held values for no-trade seconds are harmless: max/min/last ignore them).
    Returns (o, h, l, c) floats, or None."""
    if samples:
        s = [float(x) for x in samples]
        o = float(prior_close) if prior_close is not None else s[0]
        return (o, max([o] + s), min([o] + s), s[-1])
    if prior_close is not None:
        pc = float(prior_close)
        return (pc, pc, pc, pc)
    return None


def compare_5s(kc, audit):
    """Zero-tolerance OHLC verdict — kc's 5s bar vs the auditor's REST-built bar, each
    (o, h, l, c). OHLC are SELECTED values (max/min/last), so exact equality is the
    right test (no epsilon — no arithmetic to round). Verdicts:
      ok · mismatch (lists the offending fields) · missing (no kc bar) ·
      no_reference (auditor couldn't build)."""
    if kc is None:
        return {'verdict': 'missing', 'fields': [], 'deltas': {}}
    if audit is None:
        return {'verdict': 'no_reference', 'fields': [], 'deltas': {}}
    deltas = {f: float(kc[i]) - float(audit[i]) for i, f in enumerate(_OHLC)}
    bad    = [f for f, d in deltas.items() if d != 0.0]
    return {'verdict': 'mismatch' if bad else 'ok', 'fields': bad, 'deltas': deltas}


def aggregate_1m(bars):
    """Roll a minute's (o, h, l, c, v) 5s bars into one 1m bar:
    O = first.o · C = last.c · H = max h · L = min l · V = sum v."""
    return (bars[0][0], max(b[1] for b in bars), min(b[2] for b in bars),
            bars[-1][3], sum(b[4] for b in bars))


def reconcile_1m(official, audit, kc, vol_tol=0.0):
    """Three-way 1m reconcile — the official CLOSED 1m bar vs (a) the auditor's 1m
    aggregate and (b) kc's 1m aggregate. Each is (o, h, l, c, v). OHLC zero-tolerance;
    |Δvolume| ≤ vol_tol passes. official_vs_kc is the gold standard (our tape vs the
    exchange); official_vs_audit is the REST-path sanity (same source, should agree)."""
    def cmp(a, b):
        ohlc = [f for i, f in enumerate(_OHLC) if float(a[i]) != float(b[i])]
        vol  = abs(float(a[4]) - float(b[4])) > vol_tol
        return {'ohlc': ohlc, 'vol': vol, 'ok': not ohlc and not vol}
    return {'official_vs_audit': cmp(official, audit),
            'official_vs_kc':    cmp(official, kc)}


def _iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%H:%M:%S')


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════════════════════
class KlineAuditor:
    """Polls the developing 1m bar every 1s, rebuilds 5s bars (mirroring BarBuilder),
    and validates kline_collection at the 5s and 1m tiers. Phase 1: record + ERROR-log.
    Permanent, fully isolated service (its own systemd unit) — it must survive the
    collector dying, since catching exactly that is its job."""

    _BAR_S        = 5
    _MIN_MS       = 60_000
    _AUDIT        = 'kline_audit'
    _CONFIG       = 'kline_audit_config'
    _PRUNE_DAYS   = 7
    _GC_KEEP_MIN  = 5            # keep this many recent minutes of audit-5s/min-v state

    def __init__(self, db: DatabaseManager) -> None:
        self._db     = db
        self._client = BybitKlineClient()
        self._log    = get_logger(self.__class__.__name__)
        self._log.setLevel('INFO')
        logging.getLogger('BybitKlineClient').setLevel('WARNING')   # quiet the 1/s poll chatter
        self._vol_tol     = 0.0
        self._grace_s     = 3
        self._last_prune  = time.time()

    # ── lifecycle ───────────────────────────────────────────────────────────
    def run(self, tp_pk: int, symbol: str) -> None:
        self._ensure_schema()
        self._vol_tol, self._grace_s = self._load_config()
        self._log.info(f'kline auditor started: {symbol} (vol_tol={self._vol_tol}, '
                       f'm1_grace={self._grace_s}s)')
        bar_ms = self._BAR_S * 1000
        prior_close = None
        cur_win, samples = None, []
        audit_5s, min_v, done_min = {}, {}, set()

        while True:
            try:
                self._sleep_to_next_second()
                dev = self._poll_developing(symbol)
                if dev is None:
                    continue
                bar_start, _o, _h, _l, price, cum_v = dev
                now = int(time.time() * 1000)
                min_v[bar_start] = cum_v                       # the developing minute's running total
                w = (now // bar_ms) * bar_ms
                if cur_win is None:
                    cur_win = w
                if w != cur_win:                               # a 5s window closed
                    bar = build_5s_bar(prior_close, samples)
                    if bar is not None:
                        self._flush_5s(tp_pk, cur_win, bar)
                        prior_close = bar[3]
                        audit_5s[cur_win] = bar
                    samples, cur_win = [], w
                samples.append(price)

                # reconcile a fully-closed minute (>= grace into the next one)
                cur_min = (now // self._MIN_MS) * self._MIN_MS
                ready   = cur_min - self._MIN_MS
                if (now - cur_min) >= self._grace_s * 1000 and ready in min_v and ready not in done_min:
                    self._reconcile_1m(tp_pk, symbol, ready, audit_5s, min_v.get(ready))
                    done_min.add(ready)
                    self._gc(ready, audit_5s, min_v, done_min)

                self._maybe_prune(tp_pk)
            except Exception as e:                              # never let the permanent loop die
                self._log.error(f'loop error: {e}')
                time.sleep(1.0)

    def _sleep_to_next_second(self) -> None:
        now = time.time()
        time.sleep(max(0.0, math.ceil(now) - now))

    # ── polling ─────────────────────────────────────────────────────────────
    def _poll_developing(self, symbol: str):
        """Latest 1m bar (the developing one) → (bar_start_ms, o, h, l, c, v)."""
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
        """The official CLOSED 1m bar for `minute_start` → (o, h, l, c, v) or None."""
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

    # ── tiers ───────────────────────────────────────────────────────────────
    def _flush_5s(self, tp_pk: int, win_start: int, audit_bar) -> None:
        kc = self._kc_5s(tp_pk, win_start)
        r  = compare_5s(kc, audit_bar)
        self._record(tp_pk, win_start, '5s', r['verdict'], kc, audit_bar, None, ','.join(r['fields']))
        if r['verdict'] in ('mismatch', 'missing'):
            self._log.error(f"5s {r['verdict']} @ {_iso(win_start)}: "
                            f"kc={kc} audit={audit_bar} fields={r['fields']}")

    def _reconcile_1m(self, tp_pk: int, symbol: str, minute_start: int, audit_5s: dict, audit_v) -> None:
        n      = self._MIN_MS // (self._BAR_S * 1000)                    # 12 bars/minute
        wins   = [minute_start + i * self._BAR_S * 1000 for i in range(n)]
        abars  = [audit_5s[w] for w in wins if w in audit_5s]
        kcbars = self._kc_minute(tp_pk, minute_start)
        official = self._official_1m(symbol, minute_start)
        if official is None or len(abars) < n or len(kcbars) < n:
            self._record(tp_pk, minute_start, '1m', 'incomplete', None, None, official,
                         f'audit={len(abars)}/{n} kc={len(kcbars)}/{n} official={official is not None}')
            self._log.error(f'1m incomplete @ {_iso(minute_start)}: audit {len(abars)}/{n}, '
                            f'kc {len(kcbars)}/{n}, official={official is not None}')
            return
        a_ohlc  = aggregate_1m([(b[0], b[1], b[2], b[3], 0.0) for b in abars])     # OHLC; v from below
        audit_1m = (a_ohlc[0], a_ohlc[1], a_ohlc[2], a_ohlc[3], float(audit_v or 0.0))
        kc_1m    = aggregate_1m(kcbars)
        r  = reconcile_1m(official, audit_1m, kc_1m, self._vol_tol)
        ok = r['official_vs_audit']['ok'] and r['official_vs_kc']['ok']
        detail = (f"off_vs_audit:{self._pair(r['official_vs_audit'])} | "
                  f"off_vs_kc:{self._pair(r['official_vs_kc'])}")
        self._record(tp_pk, minute_start, '1m', 'ok' if ok else 'mismatch', kc_1m, audit_1m, official, detail)
        if not ok:
            self._log.error(f'1m mismatch @ {_iso(minute_start)}: official={official} '
                            f'audit={audit_1m} kc={kc_1m} | {detail}')

    @staticmethod
    def _pair(p: dict) -> str:
        bits = list(p['ohlc']) + (['vol'] if p['vol'] else [])
        return 'ok' if not bits else ','.join(bits)

    # ── persistence ─────────────────────────────────────────────────────────
    def _record(self, tp_pk, ts, tier, verdict, kc, audit, official, detail) -> None:
        def u(t):                                              # → [o,h,l,c,v] padded with None
            return (list(t) + [None] * 5)[:5] if t else [None] * 5
        kco, ao, oo = u(kc), u(audit), u(official)
        self._db.execute(
            f'''INSERT INTO {self._AUDIT}
                   (ka_tp_pk, ka_timestamp, ka_tier, ka_verdict, ka_detail,
                    ka_kc_open, ka_kc_high, ka_kc_low, ka_kc_close, ka_kc_volume,
                    ka_audit_open, ka_audit_high, ka_audit_low, ka_audit_close, ka_audit_volume,
                    ka_official_open, ka_official_high, ka_official_low, ka_official_close, ka_official_volume)
                VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE ka_verdict=VALUES(ka_verdict), ka_detail=VALUES(ka_detail),
                    ka_kc_close=VALUES(ka_kc_close), ka_audit_close=VALUES(ka_audit_close),
                    ka_official_close=VALUES(ka_official_close)''',
            (tp_pk, ts, tier, verdict, detail,
             *kco, *ao, *oo))

    def _ensure_schema(self) -> None:
        self._db.execute(f'''CREATE TABLE IF NOT EXISTS {self._AUDIT} (
            ka_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
            ka_tp_pk INT, ka_timestamp BIGINT, ka_tier VARCHAR(4), ka_verdict VARCHAR(16),
            ka_detail VARCHAR(255), ka_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            ka_kc_open FLOAT, ka_kc_high FLOAT, ka_kc_low FLOAT, ka_kc_close FLOAT, ka_kc_volume FLOAT,
            ka_audit_open FLOAT, ka_audit_high FLOAT, ka_audit_low FLOAT, ka_audit_close FLOAT, ka_audit_volume FLOAT,
            ka_official_open FLOAT, ka_official_high FLOAT, ka_official_low FLOAT, ka_official_close FLOAT, ka_official_volume FLOAT,
            UNIQUE KEY uq_audit (ka_tp_pk, ka_timestamp, ka_tier))''')

    def _load_config(self):
        """kline_audit_config — dialable knobs (config-tables discipline). Seeds a
        default active row if empty. Returns (volume_tolerance, m1_grace_s)."""
        self._db.execute(f'''CREATE TABLE IF NOT EXISTS {self._CONFIG} (
            kac_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
            kac_label VARCHAR(80) DEFAULT '', kac_is_active TINYINT DEFAULT 0,
            kac_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            kac_volume_tolerance FLOAT DEFAULT 0.0,
            kac_m1_grace_s INT DEFAULT 3)''')
        sel = f'SELECT * FROM {self._CONFIG} WHERE kac_is_active=1 ORDER BY kac_pk DESC LIMIT 1'
        rows = self._db.execute(sel, fetch=True)
        if not rows:
            self._db.execute(f"INSERT INTO {self._CONFIG} (kac_label, kac_is_active) VALUES ('default', 1)")
            rows = self._db.execute(sel, fetch=True)
        r = rows[0]
        return float(r['kac_volume_tolerance']), int(r['kac_m1_grace_s'])

    # ── housekeeping ────────────────────────────────────────────────────────
    def _gc(self, ready_min: int, audit_5s: dict, min_v: dict, done_min: set) -> None:
        keep = ready_min - self._GC_KEEP_MIN * self._MIN_MS
        for d in (audit_5s, min_v):
            for k in [k for k in d if k < keep]:
                del d[k]
        for m in [m for m in done_min if m < keep]:
            done_min.discard(m)

    def _maybe_prune(self, tp_pk: int) -> None:
        now = time.time()
        if now - self._last_prune < 3600:
            return
        cutoff = int((datetime.now(timezone.utc) - timedelta(days=self._PRUNE_DAYS)).timestamp() * 1000)
        self._db.execute(f'DELETE FROM {self._AUDIT} WHERE ka_tp_pk=%s AND ka_timestamp < %s', (tp_pk, cutoff))
        self._last_prune = now
