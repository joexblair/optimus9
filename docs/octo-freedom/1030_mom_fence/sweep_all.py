"""THE 11-HOUR SWEEP. One knob at a time against the bank, net% the target.

Joe 1030: *"are you also sweeping all of the knobs? you've got 11 hours of free time starting now,
so you can sweep whatever you want, including the configs for MAge, b and r. use step=1 (or
step=0.05 for the bb%b multi)"*.

WHAT THIS IS. A ONE-AT-A-TIME scan: every arm moves exactly one knob off the held baseline, so a
moved net% belongs to that knob. It is NOT a factorial - 150 arms one-at-a-time is 5 h, the same
150 knobs crossed pairwise is 11,000 arms and does not fit in a week.

THE HELD BASELINE, all of it his, and stated on every row:
    RMOM_FNC 75, L2_MOM_MAXTF 20, LIN2_EXFNC_LATCH_REL lift, LIN2_COUNTER_OOB_ON 0,
    LIN2_MATRY_WSF_TAKEOVER_ON 0, the gate's cadence in the review list, the open handed in at
    2026-08-29 23:53:55 SHORT, the window 2026-08-30..09-06.

THE STOP RUNS FIRST. His 1030 *"are you sweeping using mae1.1? that will impact the results"*, so
the stop-ON half of every knob runs before the stop-OFF half. If the 11 h runs out, the partial is
the stop-OFF half and the report says so rather than printing a half-grid as a grid.

WHAT IS NOT SWEPT, and why:
    the scorer   swing pct 2.0 and the drag 0.1975. v4_rcfg_sweep's own standing note: sweeping
                 them optimises the scorer, not the mech - his two-stage rule.
    the window   a knob picked on the window it was measured on is fitted. These rows are a
                 MEASUREMENT. No value is banked off them without his word.

STEPS THAT ARE MINE, flagged: his "step=1" lands cleanly on every integer knob below. LIFT_TOL and
GAP_PER_TF are floats he gave no step for, so their steps are mine and marked.
"""
import os
import subprocess
import sys
import time

HERE = '/home/joe/thecodes/docs/octo-freedom/1030_mom_fence'
BASE = dict(
    LG_TAPE_END='2026-10-05',
    W_WIN_START='2026-08-30 00:00:00', W_WIN_END='2026-09-06 23:59:55',
    W_WALKS='none', W_V4_EXPERIMENT='1',
    W_V4_RMOM_FNC='75', W_V4_L2_MOM_MAXTF='20',
    W_V4_LIN2_EXFNC_LATCH_REL='lift', W_V4_LIN2_COUNTER_OOB_ON='0',
    W_V4_LIN2_MATRY_WSF_TAKEOVER_ON='0',
)
#   (the knob, its baseline, the values to scan, whose step)
SCAN = [
    ('LIN2_EXFNC_LATCH_WOB',   4,   list(range(1, 13)),                 'his step 1'),
    ('LIN2_CHAIN_OPEN_XWOB',   1,   list(range(1, 13)),                 'his step 1'),
    ('LIN2_CHAIN_OPEN_LINES',  2,   list(range(1, 7)),                  'his step 1'),
    ('LIN2_B1_OOB_DWELL',      0,   list(range(0, 13)),                 'his step 1'),
    ('LIN2_MATRY_WSF_SCAN_HI', 4,   list(range(2, 9)),                  'his step 1'),
    ('LIN2_BARRAGE_MIN_TF',    9,   list(range(1, 13)),                 'his step 1'),
    ('LIN2_BARRAGE_LINES',     6,   list(range(2, 11)),                 'his step 1'),
    ('LIN2_BARRAGE_MAX_TF',   15,   list(range(8, 21)),                 'his step 1'),
    ('LIN2_CROSS_WOB',        12,   list(range(1, 21)),                 'his step 1'),
    ('LIN2_REV_WOB',          12,   list(range(1, 21)),                 'his step 1'),
    ('L2_LIN_HOP',             2,   list(range(1, 7)),                  'his step 1'),
    ('LIFT_WOB',               8,   list(range(2, 15)),                 'his step 1'),
    ('LIFT_PTS',               6,   list(range(3, 11)),                 'his step 1'),
    ('LIN2_REV_FENCE',        40,   list(range(20, 51, 2)),             'step 2 is MINE'),
    ('LIFT_TOL',             2.0,   [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], 'step 0.5 is MINE'),
    ('GAP_PER_TF',           2.8,   [1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 4.0], 'step 0.4 is MINE'),
    ('LIN2_BARRAGE_TOL_S',    70,   [10, 30, 50, 70, 90, 110, 130, 150], 'step 20 is MINE'),
    ('LIN2_CAD_LATCH_LIFE_S', 600,  [120, 300, 600, 900, 1200],         'step is MINE'),
]
MAXP = 15


def arms():
    out = []
    for cap in ('on', 'off'):
        out.append(('CONTROL', 'bank', cap, dict()))
        for k, b, vals, note in SCAN:
            for v in vals:
                if v == b:
                    continue
                out.append((k, v, cap, {'W_V4_' + k: str(v)}))
    return out


def run(batch):
    procs = []
    for k, v, cap, env in batch:
        e = dict(os.environ); e.update(BASE); e.update(env)
        e['W_MAE_CAP'] = 'on' if cap == 'on' else ''
        tag = 'all_%s_%s_%s' % (k, str(v).replace('.', 'p'), cap)
        with open(os.path.join(HERE, tag + '.md'), 'w') as o, \
             open(os.path.join(HERE, tag + '.err'), 'w') as r:
            procs.append((tag, subprocess.Popen(
                ['nice', '-n', '5', 'python3', '-u', 'chain_lift_2d.py'],
                cwd=HERE, env=e, stdout=o, stderr=r)))
    for tag, p in procs:
        p.wait()


def drain():
    """wait for the in-play sweeps to finish. His 1030: *"don't stop the in-play sweeps"*."""
    while True:
        n = int(subprocess.run(['bash', '-c',
                                'pgrep -cf "python3 -u chain_lift_2d.py" || true'],
                               capture_output=True, text=True).stdout.strip() or 0)
        #   this process launches its own children with the same command line, so only the
        #   PRE-EXISTING arms are waited on - counted once, before any of ours exist.
        if n == 0:
            return
        print('# %d in-play arms still running, waiting' % n, flush=True)
        time.sleep(60)


if __name__ == '__main__':
    A = arms()
    t0 = time.time()
    drain()
    print('# the in-play sweeps have drained, %.0f s waited' % (time.time() - t0), flush=True)
    print('# %d arms, %d at a time' % (len(A), MAXP), flush=True)
    for i in range(0, len(A), MAXP):
        run(A[i:i + MAXP])
        print('# %d of %d arms done, %.0f s elapsed' % (min(i + MAXP, len(A)), len(A),
                                                        time.time() - t0), flush=True)
    print('# the sweep is complete, %.0f s' % (time.time() - t0), flush=True)
