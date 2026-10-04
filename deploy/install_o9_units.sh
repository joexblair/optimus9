#!/bin/bash
# Moves the o9 diagnostics processes from nohup to systemd (Joe 10-04: "yes" to restart after a
# crash or reboot). For each unit: install it, stop the running nohup copy by its exact command
# line, then enable + start the unit. Run as root:  sudo bash deploy/install_o9_units.sh
#
# o9-live and fakeAPI are NOT in this list: o9-live refuses to start while the exchange holds a
# position its book did not open (octo_loop.py), so their move waits on that ruling and a flat book.
set -euo pipefail
cd /home/joe/thecodes

UNITS=(o9-net-probe o9-win-events o9-wan-reload o9-octo-recon o9-feed-errors o9-ui-server)
declare -A OLD=(
  [o9-net-probe]='python3 -u -m optimus9.live.net_probe'
  [o9-win-events]='python3 -u -m optimus9.live.win_events'
  [o9-wan-reload]='python3 -u -m optimus9.live.wan_reload'
  [o9-octo-recon]='python3 -u -m optimus9.live.octo_recon --watch'
  [o9-feed-errors]='python3 -m optimus9.live.feed_errors run --fakeapi-log /home/joe/thecodes/fakeapi.log --o9live-log /home/joe/thecodes/o9live_octo.log'
  [o9-ui-server]='python3 -m uvicorn optimus9.live.ui_server:app --host 0.0.0.0 --port 8099'
)

for u in "${UNITS[@]}"; do install -m 644 "deploy/$u.service" /etc/systemd/system/; done
systemctl daemon-reload

for u in "${UNITS[@]}"; do
  for pid in $(pgrep -f -x -- "${OLD[$u]}" || true); do
    kill "$pid"
    while kill -0 "$pid" 2>/dev/null; do sleep 0.2; done
    echo "$u: stopped nohup pid $pid"
  done
  systemctl enable --now "$u" 2>/dev/null
  echo "$u: $(systemctl is-active "$u")"
done
