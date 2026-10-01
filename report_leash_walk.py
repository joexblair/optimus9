"""report_leash_walk — the ACCEPTANCE TEST for the `leash_walk` port, and the recon's reference.

Joe 1001: *"there is no surviving mech that relies on `brk`, because our verified strategy uses
`WALK FIRES FROM` as our one and only signal"* and *"the Joe has validated every row in this report,
and has derived profit only from the `WALK FIRES FROM` timestamps, therefore it is the only outcome
that is stamped as ready for live trading"*.

WHAT IT PROVES. The validated 09-01 report was produced in a job-scoped scratch directory that no
longer exists. This script rebuilds the same 9 signal bars from `optimus9/compute/arm_state.py` and
`optimus9/compute/leash_walk.py` — repo code, knobs from `wsf_trade_config` v4 — and ASSERTS them.
A mismatch exits non-zero and names the bars. That is the point: without this, the handed-over
numbers are a written record rather than a checkable result, which is `OPEN.md`'s own standard.

THE TAPE IS SET EXPLICITLY. `build_ws_lines.TAPE_END` is 2026-09-30 in the repo; the validated run
used **2026-09-08**, and the tape is a FIXED 94.5-day width anchored on its END, so moving the end
moves the start too. This script pins 09-08 for its own run and does not touch the constant.

NOTHING IS CACHED BEYOND THIS PROCESS. `momentum_true` and `flat_run_at` are computed lazily per
(tf, bar, dr) and memoised in memory only. The walk asks for one dr per bar — the arm's — so the
work is a fraction of a precomputed grid, and the shape is the one o9-live uses.

    python3 report_leash_walk.py
    python3 report_leash_walk.py --day 2026-09-02      # any day inside the tape
"""
import argparse
import datetime as dt
import io
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')

import optimus9.orchestration.build_ws_lines as BWL  # noqa: E402

VALIDATION_END = dt.datetime(2026, 9, 8, 0, 0, tzinfo=dt.timezone.utc)
BWL.TAPE_END = VALIDATION_END
BWL.END_MS = int(VALIDATION_END.timestamp() * 1000)

for _m in [k for k in list(sys.modules)
           if k in ('report_coil_exit', 'sweep_v3_signal', 'measure_live_stop',
                    'build_wsf_trades')]:
    del sys.modules[_m]

_e, sys.stderr = sys.stderr, io.StringIO()
import sweep_v3_signal as S  # noqa: E402
sys.stderr = _e

import walk_mom_models as W  # noqa: E402
from optimus9.analysis.jig import ws1mage_rev  # noqa: E402
from optimus9.compute import trade_config as TC  # noqa: E402
from optimus9.compute.leash_walk import rev_lookback_mask, walk  # noqa: E402
from optimus9.compute.momo_seam import seam_mask  # noqa: E402
from optimus9.compute.test_points import flat_run_at  # noqa: E402

# Joe 1001 validated these 9 bars on 09-01 and derived the day's MAE/MFE from them.
VALIDATED_09_01 = ['00:27:35', '02:40:35', '03:38:00', '09:02:15', '14:50:00',
                   '17:59:25', '18:20:00', '22:24:10', '23:18:50']

SHAPE_09_01 = dict(mech=2768, cut=1673, emitted=1095, runs=23)
"""THE WHOLE SHAPE OF THE DAY, ASSERTED — not just the 9 bars.

Added 1001 after the port validation found the test one-sided: *"Loosening the arm by one bar keeps
all 9 and the test still exits 0, while MECH moves 2768 -> 2777 and EMITTED 1095 -> 1104."* It
mutated `arm_wob` 6 -> 5 and the test passed. These four numbers were printed and never checked,
while the commit message cited them AS the acceptance.

A KNOB CHANGE WILL NOW FAIL THIS TEST. That is the intent: these numbers are the validated day, and
moving them means the day has to be re-validated by Joe before they are edited here.
"""

