"""stack_model — the ONE position-stack arithmetic (SRP: arithmetic only, no policy, no I/O, no DB).

Mirrors `services.fakeapi.engine.MatchingEngine` exactly, which mirrors Bybit:

    ADD   :  new_avg = (old_avg * old_sz + px * qty) / (old_sz + qty)     # engine.py:55
    CLOSE :  realized = bd * (px - avg_entry) * close_qty - fee           # engine.py:64

**There are no legs at the exchange.** A `positionIdx` holds ONE averaged position. `o9_ledger`'s per-leg rows
are bookkeeping; you cannot exit leg 3 and hold leg 1. Any model that gives each entry its own exit is pricing
trades a real account cannot take (register E1).

Extracted 0709 (Joe: option (i)) because this arithmetic existed twice — `live/replay.py` (DB-backed, one-way,
v2_walk) and `risk_stack_dist.py` (in-memory mirror, v2_walk_ad) — in a branch whose theme is two
implementations of one mechanism silently disagreeing (register E5).

Policy lives elsewhere on purpose:
  - WHETHER to add   -> RiskGovernor / the first-leg gate (`optimus9.live.risk`)
  - HOW MUCH to add  -> PositionSizer (`optimus9.live.sizing`)
  - WHEN to exit     -> lr_exit_v2 (`optimus9.analysis.lr_v2`)
This class only answers: given that an add/close happened, what is the position and what was realized?
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Position:
    """One side's averaged position. bd: +1 long, -1 short."""
    bd: int
    size: float = 0.0
    avg_entry: float = 0.0
    first_px: float = 0.0                 # entry price of the FIRST leg — the governor's reference
    n_adds: int = 0                       # legs folded in (1 = opened, never added)
    fees: float = 0.0

    @property
    def is_open(self) -> bool:
        return self.size > 0.0


@dataclass
class PositionStack:
    """Per-side averaged positions, exchange-faithful. `fee_bps` is charged per side of each fill."""
    fee_bps: float = 5.5
    realized: float = 0.0
    _pos: dict = field(default_factory=dict)          # bd -> Position

    def _fee(self, px: float, qty: float) -> float:
        return px * qty * self.fee_bps / 10_000.0

    def get(self, bd: int) -> Position | None:
        p = self._pos.get(bd)
        return p if (p and p.is_open) else None

    def gross_exposure(self, price: float) -> float:
        """Notional across BOTH sides at `price` (hedge mode: legs do not net against each other)."""
        return sum(p.size for p in self._pos.values() if p.is_open) * price

    def add(self, bd: int, px: float, qty: float) -> None:
        """Open or pyramid. Re-weights avg_entry exactly as MatchingEngine does."""
        p = self._pos.get(bd)
        fee = self._fee(px, qty)
        if p is None or not p.is_open:
            self._pos[bd] = Position(bd=bd, size=qty, avg_entry=px, first_px=px, n_adds=1, fees=fee)
        else:
            new_sz = p.size + qty
            p.avg_entry = (p.avg_entry * p.size + px * qty) / new_sz
            p.size = new_sz
            p.n_adds += 1
            p.fees += fee
        self.realized -= fee

    def close(self, bd: int, px: float, qty: float | None = None) -> float:
        """Close (default: the WHOLE averaged position — what one reversal signal does live).
        Returns realized PnL net of the exit fee. Closing a flat side is a no-op returning 0.0."""
        p = self.get(bd)
        if p is None:
            return 0.0
        q = p.size if qty is None else min(float(qty), p.size)
        fee = self._fee(px, q)
        pnl = bd * (px - p.avg_entry) * q - fee
        p.size -= q
        p.fees += fee
        self.realized += pnl
        if p.size <= 0.0:
            self._pos.pop(bd, None)
        return pnl
