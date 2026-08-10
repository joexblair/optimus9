"""curl_pred — predict the r-line turn BEFORE its extreme. Joe 0804.

HYPOTHESIS (Joe 0804): "we are not capitalising on momo. if we ride the momo wave to a) a boundary
cross or b) a curl before the boundary, then we can hand a well prepared trade to s6x for exit."

WHY A NEW FUNCTION AND NOT A 5th momo() OUTPUT
  predict_board.py:170 does `st, sl, r2, rw = momo(arr, dr, w)` — a 4-tuple unpack that a 5th
  element breaks. vmomo.py and build_trades2.py:93 are vectorised mirrors that must match momo()
  exactly and would fork. So this lives beside momo(), not inside it. Fold into build_exhv2.py as a
  sibling once a setting is chosen.

SAMPLING (Joe 0804: "the sampling size ... is too fine for curl-pred ... curl-pred will start
testing after `momo` or `curl`, and sample at {sweep value} finer sampling")
  momo() keeps its CURRENT grid: MOMO_STEP_BARS 60 bars (300 s) x MOMO_SAMPLES 12 = 660 bars,
  and its curl quadratic runs on all MOMO_WINDOW_MIN*12 = 720 bars.
  curl_pred runs on a FINER window: step_bars x (samples-1) + 1 bars, both swept.

FIRE RULES swept
  'ahead'   vertex beyond the window end (vtx > 1.0) — the turn has NOT happened yet. The true
            prediction, and the one that can fire BEFORE the extreme.
  'inside'  vertex within CURL_VTX_LO..HI — momo()'s own curl test at a finer scale. Fires at or
            after the turn.
Curvature must OPPOSE the trade: dr -1 (r falling toward 18) turns up, so qa > 0; dr +1 needs qa < 0.

SCORING, against Joe's two guides
  target 1  lead in bars from the fire bar to sw_momo_r_ext_ms. POSITIVE = fired before the extreme.
  target 2  lead in bars from the fire bar to the debounced s6x cross (s46_exit, sx_run_bars >= 3).
Joe: "just prior to the pivot is preferred - it allows an LTF (eg gcs15) to groom the exit", so a
small POSITIVE lead beats both a negative lead and a large positive one.

    python3 curl_pred.py                  # sweep and report
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('RPL_TF_CEILING', '30')
import datetime as dt
import numpy as np
import build_exhv2 as X
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

NPZ = os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp/lines_all.npz'
TFS = (15, 22)
MOMO_STATES = (1, 2)                       # momo | curl — the states that arm curl_pred
STEP_BARS = (1, 2, 3, 6, 12)               # SWEEP: finer grid than momo's 60
SAMPLES = (6, 12, 24)                      # SWEEP: points in the quadratic fit
ARC_MIN = (0.5, 1.0, 2.0, 4.0)             # SWEEP: arc floor. momo's own CURL_ARC_MIN is 4.0
MODES = ('ahead', 'inside')                # SWEEP: see the docstring
u = lambda ms: dt.datetime.utcfromtimestamp(ms / 1000).strftime('%m-%d %H:%M:%S')


def curl_pred(rr, dr, w, step_bars, samples, arc_min, mode):
    """True when the FINER quadratic says r is turning against the trade. Strictly causal:
    every sampled index is <= w, exactly as momo() does at build_exhv2.py:122."""
    nb = step_bars * (samples - 1) + 1
    if w - nb + 1 < 0:
        return False
    idx = np.arange(w - nb + 1, w + 1, step_bars)
    y = rr[idx]
    if not np.isfinite(y).all():
        return False
    x = np.linspace(0.0, 1.0, len(y))
    qa, qb, _ = np.polyfit(x, y, 2)
    if abs(qa) < 1e-12:
        return False
    # curvature must OPPOSE the trade: dr -1 travels DOWN to 18, so a turn is qa > 0
    if not ((qa > 0) if dr < 0 else (qa < 0)):
        return False
    if abs(qa) * 0.25 < arc_min:
        return False
    vtx = -qb / (2 * qa)
    return (vtx > 1.0) if mode == 'ahead' else (X.CURL_VTX_LO < vtx < X.CURL_VTX_HI)


def first_fire(rr, dr, a, b_end, cfg):
    """first bar in [a, b_end] where curl_pred fires. None if it never does."""
    for w in range(a, b_end + 1):
        if curl_pred(rr, dr, w, *cfg):
            return w
    return None


def main():
    d = np.load(NPZ)
    ts = d['ts'].astype(np.int64)
    G = {tf: {'p': d['g%d_p' % tf], 'n': d['g%d_n' % tf]} for tf in TFS}
    R = {tf: d['r%d' % tf].astype(float) for tf in TFS}

    db = DatabaseManager(**get_db_config()); db.connect()
    rows = db.execute('SELECT sw_n,sw_entry_ms,sw_exit_ms,sw_dr,sw_entry_utc,sw_momo_activated_ms,'
                      'sw_momo_r_ext,sw_momo_r_ext_ms FROM s46_window ORDER BY sw_n', fetch=True)
    EXR = db.execute("SELECT sx_ms,sx_dir FROM s46_exit WHERE sx_line='s6x' AND sx_run_bars>=3 "
                     'ORDER BY sx_ms', fetch=True)
    db.disconnect()
    SX = {dr_: np.array(sorted(int(r['sx_ms']) for r in EXR if int(r['sx_dir']) == dr_), np.int64)
          for dr_ in (1, -1)}
    live = [r for r in rows if r['sw_momo_activated_ms'] and r['sw_momo_r_ext_ms']]
    print('s46_window rows %d   armed (momo activated AND r-ext known) %d' % (len(rows), len(live)))
    print('momo grid: step %d bars x %d samples = %d bars.  curl quadratic: %d bars.'
          % (X.MOMO_STEP_BARS, X.MOMO_SAMPLES,
             X.MOMO_STEP_BARS * (X.MOMO_SAMPLES - 1) + 1, X.MOMO_WINDOW_MIN * 12))
    print()

    out = []
    for mode in MODES:
        for sb in STEP_BARS:
            for ns in SAMPLES:
                for am in ARC_MIN:
                    cfg = (sb, ns, am, mode)
                    L1, L2, nfire = [], [], 0
                    for r in live:
                        dr = int(r['sw_dr'])
                        a = int(np.searchsorted(ts, int(r['sw_momo_activated_ms'])))
                        xe = int(np.searchsorted(ts, int(r['sw_momo_r_ext_ms'])))
                        # search from the momo activation bar up to the extreme bar. Firing AFTER the
                        # extreme is a miss by construction, so the window ends there.
                        for tf in TFS:
                            w = first_fire(R[tf], dr, a, xe, cfg)
                            if w is None:
                                continue
                            nfire += 1
                            L1.append(xe - w)                      # bars BEFORE the extreme
                            sm = SX[dr]
                            j = int(np.searchsorted(sm, int(ts[w])))
                            if j < len(sm):
                                L2.append(int((sm[j] - ts[w]) / 5000))
                            break                                  # first TF to fire wins
                    if nfire < 5:
                        continue
                    a1 = np.array(L1, float); a2 = np.array(L2, float)
                    out.append(dict(mode=mode, sb=sb, ns=ns, am=am, n=nfire,
                                    cov=100.0 * nfire / len(live),
                                    l1med=float(np.median(a1)), l1p25=float(np.percentile(a1, 25)),
                                    l2med=float(np.median(a2)) if len(a2) else float('nan'),
                                    l2n=len(a2)))
    print('  %-7s %5s %4s %5s %5s %6s %9s %9s %9s'
          % ('mode', 'step', 'smp', 'arc', 'n', 'cov%', 'lead-ext', 'p25-ext', 'lead-s6x'))
    print('  (lead in 5 s bars. POSITIVE = fired BEFORE the event. small positive is the target.)')
    for o in sorted(out, key=lambda z: abs(z['l1med'] - 12)):
        print('  %-7s %5d %4d %5.1f %5d %6.0f %9.0f %9.0f %9.0f'
              % (o['mode'], o['sb'], o['ns'], o['am'], o['n'], o['cov'],
                 o['l1med'], o['l1p25'], o['l2med']))


if __name__ == '__main__':
    main()
