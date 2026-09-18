# o9-live × sneaky-trade-1 — preflight measurements, 2026-09-17

Written before any code was changed. Nothing in the repo was edited to produce this.
Every figure below was produced by re-walking the tape with the SAME modules
`build_sneaky_trade_1.py` uses, from the same line cache (`END_MS` 2026-09-08, `HOURS` 40,
`WARMUP` 1114).

**Fidelity check first.** The re-walk reproduces the banked table exactly: 255 taken rows,
+1,995.12 USDT unstaggered / +1,984.76 staggered, +7.78 per trade, 52.2% wins. So the walk
below is the same walk, not an approximation of it.

---

## 1. KLINE COMPLETENESS — what already exists

| module | what it does | does it answer "is span [t0,t1] complete" |
|---|---|---|
| `optimus9/data/kline_auditor.py` | live service. Polls Bybit REST 1 s, rebuilds 5 s bars, records per-field tick variance vs `kline_collection` at a 5 s liveness tier and a 1 m tick-exact tier. Writes `kline_audit`, prunes at 7 days | NO. It is a forward-running service; it can only report spans it was running across, and its record reaches back 7 days |
| `optimus9/data/synthetic_backfiller.py` | 1 m → 12 × 5 s split. SUNSET Joe 2026-07-05, auto-backfill DISABLED | NO. `_gap_start` = `MAX(kc_timestamp)` — the tail only |
| `optimus9/data/binance_backfiller.py` | Binance Spot gap fill, "kept for non-futures pairs" | NO. Same `_gap_start` tail-only shape |
| `optimus9/data/kline_sanitiser.py` | overwrites OHLC from a TradingView CSV dropped in `./transfer/kline_sanitise/` | NO. Manual, CSV-scoped |
| `ops/o9_healthcheck.py` | flags `MAX(kc_timestamp)` older than 30 s | NO. Staleness, not span completeness |

**Nothing in the repo queries `kline_collection` for interior gaps over an arbitrary span.**

The auditor's pure core IS reusable: `build_5s_bar`, `aggregate_1m`, `tick_variance`,
`is_frozen` are module-level, dependency-free and tested by `tests/test_kline_auditor.py`.

### measured now, 2026-09-17 00:42 UTC

| measurement | value |
|---|---|
| `kline_collection` rows, `kc_tp_pk` 1 (FARTCOINUSDT) | 2,298,744 |
| span | 2026-05-07 00:00:00 → 2026-09-17 00:41:55 |
| rows expected at the 5 s grid over that span | 2,298,744 |
| missing rows | 0 |
| last 14 days: rows | 241,919 |
| last 14 days: steps that are not exactly 5,000 ms | 0 |
| last 14 days: rows with `kc_volume` = 0 (carry-forward filler) | 63,724 = 26.34% |
| `optimus9_system.filler_invisible` | 1 — volume-0 bars are already invisible to the lines |

### what the auditor recorded over its own 7-day window

| tier | verdict | n | first | last |
|---|---|---|---|---|
| 1m | match | 9,977 | 2026-09-09 23:52 | 2026-09-17 00:40 |
| 1m | variance (our tape ≠ the exchange) | 32 | 2026-09-10 14:42 | 2026-09-15 16:12 |
| 1m | incomplete | 5 | 2026-09-11 21:51 | 2026-09-15 05:51 |
| 5s | live | 119,768 | 2026-09-09 23:51:45 | 2026-09-17 00:41:55 |
| 5s | frozen | 391 | 2026-09-10 03:14:50 | 2026-09-16 23:12:50 |
| 5s | missing | 1 | 2026-09-11 21:51:10 | 2026-09-11 21:51:10 |

Three candidate meanings of "complete" give three different verdicts on the same tape.
Which one gates the warm-up is Joe's call — see §4.

---

## 2. THE HALT — the banked 255 is selected by events that happen AFTER the entry

The producer searches in this order: the carrying line's test-point `mx` → the fence exit `fx`
→ the close `eb` → and ONLY THEN the open `ob`. A row exists only when all four land before the
dr flip. A live loop reaches the open bar first and cannot know the rest.

### census over the banked window 2026-06-10 → 2026-09-04

| step | n |
|---|---|
| test-points reaching the producer | 5,761 |
| gate passes at the test-point (`drop` ≥ 50, `src` ws1 or ws2, `hi` == ws4) | 862 |
| dropped: ws4 produced no test-point of its own in the dr stretch (`mx` is None) | 511 |
| of those 511, an ws1x crossing DID fire → live would have opened | 491 |
| survived to the producer | 351 |
| dropped: ws4r never crossed 17/83 before the dr flip | 4 |
| dropped: no gcws30mage-rev before the dr flip | 20 |
| dropped: no ws1x crossing before the dr flip | 0 |
| dropped: the ws1x crossing landed at or after the close | 72 |
| **banked rows** | **255** |

### where the carrying line lands, relative to the entry

| measurement | n of 255 |
|---|---|
| ws4's own test-point at or before the open bar | 8 |
| the fence exit at or before the open bar | 8 |
| the open bar is EARLIER than ws4's own test-point | 247 |

Lag from the sourcing test-point to ws4's test-point, over the 247 banked rows where ws4's
test-point is later: p50 15.8 min, p90 61.7 min, max 125.2 min.

### what a causal loop actually opens

Identical mechanics, causal ordering only: gate at the test-point → open at the first ws1x
crossing → arm the exit when ws4's fence exit lands → close at the first rev → else the dr flip
closes it with an EXIT order (Joe 0917).

22,000 coins, 0.55% drag.

