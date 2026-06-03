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
from ..constants import FENCE_HI, FENCE_LO


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
                 warmup_hours=24.0, curl_floor=1.0, curl_lookback=7, flatten=0.5,
                 pseudo_cross=15.0, grace=2, fence_pad=5.0):
        self._db       = db
        self._fam      = family
        self._tp       = int(tp_pk)
        self._lookback = float(lookback_hours)
        self._warmup   = float(warmup_hours)
        # fence widened symmetrically: upper += pad, lower -= pad (default 5 → 25:75)
        self._bl = BreachingLine(mult=family['tf_seconds'] // 5, curl_floor=curl_floor,
                                 curl_lookback=curl_lookback, flatten=flatten,
                                 pseudo_cross=pseudo_cross, grace=grace,
                                 fence_hi=FENCE_HI + float(fence_pad),
                                 fence_lo=FENCE_LO - float(fence_pad))
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
        # TF9 seams (cycle boundaries) — exit2's anchor is the K just before the seam
        # preceding max K, so the machine needs to know where the 9-min seams fall.
        cyc  = ts // (self._fam['tf_seconds'] * 1000)
        seam = np.empty(len(ts), bool); seam[0] = True; seam[1:] = cyc[1:] != cyc[:-1]
        r  = self._bl.run(k, bm, bM, seam=seam)   # run(k, bb_m, bb_M, seam)
        # ── two HTF (9-min) views per 5s bar, lookahead-free (see _htf_views) ──
        # c9 = last CLOSED 9-min bar (held across the cycle); e9 = the EMERGING bar
        # accumulated from cycle-open to THIS 5s bar (O anchored at the cycle's first
        # 5s open; H/L running extremes so far; C = this 5s close). Realtime reads e9;
        # c9 is the confirmed reference. Replaces the old forward-filled full-bar tf_*
        # which leaked the whole closed bar onto its first 5s row (the 21:45 mismatch).
        c9, e9 = self._htf_views(base, ts)

        # px_smooth = DEMA(9m close, 2) on the developing bin — display only.
        # REVIEW: still developing-bin/lookahead basis; candidate to ride e9['close'].
        tf    = IC.resample(base, self._fam['tf_seconds'])
        tf_ts = tf['timestamp'].to_numpy()
        idx   = np.clip(np.searchsorted(tf_ts, ts, side='right') - 1, 0, None)
        px  = IC.dema(tf['close'].to_numpy(dtype=float), 2)[idx]

        rows = []
        for i in range(len(ts)):
            if ts[i] < win_start:
                continue
            rows.append({
                'bar_ms':    int(ts[i]),
                'px_smooth': _f(px[i]),
                'c9_open':   _f(c9['o'][i]), 'c9_high': _f(c9['h'][i]),
                'c9_low':    _f(c9['l'][i]), 'c9_close': _f(c9['c'][i]),
                'e9_open':   _f(e9['o'][i]), 'e9_high': _f(e9['h'][i]),
                'e9_low':    _f(e9['l'][i]), 'e9_close': _f(e9['c'][i]),
                'hb9b':      _f(k[i]),  'hb9M': _f(bM[i]),  'hb9m': _f(bm[i]),
                'k_gt_bb_main': int(bool(k[i] > bM[i])),   # raw K>bb_main — the IB-cross marker
                'slope_k':   _f(r['slope_k'][i]),          # curl input: k[i]-k[i-curl_lookback]
                'k_anchor':  _f(r['k_anch'][i]),           # exit2 reversal anchor (K 1 bar pre-extreme)
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
        nm = self._fam['name']   # prefix every identifier so multiple BL overlays
                                 # (hb9, s18b, …) coexist on one chart without clashing
        pine = f'''//@version=6
indicator("BL states ({nm})", overlay=true)
// {len(rows)} bars, last {self._lookback}h — {len(trans)} transitions
// state 0 idle · 1 breached · 2 curled · 3 complete
var int[] {nm}_tt = array.from({t})
var int[] {nm}_ss = array.from({s})
{nm}_hit = -1
for {nm}_j = 0 to array.size({nm}_tt) - 1
    {nm}_pt = array.get({nm}_tt, {nm}_j)
    if {nm}_pt >= time and {nm}_pt < time + 5000
        {nm}_hit := {nm}_j
        break
if {nm}_hit >= 0
    {nm}_st = array.get({nm}_ss, {nm}_hit)
    {nm}_col = {nm}_st == 1 ? color.yellow : {nm}_st == 2 ? color.orange : {nm}_st == 3 ? color.lime : color.gray
    label.new(bar_index, high, str.tostring({nm}_st), color={nm}_col,
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

    def _htf_views(self, base, ts):
        """Per-5s, lookahead-free 9-min OHLC, two views:
          c9 = last CLOSED 9-min bar (prev cycle's full OHLC, held across this cycle).
          e9 = EMERGING 9-min bar — O anchored at the cycle's first 5s open; H/L the
               running extremes from cycle-open to THIS 5s bar; C = this 5s close.
        Cycles are epoch-anchored 540s bins (== midnight UTC grid == TV's), so e9 at a
        cycle's last 5s bar equals that cycle's true closed OHLC. Returns (c9, e9) dicts
        of float arrays keyed 'o'/'h'/'l'/'c'."""
        period = self._fam['tf_seconds'] * 1000
        o5 = base['open'].to_numpy(dtype=float); h5 = base['high'].to_numpy(dtype=float)
        l5 = base['low'].to_numpy(dtype=float);  c5 = base['close'].to_numpy(dtype=float)
        cyc = ts // period
        n   = len(ts)
        e_o = np.empty(n); e_h = np.empty(n); e_l = np.empty(n)
        c_o = np.full(n, np.nan); c_h = np.full(n, np.nan)
        c_l = np.full(n, np.nan); c_c = np.full(n, np.nan)
        prev = None; cur = None; r_o = r_h = r_l = 0.0
        for i in range(n):
            if cyc[i] != cur:
                if cur is not None:
                    prev = (r_o, r_h, r_l, c5[i - 1])    # closed bar: C = cycle's last 5s
                cur = cyc[i]; r_o = o5[i]; r_h = h5[i]; r_l = l5[i]
            else:
                if h5[i] > r_h: r_h = h5[i]
                if l5[i] < r_l: r_l = l5[i]
            e_o[i] = r_o; e_h[i] = r_h; e_l[i] = r_l
            if prev is not None:
                c_o[i], c_h[i], c_l[i], c_c[i] = prev
        return ({'o': c_o, 'h': c_h, 'l': c_l, 'c': c_c},
                {'o': e_o, 'h': e_h, 'l': e_l, 'c': c5})

    def _data_max(self):
        return int(self._db.execute(
            'SELECT MAX(kc_timestamp) AS m FROM kline_collection WHERE kc_tp_pk=%s',
            (self._tp,), fetch=True)[0]['m'])

    def _persist(self, rows):
        self._db.execute(f'DROP TABLE IF EXISTS {self._TABLE}')
        self._db.execute(f'''CREATE TABLE {self._TABLE} (
            bls_pk BIGINT AUTO_INCREMENT PRIMARY KEY, bar_time DATETIME,
            px_smooth FLOAT,
            c9_open FLOAT, c9_high FLOAT, c9_low FLOAT, c9_close FLOAT,
            e9_open FLOAT, e9_high FLOAT, e9_low FLOAT, e9_close FLOAT,
            k_line FLOAT, bb_main FLOAT, bb_mid FLOAT, k_gt_bb_main TINYINT,
            slope_k FLOAT, k_anchor FLOAT,
            predicted TINYINT, exit1 TINYINT, exit2 TINYINT, exit3 TINYINT,
            breach_dir TINYINT, state TINYINT)''')
        if not rows:
            return
        cols = ['bar_time', 'px_smooth',
                'c9_open', 'c9_high', 'c9_low', 'c9_close',
                'e9_open', 'e9_high', 'e9_low', 'e9_close',
                'k_line', 'bb_main', 'bb_mid', 'k_gt_bb_main', 'slope_k', 'k_anchor',
                'predicted', 'exit1', 'exit2', 'exit3', 'breach_dir', 'state']
        ph = ','.join(['%s'] * len(cols))
        data = [[_dt(r['bar_ms']), r['px_smooth'],
                 r['c9_open'], r['c9_high'], r['c9_low'], r['c9_close'],
                 r['e9_open'], r['e9_high'], r['e9_low'], r['e9_close'],
                 r['hb9b'], r['hb9M'], r['hb9m'], r['k_gt_bb_main'], r['slope_k'], r['k_anchor'],
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
