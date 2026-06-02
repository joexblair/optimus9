"""
bl_detect — run the BL 4-state machine over a window for one line family and emit
a per-5s persistence table + a labelled Pine overlay. Spec: bl_machine_design.md.

First target (hb9, 12h): the Python states should match the manual application of
the states on the Pine chart (Joe's eye). Lines are computed on their HTF, then
forward-filled to the 5s base (mimics the TV lines); the machine ticks on 5s with
a slope/curl lookback of tf_seconds/5 bars (hb9 = 540/5 = 108).
"""
from datetime import datetime, timezone

import numpy as np

from logger import get_logger
from ..db.kline_loader import KlineLoader
from ..compute.indicator_computer import IndicatorComputer as IC
from ..compute.breaching_line import BreachingLine


# hb9 family — TF9 = 9 minutes (540s). BB lines hand-curated; not AM-swept.
HB9 = {
    'name':       'hb9',
    'tf_seconds': 540,
    'k':  dict(kind='k',  rsi_len=74, stc_len=29, k_len=5,    src='hlc3'),   # hb9b
    'bM': dict(kind='bb', bb_len=19,  bb_mult=0.78,           src='hl2'),    # hb9M
    'bm': dict(kind='bb', bb_len=13,  bb_mult=0.78,           src='ohlc4'),  # hb9m
}


