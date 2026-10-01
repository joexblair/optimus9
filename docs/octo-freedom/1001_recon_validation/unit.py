"""Run the 12 checks against ONE mutation, in a fresh process. -> one JSON line.

    python3 unit.py BASE
    python3 unit.py A1
"""
import importlib.util
import io
import json
import os
import sys

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import logging  # noqa: E402
logging.disable(logging.CRITICAL)
import muts  # noqa: E402

mid = sys.argv[1]
ids = [] if mid == 'BASE' else [mid]
arm, lw = muts.build(ids)
muts.install(arm, lw)

CHECKS = [('test_arm_state', 'test_p1_warmup_is_bounded', 'P1'),
          ('test_arm_state', 'test_p2_arm_is_the_first_bar_the_run_reaches_wob', 'P2'),
          ('test_arm_state', 'test_p3_mid_cross_cancels_from_either_direction', 'P3'),
          ('test_arm_state', 'test_p4_dr_change_restarts_the_run', 'P4'),
          ('test_arm_state', 'test_p5_dr_zero_cannot_arm', 'P5'),
          ('test_arm_state', 'test_episodes_match_the_live_array', 'EP'),
          ('test_arm_state', 'test_step_refuses_non_consecutive_bars', 'AC'),
          ('test_leash_walk', 'test_q1_qualify_counter_matches_the_sorted_form', 'Q1'),
          ('test_leash_walk', 'test_q2_rev_mask_matches_knowable', 'Q2'),
          ('test_leash_walk', 'test_q3_no_state_crosses_an_arm', 'Q3'),
          ('test_leash_walk', 'test_q4_race_lookback_is_trailing_and_inclusive', 'Q4'),
          ('test_leash_walk', 'test_step_refuses_non_consecutive_bars', 'LC')]

mods = {}
for f in ('test_arm_state', 'test_leash_walk'):
    sp = importlib.util.spec_from_file_location(f, '/home/joe/thecodes/tests/%s.py' % f)
    m = importlib.util.module_from_spec(sp)
    _o, sys.stdout = sys.stdout, io.StringIO()
    sp.loader.exec_module(m)
    sys.stdout = _o
    mods[f] = m

res = {}
for f, fn, tag in CHECKS:
    try:
        getattr(mods[f], fn)()
        res[tag] = 'pass'
    except AssertionError as e:
        res[tag] = 'FAIL: ' + str(e)[:110]
    except Exception as e:  # noqa: BLE001
        res[tag] = 'ERROR %s: %s' % (type(e).__name__, str(e)[:100])
print(json.dumps({'id': mid, 'res': res}))
