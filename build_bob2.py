"""build_bob2 — bobbing on EVERY TF, the HTF Mage that ends it, and the corrected s6 exhaustion reverse.
Joe 0803 19:00.

    Joe: "bobbing is a function for all TFs - you'll find lots of bobbing in the <=1 TFs"
         "bob ending is related to the same TF"
         "'which HTF Mage breaks them out' does it cross OOB on the cage side? - yes"
         "9/12/whatever works"
         "no, I'm referring to s4m crossing up while s4Mage is slowly reversing (still OOB)"

WHAT CHANGED FROM build_bob.py
  1. SEQUENCES ARE PER-TF, not s4-only. Measured: s1 has 3,547 sequences, s4 1,096, s120 45. The full
     ladder is ~94,000 sequences.
  2. THE BREAK IS ON THE BOB'S OWN TF ("bob ending is related to the same TF") - unchanged, that was
     already right: the bob at TF X ends when TF X's own Mage traverses 50 away from the cage side.
  3. THE BREAKER CROSSES OOB ON THE CAGE SIDE (Joe: "yes"). So a hi cage is broken by a rung crossing
     OOB HI. Only rungs ABOVE the bob's own TF are considered - the hypothesis is that a HIGHER TF
     pulls it out.
  4. THE s6 EVENT WAS THE WRONG LINE. build_bob.py used s4Mage crossing INTO OOB. Joe means s4m - the
     MINI bb 6|0.45 at TF4 - crossing UP through LO while s4Mage (bb 37|0.70 @ TF4) is STILL lo-OOB and
     slowly reversing. Mirrored for the hi side: s4m crossing DOWN through HI while s4Mage is still
     hi-OOB. rpl_s6exh is left in place; this writes rpl_s6exh2.

WHY ONE ROW PER SEQUENCE AND NOT THE FULL CROSS-PRODUCT. seq x 120 rungs = 11.3 M rows. The question is
"which HTF Mage ends the bob", so each sequence stores the rung that actually did it - nearest cage-side
OOB crossing at or BEFORE the break - plus the RUNNER-UP, because Joe 0803 noted "there will be more than
one TF creating the same pull". The full 120-rung detail already exists for TF4 in rpl_bob_htf.

MOMO SAMPLES (Joe: "9/12/whatever works"). Twelve stored, bk_s0..bk_s11, at MOMO_STEP_BARS = 60 bars =
5 min apart, s11 = the bob-start bar itself. Nine is the slice bk_s3..bk_s11. Nothing is gated here; the
slope and R2 of the 12-point fit are stored beside them.

THE POINT OF THE TABLE, in Joe's words: "if we have that HTF Mage value, and the momo-test samples before
it, we can build a model that detects which HTF Mage will end the bobbing" -> a more targeted exit, and
staying out of entries like 07-28 11:00. Everything needed for that model is bk_* at the BOB START, which
is the trade-open bar and therefore causal. bk_dbrk is the LABEL and is not causal - it is the answer.

LINES  ladder Mage = L0's M = bb 37|0.83|close at TF 1..120.
       TF4 CARRIES TWO MAGES: the walk producer s4Mage is bb 37|0.70 (rpl_trades), the ladder rung s4 is
       bb 37|0.83. The ladder is used throughout here so every rung is the same spec; bs_tf=4 is
       therefore NOT identical to rpl_bob_seq, which used the 0.70 line.
       s4m = mini bb 6|0.45 @TF4 (L0 E[4]['m']),  s4Mage-0.70 and s6Mage-0.70 built fresh.
WINDOW 05-18 -> 07-31. Pre-05-18 is synthetic warmup, never analysis (rpl_walk.py:121, Joe 0729).

    python3 build_bob2.py
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
TAPE0 = int(dt.datetime(2026, 5, 18, tzinfo=dt.timezone.utc).timestamp() * 1000)
# WINDOW (Joe 0803: "reduce the window to 07-25 to 07-30 and recreate the tables"). --from/--to bound
# which sequences and events are BANKED; the LINES keep their full L0 lookback either way, so a narrow
# window costs no line quality. --suffix writes to <table><suffix> so the full-tape build survives.
WIN0, WIN1, SUF = TAPE0, None, ''
DWELL, WOB = 6, 72
MOMO_STEP_BARS, MOMO_SAMPLES = 60, 12
LADDER = list(range(1, 121))
SC = ['bk_s%d' % k for k in range(MOMO_SAMPLES)]

DDL_T = '''CREATE TABLE IF NOT EXISTS rpl_bob2%s (
    b2_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    b2_tf INT, b2_side VARCHAR(2), b2_dr TINYINT,
    b2_start_ms BIGINT, b2_start_utc VARCHAR(20),
    b2_last_ms BIGINT, b2_break_ms BIGINT, b2_break_utc VARCHAR(20), b2_break_bars INT,
    b2_n_exc INT, b2_span_bars INT, b2_mage_at_start DOUBLE, b2_mage_min DOUBLE, b2_mage_max DOUBLE,
    b2_px_start DOUBLE, b2_px_break DOUBLE, b2_ret_to_break DOUBLE,
    bk_tf INT, bk_dbrk INT, bk_mage DOUBLE, bk_state VARCHAR(2), bk_slope DOUBLE, bk_r2 DOUBLE,
    bk2_tf INT, bk2_dbrk INT, bk2_mage DOUBLE,
    bk_n_before INT,
    %s,
    UNIQUE KEY (b2_tf, b2_start_ms), KEY (b2_tf), KEY (bk_tf), KEY (b2_side)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''' % (' %s', ', '.join('%s DOUBLE' % c for c in SC))

DDL_SE_T = '''CREATE TABLE IF NOT EXISTS rpl_s6exh2%s (
    sx_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    sx_ms BIGINT, sx_utc VARCHAR(20), sx_side VARCHAR(2), sx_dr TINYINT,
    sx_s4m DOUBLE, sx_s4mage DOUBLE, sx_s6mage DOUBLE, sx_s6x DOUBLE, sx_px DOUBLE,
    sx_s4m_oob_bars INT, sx_s4mage_oob_bars INT, sx_s6_ib TINYINT,
    sx_rev_exit_ms BIGINT, sx_rev_hold INT, sx_rev_ret DOUBLE, sx_rev_mae DOUBLE, sx_rev_mfe DOUBLE,
    sx_con_exit_ms BIGINT, sx_con_hold INT, sx_con_ret DOUBLE, sx_con_mae DOUBLE, sx_con_mfe DOUBLE,
    sx_kills_ms BIGINT, sx_kills_ret DOUBLE, sx_kills_ret_at_event DOUBLE,
    UNIQUE KEY (sx_ms, sx_side), KEY (sx_side), KEY (sx_s6_ib)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''


def runs_of(m):
    i = np.flatnonzero(m)
    if not len(i):
        return []
    o = []; a = i[0]; p = i[0]
    for z in i[1:]:
        if z != p + 1:
            o.append((a, p)); a = z
        p = z
    o.append((a, p)); return o


def main(argv):
    global WIN0, WIN1, SUF
    g = lambda f, d: (argv[argv.index(f) + 1] if f in argv else d)
    _ms = lambda x: int(dt.datetime(*[int(z) for z in x.split('-')],
                                    tzinfo=dt.timezone.utc).timestamp() * 1000)
    d0, d1 = g('--from', None), g('--to', None)
    if d0:
        WIN0 = _ms(d0)
    if d1:
        WIN1 = _ms(d1)
    SUF = g('--suffix', '')
    t0 = time.time()
    print('WINDOW %s -> %s   tables rpl_bob2%s / rpl_s6exh2%s'
          % (u(WIN0), u(WIN1) if WIN1 else 'tape end', SUF, SUF), flush=True)
    L = R.L0; ts = np.asarray(L['ts'], np.int64); n = len(ts); E = L['E']
    print('L0 %d bars %s -> %s' % (n, u(ts[0]), u(ts[-1])), flush=True)

    ovr = {}
    ovr.update(bbline('p4', 4.0, length=37, mult=0.70, src='close'))
    ovr.update(bbline('m6', 6.0, length=37, mult=0.70, src='close'))
    end_ms = int(ts[-1]) + 5000
    with Jig(end_ms, hours=int((end_ms - TAPE0) / 3600000) + 2, warmup=180, overrides=ovr) as j:
        t2 = np.asarray(j.ts, np.int64); base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        srcv = IC.build_source(base, R.PXS_CFG['src']); ei = np.flatnonzero(evt)
        p_ = np.full(len(srcv), np.nan); p_[ei] = IC.dema(srcv[ei], int(R.PXS_CFG['len']))
        f = np.isfinite(p_); ix = np.where(f, np.arange(len(p_)), 0); np.maximum.accumulate(ix, out=ix)
        p_ = p_[ix]; p_[:int(np.argmax(f))] = p_[int(np.argmax(f))]
        M4_ = np.asarray(j.W.line('p4'), float); M6_ = np.asarray(j.W.line('m6'), float)
    off = int(np.searchsorted(ts, int(t2[0]))); kk = min(len(t2), n - off)
    lift = lambda a: np.concatenate([np.full(off, np.nan), a[:kk], np.full(n - off - kk, np.nan)])
    px, M4, M6 = lift(p_), lift(M4_), lift(M6_)
    print('fresh lines aligned   %.0f s' % (time.time() - t0), flush=True)

    # ---------- SEQUENCES ON EVERY TF ----------
    S_tf, S_x0, S_xl, S_brk, S_side, S_n, S_span = [], [], [], [], [], [], []
    for tf in LADDER:
        Mg = E[tf]['M']
        A = []
        for side in ('hi', 'lo'):
            m = (np.nan_to_num(Mg, nan=-1e9) >= HI) if side == 'hi' else (np.nan_to_num(Mg, nan=1e9) <= LO)
            for a, b in runs_of(m):
                if b - a + 1 > DWELL and int(ts[a]) >= WIN0 and (WIN1 is None or int(ts[a]) < WIN1):
                    A.append((int(a), int(b), side))
        if not A:
            continue
        A.sort()
        seqs = []; cur = [A[0]]
        for i in range(1, len(A)):
            x, y, s = A[i]; _, py, ps = A[i - 1]
            if ps != s:
                brk = True
            else:
                sg = Mg[py:x + 1]
                brk = bool((sg < 50).any() if s == 'hi' else (sg > 50).any())
            if brk:
                seqs.append(cur); cur = [A[i]]
            else:
                cur.append(A[i])
        seqs.append(cur)
        for sq in seqs:
            x0, _, side = sq[0]; _, yl, _ = sq[-1]
            tail = Mg[yl:]
            w = np.flatnonzero((tail < 50) if side == 'hi' else (tail > 50))
            S_tf.append(tf); S_x0.append(x0); S_xl.append(yl)
            S_brk.append(int(yl + w[0]) if len(w) else -1)
            S_side.append(side); S_n.append(len(sq)); S_span.append(yl - x0 + 1)
    S_tf = np.array(S_tf); S_x0 = np.array(S_x0); S_xl = np.array(S_xl)
    S_brk = np.array(S_brk); S_n = np.array(S_n); S_span = np.array(S_span)
    S_hi = np.array([s == 'hi' for s in S_side])
    NS = len(S_tf)
    print('sequences on all TFs: %d   %.0f s' % (NS, time.time() - t0), flush=True)

    # ---------- THE BREAKER: nearest CAGE-SIDE OOB cross at/before the break, from a rung ABOVE ----------
    best_d = np.full(NS, -10 ** 9); best_tf = np.zeros(NS, np.int32)
    sec_d = np.full(NS, -10 ** 9); sec_tf = np.zeros(NS, np.int32)
    nbefore = np.zeros(NS, np.int32)
    has = S_brk >= 0
    bb = np.where(has, S_brk, 0)
    for tf in LADDER:
        Mg = E[tf]['M']
        oh = np.nan_to_num(Mg, nan=-1e9) >= HI
        ol = np.nan_to_num(Mg, nan=1e9) <= LO
        XH = np.flatnonzero(oh & ~np.r_[False, oh[:-1]])
        XL = np.flatnonzero(ol & ~np.r_[False, ol[:-1]])
        for arr, sidemask in ((XH, S_hi), (XL, ~S_hi)):
            if not len(arr):
                continue
            sel = has & sidemask & (S_tf < tf)          # a HIGHER rung, cage side, sequence has a break
            if not sel.any():
                continue
            i = np.searchsorted(arr, bb, side='right') - 1     # last cross at or before the break
            ok = sel & (i >= 0)
            if not ok.any():
                continue
            dd = np.where(ok, arr[np.clip(i, 0, len(arr) - 1)] - bb, -10 ** 9)   # <= 0
            nbefore += ok.astype(np.int32)
            up = ok & (dd > best_d)
            sec_d = np.where(up, best_d, np.where(ok & (dd > sec_d), dd, sec_d))
            sec_tf = np.where(up, best_tf, np.where(ok & (dd > sec_d) & ~up, np.int32(tf), sec_tf))
            best_d = np.where(up, dd, best_d); best_tf = np.where(up, np.int32(tf), best_tf)
    print('breaker search done   %.0f s' % (time.time() - t0), flush=True)

    # ---------- rows ----------
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute(DDL_T % SUF if '%s' in DDL_T else DDL_T)
    d.execute(DDL_SE_T % SUF if '%s' in DDL_SE_T else DDL_SE_T)
    d.execute('DELETE FROM rpl_bob2%s' % SUF); d.execute('DELETE FROM rpl_s6exh2%s' % SUF)
    rows = []
    for q in range(NS):
        tf = int(S_tf[q]); x0 = int(S_x0[q]); brk = int(S_brk[q]); side = 'hi' if S_hi[q] else 'lo'
        Mg = E[tf]['M']
        seg = Mg[x0:(brk if brk >= 0 else n)]; seg = seg[np.isfinite(seg)]
        bt = int(best_tf[q]) or None
        smp = [None] * MOMO_SAMPLES; sl = r2 = bkm = None; bkst = None
        if bt:
            Bm = E[bt]['M']
            idx = x0 - np.arange(MOMO_SAMPLES - 1, -1, -1) * MOMO_STEP_BARS
            smp = [float(Bm[i]) if i >= 0 and np.isfinite(Bm[i]) else None for i in idx]
            g = [z for z in smp if z is not None]
            if len(g) == MOMO_SAMPLES:
                xx = np.arange(MOMO_SAMPLES, dtype=float); yy = np.array(g)
                a1, a0 = np.polyfit(xx, yy, 1)
                res = ((yy - (a1 * xx + a0)) ** 2).sum(); tot = ((yy - yy.mean()) ** 2).sum()
                sl = float(a1); r2 = float(1 - res / tot) if tot > 1e-12 else None
            if np.isfinite(Bm[x0]):
                bkm = float(Bm[x0])
                bkst = 'hi' if bkm >= HI else ('lo' if bkm <= LO else 'ib')
        rows.append(tuple([tf, side, 1 if side == 'hi' else -1, int(ts[x0]), u(ts[x0]), int(ts[S_xl[q]]),
                           int(ts[brk]) if brk >= 0 else None, u(ts[brk]) if brk >= 0 else None,
                           int(brk - x0) if brk >= 0 else None, int(S_n[q]), int(S_span[q]),
                           float(Mg[x0]) if np.isfinite(Mg[x0]) else None,
                           float(seg.min()) if len(seg) else None, float(seg.max()) if len(seg) else None,
                           float(px[x0]) if np.isfinite(px[x0]) else None,
                           float(px[brk]) if brk >= 0 and np.isfinite(px[brk]) else None,
                           float((1 if side == 'hi' else -1) * (px[brk] - px[x0]) / px[x0] * 100.0)
                           if brk >= 0 and np.isfinite(px[x0]) else None,
                           bt, int(best_d[q]) if bt else None, bkm, bkst, sl, r2,
                           int(sec_tf[q]) or None, int(sec_d[q]) if int(sec_tf[q]) else None,
                           float(E[int(sec_tf[q])]['M'][x0]) if int(sec_tf[q]) and
                           np.isfinite(E[int(sec_tf[q])]['M'][x0]) else None,
                           int(nbefore[q])] + smp))
    cols = ('b2_tf,b2_side,b2_dr,b2_start_ms,b2_start_utc,b2_last_ms,b2_break_ms,b2_break_utc,'
            'b2_break_bars,b2_n_exc,b2_span_bars,b2_mage_at_start,b2_mage_min,b2_mage_max,b2_px_start,'
            'b2_px_break,b2_ret_to_break,bk_tf,bk_dbrk,bk_mage,bk_state,bk_slope,bk_r2,bk2_tf,bk2_dbrk,'
            'bk2_mage,bk_n_before,' + ','.join(SC))
    d.executemany('INSERT INTO rpl_bob2' + SUF + ' (%s) VALUES (%s)' % (cols, ','.join(['%s'] * (27 + MOMO_SAMPLES))),
                  rows, chunk=3000)
    print('rpl_bob2'+SUF+' %d rows   %.0f s' % (len(rows), time.time() - t0), flush=True)

    # ---------- s6Mage EXHAUSTION, CORRECTED EVENT ----------
    # s4m = MINI bb 6|0.45 @TF4. Event: s4m crosses UP through LO while s4Mage(0.70) is STILL lo-OOB.
    # Mirrored: s4m crosses DOWN through HI while s4Mage is still hi-OOB.
    cau = _Causal(None); X6 = E[6]['x']; s4m = E[4]['m']
    dd6 = X6 - M6
    OH6 = (X6 >= HI) & (M6 >= HI); OL6 = (X6 <= LO) & (M6 <= LO)
    cdn = cau.cross_wob(dd6, 0.0, -1, WOB); cup = cau.cross_wob(dd6, 0.0, 1, WOB)
    EV = {1: np.flatnonzero((cdn & ~np.r_[False, cdn[:-1]]) & OH6),
          -1: np.flatnonzero((cup & ~np.r_[False, cup[:-1]]) & OL6)}

    def outcome(x, sgn):
        nz = EV[sgn][EV[sgn] > x]
        e = int(nz[0]) if len(nz) else (n - 1)
        p0 = px[x]; sg = px[x + 1:e + 1]
        if not len(sg) or not np.isfinite(p0):
            return None
        return dict(e=e, p0=float(p0), ret=float(sgn * (px[e] - p0) / p0 * 100.0),
                    mae=float(abs(min(0.0, sgn * ((sg.min() if sgn > 0 else sg.max()) - p0) / p0 * 100.0))),
                    mfe=float(max(0.0, sgn * ((sg.max() if sgn > 0 else sg.min()) - p0) / p0 * 100.0)))

    runlen = lambda m: (np.arange(len(m)) + 1) - np.maximum.accumulate(
        np.where(m, 0, np.arange(len(m)) + 1))
    A4 = {1: np.nan_to_num(M4, nan=-1e9) >= HI, -1: np.nan_to_num(M4, nan=1e9) <= LO}
    m4o = {1: np.nan_to_num(s4m, nan=-1e9) >= HI, -1: np.nan_to_num(s4m, nan=1e9) <= LO}
    ib6 = (M6 > LO) & (M6 < HI)
    se = []
    # cage lo -> s4m crosses UP through LO (leaves lo OOB) while s4Mage still lo-OOB : sgn_cage = -1
    for cage in (-1, 1):
        m = m4o[cage]
        leave = np.flatnonzero((~m) & np.r_[False, m[:-1]])          # rising edge of "no longer OOB"
        for b in leave:
            b = int(b)
            if int(ts[b]) < WIN0 or (WIN1 and int(ts[b]) >= WIN1) or not A4[cage][b]:   # s4Mage STILL OOB
                continue
            if not np.isfinite(M6[b]):
                continue
            rev = -cage                                              # reverse = the way s4m is spiking
            ro = outcome(b, rev); co = outcome(b, cage)
            if not ro or not co:
                continue
            se.append((int(ts[b]), u(ts[b]), 'hi' if cage > 0 else 'lo', cage,
                       float(s4m[b]), float(M4[b]), float(M6[b]), float(X6[b]), float(px[b]),
                       int(runlen(m)[b - 1]) if b else 0, int(runlen(A4[cage])[b]), int(bool(ib6[b])),
                       int(ts[ro['e']]), int(ro['e'] - b), ro['ret'], ro['mae'], ro['mfe'],
                       int(ts[co['e']]), int(co['e'] - b), co['ret'], co['mae'], co['mfe'],
                       None, None, None))
    d.executemany('INSERT IGNORE INTO rpl_s6exh2' + SUF + ' (sx_ms,sx_utc,sx_side,sx_dr,sx_s4m,sx_s4mage,sx_s6mage,'
                  'sx_s6x,sx_px,sx_s4m_oob_bars,sx_s4mage_oob_bars,sx_s6_ib,sx_rev_exit_ms,sx_rev_hold,'
                  'sx_rev_ret,sx_rev_mae,sx_rev_mfe,sx_con_exit_ms,sx_con_hold,sx_con_ret,sx_con_mae,'
                  'sx_con_mfe,sx_kills_ms,sx_kills_ret,sx_kills_ret_at_event) VALUES (%s)'
                  % ','.join(['%s'] * 25), sorted(se), chunk=2000)
    print('rpl_s6exh2'+SUF+' %d rows (s6 IB: %d)   total %.0f s'
          % (len(se), sum(1 for z in se if z[11]), time.time() - t0), flush=True)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
