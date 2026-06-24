"""
bias_machine.py — beta engine for the bias-machine grind.

Single-sources every line config + the pk / entry / exit mechanics so sweeps, pine emits and
validators share ONE implementation (kills the per-script duplication + config drift that let
the 0.72/0.73 s14M slip through). First consumer: bias_pk_grind.py.

Canonical config (bias_machine_spec.md + Joe 0617):
  generic per-TF set (every TF except 7):  m BB 10|0.4|hlc3 · M BB 37|0.72|ohlc4 · r K 5|6|6|close
  s14 set (TF7, doubled):                  m BB 20|0.77|hlc3 · M BB 74|0.73|ohlc4 · r K 10|12|12|hl2
  s30 set (30s):                           m BB 10|0.40|hlc3 · M BB 37|0.72|ohlc4 · r K 5|6|6|close
  anchor/floater ruler  s6r = generic r @ TF6 (K 5|6|6|close)
  gate line             s14M (the s14 M line, 74|0.73|ohlc4) — used by BOTH the pk gate and exit-A
  OOB 85/15 · NEUTRAL_BAND 2.2 · 33K lots · 0.11% rt fee
Reversal (s30M wobslay) = 1-BAR off the OOB extreme on closed bars. The 2-bar/10s rule is
emerging-only (prod). The pk-anchor trigger (s{tf}m local extremum) is unchanged (3-point).
TF7 is the s14 slot → the generic TF axis excludes 7: TFS = (4,5,6,8,9,10,11,12).
"""
import math
import numpy as np
import logging
from dataclasses import dataclass
for _n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(_n).setLevel('ERROR')
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.analysis.bl_detect import BLDetect
from optimus9.compute.pk5s_gate_computer import Pk5sGateComputer
from optimus9.compute.pk_vote_machine import PKVoteMachine
from optimus9.orchestration.gate_signal_sweep import apply_decision_delay

OOB_HI, OOB_LO = 85.0, 15.0
NEUTRAL_BAND = 2.2
COINS, FEE_RT = 33_000, 0.11
H = 3600_000
TFS = (4, 5, 6, 8, 9, 10, 11, 12)          # generic TF axis (7 == s14 slot, excluded)
S3_ENTRY_TOL = 7 * 6                        # s3 confluence tolerance: 7 × 30s bars (in 5s base bars)

# line configs — ('bb', length, mult, src) | ('k', rsi_len, stc_len, k_len, src)
GEN_M = ('bb', 10, 0.4, 'hlc3')            # generic m  (pk trigger + exit-B m)
GEN_R = ('k', 6, 6, 5, 'close')            # generic r  (anchor ruler + exit-B r)
S30M  = ('bb', 37, 0.72, 'ohlc4')
S30m  = ('bb', 10, 0.40, 'hlc3')
S30r  = ('k', 6, 6, 5, 'close')
S14m  = ('bb', 20, 0.77, 'hlc3')           # exit-A gate
S14M  = ('bb', 74, 0.73, 'ohlc4')          # pk gate + exit maj (unified 0.73)
S14r  = ('k', 12, 12, 10, 'hl2')
S3M_E = ('bb', 10, 0.4, 'ohlc4')           # s3 entry m-line — ohlc4 (smoothed vs GEN_M hlc3) to damp double-spikes
MO12m = ('bb', 7, 0.64, 'close')           # "momentum" series (Joe 0619): osc-only swap vs s12m; trigger stays s12m
XM45m = ('bb', 111, 0.99, 'ohlc4')         # xm45 set (TF45=45s): premature-s30a filter (Joe 0618)
XM45M = ('bb', 222, 0.92, 'hlcc4')
XM45r = ('k', 40, 96, 12, 'close')         # display k12|rsi40|stc96|close
SEQ_CAP = 252                              # sequential cascade cap: 21 min (7 TF3 bars) in base 5s bars
XM45R_LOOKBACK = 720                       # xm45r OOB lookback = 1 hour in base 5s bars


def _sign(v):
    return np.where(v >= OOB_HI, 1, np.where(v <= OOB_LO, -1, 0))


