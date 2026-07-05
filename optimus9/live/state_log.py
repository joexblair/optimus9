"""StateLogger — edge-triggered cascade state-change log (Joe 0705, phase-3 of the UI mods).

SRP: given the per-bar AGNOSTIC substrate (cascade_substrate — pure, both-sides, signed states that CANNOT diverge
from the producer) + the window, detect FLIPS on any state and write each as an event to o9_state_log, plus a
RELATIONAL snapshot (o9_state_log_line) of all cascade line values at that bar, plus a line to a log file. Warts and
all: every pure-state flip is recorded; the trade-trigger sits 1 bar before its trade (attribute by time). The
stateful latches (arm/gate/rtr) are NOT logged here — they must be producer-emitted (the DESYNC lives there; a
re-derived latch would poison the dig). The running loop WRITES; troubleshooting READS. Must never break trading.
"""
from __future__ import annotations

import time

# comprehensive cascade line snapshot per event — every line the arm/gate/finisher flow reads (value_mode-honoured)
LINES = ['s5m', 's5M', 's5r', 's7m', 's7M', 's7r', 's2M', 's3m', 's3M', 's3r',
         's4m', 's4M', 's4r', 's15m', 's15M', 's15r', 's30m', 's30M', 's30r']


class StateLogger:
    def __init__(self, o9db, logfile, clock=None):       # cfgdb dropped: substrate is registry-free (pure states)
        self.db = o9db                                   # o9_live — event tables live here
        self._now = clock or (lambda: int(time.time() * 1000))
        self.logfile = logfile
        self._last = None                                # prior-bar substrate dict (in-memory; first bar = baseline)
        self._ensure()

    def _ensure(self):
        self.db.execute("""CREATE TABLE IF NOT EXISTS o9_state_log (
            sl_id BIGINT AUTO_INCREMENT PRIMARY KEY, kline_ms BIGINT NOT NULL, state VARCHAR(32) NOT NULL,
            old_v TINYINT NOT NULL, new_v TINYINT NOT NULL, meta VARCHAR(16), mask BIGINT NOT NULL, es TINYINT NOT NULL,
            price DECIMAL(20,8), created_ms BIGINT NOT NULL, KEY k_ts (kline_ms), KEY k_state (state))""")
        try:                                             # additive for pre-meta tables (arm/gate reason, trade path)
            self.db.execute("ALTER TABLE o9_state_log ADD COLUMN meta VARCHAR(16) AFTER new_v")
        except Exception:
            pass
        self.db.execute("""CREATE TABLE IF NOT EXISTS o9_state_log_line (
            sll_id BIGINT AUTO_INCREMENT PRIMARY KEY, sl_id BIGINT NOT NULL, line VARCHAR(16) NOT NULL,
            val DECIMAL(12,4), KEY k_sl (sl_id))""")

    def record(self, W, sub, mech, mask, es, kline_ms, price):
        """Write EVERY board event this bar: (1) substrate flips (diff vs prior bar, signed old_v→new_v ∈ {-1,0,1});
        (2) producer mechanism OCCURRENCES (arm/gate/rtr/stale/trade — old_v=0→new_v=side, meta=src/reason/path).
        Each row gets a line snapshot + a file line. `mask` stored for reference (side-locked grid view). First
        call sets the substrate baseline (no flips), but mech occurrences still log."""
        prev = self._last
        self._last = dict(sub)
        rows = []                                                        # (state, old, new, meta)
        if prev is not None:
            rows += [(k, prev.get(k, 0), v, None) for k, v in sub.items() if prev.get(k, 0) != v]
        rows += [(st, 0, int(side), meta) for (st, side, meta) in (mech or [])]
        if not rows:
            return
        T = len(W.ts) - 1
        vals = {}
        for ln in LINES:
            try:
                vals[ln] = round(float(W.line(ln)[T]), 4)
            except Exception:
                pass
        now = self._now()
        for state, old, new, meta in rows:
            self.db.execute("INSERT INTO o9_state_log (kline_ms,state,old_v,new_v,meta,mask,es,price,created_ms) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (int(kline_ms), state, int(old), int(new), meta, int(mask), int(es), price, now))
            sl_id = self.db.execute("SELECT LAST_INSERT_ID() id", fetch=True)[0]['id']
            for ln, v in vals.items():
                self.db.execute("INSERT INTO o9_state_log_line (sl_id,line,val) VALUES (%s,%s,%s)", (sl_id, ln, v))
            self._append_file(kline_ms, state, old, new, meta, es, price)

    def _append_file(self, kline_ms, state, old, new, meta, es, price):
        try:
            with open(self.logfile, 'a') as f:
                f.write("%s  %-12s %+d->%+d %-4s side=%-5s px=%s\n" % (
                    time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(kline_ms) / 1000)),
                    state, old, new, (meta or ''), ('SHORT' if es == 1 else 'LONG' if es == -1 else '-'), price))
        except Exception:
            pass
