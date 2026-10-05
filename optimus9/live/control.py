"""O9Control — operator control state (SRP: read/write o9_control; the UI writes, the loop reads).

Sizing knobs (mode/max_order/split/risk_pct/drag_pct) + halt + flatten live in the DB (never hard-coded, never in-process
only) so the UI can change them and the running loop picks them up next bar. One row (ctl_id=1).
"""
from __future__ import annotations

import time


class O9Control:
    def __init__(self, db, clock=None):
        self.db = db
        self._now = clock or (lambda: int(time.time() * 1000))
        self._ensure_columns()
        if not self.db.execute("SELECT 1 FROM o9_control WHERE ctl_id=1", fetch=True):
            self.db.execute("INSERT INTO o9_control (ctl_id, mode, max_order, split, updated_ms) "
                            "VALUES (1,'fixed',66000,1,%s)", (self._now(),))

    # dynamic_leverage's two knobs (Joe 1005). risk_pct 2.0 = % of equity at risk per entry, the classic
    # risk-per-trade convention (1005_knobs.md s3; Joe 1005 asked for "a safe solution" and approved the
    # table). drag_pct 0.1975 = round trip, 2 x 5.50 bps taker + 8.75 bps slippage at 22,000 coins
    # (docs/strat-3-r-oob/spec.md:77). Added in place, idempotent, defaults only - no row is rewritten.
    _COLUMNS = (('risk_pct', "DECIMAL(6,4) NOT NULL DEFAULT 2.0000 AFTER split"),
                ('drag_pct', "DECIMAL(6,4) NOT NULL DEFAULT 0.1975 AFTER risk_pct"))

    def _ensure_columns(self):
        have = {r['c'] for r in self.db.execute(
            "SELECT COLUMN_NAME c FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
            "AND TABLE_NAME='o9_control'", fetch=True)}
        for col, ddl in self._COLUMNS:
            if col not in have:
                self.db.execute("ALTER TABLE o9_control ADD COLUMN %s %s" % (col, ddl))

    def read(self) -> dict:
        return self.db.execute("SELECT mode, max_order, split, risk_pct, drag_pct, halted, flatten_req "
                               "FROM o9_control WHERE ctl_id=1", fetch=True)[0]

    def set_sizing(self, mode=None, max_order=None, split=None, risk_pct=None, drag_pct=None):
        cur = self.read()
        self.db.execute("UPDATE o9_control SET mode=%s, max_order=%s, split=%s, risk_pct=%s, drag_pct=%s, "
                        "updated_ms=%s WHERE ctl_id=1",
                        (mode or cur["mode"], int(max_order or cur["max_order"]), int(split or cur["split"]),
                         float(risk_pct or cur["risk_pct"]), float(drag_pct or cur["drag_pct"]), self._now()))

    def request_flatten(self, halt: bool):
        if halt:                                             # kill-switch: close + stop trading
            self.db.execute("UPDATE o9_control SET flatten_req=1, halted=1, updated_ms=%s WHERE ctl_id=1",
                            (self._now(),))
        else:                                                # plain exit: close, keep trading
            self.db.execute("UPDATE o9_control SET flatten_req=1, updated_ms=%s WHERE ctl_id=1", (self._now(),))

    def clear_flatten(self):
        self.db.execute("UPDATE o9_control SET flatten_req=0, updated_ms=%s WHERE ctl_id=1", (self._now(),))

    def resume(self):
        self.db.execute("UPDATE o9_control SET halted=0, updated_ms=%s WHERE ctl_id=1", (self._now(),))

    def halt(self):                                          # stop trading (no close); clear any stale flatten
        self.db.execute("UPDATE o9_control SET halted=1, flatten_req=0, updated_ms=%s WHERE ctl_id=1",
                        (self._now(),))
