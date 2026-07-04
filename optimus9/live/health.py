"""HealthStore — live health heartbeat (SRP: read/write o9_health; the running processes WRITE, the UI READS).

The mirror of O9Control's direction (control = UI writes / loop reads; health = processes write / UI reads).
Carries the cascade phase (loop, via v2_phase) + feed-health counters (loop/adapter/feed). Tape-health
(kline gaps / frozen / synthetic) is computed live in the UI from kline_collection, never stored here.
One row (health_id=1).
"""
from __future__ import annotations

import time

_BUMPABLE = ("order_rejects", "ws_reconnects", "db_reconnects")


class HealthStore:
    def __init__(self, db, clock=None):
        self.db = db
        self._now = clock or (lambda: int(time.time() * 1000))
        if not self.db.execute("SELECT 1 FROM o9_health WHERE health_id=1", fetch=True):
            self.db.execute("INSERT INTO o9_health (health_id, updated_ms) VALUES (1,%s)", (self._now(),))

    def read(self) -> dict:
        return self.db.execute("SELECT * FROM o9_health WHERE health_id=1", fetch=True)[0]

    def set_phase(self, ph: dict):
        """Write a v2_phase readout (label/tone + the three tracks)."""
        self.db.execute("UPDATE o9_health SET phase_label=%s, phase_tone=%s, arm=%s, gate=%s, gate_reason=%s, "
                        "exit_line=%s, updated_ms=%s WHERE health_id=1",
                        (ph["label"], ph["tone"], ph["arm"], ph["gate"], ph["gate_reason"],
                         ph["exit"], self._now()))

    def set_metrics(self, **kw):
        """Patch process metrics; only the passed keys change (loop_ms/rtt_ms/clock_skew_ms/pubtrade_age_ms)."""
        cur = self.read()
        cols = ("loop_ms", "rtt_ms", "clock_skew_ms", "pubtrade_age_ms")
        vals = [kw.get(c, cur[c]) for c in cols]
        self.db.execute("UPDATE o9_health SET loop_ms=%s, rtt_ms=%s, clock_skew_ms=%s, pubtrade_age_ms=%s, "
                        "updated_ms=%s WHERE health_id=1", (*vals, self._now()))

    def bump(self, field: str):
        """Increment a session counter (order_rejects / ws_reconnects / db_reconnects)."""
        if field not in _BUMPABLE:
            raise ValueError("not a bumpable health counter: %s" % field)
        self.db.execute("UPDATE o9_health SET {f}={f}+1, updated_ms=%s WHERE health_id=1".format(f=field),
                        (self._now(),))
