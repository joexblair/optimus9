"""predict_board — the 5-min prediction watch READER. Joe 0802.

WHAT IT IS. One read-only snapshot of the board, printed for the prediction session to reason over.
It NEVER writes, and it NEVER touches the jig process, build_rpl_jig.py, exhv2 or the gates
(docs/260802_predict_rsd_handover.md §1).

WHAT IT PRINTS, in order
  1. TRIGGER   s1Mage (jg_mg1) / s2Mage (jg_mg2) vs HI 85.0 / LO 15.0, plus the rising-edge time of the
               current OOB stretch. Handover §3.3 rule 2: predict ONLY when s1M OR s2M is OOB.
  2. MOMO      s4r / s15r / s22r through a LOCAL copy of exhv2's momo() formula. Handover §3.2 forbids
               `import build_exhv2` here — it pulls the whole RPL chain and costs >2 min. The knobs are
               read from the handover table: SAMPLES 12, STEP 60 bars = 5 min, window 660 bars = 55 min,
               SLOPE_MIN 1.0, R2_MIN 0.50, LEVEL_SLACK 13.9, CURL_ARC_MIN 4.0.
  3. BOARD     the full banked configuration — x/m/M at s4/s15, the five rsd Mages, s1r/s30r,
               h30/h45/h60/h90, the gather spread + boundary distance, r-pred flags and gaps.
  4. LEDGER    every jp_outcome='open' row in rpl_jig_pred with its favourable excursion so far, in %,
               against the 0.9% bar. Scoring is one-sided (handover §3.3 rule 1): a call can reach
               `right`; nothing here can mark it wrong.

DIRECTION CONVENTION. `dr` for momo is the side the triggering Mage breached: OOB-hi -> +1, OOB-lo -> -1.
Same convention exhv2 uses for the walk (`ed` resolves to the breach side in all four bias/side cases).
If s1M and s2M are OOB on OPPOSITE sides, both are printed and neither is picked.

    python3 predict_board.py            # snapshot + ledger
    python3 predict_board.py --bars 900 # widen the r history slice (default 900 = 75 min)
"""
import sys, logging
import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
logging.disable(logging.INFO)
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

HI, LO = 85.0, 15.0          # optimus9_system.hi_boundary / lo_boundary
BAR_MS = 5000
PCT = 0.9                    # handover §3.3: work = price moves >= 0.9% in the prediction's direction

# momo knobs — handover §3.3 table. Reimplemented, NOT imported.
MOMO_SAMPLES    = 12         # point samples in the fit
MOMO_STEP_BARS  = 60         # 60 bars = 5 min at the 5 s grid
MOMO_SLOPE_MIN  = 1.0        # r-units per 5-min sample
MOMO_R2_MIN     = 0.50
MOMO_WINDOW_MIN = 60
LEVEL_SLACK     = 13.9
CURL_ARC_MIN    = 4.0
CURL_VTX_LO, CURL_VTX_HI = 0.05, 0.95
NEED_BARS = (MOMO_SAMPLES - 1) * MOMO_STEP_BARS + 1   # 661 bars = 55.1 min of r history


def momo(r, dr, w):
    """(state, slope, r2, r_at_bar) at bar index `w`. Verbatim copy of build_exhv2.momo() — the import
    is banned in this session (handover §3.3). Any divergence here is a defect, not a variant."""
    idx = np.array([w - k * MOMO_STEP_BARS for k in range(MOMO_SAMPLES - 1, -1, -1)])
    if idx[0] < 0:
        return 'none', 0.0, 0.0, float('nan')
    y = r[idx]
    if not np.isfinite(y).all():
        return 'none', 0.0, 0.0, float('nan')
    x = np.arange(len(y), dtype=float)
    sl, ic = np.polyfit(x, y, 1)
    res = ((y - (sl * x + ic)) ** 2).sum(); tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - res / tot if tot > 1e-12 else 0.0
    rw = float(r[w])
    trk = max(0.0, min(1.0, float(r2) * min(1.0, abs(sl) / max(1e-9, MOMO_SLOPE_MIN))))
    slack = LEVEL_SLACK * trk
    level = (rw >= 50 - slack) if dr > 0 else (rw <= 50 + slack)
    if abs(sl) < MOMO_SLOPE_MIN:
        if not level:
            return 'none', float(sl), float(r2), rw
        nb = MOMO_WINDOW_MIN * 12
        if w - nb + 1 >= 0:
            yy = r[w - nb + 1:w + 1]
            if np.isfinite(yy).all():
                xx = np.linspace(0.0, 1.0, len(yy))
                qa, qb, _ = np.polyfit(xx, yy, 2)
                if abs(qa) > 1e-12:
                    vtx = -qb / (2 * qa); arc = abs(qa) * 0.25
                    if CURL_VTX_LO < vtx < CURL_VTX_HI and arc >= CURL_ARC_MIN:
                        return 'curl', float(sl), float(r2), rw
        return 'sideways', float(sl), float(r2), rw
    aligned = (sl > 0) if dr > 0 else (sl < 0)
    if level and aligned and r2 >= MOMO_R2_MIN:
        return 'momo', float(sl), float(r2), rw
    return 'none', float(sl), float(r2), rw


