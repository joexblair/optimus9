"""ArmAlerter — near-realtime alert on every o9-live ARM (Joe 0707, reconcile phase).

SRP: poll o9_state_log for fresh `state='arm'` rows, dedup the known double-logging (2-10x per bar) by kline_ms,
and emit one line per distinct arm — stdout + append to a log file. READ-ONLY; never touches the trading loop, the
cascade, or the UI (must-never-break-trading). Purpose: watch a live arm as it fires so we can diff it against the
backtest at that bar in near-realtime instead of post-hoc. Trading can be halted and arms still log — this works now.

Run (from /home/joe/thecodes):  python3 -m optimus9.live.arm_alert
Env: O9_ALERT_POLL_S (default 2.0), O9_ALERT_DB (default o9_live), O9_ALERT_LOG (default live/arm_alerts.log).
"""
from __future__ import annotations

import os
import sys
import time

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DB_NAME = os.environ.get("O9_ALERT_DB", "o9_live")
POLL_S = float(os.environ.get("O9_ALERT_POLL_S", "2.0"))
LOGFILE = os.environ.get("O9_ALERT_LOG", os.path.join(os.path.dirname(__file__), "arm_alerts.log"))


def _side(es: int) -> str:
    # es = the OOB BREACH side; the trade goes AGAINST it (bd = -es; side = _SIDE[bd]). GROUND TRUTH: o9_ledger
    # opened a Sell at the es=+1 trade event (20:42:15). So es=+1 -> SHORT, es=-1 -> LONG.
    return "SHORT" if es == 1 else "LONG" if es == -1 else "-"


def _utc(ms: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(ms) / 1000))


class ArmAlerter:
    """One responsibility: turn new arm rows into deduped alert emissions. The loop owns cadence; this owns detection."""

    def __init__(self, db, logfile=LOGFILE):
        self.db = db
        self.logfile = logfile
        self._last_kline_ms = self._current_max()   # baseline: don't replay history as alerts

    def _current_max(self) -> int:
        r = self.db.execute("SELECT MAX(kline_ms) mk FROM o9_state_log WHERE state='arm'", fetch=True)
        return int(r[0]["mk"]) if r and r[0]["mk"] is not None else 0

    def fresh_arms(self) -> list:
        """Arm rows with kline_ms strictly beyond the last seen, one per distinct kline_ms (dedups the double-log,
        across polls too — dup rows share the arm's kline_ms, so > excludes them). Ascending by bar."""
        rows = self.db.execute(
            "SELECT kline_ms, es, price, meta, MIN(created_ms) created_ms FROM o9_state_log "
            "WHERE state='arm' AND kline_ms > %s GROUP BY kline_ms, es, price, meta ORDER BY kline_ms",
            (self._last_kline_ms,), fetch=True)
        if rows:
            self._last_kline_ms = int(rows[-1]["kline_ms"])
        return rows

    def emit(self, row) -> None:
        kline_ms, created_ms = int(row["kline_ms"]), int(row["created_ms"])
        lag_s = (created_ms - kline_ms) / 1000.0
        line = "%sZ  ARM  %-5s  px=%s  kline_ms=%d  arm=%s  lag=%.1fs" % (
            _utc(kline_ms), _side(int(row["es"])), row["price"], kline_ms, row["meta"] or "?", lag_s)
        print(line, flush=True)
        try:
            with open(self.logfile, "a") as f:
                f.write(line + "\n")
        except Exception:
            pass

    def poll_once(self) -> int:
        arms = self.fresh_arms()
        for r in arms:
            self.emit(r)
        return len(arms)


def main():
    cfg = get_db_config(); cfg["database"] = DB_NAME
    db = DatabaseManager(**cfg); db.connect()
    alerter = ArmAlerter(db)
    print("[arm_alert] watching %s.o9_state_log for arms (poll %.1fs) — baseline kline_ms=%d, log=%s" % (
        DB_NAME, POLL_S, alerter._last_kline_ms, alerter.logfile), flush=True)
    while True:
        try:
            alerter.poll_once()
        except Exception as e:            # a diagnostic must never die on a transient DB blip
            print("[arm_alert] poll error: %r" % e, file=sys.stderr, flush=True)
        time.sleep(POLL_S)


if __name__ == "__main__":
    main()