| population | opens | total USDT | per trade | wins |
|---|---|---|---|---|
| banked table (the plan) | 255 | +1,984.76 | +7.78 | 52.2% |
| causal loop, every gate-passing crossing | 770 | −12,897.76 | −16.75 | 19.0% |
| — of those, the 255 banked rows | 255 | +1,995.12 | +7.82 | 52.2% |
| — of those, with no banked row | 515 | −14,892.88 | −28.92 | 2.5% |
| causal loop, wait for ws4's test-point before opening | 10 | −77.26 | −7.73 | 20.0% |
| causal loop, wait for the fence exit before opening | 10 | −77.26 | −7.73 | 20.0% |

MAE and MFE read pxs at EVERY 5 s bar, in the dr direction:

| population | n | MAE% med | MFE% med | MFE/MAE med | hold med |
|---|---|---|---|---|---|
| banked rows | 255 | 0.119 | 0.818 | 5.85 | 17.2 min |
| causal opens with no banked row | 515 | 0.409 | 0.230 | 0.57 | 26.8 min |
| — of those, ws4 had no test-point in the stretch | 491 | 0.409 | 0.229 | 0.55 | 27.0 min |
| — of those, ws4 had one, no fence exit or no rev | 24 | 0.407 | 0.360 | 0.75 | 24.3 min |
| every causal open | 770 | 0.315 | 0.368 | 1.14 | 22.5 min |

Opens per day over 87 days: banked 2.93, causal 8.85, causal with no banked row 5.92.

Joe's pyramid limit of 2 concurrent never binds: 0 refusals at 770 opens, and max 2 concurrent
on the banked 255 (191 opens land flat, 64 land alongside one other).

### the 30 s reconciliation contract, run against the causal open set

| contract line | result |
|---|---|
| live ENTRY fills | 770 |
| ENTRY fills matching a taken signal inside 30 s | 255 |
| ENTRY fills that are EXTRA | 515 |
| taken signals with no ENTRY fill inside 30 s (MISS) | 0 of 255 |
| live EXIT fills | 770 |
| EXIT fills matching a taken signal inside 30 s | 255 |
| EXIT fills that are EXTRA | 515 |
| taken signals with no EXIT fill inside 30 s (MISS) | 0 of 255 |
| EXTRA share of entry fills | 66.9% |
| EXTRA entry fills per day | 5.92 |

### the stagger population, banked vs causal

| measurement | banked 255 | causal 770 |
|---|---|---|
| opens | 255 | 770 |
| distinct open bars | 216 | 669 |
| open bars carrying exactly 1 open | 177 | 568 |
| open bars carrying exactly 2 opens | 39 | 101 |
| open bars carrying 3 or more | 0 | 0 |
| median gap between consecutive distinct open bars | 22,805 s | 8,447.5 s |
| distinct open bars with another inside 5 s | 0 of 216 | 0 of 669 |
| distinct open bars with another inside 15 s | 0 of 216 | 0 of 669 |
| distinct open bars with another inside 30 s | 1 of 216 | 1 of 669 |
| distinct open bars with another inside 60 s | 1 of 216 | 2 of 669 |
| `st1_slot` on the taken rows in the db | 216 at slot 0, 39 at slot 1 | — |
| handover §8 line-3 query run literally on the db table | 0 | — |

### the alternative reading of where the fence-exit search starts

Handover §3 step 4 and spec §17.1 say "the carrying line's r crosses beyond 17/83 on the dr
side" and do not state that the search starts at the carrying line's own test-point. Starting it
at the SOURCING test-point instead removes the `mx` dependency:

| rule | opens | total USDT | per trade | wins |
|---|---|---|---|---|
| fence exit searched from the sourcing test-point, backtest-ordered | 300 | −1,142.56 | −3.81 | 24.7% |
| the same, causal loop | 564 | −9,479.27 | −16.81 | 13.7% |

---

## 3. THE 24 OPENS THAT GET NO CLOSE SIGNAL

Subset of the 515: the gate passed, ws4 DID produce a test-point, the crossing fired, and then
either ws4r never crossed 17/83 (4 cases) or no rev landed (20 cases) before the dr flip. Closed
by the dr flip with an EXIT order.

| measurement | value |
|---|---|
| n | 24 |
| total | −798.47 USDT |
| per trade | −33.27 |
| wins | 0 = 0.0% |
| MAE% median | 0.407 |
| MFE% median | 0.360 |
| MFE/MAE median | 0.75 |
| hold median | 24.3 min |

---

## 4. CONCRETIONS THAT ARE NOT IN THE HANDOVER OR THE SPEC

| # | concretion | why it is not decidable from what is written |
|---|---|---|
| 1 | what "the klines are complete" means | rows present at the 5 s grid (0 gaps), real-trade bars (26.34% are filler), or tape == exchange (32 variance minutes in 7 days) |
| 2 | the warm-up span the gate covers | the line cache uses `WARMUP` 1114 h because it floors on the kline start, not because it is a minimum. Unmeasured |
| 3 | the entry rule a causal loop uses | §2 above |
| 4 | the duplicate count the reconciler reports | the handover §8 query returns 0 against the banked table, because the stagger already moved the second order's bars. The number Joe quoted, 39, is the PRE-stagger count and `st1_slot` carries it |

---

## 5. RUNNING STATE

| process | state |
|---|---|
| collector (`run.py supervisor`) | running, tape current to the second |
| `run.py kline_audit` | running |
| `kline_sanitise_service.py` | running |
| fakeAPI (`uvicorn services.fakeapi.app:app`) | NOT running |
| `ops/run_o9live.py` | NOT running |