def side_of(v):
    """'hi' above HI, 'lo' below LO, '' in-bounds."""
    if v is None or not np.isfinite(v):
        return ''
    return 'hi' if v >= HI else ('lo' if v <= LO else '')


def edge_ms(rows, col):
    """Start ms of the CURRENT uninterrupted OOB stretch of `col`, or None if in-bounds at the last bar.
    Walks backwards from the last bar — causal, no forward index."""
    if not rows:
        return None
    s = side_of(rows[-1][col])
    if not s:
        return None
    ms = rows[-1]['jg_ms']
    for r in reversed(rows[:-1]):
        if side_of(r[col]) != s:
            break
        ms = r['jg_ms']
    return ms


def f(v, n=2):
    return 'n/a' if v is None or not np.isfinite(float(v)) else ('%.*f' % (n, float(v)))


def main():
    argv = sys.argv[1:]
    nbars = int(argv[argv.index('--bars') + 1]) if '--bars' in argv else 900

    db = DatabaseManager(**get_db_config()); db.connect()
    rows = db.execute(
        "SELECT * FROM rpl_jig WHERE jg_kind='heartbeat' ORDER BY jg_ms DESC LIMIT %s",
        (max(nbars, NEED_BARS + 60),), fetch=True)
    rows = list(reversed(rows or []))
    if not rows:
        print('NO HEARTBEATS — the jig is not writing. Say so; do not restart it.')
        db.disconnect(); return
    cur = rows[-1]
    w = len(rows) - 1

    import time as _t
    age = _t.time() * 1000 - cur['jg_ms']
    gaps = np.diff([r['jg_ms'] for r in rows[-121:]])
    print('== JIG ==')
    print('  run %s   last %s   age %.0f s   bars held %d' % (cur['jg_run'], cur['jg_utc'], age / 1000, len(rows)))
    # LIVENESS and CONTINUITY are different questions and were conflated. The gap scan looks back over
    # the last 121 rows, so a hole left by an earlier outage keeps reading STALL long after the jig is
    # writing again — it did exactly that at 21:14:55, age 17 s, max gap 1,500,000 ms from the 20:48-21:13
    # outage. Liveness is `age` at the CURRENT bar; continuity is the gap history. Reported separately.
    print('  LIVENESS  age %.0f s  -> %s' % (
        age / 1000, 'ALIVE' if age <= 60000 else 'STALE — restart it (cron rule 6)'))
    print('  CONTINUITY last 120 gaps: min %d ms  max %d ms  %s' % (
        gaps.min(), gaps.max(),
        'clean' if gaps.max() <= 10000 else 'HOLE of %.1f min in the window — excursion inside it is '
                                            'unmeasured for every call open across it' % (gaps.max() / 60000.0)))

    # ---- 1. TRIGGER -------------------------------------------------------------------------
    print('\n== TRIGGER (handover §3.3 rule 2: predict ONLY on s1M or s2M OOB) ==')
    trig = []
    for nm, col in (('s1M', 'jg_mg1'), ('s2M', 'jg_mg2')):
        v = cur[col]; s = side_of(v)
        e = edge_ms(rows, col)
        held = '' if e is None else '  stretch %.1f min from %s' % (
            (cur['jg_ms'] - e) / 60000.0, next(r['jg_utc'] for r in rows if r['jg_ms'] == e))
        print('  %-4s %8s   %s%s' % (nm, f(v), ('OOB-' + s) if s else 'in-bounds', held))
        if s:
            trig.append((nm, s, e))
    if not trig:
        print('  >> NO TRIGGER. Do not predict this cycle. Do not fabricate one to fill the watch.')
    sides = {s for _, s, _ in trig}

    # ---- 2. MOMO ----------------------------------------------------------------------------
    print('\n== MOMO  s4r / s15r / s22r  (rule 3: momo -> continuation, no momo -> exhaustion) ==')
    if len(rows) < NEED_BARS:
        print('  history %d bars < %d needed (55 min) — momo unavailable this cycle' % (len(rows), NEED_BARS))
    for s in (sorted(sides) or []):
        dr = 1 if s == 'hi' else -1
        print('  dr=%+d (breach side %s)' % (dr, s))
        for nm, col in (('s4r', 'jg_r4'), ('s15r', 'jg_r15'), ('s22r', 'jg_r22')):
            arr = np.array([r[col] if r[col] is not None else np.nan for r in rows], float)
            st, sl, r2, rw = momo(arr, dr, w)
            print('    %-5s r %6s   %-8s slope %+7.3f  R2 %5.3f' % (nm, f(rw), st, sl, r2))

    # ---- 3. BOARD ---------------------------------------------------------------------------
    print('\n== BOARD  %s ==' % cur['jg_utc'])
    print('  pxs %.8f   close %.8f' % (cur['jg_pxs'], cur['jg_close']))
    # s4m / s4x are computed by the jig but NOT banked as columns — only jg_m4 (s4Mage), jg_r4, jg_gap4
    print('  s4:   M %8s  m    n/a   x    n/a   r %6s   gap %s  rp %s' % (
        f(cur['jg_m4']), f(cur['jg_r4']), f(cur['jg_gap4']), cur['jg_rp4']))
    print('  s15:  M %8s  m %8s  x %8s  r %6s   gap %s  rp %s' % (
        f(cur['jg_m15M']), f(cur['jg_m15']), f(cur['jg_x15']), f(cur['jg_r15']),
        f(cur['jg_gap15']), cur['jg_rp15']))
    print('  s22:  M %8s                          r %6s   gap %s  rp %s' % (
        f(cur['jg_m22M']), f(cur['jg_r22']), f(cur['jg_gap22']), cur['jg_rp22']))
    print('  gcs15: x %8s  m %8s' % (f(cur['jg_g15x']), f(cur['jg_g15m'])))
    print('  Mages: mg5 %7s  mg15 %7s  mg30 %7s  mg1 %7s  mg2 %7s' % (
        f(cur['jg_mg5']), f(cur['jg_mg15']), f(cur['jg_mg30']), f(cur['jg_mg1']), f(cur['jg_mg2'])))
    print('  r:     s1r %6s  s30r %6s  s4r %6s  s15r %6s  s22r %6s' % (
        f(cur['jg_s1r']), f(cur['jg_s30r']), f(cur['jg_r4']), f(cur['jg_r15']), f(cur['jg_r22'])))
    print('  HTF:   h30 %6s  h45 %6s  h60 %6s  h90 %6s' % (
        f(cur['jg_h30']), f(cur['jg_h45']), f(cur['jg_h60']), f(cur['jg_h90'])))
    print('  gather spread:  g5 %6s  g15 %6s  s30 %6s  s1 %6s' % (
        f(cur['jg_gsp_g5']), f(cur['jg_gsp_g15']), f(cur['jg_gsp_s30']), f(cur['jg_gsp_s1'])))
    print('  gather bnd-dist:g5 %6s  g15 %6s  s30 %6s  s1 %6s' % (
        f(cur['jg_gbd_g5']), f(cur['jg_gbd_g15']), f(cur['jg_gbd_s30']), f(cur['jg_gbd_s1'])))
    print('  walk:  s4M %s  side %s  dir %s  run_bars %s  qualified %s  hops %s' % (
        f(cur['jg_m4']), cur['jg_side'], cur['jg_dir'], cur['jg_run_bars'], cur['jg_qualified'], cur['jg_hops']))
    print('  s15 %s slope %s R2 %s   s22 %s slope %s R2 %s   (jig-banked, walk-bar reads)' % (
        cur['jg_s15_state'], f(cur['jg_s15_slope'], 3), f(cur['jg_s15_r2'], 3),
        cur['jg_s22_state'], f(cur['jg_s22_slope'], 3), f(cur['jg_s22_r2'], 3)))
    print('  rsd Mages lastoob %s   mid %s' % (cur['jg_mage_lastoob'], cur['jg_mage_mid']))

    # ---- 4. LEDGER --------------------------------------------------------------------------
    print('\n== OPEN CALLS  (one-sided: reaches 0.9% -> right; nothing here marks a call wrong) ==')
    opens = db.execute(
        "SELECT jp_pk, jp_at_ms, jp_at_utc, jp_claim FROM rpl_jig_pred WHERE jp_outcome='open' ORDER BY jp_pk",
        fetch=True) or []
    if not opens:
        print('  none')
    for o in opens:
        head = (o['jp_claim'] or '').strip().upper()
        d = 1 if head.startswith('LONG') else (-1 if head.startswith('SHORT') else 0)
        px = db.execute(
            "SELECT jg_pxs FROM rpl_jig WHERE jg_kind='heartbeat' AND jg_ms>=%s ORDER BY jg_ms",
            (o['jp_at_ms'],), fetch=True) or []
        p = np.array([r['jg_pxs'] for r in px], float)
        if len(p) < 2:
            print('  #%d %s  no bars yet' % (o['jp_pk'], o['jp_at_utc'])); continue
        p0 = p[0]
        up = (p.max() / p0 - 1) * 100
        dn = (1 - p.min() / p0) * 100
        if d == 0:
            print('  #%d %s  DIRECTION UNPARSED (claim does not start LONG/SHORT) — up %.3f%% / down %.3f%%, '
                  'age %.1f min. Needs a Joe ruling, not a guess.'
                  % (o['jp_pk'], o['jp_at_utc'], up, dn, (p.size * BAR_MS) / 60000.0))
            continue
        fav, adv = (up, dn) if d > 0 else (dn, up)
        print('  #%d %s  %-5s  entry %.8f  fav %+.3f%%  adv %-.3f%%  age %.1f min  %s'
              % (o['jp_pk'], o['jp_at_utc'], 'LONG' if d > 0 else 'SHORT', p0, fav, adv,
                 (p.size * BAR_MS) / 60000.0,
                 '>>> REACHED 0.9%% — mark right' if fav >= PCT else 'open (%.3f%% to go)' % (PCT - fav)))
    db.disconnect()


if __name__ == '__main__':
    main()
