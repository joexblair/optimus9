# o9-live — spec & durable notes

The canonical reference for the o9-live forward-test: what runs where, the DB layout, the deploy workflow, and the
current live config. This is the *steady-state spec*; the running log of individual tweaks lives in
[o9live_changelog.md](o9live_changelog.md) (SRP — this doc is the "what is", that doc is the "what changed & why").

## Infrastructure
| role | host | notes |
|---|---|---|
| **dev** | WSL (`~/thecodes`, `sifu01`) | main + feature branches + all analysis/backtest. `pk_optimizer` DB (WSL-only). |
| **prod forward-test** | **`sg-app-01` = `172.236.152.81`** (Linode SG) | runs the `live` branch: collector + fakeAPI + loop + UI. Near Bybit (low tick latency). |
| **DB** | Akamai Managed MySQL — `a493943-akamai-prod-5255352-default.g2a.akamaidb.net` | holds `o9_infra` + `o9_live`. |
| network | WireGuard → on-prem pfSense (planned); tunnel-only FW | creds/ports Joe-held, never committed. |

## Database topology
- **`o9_infra`** = the DEFAULT db (`get_db_config()`), = **tape (kline_collection, ticks) + all config** (indicator_*,
  lp_config, lr_gate*, optimus9_system, trading_pairs, risk_config, cascade_state, `vw_indicator_configs_live`). On SG
  this plays the role `pk_optimizer` plays on WSL. *Config and tape must share one db* — the code reads both from the default.
- **`o9_live`** = exchange + o9-live tables only: fx_order/fx_fill/fx_position, o9_ledger, o9_account, o9_decision,
  o9_forecast, o9_control, **o9_state_log(+_line)**, **o9_trade_archive**. Accessed via `c['database']='o9_live'`.

## Two instances, one set of shared infra (Joe 1023)

Joe 1023, verbatim — his own quote marks, so this is a block rather than an italic run:

> I think we should run both strategies - the "all lines on closed bars" version, and the "v4core
> lines on closed bars" version. separate instances, each holding its own trading account. one
> "safe", and one "more net"

> each instance should have its own "trading" db - fakeAPI will handle the infra (klines, account
> transactions, etc)

> each instance's rows land in its own trading database

**The split is the topology above, used twice.** `o9_infra` (SG) / `pk_optimizer` (WSL) is SHARED;
the trading db is PER-INSTANCE. `o9_live_test` already exists with the same 9 tables, so the
pattern is proven, not theoretical.

| the layer | where | shared or per-instance |
|---|---|---|
| `kline_collection`, `ticks` | `o9_infra` | **shared** — one tape, no drift between instances |
| `indicator_*`, `optimus9_system`, `mech_line_config`, `vw_indicator_configs_live` | `o9_infra` | **shared** |
| `fx_order`, `fx_position`, `fx_fill`, `fx_fill_book` | the trading db | **per-instance** |
| `o9_ledger`, `o9_account`, `o9_decision`, `o9_forecast`, `o9_sizing` | the trading db | **per-instance** |
| `o9_control`, `o9_state_log(+_line)`, `o9_trade_archive` | the trading db | **per-instance** — instance state |

**Why `fx_*` CANNOT be shared, and this is the one hard constraint.** `MatchingEngine.submit` calls
`store.open_leg(symbol, position_idx)`, which returns **any** open row for that symbol and leg. A
shared `fx_position` would have instance B pyramiding onto instance A's position, silently.
"Account transactions" means fakeAPI owns the MACHINERY — the book walk, the fills, the position
arithmetic — while each instance's rows land in its own db.

### What already supports it
| the piece | how it is bound |
|---|---|
| fakeAPI's store, and `/dev/reset` | `PK_DB_NAME`, per container. So a reset is already instance-scoped |
| the loop | `PK_DB_NAME` |
| **the UI** | `PK_DB_NAME` as of 1023 — see the fix below. The five shared-infra reads stay explicit as `_db("pk_optimizer")` |
| the API credentials | `O9_FAKE_API_KEY` / `O9_FAKE_API_SECRET` |
| start equity, symbol, drawdown ref | `O9_START_EQUITY` (default 888), `O9_SYMBOL`, `O9_DD_REF` |

**The 1023 fix that made it safe.** `ui_server._db` had the trading db name as a hard-coded default
argument (`name="o9_live"`) while every other part of the stack read `PK_DB_NAME`. A second
instance's UI would have served the FIRST instance's trades — both pages alive and plausible, which
is the worst way for this to fail. It now resolves `TRADING_DB = os.environ.get("PK_DB_NAME",
"o9_live")`.

### What is NOT done
| item | state |
|---|---|
| the second compose project | not written. Needs its own project name, db, key pair and UI port |
| `AuthEmulator` is multi-key ready and unused | its ctor takes `{api_key: api_secret}` and `verify()` returns the account — but `app.py` discards that return at all six call sites and `_CREDS` is built from one env pair. Not needed for the per-db split; relevant only if one fakeAPI ever serves two accounts |
| which strategy is "safe" and which is "more net" | the all-lines-closed arm measured FEWER trades (210 vs 543), higher win rate, lower drawdown. The `v4core`-lines-closed arm has NOT been measured yet |

