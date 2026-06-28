# o9-live — live forward-test design (sketch, 0628)

Status: DESIGN / riffing. Interrogate before building. Edge being forward-tested: the cf15 latch-release
cascade, validated 8-window (see memory `project-cascade-edge`).

## Purpose
- Forward-test the validated cf15 edge on **real live data, in realtime, with modeled fills + zero capital risk**.
- Bybit test/demo are unusable: testnet flaky + provisioning-blocked; **demo prints test-env prices** (corrupted by test users — a test user dumping 600k FARTCOIN moves the test book). So we build our own exchange, fed by Bybit's **real `publicTrade` feed**. Real prices + modeled fills + no risk is the only combination that exists.
- Proves: plumbing · realtime decisions == backtest · out-of-sample edge · a real (book-walk) cost model. Does NOT prove true fill economics until real money — it's the last gate before that.

## Phasing
- **Phase 1 — LOCAL (WSL):** both containers + a new o9-live DB on WSL MySQL. Prove the whole stack before a dollar of cloud.
- **Phase 2 — LINODE (Singapore = Bybit's AWS `ap-southeast-1`):** same images; DB → Linode Managed MySQL. The DB seam stays clean → migration is a connection-string + compose change, no code.

## Architecture — 3 responsibilities, 2 containers
```
Bybit public WS ─┐
   (real tape)   ▼
        ┌───────────────── o9-live container ─────────────────┐        ┌──── fake-API container ────┐
        │ 1a collector: publicTrade → 5s bars  ─► live DB      │        │ Bybit v5 contract (mock)    │
        │ 1b loop(5s): BiasWindow(now)→W.line→cf15 cascade ─►  │  HTTP  │ book-walk fills + fees      │
        │ 1c trade-machine adapter (abstract; Bybit=1 impl) ──┼───────►│ position/order/fill store   │
        └─────────────────────────────────────────────────────┘        └─────────────────────────────┘
                              ▲ shared DB (WSL MySQL → later Managed) ▲   ◄── orderbook WS (real depth)
```

## Container 1 — o9-live
**1a. Tick collector (SRP: ingest).** One long-lived WS to `publicTrade.FARTCOINUSDT` (real matched-trade tape). Bucket trades to 5s OHLCV off trade-time (not wall-clock); gap-bars emitted + flagged synthetic; **last-message watchdog** (the frozen-tape lesson — a dead conn looks quiet). Writes ticks + 5s klines. *Bybit's min native candle is 1m → 5s MUST be tick-built; mandatory, not optional.*
- **A/B self-validation (POST fake-go-live):** once the system runs, compare the live 5s tape (Stream A) to the TV-sanitised tape (Stream B) over the same wall-clock → agreement confirms the live feed reproduces the validated tape; divergence flags a feed fault. Bonus: `publicTrade` carries no index wicks → surfaces non-tradeable wicks (#19).

**1b. The strategy (SRP: decide) — collector-triggered.** When the collector (1a) prints a 5s kline (the kline build IS the clock — no separate timer/loop) it triggers → a bounded `BiasWindow(now)` (BUFFER = longest line lookback + cascade horizon ≈ hours, NOT the 7-day backtest span) → `lr_detect(W, lr_params(db), s30r_lb_bars=resolve_s30r_lb(db, W))` → the latest-bar entry → an **intent** (`open/add/close`, 66k). The SAME `lr_detect` (optimus9/analysis/lr.py) runs in prod (strat_review cascade producer) + the backtest ⇒ **live == prod == backtest by construction**. Never touches the exchange. *(Derive BUFFER by tracing the longest-lookback line — the one measurement that matters.)*

**1c. Trade-machine adapter (SRP: execute) — decoupled from Bybit.** Takes the intent, translates to orders behind an **abstract interface**; Bybit-v5 is one impl, fake-API another. Thin `requests`/`websocket-client` wrapper (**not pybit** — it computes its own URL + hardcodes signing). Two seams only: **base-URL = ctor arg**, **signing = strategy object** (real HMAC live / pass-through mock). Swap URL → real Bybit, zero strategy change.
- Exit: **fill-on-signal** (strategy's exit trigger = the close order). Hard **SL = 0.5%** held server-side by the fake-API (fires on kline cross).

## Container 2 — fake-API (the exchange)
- **Mocks the Bybit v5 contract** so the adapter is a true drop-in: `POST /v5/order/create`, `POST /v5/position/trading-stop`, `GET /v5/position/list`, `GET /v5/execution/list`, `POST /v5/position/set-leverage`. Universal envelope, **string numerics (Decimal, not float)**, the real error codes (10002 ts, 10004 sign, 110043 leverage-unchanged…).
- **Fill model = walk the LIVE order book** (`orderbook` WS, subscribed here) for the position size → avg fill + slippage; apply **taker 5.5 bps**, per-leg (entry walk + exit walk). This captures the **real entry-condition cost** (thin book during reversals) — the headline the forward-test exists to measure. *No order-splitting* (data: 66k eats 4.7 bps into a 4.2M-coin book — nothing to save; splitting only buys timing risk against the reversal).
- **Auth:** emulate the HMAC recipe + recv_window/clock rule (so auth/clock bugs surface here, not prod); stub the key→account lookup.
- **Stores** every order, position (open/close, fill prices, slippage, fees, realized PnL) → (1) test o9-live's output, (2) confirm the edge in realtime.

## Slippage model (settled)
Live order-book walk at fill, per-leg. NOT flat, NOT volume-to-fill (rejected — biased toward "splitting wins" via a print-time artifact). Real cost validated on the live book: FARTCOIN spread **1.6 bps**, ~**0.20% RT all-in** at 66k — below the backtest's 0.31%, so the edge is *conservatively* costed. Caveat: that's a calm snapshot; reversal-entry books thin → the live walk measures the truth.

## Data / DB
- **Phase 1:** new o9-live DB on WSL MySQL.
- **COPIED (config/reference, from dev):** `indicator_configs`, `indicator_series`, `indicator_lines`, `indicator_timeframes`, `indicator_value_modes`, `lp_config`, `trade_gate`, `trade_gate_line`, + the `vw_indicator_configs_live` view DDL. (Add `bias_producer`/`bl_lines` only if BL becomes a live producer.)
- **GENERATED live (by collector):** `kline_collection`, `ticks`.
- **NEW (fake-exchange):** `fx_order`, `fx_position`, `fx_fill` + the o9-live decision log.

## What it proves (honest scope)
- **YES:** plumbing · realtime decisions == backtest · out-of-sample edge on unseen live data · a real book-walk cost model · the auth/clock/contract drop-in.
- **NO (until real money):** true fill economics — queue position, partial fills, funding, latency-to-match. Layer: fake-API (here) → real Bybit small-size (later).

## DECISIONS (resolved 0628)
1. **Warmup source** — copy the sanitised history (TV-true, on hand) to seed the buffer; collector appends live. *(Phase 1; Phase 2 may REST-backfill.)*
2. **Producer scope** — **cf15 cascade only** (the validated mechanic; no unvalidated producers).
3. **Position sizing** — **fixed 66k coins** (match the backtest; sizing is a later lever).
4. **Live recompute** — bounded-buffer `run_window` per 5s (see 1b); derive BUFFER from the longest-lookback line. Trivial once bounded.
5. **PYRAMIDING** — multiple cascade entries **accumulate into one same-side position** (Bybit one-way: size grows, avg-entry re-weights; exits reduce). Built this way from the start, not retrofitted.

## Build milestones (decompose)
1. Bybit v5 client wrapper (base-URL + signing seams) + fake-API contract skeleton (envelope, order/position/execution).
2. Tick collector (publicTrade → 5s bars).
3. Fake-API fill model (order-book walk + fees) + the pyramiding position store (`fx_*` per `o9_live_schema.sql`).
4. o9-live loop (bounded `BiasWindow` → `lr_detect` → intent → adapter).
5. Wire end-to-end locally (compose, WSL DB) + a live dry-run = **fake-go-live**.
6. A/B feed validation (live tape vs TV) — *post* fake-go-live.
7. Phase 2: Linode deploy (Singapore, GHCR, firewall/no-published-ports, chrony+sync-gate, autoheal, dead-man's-switch).
