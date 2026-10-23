"""STEP 3: the mech knobs, ONE AXIS AT A TIME off the banked centre, in-sample only.

Joe 1022 agreed the split: SWEEP 2026-07-02 to 2026-08-31, HOLD OUT 2026-09-01 to 2026-10-04. The
8 days read by eye all session sit inside the HOLD-OUT on purpose.

ONE AXIS AT A TIME, not a cross. 18 arms instead of 2,916, and every row is readable against the
centre. The axes that move the result are the only ones worth crossing, and that is the night run.

THE TWO TRAJ AXES ARE NOT HERE. `TRAJ_MIN_FRAC` and `TRAJ_MIN_TRAVEL` touch only the confluence
read, not the signals, so they are inert against a trade list and are swept separately.

THE SCORER IS HELD: swing pct 2.0, the pseudo stop 1.1. Sweeping it would optimise the scorer.

Each arm is a SUBPROCESS carrying W_V4_* env, so v4_knobs' refusal is exercised for real: an
off-bank arm must declare W_V4_EXPERIMENT=1 or the import raises.

usage: v4_mech_sweep.py <out.md>
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
IS_A, IS_B = '2026-07-02 12:00:00', '2026-08-31 23:59:55'

AXES = [
    ('LIN_IB_DWELL',    2.5,  (1.5, 2.0, 2.5, 3.0, 4.0)),
    ('TF_CEILING',      10,   (8, 10, 12)),
    ('BSTOP_SYNC_MIN',  8.8,  (4.4, 8.8, 13.2)),
    ('LIFT_WOB',        8,    (4, 6, 8, 12)),
    ('GAP_PER_TF',      2.8,  (1.5, 2.8, 4.0)),
]


def arms():
    seen = set()
    out = [(None, None, 'BANKED')]
    for name, centre, vals in AXES:
        for v in vals:
            if v == centre:
                continue
            key = (name, v)
            if key in seen:
                continue
            seen.add(key)
            out.append((name, v, '%s %s' % (name, v)))
    return out


if __name__ == '__main__':
    out = open(sys.argv[1], 'w', buffering=1)

    def log(s):
        out.write(s + '\n'); print(s, flush=True)

    A = arms()
    log('# the mech sweep, one axis at a time. %d arms.' % len(A))
    log('# IN-SAMPLE %s .. %s. the hold-out 2026-09-01 .. 2026-10-04 is NOT touched.' % (IS_A, IS_B))
    log('# HELD: swing pct 2.0, the pseudo stop 1.1, TRAJ_WIDTH 21, the Mage spec.')
    log('')
    log('| the arm | fires | EXHAUST | trades | positives | MFE mean %% | MAE mean %% | MFE over MAE | the positives MFE mean %% |')
    log('|---|---|---|---|---|---|---|---|---|')
    t0 = time.time()
    for i, (name, v, label) in enumerate(A, 1):
        env = dict(os.environ)
        if name is not None:
            env['W_V4_' + name] = str(v)
            env['W_V4_EXPERIMENT'] = '1'
        r = subprocess.run([sys.executable, os.path.join(HERE, 'v4_arm.py'), IS_A, IS_B, label],
                           env=env, capture_output=True, text=True)
        row = [l for l in r.stdout.splitlines() if l.startswith('|')]
        if row:
            log(row[-1])
        else:
            log('| %s | FAILED | %s | - | - | - | - | - | - |'
                % (label, (r.stderr.strip().splitlines() or ['?'])[-1][:90]))
        print('# arm %d of %d, %.0f s elapsed' % (i, len(A), time.time() - t0), flush=True)
    log('# the sweep took %.0f s' % (time.time() - t0))
    out.close()
