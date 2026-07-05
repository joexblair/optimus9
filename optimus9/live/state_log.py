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
            old_v TINYINT NOT NULL, new_v TINYINT NOT NULL, mask BIGINT NOT NULL, es TINYINT NOT NULL,
            price DECIMAL(20,8), created_ms BIGINT NOT NULL, KEY k_ts (kline_ms), KEY k_state (state))""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS o9_state_log_line (
            sll_id BIGINT AUTO_INCREMENT PRIMARY KEY, sl_id BIGINT NOT NULL, line VARCHAR(16) NOT NULL,
            val DECIMAL(12,4), KEY k_sl (sl_id))""")

    def record(self, W, sub, mask, es, kline_ms, price):
        """Diff the substrate dict vs the prior bar; for each flipped state write a signed event (old_v→new_v ∈
        {-1,0,1}) + a line snapshot + a file line. `mask` is stored for reference (the side-locked grid view — NOT
        diffed). No-change bars are a no-op. First call sets the baseline (no log)."""
        prev = self._last
        self._last = dict(sub)
        if prev is None:
            return
        changes = [(k, prev.get(k, 0), v) for k, v in sub.items() if prev.get(k, 0) != v]
        if not changes:
            return
        T = len(W.ts) - 1
        vals = {}
        for ln in LINES:
            try:
                vals[ln] = round(float(W.line(ln)[T]), 4)
            except Exception:
                pass
        now = self._now()
        for state, old, new in changes:
            self.db.execute("INSERT INTO o9_state_log (kline_ms,state,old_v,new_v,mask,es,price,created_ms) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                            (int(kline_ms), state, int(old), int(new), int(mask), int(es), price, now))
            sl_id = self.db.execute("SELECT LAST_INSERT_ID() id", fetch=True)[0]['id']
            for ln, v in vals.items():
                self.db.execute("INSERT INTO o9_state_log_line (sl_id,line,val) VALUES (%s,%s,%s)", (sl_id, ln, v))
            self._append_file(kline_ms, state, old, new, mask, es, price)

    def _append_file(self, kline_ms, state, old, new, mask, es, price):
        try:
            with open(self.logfile, 'a') as f:
                f.write("%s  %-12s %d->%d  side=%-5s px=%s  mask=%d\n" % (
                    time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(kline_ms) / 1000)),
                    state, old, new, ('SHORT' if es == 1 else 'LONG' if es == -1 else '-'), price, mask))
        except Exception:
            pass
