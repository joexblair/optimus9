"""
Optimus9 — parameter optimizer and (eventual) trading bot.

This package replaces the monolithic managers.py from earlier rounds.
Layers:

  optimus9.db  — Database connection and query layer.
  optimus9.data  — Exchange clients and data ingestion (Binance, Bybit, kline builders).
  optimus9.compute  — Stateless numerical machinery — indicators, PK detection, vote machines, swing analysis.
  optimus9.orchestration  — Run drivers — wires compute over data, persists results.
  optimus9.analysis  — Post-run reporting — single-run analysis, comparison across runs, outlier detection.

See round spec 260514_pk5s_spec.md and onward for design notes.
"""

# ── class re-exports ─────────────────────────────────────────────────
#
# Classes are re-exported at top level so `from optimus9 import X`
# works regardless of which subpackage X lives in.

# db
from .db.database_manager import DatabaseManager

# data
from .data.binance_client import BinanceClient
from .data.binance_backfiller import BinanceBackfiller
from .data.bybit_kline_client import BybitKlineClient
from .data.bybit_websocket_client import BybitWebSocketClient
from .data.synthetic_bar_builder import SyntheticBarBuilder
from .data.synthetic_backfiller import SyntheticBackfiller
from .data.tick_collector import TickCollector
from .data.bar_builder import BarBuilder
from .data.indicator_monitor import IndicatorMonitor

# compute
from .compute.indicator_computer import IndicatorComputer

from .compute.pk_state_computer  import PKStateComputer
from .compute.pk_gate_filter     import PKGateFilter
from .compute.pk_signal_detector import PKSignalDetector
from .compute.pk_vote_machine    import PKVoteMachine
from .compute.pk5s_gate_computer import Pk5sGateComputer


from .compute.swing_analyzer import SwingAnalyzer
from .compute.parameter_grid_builder import ParameterGridBuilder

# orchestration
from .orchestration.optimizer_runner import OptimizerRunner
from .orchestration.report_exporter import ReportExporter
from .orchestration.report_manager import ReportManager
from .orchestration.process_manager import WorkerSpec, ProcessManager

# analysis
from .analysis.analyze_manager import AnalyzeManager
from .analysis.outlier_reporter import OutlierReporter

__all__ = [
    'DatabaseManager',
    'BinanceClient',
    'BinanceBackfiller',
    'BybitKlineClient',
    'BybitWebSocketClient',
    'SyntheticBarBuilder',
    'SyntheticBackfiller',
    'TickCollector',
    'BarBuilder',
    'IndicatorMonitor',
    'IndicatorComputer',
    'PKStateComputer',
    'PKGateFilter',
    'PKSignalDetector',
    'PKVoteMachine',
    'Pk5sGateComputer',
    'SwingAnalyzer',
    'ParameterGridBuilder',
    'OptimizerRunner',
    'ReportExporter',
    'ReportManager',
    'WorkerSpec',
    'ProcessManager',
    'AnalyzeManager',
    'OutlierReporter',
]
