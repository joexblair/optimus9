"""Does the rider EARN the baton, or does it appear? Joe 1005.

Joe: "the rider tag must be earnt though the lineage of baton passes. they don't have to be
strictly sequential, hopping one or two TFs is accepted".

THE PRODUCER AS BUILT, baton.py:120-131, no lineage anywhere in it:
    avail = lambda j: [t for t in TFS if MT[t][j] and not ST[t][j]]
    if rider is None:
        c = avail(j); rider = max(c)
Successor = the HIGHEST available TF. The outgoing rider's TF is never consulted, so a pass can
jump any distance, in either direction, and the chain can never break.

This script re-walks 09-25 on the same masks and measures, at the EXACT SEAT BAR (the pass bar + 1,
not the pass bar the report's `candidates` column shows), whether a successor within +-W TFs of the
outgoing rider existed.
"""
import os as _os
import datetime as dt, io, os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.line_config import override, mech_lines
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window, momo_g_why
from optimus9.analysis.jig import stall_mask
from optimus9.compute import momo_core as MC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e
STALL_N = 6; TFS = list(range(3, 24))
# TAPE END, exclusive. Override with LG_TAPE_END=YYYY-MM-DD when the window needs a later tape:
# a day AFTER this date is NOT in the cache, and K() would searchsorted past the end of ts and
# index the last bar instead of failing. 2026-10-04 covers 09-25..10-03. For 10-04 use 2026-10-05
# (build it first: build_tape.py 2026-10-05).
EM = int(dt.datetime.strptime(_os.environ.get('LG_TAPE_END', '2026-10-04'), '%Y-%m-%d')
        .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
db = DatabaseManager(**get_db_config()); db.connect()
spec = {}
for g in mech_lines(db, 'wsf'):
    if g['role'] not in spec: _t, s_, m_ = g['override']; spec[g['role']] = (s_, m_)
sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
BANK = {t: momo_bank(db, t) for t in TFS}
db.disconnect()
tp = np.load(os.path.join(TAPE_DIR, _tape_key(EM, HOURS, WARMUP, {'src': sy['s'], 'len': sy['l']}) + '.npz'))
ts = tp['__ts__']
LD = lambda tfs, role: np.asarray(np.load(os.path.join(LINE_DIR, _line_key(EM, HOURS, WARMUP, override(tfs, *spec[role])) + '.npy'), mmap_mode='r'), float)
R = {t: LD(t * 60, 'r')[:len(ts)] for t in TFS}
U = lambda k: dt.datetime.fromtimestamp(int(ts[k]) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
K = lambda s: int(np.searchsorted(ts, int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp() * 1000)))
P = K('2026-09-25 00:00:00'); A = max(0, P - 3 * 3600 // 5); B = K('2026-09-25 23:59:55'); N = B - A + 1
G1, M13 = LD(60, 'Mage'), LD(13 * 60, 'm')
DRv = np.zeros(len(ts), np.int8); cur = 0
for k in range(min(len(ts), len(G1), len(M13))):
    a, b = G1[k], M13[k]
    if a == a and b == b:
        if a >= 85.0 and b >= 85.0: cur = +1
        elif a <= 15.0 and b <= 15.0: cur = -1
    DRv[k] = cur
D = DRv[A:B + 1]
MT, ST = {}, {}
for t in TFS:
    both = {}
    for dd in (-1, +1):
        with momo_config(BANK[t]):
            with momo_window(int(BANK[t]['k_window']) * t):
                step, samples = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
        both[dd] = stall_mask(R[t], dd, STALL_N, step, samples)[A:B + 1]
    ST[t] = np.where(D > 0, both[+1], both[-1])
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            MT[t] = np.array([momo_g_why(R[t], int(D[i]), A + i)[0] in ('momo', 'curl') for i in range(N)])
avail = lambda j: [t for t in TFS if MT[t][j] and not ST[t][j]]

# ---- the chain as built, recording the SEAT bar and the availability there
CH = []; j = 0; rider = None; nn = 0
while j < N:
    if rider is None:
        c = avail(j)
        if not c: j += 1; continue
        rider = max(c); start = j; seat_av = c
    if ST[rider][j] or not MT[rider][j]:
        nn += 1
        CH.append({'n': nn, 'r': rider, 'start': start, 'end': j, 'seat_av': seat_av,
                   'why': 'STALLED' if ST[rider][j] else 'lost mom-true'})
        rider = None; j += 1; continue
    j += 1
if rider is not None:
    CH.append({'n': nn + 1, 'r': rider, 'start': start, 'end': N - 1, 'seat_av': seat_av, 'why': 'still riding'})

print('## LEGALITY AT THE SEAT BAR — availability measured where the successor is actually seated')
print('| hop window W | passes where a successor within +-W existed | chain would END | the taken pass was legal |')
print('|' + '---|' * 4)
pairs = [(CH[i]['r'], CH[i + 1]) for i in range(len(CH) - 1)]
for W in (1, 2, 3):
    legal = sum(1 for out, nx in pairs if any(abs(t - out) <= W for t in nx['seat_av']))
    took = sum(1 for out, nx in pairs if abs(nx['r'] - out) <= W)
    print('| %d | %d | %d | %d of %d |' % (W, legal, len(pairs) - legal, took, len(pairs)))

print()
print('## THE LINEAGE OF THE TWO RIDERS')
def show(tgt, title):
    print()
    print('### %s' % title)
    print('| chain # | outgoing rider | pass bar | why | seat bar | available at the seat bar | successor taken | hop | legal at +-3 | a legal option existed |')
    print('|' + '---|' * 10)
    for i in range(len(CH) - 1):
        if CH[i + 1]['n'] < tgt - 5 or CH[i + 1]['n'] > tgt: continue
        out = CH[i]['r']; nx = CH[i + 1]
        opts = [t for t in nx['seat_av'] if abs(t - out) <= 3]
        h = nx['r'] - out
        print('| %d -> %d | ws%d | %s | %s | %s | %s | ws%d | %+d | %s | %s |'
              % (CH[i]['n'], nx['n'], out, U(A + CH[i]['end']), CH[i]['why'], U(A + nx['start']),
                 ', '.join('ws%d' % t for t in nx['seat_av']) or 'none', nx['r'], h,
                 'YES' if abs(h) <= 3 else '**no**',
                 ', '.join('ws%d' % t for t in opts) if opts else '**none — chain should END**'))
for c in CH:
    if c['start'] <= K('2026-09-25 02:12:10') - A <= c['end']: show(c['n'], '02:12:10 / 02:13:10 ride ws%d' % c['r'])
for c in CH:
    if c['start'] <= K('2026-09-25 02:42:35') - A <= c['end']: show(c['n'], '02:42:35 rides ws%d' % c['r'])
