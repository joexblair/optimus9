#!/usr/bin/env bash
# o9svc.sh — start/stop/status the four o9-live services by PID, never by pattern.
#
# WHY THIS EXISTS
#   `pkill -f "uvicorn ...ui_server"` kills the shell that ran it. Any command run through a
#   wrapper (`bash -c '<cmd>'` — Claude Code, ssh, make, systemd ExecStart) has the pattern
#   text inside its OWN /proc/<pid>/cmdline. pkill skips only itself, not its parent, so the
#   wrapper matches, takes the SIGTERM, and the command dies mid-run (exit 143 = 128+SIGTERM).
#   Pidfiles have no such ambiguity. If you must pattern-match, anchor it: pkill -f '^\.venv/...'
#   — the wrapper's cmdline starts with /bin/bash, so ^ excludes it.
#
# Usage: ops/o9svc.sh {start|stop|restart|status} [collector|fakeapi|loop|ui|all]
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
RUN=run; mkdir -p "$RUN"
PY=.venv/bin/python
SERVICES=(collector fakeapi loop ui)

cmd_for() {
  case "$1" in
    collector) echo "$PY run.py supervisor --tp_pk 1 --symbol FARTCOINUSDT" ;;
    fakeapi)   echo "$PY -m uvicorn services.fakeapi.app:app --host 127.0.0.1 --port 8098" ;;
    loop)      echo "$PY -u ops/run_o9live.py" ;;
    ui)        echo "$PY -m uvicorn optimus9.live.ui_server:app --host 0.0.0.0 --port 8099" ;;
    *) return 1 ;;
  esac
}
env_for() {
  case "$1" in
    fakeapi) echo "PK_DB_NAME=o9_live O9_LIVE_BOOK=FARTCOINUSDT" ;;
    loop)    echo "O9_DELAY_MS=2000 O9_PRODUCER=ad" ;;
    *)       echo "" ;;
  esac
}

pidfile() { echo "$RUN/$1.pid"; }
alive()   { local p; p=$(cat "$(pidfile "$1")" 2>/dev/null) || return 1
            [ -n "$p" ] && kill -0 "$p" 2>/dev/null; }

start_one() {
  local s=$1
  if alive "$s"; then echo "  $s already running (pid $(cat "$(pidfile "$s")"))"; return 0; fi
  # shellcheck disable=SC2046
  env $(env_for "$s") nohup setsid $(cmd_for "$s") >> "$s.log" 2>&1 &
  local p=$!
  echo "$p" > "$(pidfile "$s")"
  sleep 1
  if alive "$s"; then echo "  $s started (pid $p) -> $s.log"
  else echo "  $s FAILED to start — see $s.log"; rm -f "$(pidfile "$s")"; return 1; fi
}

stop_one() {
  local s=$1 p
  p=$(cat "$(pidfile "$s")" 2>/dev/null) || { echo "  $s not running (no pidfile)"; return 0; }
  if ! kill -0 "$p" 2>/dev/null; then echo "  $s stale pidfile, cleaning"; rm -f "$(pidfile "$s")"; return 0; fi
  kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p" 2>/dev/null   # setsid -> kill the process GROUP
  for _ in $(seq 20); do kill -0 "$p" 2>/dev/null || break; sleep 0.5; done
  if kill -0 "$p" 2>/dev/null; then kill -KILL -- "-$p" 2>/dev/null || kill -KILL "$p" 2>/dev/null; echo "  $s SIGKILLed"
  else echo "  $s stopped"; fi
  rm -f "$(pidfile "$s")"
}

status_one() {
  local s=$1 p
  if alive "$s"; then p=$(cat "$(pidfile "$s")")
    printf "  %-10s up    pid=%-7s %s\n" "$s" "$p" "$(ps -o etime= -p "$p" 2>/dev/null | tr -d ' ')"
  else printf "  %-10s DOWN\n" "$s"; fi
}

action=${1:-status}; target=${2:-all}
[ "$target" = all ] && list=("${SERVICES[@]}") || list=("$target")
case "$action" in
  start)   for s in "${list[@]}"; do start_one "$s"; done ;;
  stop)    for s in "${list[@]}"; do stop_one  "$s"; done ;;
  restart) for s in "${list[@]}"; do stop_one "$s"; start_one "$s"; done ;;
  status)  for s in "${list[@]}"; do status_one "$s"; done ;;
  *) echo "usage: $0 {start|stop|restart|status} [${SERVICES[*]}|all]"; exit 2 ;;
esac
