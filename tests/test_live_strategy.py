"""StrategyLoop hedge wiring — each side is an independent one-way machine; opposite-side entries are
opened as the other leg (no longer dropped). Pure-logic tests: stub the producer + exit walk (no DB/window)."""
import sys
import types

import pytest

sys.path.insert(0, "/home/joe/thecodes")
from optimus9.live.strategy import StrategyLoop
from optimus9.live import strategy as strat_mod

T = 1_000_000


class FakeW:
    def __init__(self, t):
        self.ts = [t - 5000, t]
        self.px = [0.10, 0.10]


def _loop(entries):
    lp = StrategyLoop.__new__(StrategyLoop)          # bypass __init__ (no DB)
    lp._producer = lambda W, lr: entries
    lp._lr = types.SimpleNamespace(sl=0.5)
    lp._predict = False
    lp._gate_fam = "s7"
    return lp


@pytest.fixture(autouse=True)
def _no_exit_walk(monkeypatch):
    monkeypatch.setattr(strat_mod, "strand_rescue", lambda *a, **k: [])
    monkeypatch.setattr(strat_mod, "lr_exit_v2", lambda *a, **k: [])


def test_opposite_entries_same_bar_open_both_legs():
    lp = _loop([(T, 0, 1, 0), (T, 0, -1, 0)])        # Buy + Sell entry on the same bar
    out = lp.intents(FakeW(T), {})                   # flat both sides
    got = {(i.action, i.side) for i in out}
    assert ("open", "Buy") in got and ("open", "Sell") in got   # BOTH open — neither dropped


def test_opposite_entry_while_holding_opens_other_leg():
    lp = _loop([(T, 0, -1, 0)])                       # a Sell entry
    out = lp.intents(FakeW(T), {"Buy": {"side": "Buy", "size": 100}})   # holding long
    # one-way DROPPED this; hedge opens the short leg (this is the reconcile-gap fix)
    assert any(i.action == "open" and i.side == "Sell" for i in out)
    assert not any(i.action == "add" for i in out)   # not mistaken for a pyramid of the long


def test_same_side_entry_while_holding_pyramids():
    lp = _loop([(T, 0, 1, 0)])
    out = lp.intents(FakeW(T), {"Buy": {"side": "Buy", "size": 100}})
    assert any(i.action == "add" and i.side == "Buy" for i in out)
