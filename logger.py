"""
logger.py

Singleton logger. Call get_logger(name) in every class.
Produces three log files (one per severity) plus a console handler for INFO+.

Log directory defaults to ./logs — override with PK_LOG_DIR env var.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR    = Path(os.environ.get('PK_LOG_DIR', 'logs'))
_initialised = False


class _LevelFilter(logging.Filter):
    """Passes only records at exactly one level."""

    def __init__(self, level: int) -> None:
        super().__init__()
        self._level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self._level


def _initialise(log_dir: Path) -> None:
    global _initialised
    if _initialised:
        return
    _initialised = True

    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt     = '%(asctime)s  %(name)-26s  %(levelname)-8s  %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )

    for level, filename in (
        (logging.DEBUG, 'debug.log'),
        (logging.INFO,  'info.log'),
        (logging.ERROR, 'error.log'),
    ):
        fh = RotatingFileHandler(
            log_dir / filename,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8',
        )
        fh.setLevel(level)
        fh.addFilter(_LevelFilter(level))
        fh.setFormatter(fmt)
        root.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)


def get_logger(name: str) -> logging.Logger:
    _initialise(_LOG_DIR)
    return logging.getLogger(name)
