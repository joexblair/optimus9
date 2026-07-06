"""recon_tracker.py — continuous o9-live<->backtest reconcile CI (Joe 0707).

THE 33h CLOCK. A daemon that audits o9-live against the backtest continuously and emits a SPARSE alert stream (for a
harness Monitor) — divergences, position open/close, and an hourly in-sync heartbeat — instead of the noisy per-arm
feed. Reuses recon_suite's Repro/audit_event (SRP: one-shot audit logic lives there; this owns the loop + persistence
+ alerting). Persists to o9_live.recon_track (survives tracker restarts) so the consecutive-in-sync counter is durable.

GOAL: o9-live reconciles (every arm/gate/trade matches the backtest, bit-exact lines) for 33 CONTINUOUS hours.
`in_sync_since` resets on any divergence; consecutive_h = now - in_sync_since. Goal met when consecutive_h >= 33.

Emits (stdout = Monitor events):
  DIVERGENCE  — an o9 event the backtest doesn't reproduce, or a line-fidelity miss  → resets the 33h clock
  POSITION    — a ledger open/close (with EXIT-OVERSHOOT flag when a close blows past the SL = the #54 signature)
  SYNC        — hourly heartbeat: consecutive in-sync hours + counts + equity + open position
  WARN        — health (multi-process loop, etc.)

Run (Monitor command):  cd /home/joe/thecodes && python3 -m ... no; python3 recon_tracker.py
"""
import time

import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.live.strategy import StrategyLoop
import recon_suite as rs

SYM = "FARTCOINUSDT"
POLL_S = 60
MAX_AUDIT = 25                 # cap events audited per cycle (window build is ~1-2s each); log if capped
OVERSHOOT_TOL = 0.3            # a close worse than -(sl+tol)% = #54 exit-overshoot
HEARTBEAT_S = 3600
GOAL_H = 33.0


def _utc(ms):
    return time.strftime("%H:%M:%S", time.gmtime(int(ms) / 1000))