class BLDetect:
    _TABLE = 'bl_states'

    def __init__(self, db, family=HB9, tp_pk=1, lookback_hours=12.0,
                 warmup_hours=24.0, curl_floor=1.0, flatten=0.5, pseudo_cross=15.0):
        self._db       = db
        self._fam      = family
        self._tp       = int(tp_pk)
        self._lookback = float(lookback_hours)
        self._warmup   = float(warmup_hours)
        self._bl = BreachingLine(mult=family['tf_seconds'] // 5, curl_floor=curl_floor,
                                 flatten=flatten, pseudo_cross=pseudo_cross)
        self._log = get_logger(self.__class__.__name__)

    # ── public ───────────────────────────────────────────────────────────────
    def report(self, end_ms=None) -> list:
        end_ms     = int(end_ms or self._data_max())
        win_start  = int(end_ms - self._lookback * 3600_000)
        load_start = int(win_start - self._warmup * 3600_000)

        base  = KlineLoader(self._db).load_window(self._tp, load_start, end_ms)
        ts    = base['timestamp'].to_numpy()
        close = base['close'].to_numpy(dtype=float)

        # Lines are the DEVELOPING (lookahead) HTF view, 5s-aligned — matches TV's
        # lookahead_on (last bar + ticks). The machine ticks per 5s with a curl/slope
        # lookback of tf_seconds/5 bars (hb9 = 108) to span one HTF period.
        k  = self._line(base, self._fam['k'])     # hb9b (breaching K)
        bM = self._line(base, self._fam['bM'])    # hb9M
        bm = self._line(base, self._fam['bm'])    # hb9m
        r  = self._bl.run(k, bm, bM)              # run(k, bb_m, bb_M)
        # display refs on the lines' TF (9-min) — px_smooth = DEMA(9m close,2) (matches
        # TV); + the closed TF9 OHLC, both forward-filled to the 5s rows.
        tf    = IC.resample(base, self._fam['tf_seconds'])
        tf_ts = tf['timestamp'].to_numpy()
        idx   = np.clip(np.searchsorted(tf_ts, ts, side='right') - 1, 0, None)
        px  = IC.dema(tf['close'].to_numpy(dtype=float), 2)[idx]
        d_o = tf['open'].to_numpy()[idx];  d_h = tf['high'].to_numpy()[idx]
        d_l = tf['low'].to_numpy()[idx];   d_c = tf['close'].to_numpy()[idx]

        rows = []
        for i in range(len(ts)):
            if ts[i] < win_start:
                continue
            rows.append({
                'bar_ms':    int(ts[i]),
                'px_smooth': _f(px[i]),
                'tf_open':   _f(d_o[i]), 'tf_high': _f(d_h[i]),
                'tf_low':    _f(d_l[i]), 'tf_close': _f(d_c[i]),
                'hb9b':      _f(k[i]),  'hb9M': _f(bM[i]),  'hb9m': _f(bm[i]),
                'predicted': int(bool(r['predicted'][i])),
                'exit1':     int(bool(r['exit1'][i])),
                'exit2':     int(bool(r['exit2'][i])),
                'exit3':     int(bool(r['exit3'][i])),
                'breach_dir': int(r['breach_dir'][i]),
                'state':     int(r['state'][i]),
            })
        self._persist(rows)
        states = [row['state'] for row in rows]
        trans  = sum(1 for j in range(1, len(states)) if states[j] != states[j - 1])
        self._log.info(f'bl_states: {len(rows)} bars ({self._fam["name"]}, last '
                       f'{self._lookback}h) — {trans} state transitions')
        return rows

    def emit_pine(self, rows: list, path: str = 'bl_hb9_states.pine') -> str:
        """Label each state TRANSITION with the new state, coloured by state —
        eyeball against the manual application on TV."""
        trans = [r for j, r in enumerate(rows)
                 if j == 0 or r['state'] != rows[j - 1]['state']]
        t = ','.join(str(r['bar_ms']) for r in trans) or '0'
        s = ','.join(str(r['state'])  for r in trans) or '0'
        pine = f'''//@version=6
indicator("BL states ({self._fam['name']})", overlay=true)
// {len(rows)} bars, last {self._lookback}h — {len(trans)} transitions
// state 0 idle · 1 breached · 2 curled · 3 complete
var int[] tt = array.from({t})
var int[] ss = array.from({s})
hit = -1
for j = 0 to array.size(tt) - 1
    pt = array.get(tt, j)
    if pt >= time and pt < time + 5000
        hit := j
        break
if hit >= 0
    st = array.get(ss, hit)
    col = st == 1 ? color.yellow : st == 2 ? color.orange : st == 3 ? color.lime : color.gray
    label.new(bar_index, high, str.tostring(st), color=col,
              style=label.style_label_down, size=size.small)
'''
        with open(path, 'w') as f:
            f.write(pine)
        self._log.info(f'wrote Pine overlay ({len(trans)} transitions) -> {path}')
        return path

    # ── internals ──────────────────────────────────────────────────────────
    def _line(self, base, cfg):
        """Developing (lookahead) HTF line, 5s-aligned — matches TV lookahead_on."""
        secs = self._fam['tf_seconds']
        if cfg['kind'] == 'bb':
            return IC.f_bb_lookahead(base, secs, cfg['bb_len'], cfg['bb_mult'], cfg['src'])
        return IC.f_k_lookahead(base, secs, cfg['k_len'], cfg['rsi_len'], cfg['stc_len'], cfg['src'])

    def _data_max(self):
        return int(self._db.execute(
            'SELECT MAX(kc_timestamp) AS m FROM kline_collection WHERE kc_tp_pk=%s',
            (self._tp,), fetch=True)[0]['m'])

    def _persist(self, rows):
        self._db.execute(f'DROP TABLE IF EXISTS {self._TABLE}')
        self._db.execute(f'''CREATE TABLE {self._TABLE} (
            bls_pk BIGINT AUTO_INCREMENT PRIMARY KEY, bar_time DATETIME,
            px_smooth FLOAT, tf_open FLOAT, tf_high FLOAT, tf_low FLOAT, tf_close FLOAT,
            k_line FLOAT, bb_main FLOAT, bb_mid FLOAT,
            predicted TINYINT, exit1 TINYINT, exit2 TINYINT, exit3 TINYINT,
            breach_dir TINYINT, state TINYINT)''')
        if not rows:
            return
        cols = ['bar_time', 'px_smooth', 'tf_open', 'tf_high', 'tf_low', 'tf_close',
                'k_line', 'bb_main', 'bb_mid', 'predicted',
                'exit1', 'exit2', 'exit3', 'breach_dir', 'state']
        ph = ','.join(['%s'] * len(cols))
        data = [[_dt(r['bar_ms']), r['px_smooth'], r['tf_open'], r['tf_high'],
                 r['tf_low'], r['tf_close'], r['hb9b'], r['hb9M'], r['hb9m'],
                 r['predicted'], r['exit1'], r['exit2'], r['exit3'],
                 r['breach_dir'], r['state']] for r in rows]
        self._db.executemany(
            f'INSERT INTO {self._TABLE} ({",".join(cols)}) VALUES ({ph})', data)


def _f(x):
    # 6dp, not 4 — FARTCOIN prints at 0.14xxx (5 decimals); rounding to 4 lopped the
    # 5th digit and showed as a phantom ~3.5 bps "drift" vs TV. The tape is faithful.
    return round(float(x), 6) if x == x else None        # NaN → NULL


def _dt(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
