"""RealtimeDriver — the realtime clock (SRP: wake at each seam+delay, fire on_bar for the just-closed bar).

Decoupled from the bar_builder: it watches kline_collection and triggers the loop when a new closed bar
appears. In live, the tape's newest row IS the just-closed bar (the forming bar isn't written yet), so
decide(now=ts+bar+delay) lands on it. delay = the seam grace (301ms). This is what makes o9-live realtime.
"""
from __future__ import annotations

import time


class RealtimeDriver:
    def __init__(self, app, price_db, tp_pk, bar_ms=5000, delay_ms=301, log=print):
        self.app = app
        self.db = price_db
        self.tp_pk = tp_pk
        self.bar = bar_ms
        self.delay = delay_ms
        self.log = log
        self._last = None

    def _latest_bar(self):
        r = self.db.execute(
            "SELECT kc_timestamp t, kc_close c FROM kline_collection WHERE kc_tp_pk=%s "
            "ORDER BY kc_timestamp DESC LIMIT 1", (self.tp_pk,), fetch=True)
        return (int(r[0]["t"]), float(r[0]["c"])) if r else (None, None)

    def _sleep_to_seam(self):
        now = int(time.time() * 1000)
        nxt = (now // self.bar + 1) * self.bar + self.delay      # next seam + grace
        time.sleep(max(0.0, (nxt - now) / 1000.0))

    def run(self, max_bars=None):
        n = 0
        while max_bars is None or n < max_bars:
            self._sleep_to_seam()
            ts, px = self._latest_bar()
            if ts is None or ts == self._last:
                continue                                         # no fresh bar yet (feed hiccup) — wait
            self._last = ts
            now_ms = ts + self.bar + self.delay                  # decision instant for the just-closed bar
            t0 = time.time()
            placed = self.app.on_bar(now_ms, px)
            self.log("bar %d close=%.5f decide=%.0fms → %d order(s)%s"
                     % (ts, px, (time.time() - t0) * 1000, len(placed),
                        (" " + str(placed)) if placed else ""))
            n += 1
