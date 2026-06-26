"""
bl_detect — run the BL 4-state machine over a window for one line family and emit
a per-5s persistence table + a labelled Pine overlay. Spec: bl_machine_design.md.

First target (hb9, 12h): the Python states should match the manual application of
the states on the Pine chart (Joe's eye). Lines are computed on their HTF, then
forward-filled to the 5s base (mimics the TV lines); the machine ticks on 5s with
a slope/curl lookback of tf_seconds/5 bars (hb9 = 540/5 = 108).
"""
from collections import namedtuple
from datetime import datetime, timezone

import numpy as np

from logger import get_logger
from ..db.kline_loader import KlineLoader
from ..compute.indicator_computer import IndicatorComputer as IC
from ..compute.breaching_line import BreachingLine
from ..compute.swing_detect import find_pivots, nearest
from ..constants import FENCE_HI, FENCE_LO

# _run_family's return. result stays at INDEX 3 so positional callers (grinds, sweep,
# viz: ._run_family(...)[3]['state']) keep working; report() reads the support lines by
# NAME → honest bl_states columns (predictor_min/maj, exit_support, exit3_support).
FamilyRun = namedtuple('FamilyRun',
                       'line predictor_min predictor_maj result exit_support exit3_support')

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
        # primary line = the HIGHEST-TF active breach (tie → lowest bl_pk; families are bl_pk-ordered,
        # so max() keeps the first). Used only for the c9/e9 HTF views now — px_smooth is global 5s.
        self._fam = max(self._families, key=lambda f: f['tf_seconds'])
        self._cfg = self._load_config()
        self._sys = self._load_system()
        c = self._cfg
        self._log.info(
            f"bl_config #{c['blc_pk']} '{c['blc_label']}' | curl_floor={c['blc_curl_floor']} "
            f"curl_lookback={c['blc_curl_lookback']} grace={c['blc_grace']} "
            f"pseudo_cross={c['blc_pseudo_cross']} fence_pad={c['blc_fence_pad']} "
            f"bb_pad={c['blc_bb_pad']} exit2_ref={c['blc_exit2_ref']} "
            f"bny30_reset={c['blc_bny30_bias_reset_threshold']} | "
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
            blc_exit2_ref VARCHAR(16) DEFAULT 'now',
            blc_bny30_bias_reset_threshold INT DEFAULT 2,
            blc_wob_tf_seconds INT DEFAULT 5,
            blc_wob_bars INT DEFAULT 2,
            blc_wob_strict TINYINT DEFAULT 0)''')
        have = {r['Field'] for r in self._db.execute(f'SHOW COLUMNS FROM {self._CONFIG}', fetch=True)}
        for col, ddl in (('blc_bny30_bias_reset_threshold', 'INT DEFAULT 2'),   # migrate pre-existing tables
                         ('blc_wob_tf_seconds', 'INT DEFAULT 5'),
                         ('blc_wob_bars', 'INT DEFAULT 2'),
                         ('blc_wob_strict', 'TINYINT DEFAULT 0')):
            if col not in have:
                self._db.execute(f'ALTER TABLE {self._CONFIG} ADD COLUMN {col} {ddl}')
        sel = (f'SELECT * FROM {self._CONFIG} WHERE blc_is_active=1 '
               'ORDER BY blc_pk DESC LIMIT 1')
        rows = self._db.execute(sel, fetch=True)
        if not rows:
            self._db.execute(
                f"INSERT INTO {self._CONFIG} (blc_label, blc_is_active) VALUES ('default', 1)")
            rows = self._db.execute(sel, fetch=True)
        return rows[0]

    def _load_system(self) -> dict:
        """Global system config (px_smooth DEMA params). CREATE + seed-if-empty, return the row.
        ONE global row — the px_smooth SERIES is per-coin by virtue of each coin's own base tape."""
        self._db.execute('''CREATE TABLE IF NOT EXISTS optimus9_system (
            sys_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
            pxsmooth_dema_src VARCHAR(10) DEFAULT 'close',
            pxsmooth_dema_len INT DEFAULT 2,
            pxsmooth_dema_tf  INT DEFAULT 5,
            hi_boundary FLOAT DEFAULT 85,
            lo_boundary FLOAT DEFAULT 15)''')
        have = {r['Field'] for r in self._db.execute('SHOW COLUMNS FROM optimus9_system', fetch=True)}
        for col, ddl in (('hi_boundary', 'FLOAT DEFAULT 85'), ('lo_boundary', 'FLOAT DEFAULT 15')):
            if col not in have:                                # slow-burn: global OOB out of constants.py → here
                self._db.execute(f'ALTER TABLE optimus9_system ADD COLUMN {col} {ddl}')
        sel = 'SELECT * FROM optimus9_system ORDER BY sys_pk DESC LIMIT 1'
        rows = self._db.execute(sel, fetch=True)
        if not rows:
            self._db.execute("INSERT INTO optimus9_system "
                             "(pxsmooth_dema_src, pxsmooth_dema_len, pxsmooth_dema_tf) VALUES ('close', 2, 5)")
            rows = self._db.execute(sel, fetch=True)
        return rows[0]

    def _load_families(self) -> list:
        """Build a family dict per ACTIVE breach line from bl_lines + indicator_configs.

        Two distinct support concerns, sourced separately (BRD bl_line_brd.md):
          • PREDICTION — the breach's own set mini+Major BB (same series + label,
            suffix m/M). Resolved from the SET, NOT bl_lines: every set has both, and
            sourcing here avoids the old series-only collision when >1 breach shares a
            series. → predictor_min / predictor_maj.
          • EXITS — the hand-picked support bound to THIS breach via the breach row's
            bl_support_ic_pk (and bl_exit3_support_ic_pk, the optional cross-family
            exit3 override, e.g. hb15b's hb9M). → exit_support / exit3_support.
        A BB-breach family is standalone (run_bb); its support fields stay None."""
        breaches = self._db.execute(
            '''SELECT bl.bl_ic_pk, bl.bl_pk_ic_pk, bl.bl_exit_mask,
                      bl.bl_support_ic_pk, bl.bl_exit3_support_ic_pk,
                      ic.ic_is_pk, ic.ic_line_type,
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
            # predictor BBs from the SET: same series + label, the two BB suffixes m/M
            preds = self._db.execute(
                '''SELECT il.il_suffix, ic.ic_pk FROM vw_indicator_configs_live ic
                   JOIN indicator_lines il      ON il.il_pk  = ic.ic_il_pk
                   JOIN indicator_timeframes itf ON itf.itf_pk = ic.ic_itf_pk
                   WHERE ic.ic_is_pk = %s AND itf.itf_label = %s
                     AND ic.ic_line_type = 'bb' AND il.il_suffix IN ('m', 'M')''',
                (b['ic_is_pk'], b['itf_label']), fetch=True)
            by_suf = {p['il_suffix']: self._cfg_dict(p['ic_pk']) for p in preds}
            cfg = lambda pk: self._cfg_dict(pk) if pk else None
            fams.append({'name':          f"{b['is_prefix']}{b['itf_label']}{b['il_suffix']}",
                         'tf_seconds':    int(b['itf_seconds']), 'line_type': b['ic_line_type'],
                         'k':             self._cfg_dict(b['bl_ic_pk']),
                         'predictor_min': by_suf.get('m'), 'predictor_maj': by_suf.get('M'),
                         'exit_support':  cfg(b['bl_support_ic_pk']),
                         'exit3_support': cfg(b['bl_exit3_support_ic_pk']),
                         'exit_mask': b['bl_exit_mask'], 'pk_ic_pk': b['bl_pk_ic_pk']})
            self._log.info(f"  breach {fams[-1]['name']} (TF{fams[-1]['tf_seconds']}s, "
                           f"{b['ic_line_type']}) mask={b['bl_exit_mask']} "
                           f"exit_sup={'y' if b['bl_support_ic_pk'] else '-'} "
                           f"exit3={'y' if b['bl_exit3_support_ic_pk'] else '-'}")
        return fams

    def _run_family(self, fam, base, ts):
        """Compute one family's breach line + run its machine (K via run, BB via run_bb).
        Returns a FamilyRun(line, predictor_min, predictor_maj, result, exit_support,
        exit3_support). The four support arrays are NaN/None for a BB-type family; each
        persists to bl_states under its own honest column name."""
        c, fp = self._cfg, float(self._cfg['blc_fence_pad'])
        bl = BreachingLine(mult=fam['tf_seconds'] // 5,
                           curl_floor=float(c['blc_curl_floor']),
                           curl_lookback=int(c['blc_curl_lookback']),
                           pseudo_cross=float(c['blc_pseudo_cross']),
                           grace=int(c['blc_grace']), exit2_ref=str(c['blc_exit2_ref']),
                           exit_mask=int(fam.get('exit_mask') or 7), bb_pad=float(c['blc_bb_pad']),
                           fence_hi=FENCE_HI + fp, fence_lo=FENCE_LO - fp)
        tf   = int(fam['tf_seconds'])                     # breach line's TF = the machine's cadence
        line = self._line(base, fam['k'])                 # each line computes on its own config TF
        cyc  = ts // (tf * 1000)
        seam = np.empty(len(ts), bool); seam[0] = True; seam[1:] = cyc[1:] != cyc[:-1]
        nan  = lambda: np.full(len(ts), np.nan)
        if fam['line_type'] == 'bb':
            r = bl.run_bb(line, seam=seam)
            pmin = pmaj = esup = nan(); e3s = None
        else:
            pmin = self._line(base, fam['predictor_min']) if fam['predictor_min'] else nan()
            pmaj = self._line(base, fam['predictor_maj']) if fam['predictor_maj'] else nan()
            esup = self._line(base, fam['exit_support'])  if fam['exit_support']  else pmaj
            e3s  = self._line(base, fam['exit3_support']) if fam['exit3_support'] else None
            # wobble_slayer signals (Joe 0622) — n + strict from bl_config, OOB from optimus9_system.
            # On 5s emerging lines (wob_tf_seconds=5 → no subsample). run() consumes; doesn't recompute.
            wn  = int(self._cfg['blc_wob_bars']); ws = bool(int(self._cfg['blc_wob_strict']))
            whi = float(self._sys['hi_boundary']); wlo = float(self._sys['lo_boundary'])
            e3l = e3s if e3s is not None else esup
            wob = {'xs': IC.wobble_slayer(e3l,  wn, whi, wlo, anchored=True,  strict=ws),   # exit3 reversal
                   'rs': IC.wobble_slayer(esup, wn, whi, wlo, anchored=False, strict=ws),   # re-engage (support back)
                   'kk': IC.wobble_slayer(line, wn, whi, wlo, anchored=True,  strict=ws)}   # bobble debounce (K peel-off)
            r = bl.run(line, pmin, pmaj, esup, e3s, seam=seam, wob=wob)
        return FamilyRun(line, pmin, pmaj, r, esup, e3s)

    def _cfg_dict(self, ic_pk) -> dict:
        """One indicator_configs row → the kind/params dict _line() consumes, INCLUDING
        the line's own tf_seconds. The TF is a property of the config (ic_itf_pk), so the
        calculator computes from a complete config — no caller re-sources the timeframe."""
        r = self._db.execute(
            '''SELECT ic.*, itf.itf_seconds, vm.ivm_label AS value_mode FROM indicator_configs ic
               JOIN indicator_timeframes itf ON itf.itf_pk = ic.ic_itf_pk
               LEFT JOIN indicator_value_modes vm ON vm.ivm_pk = ic.ic_ivm_pk
               WHERE ic.ic_pk = %s''', (ic_pk,), fetch=True)[0]
        tf = int(r['itf_seconds']); vmode = r['value_mode'] or 'emerging'
        if r['ic_line_type'] == 'k':
            return dict(kind='k', tf_seconds=tf, rsi_len=int(r['ic_rsi_len']), value_mode=vmode,
                        stc_len=int(r['ic_stc_len']), k_len=int(r['ic_k_len']), src=r['ic_src'])
        return dict(kind='bb', tf_seconds=tf, bb_len=int(r['ic_bb_len']), value_mode=vmode,
                    bb_mult=float(r['ic_bb_mult']), src=r['ic_src'])

    # ── public ───────────────────────────────────────────────────────────────
    def _setup(self, end_ms=None):
        """Shared compute for report() AND the grind sweep — the tape, the raw 5s-pk
        (Pine-aligned → decision-delay → bny30 gate, so it's the gated entry signal), and
        px_smooth. Returns (base, ts, win_start, raw_pk, px)."""
        end_ms     = int(end_ms or self._data_max())
        win_start  = int(end_ms - self._lookback * 3600_000)
        load_start = int(win_start - self._warmup * 3600_000)
        base  = KlineLoader(self._db).load_window(self._tp, load_start, end_ms)
        ts    = base['timestamp'].to_numpy()
        from ..orchestration.gate_signal_sweep import pine_aligned_signals
        pk_idx, pk_dirs = pine_aligned_signals(base, self._db, GCA5M_RAW, gate=False)   # RAW pk = ungated (match grind/pine)
        raw_pk = np.zeros(len(ts), np.int8); raw_pk[pk_idx] = pk_dirs
        # px_smooth: global 5s DEMA, params from optimus9_system (close/2/5) — same manner as the
        # PK machine's dema (5s base, config-driven), NOT the old primary-TF resample.
        s = self._sys
        if int(s['pxsmooth_dema_tf']) <= 5:
            px = IC.dema(IC.build_source(base, s['pxsmooth_dema_src']), int(s['pxsmooth_dema_len']))
        else:
            sdf = IC.resample(base, int(s['pxsmooth_dema_tf']))
            idx = np.clip(np.searchsorted(sdf['timestamp'].to_numpy(), ts, side='right') - 1, 0, None)
            px  = IC.dema(IC.build_source(sdf, s['pxsmooth_dema_src']), int(s['pxsmooth_dema_len']))[idx]
        return base, ts, win_start, raw_pk, px

    def report(self, end_ms=None) -> list:
        base, ts, win_start, raw_pk, px = self._setup(end_ms)
        c9, e9 = self._htf_views(base, ts)                # c9/e9 + px on the primary line's TF
        from ..orchestration.gate_signal_sweep import bny30_latched_bias
        bny30_bias = bny30_latched_bias(base, int(self._cfg['blc_bny30_bias_reset_threshold']), use_k=False)  # M-only

        # run EVERY active breach line (K via run, BB via run_bb), then fold the combined
        # state the gate reacts to. combined = the LEAST-progressed ACTIVE breach: min over
        # the NON-ZERO states, and 0 ONLY when every line is idle. Plain min(states) is wrong
        # (Joe 2026-06-06): it lets a {0,1} pair read 0/idle while a line is still breaching —
        # counterproductive. This fold makes the gate test exactly combined∈{0,3}
        # (0 = all idle, 3 = all done, 1/2 = a breach in flight on some line).
        runs     = [(fam, self._run_family(fam, base, ts)) for fam in self._families]
        st_mat   = np.vstack([fr.result['state'] for _, fr in runs])
        nz       = np.where(st_mat == 0, 99, st_mat)          # mask idle so min ignores it
        combined = np.where((st_mat == 0).all(axis=0), 0, nz.min(axis=0)).astype(np.int8)

        # swing context: nearest pivot back/forth + adverse-side pivot, from the 0.9% ZigZag on
        # px_smooth (the canonical basis — 5s DEMA agrees with raw close to ~0.005%). ffill the
        # DEMA warmup NaN so find_pivots' running extreme doesn't stall.
        pxf = np.asarray(px, float).copy(); m = np.isfinite(pxf)
        if m.any() and not m.all():
            ix = np.where(m, np.arange(len(pxf)), 0); np.maximum.accumulate(ix, out=ix)
            pxf = pxf[ix]; pxf[:int(np.argmax(m))] = pxf[int(np.argmax(m))]
        piv   = find_pivots(pxf, 0.9)
        pv_all = np.array(sorted(x for x, _ in piv))
        pv_hi  = np.array(sorted(x for x, k in piv if k == 'H'))
        pv_lo  = np.array(sorted(x for x, k in piv if k == 'L'))

        rows = []
        for fam, fr in runs:
            line, r = fr.line, fr.result
            for i in range(len(ts)):
                if ts[i] < win_start:
                    continue
                bd = int(r['breach_dir'][i])
                cl = nearest(pv_all, i)
                ad = nearest(pv_hi if bd == 1 else pv_lo, i) if bd in (1, -1) else None
                rows.append({
                    'bar_ms':    int(ts[i]),
                    'line_name': fam['name'],
                    'px_smooth': _f(px[i]),
                    'c9_open':   _f(c9['o'][i]), 'c9_high': _f(c9['h'][i]),
                    'c9_low':    _f(c9['l'][i]), 'c9_close': _f(c9['c'][i]),
                    'e9_open':   _f(e9['o'][i]), 'e9_high': _f(e9['h'][i]),
                    'e9_low':    _f(e9['l'][i]), 'e9_close': _f(e9['c'][i]),
                    'breach_line':   _f(line[i]),
                    'predictor_min': _f(fr.predictor_min[i]),
                    'predictor_maj': _f(fr.predictor_maj[i]),
                    'exit_support':  _f(fr.exit_support[i]),
                    'exit3_support': (_f(fr.exit3_support[i]) if fr.exit3_support is not None else None),
                    'breach_slope': _f(r['slope_k'][i]),    # r['slope_k'] = machine-internal key
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
                    'bny30_bias': int(bny30_bias[i]),      # M-only inverted bny30 direction bias
                    'swing_closest_ms': (int(ts[cl]) if cl is not None else None),
                    'swing_adverse_ms': (int(ts[ad]) if ad is not None else None),
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
    def _line(self, base, cfg):
        """HTF line on the line's OWN TF (cfg['tf_seconds']), 5s-aligned. Routes by the line's
        `value_mode` (#33): 'emerging' (default) = lookahead developing line (TV lookahead_on);
        'closed' = the line of the last CLOSED TF bar (resampled f_bb/f_k + align) — stabler, fewer
        intra-bar crosses → fewer churny bls flips. The TF rides in the config (no primary leakage)."""
        secs = cfg['tf_seconds']
        if cfg.get('value_mode') == 'closed':
            fr = IC.resample(base, secs, 'midnight')          # midnight-anchored bars (TV grid) — non-day-
            if cfg['kind'] == 'bb':                           # divisor TFs (7/22min) drift on the epoch grid
                v = IC.f_bb(IC.build_source(fr, cfg['src']), cfg['bb_len'], cfg['bb_mult'])
            else:
                v = IC.f_k(IC.build_source(fr, cfg['src']), cfg['rsi_len'], cfg['stc_len'], cfg['k_len'])
            return IC.align_to_base(v, fr, base)
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
            line_name VARCHAR(16), px_smooth FLOAT,
            c9_open FLOAT, c9_high FLOAT, c9_low FLOAT, c9_close FLOAT,
            e9_open FLOAT, e9_high FLOAT, e9_low FLOAT, e9_close FLOAT,
            breach_line FLOAT, predictor_min FLOAT, predictor_maj FLOAT,
            exit_support FLOAT, exit3_support FLOAT,
            breach_slope FLOAT, exit2_ref FLOAT, exit2_ref_dt DATETIME, bl_ext FLOAT,
            predicted TINYINT, exit1 TINYINT, exit2 TINYINT, exit3 TINYINT,
            breach_dir TINYINT, state TINYINT, combined_state TINYINT, raw_pk TINYINT, bny30_bias TINYINT,
            swing_closest_dt DATETIME, entry_dt DATETIME, swing_adverse_dt DATETIME)''')
        if not rows:
            return
        cols = ['bar_time', 'line_name', 'px_smooth',
                'c9_open', 'c9_high', 'c9_low', 'c9_close',
                'e9_open', 'e9_high', 'e9_low', 'e9_close',
                'breach_line', 'predictor_min', 'predictor_maj', 'exit_support', 'exit3_support',
                'breach_slope',
                'exit2_ref', 'exit2_ref_dt', 'bl_ext',
                'predicted', 'exit1', 'exit2', 'exit3', 'breach_dir', 'state',
                'combined_state', 'raw_pk', 'bny30_bias', 'swing_closest_dt', 'entry_dt', 'swing_adverse_dt']
        ph = ','.join(['%s'] * len(cols))
        data = [[_dt(r['bar_ms']), r['line_name'], r['px_smooth'],
                 r['c9_open'], r['c9_high'], r['c9_low'], r['c9_close'],
                 r['e9_open'], r['e9_high'], r['e9_low'], r['e9_close'],
                 r['breach_line'], r['predictor_min'], r['predictor_maj'],
                 r['exit_support'], r['exit3_support'], r['breach_slope'],
                 r['exit2_ref'], r['exit2_ref_dt'], r['bl_ext'],
                 r['predicted'], r['exit1'], r['exit2'], r['exit3'],
                 r['breach_dir'], r['state'], r['combined_state'], r['raw_pk'], r['bny30_bias'],
                 (_dt(r['swing_closest_ms']) if r['swing_closest_ms'] else None), _dt(r['bar_ms']),
                 (_dt(r['swing_adverse_ms']) if r['swing_adverse_ms'] else None)] for r in rows]
        self._db.executemany(
            f'INSERT INTO {self._TABLE} ({",".join(cols)}) VALUES ({ph})', data)


def _f(x):
    # 6dp, not 4 — FARTCOIN prints at 0.14xxx (5 decimals); rounding to 4 lopped the
    # 5th digit and showed as a phantom ~3.5 bps "drift" vs TV. The tape is faithful.
    return round(float(x), 6) if x == x else None        # NaN → NULL


def _dt(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
