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
from ..compute.outcome_walker import walk_to_first_cross, winner_mae
from ..orchestration.gate_signal_sweep import generate_gca5m_signals, GCA5M


# The bny30 gate filters: (report column name, DB ind_name). Configs are loaded
# LIVE from the indicator_configs_live view (no hardcoding — can't drift off TV).
# Add a pair → its g8_<name>/val_<name> columns appear automatically.
DEFAULT_GATE = [('bny30M', 'bnyM'), ('bny30p', 'bnyp')]


class GoalAlignment:
    _TABLE = 'gate_validation'
    _WARMUP_HOURS = 6

    def __init__(self, db, lookback_hours=6.0, stop_loss=0.4, profit_point=0.9,
                 tp_pk=1, gca5m_cfg=None, gate=None, boundary_slip=3.0):
        self._db      = db
        self._lookback = float(lookback_hours)
        self._stop    = float(stop_loss)
        self._profit  = float(profit_point)
        self._tp_pk   = int(tp_pk)
        self._gca     = gca5m_cfg or GCA5M
        self._gate    = gate or DEFAULT_GATE
        self._slip    = float(boundary_slip)
        self._filters = []          # resolved from the live view at report() time
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

        # resolve gate filter configs LIVE from the DB view (no hardcoding)
        self._filters = [(disp, self._load_gate_config(name)) for disp, name in self._gate]
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

    def winner_mae_stop(self, end_ms=None, profit=None, k=1.0, trim=0.05,
                        horizon=None) -> dict:
        """Data-derived stop centre for downstream SL/TP sweeps (e.g.
        cluster_scoring). Over the lookback window, collects the MAE of every
        gca5m PK that eventually wins (+profit%, stop ignored) and returns a
        robust centre = trimmed mean + k·σ — the stop just wide enough to keep
        most eventual winners, with outliers trimmed so one freak dip can't blow
        it out. Returns {stop_centre, n_winners, mean, std, p50, p90}.
        """
        profit     = float(profit if profit is not None else self._profit)
        end_ms     = int(end_ms or self._data_max())
        win_start  = int(end_ms - self._lookback * 3600_000)
        load_start = int(win_start - self._WARMUP_HOURS * 3600_000)

        base  = KlineLoader(self._db).load_window(self._tp_pk, load_start, end_ms)
        close = base['close'].to_numpy(dtype=float)
        ts    = base['timestamp'].to_numpy()
        bars, dirs = generate_gca5m_signals(base, self._db, self._gca)

        maes = [m for bar, d in zip(bars.tolist(), dirs.tolist())
                if ts[bar] >= win_start
                and (m := winner_mae(close, bar, d, profit, horizon)) is not None]
        if not maes:
            self._log.warning('winner_mae_stop: no winners in window')
            return {'stop_centre': None, 'n_winners': 0}

        arr = np.asarray(maes, dtype=float)
        if trim and len(arr) >= 20:                          # drop tails, robust
            lo, hi = np.quantile(arr, [trim, 1.0 - trim])
            arr = arr[(arr >= lo) & (arr <= hi)]
        out = {'stop_centre': round(float(arr.mean() + k * arr.std()), 4),
               'n_winners':   len(maes),
               'mean':        round(float(arr.mean()), 4),
               'std':         round(float(arr.std()), 4),
               'p50':         round(float(np.median(maes)), 4),
               'p90':         round(float(np.quantile(maes, 0.9)), 4)}
        self._log.info(f'winner_mae_stop: n={out["n_winners"]} mean={out["mean"]} '
                       f'std={out["std"]} p90={out["p90"]} → '
                       f'centre(mean+{k}σ)={out["stop_centre"]}')
        return out

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
        # boundary_slip loosens the OOB zone inward: 15+slip / 85-slip (slip=3 → 18/82)
        hi = float(cfg['ic_high_boundary']) - self._slip
        lo = float(cfg['ic_low_boundary'])  + self._slip
        side = np.zeros(len(base), dtype=np.int8)
        with np.errstate(invalid='ignore'):
            side[val >= hi] =  1
            side[val <= lo] = -1
        return val, side

    def _load_gate_config(self, ind_name):
        """Resolve a gate line's LIVE config from indicator_configs_live (the
        ic_live_after_dt view) — no hardcoding, always matches production/TV."""
        r = self._db.execute(
            '''SELECT ic_line_type, ic_src, ic_bb_len, ic_bb_mult, ic_k_len, ic_rsi_len,
                      ic_stc_len, ic_low_boundary, ic_high_boundary, itf_seconds
               FROM indicator_configs_live WHERE ind_name = %s''', (ind_name,), fetch=True)
        if not r:
            raise ValueError(f'no live indicator_configs for {ind_name!r}')
        c = r[0]
        return {'ic_itf_seconds':   int(c['itf_seconds']),
                'ic_line_type':     c['ic_line_type'],
                'ic_src':           c['ic_src'],
                'ic_high_boundary': float(c['ic_high_boundary']),
                'ic_low_boundary':  float(c['ic_low_boundary']),
                'ic_bb_len':        c['ic_bb_len'],  'ic_bb_mult': c['ic_bb_mult'],
                'ic_k_len':         c['ic_k_len'],   'ic_rsi_len': c['ic_rsi_len'],
                'ic_stc_len':       c['ic_stc_len']}

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
