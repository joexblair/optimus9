# o9-live security spec — redundancy, self-healing, watching

Joe 1011: *"add all of our redundancy specs to a o9-live-security spec"*. One place for every layer that
keeps o9-live trading on a true tape, heals a broken feed, and tells Joe when something goes wrong.
Values are the running ones on 10-11; each row names the ruling it came from.

**In plain English:**
- Trades come in on **two** sockets to two Bybit hosts.
- A socket that goes quiet for 60 s restarts itself and refills the trades it missed.
- If that doesn't bring trades back within 50 s, pfSense reloads the internet connection.
- A second, independent path (Bybit's REST API) checks every bar we build.
- Eight network probes, the Windows event log and pfSense record which hop failed.
- Problems are written to one errors log, and the ones Joe would act on reach his device.

The incident record for all of this is `docs/octo-freedom/1002_outage_diagnostics.md`.

## 1. Self-healing, in firing order

| # | layer | what it does | values | ruling | code |
|---|---|---|---|---|---|
| 1 | two tick sockets | both write every trade into `ticks`; a trade dropped on one lands via the other (`INSERT IGNORE` on trade id) | `collector` = `stream.bybit.com`, `collector2` = `stream.bytick.com` | Joe 1002 (outage item #6) | `optimus9/data/tick_collector.py` (`O9_TICK_ENDPOINTS`) |
| 2 | heartbeat | each socket sends Bybit a ping | every 20 s | — | `bybit_websocket_client.py` `_PING_INTERVAL_S` |
| 3 | stall restart | no trade or book message for the stall time → the socket is aborted and reconnects at once; ping replies do not count as alive | 60 s | Joe 1002: *"auto restart on any tick freeze that dwells more than 60 seconds"* | `bybit_websocket_client.py` `_watchdog` |
| 4 | restart offset | the two tick sockets never restart within this offset of each other, so one is always listening | 10 s | Joe 1002: *"I'm sure 10s is enough, but your call"* | `RestartGate` |
| 5 | reconnect wait | after a socket error: wait, then reconnect. Each attempt that never comes up doubles the wait; a connection that came up and then dropped starts again at 1 s | 1 s → 2 → 4 … cap 60 s; reset to 1 s on a good connect | Joe 1011: *"the reset to 1s is logical, bake it in"* (before: reset only on a stall restart, so the UI book reached 60 s) | `_stream_loop` |
| 6 | gap-fill | every (re)connect of a tick socket merges Bybit's 1,000 most recent trades from REST | 1,000 trades; they reach back a median 7.4 min, under 2.9 min one second in 10 (measured 10-04 over 09-27 to 10-04, 607,954 s) | Joe 1002: gap-fill after reconnect | `TickCollector._backfill_recent` |
| 7 | WAN reload | if no trade arrives on ANY socket within 50 s of the first stall restart, ssh to pfSense with a forced-command key: `pfSctl -c 'interface reload wan'`. No limit on how often | 50 s | Joe 1002: *"Trades only, no limit … if the tick flow begins everytime the int is reset, then we have infra issues to troubleshoot"* | `optimus9/live/wan_reload.py` → `diag_wan_reload` |
| 8 | book sockets | fakeAPI's and the UI's order books: same stall restart and reconnect wait; no gap-fill, because Bybit sends a fresh snapshot on every subscribe | `orderbook.50`, 60 s stall | Joe 1002 | `optimus9/live/feed.py` `OrderBookFeed` |
| 9 | fill book age | fakeAPI records how old its book was at every fill | per fill | outage item #7 | `services/fakeapi/store.py` → `fx_fill_book` |
| 10 | service restart | every supervised service is restarted by systemd if it exits (section 5) | 5 s (`kline-sanitise` 10 s, on failure) | Joe 1005: *"yes thanks"* to systemd | `deploy/*.service`, `deploy/install_o9_units.sh` |

## 2. The four sockets

| socket | host | feeds | stall restart | gap-fill | liveness log (one line per second) |
|---|---|---|---|---|---|
| `collector` | `stream.bybit.com` | the tape | 60 s | 1,000 trades | `ws_liveness_collector.log` |
| `collector2` | `stream.bytick.com` | the tape | 60 s | 1,000 trades | `ws_liveness_collector2.log` |
| fakeAPI book | `stream.bybit.com` | fakeAPI's fill prices | 60 s | fresh snapshot | `ws_liveness_fakeapi_book.log` |
| UI book | `stream.bybit.com` | the UI's book display only | 60 s | fresh snapshot | `ws_liveness_ui_book.log` |

## 3. Checking the tape

| check | what it does | values | code |
|---|---|---|---|
| kline audit, 5 s tier | REST 1 s price samples against each 5 s bar: a bar MISSING or FROZEN (close static while the REST price moved) | every 5 s bar | `optimus9/data/kline_auditor.py` (`kline_auditor.service`) |
| kline audit, 1 m tier | Bybit's official closed 1 m bar against our tape's 1 m aggregate, tick-exact | `match` / `variance` / `incomplete` | same |
| 1 m gold check | when only the auditor's own REST samples are short, our tape is still checked against the official bar | `off_vs_kc:match`, or `variance` | Joe 1007 (b79ea43) |
| kline sanitise | reconciles the tape's OHLC against dropped TradingView CSVs | when a CSV is dropped | `kline_sanitise_service.py` (`kline-sanitise.service`) |
| recon | o9-live's signals and actions held against the backtest chain, bar for bar; section D holds the tape against the auditor | continuous (`--watch`) | `optimus9/live/octo_recon.py` (`o9-octo-recon.service`) |

## 4. Watching the path (records, not actions)

| recorder | what | values | writes | code |
|---|---|---|---|---|
| net probe | 8 targets: ping 192.168.1.1 (pfSense LAN), ping 222.152.41.165 (hop 3, ISP), ping `api.bybit.com`, ping 1.1.1.1, DNS `stream.bybit.com`, TCP `stream.bybit.com:443`, TCP `stream.bytick.com:443`, TCP `api.bybit.com:443` | every 5 s; timeouts ping 1 s, DNS 4 s, TCP 3 s; alarm after 1 failed round (hop 3: 2, Joe 10-03) | `diag_net_probe` | `optimus9/live/net_probe.py` (`o9-net-probe.service`) |
| Windows events | System, the WSL switch, NCSI, NetworkProfile, DHCP, Firewall, TCPIP/Operational; a `Tcpip` event (port exhaustion 4227 / 4231 / 4266) writes an errors-log line | every 60 s; reads only | `windows_events.log` | `optimus9/live/win_events.py` (`o9-win-events.service`) |
| pfSense posts | pfSense posts `/alert` (ping 1.1.1.1 no reply) and `/gateway` status | `/gateway` every minute | `pfsense_alerts.log` | `services/pfsense_alerts/server.py` (`pfsense-alerts.service`); in via Windows 192.168.1.48:8097 portproxy, firewall allows pfSense only |
| socket liveness | per socket per second: messages, trades, last-message age, newest trade time, pings, replies, RTT | 1 line/s | `ws_liveness_*.log` | `optimus9/data/ws_liveness.py` |
| WAN reload record | every episode: last trade, restart, decision, ssh result, first trade after | per episode | `diag_wan_reload` | `wan_reload.py` |

## 5. Alerts to Joe

| step | rule | ruling | code |
|---|---|---|---|
| errors log | one append-only file: kline_audit verdicts that are not `live` / `match`, the collector's journal warnings, errors and backfills, fakeAPI and o9-live errors, diagnostic alarms | Joe 1002: *"create an errors log … and shell monitor the log"* | `optimus9/live/feed_errors.py` → `o9live_errors.log` (`o9-feed-errors.service`) |
| /rc feed | every errors-log line and every pfSense `/alert` post becomes one alert line | Joe 1002: *"send to the /rc channel so I see it on my device"* | `optimus9/live/rc_alerts.py`, run under a Claude session Monitor, re-armed every 30 min |
| 5 s frozen | alerts only at 12 frozen bars in a row (60 s, the stall-restart threshold) | Joe 1002: *"doesn't need to be so twitchy"* | `FROZEN_RUN_BARS` |
| API throttle | a `1m incomplete` that is only Bybit's 10006 throttle (our tape and the official bar complete) alerts only with another verdict in the same minute | Joe 1007 | `ThrottleGate` |
| repeats | the same source and kind prints once, then once a minute with a count | Joe 1002 | `REPEAT_S` |
| push | the session pushes the alerts Joe would act on now; routine self-healed events are reported in the session, not pushed | Joe 1005: *"6 hourly bullet pointed summary"* | memory `rc-channel-alerts` |

## 6. Supervision

| process | supervisor | restart |
|---|---|---|
| `klinecollect` (both tick sockets, bar builder) | systemd | always, 5 s |
| `kline_auditor` | systemd | always, 5 s |
| `kline-sanitise` | systemd | on failure, 10 s |
| `pfsense-alerts` | systemd | always, 5 s |
| `o9-net-probe` | systemd | always, 5 s |
| `o9-win-events` | systemd | always, 5 s |
| `o9-wan-reload` | systemd | always, 5 s |
| `o9-octo-recon` | systemd | always, 5 s |
| `o9-feed-errors` | systemd | always, 5 s |
| `o9-ui-server` (UI + UI book) | systemd | always, 5 s |
| o9-live (`ops/run_o9live.py`) | nohup, not supervised | manual; waits on Joe's restart-with-a-position ruling |
| fakeAPI (`services.fakeapi.app`) | nohup, not supervised | manual; same |

## 7. o9-live's own guards

| guard | rule | ruling |
|---|---|---|
| unclosed bar | a decide whose window would end on a bar that has not closed is refused (an `ERROR` bar line); the next decide steps over the missed bars | Joe 1002 |
| feed gap | a gap under 5 min: opens inside it are placed, late. 5 min or more: none placed, each written as `non-trading octo-sig` | Joe 1002: *"if the gap is less than 5 minutes, yes - place the trade"* |
| operator halt | the UI's halt stops new trades; closes still run | `o9_control.halted` |
| operator flatten | the UI's flatten closes both legs on the next bar | `o9_control.flatten_req` |
| order size | dynamic leverage at 2% risk, never more than 66,000 coins per order | Joe 1005 |

## 8. Restarting a component

Restart o9-live or fakeAPI only while flat (`o9_ledger` has no open leg). Precedent: 10-02 21:16–21:21
and 10-11 21:51–21:54, 0 missing bars.

| component | how | needs |
|---|---|---|
| a systemd service | `kill <MainPID>` (`systemctl show <unit> -p MainPID --value`); systemd restarts it in 5 s | — |
| fakeAPI | `PK_DB_NAME=o9_live O9_LIVE_BOOK=FARTCOINUSDT setsid nohup python3 -m uvicorn services.fakeapi.app:app --host 127.0.0.1 --port 8098 --log-config services/fakeapi/log_config.json >> fakeapi.log 2>&1 < /dev/null & disown` | **`PK_DB_NAME=o9_live`** — without it fakeAPI opens `pk_optimizer`, has no `fx_*` tables and answers 500; o9-live then refuses every bar (10-11 21:51:50–21:52:40, 11 bars, flat, no signal lost) |
| `klinecollect` | `kill <MainPID>`; both sockets reconnect and gap-fill | — |

## 9. Open items

| item | state |
|---|---|
| the WAN reload also fires in a quiet market: Bybit had no trades, so the 50 s check cannot tell a quiet market from a dead link. Both automatic reloads so far (10-10 22:29:51, 10-11 04:47:06) were quiet markets | recorded; no limit by Joe's ruling |
| UI server socket errors are not copied into `o9live_errors.log`, so UI book drops do not reach /rc | found 10-11 |
| o9-live and fakeAPI are not under systemd | waits on Joe's ruling |
| a wide backstop stop-loss is built (`adapter.set_backstop`; fakeAPI's StopMonitor honours it) but o9-live does not set one | built, not wired |
| pfSense VPN for the UI from Joe's phone | waits on Joe's answers (WAN address type, 4 choices) |

## Change log

| date | change |
|---|---|
| 10-11 | written (Joe 1011). Reconnect wait resets to 1 s on a good connect (2c79963); fakeAPI, UI server and klinecollect restarted onto it 21:51–21:54, flat |
