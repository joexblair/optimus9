"""Sweep the knobs that move the sig_utc signal, end to end, scored against the causal baseline.

Joe 0929: "sweep everything that touches, especially the span and slope_min", "be granular",
"always small steps, and read from full datasets (as opposed to sampling)", "keep sweeping until
you've exhausted every idea".

THE CHAIN, rebuilt in memory per config - nothing is written to any table:
  1  sideways per (bar, TF)     fastverdict.sideways_mask, PROVEN identical to momo_g_why
                                (0 mismatches, 8 TFs x 86,400 bars, 0929)
  2  v3 rows                    one per (line, dr run): the FIRST bar in that run where r is
                                sideways AND outside the fence - verbatim from build_wsf_dtf_v3
  3  moments                    consecutive ok rows at one dr, ok = support_count >= support_min
  4  release + resolve          coil_moment.release and coil_exit.resolve, unchanged
  5  rule#1 gate                rule1_gate.gate, config v2, unchanged
  6  walk                       trade_walk.walk, unchanged
  7  score                      MAE/MFE at the EMIT bar - max(brk, rev, actionable) - which is the
                                first bar o9-live can act on, so every row is comparable to the
                                baseline

THE BASELINE TO BEAT, whole book at the emit bar:
    118 trades | MFE>MAE 65 (55.1%) | MAE mean 0.724 | MFE mean 0.914 | summed MFE-MAE +22.349

    python3 sweep_v3_signal.py --grid span_slope
"""
import argparse, io, json, sys, time, itertools
import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
import build_wsf_trades as BWT, report_coil_exit as RCE
from fastverdict import sideways_mask
from optimus9.compute import trade_config as TC, coil_exit
from optimus9.compute.coil_moment import moments as coil_moments, release
from optimus9.compute.stretchy_leash import combined_coil, coil as leash_coil
from optimus9.compute.v3_config import v3_config
from optimus9.compute.dr_latch import latch_wob
from optimus9.compute.momo_config import momo_bank
from optimus9.compute.rule1_gate import gate
from optimus9.compute.trade_walk import walk as twalk, mae_mfe

NO_FLIP_OPEN = False                       # set by --no-flip-open; Joe 0929 ruled the backstop out
                                           # as an OPENER after seeing the measurement


def walk_no_flip_open(opens, dr, start, end):
    """trade_walk.walk with the dr-flip's OPEN removed. The close is untouched, and so is the
    opposing-dr rule on sig_utc. Joe 0929: "dr-flip as an open is not helpful"."""
    O = set(int(x) for x in opens); start = max(1, int(start)); out = []; pos = None
    for k in range(start, int(end) + 1):
        if pos is not None:
            d = int(dr[k])
            if d == -pos['dr'] and d != 0:
                pos['left'] = True
            if pos['left'] and d == pos['dr'] and d != int(dr[k - 1]):
                out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                opened_by=pos['opened_by'], closed_by='dr-flip'))
                pos = None
                continue
        if k in O:
            d = int(dr[k])
            if pos is not None and not (d == -pos['dr'] and d != 0):
                continue                   # same-dr sig_utc is INERT - Joe 0929
            if pos is not None:
                out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                opened_by=pos['opened_by'], closed_by='sig_utc'))
            pos = dict(open=k, dr=d, opened_by='sig_utc', left=False)
    return out, pos
from optimus9.analysis.jig import anchor_floater, ws1mage_rev
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e

BASE = dict(span=10, slope=0.4, samples=21, fence_lo=25.0, fence_hi=75.0,
            support_min=23, tf_lo=1, tf_hi=23, confirm_lag_s=180, lookback_s=240,
            gap_fill=1, boundary_xwob=4, rev_wob=2, dwell=3, level_slack=13.9,
            slack_ref=None, curl_arc_min=4.0, curl_vtx_lo=0.05, curl_vtx_hi=0.95)


