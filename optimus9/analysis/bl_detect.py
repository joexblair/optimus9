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

# gca5m raw 5s-PK config (Joe 2026-06-05): BB(hlcc4, len6, ×0.74) · pool 5/33/6/17 ·
# mult 1 (5s-native). The SnF source for the raw-pk overlay (and exit4/p-rev next).
GCA5M_RAW = dict(src='hlcc4', length=6, mult=0.74, dema_len=2, dema_src='close',
                 pool_c=5, pool_w=33, pool_range=6, pool_slope=17,
                 weight_close=5, weight_wide=2, pm_suppression=0.4, pm_additive=0.0,
                 threshold_long=7.5, threshold_short=7.5)


# hb9 family — the canonical values now live in the DB (indicator_configs +
# bl_lines, seeded Stage 1). Kept here only as a documentation reference / fallback:
#   hb9b K  5|74|29|hlc3 · hb9M BB 19|0.78|hl2 · hb9m BB 13|0.78|ohlc4 · TF9=540s
HB9 = {
    'name':       'hb9',
    'tf_seconds': 540,
    'k':  dict(kind='k',  rsi_len=74, stc_len=29, k_len=5,    src='hlc3'),   # hb9b
    'bM': dict(kind='bb', bb_len=19,  bb_mult=0.78,           src='hl2'),    # hb9M
    'bm': dict(kind='bb', bb_len=13,  bb_mult=0.78,           src='ohlc4'),  # hb9m
}


