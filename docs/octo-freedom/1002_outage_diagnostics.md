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
| 4 | network probes every 5 s: ping 192.168.1.1 (hop 1), ping 222.152.41.165 (hop 3, the last ISP router that answers - halfway to Bybit), ping `api.bybit.com` (a CloudFront edge), ping 1.1.1.1, DNS `stream.bybit.com`, TCP `stream.bybit.com:443`, `stream.bytick.com:443`, `api.bybit.com:443`; a flip writes an errors-log line. The two hop pings added 10-03 (Joe: *"3 more pings for completeness"*); hop 3 alerts only after 2 failed rounds in a row (Joe 10-03: *"increase the tolerance to 2 pings for that hop"*), every other target after 1; route from `tracert` 10-03 17:10: 192.168.1.1 -> 125.236.192.9 -> 222.152.41.165 -> * * * -> edge, 7 hops | `o9_live.diag_net_probe` | `optimus9/live/net_probe.py` | nohup |
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
| 10-03 18:07:45 → (IrfanView, ~15 min) | Windows at 97-99% CPU: `i_view32` (IrfanView) 63-64% of all 16 cores; WSL starved. o9-live decide 1.7 s -> 5.2-6.2 s, every other bar decided, guard errors (`the window ends at ... a bar that has not closed`) on 4+ bars | no decision on a future bar, no order affected. Found on the way: the UI's latest-price query had no `kc_tp_pk` filter (1.6 s filesort over 2.57 M rows, 0.007 s filtered) - fixed 18:10:37, UI book socket now logs to `ws_liveness_ui_book.log` |
| 10-03 21:52:13 → 21:53:17 | no FARTCOIN trades on Bybit for 64 s (both tick sockets saw the same gap, every ping answered); `collector` hit 60 s and auto-restarted at 21:53:13, `collector2` was held by the 10 s gate and never restarted | a quiet market, not a fault - the first live tick-socket restart. Reconnected in 1 s, gap-fill merged 1,000 trades, WAN watchdog banked `socket restart enough`, no trade lost (collector2 stayed connected) |
| 10-03 22:40:23 → 22:41:42 | no trades for 79 s (both sockets, every ping answered); `collector` restarted 22:41:23 (60 s), `collector2` 22:41:34 (70 s, the gate's 10 s) | a quiet market again; trades back 22:41:42, 19 s after the first restart, so the WAN watchdog banked `socket restart enough` - 31 s short of a WAN reload |
| 10-03 23:28:26 → 23:29:33 | no trades for 67 s (both sockets, every ping answered); `collector2` restarted 23:29:27, `collector` held by the gate | quiet market; trades back 6 s after the restart, `socket restart enough`, no WAN reload |
| 10-04 02:25:14 → 02:26:25 | no trades for 71 s (both sockets, every ping answered); `collector2` restarted 02:26:14, `collector` held by the gate | quiet market; trades back 11 s after the restart, `socket restart enough`, no WAN reload |
| 10-04 03:57:18 → 03:58:26 | no trades for 68 s (both sockets, every ping answered); `collector2` restarted 03:58:18, `collector` held by the gate | quiet market; trades back 8 s after the restart, `socket restart enough`, no WAN reload |
| 10-04 11:50:21 → 11:51:56 | no trades for 95 s (both sockets, every ping answered); `collector` restarted 11:51:21, `collector2` 11:51:31 (the gate's 10 s) | quiet market; trades back 35 s after the first restart, `socket restart enough` - 15 s short of a WAN reload |
| 10-04 13:37:36 / 13:37:45 | REAL stalls on 2 of 4 sockets at once: fakeAPI's book socket (`stream.bybit.com`) silent from 13:37:36 and `collector2` (`stream.bytick.com`) from 13:37:45, each with half its pings unanswered (3 of 6). `collector` and the UI's book socket stayed live (every ping answered); 0 probe failures | auto-restarts 13:38:37 (book) and 13:38:45 (`collector2`), each back in 1 s. No trade lost - `collector` kept receiving trades throughout; 0 fills in the window. The first real tick-socket stall since the build: the second socket's redundancy did its job, from the other side |
| 10-04 13:52:10 → 13:53:25 | no trades for 75 s (both sockets, every ping answered); `collector` restarted 13:53:11, `collector2` 13:53:21 | quiet market; trades back 14 s after the first restart, `socket restart enough`, no WAN reload |
| 10-04 18:14:33 | `collector`'s connection dropped (`no close frame received or sent`) with its pings all answered up to then and its last trade 20 s earlier - an abrupt close, not a silent 16-min death | the client's own reconnect: 1 s wait, connected 18:14:35, gap-fill 1,000 trades. `collector2` kept receiving throughout; 0 probe failures; no trade lost |
| 10-04 23:10:45 | `collector2`'s connection dropped (`no close frame received or sent`) with its pings all answered up to then (6 of 6, rtt 204 ms); both tick sockets' last message was 23:10:37, so no trades were printing in the 8 s before the drop - an abrupt close, not a silent 16-min death | the client's own reconnect: 1 s wait, connected 23:10:47, gap-fill 1,000 trades. `collector` stayed connected throughout (its next message also 23:10:47); 0 probe failures; no trade lost |
| 10-06 06:15:50 | `collector`'s connection dropped (`no close frame received or sent`), its pings all answered up to then (6 of 6); both tick sockets' last message 06:15:47 - the same abrupt-close shape as 10-04 18:14 and 23:10 | the client's own reconnect: 2 s wait, connected 06:15:53, gap-fill 1,000 trades. `collector2` stayed connected (its next message also 06:15:53); 1 hop-3 ping missed in the window, all other probes answered; no trade lost |
| 10-06 06:17:04 | **three sockets to `stream.bybit.com` dropped in the same second** (`no close frame received or sent`): `collector` (its second drop in 74 s), fakeAPI's book and the UI's book. `collector2` on `stream.bytick.com` did NOT drop (a 3 s message gap, no event). All pings answered on every socket; no probe failed; pfSense gateway online, 0.0 % loss; Windows logged only its routine VmSwitch 285 (~53 per hour all day) | each client's own reconnect: books at 06:17:06, `collector` at 06:17:09 with a 1,000-trade gap-fill; no trade lost. (A host-side reading - only `stream.bybit.com` sockets closed - was withdrawn at 06:18:56, when the `stream.bytick.com` socket dropped too.) |
| 10-06 06:18:56 | `collector2` (`stream.bytick.com`) dropped (`no close frame received or sent`) - the 5th socket drop in 3 min 6 s (06:15:50 collector, 06:17:04 collector + both books, 06:18:56 collector2). Both Bybit hosts have now dropped, so the cluster is not one host's. The two tick sockets never dropped together; pings answered throughout; no probe failed besides one hop-3 ping at 06:15:45 | reconnected 06:18:58, gap-fill 1,000 trades; `collector` kept receiving; no trade lost. Cause not resolved |
| 10-08 20:41:32 | `collector` (`stream.bybit.com`) dropped (`no close frame received or sent`), its last message 20:41:22, pings 6 of 6 answered; `collector2` and both book sockets kept receiving (2 s gaps, no events); no probe failed | reconnected 20:41:41 after an **8 s** wait, gap-fill 1,000 trades, no trade lost. The wait has doubled on every `collector` drop since 10-04 (1, 2, 4, 8 s): `_stream_loop` resets it to 1 s only when `_connect` returns cleanly (a stall restart), never after an error on a connection that had come up |
| 10-09 11:51:55 | fakeAPI's book socket (`stream.bybit.com`, `orderbook.50`) dropped (`no close frame received or sent`), 0 messages at 11:51:56-57; the UI's book on the same stream kept receiving every second, both tick sockets kept receiving (no events); all 8 probes answered | reconnected and subscribed 11:51:58 after a **2 s** wait (its 2nd drop since 10-06 06:17:04, so the same doubling); o9-live decided every bar 11:51:40-11:52:05; no order fell in the gap (a Sell open since 11:49:10) |
| 10-09 12:03:50 | `collector2` (`stream.bytick.com`) went silent after its 12:03:50 message: **0 of 3 pings answered** (12:03:55, 12:04:15, 12:04:35), no error, no close - a real stall, the 10-04 13:37 shape. `collector` (`stream.bybit.com`) kept receiving (messages in 25 of those 60 s, 139 trades over 12:03:30-12:04:51) and both book sockets kept receiving; all 8 probes answered bar one hop-3 ping | the 60 s stall restart fired 12:04:50, connected 12:04:51 (1 s wait), gap-fill 1,000 trades 12:04:52; the tape was carried by `collector`; o9-live decided every bar 12:02:35-12:05:00 |
| 10-10 09:43:46 → 09:45:02 | no trades for 76 s (both sockets, every ping answered: 4 of 4 each; both book sockets receiving every second); `collector` restarted 09:44:47, `collector2` 09:44:57 (the gate's 10 s), each gap-filled 1,000 trades | quiet market: the tape's 5 s bars 09:43:50-09:44:55 have 0 volume and the auditor called all 17 of them `live`; trades back 09:45:02, 15 s after the first restart; the WAN check found the socket restart enough; o9-live decided every bar |
| 10-10 09:48:29 → 09:49:33 | no trades for 64 s (both sockets the same trade seconds, every ping answered: 8 of 8 each; both book sockets receiving); `collector` restarted 09:49:30 and gap-filled 1,000 trades; `collector2` needed no restart (trades back 09:49:33, inside its 10 s offset) | quiet market, 4 min after the 09:43 one: 6 of 33 tape bars since 09:47:00 carry volume; the auditor called 29 of 29 5 s bars `live` and 2 of 2 1 m bars `match`; the WAN check found the socket restart enough |
| 10-10 09:55:26 → 09:56:29 | no trades for 63 s (both sockets the same trade seconds, every ping answered: 8 of 8 each; both book sockets receiving); `collector` restarted 09:56:26 and gap-filled; `collector2` needed no restart | quiet market, the 3rd gap in 13 min (09:43, 09:48, 09:55); the auditor called 30 of 30 5 s bars `live` and 2 of 2 1 m bars `match` from 09:54; no probe failed; none since to 10:31 |
| 10-10 10:42:37 → 10:43:41 | no trades for 64 s (both sockets, every ping answered); `collector` restarted 10:43:37 and gap-filled; `collector2` needed no restart | quiet market; the auditor called 27 of 27 5 s bars `live` and 1 of 1 1 m bar `match` from 10:41:30; no probe failed |
| 10-10 10:51:44 → 10:52:47 | no trades for 63 s (both sockets, every ping answered); `collector2` restarted 10:52:44 and gap-filled; `collector` needed no restart | quiet market; the auditor called 27 of 28 5 s bars `live` (1 single `frozen`) and 1 of 1 1 m bar `match` from 10:50:30; no probe failed |
| 10-10 13:41:07 | `collector` (`stream.bybit.com`) dropped (`no close frame received or sent`), its last message 13:40:59, pings 3 of 3 answered; `collector2` and both book sockets kept receiving (no events); no probe failed | reconnected 13:41:09 after a **1 s** wait - the wait was back at 1 s because this morning's stall restarts (09:44-10:43) each returned cleanly and reset it; gap-fill 1,000 trades 13:41:10; no order in the gap (a Sell open since the 13:23:05 bar; it closed on a dr-flip at 14:16) |
| 10-10 13:59:02 → 14:00:04 | no trades for ~60 s (both sockets the same trade seconds, every ping answered); `collector2` restarted 14:00:02 and gap-filled; `collector` needed no restart | quiet market; the auditor called 26 of 26 5 s bars `live` and 2 of 2 1 m bars `match` from 13:58; no probe failed |
| 10-10 14:39:52 | fakeAPI's book socket (`stream.bybit.com`) dropped (`no close frame received or sent`), 0 messages 14:39:53-56; the UI's book on the same stream and both tick sockets kept receiving; pings 4 of 4 on every socket; no probe failed | reconnected 14:39:57 after a **4 s** wait - its 3rd drop (10-06 06:17 1 s, 10-09 11:51 2 s, now 4 s). A book socket always has messages, so it never stall-restarts and its wait is never reset: it only grows (next 8, 16, 32, 60 s). No order in the gap (a Sell open since 14:32:15) |
| 10-10 16:32 | (6 h check 10:31-16:32) 20 single 5 s `frozen` verdicts, none 2 in a row; 3 WAN checks, all `socket restart enough`; 24 hop-3 pings unanswered, every other probe answered | no further socket events after 14:39:52 |
| 10-10 19:01 → 21:56 | 8 quiet-market gaps, each with every ping answered, no probe failed and the auditor `live`/`match` throughout: 19:01:12→19:02:14, 20:22:17→20:23:27, 21:04:10→21:05:36 (both sockets restarted), 21:28:12→21:29:17, 21:36:33→21:37:41, 21:47:51→21:48:59, 21:51:12→21:52:17, 21:54:15→21:56:00 (both restarted) | every WAN check `socket restart enough`; trades came back 0, 8, 25, 4, 7, 7, 4 and 43 s after the restart (the reload waits 50 s) |
| 10-10 22:28:00 → 22:29:56 | **the first automatic WAN reload** (the only other row in `diag_wan_reload` is the 10-02 manual test). No trades for 116 s; `collector2` restarted 22:29:00, `collector` 22:29:11; no trades 50 s after the restart, so `wan_reload` ran the pfSense reload at 22:29:51 (ssh rc 0) | a QUIET MARKET, not a fault: the auditor called all 43 5 s bars `live` and 3 of 3 1 m bars `match` from 22:27, so Bybit had no trades either; pings answered on every socket. Trades back 22:29:56, 4.6 s after the reload - recorded as `trades back after reload`, but here the reload did not bring them back. During the reload: one probe round failed on 7 targets at 22:29:55 (DNS and pings), recovered next round; no socket dropped; o9-live decided every bar 22:28:00-22:31:10; the Sell open since 20:10 was untouched |
| 10-10 22:36 → 10-11 02:57 | 3 quiet-market gaps, every ping answered, no probe failed, the auditor `live`/`match` throughout: 22:35:45→22:36:53 (`collector2` restarted 22:36:45), 22:54:18→22:55:32 (both restarted, 22:55:18 / 22:55:28), 02:56:27→02:57:56 (both restarted, 02:57:27 / 02:57:37) | every WAN check `socket restart enough`; trades back 8, 14 and 29 s after the restart |
| 10-11 04:45:15 → 04:47:29 | **the 2nd automatic WAN reload**, again a quiet market: no trades for 134 s; `collector2` restarted 04:46:15, `collector` 04:46:26, both again at 04:47:16 / 04:47:26; no trades 50 s after the first restart, so `wan_reload` reloaded at 04:47:06 (ssh rc 0) | the auditor called 30 of 30 5 s bars `live` and 2 of 2 1 m bars `match` across 04:45-04:47:40 and the tape has volume only at 04:45:00, 04:45:15 and 04:47:25, so Bybit had no trades either; trades back 04:47:29, 22.1 s after the reload. One probe round failed on 7 targets during the reload, recovered next round; no book socket dropped; o9-live decided every bar; the Buy open since 03:54 untouched |
| 10-11 04:57 → 10:17 | 4 quiet-market gaps, every ping answered, no probe failed, the auditor `live`/`match` throughout: 04:57:10→04:58:42 (both restarted), 06:16:46→06:18:19 (both restarted), 08:24:20→08:25:23 (`collector` only), 10:16:29→10:17:48 (both restarted) | every WAN check `socket restart enough`; trades back 31, 33, 3 and 18 s after the restart |
| 10-11 14:25:16 → 14:25:42 | fakeAPI's book socket (`stream.bybit.com`) went silent after its 14:25:16 message, its 14:25:26 ping unanswered, then dropped 14:25:33 (`no close frame received or sent`); the UI's book on the same stream kept receiving every second (51 messages at 14:25:31, 5 of 5 pings); `collector2` 5 of 5 pings; no probe failed | reconnected 14:25:42 after an **8 s** wait - its 4th drop (1, 2, 4, 8 s), as the 10-10 14:39 row predicted; fakeAPI had no book for **26 s** (14:25:16-14:25:42) with a Buy open since 13:48:15; no order fell in the gap |
| 10-11 14:40:50 | `collector2` (`stream.bytick.com`) dropped (`no close frame received or sent`), its last message 14:40:38; every ping answered on all 4 sockets; no probe failed | reconnected 14:40:52, gap-fill 1,000 trades 14:40:53; the Buy open since 13:48:15 untouched |
| 10-11 15:11:15 → 15:12:53 | **the UI's book socket reached the 60 s wait**: silent after 15:11:15 (2 of 4 pings answered), dropped 15:11:52 (`no close frame received or sent`), waited 60 s, reconnected 15:12:53 - no book on the UI for 98 s. Its waits across drops: 10-08 15:21 2 s, 10-10 14:00 4 s, 10-10 14:10 8 s, 10-11 13:40 16 s, 10-11 14:26 32 s, 10-11 15:11 60 s (the cap). The UI server's socket errors are not in `o9live_errors.log`, so none of these reached the /rc feed | the same doubling fakeAPI's book is on (1, 2, 4, 8 s so far). The UI book feeds only the UI display, not orders. `collector` also dropped at 15:12:00 (1 s wait, back 15:12:01, gap-filled); fakeAPI's book and `collector2` kept receiving; no probe failed |
| 10-12 14:51:59 | fakeAPI's book socket dropped (`no close frame received or sent`), its last message 14:51:58; the UI's book, both tick sockets and every probe fine | **the first drop since the reconnect-wait fix (2c79963): waited 1 s**, reconnected 14:52:00, subscribed 14:52:01 - no book for ~3 s. On the old logic this 5th drop would have waited 16 s. A Sell open since 14:02:05; no order in the gap |
| 10-12 10:57:14 → 10:58:23 | no trades for 69 s (both sockets, every ping answered); `collector2` restarted 10:58:14 and gap-filled | quiet market; the WAN check found the socket restart enough |
| 10-12 13:40:00 | the UI's book socket dropped (`no close frame received or sent`), its last message 13:39:53 | 1 s wait (post-fix), reconnected 13:40:02 |
| 10-12 15:22:35 / 15:22:48 | two `stream.bybit.com` sockets dropped 13 s apart (`no close frame received or sent`): the UI's book at 15:22:35, `collector` at 15:22:48 (its last message 15:22:45); `collector2` and fakeAPI's book kept receiving; every ping and probe answered | both waited 1 s; back 15:22:37 and 15:22:50, `collector` gap-filled |
| 10-12 16:07:31 | `collector2` (`stream.bytick.com`) dropped (`no close frame received or sent`), its last message 16:07:27; every ping and probe answered | 1 s wait, back 16:07:32, gap-filled 16:07:33 |
| 10-12 16:08:14 → 16:09:11 | fakeAPI's book socket went SILENT after its 16:08:14 message (1 of 4 pings answered) while the UI's book on the same host received every second; it dropped at 16:09:09 (`no close frame received or sent`), 55 s into the silence, just short of the 60 s stall restart | 1 s wait, back 16:09:11 - no book for 57 s, the silence not the wait (the 10-11 14:25 shape, 26 s then). o9-live flat |
| 10-13 13:46:20 → 13:46:45 | `collector2` (`stream.bytick.com`) silent after 13:46:20 (1 ping unanswered) while `collector` kept receiving trades to 13:46:39; dropped 13:46:43 (`no close frame received or sent`) | 1 s wait, back 13:46:45, gap-filled; tape whole via `collector`; flat |
| 10-13 13:54:03 | `collector` (`stream.bybit.com`) dropped (`no close frame received or sent`), its last message 13:53:57 (1 ping unanswered); `collector2` and both books kept receiving; no probe failed | 1 s wait, back 13:54:05, gap-filled; flat |
| 10-13 14:48:00 | `collector` dropped (`no close frame received or sent`), its last message 14:47:55; every ping and probe answered | 1 s wait, back 14:48:02, gap-filled; a Sell open since 14:18:20, no order in the gap |
| 10-13 14:50:32 / 16:06:08 | the UI's book socket dropped twice (`no close frame received or sent`) | 1 s waits (post-fix); UI display only |
| 10-13 16:02:13 → 16:02:41 | `collector2` silent after 16:02:13 (1 ping unanswered) while `collector` kept receiving to 16:02:37; dropped 16:02:39 - the 13:46 shape again | 1 s wait, back 16:02:41, gap-filled 16:02:42; a Buy open since 15:42:00 |
| 10-13 16:04:10 | fakeAPI's book socket dropped (`no close frame received or sent`), its last message 16:04:09; the UI's book and both tick sockets kept receiving | 1 s wait, back 16:04:12 - ~3 s without a book; Buy open, no order in the gap |
| 10-13 23:47:11 → 23:48:34 | no trades for 83 s (both sockets the same last trade, 23:47:11; every ping answered, 8 of 8 and 7 of 7); `collector` restarted 23:48:11, `collector2` 23:48:21, both gap-filled; the tape holds no trade between 23:47:11.047 and 23:48:34.010 | quiet market; the WAN check found the socket restart enough (trades back 23 s after the first restart); the auditor called 33 of 33 5 s bars `live` and 2 of 2 1 m bars `match` across 23:46-23:50; no probe failed; a Buy open since 22:12, o9-live refused no bar |
| 10-13 23:58:17 → 23:59:19 | no trades for 61 s (the tape holds none between 23:58:17.926 and 23:59:19.295; every ping answered on all 4 sockets); `collector` restarted 23:59:18 and gap-filled; `collector2` needed no restart | quiet market; the WAN check found the socket restart enough (trades back 1 s after the restart); the auditor called 28 of 28 5 s bars `live` and 2 of 2 1 m bars `match` from 23:57; no probe failed; the Buy from 22:12 open, o9-live refused no bar |
| 10-14 07:02:45 | one net-probe round: 3 of 4 pings failed - 192.168.1.1 (pfSense LAN), 222.152.41.165 (hop 3), 1.1.1.1 - while `api.bybit.com` answered in 2.1 ms; the DNS lookup and the 3 TCP connects succeeded but each took 1,042-1,064 ms (3.9-22.9 ms the next round). The first LAN-ping failure since the 10-02 22:06 pfSense reboot (7 rounds with it failed since probing began 10-02 21:13) | next round (07:02:50) all 8 answered; no socket error or stall restart; both book sockets had 1 second with no message (07:02:51); pfSense `/gateway` 0.0% loss at 07:02 and 07:03; a Buy opened on the 07:02:30 bar (placed 07:02:36, before the round), o9-live refused no bar |
| 10-14 11:28:52 → 11:30:17 | no trades for 85 s (the tape holds none between 11:28:52.508 and 11:30:17.480; both sockets the same last trade; every ping answered, 9 of 9 on each); `collector2` restarted 11:29:53, `collector` 11:30:03, both gap-filled | quiet market; the WAN check found the socket restart enough (trades back 24 s after the first restart); the auditor called 33 of 33 5 s bars `live` and 2 of 2 1 m bars `match` across 11:27:30-11:32; no probe failed; a Buy open since 11:12:05, o9-live refused no bar |
| 10-14 13:48:52 → 13:49:22 | `collector` (`stream.bybit.com`) silent after 13:48:52 (that second it took 6 trades to `collector2`'s 12; its 13:49:04 ping unanswered) while `collector2` kept receiving trades every few seconds to 13:49:20; `collector` dropped 13:49:20 (`no close frame received or sent`) - the 10-13 13:46 / 16:02 shape on the other host; no probe failed | 1 s wait, back 13:49:21, gap-filled 13:49:22; tape whole via `collector2`; a Buy open since 13:22:50, o9-live refused no bar |
