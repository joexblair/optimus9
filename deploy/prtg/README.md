# PRTG monitoring — Optimus9 data pipeline

Minimum set: **2 service sensors** + **1 multi-channel SQL sensor**. PRTG 26.1.116+.

## Service sensors — is the daemon up?
Both return `1:<svc> active` / `0:<svc> DOWN`; PRTG channel **Error if value < 1**.

### A. Same machine as WSL (recommended — no SSH)
WSL2 has no sshd by default and is NAT'd, so SSH-into-WSL is a project. If PRTG runs on
the same Windows box, skip it: `check_wsl_service.bat` runs `wsl.exe systemctl is-active`.
1. Copy `check_wsl_service.bat` into PRTG's `Custom Sensors\EXEXML\` (or `\EXE\`) dir.
2. PRTG → **EXE/Script** sensor, one per service, parameter = the service name
   (`klinecollect.service`, `kline_auditor.service`).
3. **Gotcha:** PRTG's Probe Service must run as the Windows user that owns the WSL distro,
   or `wsl.exe` can't see it. (`systemctl is-active` itself needs no Linux sudo.)

### B. PRTG on a separate box (SSH)
Needs sshd installed + running in WSL, WSL2 port-forwarding, and a Linux login. A
dedicated monitoring user is the clean way (`sudo adduser prtgmon`, then SSH-key auth).
Then a PRTG **SSH Script** sensor running `check_service.sh <svc>`.

## SQL sensor (MySQL v2) — is the data healthy?
One sensor, 5 channels, from `health.sql`.

1. Copy `health.sql` into PRTG's `Custom Sensors\sql\mysql\` dir on the PRTG (Windows) box.
2. PRTG → add a **MySQL v2** sensor → DB connection to the optimus9 DB → query file
   `health.sql` → mode **"process data table"** (each column = a channel).
3. Channels + Error thresholds:

   | channel | meaning | Error |
   |---|---|---|
   | `kc_age_s` | collector writing 5s bars | > 15 |
   | `tick_age_s` | WS tick stream alive | > 60 (warn > 30) |
   | `faults_5s` | auditor 5s freeze/missing (5 min) | > 0 |
   | `variance_1m` | tape ≠ exchange — the 1m gate (10 min) | > 0 |
   | `audit_age_s` | the auditor itself alive | > 60 |

**Network:** the Windows PRTG box must reach MySQL on the Linux/WSL box — MySQL
`bind-address` open to the LAN + a `GRANT` for the PRTG user. (Local-only DB → run the
SQL sensor from a PRTG probe on the Linux box instead.)

## What each catches
- `kc_age` → the 06-04-style freeze (collector stopped writing 5s bars) — the fastest signal.
- `tick_age` → a **true WS death**. `kc_age` can't catch this alone: the bar builder writes
  flat zero-volume bars from the carried-forward price even with no ticks, so `kc_age` stays
  fresh through a dead stream. Threshold is **60s** (not 10s): FARTCOIN is low-volume, so
  natural sparse-trade quiet reaches ~38s between ticks (p99 inter-tick gap ≈ 10.5s) — a real
  death climbs into minutes, so 60s separates quiet from dead. (Tune up if a thinner market
  false-alerts; `variance_1m` also catches the resulting flat-tape drift.)
- `faults_5s` → kc writing stale closes (frozen) or missing bars, caught by the auditor.
- `variance_1m` → our tape diverged from Bybit's official 1m bar (the real data fault).
- `audit_age` → the watchdog itself died.
