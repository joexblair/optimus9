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
**1a. Tick ingest (SRP: ingest) — REUSE the existing collector, do NOT rebuild.** `TickCollector` already
subscribes to Bybit's `publicTrade` WS → `ticks`; `bar_builder`/`kline_auditor` build the 5s klines →
`kline_collection` (the proven tape; L1 self-heal handles the frozen-tape failure). o9-live points the
*existing* collector + bar_builder at the o9-live DB and READS `kline_collection`. (Bybit's min native candle
is 1m, so 5s is tick-built — which this already does.) The earlier "build an in-container collector" was a
footwork miss (caught 0628).
- **A/B self-validation (POST fake-go-live, OPTIONAL):** Joe's idea — a 2nd fresh collector cross-checking
  the tape vs TV. May be **subsumed by the kline-sanitiser** (the live tape IS `kline_collection`, already
  TV-corrected). Re-examine before building. Bonus if kept: `publicTrade` has no index wicks → surfaces #19.

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
2. Point the EXISTING `TickCollector` + `bar_builder` at the o9-live DB (reuse — no rebuild).
3. Fake-API fill model (order-book walk + fees) + the pyramiding position store (`fx_*` per `o9_live_schema.sql`).
4. o9-live loop (bounded `BiasWindow` → `lr_detect` → intent → adapter).
5. Wire end-to-end locally (compose, WSL DB) + a live dry-run = **fake-go-live**.
6. A/B feed validation (live tape vs TV) — *post* fake-go-live.
7. Phase 2: Linode deploy (Singapore, GHCR, firewall/no-published-ports, chrony+sync-gate, autoheal, dead-man's-switch).

## Live UI + sizing (0702, riffing — interrogate before building)
### Layout (3-panel, single trading page)
- **Top 20%** — rolling price as a graph line + trade entry/exit markers.
- **Middle 50%** — OPEN positions, one row each, realtime stats (unrealised PnL, PnL, …) + an **[Exit]** button on the right.
- **Bottom 30%** — scrollable list of the last 100 trades; per-row: **gross & net PnL, entry & exit px, slippage, MAE, account balance**.
- Bling: build as a live Artifact mockup first, iterate, then wire to the o9-live DB.

### Auto-sizing
- **Bybit FARTCOINUSDT limits:** minOrderQty 1 · qtyStep 1 · maxOrderQty 3,000,000 · **minNotional $5**. So "smallest order" = the **$5 notional floor ≈ 35–45 coins** @ $0.11–0.15 (notional binds, not min-qty). `max_order` (66k) sits far under the 3M ceiling.
- **LAUNCH = (a) manual modes** — revises DECISION #3 (fixed-66k) into a live control (Joe's reason: begin mainnet with caution + get intel up front):
  - **smallest** — $5 floor (cautious mainnet start) · **fixed** — `max_order` (66k, backtest-match) · **dynamic 5×** — `min(max_order, 5×equity/price)` (the validated compounding model that made $500→$15,026).
  - **`split_count`** modifier (default 1 = whole order). Splitting decided by the fake-API **book-walk (true per-slice slip)**, NOT the 5s bar high–low range (that's volatility, not one order's impact). Re-opens the design's "no-split" call — which was on a *calm deep* book; **reversal-entry books are thin**, so measure it there.
  - mode / max_order / leverage = **DB knobs**, never hardcoded. **Live mainnet results = validation / AB.**
- **Order-book-aware sizing (NEW, Joe):** o9-live (container 1, the *decide* role) consumes the `orderbook` WS to **size to available liquidity** (size down on a thin book). Mainnet-correct (real Bybit has no fake-API). **SEAM:** one shared book source between o9-live sizing + fake-API fills — avoid two divergent reads in the forward-test.
- **Conviction sizing (ROADMAP b/c, post-launch) — multi-factor within a risk-cap ceiling; reuses existing producers, not new machinery:**
  - **safety** — risk-cap %: size so the 0.5% SL loses ≤ X% of equity (the ceiling; Joe picks X).
  - **liquidity** — order-book depth (above).
  - **conviction** — HTF alignment: `hbhl33` reversal OOB primes a deeper next-`s5m` entry → size **up** (= bias-machine M-alignment state). `s7r` runway: `s7r` near exit-side OOB at entry → less room → size **down**.
  - **Kelly** — edge (win-rate + avg win/loss) from the rolling last-N live trades → one INPUT / AB candidate, not the whole lever (Joe: one-dimensional). The bottom-panel trade history *feeds* this — the UI closes the sizing loop.
- **UI mockup:** live Artifact built 0702 (3-panel + control sliver + status strip + order-book drawer; marker hover/tap tooltips, PnL green/red). Mobile = **monitor** view (positions, DD, feed health, kill-switch; sizing controls hidden <820px); desktop = operate.

## Phase-2 infra (confirmed 0702)
- **1 VM, not 2** — skip cloud-pfSense (FreeBSD appliance can't colocate with Docker; no nested virt on standard Linodes). **WireGuard on the o9-live Linux VM** = the tunnel endpoint, site-to-site to on-prem pfSense (+ road-warrior peers incl. Joe's phone for the UI). WG replaces a 2nd pfSense box.
- **VM:** Linode **Shared CPU 4GB / 2 vCPU, Singapore** (Bybit ap-southeast-1). Workload is I/O-light (WS collector + bounded per-5s loop + WG); Shared's neighbour-contention is a non-issue at 5s cadence. Resize→Dedicated later if real-money size wants zero jitter.
- **DB:** Linode **Managed MySQL 2GB / 1 vCPU / 30GB, Singapore** (availability CONFIRMED; same region = intra-region sub-ms reads). Replaces the Phase-1 local WSL DB — seam = connection-string change (as designed).
- **Tick retention:** `ticks` is the ONLY unbounded table → **rolling-window prune** (`kline_collection` is the durable artifact). Storage is the first thing to outgrow, not RAM/CPU — watch that one metric.
- **Security:** Linode **Cloud Firewall** deny-all inbound except the WG UDP port → UI + SSH reachable ONLY over the tunnel; no public exposure of the trading surface. **LISH** (out-of-band console) = break-glass if the tunnel drops. Server-side **dead-man's-switch** auto-flattens if the loop dies → safety independent of Joe's access.
- **Trading egress stays DIRECT Singapore→Bybit** — the tunnel is a MANAGEMENT plane only; never route Bybit order traffic through on-prem (adds latency + makes the home uplink a SPOF).
- **Sequence:** o9-live shows real trades on the UI → **33h clean fake-API** → provision this infra → mainnet **MINIMAL lots** (smallest = $5 notional floor).

## Post-launch roadmap
- **FIRST job after infra (Joe, 0702): gcs5 / gcs1 finishers → replace `s30Mage`-wob.** Faster (5-second + 1-second) exit-finisher lines to trigger the exit turn sooner/more precisely than the current s30M-wob component of the finisher latch. **PREREQ — 1-second tape:** o9-live builds 5s bars today; **gcs1 needs a new tick-built 1s resolution** — surface + scope that before building. (gcs5M was parked at tc=108, see [[project_gate_sweep]].) Interrogate the finisher-latch interaction before coding — don't bolt a new trigger onto a fused method.
