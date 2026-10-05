"""THE UPSTREAM SWEEP. Joe 1005: objective "best PnL with minimal loss of trades", budget 12 hours.

WHY THIS IS POSSIBLE AT ALL — a measurement that corrected my own 25.3-day estimate:
`sweep_v3_signal.Rig((ms0, ms1))` IGNORES its window. Measured 1005: Rig(10-04), Rig(09-25) and
Rig(07-23) all return the IDENTICAL span 07-02 12:00 -> 10-04 23:59 at n=1,632,960. So the 58-64 s
load is per PROCESS, not per day or per cell. Memoising it leaves ~36 s per day of actual walk.

    per upstream cell = days x ~36 s   (not days x 96 s)

The walk itself is NOT re-implemented. `report_leash_walk.main()` is called as-is with `S.Rig`
monkeypatched to hand back the cached instance, so the signals come from the same producer that
made every banked number. Re-implementing it is exactly the divergence the stage-1 harness check
was built to catch.

argv:  upstream.py <knob> <lo> <hi> <step> [more knob quads...]
env:   LG_DAYS_FIT, LG_DAYS_TEST (comma lists)  ·  LG_TAPE_END
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, io, time, contextlib, datetime as dt
import numpy as np

sys.argv_orig = list(sys.argv)
sys.argv = ['x', '--tape-end', _os.environ.get('LG_TAPE_END', '2026-10-05')]
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, _HERE)
_e = sys.stderr; sys.stderr = io.StringIO()
import report_leash_walk as RLW
from optimus9.analysis import jig as JIG
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e
S3 = RLW.S

# ---- the Rig, ONCE
_RIG = None
_REAL_RIG = S3.Rig
def _cached_rig(window):
    global _RIG
    if _RIG is None:
        t = time.time(); _RIG = _REAL_RIG(window)
        print('# Rig loaded once in %.1f s | n=%d' % (time.time() - t, _RIG.n), flush=True)
    return _RIG
S3.Rig = _cached_rig

def walk_day(day):
    """-> [(bar_label, dr)] the R| rows report_leash_walk emits for this day. Same producer."""
    sys.argv = ['x', '--day', day, '--tape-end', _os.environ.get('LG_TAPE_END', '2026-10-05')]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        with contextlib.redirect_stderr(io.StringIO()):
            try: RLW.main()
            except SystemExit: pass
    rows = []
    for ln in buf.getvalue().splitlines():
        if ln.startswith('R|') and not ln.startswith('R|run'):
            f = ln.split('|')
            if len(f) >= 7: rows.append(f[2])
    return rows

# ---- the 32 upstream knobs: where each one lives and how to set it
def set_jig(name, val):   setattr(JIG, name, val)
def set_rlw(name, val):   setattr(RLW, name, val)

KNOBS = {   # name -> (setter, cast)
 'WS1MR_DWELL':   (set_jig, int), 'WS1MR_REV_WOB': (set_jig, int), 'WS1MR_HOLD': (set_jig, int),
 'SR_SAMPLES':    (set_jig, int), 'SR_TOL':        (set_jig, float), 'SR_TEST':   (set_jig, int),
 'WSF_N':         (set_jig, int), 'WSF_HANDICAP':  (set_jig, int),
 'WSF_WS1_XWOB':  (set_jig, int), 'WMT_TF_LO':     (set_jig, int), 'WMT_TF_HI': (set_jig, int),
 'WMT_LOOKBACK_S':(set_jig, int), 'AF_BLOCK':      (set_jig, int),
 'MOMO_SAMPLES':  (set_rlw, int), 'MOMO_TOL':      (set_rlw, float),
}
ORIG = {}
def snapshot():
    for k, (setter, _c) in KNOBS.items():
        mod = JIG if setter is set_jig else RLW
        ORIG[k] = getattr(mod, k, None)
def restore():
    for k, v in ORIG.items():
        if v is not None: KNOBS[k][0](k, v)

if __name__ == '__main__':
    a = sys.argv_orig[1:]
    FIT = [x.strip() for x in _os.environ.get('LG_DAYS_FIT', '').split(',') if x.strip()]
    TEST = [x.strip() for x in _os.environ.get('LG_DAYS_TEST', '').split(',') if x.strip()]
    snapshot()
    print('# upstream harness | FIT %s | TEST %s' % (','.join(FIT), ','.join(TEST)), flush=True)
    print('# knobs settable in-process: %d of 32 — %s' % (len(KNOBS), ', '.join(sorted(KNOBS))), flush=True)
    t0 = time.time()
    r0 = walk_day(FIT[0])
    print('# first walk (%s): %.1f s, %d R| rows — the Rig cost is inside this one' % (FIT[0], time.time()-t0, len(r0)), flush=True)
    t1 = time.time(); r1 = walk_day(FIT[0] if len(FIT) < 2 else FIT[1])
    print('# second walk: %.1f s, %d R| rows — this is the TRUE per-day cost' % (time.time()-t1, len(r1)), flush=True)
    import resource
    print('# peak RSS this process: %.2f GB  -> safe parallelism on 15 GB free = %d processes'
          % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1048576.0,
             int(15.0 / max(0.5, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1048576.0))), flush=True)
    # which of the 4 fences and 13 momentum knobs are reachable?
    import optimus9.compute.momo_config as MC2
    print('# momo_config reachable: %s' % hasattr(MC2,'momo_bank'), flush=True)
