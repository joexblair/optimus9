"""The baton chain, the stalled counts and r's trajectory, every row honouring rig.DR per bar.
argv: START END [OCTOSIG_FILE]

SPLIT 1005 INTO compute() + render(), NO BEHAVIOUR CHANGE. Joe 1005: *"using sanctioned producers
keeps us whole and prevents sweeping misunderstandings"*. The window compute used to run at module
import, so nothing could call it and `octosig_db.py` would have had to re-implement the stall/baton/
traj walk - the divergent copy this project keeps paying for (`walk_mom_models.py:175` records one
that drifted to 75/25 while asserting it was verbatim at 15/85). Now both the report and the DB
builder call `compute()`. Verified byte-identical against
`transfer/2026-09-25_baton_stall_octosig_fullday.txt` before any row was inserted.

JOE 1004, RULING: "the report's rows must honour rig.DR. we are simulating o9-live walks, therefore
we must be completely aligned". So there is NO dr argument any more. Every per-bar test - mom-true,
stalled, trajectory - reads rig.DR AT THAT BAR. The earlier reports ran at a fixed dr +1 and are
superseded, not supplemented.

rig.DR is rebuilt verbatim from sweep_v3_signal.Rig.__init__:99-106 - ws1Mage AND ws13m both >= 85
-> +1, both <= 15 -> -1, otherwise HOLD the last value. Measured: it is never 0 in any walk window
(0 of 153,340 bars over 09-25..10-03), so the no-direction case does not arise here.

THE STALL under a per-bar dr: jig.stall_mask is a whole-array call taking ONE dr, so both frames are
built and selected per bar. That is the same producer, twice - not a fork.

TRAJECTORY is optimus9.compute.rule2_trajectory.trajectory, the built mech from wsf_dtf_v3_spec §22
(Joe 0924). Knobs, all passed: block 60 bars = 5 min (jig.AF_BLOCK, banked as anchor_floater.block
at config v9), min_bars 24 bars = 2 min STRICTLY more (Joe's chat value, not in a config table),
min_travel 0.0 (the producer's default, which its docstring records as deliberately unset - Joe 0924:
"I would say the true threshold is in the OOS data").
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
from optimus9.compute import momo_core as MC
from optimus9.compute.rule2_trajectory import trajectory
from optimus9.analysis.jig import stall_mask, AF_BLOCK
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e
_CFG_DB = DatabaseManager(**get_db_config()); _CFG_DB.connect()
from optimus9.compute.spec_config import spec_config
LG = spec_config(_CFG_DB, 'lazy_g_config')
LG_KEY = LG.key()
STALL_N = int(LG['stall_n'])
TFS = list(range(int(LG['baton_tf_lo']), int(LG['baton_tf_hi']) + 1))
TRAJ_MIN_BARS = int(LG['traj_min_bars'])
TRAJ_MIN_TRAVEL = float(LG['traj_min_travel'])
LIN_TFS = list(range(int(LG['band_lo']), int(LG['band_hi']) + 1))
"""THE LADDER JOE'S LINEAGE WALKS, and the baton's own. Both from `lazy_g_config`.

`baton_tf_lo` is 1, not 3. It was hardcoded `range(3, 24)` and contradicted wsf_dtf_v3_config's own
bands.band_wsf_lo = 1 and v3_report.tf_lo = 1 - nothing read the config, so nothing caught the drift.
Joe 1006: *"we need both ws1 and ws2, and if that moves any column data then it's the price of
correctness"*. Measured on 09-25: baton passes 128 -> 138, 16 of 138 ridden by ws1/ws2, and the rider
at every one of the 39 octo-sig rows is UNCHANGED - `rider = max(avail)` cannot be lowered by adding
TFs beneath it.

