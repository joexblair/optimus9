# 1002 — the 05:08 feed outage, and the recorders built to diagnose the next one

Joe 1002: *"well that's a problem. what other tests/alerts/systems can we build to better diagnose the
next outage?"*, then *"no auto reconnect yet. bake all of your ideas and get them collecting inputs.
for #3, send to the /rc channel so I see it on my device"* and *"feel free to check the windows logs"*.

## The outage, 2026-10-02 (UTC)

| what | when |
|---|---|
| last trade the collector stored | 05:08:30 |
| first `kline_audit` `5s frozen` verdict | bar 05:08:55, in `o9live_errors.log` at 05:09:21 |
| Malwarebytes reinstall + 2 WSL-switch offload changes (Windows logs) | 05:11:01 – 05:11:30 |
| collector's first error: `no close frame received or sent — reconnecting in 60s` | 05:24:35 |
| collector reconnected | 05:25:36 (no gap-fill after it: M2 in `1002_bybit_api_check.md`) |
| frozen bars in `kline_collection`, all close 0.18573, volume 0 | 205 (05:08:35 → 05:25:35) |
| anyone alerted | no |

- Cause: unknown. No record shows why the socket stopped delivering at 05:08:30.
- The client sends a ping every 20 s and never checks a reply arrives; the library keepalive is off
  (`bybit_websocket_client.py:62, 76-79`). Silence was found only when a send failed, 16 min later.
- Since `kline_audit` began (09-25 20:55) this is the only frozen span longer than 3 bars: 40 single
  bars, one 3-bar span (10-01 12:38:30), then this one.

**Against Joe's TradingView CSV** (`transfer/BYBIT_FARTCOINUSDT.P, 5S_d6c05.csv`, 10-01 00:00 → 10-02
20:35:35) — scripts and logs in `1002_frozen_tape/` (the per-bar lines, `heal_rerun.lines.npz`, are
gitignored as `*.npz`; `heal_rerun.py` rebuilds them):

| | value |
|---|---|
| frozen span: bars where the CSV has a trade | 197 of 205 |
| frozen span: CSV closes | 0.18474 – 0.18594, 83 distinct |
| frozen span: close gap to the tape | median 47 ticks, max 99, 0 bars equal |
| outside the span: closes equal, bars both traded | 28,028 of 28,031 |
| outside the span: opens differ | 21,137 — the tape opens each bar at the previous close; no line reads open/high/low |

**The chain on the CSV** (`1002_frozen_tape/heal_rerun.py`, one window, A = stored tape, B = the CSV's
closes spliced into the 205 frozen slots): A reproduces all 49 live dump lines to 20:35:35. B changes 4
WALK FIRES FROM bars — all `non-trading octo-sig` Sells from the arm set 02:33:45, while the 04:53:45
Sell was open — and no open or close. Line gaps persist on long timeframes (ws23r 6.2e-03 at 20:35:35).

**Windows logs, 04:55–05:35:** System's Tcpip provider 0 events (263 port-exhaustion events since
2025-11-28, none in the window); NCSI, DHCP, firewall 0; the WSL switch's id 285 at its ~53/hour
baseline; `Microsoft-Windows-TCPIP/Operational` is disabled on this host.

## What is collecting now

| # | recorder | writes | code | process |
|---|---|---|---|---|
| 1 | collector socket, per second: messages, trades, last-message age, newest trade `T`, pings, ping replies, RTT, rejected pongs | `ws_liveness_collector.log` | `optimus9/data/ws_liveness.py`; hook in `bybit_websocket_client.py`, wired in `tick_collector.py` | `klinecollect.service` |
| 2 | recon section D: the tape vs `kline_audit`'s REST price, every bar since live start; spans the auditor did not call `live`, with the dump lines inside each | `o9live_recon.log` `TAPE` lines, `o9_live.octo_recon_tape` | `optimus9/live/tape_check.py`, `octo_recon.py` | `octo_recon --watch` |
| 3 | alerts to Joe's device (/rc): every errors-log line (repeats once a minute with a count) and every pfSense `/alert` post. `5s frozen` alerts only at 12 consecutive bars = 60 s (Joe 1002: *"doesn't need to be so twitchy now"*); every verdict stays in the errors log | the session's shell Monitor → PushNotification | `optimus9/live/rc_alerts.py` | a Claude session Monitor, re-armed every 30 min |
| 4 | network probes every 5 s: ping 192.168.1.1, ping 1.1.1.1, DNS `stream.bybit.com`, TCP `stream.bybit.com:443`, `stream.bytick.com:443`, `api.bybit.com:443`; a flip writes an errors-log line | `o9_live.diag_net_probe` | `optimus9/live/net_probe.py` | nohup |
| 5 | pfSense gateway status every minute | `pfsense_alerts.log`, path `/gateway` | `services/pfsense_alerts/` (built) + a pfSense cron line | **waits on Joe's pfSense step** |
| 6 | the second socket, `stream.bytick.com`: from 22:24:40 INSIDE the collector and writing ticks (below). 21:15–22:24 it ran as a watch-only witness | `ws_liveness_collector2.log` (witness era: `ws_liveness_witness.log`) | `tick_collector.py` (witness era: `optimus9/live/ws_witness.py`, retired) | `klinecollect.service` |
| 7 | fakeAPI: timestamped `fakeapi.log`; its book socket's recorder; the book's age at each fill | `fakeapi.log`, `ws_liveness_fakeapi_book.log`, `o9_live.fx_fill_book` | `services/fakeapi/log_config.json`, `optimus9/live/feed.py`, `services/fakeapi/store.py` + `engine.py` | uvicorn (nohup) |
| 8 | Windows events every 60 s: System, the WSL switch, NCSI, NetworkProfile, DHCP, Firewall, TCPIP/Operational; a Tcpip event writes an errors-log line | `windows_events.log` | `optimus9/live/win_events.py` | nohup |

