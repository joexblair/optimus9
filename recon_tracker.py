"""recon_tracker.py — continuous o9-live ENTRY reconcile CI (the 33h clock). Joe 0707, v2.

SCOPE = ENTRIES ONLY (Joe's refinement). o9-live fires an entry iff the backtest does. EXIT + FINANCIAL recon are
OUT: the backtest's exits are non-causal (strand_rescue keys off the future SL bar), so o9 (causal) can't match them;
entries ARE causal (arm→gate→finisher all backward-only), so 33h in-sync is reachable.

ENGINE = the cold-run (Joe): each cycle, run the REAL backtest `v2_walk_ad` fresh over a rolling window (same 8h/6h
as o9-live, so line values match) and BIDIRECTIONALLY set-diff its entry set against o9's — catching both `spurious`
(o9 fired, backtest didn't) AND `missed` (backtest fired, o9 didn't). This is the honest test; the old per-event
audit compared o9 against a re-run of o9's OWN causal window (tautological). A `margin` delay lets both settle.

Entry identity = (bar_ms, es). Clock resets on any spurious/missed. Positions/PnL are INFORMATIONAL only (they do NOT
touch the clock). Persists o9_live.recon_track (durable). Emits sparse alerts for a Monitor.
"""
import time

import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_walk_ad

SYM = "FARTCOINUSDT"
POLL_S = 60
MARGIN_S = 90                  # don't compare entries newer than this (let o9's log + the cold-run walk settle)
BUF_H, WARM_H = 8, 6           # match o9-live's StrategyLoop window (causal-invariant on the settled slice)
HEARTBEAT_S = 3600
GOAL_H = 33.0
OVERSHOOT_TOL = 0.3            # info-only #54 flag on a close past the SL


def _utc(ms):
    return time.strftime("%H:%M:%S", time.gmtime(int(ms) / 1000))


def _side(es):
    return "SHORT" if es == 1 else "LONG" if es == -1 else "-"     # es = breach side; trade = -es (ledger ground truth)