MOMO_SAMPLES = 3     # flat_run_at's sample count, as the validated run used it
MOMO_TOL = 2.0       # flat_run_at's tolerance, r points


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--day', default='2026-09-01')
    a = ap.parse_args()
    d0 = dt.datetime.strptime(a.day, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc)
    ms0 = int(d0.timestamp() * 1000)
    ms1 = ms0 + 86400000

    rig = S.Rig((ms0, ms1))
    ts = np.asarray(rig.ts, np.int64)
    U = (lambda k: dt.datetime.fromtimestamp(int(ts[k]) / 1000, dt.timezone.utc)
         .strftime('%H:%M:%S'))
    k0 = int(np.searchsorted(ts, ms0))
    k1 = min(int(np.searchsorted(ts, ms1)) - 1, rig.n - 1)

    db = _db()
    # SEED BEFORE LOAD. `TC.load` RAISES on a missing version, and `Rig.__init__` seeds v3 only, so
    # a clean DB died here. `seed()` returns 0 when the rows are already present - it never
    # overwrites. Found by the 1001 port validation: "the one finding that stops the recon session
    # dead rather than pointing it the wrong way".
    wrote = TC.seed(db, TC.WALK_V)
    if wrote:
        print('K|wsf_trade_config v%d was absent - seeded %d rows' % (TC.WALK_V, wrote))
    cfg = TC.load(db, TC.WALK_V)
    lad = list(range(int(cfg['walk_ladder_lo']), int(cfg['walk_ladder_hi']) + 1))
    knobs = dict(
        arm_fence=(float(cfg['arm_fence_lo']), float(cfg['arm_fence_hi'])),
        arm_wob=int(cfg['arm_wob']),
        min_tf=int(cfg['walk_min_tf']),
        fall=int(cfg['walk_fall']),
        race=int(cfg['walk_race']),
        frmin=int(cfg['walk_frmin']),
        lb_bars=int(cfg['walk_lb_bars']),
        rev_lookback=int(rig.C['lookback_s']) // 5,
    )
    r1_back = int(float(cfg['walk_rule1_back_min']) * 60 / 5)
    print('K|wsf_trade_config v%d|key %s' % (cfg['_version'], TC.key(cfg)))
    print('K|arm %s fence %.1f/%.1f wob %d bars = %d s|same dr %s'
          % (cfg['arm_line'], knobs['arm_fence'][0], knobs['arm_fence'][1], knobs['arm_wob'],
             knobs['arm_wob'] * 5, cfg['arm_same_dr']))
    print('K|ladder ws%d..ws%d|min_tf ws%d|fall %d|race %d|frmin ws%d|lb %d bars = %d min'
          % (lad[0], lad[-1], knobs['min_tf'], knobs['fall'], knobs['race'], knobs['frmin'],
             knobs['lb_bars'], knobs['lb_bars'] * 5 // 60))
    print('K|rev lookback %d bars = %s s|rule#1 back %d bars = %s min'
          % (knobs['rev_lookback'], rig.C['lookback_s'], r1_back, cfg['walk_rule1_back_min']))
    print('K|tape END_MS %s|day %s|bars %d..%d'
          % (VALIDATION_END.strftime('%Y-%m-%d %H:%M'), a.day, k0, k1))

    mfr = float(rig.C['momo_fence_r'])
    fence = (mfr, 100.0 - mfr)
    mage = np.asarray(rig.lines[str(cfg['arm_line']).replace('Mage', '')]['Mage'], float)
    RL = {t: np.asarray(rig.lines['ws%d' % t]['r'], float) for t in lad}
    SM = {t: seam_mask(rig.ts, t) for t in lad}
    wcfg = W.WS1_CFG
    _mom, _fr = {}, {}

    def mom_at(t, k, d):
        ck = (t, k, d)
        if ck not in _mom:
            _mom[ck] = bool(W.momentum_true(RL[t], rig.BK[t], wcfg, d, k, SM[t], t,
                                            strip_mom_at_fence=fence)[0])
        return _mom[ck]

    def fr_at(t, k, d):
        ck = (t, k, d)
        if ck not in _fr:
            _fr[ck] = flat_run_at(RL[t], k, d, fence, MOMO_SAMPLES, MOMO_TOL) is not None
        return _fr[ck]

    legs = ws1mage_rev(rig.lines['ws1']['Mage'],
                       rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                       dwell=int(rig.C['dwell']), rev_wob=int(rig.C['rev_wob']),
                       hold=int(rig.C['boundary_xwob']))
    rev = {d: rev_lookback_mask(legs[d]['sig'], legs[d]['sig_conf'], rig.n,
                                knobs['rev_lookback']) for d in (1, -1)}

    mech, states = walk(lad, mage, rig.DR, rig.CC, mom_at, fr_at, rev, k0, k1, **knobs)
    emit = [k for k in mech if rig.gate_open(k, r1_back)]
    print('W|MECH bars %d|rule#1 cut %d|EMITTED %d|momentum_true calls %d|flat_run_at calls %d'
          % (len(mech), len(mech) - len(emit), len(emit), len(_mom), len(_fr)))

    runs = []
    st = None
    for i, k in enumerate(emit):
        if st is None:
            st = k
        if i + 1 == len(emit) or emit[i + 1] != k + 1:
            runs.append((st, k))
            st = None
    print('R|run|WALK FIRES FROM|last emitted bar|bars|dr|arm bar')
    byfirst = {s: None for s, _ in runs}
    for q, (s, e) in enumerate(runs, 1):
        stt = states[s]
        byfirst[s] = stt
        print('R|%d|%s|%s|%d|%+d|%s'
              % (q, U(s), U(e), e - s + 1, stt['arm_dr'], U(stt['arm'])))

    if a.day != '2026-09-01':
        print('V|no validated bar set for %s - nothing asserted' % a.day)
        return 0
    want = []
    for u in VALIDATED_09_01:
        want.append(int(np.searchsorted(ts, int(dt.datetime.strptime(
            '2026-09-01 ' + u, '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc)
            .timestamp() * 1000))))
    fires = {s for s, _ in runs}
    print('V|validated bar|emitted|is it a run FIRST bar|arm bar|arm dr')
    miss = []
    for u, k in zip(VALIDATED_09_01, want):
        ine = k in set(emit)
        isf = k in fires
        stt = byfirst.get(k)
        if not isf:
            miss.append(u)
        print('V|%s|%s|%s|%s|%s'
              % (u, 'YES' if ine else 'NO', 'YES' if isf else 'NO',
                 U(stt['arm']) if stt else '-', ('%+d' % stt['arm_dr']) if stt else '-'))
    extra = sorted(fires - set(want))
    print('M|validated bars %d|reproduced as a run FIRST bar %d|missing %d'
          % (len(want), len(want) - len(miss), len(miss)))
    print('M|run first bars the walk emits that are NOT validated bars|%d%s'
          % (len(extra), ('  ' + ', '.join(U(x) for x in extra)) if extra else ''))
    got = dict(mech=len(mech), cut=len(mech) - len(emit), emitted=len(emit), runs=len(runs))
    shape = [(k, SHAPE_09_01[k], got[k]) for k in ('mech', 'cut', 'emitted', 'runs')
             if SHAPE_09_01[k] != got[k]]
    print('S|the day\'s shape|field|validated|this run|match')
    for k in ('mech', 'cut', 'emitted', 'runs'):
        print('S|%s|%d|%d|%s' % (k, SHAPE_09_01[k], got[k],
                                 'YES' if SHAPE_09_01[k] == got[k] else 'NO'))
    if miss or shape:
        if miss:
            print('M|FAIL|missing %s' % ', '.join(miss))
        for k, exp, g in shape:
            print('M|FAIL|%s moved: validated %d, this run %d' % (k, exp, g))
        return 1
    print('M|PASS|all %d validated bars reproduced, and the day\'s shape is unchanged' % len(want))
    return 0


def _db():
    from optimus9.config import get_db_config
    from optimus9.db.database_manager import DatabaseManager
    d = DatabaseManager(**get_db_config())
    d.connect()
    return d


if __name__ == '__main__':
    sys.exit(main())
