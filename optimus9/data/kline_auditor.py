"""
kline_auditor — an independent REST cross-check of kline_collection. The "100% sure
of our OHLC" service.

WHY
  kline_collection is built by BarBuilder from the websocket tick stream. If that
  stream freezes (the 06-04 incident) or the tick→bar build is lossy, our tape drifts
  from the exchange and nothing notices. This service is a SECOND, INDEPENDENT data
  path — Bybit's REST kline API — that rebuilds the bars and validates them, so a
  divergence is caught the instant it happens.

HOW (verified live: the REST /v5/market/kline endpoint returns the DEVELOPING 1m bar
with a close that updates per trade — so "poll every second" reads the running price)
  Poll the developing 1m bar every 1s → the close is the price sample. Consume that 1s
  sample stream like the tick collector consumes ticks, building 5s bars the EXACT same
  way BarBuilder does — so a mismatch can only be the two Bybit paths (REST poll vs WS
  stream) genuinely disagreeing, never a construction difference.

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

This module's PURE CORE (bar construction + verdicts + 1m reconcile) is below and is
the testable heart; the polling service (KlineAuditor), the kline_audit table, and the
isolated worker land in the following slices. Spec/DoD lives in the behaviour-by-example
tests at tests/test_kline_auditor.py — no separate design doc (infra build; korero's
design-doc ritual is milestone-scoped).
"""

_OHLC = ('o', 'h', 'l', 'c')


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
