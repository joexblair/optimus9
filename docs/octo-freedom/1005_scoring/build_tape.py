"""Build the rpl tape + line cache for a given TAPE END date. Parameterised from the one-off
build_1003tape.py / build_1004.py so a new day no longer needs a new script.

    python3 docs/octo-freedom/1005_scoring/build_tape.py 2026-10-05

TAPE END is EXCLUSIVE of the day you want: END 2026-10-05 puts 10-04 inside the tape, which is what
`report_leash_walk.py --day 2026-10-04 --tape-end 2026-10-05` needs.

ADDITIVE ONLY. Every artefact is keyed by md5(end_ms|hours|warmup|spec) — a new END writes NEW keys
and touches no existing one. Verified 1003: o9-live does not read `rpl_cache` (nor BWL,
report_coil_exit or build_wsf_trades), so this cannot disturb the live loop's inputs.

IT IS CPU-HEAVY. Earlier runs: ~26 s for the tape, ~31 s for a 12-line role set; a full ws1..ws23 x
(m, Mage, r, x) + gcws{5,15,30} x (Mage, r) set is 98 lines. Do not run it while o9-live's loop is
already slow — check `ops/o9_healthcheck.py` first.
"""
import datetime as dt, io, os, sys, time
sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.line_config import override, mech_lines
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
from optimus9.orchestration.rpl_cache import cache_jig_perline, LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e

if len(sys.argv) < 2:
    raise SystemExit('usage: build_tape.py YYYY-MM-DD   (the EXCLUSIVE tape end; use the day AFTER '
                     'the last day you want inside it)')
END = dt.datetime.strptime(sys.argv[1], '%Y-%m-%d').replace(tzinfo=dt.timezone.utc)
EM = int(END.timestamp() * 1000)

db = DatabaseManager(**get_db_config()); db.connect()
spec = {}
for g in mech_lines(db, 'wsf'):
    if g['role'] not in spec:
        _t, s_, m_ = g['override']; spec[g['role']] = (s_, m_)
sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1',
                fetch=True)[0]
# refuse to build a tape whose last day is not a complete 5 s grid - a partial day silently
# produces short lines and every index after the gap is wrong
last = EM - 86400000
got = db.execute('SELECT COUNT(*) c FROM kline_collection WHERE kc_timestamp>=%s AND kc_timestamp<%s',
                 (last, EM), fetch=True)[0]['c']
db.disconnect()
day = dt.datetime.fromtimestamp(last / 1000, dt.timezone.utc).date()
print('grid check %s: %d of 17280 five-second bars' % (day, got), flush=True)
if got != 17280:
    raise SystemExit('REFUSING: %s is not a complete day (%d of 17280). Build it when the day closes.'
                     % (day, got))

OVR = {}
for tf in range(1, 24):
    for role in ('m', 'Mage', 'r', 'x'): OVR['ws%d%s' % (tf, role)] = override(tf * 60, *spec[role])
for tfs in (5, 15, 30):
    for role in ('Mage', 'r'): OVR['gcws%d%s' % (tfs, role)] = override(tfs, *spec[role])

tp = os.path.join(TAPE_DIR, _tape_key(EM, HOURS, WARMUP, {'src': sy['s'], 'len': sy['l']}) + '.npz')
have = set(os.listdir(LINE_DIR))
todo = [n for n in OVR if _line_key(EM, HOURS, WARMUP, OVR[n]) + '.npy' not in have]
print('TAPE_END %s | tape key %s (%s) | %d lines wanted | %d to build'
      % (END, os.path.basename(tp), 'present' if os.path.exists(tp) else 'MISSING', len(OVR), len(todo)),
      flush=True)
t0 = time.time()
cache_jig_perline(EM, HOURS, WARMUP, OVR, pxs_cfg={'src': sy['s'], 'len': sy['l']})
missing = [n for n in OVR
           if not os.path.exists(os.path.join(LINE_DIR, _line_key(EM, HOURS, WARMUP, OVR[n]) + '.npy'))]
print('built in %.1f s | tape %s | %d lines still missing%s'
      % (time.time() - t0, 'ok' if os.path.exists(tp) else 'FAILED', len(missing),
         (': ' + ', '.join(missing[:10])) if missing else ''))
