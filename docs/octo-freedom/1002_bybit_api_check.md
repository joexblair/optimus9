# 1002 — Bybit V5 API check: o9-live, fakeAPI and the data feeds

Joe 1002: *"research bybit's API online, see if we're up to date on both o9-live and fakeAPI's mechs.
provide a list of improvements if you find anything of value"*. Done by a read-only research agent of
the o9-live session; its report is below as it returned it. Nothing in the repo was changed by it.

**Checked against the code by the o9-live session, 1002:**

| finding | the code |
|---|---|
| M1 — reconnect waits stay at 60 s | `bybit_websocket_client.py:52-55`: `delay = 1` only after `_connect` returns cleanly; an abnormal drop raises, so `delay` doubles to `_MAX_RECONNECT_DELAY` 60 s and stays there |
| I15 — the pong reply | `bybit_websocket_client.py:69-70`: any message with `op == 'ping'` is answered `{"op":"pong"}`; Bybit's reply to our own ping carries `op: "ping"` |
| M2 — the recent-trade gap-fill runs once | `tick_collector.py:64`: only inside `run()` |

**Against the docs store:**

| doc | relation |
|---|---|
| `docs/o9_live_design.md:8` — *"Bybit test/demo are unusable: testnet flaky + provisioning-blocked; demo prints test-env prices"* | **CONFLICT, raised to Joe 1002.** L6 below reads the current `/docs/v5/demo` as Demo Trading taking its public data from mainnet. Unresolved: which is true now |
| `docs/o9-live-recon/MVP2.md` item 2, the exchange-resident backstop | complements L1: `set_backstop` misses `tpslMode` and `positionIdx`, both required |
| `docs/second_ws_spec.md`, a second websocket for reconnect gaps and dropped frames | complements M1 and E1-E2 |
| `docs/o9_live_classes.md:64`, `ClockSyncGate` | complements E5, the measured clock offset |

**MVP1 framing:** Joe 1002 ruled that MVP1 RECORDS tick and kline issues (`o9live_errors.log`) and acts
on none. M1-M4 are fixes to the data collector, not actions on issues; whether they land in MVP1 is
Joe's.

---

**What I touched.** I changed no files in the repo. Scratch files went to /tmp only. I made public GET requests to api.bybit.com and api-testnet.bybit.com, and ran one public websocket probe (subscribe, ping, pong; no auth, no orders). Database access was SELECT-only in a READ ONLY session, against o9_live (fx_fill, fx_order, o9_ledger) and dev (kline_audit, ticks). I also read the journalctl logs. o9-live and fakeAPI were not started.

**Changelog result.** No V5 changelog entry from 2025-01-01 to 2026-09-29 (the newest entry) deprecates an endpoint or parameter we use. The entries that touch us:
- orderbook level 500 was removed on 2025-09-11. We use level 50.
- The level-1000 orderbook push went from 300 ms to 200 ms on 2025-11-25.
- `seq` was added to publicTrade (2025-08-05) and to recent-trade (2025-08-07).
- New optional order parameters were added (listed in I6).
- New endpoints: `/v5/position/symbol-info` (2026-06-16), `/v5/market/price-limit` (2025-06-19), `/v5/system/status` (2025-07-08).

---

### 1. Inventory

