"""
KlineLoader — shared loader for kline_collection queries.
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

from datetime import datetime, timedelta, timezone
import pandas as pd

from logger import get_logger

# ── cross-package imports ─────────────────────────────────────────────────
from .database_manager import DatabaseManager


class KlineLoader:
    """
    Single source of truth for pulling klines from `kline_collection`.

    Consolidates the two previous patterns:
      load_recent(tp_pk, lookback_days)       — used by report_manager
      load_window(tp_pk, start_ms, end_ms)    — used by fold_manager
      load_all(tp_pk)                         — convenience: every kline for the pair

    Returns DataFrames with columns: timestamp, open, high, low, close, volume.
    Ordered ascending by timestamp. Raises RuntimeError if no rows match.
    """

    _SELECT_BASE = '''
        SELECT kc_timestamp AS timestamp, kc_open  AS open,
               kc_high      AS high,      kc_low   AS low,
               kc_close     AS close,     kc_volume AS volume
        FROM kline_collection
    '''

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def load_recent(self, tp_pk: int, lookback_days: int = None) -> pd.DataFrame:
        """Klines for tp_pk going back `lookback_days` from now (UTC).
        When `lookback_days` is None, returns the full pair history."""
        if lookback_days:
            cutoff = int((datetime.now(timezone.utc)
                          - timedelta(days=lookback_days)).timestamp() * 1000)
            where, params = 'kc_tp_pk = %s AND kc_timestamp >= %s', (tp_pk, cutoff)
        else:
            where, params = 'kc_tp_pk = %s', (tp_pk,)
        return self._fetch(where, params, tp_pk)

    def load_window(self, tp_pk: int, start_ms: int, end_ms: int) -> pd.DataFrame:
        """Klines for tp_pk within [start_ms, end_ms).  Half-open interval."""
        return self._fetch(
            'kc_tp_pk = %s AND kc_timestamp >= %s AND kc_timestamp < %s',
            (tp_pk, start_ms, end_ms),
            tp_pk,
        )

    def load_all(self, tp_pk: int) -> pd.DataFrame:
        """Every kline for tp_pk."""
        return self._fetch('kc_tp_pk = %s', (tp_pk,), tp_pk)

    def _fetch(self, where: str, params: tuple, tp_pk: int) -> pd.DataFrame:
        rows = self._db.execute(
            f'{self._SELECT_BASE} WHERE {where} ORDER BY kc_timestamp ASC',
            params, fetch=True,
        )
        if not rows:
            raise RuntimeError(f'No klines for tp_pk={tp_pk}')
        return pd.DataFrame(rows)
