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
import numpy as np
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

    def load_window(self, tp_pk: int, start_ms: int, end_ms: int, as_float: bool = False) -> pd.DataFrame:
        """Klines for tp_pk within [start_ms, end_ms).  Half-open interval.
        as_float=True returns timestamp int64 + OHLCV float64 (see _fetch_float); default unchanged."""
        where, params = 'kc_tp_pk = %s AND kc_timestamp >= %s AND kc_timestamp < %s', (tp_pk, start_ms, end_ms)
        if as_float:
            return self._fetch_float(where, params, tp_pk)
        return self._fetch(where, params, tp_pk)

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

    def _fetch_float(self, where: str, params: tuple, tp_pk: int) -> pd.DataFrame:
        """The same rows as _fetch, as int64 / float64 columns. Joe 1005 o9-live loop optimisation:
        _fetch builds one dict per row and leaves DECIMAL objects that every consumer re-converts -
        ~0.4 s of a 104 h window. Here the rows come back raw (bytes) and each value is converted
        ONCE with float()/int(), the same correctly-rounded parse float(Decimal) does, so the values
        are identical to _fetch's after .to_numpy(dtype=float)."""
        sql = f'{self._SELECT_BASE} WHERE {where} ORDER BY kc_timestamp ASC'

        def run():
            cur = self._db._conn.cursor(raw=True)
            try:
                cur.execute(sql, params)
                return cur.fetchall()
            finally:
                cur.close()
        rows = self._db._with_reconnect(run)
        if not rows:
            raise RuntimeError(f'No klines for tp_pk={tp_pk}')
        cols = list(zip(*rows))
        df = pd.DataFrame({'timestamp': np.array([int(x) for x in cols[0]], dtype=np.int64)})
        for j, c in enumerate(('open', 'high', 'low', 'close', 'volume'), 1):
            df[c] = np.array([float(x) for x in cols[j]], dtype=float)
        return df
