"""regress_trade_walk — the 1002 `TradeBook` refactor reproduces the pre-1002 `trade_walk.walk` exactly.

The OLD walk is read from git (`git show <rev>:optimus9/compute/trade_walk.py`), not from a copy, so the
check cannot drift. Random dr / px / opens / windows / caps; every output compared with `==`.

    python3 regress_trade_walk.py [rev]        # rev defaults to 08190c7, the last commit before it
"""
import subprocess
import sys
import types

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import trade_walk as NEW  # noqa: E402

rev = sys.argv[1] if len(sys.argv) > 1 else '08190c7'
src = subprocess.check_output(['git', '-C', '/home/joe/thecodes', 'show',
                               '%s:optimus9/compute/trade_walk.py' % rev]).decode()
OLD = types.ModuleType('trade_walk_old')
exec(compile(src, 'trade_walk_old', 'exec'), OLD.__dict__)

rng = np.random.default_rng(1002)
trials, trades_seen, kinds = 0, 0, {}
for t in range(5000):
    n = int(rng.integers(50, 3000))
    # a latch-shaped dr: 0 before the first latch, then strictly alternating +1 / -1 stretches
    dr = np.zeros(n, np.int8)
    k = int(rng.integers(0, 40)); cur = int(rng.choice([1, -1]))
    while k < n:
        L = int(rng.integers(1, 200)); dr[k:k + L] = cur; cur = -cur; k += L
    if rng.random() < 0.2:                       # sometimes a non-latch series, zeros inside
        dr = rng.choice(np.array([-1, 0, 1], np.int8), n)
    px = 100.0 * np.exp(np.cumsum(rng.normal(0, 0.002, n)))
    opens = np.flatnonzero(rng.random(n) < rng.uniform(0.001, 0.05))
    a = int(rng.integers(0, max(1, n // 3))); b = int(rng.integers(a, n))
    cap = None if rng.random() < 0.15 else float(rng.choice([0.05, 0.3, 0.7, 1.25, 4.0]))
    o = OLD.walk(opens, dr, px, a, b, cap)
    nw = NEW.walk(opens, dr, px, a, b, cap)
    assert o == nw, 'MISMATCH trial %d: n=%d start=%d end=%d cap=%r' % (t, n, a, b, cap)
    trials += 1; trades_seen += len(o[0])
    for tr in o[0]:
        kinds[tr['closed_by']] = kinds.get(tr['closed_by'], 0) + 1
print('trials %d | trades compared %d | closed_by %s | mismatches 0 | old rev %s'
      % (trials, trades_seen, kinds, rev))