class Tracker:
    def __init__(self, dev, o9, repro, sl):
        self.dev, self.o9, self.repro, self.sl = dev, o9, repro, sl
        self._ensure()
        self.st = self._load()
        self._last_hb = 0

    def _ensure(self):
        self.o9.execute("""CREATE TABLE IF NOT EXISTS recon_track (
            id TINYINT PRIMARY KEY, in_sync_since_ms BIGINT, last_divergence_ms BIGINT, ev_watermark BIGINT,
            led_watermark BIGINT, tot_matched BIGINT, tot_spurious BIGINT, tot_fidelity BIGINT, updated_ms BIGINT)""")

    def _now(self):
        return int(time.time() * 1000)

    def _load(self):
        r = self.o9.execute("SELECT * FROM recon_track WHERE id=1", fetch=True)
        if r:
            return r[0]
        now = self._now()
        # baseline: start the clock now; watermarks at current max so we audit only NEW events forward
        ev = self.o9.execute("SELECT COALESCE(MAX(sl_id),0) m FROM o9_state_log", fetch=True)[0]["m"]
        led = self.o9.execute("SELECT COALESCE(MAX(led_id),0) m FROM o9_ledger", fetch=True)[0]["m"]
        self.o9.execute("INSERT INTO recon_track VALUES (1,%s,%s,%s,%s,0,0,0,%s)",
                        (now, None, int(ev), int(led), now))
        return self.o9.execute("SELECT * FROM recon_track WHERE id=1", fetch=True)[0]

    def _save(self):
        s = self.st
        self.o9.execute("UPDATE recon_track SET in_sync_since_ms=%s,last_divergence_ms=%s,ev_watermark=%s,"
                        "led_watermark=%s,tot_matched=%s,tot_spurious=%s,tot_fidelity=%s,updated_ms=%s WHERE id=1",
                        (s["in_sync_since_ms"], s["last_divergence_ms"], s["ev_watermark"], s["led_watermark"],
                         s["tot_matched"], s["tot_spurious"], s["tot_fidelity"], self._now()))

    def emit(self, line):
        print(line, flush=True)

    def audit_events(self):
        """New arm/gate/trade events since the watermark → audit each against the backtest; alert on divergence."""
        wm = int(self.st["ev_watermark"])
        rows = self.o9.execute(
            "SELECT MIN(sl_id) sl_id,kline_ms,state,es,meta FROM o9_state_log WHERE sl_id>%s AND "
            "state IN ('arm','s3s4_gate','trade') GROUP BY kline_ms,state,es,meta ORDER BY MIN(sl_id) LIMIT %s",
            (wm, MAX_AUDIT), fetch=True)
        maxsl = self.o9.execute("SELECT COALESCE(MAX(sl_id),%s) m FROM o9_state_log WHERE sl_id>%s AND "
                                "state IN ('arm','s3s4_gate','trade')", (wm, wm), fetch=True)[0]["m"]
        if len(rows) >= MAX_AUDIT:
            self.emit("WARN  audit hit MAX_AUDIT=%d this cycle — backlog, not silently dropped" % MAX_AUDIT)
        for r in rows:
            bt, results = rs.audit_event(self.dev, self.o9, self.repro, r)
            rep = next(v for nm, v, d in results if nm == "event_reproduced")
            fid = next(v for nm, v, d in results if nm == "line_fidelity")
            det = next(d for nm, v, d in results if nm == "event_reproduced")
            if rep and fid is not False:
                self.st["tot_matched"] += 1
            else:
                kind = "O9-SPURIOUS" if not rep else "FIDELITY"
                self.st["tot_spurious" if not rep else "tot_fidelity"] += 1
                self.st["in_sync_since_ms"] = self._now()          # divergence resets the 33h clock
                self.st["last_divergence_ms"] = self._now()
                self.emit("DIVERGENCE %s  %s %s es=%+d %s  | %s" % (
                    kind, _utc(int(r["kline_ms"])), r["state"], int(r["es"]), r["meta"] or "", det))
        self.st["ev_watermark"] = int(maxsl) if rows else wm

    def audit_positions(self):
        """New ledger rows → position open/close alerts; flag exit-overshoot (a close past the SL = #54)."""
        wm = int(self.st["led_watermark"])
        rows = self.o9.execute("SELECT led_id,side,qty,entry_px,exit_px,net,reason,status,opened_ms,closed_ms "
                               "FROM o9_ledger WHERE led_id>%s ORDER BY led_id", (wm,), fetch=True)
        for r in rows:
            if r["status"] == "open":
                self.emit("POSITION OPEN  led%d %s qty=%.0f @ %.5f (%s)" % (
                    r["led_id"], r["side"], float(r["qty"]), float(r["entry_px"]), _utc(int(r["opened_ms"]))))
            else:
                ep, xp = float(r["entry_px"]), float(r["exit_px"] or 0)
                d = 1.0 if r["side"] == "Buy" else -1.0
                ret = (xp - ep) / ep * 100.0 * d if ep else 0.0
                flag = "  ⚠ EXIT-OVERSHOOT (past %.1f%% SL)" % self.sl if ret < -(self.sl + OVERSHOOT_TOL) else ""
                self.emit("POSITION CLOSE led%d %s ret=%+.2f%% net=%+.2f reason=%s (%s)%s" % (
                    r["led_id"], r["side"], ret, float(r["net"] or 0), r["reason"], _utc(int(r["closed_ms"])), flag))
            wm = int(r["led_id"])
        self.st["led_watermark"] = wm

    def heartbeat(self):
        now = self._now()
        if now - self._last_hb < HEARTBEAT_S * 1000:
            return
        self._last_hb = now
        consec_h = (now - int(self.st["in_sync_since_ms"])) / 3.6e6
        acct = self.o9.execute("SELECT equity FROM o9_account WHERE acct_id=1", fetch=True)
        pos = self.o9.execute("SELECT COUNT(*) c, COALESCE(SUM(qty),0) q FROM o9_ledger WHERE status='open'",
                              fetch=True)[0]
        eq = float(acct[0]["equity"]) if acct else 0.0
        goal = "  🎯 33h GOAL MET" if consec_h >= GOAL_H else ""
        self.emit("SYNC  in-sync %.1fh/%.0fh | matched=%d spurious=%d fidelity=%d | eq=$%.0f | open_pos=%d%s" % (
            consec_h, GOAL_H, self.st["tot_matched"], self.st["tot_spurious"], self.st["tot_fidelity"],
            eq, int(pos["c"]), goal))

    def loop(self):
        self.emit("[recon_tracker] started — 33h clock at %.1fh, ev_wm=%s led_wm=%s (backtest=truth)" % (
            (self._now() - int(self.st["in_sync_since_ms"])) / 3.6e6, self.st["ev_watermark"],
            self.st["led_watermark"]))
        for r in self.o9.execute("SELECT led_id,side,qty,entry_px,opened_ms FROM o9_ledger WHERE status='open' "
                                 "ORDER BY led_id", fetch=True):          # startup snapshot (watermark hides these)
            self.emit("  open: led%d %s qty=%.0f @ %.5f (%s)" % (
                r["led_id"], r["side"], float(r["qty"]), float(r["entry_px"]), _utc(int(r["opened_ms"]))))
        while True:
            try:
                self.audit_positions()      # positions first (money events), cheap
                self.audit_events()         # then the cascade audit (window builds)
                self.heartbeat()
                self._save()
            except Exception as e:
                self.emit("WARN  tracker cycle error: %r" % e)
            time.sleep(POLL_S)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    o9c = get_db_config(); o9c["database"] = "o9_live"; o9 = DatabaseManager(**o9c); o9.connect()
    strat = StrategyLoop(dev, bm.BiasConfig(**BASE_BIAS), lr_config(dev), SYM, buffer_hours=8, warmup_hours=6)
    Tracker(dev, o9, rs.Repro(dev, strat), float(lr_config(dev).sl)).loop()


if __name__ == "__main__":
    main()