- Until 22:24:40 nothing here reconnected (Joe: *"no auto reconnect yet"*); the auto-restart below
  replaced that. M1, M3, M4 are not applied; I15's rejected pong is counted (`pong_err`), not fixed.
- `fx_fill` is unchanged; `fx_fill_book` sits beside it (the Bybit check's M5, built alongside).
- First 2 min after start, collector vs witness: 56 messages / 90 trades each.

## Restarts this took (o9-live flat throughout)

| process | stopped | back | how |
|---|---|---|---|
| `klinecollect.service` | 21:16:53 | 21:16:59 | SIGTERM to the supervisor, `Restart=always`. 0 missing bars 21:16:20–21:17:15; startup gap-fill merged 1,000 trades |
| fakeAPI | 21:21:17 | 21:21:19 | right after an o9-live decision |
| fakeAPI | 21:21:47 | 21:21:49 | again, after fixing #7's trade count for book messages |
| recon watcher | 21:19 | 21:19 | its own `--watch` loop |

## Related docs

| doc | relation |
|---|---|
| `docs/second_ws_spec.md` (Joe 0708) | complementary: #6 is its watch-only half. Its union of a second socket into `ticks` changes the tape and is not built |
| `docs/sunset_register.md` | complementary: names the TV-CSV → `KlineSanitiser` route (`kline_sanitise_service.py`) for repopulating frozen klines. It could rewrite 05:08:35–05:25:35 from Joe's CSV; that rewrites a tape o9-live already decided on — Joe's call, with MVP2's parked rewritten bars |
| `1002_bybit_api_check.md` | M1 (60 s reconnect) and M2 (no gap-fill after reconnect) are visible in this outage's timeline; M5 → #7 |
| `docs/o9-live-recon/RECON.md` | the errors log; section D added to the recon job |

## The second outage: Joe's pfSense reboot, 22:06

| what | when |
|---|---|
| network probes fail (1.1.1.1, DNS, every TCP target) | 22:06:33 – 22:07:28 |
| pfSense LAN (192.168.1.1) unreachable | 22:06:43 – 22:07:08 |
| last message: collector / witness / fakeAPI book | 22:06:24 / 22:06:25 / 22:06:29 |
| all three sockets: pings sent, no replies, NO error raised | 22:06 → 22:12 (and the witness, left alone, to 22:22) |
| collector + fakeAPI restarted by hand | 22:12:19 / 22:12:17 |
| the witness, untouched, raised `no close frame received or sent` | **22:22:44 = 979 s after its last message** |

- 05:08 had the same signature: last trade 05:08:30, same error at 05:24:35 = 965 s.
- The kernel's `net.ipv4.tcp_retries2` = 15 on this box.
- What interrupted the network at 05:08 is not recorded; the probes did not exist then.
- After the restart's gap-fill `ticks` held all 392 trades of 22:06:24–22:12:37, but the 69 filler bars
  the bar builder wrote during the freeze stayed frozen: it rebuilds only the last 3 bars
  (`bar_builder.py:89-99`). Joe 1002 re-filled the closes of both spans through the kline sanitiser;
  their `kc_volume` stayed 0, so `filler_invisible` still hid them from every line. The sanitiser counted
  a row with matching OHLC as a no-op whatever its volume - Joe: *"sanitiser must not be geared up to pick
  the volume discrepancy and update the row"* / *"you could use the raw csv file"*. Fixed 22:45: with
  `write_tv_volume` on, a volume difference is a change (`kline_sanitiser.py`; the service's default stays
  off). Run over the two spans cut from `processed/BYBIT_FARTCOINUSDT.P, 5S_1001to1002.csv`, logged in
  `kline_sanitise_log` as `..._frozen0508.csv` / `..._frozen2206.csv`:

| span | bars | volume > 0 after | volume total |
|---|---|---|---|
| 05:08:35 → 05:25:35 | 205 | 197 | 2,094,165 |
| 22:06:25 → 22:12:05 | 69 | 48 | 81,657 |

- o9-live decided on the frozen tape; the recon now rebuilds the backtest from the filled one, so MISMATCH /
  MOVED lines in and after the spans are the frozen tape's effect showing, not a new fault.

## Auto-restart, Joe 1002 (built and live 22:24:40)

| piece | value | where |
|---|---|---|
| tick sockets | `stream.bybit.com` + `stream.bytick.com`, both write `ticks`, merged by trade id | `tick_collector.py`, `O9_TICK_ENDPOINTS` |
| restart trigger | 60 s with no topic message (trades); ping replies do not count | `bybit_websocket_client.py` `_watchdog`, `stall_s` |
| offset | a shared gate: no socket restarts within 10 s of another's restart | `RestartGate`, `O9_TICK_RESTART_OFFSET_S` |
| after a restart | the REST recent-trade gap-fill (1,000 trades; ~5.3 min at the 7-day mean of 3.15 trades/s) | `TickCollector._backfill_recent` via `on_connect` |
| not done (Joe 1002) | the reconnect-wait reset (M1); rebuilding the bars written during a freeze | — |
| fakeAPI book socket | same trigger, 60 s; no gap-fill (Bybit sends a fresh snapshot on subscribe) | `optimus9/live/feed.py`, `O9_BOOK_STALL_S` |
| tests | S1–S4 against a local server that goes silent with the connection open | `tests/test_ws_stall.py` |

- A stall restart returns cleanly from the socket, so it reconnects at once; a failed reconnect then
  waits the existing doubling delay (M1, unchanged).
- Measured 7 days of `ticks` (1,926,820 trades): gaps over 60 s between trades - 2, one the 05:08
  outage, one exactly 60.0 s (09-26 23:56:00). Over 45 s - 2. Over 30 s - 53.
- First 40 s on two sockets: 23 messages / 33 trades on each.

## WAN reload, Joe 1002 (watchdog live 22:30; pfSense side waits on Joe)

Joe 1002: *"if the websocket reset makes no diff for another 50s, then restart the wan connection"*; how:
*"SSH, one command"*; guard: *"Trades only, no limit ... if the tick flow begins everytime the int is reset,
then we have infra issues to troubleshoot"*.

| piece | value |
|---|---|
| trigger | the first socket `stall-restart`, then no trade on either socket for 50 s (= 110 s after the last trade) |
| action | `ssh admin@192.168.1.1` with `~/.ssh/pfsense_wan_reload`; the key's forced command is `/usr/local/sbin/pfSctl -c 'interface reload wan'` |
| limit | none, on purpose: every episode is evidence |
| record | `o9_live.diag_wan_reload`: outcome (`socket restart enough` / `wan reloaded` / `wan reload failed` / `trades back after reload`), `recovery_s` |
| alerts | each reload and each recovery writes an errors-log line -> /rc |
| code | `optimus9/live/wan_reload.py`; rule tests W1-W5 `tests/test_wan_reload.py` |
| SNMP | not used: pfSense's SNMP page sets a read community only; a write community needs a hand-edited bsnmpd config the GUI regenerates, sent in clear text |

- SSH on pfSense: key in the admin user with the forced command; Secure Shell enabled 1002 ~22:58; host key
  ED25519 `SHA256:PqCCHJpmCF7CIX1g9kuBnLgZ2mTqTQistpGMuzTjPBU` pinned in `~/.ssh/known_hosts`.

| test reload, Joe 1002 (*"test"*) | value |
|---|---|
| sent | 22:59:38.232, ssh rc 0, pfSctl answered `OK` in 0.07 s |
| probes failing (1.1.1.1, DNS, every TCP target) | one 5 s round: 22:59:43; all back 22:59:48 |
| down, Joe 1002 watching it | *"down for ~6 seconds"* - inside the probes' bound (one failed 5 s round = under 10 s) |
| pfSense LAN (192.168.1.1) | never failed |
| WAN_PPPOE after it | online, 0.0% loss, public source address unchanged (210.54.34.214) |
| both tick sockets, 100 s after | kept flowing: 42 messages / 53 trades each, longest silence 19.2 s, no restart, no error |
| fakeAPI book socket | kept flowing, longest silence 4.2 s |
| banked | `o9_live.diag_wan_reload`, outcome `manual test` |

## Live events after the build

| when (UTC) | event | outcome |
|---|---|---|
| 10-03 10:49:08 | `net_probe` lost one ping to 1.1.1.1; every other probe ok | back at 10:49:13; sockets unaffected |
| 10-03 12:03:30 → 12:04:29 | fakeAPI's book socket silent 60 s, its pings unanswered (4 sent, 1 reply); tick sockets and probes fine (10/10 replies, 0 failures) | auto-restart 12:04:29, reconnected 12:04:30; 0 orders during it. The first live auto-restart; a single-socket stall, not the network |