class Tracker:
    def __init__(self, dev, o9, cfg, lr, sl):
        self.dev, self.o9, self.cfg, self.lr, self.sl = dev, o9, cfg, lr, sl
        self._ensure()
        self.st = self._load()
        self._last_hb = 0

    def _ensure(self):
        self.o9.execute("""CREATE TABLE IF NOT EXISTS recon_track (
            id TINYINT PRIMARY KEY, in_sync_since_ms BIGINT, last_divergence_ms BIGINT, compared_hi_bar BIGINT,
            led_watermark BIGINT, tot_matched BIGINT, tot_spurious BIGINT, tot_missed BIGINT, updated_ms BIGINT)""")

    def _now(self):
        return int(time.time() * 1000)

    def _load(self):
        r = self.o9.execute("SELECT * FROM recon_track WHERE id=1", fetch=True)
        if r:
            return r[0]
        now = self._now()
        led = self.o9.execute("SELECT COALESCE(MAX(led_id),0) m FROM o9_ledger", fetch=True)[0]["m"]
        self.o9.execute("INSERT INTO recon_track VALUES (1,%s,NULL,%s,%s,0,0,0,%s)", (now, now, int(led), now))
        return self.o9.execute("SELECT * FROM recon_track WHERE id=1", fetch=True)[0]

    def _save(self):
        s = self.st
        self.o9.execute("UPDATE recon_track SET in_sync_since_ms=%s,last_divergence_ms=%s,compared_hi_bar=%s,"
                        "led_watermark=%s,tot_matched=%s,tot_spurious=%s,tot_missed=%s,updated_ms=%s WHERE id=1",
                        (s["in_sync_since_ms"], s["last_divergence_ms"], s["compared_hi_bar"], s["led_watermark"],
                         s["tot_matched"], s["tot_spurious"], s["tot_missed"], self._now()))

    def emit(self, line):
        print(line, flush=True)

    def _bt_entries(self, now, lo, hi):
        """Cold-run the real backtest over o9-live's window; entry set {(bar_ms, es)} with bar in (lo, hi]."""
        W = bm.BiasWindow(self.dev, now, lookback=BUF_H, warmup=WARM_H, cfg=self.cfg)
        return {(int(e[0]), int(e[1])) for e in v2_walk_ad(W, self.lr) if lo < int(e[0]) <= hi}

    def _o9_entries(self, lo, hi):
        """o9's entry set {(bar_ms, es)} from the trade events. bar = bar_ms if populated else kline_ms-5301."""
        rows = self.o9.execute("SELECT COALESCE(bar_ms, kline_ms-5301) bar, es FROM o9_state_log WHERE state='trade' "
                               "AND COALESCE(bar_ms, kline_ms-5301) > %s AND COALESCE(bar_ms, kline_ms-5301) <= %s",
                               (lo, hi), fetch=True)
        return {(int(r["bar"]), int(r["es"])) for r in rows}

    def entry_recon(self):
        now = self._now()
        lo, hi = int(self.st["compared_hi_bar"]), now - MARGIN_S * 1000
        if hi <= lo:
            return
        bt = self._bt_entries(now, lo, hi)
        o9 = self._o9_entries(lo, hi)
        matched, spurious, missed = bt & o9, o9 - bt, bt - o9
        self.st["tot_matched"] += len(matched)
        for bar, es in sorted(spurious):
            self.st["tot_spurious"] += 1
            self.emit("DIVERGENCE spurious  o9 entry @%sZ %s (es=%+d) — NO backtest entry" % (_utc(bar), _side(es), es))
        for bar, es in sorted(missed):
            self.st["tot_missed"] += 1
            self.emit("DIVERGENCE missed    backtest entry @%sZ %s (es=%+d) — o9 did NOT fire" % (_utc(bar), _side(es), es))
        if spurious or missed:
            self.st["in_sync_since_ms"] = now
            self.st["last_divergence_ms"] = now
        self.st["compared_hi_bar"] = hi

    def audit_positions(self):
        """INFO ONLY (not the clock): ledger opens/closes; flag exit-overshoot (#54) on a close past the SL."""
        wm = int(self.st["led_watermark"])
        for r in self.o9.execute("SELECT led_id,side,qty,entry_px,exit_px,net,reason,status,opened_ms,closed_ms "
                                 "FROM o9_ledger WHERE led_id>%s ORDER BY led_id", (wm,), fetch=True):
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
        pos = self.o9.execute("SELECT COUNT(*) c FROM o9_ledger WHERE status='open'", fetch=True)[0]["c"]
        eq = float(acct[0]["equity"]) if acct else 0.0
        goal = "  🎯 33h GOAL MET" if consec_h >= GOAL_H else ""
        self.emit("SYNC  entries in-sync %.1fh/%.0fh | matched=%d spurious=%d missed=%d | eq=$%.0f open_pos=%d%s" % (
            consec_h, GOAL_H, self.st["tot_matched"], self.st["tot_spurious"], self.st["tot_missed"], eq, pos, goal))

    def loop(self):
        self.emit("[recon_tracker v2] ENTRY recon (cold-run, bidirectional) — clock at %.1fh, compared_hi=%s" % (
            (self._now() - int(self.st["in_sync_since_ms"])) / 3.6e6, _utc(int(self.st["compared_hi_bar"]))))
        for r in self.o9.execute("SELECT led_id,side,entry_px,opened_ms FROM o9_ledger WHERE status='open' "
                                 "ORDER BY led_id", fetch=True):
            self.emit("  open: led%d %s @ %.5f (%s)" % (r["led_id"], r["side"], float(r["entry_px"]), _utc(int(r["opened_ms"]))))
        while True:
            try:
                self.audit_positions()      # info
                self.entry_recon()          # the clock
                self.heartbeat()
                self._save()
            except Exception as e:
                self.emit("WARN  tracker cycle error: %r" % e)
            time.sleep(POLL_S)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    o9 = DatabaseManager(**{**get_db_config(), "database": "o9_live"}); o9.connect()
    Tracker(dev, o9, bm.BiasConfig(**BASE_BIAS), lr_config(dev), float(lr_config(dev).sl)).loop()


if __name__ == "__main__":
    main()
