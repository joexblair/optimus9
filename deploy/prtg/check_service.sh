#!/bin/bash
# PRTG SSH Script sensor — systemd service liveness.  arg1 = service name.
# Output "<value>:<message>": 1 = active, 0 = down.  PRTG channel: Error if value < 1.
# (systemctl is-active is read-only — the SSH user needs no sudo.)
if systemctl is-active --quiet "$1"; then
  echo "1:$1 active"
else
  echo "0:$1 DOWN"
fi
