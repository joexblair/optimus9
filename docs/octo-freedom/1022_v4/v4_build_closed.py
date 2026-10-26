"""Build the CLOSED-mode line arrays v4 reads, into the rpl line cache. Joe 1024.

WHY IT EXISTS. No build script covered the closed variants. v4core's cws set already reads closed
arrays by spec, and both `v4_core_arm._line` and `v4_mode_ab` only RAISE when one is absent, so a
missing closed line had no way to be made. This file is the maker.

THE DB ROW IS NOT TOUCHED, which is the structural choice and the precedent is v4core's own: a
closed line is an OVERRIDE of the same DB spec, not a different row. `_line_key` is built from
(end_ms, hours, warmup, the override tuple) and the name is only the Jig's dict key, so a closed
line lands on its own cache key and the emerging array every other consumer reads is untouched.
Changing `gcws30Mage.value_mode` in the DB would move it for every consumer of that name.

IT BUILDS ONLY WHAT IS MISSING. `cache_jig_perline` skips a line whose key already exists, so a
re-run is a no-op and prints the same table.

    python3 v4_build_closed.py [--rebuild]
"""
import datetime as dt
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.line_config import override
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, _line_key, cache_jig_perline
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e

#   (the name v4 reads it by, the role in ln.SPEC, the timeframe in SECONDS)
#   30 s is sub-wsf on Joe's 1017 band names: wsf = ws1-ws12, sub-wsf = g5-g30, dtf = >ws12.
#   cws1Mage and cws2Mage were already cached - v4core reads them - and are listed so the whole
#   closed Mage ladder is declared in one place. Joe 1024: *"create cws{TF3-10}Mage lines and set
#   them all to mode: closed"*.
#   cws11Mage and cws12Mage added 1026 - Joe: *"create a cache for cws{1-12}Mage (mode:closed) and
#   test them in the reentry mech"*. 12 is L2_MOM_MAXTF, so the closed ladder now reaches the top
#   rung lineage2 declares.
WANTED = ((('gcws30Mage', 'Mage', 30),)
          + tuple(('cws%dMage' % t, 'Mage', t * 60) for t in range(1, 13)))
MODE = 'closed'


def specs():
    """{the name: the override tuple} for every wanted line, in MODE."""
    return {n: override(secs, ln.SPEC[role][0], MODE) for n, role, secs in WANTED}


def main(rebuild=False):
    ovr = specs()
    db = DatabaseManager(**get_db_config()); db.connect()
    row = db.execute('SELECT pxsmooth_dema_src, pxsmooth_dema_len FROM optimus9_system LIMIT 1',
                     fetch=True)
    db.disconnect()
    pxs = ({'src': row[0]['pxsmooth_dema_src'], 'len': row[0]['pxsmooth_dema_len']}
           if row else None)

    print('# v4 CLOSED LINES. tape end %s, hours %d, warmup %d, mode %s'
          % (os.environ['LG_TAPE_END'], HOURS, WARMUP, MODE))
    print('# the DB row is NOT changed - a closed line is an override on its own cache key')
    print('')
    print('| the line | tf | the spec | the cache key | before |')
    print('|---|---|---|---|---|')
    for n in ovr:
        p = os.path.join(LINE_DIR, _line_key(ln.EM, HOURS, WARMUP, ovr[n]) + '.npy')
        print('| %s | %ds | %s | %s | %s |'
              % (n, ovr[n][0], ovr[n][1], os.path.basename(p)[:20],
                 'CACHED' if os.path.exists(p) else 'missing'))

    J = cache_jig_perline(ln.EM, HOURS, WARMUP, ovr, pxs_cfg=pxs, rebuild=rebuild)
    ts = np.asarray(J.ts)
    u = (lambda t: dt.datetime.fromtimestamp(int(t) / 1000, dt.timezone.utc)
         .strftime('%Y-%m-%d %H:%M:%S'))
    print('')
    print('# ts %s -> %s, %d bars' % (u(ts[0]), u(ts[-1]), len(ts)))
    print('')
    print('| the line | finite | min | median | max | first finite |')
    print('|---|---|---|---|---|---|')
    for n in ovr:
        a = np.asarray(J.W.line(n) if hasattr(J, 'W') else J[n], float)
        f = np.isfinite(a)
        fi = int(np.argmax(f)) if f.any() else -1
        print('| %s | %d | %.2f | %.2f | %.2f | %s |'
              % (n, int(f.sum()), np.nanmin(a), np.nanmedian(a), np.nanmax(a),
                 u(ts[fi]) if fi >= 0 else '-'))
    #   THE CHANGE-RATE IS THE PROOF OF MODE. A closed line steps only when its own bar closes, so
    #   at 30 s on the 5 s grid it may change on at most 1 bar in 6 = 16.7%; the emerging array it
    #   shares a DB row with changes far more often. Printed rather than asserted because the
    #   expected rate is arithmetic, not a ruling.
    print('')
    print('| the line | mode | bars that changed | % of bars |')
    print('|---|---|---|---|')
    for n in ovr:
        for m in (MODE, 'emerging'):
            k = _line_key(ln.EM, HOURS, WARMUP, override(ovr[n][0], ovr[n][1], m))
            p = os.path.join(LINE_DIR, k + '.npy')
            if not os.path.exists(p):
                print('| %s | %s | - | not cached |' % (n, m))
                continue
            a = np.asarray(np.load(p, mmap_mode='r'), float)[:ln.N]
            d = int(np.sum(a[1:] != a[:-1]))
            print('| %s | %s | %d | %.1f%% |' % (n, m, d, 100.0 * d / (len(a) - 1)))


if __name__ == '__main__':
    main(rebuild='--rebuild' in sys.argv)