class Rig:
    """Everything that does not change between configs, loaded once.

    `win` overrides the scoring window. The sweep is fitted on 2026-09-01..09-06, the leash bank's
    own window; a holdout on earlier tape is the only way to tell a real knob from the best of 182
    noisy draws.
    """

    def __init__(self, win=None):
        db = DatabaseManager(**get_db_config()); db.connect()
        TC.seed(db, TC.V); self.Ct = TC.load(db, TC.V); self.C = v3_config(db)
        self.ts, self.lines, self.hi, self.lo, self.tfs = RCE.load(db, self.C)
        self.BK = {tf: momo_bank(db, tf, version=1) for tf in self.tfs}
        db.disconnect()
        ts = self.ts; n = len(ts); self.n = n
        w = win or BWT.WIN_MS
        self.A = int(np.searchsorted(ts, w[0]))
        self.B = min(int(np.searchsorted(ts, w[1])), n - 1)   # to_ms past the tape end clamps here
        G1 = np.asarray(self.lines['ws1']['Mage'], float)
        M13 = np.asarray(self.lines['ws13']['m'], float)
        DR = np.zeros(n, np.int8); cur = 0
        for k in range(n):
            a, b = G1[k], M13[k]
            if a == a and b == b:
                if a >= 85.0 and b >= 85.0: cur = +1
                elif a <= 15.0 and b <= 15.0: cur = -1
            DR[k] = cur
        self.DR = DR
        self.DRW = latch_wob(G1, np.asarray(self.lines['ws%d' % int(self.Ct['latch_tf'])]['m'], float),
                             0, n - 1, wob=int(self.Ct['latch_wob']),
                             hi=float(self.Ct['mage_fence_hi']), lo=float(self.Ct['mage_fence_lo']))
        db = DatabaseManager(**get_db_config()); db.connect()
        _t, r1, r2, r3, g30r, xn, px, m1, mx = BWT.load(db, self.Ct)
        db.disconnect()
        # THE TWO LOADERS MUST BE ON THE SAME BAR GRID. gate_open() indexes r1/r2/r3/g30r/px with a
        # bar number derived from self.ts, which came from RCE.load. build_wsf_trades binds END_MS
        # BY VALUE at import, so a process that walks more than one window and does not reload it
        # gets a different tape here and rule#1 reads the r lines at the wrong bars - silently.
        # 0930: oos_confirm_lag and score_5day_windows both did exactly that.
        _t = np.asarray(_t, np.int64)
        if len(_t) != n or not np.array_equal(_t, np.asarray(ts, np.int64)):
            raise RuntimeError(
                'Rig tape mismatch: report_coil_exit gave %d bars %d..%d, build_wsf_trades gave '
                '%d bars %d..%d. Reload build_wsf_trades after changing END_MS.'
                % (n, int(ts[0]), int(ts[-1]), len(_t),
                   int(_t[0]) if len(_t) else -1, int(_t[-1]) if len(_t) else -1))
        self.r1, self.r2, self.r3, self.g30r, self.xn, self.px = r1, r2, r3, g30r, xn, px
        self.R = {tf: np.asarray(self.lines['ws%d' % tf]['r'], float) for tf in self.tfs}
        # the dr runs inside the window, verbatim from build_wsf_dtf_v3
        segs = []; s = self.A
        for k in range(self.A + 1, self.B + 1):
            if DR[k] != DR[k - 1]: segs.append((s, k - 1, int(DR[s]))); s = k
        segs.append((s, self.B, int(DR[s])))
        self.segs = segs
        # the leash coil, per dr, over the coil_lines - independent of every swept knob so far
        CK = self.C['coil_lines']
        self.CC = np.sum(np.vstack([leash_coil(self.lines[k]['m'], self.lines[k]['Mage'],
                                               self.lines[k]['r'], 1) for k in CK]), axis=0)
        # per-band leash coil sign, for support_count at any support_min
        self.D = {tf: (np.asarray(self.lines['ws%d' % tf]['m'], float)
                       + np.asarray(self.lines['ws%d' % tf]['Mage'], float)) / 2.0
                  - np.asarray(self.lines['ws%d' % tf]['r'], float) for tf in self.tfs}
        self._gate = {}
        self._sw = {}

    def segs_for(self, A, B):
        """The dr runs inside [A, B], verbatim from build_wsf_dtf_v3's own segment loop."""
        DR = self.DR; out = []; s = A
        for k in range(A + 1, B + 1):
            if DR[k] != DR[k - 1]: out.append((s, k - 1, int(DR[s]))); s = k
        out.append((s, B, int(DR[s])))
        return out

    def sideways(self, tf, cfg):
        """Cached per (tf, span, slope, samples, level_slack, slack_ref, curl knobs).

        The cache is capped: 60 masks x 1.7M bools is about 100 MB, and a span/slope grid reuses
        none of them across configs, so an uncapped cache would run to several GB.
        """
        key = (tf, cfg['span'], cfg['slope'], cfg['samples'], cfg['level_slack'],
               cfg['slack_ref'], cfg['curl_arc_min'], cfg['curl_vtx_lo'], cfg['curl_vtx_hi'])
        if key not in self._sw:
            if len(self._sw) > 60:
                self._sw.clear()
            step = max(1, int(round((cfg['span'] * 12) / (cfg['samples'] - 1))))
            nb = cfg['span'] * 12
            sref = cfg['slope'] if cfg['slack_ref'] is None else cfg['slack_ref']
            self._sw[key] = sideways_mask(self.R[tf], self.DR, cfg['samples'], step, nb,
                                          cfg['slope'], sref, cfg['level_slack'],
                                          cfg['curl_vtx_lo'], cfg['curl_vtx_hi'],
                                          cfg['curl_arc_min'])
        return self._sw[key]

    def gate_open(self, k, back_bars=None):
        """rule#1 at bar `k`. -> bool.

        `back_bars` None reads `rule1_back_min` from the config — 7.0 min = 84 bars, Joe 0929, and
        every existing caller gets exactly that. `leash_walk` passes 60 bars = 5 min from
        `walk_rule1_back_min`, Joe 1001 asked 5 or 7 for that row: *"5"*. The cache is keyed on the
        lookback so the two cannot be confused for each other.
        """
        Ct = self.Ct
        bb = int(float(Ct['rule1_back_min']) * 60 / 5) if back_bars is None else int(back_bars)
        ck = (int(k), bb)
        if ck not in self._gate:
            d = int(self.DRW[k])
            res = anchor_floater(self.r1, self.px, d, k, block=int(self.C['block']), mid=50.0,
                                 xn=self.xn,
                                 dwell_bars=int(Ct['div_tf']) * int(self.C['dwell_min_per_tf']) * 12,
                                 oob=(float(Ct['oob_lo']), float(Ct['oob_hi'])))
            self._gate[ck] = bool(gate(
                self.r1, self.r2, self.r3, self.g30r, d, k, bb,
                (float(Ct['rule1_fence_lo']), float(Ct['rule1_fence_hi'])),
                (float(Ct['oob_lo']), float(Ct['oob_hi'])),
                0 if res is None else int(res['fired']),
                fwd_bars=int(float(Ct['rule1_fwd_min']) * 60 / 5),
                run_clamp=Ct['rule1_run_clamp'])['open'])
        return self._gate[ck]