MT12 and ST12 are kept as the lineage's own named accessors over LIN_TFS even though TFS now covers
them: the lineage is a different mechanic from the baton and reads its own names."""
_ALL_TFS = sorted(set(TFS) | set(LIN_TFS))
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
BANK = {t: momo_bank(db, t) for t in _ALL_TFS}
db.disconnect()
tp = np.load(os.path.join(TAPE_DIR, _tape_key(EM, HOURS, WARMUP, {'src': sy['s'], 'len': sy['l']}) + '.npz'))
ts = tp['__ts__']; PX = tp['__pxs__']
LD = lambda tfs, role: np.asarray(np.load(os.path.join(LINE_DIR, _line_key(EM, HOURS, WARMUP, override(tfs, *spec[role])) + '.npy'), mmap_mode='r'), float)
R = {t: LD(t * 60, 'r')[:len(ts)] for t in _ALL_TFS}
U = lambda k: dt.datetime.fromtimestamp(int(ts[k]) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
K = lambda s: int(np.searchsorted(ts, int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp() * 1000)))
# JOE 1004, RULING: "start the walk 3 hours earlier, regardless of if it's a o9-live loop walk or a
# target timestamp that we're focusing on". So the chain is WARMED from 3 h back and PRINTING starts
# at the requested bar - row 1 is then the rider a continuous walk would be carrying, not a cold seed.
WARM_BARS = int(LG['warm_bars'])               # 2160 bars = 3 h at the 5 s grid

# ---- rig.DR, per bar. WINDOW-INDEPENDENT, so it is built ONCE at import, not per call.
G1, M13 = LD(60, 'Mage'), LD(13 * 60, 'm')
DRv = np.zeros(len(ts), np.int8); cur = 0
for k in range(min(len(ts), len(G1), len(M13))):
    a, b = G1[k], M13[k]
    if a == a and b == b:
        if a >= 85.0 and b >= 85.0: cur = +1
        elif a <= 15.0 and b <= 15.0: cur = -1
    DRv[k] = cur


def compute(start_s, end_s, octosig_path=None, warn=True):
    """The window compute, verbatim from what ran at module scope before the 1005 split.
    -> SimpleNamespace with every array and closure the renderer and the DB builder read."""
    P = K(start_s)                                 # the first PRINTED bar
    A = max(0, P - WARM_BARS)                      # the first WALKED bar
    B = K(end_s); N = B - A + 1
    if warn and (A == 0 or P - A < WARM_BARS):
        print('# WARNING: only %.2f h of warm-up available, not 3 h' % ((P - A) * 5 / 3600.0))
    D = DRv[A:B + 1]
    if (D == 0).any():
        raise SystemExit('rig.DR is 0 on %d bars in this window - no direction, and no rule for it' % int((D == 0).sum()))

    # ---- mom-true and stalled, selected per bar by rig.DR
    MT = {}; ST = {}
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
                MT[t] = np.array([momo_g_why(R[t], int(D[i]), A + i)[0] in ('momo', 'curl')
                                  for i in range(N)])
    # ---- mom-true again, over LIN_TFS, for Joe's ws1-anchored lineage ONLY. ws3..ws12 are shared
    # with the baton's own MT - same bank, same window, same bars - so only ws1 and ws2 are new work.
    MT12 = dict(MT)
    for t in LIN_TFS:
        if t in MT12: continue
        with momo_config(BANK[t]):
            with momo_window(int(BANK[t]['k_window']) * t):
                MT12[t] = np.array([momo_g_why(R[t], int(D[i]), A + i)[0] in ('momo', 'curl')
                                    for i in range(N)])
    MT12 = {t: MT12[t] for t in LIN_TFS}

    # ---- stalled again, over LIN_TFS. The lineage's loss test fires on the RIDER's stall, and a
    # rider can be ws1 or ws2 (09-25 09:32's ladder is O........... - ws1 is the only oob line), so
    # ST over TFS 3..23 cannot answer it. Same construction as ST, same bank, same STALL_N.
    ST12 = dict(ST)
    for t in LIN_TFS:
        if t in ST12: continue
        both = {}
        for dd in (-1, +1):
            with momo_config(BANK[t]):
                with momo_window(int(BANK[t]['k_window']) * t):
                    step, samples = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
            both[dd] = stall_mask(R[t], dd, STALL_N, step, samples)[A:B + 1]
        ST12[t] = np.where(D > 0, both[+1], both[-1])
    ST12 = {t: ST12[t] for t in LIN_TFS}

    ONSET = {t: np.flatnonzero(np.diff(np.concatenate(([0], ST[t].astype(np.int8)))) == 1) for t in TFS}
    STALL_EV = sorted([(int(x), t) for t in TFS for x in ONSET[t]])
    STALL_AT = [x for x, _t in STALL_EV]
    nst = np.array([sum(1 for t in TFS if ST[t][j]) for j in range(N)])
    nmt = np.array([sum(1 for t in TFS if MT[t][j]) for j in range(N)])

    def traj(t, j):
        """r's trajectory direction for TF t at bar A+j, at rig.DR. -> 'towards', 'away' or '-'."""
        if not t: return '—'
        d = int(D[j])
        g = trajectory(R[t], d, A + j, AF_BLOCK, TRAJ_MIN_BARS, TRAJ_MIN_TRAVEL)
        if g['has']: return 'towards'
        rv = trajectory(R[t], -d, A + j, AF_BLOCK, TRAJ_MIN_BARS, TRAJ_MIN_TRAVEL)
        return 'away' if rv['has'] else '—'

    # ---- octo-sig rows
    OS = []
    if octosig_path and os.path.exists(octosig_path):
        day = start_s[:10]
        for ln in open(octosig_path):
            if not ln.startswith('R|') or ln.startswith('R|run'): continue
            f = ln.rstrip('\n').split('|')
            if len(f) < 7: continue
            try: k = K(day + ' ' + f[2])
            except ValueError: continue
            if P <= k <= B: OS.append((k, f[2], f[3], int(f[4]), int(f[5]), f[6]))

    # ---- PHASE 1: walk the chain. Compute only.
    RIDER = np.zeros(N, np.int16)
    CHAIN = []
    avail = lambda j: [t for t in TFS if MT[t][j] and not ST[t][j]]
    j = 0; rider = None; nn = 0
    while j < N:
        if rider is None:
            c = avail(j)
            if not c: j += 1; continue
            rider = max(c); start = j
        if ST[rider][j] or not MT[rider][j]:
            nn += 1
            CHAIN.append((nn, rider, start, j, 'STALLED' if ST[rider][j] else 'lost mom-true',
                          [x for x in avail(j) if x != rider]))
            RIDER[start:j + 1] = rider
            rider = None; j += 1; continue
        j += 1
    if rider is not None:
        nn += 1
        CHAIN.append((nn, rider, start, N - 1, 'still riding', avail(N - 1)))
        RIDER[start:N] = rider
    PASSED = [c[3] for c in CHAIN]
    last_baton = lambda u: (U(A + max(b for b in PASSED if b <= u)) if any(b <= u for b in PASSED) else '—')
    last_stall = lambda u: (U(A + max(b for b in STALL_AT if b <= u)) if any(b <= u for b in STALL_AT) else '—')

    import types
    return types.SimpleNamespace(
        A=A, B=B, N=N, P=P, D=D, MT=MT, MT12=MT12, ST=ST, ST12=ST12, ONSET=ONSET, STALL_EV=STALL_EV, STALL_AT=STALL_AT,
        nst=nst, nmt=nmt, traj=traj, OS=OS, RIDER=RIDER, CHAIN=CHAIN, PASSED=PASSED,
        avail=avail, last_baton=last_baton, last_stall=last_stall)


