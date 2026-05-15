"""
WorkerSpec, ProcessManager — see class docstring for purpose, Pine alignment, and design notes.
"""


"""
managers.py — PK Optimizer
All process classes. One responsibility per class.
Every class calls get_logger(self.__class__.__name__).

Terminology:
  OOB  = out of boundary (indicator has crossed high/low threshold)
  IB   = in boundary (indicator is within thresholds)
  OS/OB remain only in RSI/K oscillator context where they are technically correct.
"""

import asyncio
import itertools
import json
import math
import multiprocessing
import signal
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

import mysql.connector
import numpy as np
import pandas as pd
import requests
import websockets

from logger import get_logger


@dataclass
class WorkerSpec:
    """Describes one supervised worker."""
    name:               str
    target_fn:          Callable
    args:               tuple           = field(default_factory=tuple)
    restart_on_failure: bool            = True
    interval_s:         Optional[float] = None   # None=continuous, float=scheduled
    restart_delay_s:    float           = 5.0
    inline:             bool            = False  # True=run in main thread (console visible)
class ProcessManager:
    """
    Supervises WorkerSpecs as child processes or inline main-thread tasks.
    Continuous workers restart on exit. Scheduled workers re-run at interval.
    Inline workers run in the supervisor loop (guaranteed console visibility).
    """

    _POLL_S = 1.0

    def __init__(self) -> None:
        self._specs     = {}
        self._processes = {}
        self._last_run  = {}
        self._shutdown  = multiprocessing.Event()
        self._log       = get_logger(self.__class__.__name__)

    def register(self, spec: WorkerSpec) -> None:
        self._specs[spec.name] = spec
        mode = 'inline' if spec.inline else ('scheduled' if spec.interval_s else 'continuous')
        self._log.info(f'Registered: {spec.name}  [{mode}]'
                       + (f'  interval={spec.interval_s}s' if spec.interval_s else ''))

    def start(self) -> None:
        self._log.info(f'Starting ProcessManager — {len(self._specs)} workers')
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT,  self._handle_signal)
        for spec in self._specs.values():
            if not spec.inline:
                self._start_worker(spec)
        self._supervise()

    def _supervise(self) -> None:
        while not self._shutdown.is_set():
            for name, spec in self._specs.items():
                if spec.inline:
                    self._check_inline(name, spec)
                else:
                    self._check(name, spec)
            time.sleep(self._POLL_S)
        self._stop_all()

    def _check_inline(self, name: str, spec: WorkerSpec) -> None:
        elapsed = time.time() - self._last_run.get(name, 0)
        if elapsed >= (spec.interval_s or 0):
            try:
                spec.target_fn(*spec.args)
            except Exception as exc:
                self._log.error(f'Inline worker {name} error: {exc}')
            self._last_run[name] = time.time()

    def _check(self, name: str, spec: WorkerSpec) -> None:
        proc  = self._processes.get(name)
        alive = proc is not None and proc.is_alive()
        if spec.interval_s is not None:
            elapsed = time.time() - self._last_run.get(name, 0)
            if not alive and elapsed >= spec.interval_s:
                self._start_worker(spec)
                self._last_run[name] = time.time()
        else:
            if not alive and spec.restart_on_failure and not self._shutdown.is_set():
                self._log.warning(f'{name} died — restarting in {spec.restart_delay_s}s')
                time.sleep(spec.restart_delay_s)
                self._start_worker(spec)

    def _start_worker(self, spec: WorkerSpec) -> None:
        proc = multiprocessing.Process(
            target=spec.target_fn, args=spec.args, name=spec.name, daemon=True,
        )
        proc.start()
        self._processes[spec.name] = proc
        self._last_run[spec.name]  = time.time()
        self._log.info(f'Started {spec.name}  pid={proc.pid}')

    def _stop_all(self) -> None:
        for name, proc in self._processes.items():
            if proc.is_alive():
                proc.terminate()
                proc.join(timeout=10)
                self._log.info(f'Stopped {name}')

    def _handle_signal(self, signum: int, _frame) -> None:
        self._log.info(f'Signal {signum} — shutting down')
        self._shutdown.set()