class LineStore:
    """SRP: resolve a bias line `ind_name` → (tf_seconds, cfg-tuple) from vw_indicator_configs_live
    (the ic_live_after_dt view). Building (resample/align) stays with the window — this only owns the
    DB lookup. cfg-tuple matches BiasWindow._raw: ('bb', len, mult, src) | ('k', rsi, stc, k, src)."""
    def __init__(self, db):
        self._db = db; self._cache = {}

    def resolve(self, ind_name):
        if ind_name not in self._cache:
            r = self._db.execute(
                '''SELECT ic_line_type lt, ic_src src, ic_bb_len, ic_bb_mult, ic_rsi_len,
                          ic_stc_len, ic_k_len, itf_seconds
                   FROM vw_indicator_configs_live WHERE ind_name = %s''', (ind_name,), fetch=True)
            if not r:
                raise ValueError(f'no live indicator_configs for {ind_name!r}')
            c = r[0]
            cfg = ('bb', c['ic_bb_len'], float(c['ic_bb_mult']), c['src']) if c['lt'] == 'bb' \
                else ('k', c['ic_rsi_len'], c['ic_stc_len'], c['ic_k_len'], c['src'])
            self._cache[ind_name] = (int(c['itf_seconds']), cfg)
        return self._cache[ind_name]


@dataclass
class BiasConfig:
    """Single source of truth for one bias-machine run: line refs (by ind_name, resolved live from
    the DB) + mechanism knobs. Defaults reproduce the pre-config-drive engine behaviour exactly."""
    # line refs (ind_name in vw_indicator_configs_live)
    osc:    str = 's6r'                 # bias_pk_osc — anchor/floater value source (default ruler)
    gate_M: str = 's14M'
    gate_r: str = 's14r'
    gate_m: str = 's14m'
    s3_m:   str = 's3m'
    s3_r:   str = 's3r'
    s3_M:   str = 's3M'
    s30_M:  str = 's30M'
    s30_m:  str = 's30m'
    s30_r:  str = 's30r'
    xm45_m: str = 'xm45m'
    xm45_M: str = 'xm45M'
    xm45_r: str = 'xm45r'
    # mechanism knobs
    trigger_tf:     int   = 12         # trigger line = generic m @ this TF (s12m) — the flagged tf() seam
    trigger_src:    str   = GEN_M[3]   # pk-trigger src (default hlc3 = GEN_M); grind seam: hlc3 vs close
    gate:           str   = 'oob'      # 'oob' (s14M|s14r OOB) | 'mid' (s14M vs 50)
    floater_anchor: str   = 'same'     # 'same' = g[S] | 'last' = single g slot (any side)
    flt_half:       int   = 2          # ±N osc-bar floater scan (0 = no scan, None = legacy rolling-avg)
    g_gated:        bool  = False      # False = g updates ungated (0617) | True = only on gate-open reversals
    verdict:        str   = 'magnitude'# 'magnitude' | 'pk'
    slope_floor:    float = 0.0        # pk-verdict only (noise gate on |osc_slope − price_slope|)
    delay:          int   = 0          # pk-verdict only (decision delay over the event sequence)
    entry_order:    str   = 'co'       # 'co' | 'seq'
    s3_variant:     str   = 'rM'       # 'm' | 'r' | 'M' | 'rM'
    xm45:           bool  = False
    mae:            float = 0.4
    target:         float = 0.9
    xm45r_lookback: int   = 720


