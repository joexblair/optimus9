"""Direct cached-line read. No `import machine`.

WHY. A straight data question cost 44.13 s, of which `import machine` was 44.03 s: it builds every
producer, the ws1-ws30 mom-true masks and the 1,000,547-bar stall gate before a line can be read.
None of that is needed to read a cached line.

THE KEY IS THE SPEC, NOT THE NAME. 13 different `ws5r` arrays exist in the live generation (a
k-length sweep). Resolving by name alone returned the wrong one - 10.24 against the ruled 12.48 at
2026-09-03 00:35:00. The spec comes from the DB mech_lines('wsf') ruling, exactly as _baton_pre.py
line 71 does it, and the tape npz supplies ts so K/U are the tape's own, not arithmetic.

usage: ln.py <'YYYY-MM-DD HH:MM:SS'> <'YYYY-MM-DD HH:MM:SS'> ws7r [ws7Mage ...]
"""
import os, sys, io, datetime as dt
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
#   THE SWALLOW COVERS THE NOISY IMPORTS ONLY, and `finally` restores stderr whatever
#   happens. Without it a refusal from v4_knobs.check() - an off-ruled run with no
#   W_V4_EXPERIMENT=1 - goes into the StringIO and the process exits 1 with NOTHING on
#   either stream. That cost a diagnosis on 1101.
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    from optimus9.compute.line_config import override, mech_lines
    from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
    from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.config import get_db_config
finally:
    sys.stderr = _e

EM = int(dt.datetime.strptime(os.environ.get('LG_TAPE_END', '2026-10-05'), '%Y-%m-%d')
         .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
_db = DatabaseManager(**get_db_config()); _db.connect()
SPEC = {}
for g in mech_lines(_db, 'wsf'):
    if g['role'] not in SPEC:
        _t, s_, m_ = g['override']; SPEC[g['role']] = (s_, m_)
_sy = _db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1',
                  fetch=True)[0]
_db.disconnect()
ts = np.load(os.path.join(TAPE_DIR, _tape_key(EM, HOURS, WARMUP,
             {'src': _sy['s'], 'len': _sy['l']}) + '.npz'))['__ts__']
N = len(ts)

#   HIS 1121: *"contain the r config update to 8792 only.  you'll need a separate cache"*. None = ws{TF}r off the shared
#   line cache at the DB row, as always. A directory = ws{TF}r read from that separate cache instead, set by the one
#   process that asked for it (docs/fdm3/fdm3_r_cache.use). Every other role reads what it read.
R_DIR = None
#   HIS 1124 fdm3-htf-oracle, his answer "A separate cache": the lines that page needs and no cache holds - ws40..ws44,
#   ws55..ws59, ws85..ws89, ws115..ws119, ws235..ws240, and r / e for ws45, ws60, ws90, ws120 - are read from that
#   page's own directory (docs/fdm3/fdm3_htf_lines.use). None = not this process. A name it holds is read from it
#   first; every other name resolves as before, so a line no cache holds still refuses.
X_DIR = None


def line(name):
    """ws7r -> the array. tf from the digits, role from the tail."""
    if X_DIR is not None and os.path.exists(os.path.join(X_DIR, name + '.npy')):
        return np.asarray(np.load(os.path.join(X_DIR, name + '.npy'), mmap_mode='r'), float)[:N]
    i = 2
    while name[i].isdigit(): i += 1
    tf, role = int(name[2:i]), name[i:]
    if role == 'r' and R_DIR is not None:
        return np.asarray(np.load(os.path.join(R_DIR, 'ws%dr.npy' % tf), mmap_mode='r'), float)[:N]
    a = np.asarray(np.load(os.path.join(LINE_DIR,
        _line_key(EM, HOURS, WARMUP, override(tf * 60, *SPEC[role])) + '.npy'), mmap_mode='r'), float)
    return a[:N]

K = lambda s: int(np.searchsorted(ts, int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                  .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)))
U = lambda k: dt.datetime.fromtimestamp(int(ts[k]) / 1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    A, B, names = K(sys.argv[1]), K(sys.argv[2]), sys.argv[3:]
    cols = [(n, line(n)) for n in names]
    print('| time | ' + ' | '.join(names) + ' |')
    print('|' + '---|' * (len(names) + 1))
    for i in range(A, B + 1):
        print('| %s | %s |' % (U(i)[11:], ' | '.join('%.2f' % c[i] for _, c in cols)))
