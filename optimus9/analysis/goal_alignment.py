"""
GoalAlignment — validates the end-goal "filter out all but the profitable 5s PKs".

For each gca5m PK in the last `lookback_hours` (as of `end_ms`), records its
win/stop outcome (first +profit_point% vs −stop_loss% cross, walked forward to
end_ms) and each gate filter's block decision, into the `gate_validation` table
for Excel. emit_pine() writes a chart overlay (green/red by direction, white
overlay on gated PKs). Adhoc, time-machineable via end_ms.

Columns grow with filters: each entry in `filters` adds a `g8_<name>` boolean.
`gated` is the OR of the per-filter g8 cells.
"""
from datetime import datetime, timezone

import numpy as np

from logger import get_logger
from ..db.kline_loader import KlineLoader
from ..compute.indicator_computer import IndicatorComputer as IC
from ..compute.outcome_walker import walk_to_first_cross
from ..orchestration.gate_signal_sweep import generate_gca5m_signals, GCA5M


def _bb(src, length, mult):
    return dict(ic_itf_seconds=30, ic_line_type='bb', ic_src=src,
                ic_high_boundary=85, ic_low_boundary=15, ic_bb_len=length, ic_bb_mult=mult)


def _k(src, k, rsi, stc):
    return dict(ic_itf_seconds=30, ic_line_type='k', ic_src=src,
                ic_high_boundary=85, ic_low_boundary=15, ic_k_len=k, ic_rsi_len=rsi, ic_stc_len=stc)


# The gate under test (current bny30 config). Pass a different list to validate
# another build; add an entry → its g8_<name> column appears automatically.
DEFAULT_FILTERS = [
    ('bny30M', _bb('hl2', 58, 1.24)),
    ('bny30p', _k('ohlc4', 21, 114, 105)),
]


