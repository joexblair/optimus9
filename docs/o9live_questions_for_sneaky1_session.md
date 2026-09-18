# o9-live → sneaky-trade-1 session: questions, with the measurements behind them

**Written 2026-09-17 by the o9-live session.** Joe's routing: *"we have validated reports in the
other session — I think that's the best way to help you. put your notes into a new doc and I'll
ask the other session to give you the answers"*.

**What this session was asked to do.** Replace o9-live's strategy loop with sneaky-trade-1, run it
against the fake Bybit API, and stand up an hourly reconciliation of live fills against the
backtest. Four items: a kline completeness gate before warm-up, the loop replacement, the stagger,
and the hourly reconciliation.

**Where it stopped.** Before writing any code. Nothing in the repo has been edited except this doc
and `docs/o9live_sneaky1_preflight.md`. No table, config row or module has been touched.

**What is needed back.** Answers to Q1–Q8 in §3. Q1 is the blocker; the other three items are
buildable once it is settled.

---

## 1. HOW THE NUMBERS BELOW WERE PRODUCED

One script, one run, re-walking the tape with the SAME modules `build_sneaky_trade_1.py` uses,
from the same line cache: `END_MS` 2026-09-08 00:00 UTC, `HOURS` 40, `WARMUP` 1114, tape
1,632,960 bars at the 5 s grid.

Same knobs: `momo_fence_r` 17 → fence (17.0, 83.0) · `tp_lookback_min` 4 min = 48 bars ·
`MAGE_DWELL` 6 bars = 30 s · Mage fence 25/75 · oob 15/85 · `handoff.ride_tf_hi` 4 ·
`TFS` [1,2,3,4] · gate `drop` ≥ 50, `src` in (ws1, ws2), `hi` == ws4 · 22,000 coins fixed ·
0.55% drag round trip · window 2026-06-10 → 2026-09-05.

**Fidelity check.** The walk reproduces the banked table exactly. If any row below is wrong, it is
wrong for a reason other than the walk drifting:

| measurement | value |
|---|---|
| `sneaky_trade_1` rows in the db | 1,772 |
| of them taken (`st1_taken` = 1) | 255 |
| banked rows this walk reproduced | 255 |
| this walk, unstaggered | +1,995.12 USDT, +7.82 per trade, 52.2% wins |
| the db table, staggered | +1,984.76 USDT, +7.78 per trade, 52.2% wins |
| the handover's staggered figure | +1,984.77 USDT, +7.78 per trade, 52.2% wins |

---

## 2. THE MEASUREMENTS — please confirm or correct each against the validated reports

### 2a. the census, over 2026-06-10 → 2026-09-04

| step | n |
|---|---|
| test-points reaching the producer | 5,761 |
| gate passes at the test-point (`drop` ≥ 50, `src` ws1 or ws2, `hi` == ws4) | 862 |
| dropped: ws4 produced no test-point of its own in the dr stretch (`mx` is None) | 511 |
| — of those, an ws1x crossing DID fire inside the stretch | 491 |
| dropped: ws4r never crossed 17/83 before the dr flip (`fx` is None) | 4 |
| dropped: no gcws30mage-rev before the dr flip (`eb` is None) | 20 |
| dropped: no ws1x crossing before the dr flip (`ob` is None) | 0 |
| dropped: the ws1x crossing landed at or after the close (`ob` ≥ `eb`) | 72 |
| BANKED ROWS | 255 |

### 2b. where each condition resolves, relative to the open bar

| condition | at or before the open bar |
|---|---|
| the dr stretch (the latch change) | 255 of 255 |
| the test-point | 255 of 255 |
| the ladder `hi`, read at the test-point | 255 of 255 |
| the gate (`drop`, `src`, `hi`), read at the test-point | 255 of 255 |
| `mx` — ws4 produced a test-point in this stretch | 8 of 255 |
| `fx` — ws4r crossed 17/83 | 8 of 255 |
| `eb` — a gcws30mage-rev landed before the dr flip | 0 of 255 |

- the open bar is EARLIER than ws4's own test-point in 247 of 255 rows.
- lag from the sourcing test-point to ws4's test-point, over those 247: p50 15.8 min, p90 61.7
  min, max 125.2 min.
- `eb` is 0 of 255 by construction — a row requires `ob` < `eb`.

### 2c. what a causal loop opens

Rule priced: gate at the test-point → open at the first ws1x crossing → arm the exit when ws4's
fence exit lands → close at the first rev at or after it → else the dr flip closes the position
with an EXIT order (Joe 0917). 22,000 coins, 0.55% drag, 87 days.

| population | opens | total USDT | per trade | wins |
|---|---|---|---|---|
| banked table (the plan), staggered | 255 | +1,984.76 | +7.78 | 52.2% |
| causal loop, every gate-passing crossing | 770 | −12,897.76 | −16.75 | 19.0% |
| — of those, the banked rows | 255 | +1,995.12 | +7.82 | 52.2% |
| — of those, with no banked row | 515 | −14,892.88 | −28.92 | 2.5% |
| causal loop, wait for ws4's test-point before opening | 10 | −77.26 | −7.73 | 20.0% |
| causal loop, wait for the fence exit before opening | 10 | −77.26 | −7.73 | 20.0% |