| # | what our code uses | file:line | what current Bybit docs say | status | source |
|---|---|---|---|---|---|
| I1 | auth headers X-BAPI-API-KEY / SIGN / SIGN-TYPE "2" / TIMESTAMP / RECV-WINDOW; signature = timestamp + key + recv_window + payload, HMAC-SHA256, hex | optimus9/live/exchange/signer.py:35-43 | the guide documents the same recipe and headers; SIGN-TYPE is not in the guide, but the official pybit SDK sends the identical 5-header set | current | bybit-exchange.github.io/docs/v5/guide ; github.com/bybit-exchange/pybit pybit/_http_manager.py:350-357 |
| I2 | `recv_window` (how long a request stays valid) = 5000 ms | client.py:33 | default 5,000; rule: server_time − recv_window ≤ timestamp < server_time + 1000 | current | /docs/v5/guide |
| I3 | request timestamp from the local clock, no server sync | client.py:43 | keep the clock NTP-synced | current (see E5) | /docs/v5/guide |
| I4 | GET: sorted, urlencoded query, signed bytes = sent bytes. POST: JSON serialized once, signed = sent | client.py:56-69 | GET signs the queryString, POST signs the jsonBodyString | current | /docs/v5/guide |
| I5 | envelope: retCode / retMsg / result; non-zero retCode raises | client.py:71-77 | envelope is retCode, retMsg, result, retExtInfo, time | current | /docs/v5/guide |
| I6 | POST /v5/order/create with category, symbol, side, orderType, qty, positionIdx, reduceOnly (when set), orderLinkId (when set); reads result.orderId | adapter.py:42-48 | every field still valid. positionIdx is required in hedge mode. reduceOnly "Must specify it as true when about to close/reduce position". orderLinkId max 36 chars. New optional fields: slippageToleranceType/slippageTolerance (2025-02-27), bboSideType/bboLevel (2025-10-21), rpiTakerAccess (2026-06-03, default false). The acknowledgement is asynchronous ("use websocket to confirm status") | current; new optional fields unused | /docs/v5/order/create-order ; /docs/changelog/v5 |
| I7 | positionIdx mapping: open Buy→1, open Sell→2, reduce Sell→1, reduce Buy→2 | adapter.py:41 ; services/fakeapi/engine.py:22-26 | 1 = hedge Buy side, 2 = hedge Sell side | current | /docs/v5/position |
| I8 | POST /v5/position/trading-stop with category, symbol, stopLoss, slTriggerBy | adapter.py:52-54 | `tpslMode` Required = true; `positionIdx` Required = true | **missing 2 required fields** (nothing in o9-live calls it today) | /docs/v5/position/trading-stop |
| I9 | POST /v5/position/set-leverage, buyLeverage = sellLeverage | adapter.py:57-59 | 4 required fields; buy and sell must be equal in one-way mode and in hedge mode with cross margin | current (no caller) | /docs/v5/position/leverage |
| I10 | GET /v5/position/list with category, symbol; reads side, size | adapter.py:62 ; app.py:55-57 | limit default 20; an empty leg has side "" | current | /docs/v5/position |
| I11 | GET /v5/execution/list with category, symbol; reads the first row whose orderId matches, and its execPrice | adapter.py:65 ; app.py:60-64 | limit default 50, previous 7 days; "You may have multiple executions in a single order"; an orderId filter exists | endpoint current; we read only one row (L2) | /docs/v5/order/execution |
| I12 | call rate: 1 position/list per 5 s bar, plus 1 create and 1 execution/list per order | app.py:55-69 | per-UID linear limits: create 20/s, position/list 50/s, execution/list 50/s; IP limit 600 per 5 s | current | /docs/v5/rate-limit |
| I13 | websocket URL wss://stream.bybit.com/v5/public/linear | optimus9/data/bybit_websocket_client.py:40 | same URL | current | /docs/v5/ws/connect |
| I14 | `_PING_INTERVAL_S` (client ping period) = 20 s, sends {"op":"ping"} | bybit_websocket_client.py:41,76-79 | ping recommended every 20 s; connection cut after 10 min with no ping-pong and no data | current | /docs/v5/ws/connect |
| I15 | any message with op=="ping" is treated as a server ping and answered with {"op":"pong"} | bybit_websocket_client.py:69-70 | Bybit's public pong is `{"ret_msg":"pong","op":"ping"}`. Probe: our reply gets back `{"success":false,"ret_msg":"error:invalid op"}`, so this happens every 20 s | **defect** (M4) | /docs/v5/ws/connect + probe |
| I16 | the subscribe ack is ignored (only messages with a 'topic' key pass) | bybit_websocket_client.py:64,71 | a failed subscribe returns success:false. Probe: orderbook.500 returns "error:handler not found" | gap (M4) | /docs/v5/ws/connect + probe |
| I17 | reconnect `delay` doubles 1→60 s (`_MAX_RECONNECT_DELAY` = 60 s); it resets only when `_connect` returns cleanly | bybit_websocket_client.py:50-59 | "Reconnect as soon as possible if disconnected" | **differs** (M1, E1, E2) | /docs/v5/ws/connect |
| I18 | publicTrade.{symbol}; stores fields i, T, p, v, S | optimus9/data/tick_collector.py:50,96-97 | fields current; seq, RPI, BT, L unused; up to 1024 trades per message, "sorted by the time the trade was matched in ascending order" | current | /docs/v5/websocket/public/trade |
| I19 | orderbook.50.{symbol} (`depth` = 50 levels) | optimus9/live/feed.py:17,30 | linear depths: L1 10 ms, L50 20 ms, L200 100 ms, L1000 200 ms; L500 removed 2025-09-11 | current | /docs/v5/websocket/public/orderbook |
| I20 | a snapshot resets the book; a delta with size 0 deletes the level | feed.py:33-43 | same rules; u=1 means a snapshot after a service restart | current | same |
| I21 | fakeAPI walks the orderbook.50 levels | services/fakeapi/fill.py:29-53 | "RPI orders will not be included in the messages". API orders default to rpiTakerAccess=false, so they match the API pool only (from 2026-06-12) | consistent | announcements.bybit.com/en/article/rpi-liquidity-now-available-to-api-taker-orders-bltb943887bfa4c4d17/ |
| I22 | GET /v5/market/kline with linear, interval '1', start, end; `_BATCH_LIMIT` (rows per call) = 200 | optimus9/data/bybit_kline_client.py:48,50,113-125 | limit [1, 1000], default 200; list sorted newest first; an unclosed candle's close = "the last traded price" | current | /docs/v5/market/kline |
| I23 | GET /v5/market/recent-trade, limit ≤1000; reads execId, time, price, size, side | bybit_kline_client.py:49,86-94 | linear limit 1-1000, default 500; adds seq, isRPITrade, isBlockTrade | current | /docs/v5/market/recent-trade |
| I24 | GET /v5/market/time, result.timeNano | optimus9/data/kline_auditor.py:199-200 | returns timeSecond, timeNano | current | /docs/v5/market/time |
| I25 | retCode 10006 triggers backoff and retry | bybit_kline_client.py:119 | 10006 = "Too many visits. Exceeded the API Rate Limit." | current | /docs/v5/error |
| I26 | PositionSizer defaults: min_qty 1, qty_step 1, min_notional 5 USDT, max_order 66,000 coins | optimus9/live/sizing.py:34 ; ops/run_o9live.py:52 | live instruments-info values (E7) | match | /docs/v5/market/instrument |
| I27 | `O9_TAKER_BPS` (taker fee) = 5.5 bps | services/fakeapi/app.py:26 ; fill.py:26 ; ledger.py:15,58 | VIP 0 perpetuals: taker 0.0550%, maker 0.0200%; "actual fee rates may vary depending on your region" (page updated 2026-09-02) | current for VIP 0 | bybit.com/en/help-center/article/Trading-Fee-Structure |
| I28 | fakeAPI mocks the same 5 endpoints; errors come back as HTTP 200 with a non-zero retCode | services/fakeapi/app.py:57-132 | same convention | current shape; returns only a subset of fields | /docs/v5/error |
| I29 | fakeAPI rejects when abs(now − ts) > recv_window (code 10002) | services/fakeapi/auth.py:35-37 | Bybit's window is asymmetric: ts < server + 1000 | differs (L7) | /docs/v5/guide |
| I30 | fakeAPI returns 110001 for no liquidity, positionIdx mismatch, and reduce-only with no leg | app.py:88-89 ; engine.py:33-40,60-61 | 110001 = "Order does not exist" | differs (L8) | /docs/v5/error |
| I31 | fakeAPI hardcodes leverage 50; set-leverage and trading-stop are stubs | services/fakeapi/store.py:41 ; app.py:93-102 | — | stub | — |
| I32 | live/bybit_client.py, live/fake_api.py | — | no .py file imports them | legacy, unused | — |