def render(C, start_s, end_s):
    """PHASE 2, verbatim. Reads only what compute() returned."""
    A, B, N, P, D = C.A, C.B, C.N, C.P, C.D
    MT, ST, nst, nmt = C.MT, C.ST, C.nst, C.nmt
    ONSET, STALL_EV, STALL_AT = C.ONSET, C.STALL_EV, C.STALL_AT
    traj, OS, RIDER, CHAIN, PASSED = C.traj, C.OS, C.RIDER, C.CHAIN, C.PASSED
    avail, last_baton, last_stall = C.avail, C.last_baton, C.last_stall
    # ---- PHASE 2: render
    print('# %s .. %s   rig.DR PER BAR   STALL_N %d   ws%d..ws%d   traj block %d min_bars %d'
          % (start_s, end_s, STALL_N, TFS[0], TFS[-1], AF_BLOCK, TRAJ_MIN_BARS))
    print('# walk WARMED from %s (3 h back, Joe 1004) - printing starts at %s'
          % (U(A), U(P)))
    print('# pxs high %s %.6f  |  pxs low %s %.6f  |  dr +1 on %d bars, -1 on %d   (PRINTED span only)'
          % (U(P + int(np.argmax(PX[P:B+1]))), PX[P:B+1].max(), U(P + int(np.argmin(PX[P:B+1]))),
             PX[P:B+1].min(), int((D[P-A:] > 0).sum()), int((D[P-A:] < 0).sum())))
    print('# octo-sig rows interleaved: %d' % len(OS))
    print()
    # COLUMN NAMES FIXED 1005. "stalled TFs" showed stall ONSETS while the stalled STATE appeared only
    # as a count, so the two were read as the same thing. Now: `stalled now` is the STATE list and
    # `new stalls` is the onsets since the prior row.
    print('| # | riding | traj | dr | from | to | held | why it passed | stalled | mom-true | pxs | candidates | stalled now | new stalls | baton ts | stalled ts |')
    print('|' + '---|' * 16)
    P0 = P - A
    prev = max([b for b in PASSED if b <= P0], default=0)
    for bar, kind, row in sorted([(c[3], 'baton', c) for c in CHAIN] + [(o[0] - A, 'sig', o) for o in OS]):
        if bar < P0:
            prev = bar
            continue
        if kind == 'baton':
            nn_, rd, st_, j_, why, c = row
            print('| %d | ws%d | %s | %+d | %s | %s | %.1f m | %s | %d of %d | %d | %.6f | %s | %s | %s | %s | %s |'
                  % (nn_, rd, traj(rd, j_), D[j_], U(A + st_), U(A + j_), (ts[A+j_]-ts[A+st_])/60000.0, why,
                     nst[j_], len(TFS), nmt[j_], PX[A+j_],
                     ', '.join('ws%d' % x for x in c) if c else '**NONE**',
                     ', '.join('ws%d' % t for t in TFS if ST[t][j_]) or '—', '—',
                     last_baton(j_), last_stall(j_)))
        else:
            _k, sig, _l, _b, _d, _arm = row
            bp = [b for b in PASSED if prev < b <= bar]
            so = [(x, t) for x, t in STALL_EV if prev < x <= bar]
            cnt = {}
            for _x, t in so: cnt[t] = cnt.get(t, 0) + 1
            tfs_ = ', '.join('ws%d%s' % (t, '' if cnt[t] == 1 else ' x%d' % cnt[t]) for t in sorted(cnt)) or '—'
            rd = int(RIDER[bar])
            cav = avail(bar)
            print('| **octo-sig** | %s | %s | %+d | **%s** | %d baton | %d new stalls | since the prior row | %d of %d | %d | %.6f | %s | %s | %s | %s | %s |'
                  % ('ws%d' % rd if rd else '**no rider**', traj(rd, bar), D[bar], sig, len(bp), len(so),
                     nst[bar], len(TFS), nmt[bar], PX[A+bar],
                     ', '.join('ws%d' % x for x in cav) if cav else '**NONE**',
                     ', '.join('ws%d' % t for t in TFS if ST[t][bar]) or '—', tfs_,
                     last_baton(bar), last_stall(bar)))
        prev = bar
    print()
    print('| bar | dr | stalled of %d | mom-true of %d | pxs |' % (len(TFS), len(TFS))); print('|---|---|---|---|---|')
    for j in range(P0, N, 360):
        print('| %s | %+d | %d | %d | %.6f |' % (U(A+j), D[j], nst[j], nmt[j], PX[A+j]))


if __name__ == '__main__':
    _os_path = sys.argv[3] if len(sys.argv) > 3 else None
    _C = compute(sys.argv[1], sys.argv[2], _os_path)
    render(_C, sys.argv[1], sys.argv[2])