def run(rig, cfg, A=None, B=None):
    """One config, end to end. -> dict of results, or None when it produces no trade."""
    A = rig.A if A is None else A
    B = rig.B if B is None else B
    segs = rig.segs_for(A, B)
    tfs = [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
    FL, FH = cfg['fence_lo'], cfg['fence_hi']
    # --- step 2: the v3 rows ---
    rows = []
    for tf in tfs:
        sw = rig.sideways(tf, cfg)
        r = rig.R[tf]
        q = sw & np.isfinite(r) & ((r < FL) | (r > FH))
        for (a_, b_, d) in segs:
            if not d: continue
            seg = q[a_:b_ + 1]
            j = int(np.argmax(seg)) if seg.any() else None
            if j is None: continue
            rows.append((a_ + j, tf, d))
    if not rows: return None
    rows.sort(key=lambda x: (x[0], x[1]))
    # --- step 3: moments ---
    SUP = np.zeros(rig.n, np.int16)
    for tf in tfs:
        SUP += (rig.D[tf] > 0).astype(np.int16)
    SUPM = np.zeros(rig.n, np.int16)
    for tf in tfs:
        SUPM += (rig.D[tf] < 0).astype(np.int16)
    ann = [dict(i=i, dr=d, ok=bool((SUP[i] if d > 0 else SUPM[i]) >= cfg['support_min']))
           for (i, tf, d) in rows]
    MS = coil_moments(ann)
    # --- step 4: release + resolve ---
    lag = cfg['confirm_lag_s'] // 5; look = cfg['lookback_s'] // 5
    LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                       rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                       dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
    EMIT = {}
    for m in MS:
        d = m['dr']
        cc = (lambda i, _d=d: float(rig.CC[i] * _d))
        p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
        ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
        if ex['rev'] is None or not (A <= int(ex['rev']) <= B): continue
        brk = m['brk'] if m['brk'] is not None else m['i1']
        e = max(brk, int(ex['rev']), int(coil_exit.fired(ex)[1]))
        k = int(ex['rev'])
        if k not in EMIT or e < EMIT[k]: EMIT[k] = e
    if not EMIT: return None
    # --- step 5 + 6 ---
    opens = sorted(k for k in EMIT if rig.gate_open(k))
    if not opens: return None
    T, _ = (walk_no_flip_open if NO_FLIP_OPEN else twalk)(opens, rig.DRW, min(opens), B)
    if not T: return None
    # --- step 7: score at the emit bar ---
    keep, miss = [], 0
    for t in T:
        o = EMIT.get(t['open'], t['open'])
        if o >= t['close']: miss += 1; continue
        keep.append((t, mae_mfe(rig.px, o, t['close'], t['dr'])))
    if not keep: return None
    a = np.array([v[0] for _, v in keep]); b = np.array([v[1] for _, v in keep])
    sg = [i for i, (t, _) in enumerate(keep) if t['opened_by'] == 'sig_utc']
    lagm = sorted((int(rig.ts[EMIT[k]]) - int(rig.ts[k])) / 60000.0 for k in EMIT)
    return dict(sig_bars=len(EMIT), gated_out=len(EMIT) - len(opens), trades=len(keep),
                unreachable=miss, win=int((b > a).sum()), pct=100.0 * (b > a).sum() / len(keep),
                mae=float(a.mean()), mfe=float(b.mean()),
                smae=float(a.sum()), smfe=float(b.sum()), net=float(b.sum() - a.sum()),
                sig_n=len(sg), sig_win=int((b[sg] > a[sg]).sum()) if sg else 0,
                sig_mfe=float(b[sg].mean()) if sg else 0.0,
                lag_med=lagm[len(lagm) // 2], lag_max=lagm[-1])


# THREE INDEPENDENT WINDOWS over the 94.5 days of tape the line cache holds. The 5-day leash
# window was never a data limit - this harness reads the line cache, not the leash bank - and a
# 5-day sample is what let the span/slope grid produce a winner with ZERO out-of-sample
# correlation. Joe 0929: "read from full datasets (as opposed to sampling)".
WINDOWS = [('W1 06-10..07-20', 1781049600000, 1784505600000),
           ('W2 07-20..08-29', 1784505600000, 1787961600000),
           ('W3 08-29..09-08', 1787961600000, 1788825600000)]

GRIDS = {
    # slope 0.05 was best at EVERY span in the 3-window grid and 0.05 was the grid edge. This walks
    # below it in small steps to find where the effect stops. Joe 0929: "always small steps".
    'lowslope': [dict(BASE, span=sp, slope=sl)
                 for sp in (6, 7, 8)
                 for sl in (0.002, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.07)],
    'final': [dict(BASE, span=6, slope=0.03), dict(BASE, span=7, slope=0.04),
              dict(BASE, span=8, slope=0.10), dict(BASE, span=12, slope=0.05),
              dict(BASE)],
    # Two independent monotone findings - slope low, fence tight - both reduce trade count. Do they
    # compound, or are they the same signal counted twice? BASE is included as the control.
    'combo': ([dict(BASE, span=sp, slope=sl, fence_lo=f, fence_hi=100.0 - f)
               for sp in (6, 8)
               for sl in (0.03, 0.05, 0.40)
               for f in (10.0, 15.0, 20.0, 25.0)]),
    # fence 10 was the grid EDGE and slope+fence compound super-additively. Push both further and
    # widen the span, to find where it stops.
    'edge': ([dict(BASE, span=sp, slope=sl, fence_lo=f, fence_hi=100.0 - f)
              for sp in (7, 8, 9, 10)
              for sl in (0.02, 0.03, 0.05)
              for f in (2.5, 5.0, 7.5, 10.0)]),
    # fence 2.5 was again the grid edge. Find where it actually stops, and watch the trade count.
    'limit': ([dict(BASE, span=sp, slope=sl, fence_lo=f, fence_hi=100.0 - f)
               for sp in (8, 10, 12)
               for sl in (0.02, 0.03)
               for f in (0.25, 0.5, 1.0, 1.5, 2.0, 2.5)]),
    # tfband, CORRECTED. The first attempt held support_min at 23 while narrowing the band below 23
    # lines, so the support test was unsatisfiable and nothing fired. support_min 23 means "every
    # line supports", so the equivalent for a narrower band is the band's own size.
    'tfband2': ([dict(BASE, tf_lo=1, tf_hi=h, support_min=h) for h in (6, 8, 10, 12, 16, 20, 23)]
                + [dict(BASE, tf_lo=l, tf_hi=23, support_min=23 - l + 1) for l in (2, 3, 5, 7, 9, 13)]
                + [dict(BASE, tf_lo=1, tf_hi=h, support_min=max(1, int(round(h * 0.8))))
                   for h in (8, 12, 16, 23)]),
    # the three-way: every knob with a measured monotone effect, together. All three point the same
    # way - fewer, stronger rows - so they may be partly the same effect. slope+fence already proved
    # super-additive; this asks whether samples adds on top.
    'triple': ([dict(BASE, span=sp, slope=sl, fence_lo=f, fence_hi=100.0 - f, samples=sm)
                for sp in (10, 12)
                for sl in (0.02, 0.40)
                for f in (2.5, 25.0)
                for sm in (9, 21)]),
    # The fourth axis against the other two. `samples` looked good alone and INVERTED in combination,
    # so a knob measured alone proves nothing about the combination. support_min tracks the band
    # size, which is what "every line supports" means for a narrower band.
    'quad': ([dict(BASE, span=10, slope=sl, fence_lo=f, fence_hi=100.0 - f,
                   tf_lo=lo, tf_hi=23, support_min=23 - lo + 1)
              for sl in (0.02, 0.40)
              for f in (2.5, 25.0)
              for lo in (1, 5, 7, 9, 13)]),
    # The one caveat left open at the close: level_slack and momo_slack_ref are provably inert at the
    # BANKED fence, because r outside 25/75 always clears the level gate. Re-check at fence 2.5.
    'inert2': ([dict(BASE, span=10, slope=0.02, fence_lo=2.5, fence_hi=97.5, level_slack=v)
                for v in (0.0, 13.9, 28.0, 40.0, 46.0, 49.0)]
               + [dict(BASE, span=10, slope=0.02, fence_lo=2.5, fence_hi=97.5, slack_ref=v)
                  for v in (0.05, 0.4, 1.2)]),
    # the post-fix cheap test: the banked config, the old sweep's winner, and the fence axis
    'cheap': ([dict(BASE), dict(BASE, span=6, slope=0.03), dict(BASE, span=8, slope=0.10),
               dict(BASE, span=12, slope=0.05),
               dict(BASE, span=10, slope=0.02, fence_lo=2.5, fence_hi=97.5),
               dict(BASE, span=10, slope=0.40, fence_lo=2.5, fence_hi=97.5),
               dict(BASE, span=10, slope=0.02)]),
    'wide': [dict(BASE, span=sp, slope=sl)
             for sp in (5, 6, 7, 8, 9, 10, 12, 14)
             for sl in (0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.60, 0.80)],
    'base': [dict(BASE)],
    'span_slope': [dict(BASE, span=s, slope=sl)
                   for s in (4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 20, 25, 30)
                   for sl in (0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 1.0)],
    # Joe 0929: "always small steps". span 8 / slope 0.10 dominated the first grid and 0.10 was
    # the grid edge, so this walks the neighbourhood in fine steps to find the knee.
    'refine': [dict(BASE, span=s, slope=sl)
               for s in (6, 7, 8, 9, 10)
               for sl in (0.01, 0.02, 0.03, 0.05, 0.07, 0.09, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20,
                          0.22, 0.25)],
    'holdout': ([dict(BASE, span=8, slope=sl) for sl in (0.05, 0.08, 0.10, 0.12, 0.15, 0.20)]
                + [dict(BASE, span=s, slope=0.10) for s in (6, 7, 9, 10)]
                + [dict(BASE, span=5, slope=0.45), dict(BASE, span=4, slope=0.35),
                   dict(BASE)]),
    'samples': [dict(BASE, samples=s) for s in (3, 5, 7, 9, 11, 13, 16, 21, 26, 31, 41, 61, 121)],
    'fence': [dict(BASE, fence_lo=f, fence_hi=100.0 - f)
              for f in (10.0, 12.5, 15.0, 17.5, 20.0, 22.5, 25.0, 27.5, 30.0, 32.5, 35.0, 40.0)],
    'support': [dict(BASE, support_min=s) for s in range(14, 24)],
    'tfband': ([dict(BASE, tf_lo=1, tf_hi=h) for h in (8, 12, 16, 20, 23)]
               + [dict(BASE, tf_lo=l, tf_hi=23) for l in (2, 3, 5, 9, 13)]),
    'slack': [dict(BASE, level_slack=v) for v in (0.0, 5.0, 10.0, 13.9, 18.0, 22.0, 28.0, 34.0, 40.0)],
    'slackref': [dict(BASE, slack_ref=v) for v in (0.05, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.2)],
    'curl': ([dict(BASE, curl_arc_min=v) for v in (0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 1e9)]),
    'leash': ([dict(BASE, confirm_lag_s=v) for v in (60, 90, 120, 150, 180, 240, 300, 420, 600)]
              + [dict(BASE, lookback_s=v) for v in (0, 60, 120, 180, 240, 360, 480, 720)]
              + [dict(BASE, gap_fill=0)]),
    'magerev': ([dict(BASE, boundary_xwob=v) for v in (1, 2, 3, 4, 5, 6, 8, 10, 12)]
                + [dict(BASE, rev_wob=v) for v in (1, 2, 3, 4, 6, 8)]
                + [dict(BASE, dwell=v) for v in (1, 2, 3, 4, 6, 8, 12)]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--grid', required=True)
    ap.add_argument('--out', default='/home/joe/thecodes/docs/sweeps/results.jsonl')
    ap.add_argument('--from-ms', type=int); ap.add_argument('--to-ms', type=int)
    ap.add_argument('--no-flip-open', action='store_true',
                    help='the dr-flip backstop closes but never opens - Joe 0929')
    ap.add_argument('--multiwin', action='store_true',
                    help='score every config on all three WINDOWS instead of one')
    o = ap.parse_args()
    global NO_FLIP_OPEN
    NO_FLIP_OPEN = bool(o.no_flip_open)
    win = (o.from_ms, o.to_ms) if o.from_ms and o.to_ms else None
    rig = Rig(win)
    if win: print('G|WINDOW OVERRIDE|%d..%d|bars %d..%d' % (win[0], win[1], rig.A, rig.B), flush=True)
    g = GRIDS[o.grid]
    print('G|%s|%d configs' % (o.grid, len(g)), flush=True)
    print('G|n|span|slope|samples|fenceLo|supMin|tfLo|tfHi|lag_s|lookback|xwob|sigbars|gated|'
          'trades|MFE>MAE|MAEmean|MFEmean|NET|lagMed|lagMax', flush=True)
    t0 = time.time()
    with open(o.out, 'a') as fh:
        for i, cfg in enumerate(g, 1):
            wins = WINDOWS if o.multiwin else [(None, None, None)]
            for wname, wa, wb in wins:
                A = None if wa is None else int(np.searchsorted(rig.ts, wa))
                B = None if wb is None else min(int(np.searchsorted(rig.ts, wb)), rig.n - 1)
                try:
                    res = run(rig, cfg, A, B)
                except Exception as ex:
                    print('G|%d|%s|ERROR %s' % (i, wname, ex), flush=True); continue
                if res is None:
                    print('G|%d|%s|no trades' % (i, wname), flush=True); continue
                fh.write(json.dumps({'grid': o.grid, 'window': wname or 'default',
                                     'win_from': A if A is not None else rig.A,
                                     'win_to': B if B is not None else rig.B,
                                     **{k: cfg[k] for k in BASE}, **res}) + '\n')
                fh.flush()
                print('W|%3d|%-16s|span %2d slope %.2f samp %2d fnc %.0f sup %2d|%4d tr|%3d (%.1f%%)'
                      '|MAE %.3f|MFE %.3f|NET %+.3f|lag %.1f'
                      % (i, wname or 'default', cfg['span'], cfg['slope'], cfg['samples'],
                         cfg['fence_lo'], cfg['support_min'], res['trades'], res['win'],
                         res['pct'], res['mae'], res['mfe'], res['net'], res['lag_med']),
                      flush=True)
    print('G|done|%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    sys.exit(main())