### Evidence I measured

**E1 — websocket reconnect waits, klinecollect journal since 2026-05-29**

| cause | 1 s | 2 s | 4 s | 8 s | 16 s | 32 s | 60 s |
|---|---|---|---|---|---|---|---|
| "no close frame received or sent" | 15 | 14 | 11 | 8 | 8 | 8 | 99 |
| DNS failure | 0 | 0 | 2 | 2 | 2 | 2 | 51 |

The 5,268 "MySQL Connection not available" errors are left out. They all waited 60 s and fall on 06-04, 06-05, 06-07 and 06-23 to 06-25: database outages, not Bybit.

**E2 — one disconnect on 2026-09-25: logged 16:50:37, reconnected 16:51:38 (61 s)**

| minute (UTC) | 16:49 | 16:50 | 16:51 | 16:52 | 16:53 |
|---|---|---|---|---|---|
| ticks stored | 380 | 108 | 49 | 149 | 253 |

| kline_audit verdicts, 16:49–16:54 | count |
|---|---|
| 5s frozen (16:50:55–16:51:35) | 9 |
| 1m variance (16:50, 16:51) | 2 |
| 5s live | 51 |
| 1m match | 3 |

**E3 — FARTCOINUSDT REST orderbook, 2026-10-02 01:51:57 UTC (one snapshot, n=1; the 3 calls were ~0.2 s apart)**

