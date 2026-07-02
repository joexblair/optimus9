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
| `ExchangeAdapter` | NEW | **EXECUTE only** — order → v5 calls (see fork ✚) | `place/reduce/close/set_leverage/positions/executions` |
| `BybitV5Client` | NEW | thin `requests` wrapper; seams: `base_url`(ctor) · `Signer` | `get(path,params) / post(path,body)` |
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
| `StopMonitor` | NEW | **STOP** — watch **mark** vs open SL 0.5%, honouring the order's `triggerBy` → close fill |
| `MarkFeed` | NEW | `tickers` WS → `markPrice` + `indexPrice` ticks (mark tape); logs `last − mark` divergence (#19/#39) |
| `FxStore` | NEW | `fx_order` / `fx_position` / `fx_fill` persistence (exchange truth) |

**Mark price (settled 0702):** the SL is placed with **`triggerBy=MarkPrice`** — on mainnet **real Bybit triggers on mark** (a last-price super-wick that doesn't move mark won't stop us; the #44 fix, zero custom code). The fake-API *emulates* this: `StopMonitor` reads the `MarkFeed` and honours `triggerBy`. **mark = trigger truth · order-book walk = fill truth · signals stay on LAST** (no basis swap). `ExchangeAdapter` carries `trigger_by` on the SL / trading-stop call; default `MarkPrice`.

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

## Open forks / params to pin at build
- ✚ **Adapter shape:** ONE `ExchangeAdapter` + client-swap (base_url+signer) rather than separate Fake/Bybit adapters — the fake speaks the *identical* v5 contract, so two adapters would duplicate the mapping. (Recommended; supersedes the two-impl sketch.)
- **fakeAPI framework:** FastAPI + uvicorn (fakeAPI container only) — pending nod.
- **BUFFER** hours — derive from the longest-lookback line.
- **Reduce attribution** — FIFO.
- **Order-book source** — shared between o9-live sizer + fakeAPI fill model.
