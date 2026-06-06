# PRTG monitoring — Optimus9 data pipeline

Minimum set: **2 service sensors** + **1 multi-channel SQL sensor**. PRTG 26.1.116+.

## Service sensors (SSH Script) — is the daemon up?
`check_service.sh` returns `1:<svc> active` / `0:<svc> DOWN`.

1. It's already on the Linux box at `deploy/prtg/check_service.sh` — `chmod +x` it.
2. PRTG → add an **SSH Script** sensor on the Linux device, one per service:
   - script `check_service.sh`, parameter `klinecollect.service`
   - script `check_service.sh`, parameter `kline_auditor.service`
3. Channel: **Error if value < 1**.
4. The SSH user needs no sudo (`systemctl is-active` is read-only).

## SQL sensor (MySQL v2) — is the data healthy?
One sensor, 5 channels, from `health.sql`.

1. Copy `health.sql` into PRTG's `Custom Sensors\sql\mysql\` dir on the PRTG (Windows) box.
2. PRTG → add a **MySQL v2** sensor → DB connection to the optimus9 DB → query file
   `health.sql` → mode **"process data table"** (each column = a channel).
3. Channels + Error thresholds:

   | channel | meaning | Error |
   |---|---|---|
   | `kc_age_s` | collector writing 5s bars | > 15 |
   | `tick_age_s` | WS tick stream alive | > 10 |
   | `faults_5s` | auditor 5s freeze/missing (5 min) | > 0 |
   | `variance_1m` | tape ≠ exchange — the 1m gate (10 min) | > 0 |
   | `audit_age_s` | the auditor itself alive | > 60 |

**Network:** the Windows PRTG box must reach MySQL on the Linux/WSL box — MySQL
`bind-address` open to the LAN + a `GRANT` for the PRTG user. (Local-only DB → run the
SQL sensor from a PRTG probe on the Linux box instead.)

## What each catches
- `kc_age` / `tick_age` → the 06-04-style freeze (stopped writing) — the fastest signal.
- `faults_5s` → kc writing stale closes (frozen) or missing bars, caught by the auditor.
- `variance_1m` → our tape diverged from Bybit's official 1m bar (the real data fault).
- `audit_age` → the watchdog itself died.