| depth | ask coins in depth | furthest ask (bps from mid) | level where 66,000 coins is reached (ask) | bid coins in depth | furthest bid (bps) | level where 66,000 is reached (bid) |
|---|---|---|---|---|---|---|
| 50 | 175,218 | +27.9 | 24 | 147,924 | −29.1 | 24 |
| 200 | 1,548,246 | +122.7 | 24 | 1,507,508 | −134.6 | 28 |
| 1000 | 3,167,019 | +769.9 | 21 | 6,459,678 | −727.0 | 31 |

| price-limit band, same session | value |
|---|---|
| buyLmt | 0.20272 (+14.98% vs mark) |
| sellLmt | 0.14987 (−15.00% vs mark) |
| mark | 0.17631 |

**E4 — REST recent-trade sample: 1,000 trades over 293 s, returned newest first**

| measure | count |
|---|---|
| millisecond timestamps with more than 1 trade | 201 |
| of those, with more than 1 distinct price | 60 |
| of those 60, all trades share one seq | 47 |

**E5 — clock offset (server − local), from kline_auditor's journal since 2026-06-06**

| n | min | median | max | Bybit bounds |
|---|---|---|---|---|
| 33,061 | −71 ms | +42 ms | +1,207 ms | local clock may be up to 1,000 ms ahead and up to 5,000 ms behind |

**E6 — FARTCOINUSDT ticker, one read on 2026-10-02**

| venue | lastPrice | volume24h |
|---|---|---|
| testnet | 0.17627 | 29,208,780 |
| mainnet | 0.17757 | 126,333,614 |

**E7 — instruments-info, live GET on 2026-10-02, against the sizer defaults**

| field | Bybit | sizer |
|---|---|---|
| minOrderQty | 1 | 1 |
| qtyStep | 1 | 1 |
| minNotionalValue | 5 | 5 |
| maxMktOrderQty | 600,000 | max_order 66,000 |
| maxOrderQty | 3,000,000 | — |
| tickSize | 0.00001 | — |
| maxLeverage | 50.00 | fakeAPI hardcodes 50 |
| fundingInterval | 240 min | not modelled |
| priceLimitRatioX / Y | 0.15 / 0.3 | — |

---

### 2a. Improvements that affect MVP1 (the tape, the fake fills, the trade log)

Joe's 1002 ruling says MVP1 records tick and kline issues and acts on none of them. So whether M1–M4 land in MVP1 is his call.