class GoalAlignment:
    _TABLE = 'gate_validation'
    _WARMUP_HOURS = 6

    def __init__(self, db, lookback_hours=6.0, stop_loss=0.4, profit_point=0.9,
                 tp_pk=1, gca5m_cfg=None, filters=None):
        self._db      = db
        self._lookback = float(lookback_hours)
        self._stop    = float(stop_loss)
        self._profit  = float(profit_point)
        self._tp_pk   = int(tp_pk)
        self._gca     = gca5m_cfg or GCA5M
        self._filters = filters or DEFAULT_FILTERS
        self._log     = get_logger(self.__class__.__name__)

    # ── public ───────────────────────────────────────────────────────────────
    def report(self, end_ms=None) -> list:
        """Build the per-PK rows, persist to gate_validation, return them."""
        end_ms     = int(end_ms or self._data_max())
        win_start  = int(end_ms - self._lookback * 3600_000)
        load_start = int(win_start - self._WARMUP_HOURS * 3600_000)

        base  = KlineLoader(self._db).load_window(self._tp_pk, load_start, end_ms)
        close = base['close'].to_numpy(dtype=float)
        ts    = base['timestamp'].to_numpy()
        bars, dirs = generate_gca5m_signals(base, self._db, self._gca)

        cache = {}
        evals = {name: self._filter_eval(cfg, base, cache) for name, cfg in self._filters}

        rows = []
        for bar, d in zip(bars.tolist(), dirs.tolist()):
            if ts[bar] < win_start:               # only the lookback window
                continue
            wo, so = walk_to_first_cross(close, bar, d, self._profit, self._stop)
            g8  = {name: bool(evals[name][1][bar] != -d) for name, _ in self._filters}
            val = {name: float(evals[name][0][bar])      for name, _ in self._filters}
            rows.append({
                'run_ms':  end_ms,
                'pk_ms':   int(ts[bar]),
                'dir':     int(d),
                'win_ms':  int(ts[bar + wo]) if wo is not None else None,
                'stop_ms': int(ts[bar + so]) if so is not None else None,
                # OR-admit gate: blocked only when EVERY filter blocks (none admits)
                'gated':   all(g8.values()),
                'g8':      g8,
                'val':     val,
            })
        self._persist(rows)
        self._log.info(f'gate_validation: {len(rows)} PKs in last {self._lookback}h '
                       f'(gated {sum(r["gated"] for r in rows)}, '
                       f'won {sum(r["win_ms"] is not None for r in rows)})')
        return rows

    def emit_pine(self, rows: list, path: str = 'gca5m_gate_validation.pine') -> str:
        """Pine overlay: green=long / red=short bgcolor per PK bar; white bgcolor
        overlaid on gated PKs (two bgcolors on one bar)."""
        t = ','.join(str(r['pk_ms']) for r in rows) or '0'   # raw ms — matched by range
        d = ','.join(str(r['dir'])   for r in rows) or '0'
        g = ','.join('true' if r['gated'] else 'false' for r in rows) or 'false'
        names = ' + '.join(n for n, _ in self._filters)
        # Our tick-derived bar times don't sit cleanly on TV's 5s grid, so match a
        # PK to a bar by RANGE: pk_ms ∈ [bar_time, bar_time+5000). bgcolor must be
        # called in global scope, so compute the colours and call bgcolor at top level.
        pine = f'''//@version=6
indicator("gca5m gate validation ({names})", overlay=true)
// {len(rows)} PKs, last {self._lookback}h, stop {self._stop}% / profit {self._profit}%
var int[]  pk_t = array.from({t})
var int[]  pk_d = array.from({d})
var bool[] pk_g = array.from({g})
hit = -1
for j = 0 to array.size(pk_t) - 1
    pt = array.get(pk_t, j)
    if pt >= time and pt < time + 5000
        hit := j
        break
is_pk = hit >= 0
si = math.max(hit, 0)
base_col = is_pk ? (array.get(pk_d, si) > 0 ? color.new(color.green, 65) : color.new(color.red, 65)) : na
gate_col = (is_pk and array.get(pk_g, si)) ? color.new(color.white, 55) : na
bgcolor(base_col)         // direction: green=long / red=short
bgcolor(gate_col)         // overlay: white on gated PKs
'''
        with open(path, 'w') as f:
            f.write(pine)
        self._log.info(f'wrote Pine overlay ({len(rows)} PKs) -> {path}')
        return path

    # ── internals ──────────────────────────────────────────────────────────
    def _filter_eval(self, cfg, base, cache):
        """Return (value, side) for one filter, aligned to the 5s base.
        value = the f_bb/f_k indicator value (TV-comparable); side = its OOB
        classification vs the 15/85 boundaries (+1 HI, -1 LO, 0 IB)."""
        secs = int(cfg['ic_itf_seconds'])
        if secs not in cache:
            cache[secs] = IC.resample(base, secs)
        gate_df = cache[secs]
        src     = IC.build_source(gate_df, cfg['ic_src'])
        if cfg['ic_line_type'] == 'bb':
            vals = IC.f_bb(src, int(cfg['ic_bb_len']), float(cfg['ic_bb_mult']))
        else:
            vals = IC.f_k(src, int(cfg['ic_rsi_len']), int(cfg['ic_stc_len']), int(cfg['ic_k_len']))
        val = IC.align_to_base(vals, gate_df, base)
        hi, lo = float(cfg['ic_high_boundary']), float(cfg['ic_low_boundary'])
        side = np.zeros(len(base), dtype=np.int8)
        with np.errstate(invalid='ignore'):
            side[val >= hi] =  1
            side[val <= lo] = -1
        return val, side

    def _data_max(self):
        return int(self._db.execute(
            'SELECT MAX(kc_timestamp) AS m FROM kline_collection WHERE kc_tp_pk=%s',
            (self._tp_pk,), fetch=True)[0]['m'])

    def _persist(self, rows):
        names   = [n for n, _ in self._filters]
        g8_cols = [f'g8_{n}'  for n in names]
        val_cols = [f'val_{n}' for n in names]
        ddl = ',\n  '.join(
            ['gv_pk BIGINT AUTO_INCREMENT PRIMARY KEY', 'gv_run_utc DATETIME',
             'pk_time DATETIME', 'pk_dir TINYINT',
             'win_time DATETIME NULL', 'stop_time DATETIME NULL', 'gated TINYINT'] +
            [f'{c} TINYINT' for c in g8_cols] + [f'{c} FLOAT' for c in val_cols])
        self._db.execute(f'DROP TABLE IF EXISTS {self._TABLE}')
        self._db.execute(f'CREATE TABLE {self._TABLE} (\n  {ddl}\n)')
        if not rows:
            return
        cols = (['gv_run_utc', 'pk_time', 'pk_dir', 'win_time', 'stop_time', 'gated']
                + g8_cols + val_cols)
        ph   = ','.join(['%s'] * len(cols))

        def dt(ms):
            return (datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
                    .strftime('%Y-%m-%d %H:%M:%S')) if ms is not None else None

        def vv(x):
            return round(float(x), 2) if x == x else None     # NaN → NULL

        data = [[dt(r['run_ms']), dt(r['pk_ms']), r['dir'], dt(r['win_ms']), dt(r['stop_ms']),
                 1 if r['gated'] else 0]
                + [1 if r['g8'][n] else 0 for n in names]
                + [vv(r['val'][n]) for n in names]
                for r in rows]
        self._db.executemany(
            f'INSERT INTO {self._TABLE} ({",".join(cols)}) VALUES ({ph})', data)
