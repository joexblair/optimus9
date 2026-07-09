"""O9Ledger — o9-live's OWN bookkeeping (SRP: o9's trade record + running tally, from exchange fills).

NOT the exchange's fx_* (that's the exchange's truth). o9 records what IT observed — entry/exit fills it
got back via the adapter — as independent-rows trades (Joe's UI model) and computes its OWN equity tally.
The two are reconciled to the exchange daily (see the recon task); the exchange stays authoritative for
the live position, o9's ledger drives the UI + sizing. Taker rate is a ctor arg (config, not hard-coded).
"""
from __future__ import annotations

import time
from datetime import datetime, timezone


class O9Ledger:
    def __init__(self, db, symbol, start_equity=500.0, taker_bps=5.5, clock=None):
        self.db = db
        self.symbol = symbol
        self._taker = taker_bps
        self._now = clock or (lambda: int(time.time() * 1000))
        if not self.db.execute("SELECT 1 FROM o9_account WHERE acct_id=1", fetch=True):
            self.db.execute("INSERT INTO o9_account (acct_id, equity, updated_ms) VALUES (1,%s,%s)",
                            (start_equity, self._now()))

    # ── account (o9's tally) ──
    def equity(self) -> float:
        return float(self.db.execute("SELECT equity e FROM o9_account WHERE acct_id=1", fetch=True)[0]["e"])

    # ── position (o9's own view, summed from its open trades) ──
    def open_position(self) -> dict | None:
        r = self.db.execute("SELECT side, SUM(qty) q FROM o9_ledger WHERE symbol=%s AND status='open' "
                            "GROUP BY side", (self.symbol,), fetch=True)
        return {"side": r[0]["side"], "size": float(r[0]["q"])} if r else None

    # ── trades ──
    def record_open(self, side, qty, entry_px, order_id, reason, ts):
        self.db.execute("INSERT INTO o9_ledger (symbol, side, qty, entry_px, entry_order_id, reason, status, "
                        "opened_ms) VALUES (%s,%s,%s,%s,%s,%s,'open',%s)",
                        (self.symbol, side, qty, entry_px, order_id, reason, ts))

    def last_trade_ms(self) -> int:
        """Most recent trade open time (for the latch-reset troubleshooting test); 0 if none."""
        r = self.db.execute("SELECT MAX(opened_ms) m FROM o9_ledger WHERE symbol=%s", (self.symbol,), fetch=True)
        return int(r[0]["m"]) if r and r[0]["m"] else 0

    def open_legs(self) -> list:
        """Per-leg open trades (option B per-leg SL needs each leg's own entry). Aggregate = open_position()."""
        return self.db.execute("SELECT led_id, side, qty, entry_px, opened_ms FROM o9_ledger "
                               "WHERE symbol=%s AND status='open' ORDER BY opened_ms", (self.symbol,), fetch=True)

    def _close_rows(self, rows, exit_px, order_id, ts, close_reason='exit') -> float:
        """Close the given open rows at exit_px; compute o9's realized per trade; tally the account; and write a
        durable copy of each closed trade to o9_trade_archive (which /api/reset does NOT touch)."""
        total = 0.0
        for t in rows:
            d = 1.0 if t["side"] == "Buy" else -1.0
            qty, entry = float(t["qty"]), float(t["entry_px"])
            gross = d * (exit_px - entry) * qty
            fee = (entry + exit_px) * qty * self._taker / 10000.0           # entry+exit taker estimate
            net = gross - fee
            total += net
            self.db.execute("UPDATE o9_ledger SET exit_px=%s, exit_order_id=%s, gross=%s, net=%s, fee=%s, "
                            "status='closed', closed_ms=%s WHERE led_id=%s",
                            (exit_px, order_id, round(gross, 8), round(net, 8), round(fee, 8), ts, t["led_id"]))
            self._archive(t, exit_px, ts, gross, net, fee, close_reason)
        if rows:
            self.db.execute("UPDATE o9_account SET equity=equity+%s, realized_total=realized_total+%s, "
                            "trade_count=trade_count+%s, updated_ms=%s WHERE acct_id=1",
                            (round(total, 8), round(total, 8), len(rows), self._now()))
        return total

    def _archive(self, t, exit_px, ts, gross, net, fee, close_reason):
        """Durable copy of one closed trade → o9_trade_archive with a mmdd_NN label (the pine-emit label;
        mmdd = the trade's OPEN day, NN = 1-up within that day). This table survives /api/reset — the persistent
        trade history for the stop-tool. See docs/o9live_changelog.md."""
        mmdd = datetime.fromtimestamp(int(t["opened_ms"]) / 1000, timezone.utc).strftime("%m%d")
        nn = self.db.execute("SELECT COUNT(*) c FROM o9_trade_archive WHERE label LIKE %s",
                             (mmdd + "\\_%",), fetch=True)[0]["c"] + 1
        label = "%s_%02d" % (mmdd, nn)
        self.db.execute(
            "INSERT INTO o9_trade_archive (label,symbol,side,position_idx,qty,entry_px,exit_px,entry_ms,exit_ms,"
            "gross,net,fee,mae,open_reason,close_reason,archived_ms) VALUES "
            "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (label, self.symbol, t["side"], 1 if t["side"] == "Buy" else 2, t["qty"], t["entry_px"], exit_px,
             t["opened_ms"], ts, round(gross, 8), round(net, 8), round(fee, 8), t.get("mae"),
             t.get("reason"), close_reason, self._now()))

    def record_close(self, exit_px, order_id, ts) -> float:
        """Close ALL open o9 trades (one-way net exit / shared reversal-TP)."""
        opens = self.db.execute("SELECT * FROM o9_ledger WHERE symbol=%s AND status='open' ORDER BY opened_ms",
                                (self.symbol,), fetch=True)
        return self._close_rows(opens, exit_px, order_id, ts)

    def record_close_side(self, side, exit_px, order_id, ts) -> float:
        """Close all open o9 trades on ONE side (hedge: a side's reversal-TP closes only that side's stack;
        the opposite leg lives on independently)."""
        opens = self.db.execute("SELECT * FROM o9_ledger WHERE symbol=%s AND side=%s AND status='open' "
                                "ORDER BY opened_ms", (self.symbol, side), fetch=True)
        return self._close_rows(opens, exit_px, order_id, ts)

    def open_by_side(self) -> dict:
        """o9's open position per side (hedge view): {'Buy': {'side','size'}, 'Sell': {...}} — only open sides."""
        rows = self.db.execute("SELECT side, SUM(qty) q FROM o9_ledger WHERE symbol=%s AND status='open' "
                               "GROUP BY side", (self.symbol,), fetch=True)
        return {r["side"]: {"side": r["side"], "size": float(r["q"])} for r in rows}

    def record_close_leg(self, led_id, exit_px, order_id, ts) -> float:
        """Close ONE leg (option B per-leg SL) — the rest of the pyramid stack stays open. Idempotent
        (selects status='open' by led_id → a second call is a no-op)."""
        rows = self.db.execute("SELECT * FROM o9_ledger WHERE led_id=%s AND status='open'", (led_id,), fetch=True)
        return self._close_rows(rows, exit_px, order_id, ts, close_reason='SL')

    # ── decision audit (o9's own log) ──
    def log_decision(self, kline_ms, action, reason="", order_id=None):
        self.db.execute("INSERT INTO o9_decision (kline_ms, action, reason, order_id, created_ms) "
                        "VALUES (%s,%s,%s,%s,%s)", (kline_ms, action, reason, order_id, self._now()))