class BLDetect:
    _TABLE  = 'bl_states'
    _CONFIG = 'bl_config'

    def __init__(self, db, family=None, tp_pk=1, lookback_hours=12.0, warmup_hours=24.0):
        self._db       = db
        self._tp       = int(tp_pk)
        self._lookback = float(lookback_hours)
        self._warmup   = float(warmup_hours)
        self._log      = get_logger(self.__class__.__name__)
        # lines come from bl_lines + indicator_configs (de-hardcoded); tuning from the
        # active bl_config row. fence widened ±fence_pad (5 → 25:75).
        self._families = [family] if family is not None else self._load_families()
        self._fam = self._families[0]   # primary line — the shared TF basis (c9/e9, px, seams)
        self._cfg = self._load_config()
        c = self._cfg
        self._log.info(
            f"bl_config #{c['blc_pk']} '{c['blc_label']}' | curl_floor={c['blc_curl_floor']} "
            f"curl_lookback={c['blc_curl_lookback']} grace={c['blc_grace']} "
            f"pseudo_cross={c['blc_pseudo_cross']} fence_pad={c['blc_fence_pad']} "
            f"bb_pad={c['blc_bb_pad']} exit2_ref={c['blc_exit2_ref']} | "
            f"{len(self._families)} breach line(s): {', '.join(f['name'] for f in self._families)}")

    def _load_config(self) -> dict:
        """Ensure bl_config exists, seed a default active row if empty, return the
        active row. Knobs live here (not CLI args) so they're tweakable between runs
        with history (is_active flags the live one; old rows stay)."""
        self._db.execute(f'''CREATE TABLE IF NOT EXISTS {self._CONFIG} (
            blc_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
            blc_label VARCHAR(80) DEFAULT '',
            blc_is_active TINYINT DEFAULT 0,
            blc_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            blc_live_after_date DATETIME DEFAULT '2000-01-01',
            blc_curl_floor FLOAT DEFAULT 1.0,
            blc_curl_lookback INT DEFAULT 7,
            blc_grace INT DEFAULT 2,
            blc_pseudo_cross FLOAT DEFAULT 15.0,
            blc_fence_pad FLOAT DEFAULT 5.0,
            blc_bb_pad FLOAT DEFAULT 0.0,
            blc_exit2_ref VARCHAR(16) DEFAULT 'now')''')
        sel = (f'SELECT * FROM {self._CONFIG} WHERE blc_is_active=1 '
               'ORDER BY blc_pk DESC LIMIT 1')
        rows = self._db.execute(sel, fetch=True)
        if not rows:
            self._db.execute(
                f"INSERT INTO {self._CONFIG} (blc_label, blc_is_active) VALUES ('default', 1)")
            rows = self._db.execute(sel, fetch=True)
        return rows[0]

    def _load_families(self) -> list:
        """Build a family dict per ACTIVE breach line (name, tf_seconds, line_type, the
        breach-line cfg, support BBs M/m, exit_mask, pk_ic_pk) from bl_lines +
        indicator_configs. A K-breach family carries its M/m supports; a BB-breach family
        is standalone (run_bb). Replaces the single-family loader."""
        breaches = self._db.execute(
            '''SELECT bl.bl_ic_pk, bl.bl_pk_ic_pk, bl.bl_exit_mask, ic.ic_is_pk, ic.ic_line_type,
                      s.is_prefix, itf.itf_seconds, itf.itf_label, il.il_suffix
               FROM bl_lines bl
               JOIN indicator_configs ic   ON ic.ic_pk   = bl.bl_ic_pk
               JOIN indicator_series s     ON s.is_pk     = ic.ic_is_pk
               JOIN indicator_lines il     ON il.il_pk    = ic.ic_il_pk
               JOIN indicator_timeframes itf ON itf.itf_pk = ic.ic_itf_pk
               WHERE bl.bl_is_active = 1 AND bl.bl_role = 'breach'
               ORDER BY bl.bl_pk''', fetch=True)
        if not breaches:
            raise RuntimeError('bl_lines has no active breach line — seed it')
        fams = []
        for b in breaches:
            supports = self._db.execute(
                '''SELECT bl.bl_ic_pk, il.il_suffix FROM bl_lines bl
                   JOIN indicator_configs ic ON ic.ic_pk = bl.bl_ic_pk
                   JOIN indicator_lines il   ON il.il_pk = ic.ic_il_pk
                   WHERE bl.bl_is_active = 1 AND bl.bl_role = 'support' AND ic.ic_is_pk = %s''',
                (b['ic_is_pk'],), fetch=True)
            by_suf = {a['il_suffix']: self._cfg_dict(a['bl_ic_pk']) for a in supports}
            fams.append({'name':       f"{b['is_prefix']}{b['itf_label']}{b['il_suffix']}",
                         'tf_seconds': int(b['itf_seconds']), 'line_type': b['ic_line_type'],
                         'k':  self._cfg_dict(b['bl_ic_pk']),
                         'bM': by_suf.get('M'), 'bm': by_suf.get('m'),
                         'exit_mask': b['bl_exit_mask'], 'pk_ic_pk': b['bl_pk_ic_pk']})
            self._log.info(f"  breach {fams[-1]['name']} (TF{fams[-1]['tf_seconds']}s, "
                           f"{b['ic_line_type']}) mask={b['bl_exit_mask']}")
        return fams

    def _run_family(self, fam, base, ts):
        """Compute one family's breach line + run its machine (K via run, BB via run_bb).
        Returns (line, bM, bm, result_dict) — bM/bm are NaN for a BB-type family."""
        c, fp = self._cfg, float(self._cfg['blc_fence_pad'])
        bl = BreachingLine(mult=fam['tf_seconds'] // 5,
                           curl_floor=float(c['blc_curl_floor']),
                           curl_lookback=int(c['blc_curl_lookback']),
                           pseudo_cross=float(c['blc_pseudo_cross']),
                           grace=int(c['blc_grace']), exit2_ref=str(c['blc_exit2_ref']),
                           exit_mask=int(fam.get('exit_mask') or 7), bb_pad=float(c['blc_bb_pad']),
                           fence_hi=FENCE_HI + fp, fence_lo=FENCE_LO - fp)
        tf   = int(fam['tf_seconds'])
        line = self._line(base, fam['k'], tf)             # the breach line (K or BB), on its own TF
        cyc  = ts // (tf * 1000)
        seam = np.empty(len(ts), bool); seam[0] = True; seam[1:] = cyc[1:] != cyc[:-1]
        if fam['line_type'] == 'bb':
            r  = bl.run_bb(line, seam=seam)
            bM = bm = np.full(len(ts), np.nan)
        else:
            bM = self._line(base, fam['bM'], tf); bm = self._line(base, fam['bm'], tf)
            r  = bl.run(line, bm, bM, seam=seam)
        return line, bM, bm, r

    def _cfg_dict(self, ic_pk) -> dict:
        """One indicator_configs row → the kind/params dict _line() consumes."""
        r = self._db.execute('SELECT * FROM indicator_configs WHERE ic_pk = %s',
                             (ic_pk,), fetch=True)[0]
        if r['ic_line_type'] == 'k':
            return dict(kind='k', rsi_len=int(r['ic_rsi_len']), stc_len=int(r['ic_stc_len']),
                        k_len=int(r['ic_k_len']), src=r['ic_src'])
        return dict(kind='bb', bb_len=int(r['ic_bb_len']), bb_mult=float(r['ic_bb_mult']),
                    src=r['ic_src'])

    # ── public ───────────────────────────────────────────────────────────────
    def report(self, end_ms=None) -> list:
        end_ms     = int(end_ms or self._data_max())
        win_start  = int(end_ms - self._lookback * 3600_000)
        load_start = int(win_start - self._warmup * 3600_000)

        base  = KlineLoader(self._db).load_window(self._tp, load_start, end_ms)
        ts    = base['timestamp'].to_numpy()

        # raw 5s-PK = the Pine-aligned REALTIME signal (pk_raw → decision-delay(1) →
        # bny30 gate), so blr's "first SnF signal in the gate" is the real entry.
        from ..orchestration.gate_signal_sweep import pine_aligned_signals
        pk_idx, pk_dirs = pine_aligned_signals(base, self._db, GCA5M_RAW)
        raw_pk = np.zeros(len(ts), np.int8); raw_pk[pk_idx] = pk_dirs
        c9, e9 = self._htf_views(base, ts)                # c9/e9 + px on the primary line's TF
        tf    = IC.resample(base, self._fam['tf_seconds'])
        idx   = np.clip(np.searchsorted(tf['timestamp'].to_numpy(), ts, side='right') - 1, 0, None)
        px    = IC.dema(tf['close'].to_numpy(dtype=float), 2)[idx]

        # run EVERY active breach line (K via run, BB via run_bb), then fold the combined
        # state the gate reacts to = min(states) across lines, per bar.
        runs = [(fam, *self._run_family(fam, base, ts)) for fam in self._families]
        combined = np.vstack([r['state'] for *_, r in runs]).min(axis=0).astype(np.int8)

        rows = []
        for fam, line, bM, bm, r in runs:
            for i in range(len(ts)):
                if ts[i] < win_start:
                    continue
                rows.append({
                    'bar_ms':    int(ts[i]),
                    'line_name': fam['name'],
                    'px_smooth': _f(px[i]),
                    'c9_open':   _f(c9['o'][i]), 'c9_high': _f(c9['h'][i]),
                    'c9_low':    _f(c9['l'][i]), 'c9_close': _f(c9['c'][i]),
                    'e9_open':   _f(e9['o'][i]), 'e9_high': _f(e9['h'][i]),
                    'e9_low':    _f(e9['l'][i]), 'e9_close': _f(e9['c'][i]),
                    'hb9b':      _f(line[i]), 'hb9M': _f(bM[i]), 'hb9m': _f(bm[i]),
                    'k_gt_bb_main': int(bool(line[i] > bM[i])) if bM[i] == bM[i] else 0,
                    'slope_k':   _f(r['slope_k'][i]),
                    'exit2_ref':    _f(r['exit2_ref'][i]),
                    'exit2_ref_dt': (_dt(int(ts[r['exit2_ref_idx'][i]]))
                                     if r['exit2_ref_idx'][i] >= 0 else None),
                    'bl_ext':       _f(r['bl_ext'][i]),
                    'predicted': int(bool(r['predicted'][i])),
                    'exit1':     int(bool(r['exit1'][i])),
                    'exit2':     int(bool(r['exit2'][i])),
                    'exit3':     int(bool(r['exit3'][i])),
                    'breach_dir': int(r['breach_dir'][i]),
                    'state':     int(r['state'][i]),
                    'combined_state': int(combined[i]),    # min(states) — what the gate reads
                    'raw_pk':    int(raw_pk[i]),
                })
        self._persist(rows)
        nbars = len(set(row['bar_ms'] for row in rows))
        self._log.info(f"bl_states: {len(rows)} rows ({len(self._families)} lines × {nbars} bars, "
                       f"last {self._lookback}h) — lines {[f['name'] for f in self._families]}")
        return rows

    def emit_pine(self, rows: list, path: str = 'bl_hb9_states.pine') -> str:
        """Label each state TRANSITION with the new state, coloured by state —
        eyeball against the manual application on TV."""
        # rows are multi-line (N per bar) — collapse to the per-bar COMBINED state + raw pk
        per_bar = {}
        for r in rows:
            per_bar.setdefault(r['bar_ms'], (r['combined_state'], r['raw_pk']))
        bars  = sorted(per_bar)
        cs    = [per_bar[b][0] for b in bars]
        trans = [(bars[j], cs[j]) for j in range(len(bars)) if j == 0 or cs[j] != cs[j - 1]]
        t = ','.join(str(b)  for b, _ in trans) or '0'
        s = ','.join(str(st) for _, st in trans) or '0'
        fires = [(b, per_bar[b][1]) for b in bars if per_bar[b][1]]
        pt = ','.join(str(b) for b, _ in fires) or '0'
        pd = ','.join(str(d) for _, d in fires) or '0'
        nm = 'blc'   # the combined-state overlay (per-line detail lives in bl_review)
        c  = self._cfg
        built = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        cfg_line = (f"bl_config #{c['blc_pk']} '{c['blc_label']}': curl_floor={c['blc_curl_floor']} "
                    f"curl_lookback={c['blc_curl_lookback']} grace={c['blc_grace']} "
                    f"pseudo_cross={c['blc_pseudo_cross']} fence_pad={c['blc_fence_pad']} "
                    f"bb_pad={c['blc_bb_pad']} exit2_ref={c['blc_exit2_ref']}")
        pine = f'''//@version=6
indicator("BL combined: {','.join(f['name'] for f in self._families)}", overlay=true, max_labels_count=500)
// built {built} UTC  |  {len(bars)} bars, {len(self._families)} lines — {len(trans)} combined transitions
// {cfg_line}
// combined state = MIN(line states) · 0 idle · 1 breached · 2 curled · 3 complete
// window is timeframe-aware: a transition prints on whatever bar contains it (5s, TF9, …)
var int[] {nm}_tt = array.from({t})
var int[] {nm}_ss = array.from({s})
{nm}_bar_ms = timeframe.in_seconds() * 1000
{nm}_hit = -1
for {nm}_j = 0 to array.size({nm}_tt) - 1
    {nm}_pt = array.get({nm}_tt, {nm}_j)
    if {nm}_pt >= time and {nm}_pt < time + {nm}_bar_ms
        {nm}_hit := {nm}_j
        break
if {nm}_hit >= 0
    {nm}_st = array.get({nm}_ss, {nm}_hit)
    {nm}_col = {nm}_st == 1 ? color.yellow : {nm}_st == 2 ? color.orange : {nm}_st == 3 ? color.lime : color.gray
    label.new(bar_index, high, str.tostring({nm}_st), color={nm}_col,
              style=label.style_label_down, size=size.small)
// raw gca5m 5s-PK fires — up/green = long, down/red = short
var int[] {nm}_qt = array.from({pt})
var int[] {nm}_qd = array.from({pd})
{nm}_pk = 0
for {nm}_q = 0 to array.size({nm}_qt) - 1
    if array.get({nm}_qt, {nm}_q) >= time and array.get({nm}_qt, {nm}_q) < time + {nm}_bar_ms
        {nm}_pk := array.get({nm}_qd, {nm}_q)
        break
plotshape({nm}_pk ==  1, title="raw pk long",  style=shape.triangleup,   location=location.belowbar, color=color.new(color.green, 0), size=size.tiny)
plotshape({nm}_pk == -1, title="raw pk short", style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0),   size=size.tiny)
'''
        with open(path, 'w') as f:
            f.write(pine)
        self._log.info(f'wrote Pine overlay ({len(trans)} combined transitions, {len(fires)} raw pks) -> {path}')
        return path

    # ── internals ──────────────────────────────────────────────────────────
    def _line(self, base, cfg, tf_seconds):
        """Developing (lookahead) HTF line on the LINE'S OWN TF, 5s-aligned — matches
        TV lookahead_on. tf_seconds is per-family (mnm9=240, hb9=540): a multi-line
        engine must compute each line on its own timeframe, not the primary's."""
        if cfg['kind'] == 'bb':
            return IC.f_bb_lookahead(base, tf_seconds, cfg['bb_len'], cfg['bb_mult'], cfg['src'])
        return IC.f_k_lookahead(base, tf_seconds, cfg['k_len'], cfg['rsi_len'], cfg['stc_len'], cfg['src'])

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
            line_name VARCHAR(16), px_smooth FLOAT,
            c9_open FLOAT, c9_high FLOAT, c9_low FLOAT, c9_close FLOAT,
            e9_open FLOAT, e9_high FLOAT, e9_low FLOAT, e9_close FLOAT,
            k_line FLOAT, bb_main FLOAT, bb_mid FLOAT, k_gt_bb_main TINYINT,
            slope_k FLOAT, exit2_ref FLOAT, exit2_ref_dt DATETIME, bl_ext FLOAT,
            predicted TINYINT, exit1 TINYINT, exit2 TINYINT, exit3 TINYINT,
            breach_dir TINYINT, state TINYINT, combined_state TINYINT, raw_pk TINYINT)''')
        if not rows:
            return
        cols = ['bar_time', 'line_name', 'px_smooth',
                'c9_open', 'c9_high', 'c9_low', 'c9_close',
                'e9_open', 'e9_high', 'e9_low', 'e9_close',
                'k_line', 'bb_main', 'bb_mid', 'k_gt_bb_main', 'slope_k',
                'exit2_ref', 'exit2_ref_dt', 'bl_ext',
                'predicted', 'exit1', 'exit2', 'exit3', 'breach_dir', 'state',
                'combined_state', 'raw_pk']
        ph = ','.join(['%s'] * len(cols))
        data = [[_dt(r['bar_ms']), r['line_name'], r['px_smooth'],
                 r['c9_open'], r['c9_high'], r['c9_low'], r['c9_close'],
                 r['e9_open'], r['e9_high'], r['e9_low'], r['e9_close'],
                 r['hb9b'], r['hb9M'], r['hb9m'], r['k_gt_bb_main'], r['slope_k'],
                 r['exit2_ref'], r['exit2_ref_dt'], r['bl_ext'],
                 r['predicted'], r['exit1'], r['exit2'], r['exit3'],
                 r['breach_dir'], r['state'], r['combined_state'], r['raw_pk']] for r in rows]
        self._db.executemany(
            f'INSERT INTO {self._TABLE} ({",".join(cols)}) VALUES ({ph})', data)


def _f(x):
    # 6dp, not 4 — FARTCOIN prints at 0.14xxx (5 decimals); rounding to 4 lopped the
    # 5th digit and showed as a phantom ~3.5 bps "drift" vs TV. The tape is faithful.
    return round(float(x), 6) if x == x else None        # NaN → NULL


def _dt(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
