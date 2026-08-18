"""verify_momo_refactor — prove the 0818 momo refactor changed no verdict.

Joe 0818 asked for the two checks in docs/handover_momo_refactor.md to be runnable. They were run
once from a throwaway script and the numbers were written down; that is not a check anyone can
repeat. This is the same two checks, committed.

  check 1  momo() and momo_g(), old code against new, at the default 60-minute window
  check 2  momo_g() inside momo_window(K_WINDOW x TF) at 21 fixed sample points
  check 3  v_ws_fin_walk hashed with a stated recipe, against the pre-refactor hash

WHERE THE OLD CODE COMES FROM. Not a frozen copy in the repo - a second copy of a formula is the
thing momo_core.py exists to avoid. It is read out of git at BASE_COMMIT, the last commit before
the refactor, and executed into a throwaway module. The old momo_gated is then pointed at the old
momo_core by hand, because its own import line would otherwise pick up the refactored one.

  python3 verify_momo_refactor.py
"""
import hashlib
import subprocess
import sys
import types

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute import momo_core as NEW_CORE
from optimus9.compute import momo_gated as NEW_GATED

BASE_COMMIT = '5a9c604'          # the commit before the refactor
LINES = ('wlb_ws1r', 'wlb_ws2r', 'wlb_ws10r')   # three r lines off the 08-04 tape
DIRS = (1, -1)                   # read upward, read downward
STEP_1 = 7                       # every 7th bar of the 17,281 in the window
STEP_2 = 23                      # every 23rd bar
TFS_2 = (13, 21, 27)             # the timeframes check 2 walks
FIXED_SAMPLES_2 = 21             # what build_ws_fin.py sets
K_WINDOW = 4                     # momentum window = 4 x the timeframe, in minutes

# v_ws_fin_walk as it stood before the refactor. THE RECIPE, so this is reproducible:
#   SELECT * FROM v_ws_fin_walk          (the view carries its own ORDER BY wfw_row)
#   every column of every row cast to str, columns joined with '|', rows joined with '\n'
#   sha256 of those bytes, utf-8
VIEW_ROWS = 121
VIEW_SHA256 = '98c5db7dd5d3356e2d072b06a75a0d875704168bfa6de3f1224d2f16881b2966'


def _old(path, name):
    """The file as it was at BASE_COMMIT, executed into a throwaway module."""
    src = subprocess.run(['git', 'show', f'{BASE_COMMIT}:{path}'],
                         capture_output=True, text=True, check=True).stdout
    m = types.ModuleType(name)
    exec(compile(src, f'{BASE_COMMIT}:{path}', 'exec'), m.__dict__)
    return m


def _same(a, b):
    """Two 4-tuples, treating not-a-number as equal to not-a-number."""
    if a[0] != b[0]:
        return False
    for x, y in zip(a[1:], b[1:]):
        if isinstance(x, float) and np.isnan(x) and isinstance(y, float) and np.isnan(y):
            continue
        if x != y:
            return False
    return True


def series(db):
    rows = db.execute(f'SELECT {",".join(LINES)} FROM ws_line_bar ORDER BY wlb_ms', fetch=True)
    return {c: np.array([float(r[c]) for r in rows]) for c in LINES}


def check_1(old_core, old_gated, data):
    n = bad = 0
    for name, r in data.items():
        for dr in DIRS:
            for w in range(0, len(r), STEP_1):
                for o, nw in ((old_core.momo(r, dr, w), NEW_CORE.momo(r, dr, w)),
                              (old_gated.momo_g(r, dr, w), NEW_GATED.momo_g(r, dr, w))):
                    n += 1
                    if not _same(o, nw):
                        bad += 1
                        print(f'  DIFF {name} dir {dr} bar {w}: was {o} now {nw}')
    return n, bad


def check_2(old_gated, data):
    old_gated.MOMO_FIXED_SAMPLES = FIXED_SAMPLES_2
    NEW_GATED.MOMO_FIXED_SAMPLES = FIXED_SAMPLES_2
    n = bad = 0
    try:
        for tf in TFS_2:
            for name, r in data.items():
                for dr in DIRS:
                    with old_gated.momo_window(K_WINDOW * tf):
                        o = [old_gated.momo_g(r, dr, w) for w in range(0, len(r), STEP_2)]
                    with NEW_GATED.momo_window(K_WINDOW * tf):
                        nw = [NEW_GATED.momo_g(r, dr, w) for w in range(0, len(r), STEP_2)]
                    for a, b in zip(o, nw):
                        n += 1
                        if not _same(a, b):
                            bad += 1
                            print(f'  DIFF tf {tf} {name} dir {dr}: was {a} now {b}')
    finally:
        NEW_GATED.MOMO_FIXED_SAMPLES = 0
    return n, bad


def check_3(db):
    rows = db.execute('SELECT * FROM v_ws_fin_walk', fetch=True)
    cols = list(rows[0].keys())
    blob = '\n'.join('|'.join(str(r[c]) for c in cols) for r in rows)
    return len(rows), hashlib.sha256(blob.encode('utf-8')).hexdigest()


def main():
    old_core = _old('optimus9/compute/momo_core.py', 'old_momo_core')
    old_gated = _old('optimus9/compute/momo_gated.py', 'old_momo_gated')
    old_gated.X = old_core        # bind the OLD core; its import line would fetch the new one

    db = DatabaseManager(**get_db_config()); db.connect()
    data = series(db)
    print(f'old code from git {BASE_COMMIT}   bars per line {len(next(iter(data.values()))):,}')

    n1, b1 = check_1(old_core, old_gated, data)
    print(f'check 1  default 60-minute window          {n1:>7,} calls  {b1} mismatches')

    n2, b2 = check_2(old_gated, data)
    print(f'check 2  momo_window, {FIXED_SAMPLES_2} fixed points        {n2:>7,} calls  {b2} mismatches')

    rows, sha = check_3(db)
    ok3 = rows == VIEW_ROWS and sha == VIEW_SHA256
    print(f'check 3  v_ws_fin_walk                     {rows:>7,} rows   {"MATCH" if ok3 else "DIFFERS"}')
    print(f'         sha256 {sha}')
    if not ok3:
        print(f'         expected {VIEW_SHA256}, {VIEW_ROWS} rows')
    db.disconnect()
    return 0 if (b1 == 0 and b2 == 0 and ok3) else 1


if __name__ == '__main__':
    sys.exit(main())
