"""stream_tail — emit o9-live cascade events (arm + s3s4_gate) to stdout, one line per fresh event, for a
harness Monitor to wake an agent in near-realtime (Joe 0707, reconcile phase).

SRP: tail o9_state_log for the two mechanism events that matter to the reconcile (arm = the setup; s3s4_gate =
the gate open), dedup the known double-logging by (state, kline_ms), print a terse machine-readable line each. Baseline
at startup = current max sl_id → only NEW events emit (no history replay). READ-ONLY; never touches the loop.
Distinct from arm_alert.py (that = the operator's arm-only terminal tail); this = the agent wake-feed (arm+gate).

Run (Monitor command):  cd /home/joe/thecodes && python3 -m optimus9.live.stream_tail
"""
from __future__ import annotations

import os
import sys
import time

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DB_NAME = os.environ.get("O9_STREAM_DB", "o9_live")
POLL_S = float(os.environ.get("O9_STREAM_POLL_S", "3.0"))
STATES = ("arm", "s3s4_gate")


def _side(es: int) -> str:
    return "LONG" if es == 1 else "SHORT" if es == -1 else "-"   # authoritative: strategy.py _SIDE (1=Buy, -1=Sell)


def _utc(ms: int) -> str:
    return time.strftime("%H:%M:%S", time.gmtime(int(ms) / 1000))


def main():
    cfg = get_db_config(); cfg["database"] = DB_NAME
    db = DatabaseManager(**cfg); db.connect()
    ph = "(%s)" % ",".join(["%s"] * len(STATES))
    watermark = db.execute("SELECT COALESCE(MAX(sl_id),0) m FROM o9_state_log WHERE state IN %s" % ph,
                           STATES, fetch=True)[0]["m"]
    seen = set()                                                 # (state, kline_ms) — dedups the 2-10x double-log
    print("[stream_tail] watching %s.o9_state_log %s (poll %.1fs, baseline sl_id=%d)" % (
        DB_NAME, STATES, POLL_S, watermark), flush=True)
    while True:
        try:
            rows = db.execute(
                "SELECT sl_id, kline_ms, state, es, new_v, meta, price FROM o9_state_log "
                "WHERE sl_id > %%s AND state IN %s ORDER BY sl_id" % ph,
                (watermark, *STATES), fetch=True)
            for r in rows:
                watermark = max(watermark, int(r["sl_id"]))
                key = (r["state"], int(r["kline_ms"]))
                if key in seen:
                    continue                                     # double-log dup — count it in the hunt, not here
                seen.add(key)
                if r["state"] == "arm":
                    print("EVENT arm       es=%+d %-5s px=%s src=%s  kline=%d dt=%sZ" % (
                        int(r["es"]), _side(int(r["es"])), r["price"], r["meta"] or "?",
                        int(r["kline_ms"]), _utc(r["kline_ms"])), flush=True)
                else:
                    print("EVENT s3s4_gate es=%+d %-5s reason=%s      kline=%d dt=%sZ" % (
                        int(r["es"]), _side(int(r["es"])), r["meta"] or "?",
                        int(r["kline_ms"]), _utc(r["kline_ms"])), flush=True)
        except Exception as e:                                   # a wake-feed must never die on a transient DB blip
            print("[stream_tail] poll error: %r" % e, file=sys.stderr, flush=True)
        time.sleep(POLL_S)


if __name__ == "__main__":
    main()