## The walked slippage, on the account transactions screen (Joe 1023)

Joe 1023: *"I'd love it if fakeAPI calculates the slippage dynamically, based on bps at position
open, and prints it on the account transactions screen"*, then *"yes - good catch"* on the exit leg.

THE CALCULATION ALREADY EXISTED AND WAS ALREADY STORED. `OrderBookWalker` walks the LIVE book for
each order's own size and returns the adverse fill against the book mid in bps; `FxStore` writes it
to `fx_fill.slippage_bps`. It was never surfaced. The trade-history table now carries `Slip in`,
`Slip out` and `Slip $`, joined on `o9_ledger.entry_order_id`/`exit_order_id` = `fx_fill.order_id`.

- `/v5/execution/list` is deliberately UNCHANGED: the real Bybit returns no slippage field, so
  adding one would drift the contract `BybitClient` is a drop-in for. The UI reads `fx_fill`
  directly, because slippage is exchange truth rather than client truth.
- MEASURED on 192 closed trades: entry 2.20 bps mean, exit 2.53, round trip 4.72 mean / 7.65 p95 /
  10.38 max, USD 110.41 in total. The banked assumptions are 8.75 bps round trip (conservative,
  4.375 a leg at 22,000 coins) and 6.70 (taker/taker) — so the real book has been cheaper than
  both, while p95 still crosses the taker/taker figure.
- ONE KNOWN DOUBLE-COUNT PATH, documented not guarded: `Ledger._close_rows` stamps the same exit
  order id on every row it closes, so one exit order could sit on two ledger rows and each would
  read that exit's slippage in full. All 192 trades are currently 1:1 on both order ids. Safe per
  ROW regardless; anyone SUMMING the dollar column must re-check that ratio.

## Services (SG)
- **collector** — fills `o9_infra.kline_collection` + `ticks` from Bybit (SG-collected clean tape).
- **fakeAPI** (`services.fakeapi.app`, :8098) — paper exchange, **Bybit hedge mode** (positionIdx legs).
- **loop** (`ops/run_o9live.py`) — stateless per-5s-bar producer → decide → size → execute. Env: `O9_PRODUCER=ad`,
  `O9_DELAY_MS=2000`, `O9_SIZE_MODE=dynamic5x`.
- **UI** (`optimus9.live.ui_server`, :8099) — cascade block, feed board, reset/flatten/resume.

## Current live config (as of 2026-07-09)
- **Exit:** coarse-curl cascade — gate `s7r` breach-then-OOB-curl @105s + unlatch `s5r` coarse-curl @40s (DB `lp_config`:
  gate_mode/unlatch_mode=1, seam_gate=105000, seam_unlatch=40000). +1.2% v2_walk. See [[project_exit_curl]], `docs/exit_brd.md`.
- **Hedge mode:** two independent legs per symbol by positionIdx; strategy opens both sides. See `docs/hedge_mode_spec.md`.
- **filler_invisible = ON** (event-tape lines, TV-parity). **seam grace = 2000ms** (desync interim; proper fix = finalized-bar read).
- **RiskGovernor** built (`risk_config`, v2_walk-grounded) but **NOT wired into the loop** yet. See `docs/dynamic_risk_spec.md`.

## Deploy & versioning
- **`live` = prod**, **`main` = dev**, tags = releases. Promote on ship: `git checkout live && git merge main && git tag live-<date> && git push --tags`.
- SG deploy: `git pull` on `live`. **Rollback:** `git checkout <prev-tag>`.
- Bootstrap a fresh box: `docs/sg_bootstrap.md`. Clone: `git clone --branch live git@github.com:joexblair/optimus9.git`.

## Reset semantics (`POST :8099/api/reset`)
Wipes the paper account (o9_ledger, o9_decision, o9_forecast, fx_*) → $500, halts the loop. **Preserves by design**:
`o9_state_log(+_line)` (the line-value audit trail) + `o9_trade_archive` (durable trades, `mmdd_NN` labels). Resume via `/api/resume`.

## Durable vs transient tables
- **Durable (survive reset):** `o9_state_log/_line` (emerging line values, keyed by kline_ms), `o9_trade_archive` (closed
  trades, `mmdd_NN` labels — the stop-tool's persistent history).
- **Transient (reset wipes):** `o9_ledger`, `o9_account`, `o9_decision`, `o9_forecast`, `fx_*`.

## Related docs
`docs/o9-live/o9live_changelog.md` · `docs/sg_bootstrap.md` · `docs/hedge_mode_spec.md` · `docs/dynamic_risk_spec.md` ·
`docs/exit_brd.md` · `docs/o9_live_schema.sql`
