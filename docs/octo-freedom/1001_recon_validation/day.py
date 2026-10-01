"""Run the acceptance test's walk on 09-01 once per mutation, tape loaded ONCE.

Mirrors report_leash_walk.main() line for line for the inputs; only the two mech modules are
swapped. -> one JSON line per mutation in day_results.jsonl.

    python3 day.py BASE P_ltmax+P_drcons+P_midrun A1 A3 ...
"""
import datetime as dt
import io
import json
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import optimus9.orchestration.build_ws_lines as BWL  # noqa: E402

VALIDATION_END = dt.datetime(2026, 9, 8, 0, 0, tzinfo=dt.timezone.utc)
BWL.TAPE_END = VALIDATION_END
BWL.END_MS = int(VALIDATION_END.timestamp() * 1000)
for _m in [k for k in list(sys.modules)
           if k in ('report_coil_exit', 'sweep_v3_signal', 'measure_live_stop', 'build_wsf_trades')]:
    del sys.modules[_m]
_e, sys.stderr = sys.stderr, io.StringIO()
import sweep_v3_signal as S  # noqa: E402
sys.stderr = _e
import walk_mom_models as W  # noqa: E402
from optimus9.analysis.jig import ws1mage_rev  # noqa: E402
from optimus9.compute import trade_config as TC  # noqa: E402
from optimus9.compute.momo_seam import seam_mask  # noqa: E402
from optimus9.compute.test_points import flat_run_at  # noqa: E402
import muts  # noqa: E402

VALIDATED_09_01 = ['00:27:35', '02:40:35', '03:38:00', '09:02:15', '14:50:00',
                   '17:59:25', '18:20:00', '22:24:10', '23:18:50']
EXTRA_14 = ['05:44:10', '07:00:40', '08:09:15', '08:12:45', '11:30:20', '11:34:15', '11:37:00',
            '13:05:25', '13:54:20', '15:13:00', '16:16:10', '16:21:20', '18:11:35', '23:27:20']
SHAPE = dict(mech=2768, cut=1673, emitted=1095, runs=23)
MOMO_SAMPLES, MOMO_TOL = 3, 2.0

ms0 = int(dt.datetime(2026, 9, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
ms1 = ms0 + 86400000
rig = S.Rig((ms0, ms1))
ts = np.asarray(rig.ts, np.int64)
U = (lambda k: dt.datetime.fromtimestamp(int(ts[k]) / 1000, dt.timezone.utc).strftime('%H:%M:%S'))
k0 = int(np.searchsorted(ts, ms0))
k1 = min(int(np.searchsorted(ts, ms1)) - 1, rig.n - 1)

from optimus9.config import get_db_config  # noqa: E402
from optimus9.db.database_manager import DatabaseManager  # noqa: E402
db = DatabaseManager(**get_db_config()); db.connect()
cfg = TC.load(db, TC.WALK_V)
db.disconnect()
lad = list(range(int(cfg['walk_ladder_lo']), int(cfg['walk_ladder_hi']) + 1))
KNOBS = dict(arm_fence=(float(cfg['arm_fence_lo']), float(cfg['arm_fence_hi'])),
             arm_wob=int(cfg['arm_wob']), min_tf=int(cfg['walk_min_tf']),
             fall=int(cfg['walk_fall']), race=int(cfg['walk_race']),
             frmin=int(cfg['walk_frmin']), lb_bars=int(cfg['walk_lb_bars']),
             rev_lookback=int(rig.C['lookback_s']) // 5)
r1_back = int(float(cfg['walk_rule1_back_min']) * 60 / 5)

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
want = [int(np.searchsorted(ts, int(dt.datetime.strptime('2026-09-01 ' + u, '%Y-%m-%d %H:%M:%S')
                                    .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)))
        for u in VALIDATED_09_01]


def one(tag, ids, knob_over=None):
    probe = {'ltmax': 0, 'drcons': 0, 'midrun_nonzero': 0, 'midrun_changes_outcome': 0,
             'midcross': 0}
    arm_src, lw_src = muts.build(ids)
    am, lw = muts.install(arm_src, lw_src, probe)
    kn = dict(KNOBS)
    if knob_over:
        kn.update(knob_over)
    rev = {d: lw.rev_lookback_mask(legs[d]['sig'], legs[d]['sig_conf'], rig.n, kn['rev_lookback'])
           for d in (1, -1)}
    mech, states = lw.walk(lad, mage, rig.DR, rig.CC, mom_at, fr_at, rev, k0, k1, **kn)
    emit = [k for k in mech if rig.gate_open(k, r1_back)]
    runs, st = [], None
    for i, k in enumerate(emit):
        if st is None:
            st = k
        if i + 1 == len(emit) or emit[i + 1] != k + 1:
            runs.append((st, k)); st = None
    fires = {s for s, _ in runs}
    miss = [u for u, k in zip(VALIDATED_09_01, want) if k not in fires]
    extra = sorted(U(x) for x in fires - set(want))
    got = dict(mech=len(mech), cut=len(mech) - len(emit), emitted=len(emit), runs=len(runs))
    moved = {k: [SHAPE[k], got[k]] for k in SHAPE if SHAPE[k] != got[k]}
    # the episodes on the day, from the (possibly mutated) arm module
    live, arm, adr = am.run(mage, rig.DR, k0, k1, kn['arm_fence'], kn['arm_wob'])
    eps = am.episodes(live, arm, adr, k0, k1)
    out = dict(tag=tag, ids=ids, knob_over=knob_over, shape=got, moved=moved, missing=miss,
               extra_changed=(extra != EXTRA_14), extra=extra,
               runs=[[U(s), U(e), e - s + 1] for s, e in runs],
               accept='PASS' if not miss and not moved else 'FAIL',
               episodes=len(eps), probe=probe, bars=k1 - k0 + 1)
    print(json.dumps(out), flush=True)
    return out


if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'day_results.jsonl'), 'a') as fh:
        for a in sys.argv[1:]:
            if a.startswith('LB='):
                v = int(a[3:])
                r = one(a, [], dict(lb_bars=v))
            else:
                ids = [] if a == 'BASE' else a.split('+')
                r = one(a, ids)
            fh.write(json.dumps(r) + '\n'); fh.flush()