- opens per day over 87 days: banked 2.93, causal 8.85, causal with no banked row 5.92.

MAE and MFE read pxs at EVERY 5 s bar, in the dr direction:

| population | n | MAE% med | MFE% med | MFE/MAE med | hold med |
|---|---|---|---|---|---|
| banked rows | 255 | 0.119 | 0.818 | 5.85 | 17.2 min |
| causal opens with no banked row | 515 | 0.409 | 0.230 | 0.57 | 26.8 min |
| — ws4 had no test-point in the stretch | 491 | 0.409 | 0.229 | 0.55 | 27.0 min |
| — ws4 had one, no fence exit or no rev | 24 | 0.407 | 0.360 | 0.75 | 24.3 min |
| every causal open | 770 | 0.315 | 0.368 | 1.14 | 22.5 min |

- Joe's pyramid limit of 2 concurrent refuses 0 opens at 770. Max concurrent on the banked 255 is
  2: 191 opens land flat, 64 land alongside one other.

### 2d. the stagger population

| measurement | banked | causal |
|---|---|---|
| opens | 255 | 770 |
| distinct open bars | 216 | 669 |
| open bars carrying exactly 1 open | 177 | 568 |
| open bars carrying exactly 2 opens | 39 | 101 |
| open bars carrying 3 or more | 0 | 0 |
| median gap between consecutive distinct open bars | 22,805.0 s | 8,447.5 s |
| distinct open bars with another inside 5 s | 0 of 216 | 0 of 669 |
| distinct open bars with another inside 15 s | 0 of 216 | 0 of 669 |
| distinct open bars with another inside 30 s | 1 of 216 | 1 of 669 |
| distinct open bars with another inside 60 s | 1 of 216 | 2 of 669 |

- `st1_slot` on the taken rows in the db: 216 at slot 0, 39 at slot 1.
- the handover §8 line-3 query, run literally against `sneaky_trade_1`, returns **0** groups.

### 2e. the 30 s contract, run against the causal open set

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

### 2f. the kline tape, measured 2026-09-17 00:42 UTC

| measurement | value |
|---|---|
| `kline_collection` rows, `kc_tp_pk` 1 (FARTCOINUSDT) | 2,298,744 |
| span | 2026-05-07 00:00:00 → 2026-09-17 00:41:55 |
| rows expected at the 5 s grid over that span | 2,298,744 |
| missing rows | 0 |
| last 14 days: rows | 241,919 |
| last 14 days: steps not exactly 5,000 ms | 0 |
| last 14 days: rows with `kc_volume` = 0 (carry-forward filler) | 63,724 = 26.34% |
| `optimus9_system.filler_invisible` | 1 |

`kline_audit`, the auditor's own 7-day record:

| tier | verdict | n | first | last |
|---|---|---|---|---|
| 1m | match | 9,977 | 2026-09-09 23:52 | 2026-09-17 00:40 |
| 1m | variance (our tape ≠ the exchange) | 32 | 2026-09-10 14:42 | 2026-09-15 16:12 |
| 1m | incomplete | 5 | 2026-09-11 21:51 | 2026-09-15 05:51 |
| 5s | live | 119,768 | 2026-09-09 23:51:45 | 2026-09-17 00:41:55 |
| 5s | frozen | 391 | 2026-09-10 03:14:50 | 2026-09-16 23:12:50 |
| 5s | missing | 1 | 2026-09-11 21:51:10 | 2026-09-11 21:51:10 |

---

## 3. THE QUESTIONS

### Q1 — THE ENTRY RULE. What does the live loop do at a gate-passing ws1x crossing? **BLOCKER**

`sneaky_trade_1.signal()` computes in this order:

```
fx = fence_exit(r_hi_line, dr, mx, fence, flip)     # 1
if fx is None: return None
eb = close_bar(rev_bars, fx, flip)                  # 2
if eb is None: return None
ob = open_bar(x_line, dr, tp, eb, oob_lo, oob_hi)   # 3
```

`ob` is computed last and happens first on the tape. A live loop standing on the open bar has
`fx` in 8 of 255 rows, `mx` in 8 of 255, and `eb` in 0 of 255 (§2b).

- opening on every gate-passing crossing gives 770 opens at −16.75 per trade (§2c).
- waiting for ws4's test-point, or for the fence exit, gives 10 opens at −7.73 (§2c).
- the banked 255 and the 515 with no banked row separate in the excursion — MFE/MAE median 5.85
  against 0.57 — but that is read over the whole hold, not at the entry bar.

**What is needed:** the rule a live loop applies standing on the crossing bar, using only bars at
or before it. If the validated reports already contain it, quoting it is enough.

### Q2 — is `mx` Joe's rule or the builder's choice?

`build_sneaky_trade_1.py` starts the fence-exit search at `mx` = the carrying line ws4's OWN
test-point bar, and drops the candidate entirely when ws4 produced no test-point in that dr
stretch. That drop removes 511 of 862 gate-passing candidates (§2a) — larger than any of the
three named gate tests.

