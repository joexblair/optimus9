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
from optimus9.analysis.jig import anchor_floater, ws1mage_rev
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e

BASE = dict(span=10, slope=0.4, samples=21, fence_lo=25.0, fence_hi=75.0,
            support_min=23, tf_lo=1, tf_hi=23, confirm_lag_s=180, lookback_s=240,
            gap_fill=1, boundary_xwob=4, rev_wob=2, dwell=3, level_slack=13.9,
            slack_ref=None, curl_arc_min=4.0, curl_vtx_lo=0.05, curl_vtx_hi=0.95)


class Rig:
    """Everything that does not change between configs, loaded once."""

    def __init__(self):
        db = DatabaseManager(**get_db_config()); db.connect()
        TC.seed(db, TC.V); self.Ct = TC.load(db, TC.V); self.C = v3_config(db)
        self.ts, self.lines, self.hi, self.lo, self.tfs = RCE.load(db, self.C)
        self.BK = {tf: momo_bank(db, tf, version=1) for tf in self.tfs}
        db.disconnect()
        ts = self.ts; n = len(ts); self.n = n
        self.A = int(np.searchsorted(ts, BWT.WIN_MS[0]))
        self.B = int(np.searchsorted(ts, BWT.WIN_MS[1]))
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

    def gate_open(self, k):
        if k not in self._gate:
            Ct = self.Ct; d = int(self.DRW[k])
            res = anchor_floater(self.r1, self.px, d, k, block=int(self.C['block']), mid=50.0,
                                 xn=self.xn,
                                 dwell_bars=int(Ct['div_tf']) * int(self.C['dwell_min_per_tf']) * 12,
                                 oob=(float(Ct['oob_lo']), float(Ct['oob_hi'])))
            self._gate[k] = bool(gate(
                self.r1, self.r2, self.r3, self.g30r, d, k,
                int(float(Ct['rule1_back_min']) * 60 / 5),
                (float(Ct['rule1_fence_lo']), float(Ct['rule1_fence_hi'])),
                (float(Ct['oob_lo']), float(Ct['oob_hi'])),
                0 if res is None else int(res['fired']),
                fwd_bars=int(float(Ct['rule1_fwd_min']) * 60 / 5),
                run_clamp=Ct['rule1_run_clamp'])['open'])
        return self._gate[k]


def run(rig, cfg):
    """One config, end to end. -> dict of results, or None when it produces no trade."""
    tfs = [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
    FL, FH = cfg['fence_lo'], cfg['fence_hi']
    # --- step 2: the v3 rows ---
    rows = []
    for tf in tfs:
        sw = rig.sideways(tf, cfg)
        r = rig.R[tf]
        q = sw & np.isfinite(r) & ((r < FL) | (r > FH))
        for (a_, b_, d) in rig.segs:
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
        if ex['rev'] is None or not (rig.A <= int(ex['rev']) <= rig.B): continue
        brk = m['brk'] if m['brk'] is not None else m['i1']
        e = max(brk, int(ex['rev']), int(ex['actionable']))
        k = int(ex['rev'])
        if k not in EMIT or e < EMIT[k]: EMIT[k] = e
    if not EMIT: return None
    # --- step 5 + 6 ---
    opens = sorted(k for k in EMIT if rig.gate_open(k))
    if not opens: return None
    T, _ = twalk(opens, rig.DRW, min(opens), rig.B)
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


GRIDS = {
    'base': [dict(BASE)],
    'span_slope': [dict(BASE, span=s, slope=sl)
                   for s in (4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 20, 25, 30)
                   for sl in (0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 1.0)],
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
    o = ap.parse_args()
    rig = Rig()
    g = GRIDS[o.grid]
    print('G|%s|%d configs' % (o.grid, len(g)), flush=True)
    print('G|n|span|slope|samples|fenceLo|supMin|tfLo|tfHi|lag_s|lookback|xwob|sigbars|gated|'
          'trades|MFE>MAE|MAEmean|MFEmean|NET|lagMed|lagMax', flush=True)
    t0 = time.time()
    with open(o.out, 'a') as fh:
        for i, cfg in enumerate(g, 1):
            try:
                res = run(rig, cfg)
            except Exception as ex:
                print('G|%d|ERROR %s' % (i, ex), flush=True); continue
            if res is None:
                print('G|%d|%s|no trades' % (i, cfg['span']), flush=True); continue
            fh.write(json.dumps({'grid': o.grid, **{k: cfg[k] for k in BASE}, **res}) + '\n')
            fh.flush()
            print('G|%d|%d|%.2f|%d|%.1f|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d (%.1f%%)|%.3f|%.3f|%+.3f|%.1f|%.1f'
                  % (i, cfg['span'], cfg['slope'], cfg['samples'], cfg['fence_lo'],
                     cfg['support_min'], cfg['tf_lo'], cfg['tf_hi'], cfg['confirm_lag_s'],
                     cfg['lookback_s'], cfg['boundary_xwob'], res['sig_bars'], res['gated_out'],
                     res['trades'], res['win'], res['pct'], res['mae'], res['mfe'], res['net'],
                     res['lag_med'], res['lag_max']), flush=True)
    print('G|done|%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    sys.exit(main())
