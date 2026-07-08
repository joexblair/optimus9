"""FxStore — persistence for the mock exchange (SRP: read/write fx_* rows, no business logic).

The EXCHANGE truth: fx_order (every order), fx_position (the one-way net, pyramiding), fx_fill
(every book-walk fill). o9-live's TradeLedger is the client-side per-trade view over this net.
"""
from __future__ import annotations

import time
import uuid


class FxStore:
    def __init__(self, db, clock=None):
        self._db = db
        self._now = clock or (lambda: int(time.time() * 1000))

    # ── orders ──
    def insert_order(self, symbol, side, order_type, qty, order_link_id="", price=None,
                     reduce_only=False, status="Filled") -> str:
        oid = "fx-" + uuid.uuid4().hex[:32]
        ms = self._now()
        self._db.execute(
            "INSERT INTO fx_order (order_id, order_link_id, symbol, side, order_type, qty, price, "
            "reduce_only, order_status, created_ms, updated_ms) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (oid, order_link_id, symbol, side, order_type, qty, price, int(reduce_only), status, ms, ms))
        return oid

    # ── positions (hedge mode: one open leg per positionIdx, 1=long 2=short) ──
    def open_leg(self, symbol, position_idx=None) -> dict | None:
        """The open position row for a leg. position_idx=None → any open leg (one-way/aggregate readers)."""
        if position_idx is None:
            rows = self._db.execute(
                "SELECT * FROM fx_position WHERE symbol=%s AND status='open' ORDER BY position_id LIMIT 1",
                (symbol,), fetch=True)
        else:
            rows = self._db.execute(
                "SELECT * FROM fx_position WHERE symbol=%s AND position_idx=%s AND status='open' LIMIT 1",
                (symbol, position_idx), fetch=True)
        return rows[0] if rows else None

    def create_position(self, symbol, side, size, avg_entry, fee, position_idx=1, leverage=50) -> int:
        ms = self._now()
        self._db.execute(
            "INSERT INTO fx_position (symbol, side, position_idx, size, avg_entry, entry_count, leverage, "
            "status, opened_ms, total_fees) VALUES (%s,%s,%s,%s,%s,1,%s,'open',%s,%s)",
            (symbol, side, position_idx, size, avg_entry, leverage, ms, fee))
        return self._db.execute("SELECT LAST_INSERT_ID() id", fetch=True)[0]["id"]

    def grow_position(self, position_id, new_size, new_avg, fee_add):
        self._db.execute(
            "UPDATE fx_position SET size=%s, avg_entry=%s, entry_count=entry_count+1, "
            "total_fees=total_fees+%s WHERE position_id=%s", (new_size, new_avg, fee_add, position_id))

    def reduce_position(self, position_id, new_size, realized_add, fee_add):
        closed = new_size <= 1e-9
        self._db.execute(
            "UPDATE fx_position SET size=%s, realized_pnl=realized_pnl+%s, total_fees=total_fees+%s, "
            "status=%s, closed_ms=%s WHERE position_id=%s",
            (new_size, realized_add, fee_add, "closed" if closed else "open",
             self._now() if closed else None, position_id))

    # ── fills ──
    def insert_fill(self, order_id, position_id, symbol, side, fill, closed_qty=0.0):
        self._db.execute(
            "INSERT INTO fx_fill (order_id, position_id, symbol, side, exec_price, exec_qty, mid_price, "
            "slippage_bps, fee, closed_size, exec_ms) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (order_id, position_id, symbol, side, fill.avg_px, fill.filled_qty, fill.mid,
             fill.slip_bps, fill.fee, closed_qty, self._now()))
