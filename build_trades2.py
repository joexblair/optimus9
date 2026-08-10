"""build_trades2 — Joe's four ideas bolted onto rpl_trades, as raw stored values. Joe 0803 11:40.

    Joe: "try things like - requiring an r line to be on a side of 50 when the trade starts. add s15 and
    s22 momo to the mix - test them when the s6 exit is signalling, see if you get more length from the
    trade / require oob gcs5x crossing gcs5Mage (or any other ltf) to optimise the trade entry / fire RPL
    ladder's init scan just befer the trade entry, to discover if your trading against trend"

    and: "RPL init scan: RPL starts at the ceiling TF, and looks down to find the highest TF that has a
    oob r, or a r-prediction. you'll need to scan bear and bull"

WHY THE r LINES COME FROM L0 AND NOT A FRESH JIG. Measured 0803: against rpl_walk.L0 (warmup 1012 h) a
fresh 90 h-warmup jig reproduces every BOLLINGER line to 0.0000 — s1/s4/s15/s22/s60/s120 M and m are bit
-identical, so the cache is reading the same klines and is NOT stale. The kline oscillator r does NOT
match, and the gap scales with TF: s4 0.85% of bars, s22 4.4%, s60 12.5%, s120 29.8% (max 7.32 points).
That is warmup, not contamination — k_len 7 -> rsi 5 -> stc 11 is a recursive chain, and 90 h at a 2 h bar
is 45 bars of burn-in. build_trades.py used 60 h, so ITS tr_r{t}/tr_opp{t} at the high rungs are
under-warmed; this run overwrites them from L0.

WHAT IS ADDED, one set per existing rpl_trades row (keyed on tr_ms)
  A  r VALUE at 18 rungs at the entry bar          tr_rv{tf}         — "r on a side of 50" is a WHERE
  B  momo of s15/s22 Mage AND r at the EXIT bar    tr_x{ln}_{st,sl,r2,rw}
     plus the 2nd and 3rd s6 exit signals          tr_ret2/3, mae2/3, hold2/3, exit2/3_ms
  C  LTF confirming x-cross-Mage entry, both OOB   tr_c{tag}_bars, tr_c{tag}_px   (gcs5/15/30, s1, s2)
  D  RPL init scan, ceiling-down                   tr_init_{bull,bear}[90][_12]

CONCRETIONS I CHOSE (structural; every VALUE stays raw so the threshold is Joe's)
  * momo is stored as state+slope+R2+level, not as a pass/fail — Joe has already said the 50 level gate is
    too low for a Mage, so no gate is baked in.
  * the LTF entry cross is the CONFIRMING direction (x over Mage for a long), mirroring Joe's exit rule
    which is a crossunder for a hi breach; both lines must be OOB on the trade side, also mirroring it.
  * cross debounce for the LTF entry = 6 bars = 30 s, matching the entry DWELL. The 72 Joe swept is the
    EXIT wob; 72 bars on a 5 s line is 6 minutes and would not be an entry timer.
  * the init scan is recorded at ceiling 120 and at ceiling 90 (rpl_config tf_ceiling), and at the entry
    bar and 12 bars (1 min) before it. Nothing is thresholded.
  * NO CAP on how long the LTF cross may take to arrive: bars-to-cross is stored, -1 = never.

    python3 build_trades2.py
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline, _Causal
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
HI, LO = R.HI, R.LO
DWELL, WOB, XWOB = 6, 72, 6
RUNGS = [15, 22, 30, 45, 60, 90, 120]                       # the rungs already in rpl_trades
RV = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 22, 25, 30, 45, 60, 90, 120]      # idea A ladder
MOMO_LN = [('m15', 15, 'M'), ('m22', 22, 'M'), ('r15', 15, 'r'), ('r22', 22, 'r')]
LTF = [('g5', 5.0 / 60.0), ('g15', 0.25), ('g30', 0.5), ('s1', 1.0), ('s2', 2.0)]
CEIL_A, CEIL_B, PRE = 120, 90, 12                           # 12 bars = 1 min before the entry

# momo constants, read from build_exhv2's source rather than imported — importing it costs ~2 min and
# pulls a second heavy module in alongside L0. predict_board.py set this precedent. Values are asserted
# against the source text below so a change there fails loudly instead of silently forking.
MOMO_WINDOW_MIN, MOMO_STEP_MIN = 60, 5                      # build_exhv2:32,40
MOMO_STEP_BARS = MOMO_STEP_MIN * 12                         # 60 bars at the 5 s grid
MOMO_SAMPLES = MOMO_WINDOW_MIN // MOMO_STEP_MIN             # 12 samples
MOMO_SLOPE_MIN, MOMO_R2_MIN, LEVEL_SLACK = 1.0, 0.50, 13.9
CURL_ARC_MIN, CURL_VTX_LO, CURL_VTX_HI = 4.0, 0.05, 0.95


def _check_momo_consts():
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_exhv2.py')).read()
    g = {}
    for ln in src.splitlines():
        s = ln.split('#')[0].strip()
        if s.startswith(('MOMO_', 'LEVEL_SLACK', 'CURL_')) and '=' in s and '(' not in s.split('=')[1]:
            k, v = s.split('=', 1)
            try:
                g[k.strip()] = float(v.strip())
            except ValueError:
                pass
    bad = []
    for k, mine in (('MOMO_SAMPLES', MOMO_SAMPLES), ('MOMO_STEP_BARS', MOMO_STEP_BARS),
                    ('MOMO_SLOPE_MIN', MOMO_SLOPE_MIN), ('MOMO_R2_MIN', MOMO_R2_MIN),
                    ('LEVEL_SLACK', LEVEL_SLACK), ('MOMO_WINDOW_MIN', MOMO_WINDOW_MIN),
                    ('CURL_VTX_LO', CURL_VTX_LO), ('CURL_VTX_HI', CURL_VTX_HI),
                    ('CURL_ARC_MIN', CURL_ARC_MIN)):
        if k in g and abs(g[k] - mine) > 1e-12:
            bad.append('%s: build_exhv2=%g here=%g' % (k, g[k], mine))
    if bad:
        raise SystemExit('momo constants have drifted from build_exhv2:\n  ' + '\n  '.join(bad))
    print('momo constants match build_exhv2 (%d checked)' % len(g))


def vmomo(r, dr):
    """(state int8 0=none/1=sideways/2=curl/3=momo, slope, r2, level) at EVERY bar.
    Vectorisation of build_exhv2.momo() at :113-162, verified bar-for-bar in vmomo.py (0 mismatches
    over 1,172 samples per direction)."""
    n = len(r); S, SB = MOMO_SAMPLES, MOMO_STEP_BARS
    span = (S - 1) * SB
    slope = np.full(n, np.nan); r2 = np.full(n, np.nan)
    idx = np.arange(span, n)
    if len(idx):
        cols = np.stack([r[idx - (S - 1 - k) * SB] for k in range(S)], axis=1)
        ok = np.isfinite(cols).all(axis=1)
        x = np.arange(S, dtype=float); xm = x.mean(); sxx = ((x - xm) ** 2).sum()
        ym = cols.mean(axis=1)
        sl = ((cols - ym[:, None]) * (x - xm)).sum(axis=1) / sxx
        ic = ym - sl * xm
        res = ((cols - (sl[:, None] * x + ic[:, None])) ** 2).sum(axis=1)
        tot = ((cols - ym[:, None]) ** 2).sum(axis=1)
        rr = np.where(tot > 1e-12, 1 - res / np.where(tot > 1e-12, tot, 1), 0.0)
        slope[idx] = np.where(ok, sl, np.nan); r2[idx] = np.where(ok, rr, np.nan)
    rw = r.copy()
    st = np.zeros(n, np.int8)
    have = np.isfinite(slope) & np.isfinite(r2) & np.isfinite(rw)
    trk = np.clip(np.where(have, r2, 0.0) *
                  np.minimum(1.0, np.abs(np.where(have, slope, 0.0)) / max(1e-9, MOMO_SLOPE_MIN)), 0.0, 1.0)
    slack = LEVEL_SLACK * trk
    level = (rw >= 50 - slack) if dr > 0 else (rw <= 50 + slack)
    flat = np.abs(slope) < MOMO_SLOPE_MIN
    aligned = (slope > 0) if dr > 0 else (slope < 0)
    st[have & (~flat) & level & aligned & (r2 >= MOMO_R2_MIN)] = 3
    cand = have & flat & level
    st[cand] = 1
    nb = MOMO_WINDOW_MIN * 12
    ci = np.flatnonzero(cand); ci = ci[ci - nb + 1 >= 0]
    if len(ci):
        xx = np.linspace(0.0, 1.0, nb)
        A = np.vstack([xx ** 2, xx, np.ones(nb)]).T
        pinv = np.linalg.pinv(A)
        for a in range(0, len(ci), 20000):                 # chunked: the full stack is len(ci) x 720
            cc = ci[a:a + 20000]
            YY = np.stack([r[i - nb + 1:i + 1] for i in cc], axis=1)
            good = np.isfinite(YY).all(axis=0)
            co = pinv @ np.nan_to_num(YY)
            qa, qb = co[0], co[1]
            with np.errstate(divide='ignore', invalid='ignore'):
                vtx = np.where(np.abs(qa) > 1e-12, -qb / (2 * qa), np.nan)
            arc = np.abs(qa) * 0.25
            hit = good & np.isfinite(vtx) & (vtx > CURL_VTX_LO) & (vtx < CURL_VTX_HI) & (arc >= CURL_ARC_MIN)
            st[cc[hit]] = 2
    return st, slope, r2, rw


def runs_of(m):
    idx = np.flatnonzero(m)
    if not len(idx):
        return []
    out = []; a = idx[0]; p = idx[0]
    for i in idx[1:]:
        if i != p + 1:
            out.append((a, p)); a = i
        p = i
    out.append((a, p)); return out


def runlen(m):
    """consecutive True bars ending AT i — backward, causal. build_trades.py:69."""
    idx = np.arange(len(m)); rst = np.where(m, 0, idx + 1)
    return (idx + 1) - np.maximum.accumulate(rst)


NEW = (['tr_rv%d DOUBLE' % t for t in RV] +
       [c for tag, _, _ in MOMO_LN for c in
        ('tr_x%s_st TINYINT' % tag, 'tr_x%s_sl DOUBLE' % tag,
         'tr_x%s_r2 DOUBLE' % tag, 'tr_x%s_rw DOUBLE' % tag)] +
       ['tr_ret2 DOUBLE', 'tr_ret3 DOUBLE', 'tr_mae2 DOUBLE', 'tr_mae3 DOUBLE',
        'tr_hold2 INT', 'tr_hold3 INT', 'tr_exit2_ms BIGINT', 'tr_exit3_ms BIGINT'] +
       [c for tag, _ in LTF for c in ('tr_c%s_bars INT' % tag, 'tr_c%s_px DOUBLE' % tag)] +
       ['tr_init_bull INT', 'tr_init_bear INT', 'tr_init_bull90 INT', 'tr_init_bear90 INT',
        'tr_init_bull_12 INT', 'tr_init_bear_12 INT'])


def main(argv):
    _check_momo_consts()
    t0 = time.time()
    L = R.L0; ts = np.asarray(L['ts'], np.int64); n = len(ts); E = L['E']; P = L['P']
    print('L0 %d bars  %s -> %s  TFs %d..%d   %.0f s'
          % (n, u(ts[0]), u(ts[-1]), R.TFS[0], R.TFS[-1], time.time() - t0))

    # --- the few lines L0 does NOT carry: the 0.70-mult Mages and the sub-minute LTF pairs ---
    ovr = {}
    ovr.update(bbline('p4', 4.0, length=37, mult=0.70, src='close'))
    ovr.update(bbline('m6', 6.0, length=37, mult=0.70, src='close'))
    for tag, tf in LTF[:3]:                                 # gcs5/gcs15/gcs30 are below L0's TF grid
        ovr.update(bbline('%sM' % tag, tf, length=37, mult=0.83, src='close'))
        ovr.update(bbline('%sX' % tag, tf, length=5, mult=0.37, src='close'))
    # COVER the tape, then ALIGN by timestamp — do not assume the fresh jig reproduces L0's exact span.
    # warmup 180 h: measured 0803, 60 h already reproduces L0's r to 0.0000 at every TF up to s120 when
    # scored on the analysis window, so 180 h is 3x the proven requirement.
    TAPE0 = int(dt.datetime(2026, 5, 18, tzinfo=dt.timezone.utc).timestamp() * 1000)
    end_ms = int(ts[-1]) + 5000
    hrs = int((end_ms - TAPE0) / 3600000) + 2
    with Jig(end_ms, hours=hrs, warmup=180, overrides=ovr) as j:
        t2 = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        srcv = IC.build_source(base, R.PXS_CFG['src']); ei = np.flatnonzero(evt)
        px = np.full(len(srcv), np.nan); px[ei] = IC.dema(srcv[ei], int(R.PXS_CFG['len']))
        f = np.isfinite(px); ixf = np.where(f, np.arange(len(px)), 0); np.maximum.accumulate(ixf, out=ixf)
        px = px[ixf]; px[:int(np.argmax(f))] = px[int(np.argmax(f))]
        M4 = np.asarray(j.W.line('p4'), float); M6 = np.asarray(j.W.line('m6'), float)
        LT = {tag: (np.asarray(j.W.line('%sX' % tag), float), np.asarray(j.W.line('%sM' % tag), float))
              for tag, _ in LTF[:3]}
    off = int(np.searchsorted(ts, int(t2[0])))
    k = min(len(t2), n - off)
    if int(ts[off]) != int(t2[0]) or not (ts[off:off + k] == t2[:k]).all():
        raise SystemExit('grid mismatch: fresh jig starts %s, L0[%d]=%s' % (u(t2[0]), off, u(ts[off])))

    def onL0(a):                                            # lift a fresh-jig array onto L0's index
        out = np.full(n, np.nan); out[off:off + k] = a[:k]; return out

    px = onL0(px); M4 = onL0(M4); M6 = onL0(M6)
    LT = {tag: (onL0(v[0]), onL0(v[1])) for tag, v in LT.items()}
    print('fresh lines aligned onto L0 grid at offset %d (%s), %d bars   %.0f s'
          % (off, u(t2[0]), k, time.time() - t0))
    for tag, tf in LTF[3:]:                                 # s1/s2 come straight from L0
        LT[tag] = (E[int(tf)]['x'], E[int(tf)]['M'])

    # --- exits: the s6x x s6Mage cross at wob 72, both OOB (Joe's rule, unchanged) ---
    cau = _Causal(None); X6 = E[6]['x']; dd = X6 - M6
    OH = (X6 >= HI) & (M6 >= HI); OL = (X6 <= LO) & (M6 <= LO)
    cdn = cau.cross_wob(dd, 0.0, -1, WOB); cup = cau.cross_wob(dd, 0.0, 1, WOB)
    EV = {1: np.flatnonzero((cdn & ~np.r_[False, cdn[:-1]]) & OH),
          -1: np.flatnonzero((cup & ~np.r_[False, cup[:-1]]) & OL)}

    # --- LTF confirming entry cross: x over Mage for a long, both OOB on the trade side ---
    CX = {}
    for tag, _ in LTF:
        xx, mm = LT[tag]; d2 = xx - mm
        cu = cau.cross_wob(d2, 0.0, 1, XWOB); cd = cau.cross_wob(d2, 0.0, -1, XWOB)
        CX[(tag, 1)] = np.flatnonzero((cu & ~np.r_[False, cu[:-1]]) & (xx >= HI) & (mm >= HI))
        CX[(tag, -1)] = np.flatnonzero((cd & ~np.r_[False, cd[:-1]]) & (xx <= LO) & (mm <= LO))

    # --- momo at every bar for the four s15/s22 lines, both directions ---
    MO = {}
    for tag, tf, kind in MOMO_LN:
        arr = E[tf][kind]
        for dr in (1, -1):
            MO[(tag, dr)] = vmomo(arr, dr)
    print('momo + crosses built   %.0f s' % (time.time() - t0))

    # --- RPL init scan: ceiling DOWN, highest TF with an OOB r or an r-pred, per polarity ---
    INIT = {}
    for ceil in (CEIL_A, CEIL_B):
        for dr in (1, -1):
            best = np.zeros(n, np.int32)
            for tf in range(1, ceil + 1):                   # ascending, so the LAST write is the highest
                r_ = E[tf]['r']
                hit = ((r_ >= HI) if dr > 0 else (r_ <= LO)) | (np.asarray(P[tf], np.int8) == dr)
                np.copyto(best, np.int32(tf), where=hit)
            INIT[(ceil, dr)] = best
    print('init scan built (%d TFs x 2 ceilings x 2 polarities)   %.0f s' % (CEIL_A, time.time() - t0))

    # --- excursions, redefined exactly as build_trades did so tr_ms keys match ---
    ALLR = []
    for side in ('hi', 'lo'):
        for a, b in runs_of((M4 >= HI) if side == 'hi' else (M4 <= LO)):
            ALLR.append((int(a), int(b), side))
    ALLR.sort()
    QUAL = [r_ for r_ in ALLR if (r_[1] - r_[0] + 1) > DWELL]
    print('excursions with dwell>%d: %d' % (DWELL, len(QUAL)))

    # --- REBUILD THE BASE ROWS SINGLE-PASS (Joe 0803 12:50) --------------------------------------
    # build_trades.py walked the tape in 13-day chunks and de-duplicated on tr_ms with INSERT IGNORE.
    # An excursion straddling a chunk edge was therefore banked ONCE with its truncated span and the
    # correct full-span version was dropped: 5,954 rows banked against 6,893 excursions on this single
    # pass — 939 missing, 13.6%. There is no chunking here (L0 already spans the tape), so the boundary
    # class of error cannot occur. Column definitions are carried verbatim from build_trades.py.
    S1 = E[1]['M']                                          # s1Mage bb 37 | 0.83 | close
    HOLD = {'hi': runlen(np.nan_to_num(S1, nan=-1e9) >= HI - 15),   # fuzzy-oob slack 15 board points
            'lo': runlen(np.nan_to_num(S1, nan=1e9) <= LO + 15)}
    base_rows = []
    for kq, (x, y, side) in enumerate(QUAL):
        sgn = 1 if side == 'hi' else -1
        prev = QUAL[kq - 1] if kq else None
        if prev is None:
            alt_s = alt_l = 0
        elif prev[2] != side:
            alt_s = alt_l = 1
        else:
            alt_s = 0
            seg = M4[prev[1]:x + 1]
            alt_l = int((seg < 50).any() if side == 'hi' else (seg > 50).any())
        nz = EV[sgn][EV[sgn] > x]
        e = int(nz[0]) if len(nz) else (n - 1)
        p0 = px[x]; seg = px[x + 1:e + 1]
        if not len(seg) or not np.isfinite(p0):
            continue
        htf = []
        for t in RUNGS:
            mv, rv = E[t]['M'][x], E[t]['r'][x]
            if np.isfinite(mv) and np.isfinite(rv):
                htf += [float(mv), float(rv), int((mv < rv) if sgn > 0 else (mv > rv))]
            else:
                htf += [None, None, None]
        base_rows.append(tuple([int(ts[x]), u(ts[x]), side, sgn, float(p0), int(y - x + 1),
                                alt_s, alt_l, int(HOLD[side][x - 1]) if x else 0] + htf +
                               [int(ts[e]), u(ts[e]), float(px[e]), int(e - x),
                                float(sgn * (px[e] - p0) / p0 * 100.0),
                                float(abs(min(0.0, sgn * ((seg.min() if sgn > 0 else seg.max()) - p0) / p0 * 100.0))),
                                float(max(0.0, sgn * ((seg.max() if sgn > 0 else seg.min()) - p0) / p0 * 100.0)),
                                int(not len(nz))]))
    d = DatabaseManager(**get_db_config()); d.connect()
    bcols = (['tr_ms', 'tr_utc', 'tr_side', 'tr_dr', 'tr_px', 'tr_dwell_bars', 'tr_alt_strict',
              'tr_alt_loose', 'tr_s1hold'] +
             [c for t in RUNGS for c in ('tr_m%d' % t, 'tr_r%d' % t, 'tr_opp%d' % t)] +
             ['tr_exit_ms', 'tr_exit_utc', 'tr_exit_px', 'tr_hold_bars', 'tr_ret', 'tr_mae',
              'tr_mfe', 'tr_no_cross'])
    d.execute('DELETE FROM rpl_trades')
    d.executemany('INSERT INTO rpl_trades (%s) VALUES (%s)'
                  % (','.join(bcols), ','.join(['%s'] * len(bcols))), base_rows, chunk=2000)
    print('base rows rebuilt single-pass: %d (was 5954 chunked)   %.0f s'
          % (len(base_rows), time.time() - t0))

    have = {r_['COLUMN_NAME'].lower() for r_ in d.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
        "AND TABLE_NAME='rpl_trades'", fetch=True)}
    add = [c for c in NEW if c.split()[0].lower() not in have]
    for c in add:
        d.execute('ALTER TABLE rpl_trades ADD COLUMN %s' % c)
    print('added %d columns (%d already present)' % (len(add), len(NEW) - len(add)))

    cols = [c.split()[0] for c in NEW]
    sql = ('UPDATE rpl_trades SET ' + ','.join('%s=%%s' % c for c in cols) + ' WHERE tr_ms=%s')
    rows = []
    for x, y, side in QUAL:
        sgn = 1 if side == 'hi' else -1
        nz = EV[sgn][EV[sgn] > x]
        e = int(nz[0]) if len(nz) else (n - 1)
        p0 = px[x]
        v = [float(E[t][ 'r'][x]) if np.isfinite(E[t]['r'][x]) else None for t in RV]
        for tag, tf, kind in MOMO_LN:
            st, sl, r2, rw = MO[(tag, sgn)]
            v += [int(st[e]), float(sl[e]) if np.isfinite(sl[e]) else None,
                  float(r2[e]) if np.isfinite(r2[e]) else None,
                  float(rw[e]) if np.isfinite(rw[e]) else None]
        ex = [e]
        for _ in (2, 3):                                    # the 2nd and 3rd s6 exit signals
            nx = EV[sgn][EV[sgn] > ex[-1]]
            ex.append(int(nx[0]) if len(nx) else (n - 1))
        for k in (1, 2):
            e2 = ex[k]; seg = px[x + 1:e2 + 1]
            if len(seg):
                v += [float(sgn * (px[e2] - p0) / p0 * 100.0)]
            else:
                v += [None]
        for k in (1, 2):
            e2 = ex[k]; seg = px[x + 1:e2 + 1]
            v += [float(abs(min(0.0, sgn * ((seg.min() if sgn > 0 else seg.max()) - p0) / p0 * 100.0)))
                  if len(seg) else None]
        v += [int(ex[1] - x), int(ex[2] - x), int(ts[ex[1]]), int(ts[ex[2]])]
        for tag, _ in LTF:
            c = CX[(tag, sgn)]; c = c[(c > x) & (c <= e)]
            if len(c):
                v += [int(c[0] - x), float(px[int(c[0])])]
            else:
                v += [-1, None]
        v += [int(INIT[(CEIL_A, 1)][x]), int(INIT[(CEIL_A, -1)][x]),
              int(INIT[(CEIL_B, 1)][x]), int(INIT[(CEIL_B, -1)][x]),
              int(INIT[(CEIL_A, 1)][max(0, x - PRE)]), int(INIT[(CEIL_A, -1)][max(0, x - PRE)])]
        rows.append(tuple(v) + (int(ts[x]),))
    d.executemany(sql, rows, chunk=500)
    got = d.execute('SELECT COUNT(*) n, SUM(tr_init_bull IS NOT NULL) f FROM rpl_trades', fetch=True)[0]
    print('updated %d excursions -> rpl_trades %d rows, %d filled   total %.0f s'
          % (len(rows), got['n'], got['f'], time.time() - t0))

    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
