# o9-live — class design (agreed 0702)

Build spec for the three components. **REUSE** = existing, do not rebuild. **NEW** = to write.
Companion to `o9_live_design.md` (architecture) + `o9_live_schema.sql` (tables). SRP splits are load-bearing.

## Locations
- `optimus9/live/` — o9-live (reuses `optimus9.analysis.lr`, `optimus9.compute`, `optimus9.data.*`).
- `services/fakeapi/` — the mock Bybit exchange (own container; standalone).
- `ops/manager/` — the container-manager / Supervisor.

## Component 1 — o9-live  (ingest · decide · size · execute · serve)
| class | R/N | responsibility | key methods |
|---|---|---|---|
| `O9LiveApp` | NEW | composition + lifecycle; wires collector→loop→adapter | `start() / stop()` |
| `TickCollector` | REUSE | publicTrade WS → `ticks` | (existing) |
| `BarBuilder` / `KlineAuditor` | REUSE | ticks → 5s `kline_collection` (the print = the clock) | (existing) |
| `RunWindow` | REUSE\* | bounded buffer read (BUFFER hrs) → `W.line` | `line(name)` — \*BiasWindow, small buffer |
| `StrategyLoop` | NEW | **DECIDE only** — on_kline: RunWindow→lr_detect→intent | `on_kline(ts) → TradeIntent?` |
| `lr_detect` / `LRConfig` | REUSE | cascade producer + config (live==prod==backtest) | (existing) |
| `TradeIntent` | NEW | value obj `{action, side, reason, ts}` — the seam, **not a baked verdict** | — |
| `PositionSizer` | NEW | **SIZE only** — intent+acct+book → orders | `size(intent, acct, book) → [Order]` |
| `ExchangeAdapter` «iface» | NEW | **EXECUTE only** — our exchange-AGNOSTIC intent contract (defined by OUR needs, not Bybit's API) | `place/reduce/close/set_backstop/positions/executions` |
| └ `BybitAdapter` | NEW | the Bybit impl — maps the contract → v5 calls; fake vs real = client construction only | (future: other exchanges = new impls) |
| `BybitV5Client` | NEW | thin `requests` wrapper; seams: `base_url`(ctor) · `Signer` | `get(path,params) / post(path,body)` |
| `MarkFeed` | NEW | `tickers` WS → mark/index ticks (feeds StopManager; logs `last−mark` divergence #19/#39) | `mark() / index()` |
| `StopManager` | NEW | **SOFT STOP** — per mark-tick vs each trade's 0.5% stop → close intent; level HIDDEN from the exchange | `on_mark(px) → [close]` |
| `Signer` «iface» | NEW | request auth | `sign(ts, recv, payload) → headers` |
| ├ `HmacSigner` | NEW | real Bybit v5 HMAC-SHA256 (primary — exercises auth on the fake path too) | |
| └ `PassThroughSigner` | NEW | debug bypass only | |
| `TradeLedger` | NEW | **independent virtual trades over the one-way net**; per-trade entry/SL/MAE/unreal | `open_trade / reduce(row,qty) / attribute_fill / rows()` |
| `OrderBookFeed` | NEW | orderbook WS → depth snapshot (feeds the sizer) — reuses `bybit_websocket_client` | `depth() / best()` |
| `UiServer` | NEW | **SERVE** — read API + terminal page; controls | `GET /api/state,/api/history` · `POST /exit,/flatten,/sizing` |
| `HeartbeatEmitter` | NEW | loop-liveness beacon (watched by Supervisor) | `beat()` |

- **Sizing modes (launch):** `smallest` ($5 notional floor) · `fixed` (max_order 66k) · `dynamic5x`; `split_count` modifier. Roadmap inputs: liquidity (book), conviction (HTF hbhl33 / s7r runway), Kelly-as-one-input. All config DB-sourced.
- **TradeLedger vs FxStore:** ledger = the *client* per-trade view (attribution over the net); `FxStore` = the *exchange truth* (net). Two sides of the API, not duplication. Attribution policy on partial reduce = **FIFO** (pin at build).
- Flow: `BarBuilder ▸ StrategyLoop ▸ TradeIntent ▸ PositionSizer ▸ ExchangeAdapter ▸ (fakeAPI|Bybit)` ; fills ▸ `TradeLedger ▸ UiServer / sizer(acct) / DeadMansSwitch`.

## Component 2 — fakeAPI  (mock Bybit v5 exchange)
| class | R/N | responsibility |
|---|---|---|
| `FakeApiServer` | NEW | **CONTRACT** — v5 routes + universal envelope + real error codes (FastAPI, pending nod) |
| `AuthEmulator` | NEW | **AUTH** — HMAC recipe + recv_window/clock check; stub key→acct (surfaces auth/clock bugs here) |
| `OrderBookWalker` | NEW | **FILL PRICE** — walk live book for size → avg fill + slip; taker 5.5 bps, per-leg |
| `OrderBookFeed` | NEW | orderbook WS → depth (shared-source seam with o9-live) |
| `MatchingEngine` | NEW | **LIFECYCLE** — apply fills → positions; one-way pyramid grow/reweight/reduce |
| `StopMonitor` | NEW | **BACKSTOP only** — emulate the WIDE exchange SL (~0.7%, `triggerBy=MarkPrice`) → close fill (the tight 0.5% soft-stop is o9-live's `StopManager`) |
| `FxStore` | NEW | `fx_order` / `fx_position` / `fx_fill` persistence (exchange truth) |

**Stops (settled 0702) — SOFT primary + WIDE exchange backstop:**
- **Primary = SOFT stop in o9-live** (`StopManager` watches the `MarkFeed` per tick → market close at the 0.5% level). The stop level **never reaches the exchange** → no stop-hunting ("intent away from prying eyes").
- **Backstop = a WIDE SL (~0.7%) placed WITH the exchange** via `triggerBy=MarkPrice` — the failsafe for total o9-live failure (crash/disconnect). Wider than the soft stop, so it only fires if the soft one couldn't. `ExchangeAdapter.set_backstop(trigger_by=MarkPrice)`.
- **Trade-off (accepted):** a soft stop carries execution risk if o9-live↔exchange hiccups *at* the stop moment — the wide backstop is exactly what caps that.
- **mark = trigger truth · book-walk = fill truth · signals stay on LAST** (no basis swap). fakeAPI's `StopMonitor` emulates ONLY the wide backstop; the shared mark feed serves both.

Routes: `POST /v5/order/create`, `/position/trading-stop`, `/position/set-leverage` · `GET /v5/position/list`, `/execution/list`. String numerics (Decimal). Error codes 10002/10004/110043.

## Component 3 — container-manager  (`ops/manager/`)
**NOW** (run + safeguard one stack — needed for fake-go-live):
| class | responsibility |
|---|---|
| `Supervisor` | health-gated boot order + run loop |
| `HealthGate` | DB reachable · fakeAPI `/health` · images up |
| `ClockSyncGate` | chrony drift < recv_window → else block/halt |
| `HeartbeatMonitor` | watch o9-live beacon + container liveness |
| `DeadMansSwitch` | stall/death → flatten (`/flatten`; else exchange SL) + halt |
| `Autohealer` | restart w/ backoff; max-retry → escalate to halt |
| `Alerter` | push to phone on halt/flatten/drift/death |
| `HousekeepingJobs` | tick-prune · logrotate · backup-verify · image-GC |

**LATER** (deferred until the forward-test proves out / BTCUSDT lands — do NOT build first):
| class | responsibility |
|---|---|
| `FleetController` | manage N per-pair stacks + the deploy pipeline |
| `Stack(symbol)` | one pair's full deployment; `spin_up()/tear_down()` — BTCUSDT = a new Stack |
| `ReleaseManager` | git tag/branch → build/pull image (GHCR) + update cadence |
| `CanaryValidator` | new version in SHADOW on live data vs prod → pass/fail (the isolate+OOS discipline, at deploy level) |
| `Promoter` | canary-pass → blue-green cutover; rollback on fail |

Docker Compose owns lifecycle/restart/healthchecks; the Supervisor adds only the trading-safety layer. Don't rebuild Docker.

## Build order (agreed)
① fakeAPI contract skeleton + `BybitV5Client` (the seam) → ② point existing collector at o9-live DB → ③ fakeAPI fill model + `FxStore` → ④ o9-live loop (RunWindow→lr_detect→intent→sizer→adapter) → ⑤ `UiServer` wired to the mockup → ⑥ minimal Supervisor → local **fake-go-live**.

## Resolved (0702)
- **Adapter shape:** abstract `ExchangeAdapter` (exchange-agnostic contract) + `BybitAdapter` impl; fake-vs-real = client construction (base_url+signer), NOT a separate adapter. Future exchanges = new impls under the interface.
- **Framework:** FastAPI + uvicorn — `UiServer` on **o9-live** (bespoke view, always) + fakeAPI mock REST (test-only).
- **Stops:** soft 0.5% in o9-live `StopManager` (hidden) + wide ~0.7% exchange backstop (`triggerBy=MarkPrice`).

## Parallel fake-API + mainnet (after 33h) — the `Stack` capability, pulled forward
Post-33h Joe runs **fakeAPI (paper shadow) + Bybit mainnet (minimal lots) in parallel**. This needs the container-manager to run **>1 stack** — a lightweight `Supervisor`-over-`Stack(config)`, pulled forward from the deferred fleet work (the deploy pipeline — ReleaseManager/Canary/Promoter — STAYS deferred). **FORK to decide when we build that phase (not now, not blocking the single-stack build):**
- **(a) two o9-live instances** (fake stack + mainnet stack) — clean failure isolation, but 2× compute + they'd drift as separate windows.
- **(b) one instance, fan the intent to two adapters** (fakeAdapter + bybitAdapter), two `TradeLedger` books, one UI showing both — decide-once, directly comparable fills (validates the cost model). Coupling + independent order-failure handling.
- Sub-Q: matched size (clean fill comparison) vs independent size (mainnet-minimal / paper-normal). Lean: **(b)** for the comparability, run both at mainnet-minimal size during the overlap.

## Params to pin at build
- **BUFFER** hours — derive from the longest-lookback line.
- **Reduce attribution** — FIFO.
- **Order-book + mark source** — shared between o9-live (sizer / StopManager) + fakeAPI (fill / backstop).