Handover §3 step 4 and spec §17.1 say *"the carrying line's r crosses beyond 17/83 on the dr
side"*. Neither states where the search starts. **This reading is mine and is flagged as mine.**

Priced, with the `mx` dependency removed and the fence exit searched from the SOURCING test-point:

| rule | opens | total USDT | per trade | wins |
|---|---|---|---|---|
| fence exit from the sourcing test-point, backtest-ordered | 300 | −1,142.56 | −3.81 | 24.7% |
| the same, causal loop | 564 | −9,479.27 | −16.81 | 13.7% |

**What is needed:** is starting the fence-exit search at the carrying line's own test-point a rule
Joe stated, or an implementation choice? And is "ws4 produced no test-point in this stretch" meant
to end the candidate?

### Q3 — what does "the klines are complete" mean?

Three readings, three verdicts on the same tape (§2f):

| reading | verdict now |
|---|---|
| every 5 s row present | 0 missing over 2026-05-07 → 2026-09-17 |
| every bar carries a real trade | 26.34% of the last 14 days are `kc_volume` = 0 filler |
| the tape equals the exchange | 32 variance minutes and 391 frozen 5 s bars in 7 days |

`filler_invisible` = 1 already hides `kc_volume` = 0 bars from the lines, which bears on the
second reading.

**What is needed:** which reading gates the warm-up.

### Q4 — what warm-up span must be complete?

The line cache uses `WARMUP` 1114 h because it floors exactly on the kline_collection start, not
because it is a measured minimum. I have not measured a minimum.

Measured spans that bear on it, over the banked window:

| measurement | value |
|---|---|
| dr stretch length, p50 | 30.9 min |
| dr stretch length, p90 | 91.7 min |
| dr stretch length, p99 | 168.2 min |
| dr stretch length, max | 294.5 min = 4.91 h |
| open bar back to its own dr-stretch start, p50 | 9.2 min |
| open bar back to its own dr-stretch start, p99 | 61.8 min |
| open bar back to its own dr-stretch start, max | 68.1 min = 1.13 h |

Those cover the walk. They do not cover the warm-up of ws1..ws12 r/Mage, ws1x, ws13m and
gcws30Mage themselves.

**What is needed:** the span, or the measurement that sets it.

### Q5 — the duplicate count, reconciliation contract line 3

Handover §8: *"REPORT, every run: the number of taken signals sharing an identical open AND close
bar"*, with 39 of 255 quoted. Run literally against `sneaky_trade_1` it returns **0** groups,
because the stagger already moved the second order's open and close bars by one 5 s bar. The 39
is carried by `st1_slot` = 1 (§2d).

**What is needed:** confirm the reconciler reports the pre-stagger count — reconstructed as
(`st1_open_bar` − `st1_slot`, `st1_close_bar` − `st1_slot`), or equivalently the `st1_slot` > 0
count — and not the literal query.

### Q6 — the stagger population under a live entry rule

The stagger's shape and ordering both survive a causal loop: still always exactly two, never
three, and the second order is the one whose test-point came later, which is decidable on the
shared open bar. The population does not: 39 pairs becomes 101 (§2d).

**What is needed:** nothing, if Q1 settles the entry rule. Recorded so the count is not read as a
break when it lands.

### Q7 — the concurrency limit

`handoff.ride_tf_hi` 4 and the pyramid limit 2 are banked. The limit refuses 0 of 770 opens, and
max concurrent on the banked 255 is 2 (§2c).

**What is needed:** confirm that at a larger open population the limit is still 2, and that a
third concurrent open is refused rather than queued.

### Q8 — the collision cost on a staggered pair

Joe's brief: the stagger costs −10.34 USDT over 87 days in price drift, the collision it avoids is
not in the 0.55% drag, and it pays for itself above 0.27 USDT per pair. To be measured once fills
exist.

**What is needed:** the definition to measure it against — what counts as the collision, and which
two fills are compared.

---

## 4. WHAT THIS SESSION HAS NOT MEASURED

| item | note |
|---|---|
| the minimum warm-up for ws1..ws13 and gcws30 | see Q4 |
| the cost of building the wsf line set on a window ending at now, per 5 s bar | the live loop's cadence depends on it |
| the leverage setting on the fake API | handover §8b: ~6.2x for one position, ~12.5x for two |
| Joe's eyes on sneaky-trade-1 | `eyes_on_pine` holds 0 rows for this mechanic |

---

## 5. STATE

| item | state |
|---|---|
| repo changes | none, beyond this doc and `docs/o9live_sneaky1_preflight.md` |
| `sneaky_trade_1` table | untouched, 1,772 rows, 255 taken |
| `wsf_dtf_v3_config` | untouched |
| collector (`run.py supervisor`) | running, tape current to the second |
| `run.py kline_audit` | running |
| `kline_sanitise_service.py` | running |
| fakeAPI (`uvicorn services.fakeapi.app:app`) | not running |
| `ops/run_o9live.py` | not running |
