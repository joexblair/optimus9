"""O9Control — operator control state (SRP: read/write o9_control; the UI writes, the loop reads).

Sizing knobs (mode/max_order/split) + halt + flatten live in the DB (never hard-coded, never in-process
only) so the UI can change them and the running loop picks them up next bar. One row (ctl_id=1).
"""
from __future__ import annotations

import time


class O9Control:
    def __init__(self, db, clock=None):
        self.db = db
        self._now = clock or (lambda: int(time.time() * 1000))
        if not self.db.execute("SELECT 1 FROM o9_control WHERE ctl_id=1", fetch=True):
            self.db.execute("INSERT INTO o9_control (ctl_id, mode, max_order, split, updated_ms) "
                            "VALUES (1,'fixed',66000,1,%s)", (self._now(),))

    def read(self) -> dict:
        return self.db.execute("SELECT mode, max_order, split, halted, flatten_req FROM o9_control "
                               "WHERE ctl_id=1", fetch=True)[0]

    def set_sizing(self, mode=None, max_order=None, split=None):
        cur = self.read()
        self.db.execute("UPDATE o9_control SET mode=%s, max_order=%s, split=%s, updated_ms=%s WHERE ctl_id=1",
                        (mode or cur["mode"], int(max_order or cur["max_order"]),
                         int(split or cur["split"]), self._now()))

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