class BiasWindow:
    """One rolling window. Precomputes the shared lines + s30 wobs; lazily caches per-TF lines."""

    def __init__(self, db, end, lookback=168, warmup=80, cfg=None):
        self.cfg = cfg or BiasConfig()
        self._ls = LineStore(db)
        det = BLDetect(db, lookback_hours=lookback, warmup_hours=warmup)
        base, ts, _ws, _x, px = det._setup(end)
        self.base, self.ts, self.px = base, ts, px
        self.W1 = min(int(ts[-1]), end)
        self.W0 = self.W1 - lookback * H
        self._tfcache = {}
        c = self.cfg
        # every named line is resolved LIVE from vw_indicator_configs_live (no tuples)
        self.s6r = self._line('s6r')                          # anchor ruler (ups_s6r_anchor)
        otf, _ = self._ls.resolve(c.osc)
        self._osc = self._line(c.osc); self._bpt = otf // 5   # bias_pk_osc (cfg-driven) + base 5s bars/osc-TF bar
        self.s14M = self._line(c.gate_M)
        self.s14M_sign = _sign(self.s14M)
        self.s14r_sign = _sign(self._line(c.gate_r))          # gate = s14M OR s14r OOB
        self.s14m_sign = _sign(self._line(c.gate_m))
        self._build_s30_wobs()
        self.s3m_sign = _sign(self._line(c.s3_m))             # s3 entry m
        self.s3r_sign = _sign(self._line(c.s3_r))             # s3 entry r (= generic r @180)
        self.s3M_sign = _sign(self._line(c.s3_M))             # s3 Major (alt to s3r in the entry)
        self.xm45m_sign = _sign(self._line(c.xm45_m))         # xm45 set (TF45) — premature-s30a filter
        self.xm45M_sign = _sign(self._line(c.xm45_M))
        self.xm45r_recent = {s: self._recent_oob(_sign(self._line(c.xm45_r)), s, c.xm45r_lookback) for s in (1, -1)}
        self._entry_cfg = dict(ordering=c.entry_order, variant=c.s3_variant, xm45=c.xm45)

    # ── line builders ──
    def _raw(self, tf_sec, cfg):
        fr = IC.resample(self.base, tf_sec)
        if cfg[0] == 'bb':
            v = IC.f_bb(IC.build_source(fr, cfg[3]), cfg[1], cfg[2])
        else:
            v = IC.f_k(IC.build_source(fr, cfg[4]), cfg[1], cfg[2], cfg[3])
        return v, fr

    def _aligned(self, tf_sec, cfg):
        v, fr = self._raw(tf_sec, cfg)
        return IC.align_to_base(v, fr, self.base)

    def _line(self, ind_name):
        """Base-aligned line built from its LIVE DB config (vw_indicator_configs_live)."""
        return self._aligned(*self._ls.resolve(ind_name))

    def _line_emerging(self, ind_name, anchor='midnight'):
        """Developing (emerging) line — one value per 5s bar against the forming higher-TF bar, via
        f_*_lookahead. For the blp set (Joe 0620). anchor='midnight' (TV-aligned, the blp default;
        non-day-divisor TFs drift on the epoch grid — TODO: source the anchor from a DB column)."""
        tf_sec, cfg = self._ls.resolve(ind_name)
        if cfg[0] == 'bb':
            return IC.f_bb_lookahead(self.base, tf_sec, cfg[1], cfg[2], cfg[3], anchor=anchor)
        return IC.f_k_lookahead(self.base, tf_sec, cfg[3], cfg[1], cfg[2], cfg[4], anchor=anchor)

    # ── blp line-positioning mechanic (Joe 0620) ──────────────────────────────────────────────
    def blp14(self):
        """The 3 emerging blp14 lines sampled on the 1-min cycle. Returns (sample_bars, {k: vals}),
        where vals[k] is the emerging blp14k at each minute-aligned base bar."""
        if not hasattr(self, '_blp14'):
            mins = np.where(self.ts % 60_000 == 0)[0]                  # minute-aligned 5s bars
            self._blp14 = (mins, {k: self._line_emerging(f'blp14{k}')[mins] for k in ('m', 'M', 'r')})
        return self._blp14

    def blp_crosses(self):
        """Any-pair crossover among the emerging blp14 m/M/r lines on the 1-min samples. A cross =
        the (a−b) ordering flips between consecutive valid minute samples. Returns dicts:
        (t, bar, pair, before=(a,b), after=(a,b)) — before = last sample pre-cross, after = at cross."""
        mins, L = self.blp14()
        pairs = (('m', 'M'), ('m', 'r'), ('M', 'r'))
        out = []; prev = {p: None for p in pairs}
        for i, j in enumerate(mins):
            for a, b in pairs:
                va, vb = L[a][i], L[b][i]
                if np.isnan(va) or np.isnan(vb):
                    continue
                p = prev[(a, b)]
                if p is not None and (p[0] - p[1]) * (va - vb) < 0:    # ordering flipped → cross
                    out.append(dict(t=int(self.ts[j]), bar=int(j), pair=(a, b),
                                    before=(round(float(p[0]), 1), round(float(p[1]), 1)),
                                    after=(round(float(va), 1), round(float(vb), 1))))
                prev[(a, b)] = (va, vb)
        return out

    def blp_signals(self, wob_tol_min=2):
        """Line-positioning cascade → blp14 m×M cross signals (Joe 0620 v2). At each s30M wob (side S =
        its OOB side), require on side S: ANY s22 line OOB · xm45a · a blp14 **m×M** cross with BOTH m,M
        OOB on S, within ±wob_tol of the wob. s14M is NOT a gate here — annotated 'GATED' if its line is
        IB. Label colour follows the s14M side-of-50. gravity = blp14M or s22M on the OTHER side of 50.
        FLAGGED ASSUMPTIONS: side S = the s30M-wob side; both m,M OOB tested at the cross's after-values."""
        mins, L = self.blp14()
        s22M, s22m, s22r = self._line('s22M'), self._line('s22m'), self._line('s22r')
        s22sign = {'m': _sign(s22m), 'M': _sign(s22M), 'r': _sign(s22r)}
        mM = [c for c in self.blp_crosses() if c['pair'] == ('m', 'M')]     # the m×M crosses only
        tol = wob_tol_min * 60_000
        out = []
        for T, J, S in ((self.HT, self.HJ, 1), (self.LT, self.LJ, -1)):
            for wt, wj in zip(T, J):
                wt, wj = int(wt), int(wj)
                if not (self.W0 <= wt <= self.W1):                       continue
                if not any(s22sign[k][wj] == S for k in ('m', 'M', 'r')): continue  # ANY s22 line OOB on S
                if not bool(self._xm45_ok(wj, wj + 1, S)[0]):            continue   # xm45a
                oob = (lambda x: x >= OOB_HI) if S == 1 else (lambda x: x <= OOB_LO)
                cand = [c for c in mM if abs(c['t'] - wt) <= tol         # m×M cross, both OOB on S, ±tol
                        and oob(c['after'][0]) and oob(c['after'][1])]
                if not cand:                                             continue
                cx = min(cand, key=lambda c: abs(c['t'] - wt))
                mi = int(np.searchsorted(mins, wj, side='right')) - 1
                other = (L['M'][mi] - 50) * S < 0 or (s22M[wj] - 50) * S < 0
                grav = round(float(L['M'][mi] if (L['M'][mi] - 50) * S < 0 else s22M[wj]), 1) if other else None
                out.append(dict(wob_t=wt, side=S, cross=cx, gravity=grav,
                                gated=bool(self.s14M_sign[wj] == 0),       # s14M IB → 'GATED'
                                s14_hi=bool(self.s14M[wj] > 50)))          # colour per s14M side-of-50
        return out

    def _at(self, t):
        return int(np.searchsorted(self.ts, t, side='right')) - 1

    # ── s30 entry/exit wobs (1-bar off the OOB extreme, all-3 s30 OOB at the extreme) ──
    def _build_s30_wobs(self):
        c = self.cfg
        (s30, cM), (_, cm), (_, cr) = (self._ls.resolve(c.s30_M), self._ls.resolve(c.s30_m),
                                       self._ls.resolve(c.s30_r))
        f30 = IC.resample(self.base, s30)
        t30 = f30['timestamp'].to_numpy() + s30 * 1000
        M = IC.f_bb(IC.build_source(f30, cM[3]), cM[1], cM[2])
        m = IC.f_bb(IC.build_source(f30, cm[3]), cm[1], cm[2])
        r = IC.f_k(IC.build_source(f30, cr[4]), cr[1], cr[2], cr[3])
        hi, lo = [], []
        for i in range(1, len(M)):
            a, b = M[i - 1], M[i]
            if a != a or b != b:
                continue
            if a >= OOB_HI and b < a and m[i - 1] >= OOB_HI and r[i - 1] >= OOB_HI:
                sd = 1
            elif a <= OOB_LO and b > a and m[i - 1] <= OOB_LO and r[i - 1] <= OOB_LO:
                sd = -1
            else:
                continue
            tw = int(t30[i]); j = self._at(tw)
            if j >= 0:
                (hi if sd == 1 else lo).append((tw, j))
        hi.sort(); lo.sort()
        self.HT = np.array([t for t, j in hi]); self.HJ = np.array([j for t, j in hi])
        self.LT = np.array([t for t, j in lo]); self.LJ = np.array([j for t, j in lo])

    def _wob_side(self, sd):
        return (self.HT, self.HJ) if sd == 1 else (self.LT, self.LJ)

    def _recent_oob(self, sign, S, W):
        # per-bar bool: was `sign` OOB on side S at any bar within the prior W base-bars (inclusive)?
        b = (sign == S).astype(np.int64); cs = np.concatenate([[0], np.cumsum(b)])
        idx = np.arange(len(b)); lo = np.maximum(0, idx - W)
        return (cs[idx + 1] - cs[lo]) > 0

    def set_entry(self, ordering='co', variant='rM', xm45=False):
        # A/B entry mode: ordering {'co'=forward-tolerance | 'seq'=sequential cascade};
        # variant {'m','r','M','rM'} = the s3 gate; xm45 = add the xm45a gate.
        self._entry_cfg = dict(ordering=ordering, variant=variant, xm45=xm45)

    def _s3_ok(self, lo, hi, es):
        v = self._entry_cfg['variant']; m = self.s3m_sign[lo:hi] == es
        if v == 'm': return m
        if v == 'r': return m & (self.s3r_sign[lo:hi] == es)
        if v == 'M': return m & (self.s3M_sign[lo:hi] == es)
        return m & ((self.s3r_sign[lo:hi] == es) | (self.s3M_sign[lo:hi] == es))

    def _xm45_ok(self, lo, hi, es):
        return (self.xm45m_sign[lo:hi] == es) & (self.xm45M_sign[lo:hi] == es) & self.xm45r_recent[es][lo:hi]

    def _entry(self, t_up, bd, deadline=None, s3_lookback=0):
        # cascade gate, A/B-configurable via set_entry. order: s3 gate → [xm45a] → s30 wob = entry.
        # deadline = next OPPOSITE pk (cancel). default cfg (co/rM/no-xm45) reproduces prior behaviour.
        cfg = self._entry_cfg; es = -bd; n = len(self.s3m_sign)
        if cfg['ordering'] == 'co':                            # s30 wob first; s3 within S3_ENTRY_TOL fwd; xm45a at wob
            ET, EJ = self._wob_side(-bd)
            ei = int(np.searchsorted(ET, t_up, side='right'))
            while ei < len(EJ):
                et = int(ET[ei])
                if deadline is not None and et >= deadline:
                    return None, None
                ej = int(EJ[ei]); hi = min(ej + S3_ENTRY_TOL + 1, n)
                if np.any(self._s3_ok(ej, hi, es)) and (not cfg['xm45'] or bool(self._xm45_ok(ej, ej + 1, es)[0])):
                    return ej, et
                ei += 1
            return None, None
        # sequential: s3 opens → xm45a opens → next s30 wob, all within SEQ_CAP of the pk
        j0 = self._at(t_up); cap = min(j0 + SEQ_CAP, n)
        lo = max(0, j0 - s3_lookback * 36)                     # s3 lookback: N s3-bars back (s3 = TF180 = 36 base bars)
        w1 = np.where(self._s3_ok(lo, cap, es))[0]
        if not len(w1):
            return None, None
        s2 = lo + int(w1[0])                                   # s3 gate bar (may precede the pk when found via lookback)
        if cfg['xm45']:
            w2 = np.where(self._xm45_ok(s2, cap, es))[0]
            if not len(w2):
                return None, None
            s2 = s2 + int(w2[0])
        ET, EJ = self._wob_side(-bd)
        ei = int(np.searchsorted(ET, int(self.ts[max(s2, j0)]), side='right'))   # entry follows the pk (lookback relaxes the gate, not the entry)
        if ei >= len(EJ):
            return None, None
        et = int(ET[ei]); ej = int(EJ[ei])
        if ej > cap or (deadline is not None and et >= deadline):
            return None, None
        return ej, et

    def _deadlines(self, ups):
        # per pk, the time of the next OPPOSITE-direction pk (BULL↔BEAR). NEUT/VOID neither cancel
        # nor are cancelled. An entry must trigger strictly before this time or the pk is void.
        out = [None] * len(ups); next_bull = next_bear = None
        for i in range(len(ups) - 1, -1, -1):
            c = ups[i]['call']
            if c == 'BEAR':
                out[i] = next_bull
            elif c == 'BULL':
                out[i] = next_bear
            if c == 'BULL':
                next_bull = ups[i]['t']
            elif c == 'BEAR':
                next_bear = ups[i]['t']
        return out

    # ── per-TF generic lines (cached): m & r aligned + their OOB-sign arrays ──
    def tf(self, tf):
        key = (tf, self.cfg.trigger_src)                       # trigger src is a grind seam (hlc3 vs close)
        if key not in self._tfcache:
            sec = tf * 60
            mb, fr = self._raw(sec, (GEN_M[0], GEN_M[1], GEN_M[2], self.cfg.trigger_src))
            ma = IC.align_to_base(mb, fr, self.base)
            ra = self._aligned(sec, GEN_R)
            self._tfcache[key] = dict(mb=mb, tc=fr['timestamp'].to_numpy() + sec * 1000,
                                      m_sign=_sign(ma), r_sign=_sign(ra))
        return self._tfcache[key]

    # ── pk anchor triggers: s{tf}m local extrema (3-point), with side-of-50 s6r resolution ──
    def trigs(self, tf):
        d = self.tf(tf); mb, tc = d['mb'], d['tc']
        out = []
        for k in range(2, len(mb)):
            a, b, c = mb[k - 2], mb[k - 1], mb[k]
            if a != a or b != b or c != c:
                continue
            S = -1 if (b <= OOB_LO and b < a and b < c) else (1 if (b >= OOB_HI and b > a and b > c) else 0)
            if S == 0:
                continue
            rt = int(tc[k - 1]); j = self._at(rt)
            if j >= 0:
                out.append(dict(t=rt, j=j, s=S, oscv=self._osc[j]))
        return out                                            # raw reversals; side-of-50 + floater live in ups()

    def set_osc(self, line, bpt):
        """Swap the bias_pk_osc — the line anchor/floater are read from. bpt = base 5s bars per its
        TF bar (TF6→72, TF12→144). Trigger TF is chosen separately via the trigs(tf) passed to ups()."""
        self._osc = line; self._bpt = bpt

    def _floater_extreme(self, center, S, half_base):
        # confirmed osc extreme within ±half_base base-bars of the last anchor's bar. The window is
        # the rolling-average same-side anchor spacing (round-up-to-even), so it can't overshoot/look
        # ahead beyond a typical peak gap. Returns (value, bar) or (None, None) if the window is all-NaN.
        lo = max(0, center - half_base); hi = min(len(self._osc), center + half_base + 1)
        seg = self._osc[lo:hi]
        if not np.any(~np.isnan(seg)):
            return None, None
        idx = int(np.nanargmax(seg) if S == 1 else np.nanargmin(seg))
        bj = lo + idx
        return float(self._osc[bj]), bj

    # ── SRP split (Joe 0619): pk_events builds the anchor/floater stream (NO verdict); verdict_*
    #    apply a decision over that stream. ups() = magnitude verdict — kept as the future SnF meld seam.
    def pk_events(self, trigs, gate, flt_half=2, floater_src='same', g_gated=False):
        # EVENT STREAM ONLY — no call. rule (Joe 0617): a wrong-side print can't be consumed → dropped
        # (no anchor, g untouched). anchor = raw osc at the reversal; floater = the CONFIRMED osc extreme
        # near the SOURCE anchor's bar. floater_src: 'same' = last SAME-side anchor g[S] (default, current
        # behaviour); 'last' = last anchor of ANY side (single g slot, Joe 0619).
        # g_gated (Joe 0620, A/B): False = g updates on every right-side reversal, s14M only decides firing
        # (the 0617 rule); True = g updates ONLY on gate-OPEN reversals (a gate-shut pivot isn't a valid
        # floater). floater absent only at epoch. window = ±flt_half osc-TF bars (default 2; flt_half=0 ⇒
        # no scan = raw osc at the source bar; flt_half=None ⇒ legacy rolling-avg-of-last-7-gaps).
        # The scan finds the extreme on the FLOATER ANCHOR's OWN side (stored in g), not the current
        # event's side — so a 'last' floater off an other-side anchor scans the right extreme (Joe 0620).
        BPT = self._bpt
        out = []; g = {1: None, -1: None}; g_last = None; dq = {1: [], -1: []}
        for W in trigs:
            S = W['s']; v = W['oscv']
            if not ((S == 1 and v > 50) or (S == -1 and v < 50)):
                continue                                       # wrong-side → cannot be consumed
            flt_src = g_last if floater_src == 'last' else g[S]   # (bar, anchor_side) | None
            gate_ok = (self.s14M_sign[W['j']] == S or self.s14r_sign[W['j']] == S) if gate == 'oob' \
                else ((self.s14M[W['j']] > 50) == (S == 1))
            if (not g_gated) or gate_ok:                       # gate the g-update only when g_gated
                if flt_half is None and flt_src is not None:
                    dq[S].append(round((W['j'] - flt_src[0]) / BPT)); dq[S] = dq[S][-7:]
                g[S] = (W['j'], S); g_last = (W['j'], S)       # floater source = prev valid anchor (bar, side)
            if not gate_ok or flt_src is None or not (self.W0 <= W['t'] <= self.W1):
                continue
            half = flt_half if flt_half is not None else math.ceil((sum(dq[S]) / len(dq[S])) / 2)
            fv, fv_bar = self._floater_extreme(flt_src[0], flt_src[1], half * BPT)
            if fv is None:
                continue
            out.append(dict(t=W['t'], side=S, anc=round(float(v), 1), flt=round(float(fv), 1),
                            anc_bar=W['j'], flt_bar=fv_bar))
        return out

    def verdict_magnitude(self, events):
        # verdict by |anchor − floater|: NEUT inside the band, else BULL/BEAR by which is higher.
        return [dict(e, call=('NEUT' if abs(e['anc'] - e['flt']) <= NEUTRAL_BAND
                              else ('BULL' if e['anc'] > e['flt'] else 'BEAR'))) for e in events]

    def verdict(self, events):
        # apply the CONFIGURED verdict to an event stream (single-sources cfg.verdict → method).
        # consumers feed the stream here instead of binding to a baked-in call.
        c = self.cfg
        if c.verdict == 'pk':
            return self.verdict_pk(events, c.slope_floor, c.delay)
        return self.verdict_magnitude(events)

    # ── cfg-driven bias signal stream: trigs → events → configured verdict (the consumer entry-point) ──
    def signals(self):
        c = self.cfg
        events = self.pk_events(self.trigs(c.trigger_tf), c.gate, c.flt_half, c.floater_anchor, c.g_gated)
        return self.verdict(events)

    # ── gated pk updates → list of dict(t, side, call, …) ; call ∈ BULL/BEAR/NEUT ──
    def ups(self, trigs, gate, flt_half=2):
        # magnitude verdict over the event stream — back-compat wrapper + the seam SnF will meld
        # multiple pk signals through. Behaviour-identical to the pre-split ups().
        return self.verdict_magnitude(self.pk_events(trigs, gate, flt_half))

    # ── alt anchor (Joe 0617): s6m reversal ARMS, then wait for s6r to reverse; anchor = the s6r
    #    extreme (max hi / min lo) over [arm → s6r reversal]. pk fires at the s6r-reversal bar. ──
    def _s6r_swing_extreme(self, s, j, S):
        n = len(s); best = s[j]; bj = j; k = j
        if best != best:
            return None, None, None
        while k + 1 < n:
            v = s[k + 1]
            if v != v:
                break
            if (S == 1 and v >= best) or (S == -1 and v <= best):
                best = v; bj = k + 1; k += 1                # still extending the swing
            else:
                return float(best), bj, k + 1               # s6r reversed against S
        return float(best), bj, k                           # ran to data-end

    def ups_s6r_anchor(self, gate='oob', tf=6):
        ruler = self.s6r if tf == 6 else self._aligned(tf * 60, GEN_R)  # s{tf}r anchor/floater ruler
        out = []; last = {1: None, -1: None}
        for W in self.trigs(tf):                             # s{tf}m reversals arm the watch
            S = W['s']; anc, aj, rj = self._s6r_swing_extreme(ruler, W['j'], S)
            if anc is None:
                continue
            flt = last[S]; last[S] = (anc, aj)               # floater = prev same-side anchor (value, bar)
            if gate == 'oob' and not (self.s14M_sign[W['j']] == S or self.s14r_sign[W['j']] == S):
                continue
            if flt is None:
                continue
            flt_v, flt_bar = flt
            t = int(self.ts[rj])
            if not (self.W0 <= t <= self.W1):
                continue
            call = 'NEUT' if abs(anc - flt_v) <= NEUTRAL_BAND else ('BULL' if anc > flt_v else 'BEAR')
            out.append(dict(t=t, side=S, call=call, anc=round(anc, 1), flt=round(flt_v, 1),
                            anc_bar=aj, flt_bar=flt_bar))
        cnt = {}
        for o in out:
            cnt[o['t']] = cnt.get(o['t'], 0) + 1
        for o in out:
            if cnt[o['t']] > 1:
                o['call'] = 'VOID'                            # competing same-bar decisions → both void
        return out

    # ── pk-machine feed (Joe 0617): replace the raw anchor>floater call with the pk machine's
    #    divergence/PM verdict. line_slope = osc(anchor)−osc(floater), price_slope =
    #    px_smooth(anchor)−px_smooth(floater) → _pk_state_from_slopes → close/wide probes →
    #    PKVoteMachine → pk_raw → apply_decision_delay over the EVENT sequence. Returns ups-like
    #    directional calls. NOTE: decision_delay counts pk EVENTS here, not bars — flagged for Joe.
    def verdict_pk(self, events, slope_floor, delay, w_close=5, w_wide=2, thr=7.5, pm_suppress=0.4):
        # verdict by the pk machine over the FULL event stream (no pre-filter coupling). line_slope =
        # osc(anc)−osc(flt), price_slope = px_smooth(anc)−px_smooth(flt) → _pk_state_from_slopes
        # (divergence ±1 fires direction / PM ±2 votes 0 → single-line suppress) → PKVoteMachine →
        # apply_decision_delay over the EVENT sequence. NOTE: decision_delay counts pk EVENTS, not bars.
        if not events:
            return []
        states = np.array([
            float(Pk5sGateComputer._pk_state_from_slopes(
                e['anc'] - e['flt'], self.px[e['anc_bar']] - self.px[e['flt_bar']], slope_floor))
            for e in events], dtype=float)
        probe = {(0, 'close'): states, (0, 'wide'): states}
        wts   = {(0, 'close'): w_close, (0, 'wide'): w_wide}
        pk_raw = PKVoteMachine(pm_suppress_str=pm_suppress).aggregate(probe, wts, thr, thr)['pk_raw']
        delayed = apply_decision_delay(pk_raw, delay)
        out = []; prev = 0
        for e, d in zip(events, delayed):
            d = int(d)
            if d != 0 and d != prev:
                out.append(dict(e, call=('BULL' if d == 1 else 'BEAR')))
            prev = d
        return out

    def pk_feed(self, ups, slope_floor, delay, w_close=5, w_wide=2, thr=7.5, pm_suppress=0.4):
        # back-compat wrapper (the OLD coupled path): pre-filter to magnitude-directional events, then
        # verdict_pk. SRP-clean path is verdict_pk(pk_events(...)) over the full, unfiltered stream.
        return self.verdict_pk([u for u in ups if u['call'] in ('BULL', 'BEAR')],
                               slope_floor, delay, w_close, w_wide, thr, pm_suppress)

    # ── trades: entry = next aligned s30 wob; exit = next opposite s30 wob with gate lines OOB ──
    # exit_signs = list of base-aligned OOB-sign arrays that must all == bias dir at the exit wob.
    def run(self, ups, exit_signs, stop=None):
        # stop (optional): hard %-stop with ACTUAL-tape fill — exits the first 5s bar whose adverse
        # move ≤ -stop, before the confluence exit. None = no stop (the reconstruction baseline).
        px = self.px; trades = []; seen = set(); dl = self._deadlines(ups)
        for idx, u in enumerate(ups):
            if u['call'] in ('NEUT', 'VOID'):
                continue
            bd = 1 if u['call'] == 'BULL' else -1
            ej, et = self._entry(u['t'], bd, dl[idx])          # cancel if entry falls after opposite pk
            if ej is None or ej in seen:
                continue
            seen.add(ej)
            XT, XJ = self._wob_side(bd)                        # exit side = bd (opposite the entry)
            xi = int(np.searchsorted(XT, et, side='right')); xj = xt = None
            while xi < len(XJ):
                jj = int(XJ[xi])
                if all(s[jj] == bd for s in exit_signs):
                    xj = jj; xt = int(XT[xi]); break
                xi += 1
            eod = xj is None
            if eod:
                xj = len(px) - 1; xt = self.W1
            ep = float(px[ej])
            if stop is not None:                               # truncate at the first stop breach
                adverse = bd * (px[ej:xj + 1] - ep) / ep * 100.0
                hit = np.where(adverse <= -stop)[0]
                if len(hit):
                    xj = ej + int(hit[0]); xt = int(self.ts[xj]); eod = False
            xp = float(px[xj])
            seg = bd * (px[ej:xj + 1] - ep) / ep * 100.0       # signed % path in bias dir
            mae = float(seg.min()); mfe = float(seg.max())     # worst adverse / best favourable
            move = float(seg[-1])
            pnl = COINS * ep * (move - FEE_RT) / 100.0
            trades.append(dict(et=et, xt=xt, ep=ep, xp=xp, bd=bd, pnl=pnl,
                               mae=mae, mfe=mfe, eod=eod))
        return trades


    # placement metric: after each pk update, the following trade is allowed `mae_allow`% adverse;
    # potential profit = max favourable % reached BEFORE that adverse breach (walk to data-end).
    # correctly-placed iff potential ≥ target%. Exit is irrelevant here — this scores pk placement.
    def placements(self, ups, mae_allow=0.3, target=0.9, s3_lookback=0):
        px = self.px; out = []; seen = set(); dl = self._deadlines(ups)
        for idx, u in enumerate(ups):
            if u['call'] in ('NEUT', 'VOID'):
                continue
            bd = 1 if u['call'] == 'BULL' else -1
            ej, et = self._entry(u['t'], bd, dl[idx], s3_lookback)   # cancel if entry falls after opposite pk
            if ej is None or ej in seen:
                continue
            seen.add(ej)
            ep = float(px[ej])
            seg = bd * (px[ej:] - ep) / ep * 100.0             # forward signed % path to data-end
            br = np.where(seg <= -mae_allow)[0]
            k = int(br[0]) if len(br) else len(seg)            # first −mae_allow breach (or end)
            potential = float(seg[:k].max())                   # MFE before the adverse breach
            mae = float(seg[:k].min())                          # MAE: worst adverse excursion pre-breach (≤0)
            hit = potential >= target
            tt = None
            if hit:
                tg = np.where(seg[:k] >= target)[0]
                if len(tg):
                    tt = (int(self.ts[ej + int(tg[0])]) - et) // 1000
            stop_s = (int(self.ts[ej + k]) - et) // 1000 if len(br) else None
            out.append(dict(pk_t=u['t'], et=et, bd=bd, potential=round(potential, 3),
                            mae=round(mae, 3), hit=hit, secs_to_target=tt, secs_to_stop=stop_s,
                            anc=u.get('anc'), flt=u.get('flt')))
        return out


def stopped_net(trades, stop_pct):
    """Reconstruct a config's net$ at a given hard stop, from recorded MAE (no re-run needed).
    A trade whose MAE breached -stop exits at -(stop+fee)·notional; else keeps realized pnl."""
    if stop_pct is None:
        return sum(t['pnl'] for t in trades)
    tot = 0.0
    for t in trades:
        if t['mae'] <= -stop_pct:
            tot += -COINS * t['ep'] * (stop_pct + FEE_RT) / 100.0
        else:
            tot += t['pnl']
    return tot
