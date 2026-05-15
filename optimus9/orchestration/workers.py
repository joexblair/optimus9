"""
Worker entry-point functions for ProcessManager-supervised tasks.

Each function is the entry point for a multiprocessing.Process child:
  1. Resets signal handlers to default — children inherit the parent
     ProcessManager's SIGTERM/SIGINT handlers via fork(), which would
     intercept terminate() calls and prevent the child from dying. We
     want default behavior (SIGTERM terminates) in workers.
  2. Builds a fresh DatabaseManager from kwargs (MySQL connections aren't
     picklable, so we can't pass an open one across the process boundary)
  3. Connects
  4. Instantiates the worker class and runs the blocking loop
  5. Cleans up in finally (even on crash, the connection is closed)

Round: r03_260516_supervisor
"""

import signal

from ..db.database_manager import DatabaseManager
from ..data.tick_collector import TickCollector
from ..data.bar_builder    import BarBuilder


def _reset_child_signals() -> None:
    """
    Restore default SIGTERM / SIGINT disposition. Required because
    multiprocessing.Process uses fork() on Linux, which inherits the
    parent's signal handlers — ProcessManager installs custom ones that
    block normal termination.
    """
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT,  signal.SIG_DFL)


def tick_collector_worker(tp_pk: int, symbol: str, db_kwargs: dict) -> None:
    """ProcessManager entry point for TickCollector."""
    _reset_child_signals()
    db = DatabaseManager(**db_kwargs)
    db.connect()
    try:
        TickCollector(db).run(tp_pk, symbol)
    finally:
        db.disconnect()


def bar_builder_worker(tp_pk: int, db_kwargs: dict) -> None:
    """ProcessManager entry point for BarBuilder."""
    _reset_child_signals()
    db = DatabaseManager(**db_kwargs)
    db.connect()
    try:
        BarBuilder(db).run(tp_pk)
    finally:
        db.disconnect()