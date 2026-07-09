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