| # | change | why (doc evidence) | component | size |
|---|---|---|---|---|
| M1 | Reset the reconnect `delay` once a connection has subscribed, so later disconnects reconnect at 1 s instead of 60 s. | Docs: "Reconnect as soon as possible if disconnected" (/docs/v5/ws/connect). Today `delay` only resets on a clean close (bybit_websocket_client.py:54-55), so once it reaches 60 s it stays there for the life of the process. E1: 99 of 163 disconnects waited 60 s. E2: one 61 s gap produced 9 frozen 5s verdicts and 2 variance 1m verdicts. | data: BybitWebSocketClient, which serves both the tick collector and fakeAPI's OrderBookFeed | small |
| M2 | Run the REST recent-trade gap-fill after every reconnect, not only at process start. | `_backfill_recent` runs once, inside run() (tick_collector.py:64). recent-trade limit is 1-1000 (/docs/v5/market/recent-trade). E4: 1,000 trades covered 293 s in one sample. | data: TickCollector | small |
| M3 | Insert the gap-fill trades oldest-first, or store `seq` and order bars by (tk_timestamp, tk_pk). | recent-trade comes back newest first (E4; the docs don't say). tick_collector.py:80-83 inserts in list order, and bar_builder.py:118-120 orders by tk_timestamp only. So for gap-fill rows, trades sharing a millisecond come back in reverse execution order. E4: 60 multi-price milliseconds in 293 s. Effect on bar closes is unmeasured; kline_audit's 1m tier would show it. | data | small |
| M4 | Remove the pong reply (I15). Log subscribe acks that return success:false (I16). | Probe results quoted in I15 and I16. Whether the invalid op affects disconnects is unmeasured. | data | small |
| M5 | fakeAPI: carry the book's `cts` (matching-engine time of the book) into LIVE_BOOK and record it on each fill. No threshold proposed. | feed.py:44-47 drops ts and cts. Docs: cts = "The timestamp from the matching engine when this orderbook data is produced". During an M1 reconnect the fake fills from a book up to ~60 s old, with no record of that. | fakeAPI | small; adds a column to fx_fill, so it is Joe's call (build alongside) |
| M6 | Have the trade log record the executed qty (sum of execQty for the orderId) instead of the requested `o.qty`. Have fakeAPI also persist the requested qty and the `exhausted` flag (book ran out before the full qty filled). | engine.py:42 stores the filled qty. fill.py:53 computes `exhausted` but store.py:63-68 does not persist it. app.py:72 writes the requested qty to the ledger. On Bybit a market order fills as IOC (fill what you can now, cancel the rest), so a short fill splits the ledger from the exchange silently. How often it happens is unmeasured: fx_fill held 1 row when I read it; E3 shows 66,000 coins used 24 of 50 levels in one snapshot. | o9-live + fakeAPI | small |
| M7 | Choose the depth of the fake's book walk: L50 (20 ms) vs L200 (100 ms) vs L1000 (200 ms). | Doc depths are in I19; snapshot in E3. This trades freshness against depth, which is Joe's value call. Listed as an option, not a recommendation. | fakeAPI feed.py:17 | small |
| M8 | Set orderLinkId (max 36 chars, unique) to a signal key, and have fakeAPI return it from execution/list. | Order.order_link_id defaults to "" and nothing sets it (sizing.py:30). The fake stores it (store.py:23-25) but app.py:130-131 doesn't return it. Bybit returns orderLinkId on execution rows, so the trade log could join to fills on the same key on both venues. The key format is Joe's. | o9-live + fakeAPI | small |
| M9 | (optional) Copy GET /v5/system/status maintenance windows (begin/end/state) into the errors log. | Endpoint added 2025-07-08 (/docs/v5/system-status). | feed_errors | small |

### 2b. Later (real money / MVP2)

| # | change | why (doc evidence) | component | size |
|---|---|---|---|---|
| L1 | set_backstop: send `tpslMode` and `positionIdx`, one call per open leg. fakeAPI should reject a call missing them. | The trading-stop table marks both Required = true (/docs/v5/position/trading-stop). | adapter + fakeAPI | small |
| L2 | Read fills properly: query execution/list by orderId, take VWAP = Σ execValue / Σ execQty and Σ execFee, and wait for the rows. Or use GET /v5/order/realtime (avgPrice, cumExecQty, cumExecFee, orderStatus), or the private WS `execution` / `execution.fast`. fakeAPI should honour the orderId filter and return execId, execValue, feeRate and orderLinkId. | The order/create ack is asynchronous, and one order can have multiple executions (/docs/v5/order/execution, /docs/v5/websocket/private/fast-execution). app.py:60-64 reads once and takes the first row. | o9-live + fakeAPI | medium |
| L3 | Take fees from the exchange: takerFeeRate from GET /v5/account/fee-rate, and execFee per fill. | ledger.py:58 estimates the fee from 5.5 bps. The fee page says actual rates "may vary depending on your region". | o9-live | small |
| L4 | Startup checks: hedge mode (POST /v5/position/switch-mode, mode=3); leverage (GET /v5/position/symbol-info, new 2026-06-16; treat set-leverage 110043 "Set leverage has not been modified" as a no-op); instrument filters read live (maxMktOrderQty is adjusted on the 3rd and 17th, 08:00 UTC+8). fakeAPI: enforce the lot and notional limits with Bybit's codes (e.g. 110094 "Order notional value below the lower limit"), raise 110043, and stop hardcoding leverage 50. | /docs/v5/position/position-mode, /batch-lvg, /leverage, /market/instrument, /error | o9-live + fakeAPI | medium |
| L5 | Market-order slippage tolerance: TickSize [1-10000] or Percent [0.01-10]. It is off by default ("executes as a standard market order, without any restrictions on slippage"); with it on, anything past the tolerance is cancelled. The value is Joe's. The fake walk would need to stop at the tolerance price. The price-limit band (±15%, E3) does not bind at the current order size, so no fake change is needed for that. | create-order; bybitglobal.com/en/help-center/article/Market-Order-with-Slippage-Tolerance | o9-live + fakeAPI | small-medium |
| L6 | Bybit Demo Trading as a contract-test venue: api-demo.bybit.com, private WS stream-demo.bybit.com, public data from mainnet. It supports all 5 endpoints we use plus switch-mode; WS Trade is not supported; orders are kept 7 days; 50,000 USDT starting balance. Same BybitV5Client with a different base_url and a demo key; it would catch L1/L2/L4 on Bybit's own engine. Demo's fill mechanism is undocumented ("executed orders don't enter the actual order book"), so a side-by-side with fakeAPI would measure it rather than assume it. Testnet is a separate market (E6), so it is for contract tests only. | /docs/v5/demo ; bybitglobal.com FAQ-Demo-Trading | ops | medium |
| L7 | fakeAPI: use Bybit's asymmetric timestamp rule. E5 shows no live effect today. | /docs/v5/guide | fakeAPI auth.py | small |
| L8 | fakeAPI: stop returning 110001 for its three failure cases (I30). | /docs/v5/error | fakeAPI | small |
| L9 | Raise `_BATCH_LIMIT` from 200 to 1000 for backfills (5× fewer calls). | kline limit [1, 1000] | data | small |
| — | Gap noted, not proposed: fakeAPI does not model funding (FARTCOIN fundingInterval 240 min). P&L stays closed per the MAE/MFE-only rule. | — | fakeAPI | — |

### 3. What I could not verify

- **Quotes may be paraphrased.** The doc pages went through a summarizing fetcher. I re-requested verbatim text for the trading-stop table, the create-order rows, the orderbook depths and publicTrade; other quotes may be paraphrased.
- **Help-center pages.** bybit.com timed out in the fetcher. I read the fee page with curl, and the slippage and demo FAQ pages from the bybitglobal.com mirror.
- **Exact retCodes** for three cases: positionIdx not matching the account's position mode, reduce-only with no position, and a market order with nothing to fill. The 110017 text ("orderQty will be truncated to zero") is the closest doc match for reduce-only, but it is not confirmed.
- **Whether trading-stop always required tpslMode and positionIdx.** No changelog entry since 2025-01, so I report them as "missing", not "changed".
- **Default market-order protection threshold.** The docs say a "slippage threshold" relative to the mark price but give no number.
- **How Demo Trading prices fills.**
- **Joe's real account:** fee tier/region, position mode and leverage. These need API keys.
- **Disconnects:** what causes the "no close frame" disconnects, and whether the invalid-op pong affects connection lifetime.
- **Book exhaustion at our order sizes.** How often 50 levels run out is unmeasured: 1 fx_fill row, 1 snapshot.

**TL;DR:** Every Bybit endpoint, field, header and topic we use is still current. The one doc mismatch is set_backstop, which misses 2 required fields (tpslMode, positionIdx) but is never called. The finding that affects MVP1 is ours, not Bybit's: the websocket client waits 60 s on every reconnect, against Bybit's "reconnect as soon as possible". One such 61 s gap left 9 frozen 5s and 2 variance 1m kline_audit verdicts. Whether that is fixed in MVP1 is Joe's call.