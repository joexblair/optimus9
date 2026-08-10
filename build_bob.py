"""build_bob — which HTF Mage ends the bobbing, and the s6Mage exhaustion reverse. Joe 0803 17:00.

    Joe: "the scenarios you see here are the definition of bobbing - mage is pegged while it waits for
    whichever higher TF Mage is tracking towards OOB. hypothesis: if we know which HTF Mage(s) break the
    bobbers out of their bearish cage, then we can find the HTF mage's value at the time when we opened
    the trade (ie s4M crossing to OOB). if we have that HTF Mage value, and the 9 momo-test samples before
    it, we can build a model that detects which HTF Mage will end the bobbing, and we get 1) a more
    targetted exit and 2) we stay away from entering trades like 07-28 11:00"

    and: "when s4m spikes up and crosses the low boundary, measure s6Mages value. if s6Mage is IB while
    s4Mage is OOB, then s6Mage is exhausted: exit the trade AND start a new trade in the direction of s4M"

NOTHING IS THRESHOLDED. Every measure is banked raw, per sequence and per rung, so which HTF Mage "breaks
the cage" is a query, not a constant baked in here.

--- BOBBING SEQUENCE (bs) ------------------------------------------------------------------------------
A maximal run of consecutive s4Mage OOB excursions, all the same side, with NO 50-traverse between them.
That is exactly rpl_trades.tr_alt_loose = 0 chained: the run breaks at the first excursion whose
tr_alt_loose = 1 (side flipped, or s4Mage went past 50 in between - Joe 0802). 1,257 sequences on the
tape, mean 4.7 excursions, median 3, max 45; duration median 19 min, max 475 min.
  bs_start  = the FIRST excursion of the run. This is "the time when we opened the trade" (s4M -> OOB).
  bs_break  = the bar s4Mage crosses 50 going away from the cage side. The bob ENDS here.
              Measured on s4Mage directly, not inferred from the next excursion, so a run that ends at
              the tape edge is recorded with bs_break_ms NULL rather than silently dropped.

--- PER-RUNG DETAIL (bh), one row per (sequence x TF), TF = 1..120 --------------------------------------
At bs_start:  bh_mage (the Mage value), bh_state (hi/lo/ib), and the momo fit.
              MOMO SAMPLE COUNT: Joe said "the 9 momo-test samples". build_exhv2.py:42 has
              MOMO_SAMPLES = MOMO_WINDOW_MIN // MOMO_STEP_MIN = 60 // 5 = 12. Nine was the value when the
              window was 45 min. ALL TWELVE are stored as bh_s0..bh_s11 (s11 = the bar itself, s0 =
              55 min back at MOMO_STEP_BARS = 60 bars = 5 min apart), so "9 samples" is the slice
              bh_s3..bh_s11 and neither number is baked in.
Around bs_break: bh_dbrk_hi / bh_dbrk_lo = SIGNED bars from the break bar to this rung's NEAREST Mage
              OOB crossing on each side. Negative = the rung crossed BEFORE the break (a candidate for
              having caused it); positive = after. NULL = that rung never crosses that side on the tape.
              No window, no cap - Joe 0802 standing rule. The "which Mage broke the cage" question is
              then ORDER BY ABS(bh_dbrk_*) in SQL, and the same-side / opposite-side ambiguity Joe left
              open is answered by choosing which column to read.

--- s6Mage EXHAUSTION REVERSE (se) ---------------------------------------------------------------------
Joe's rule reads "when s4m spikes up and crosses the low boundary ... if s6Mage is IB while s4Mage is
OOB". Crossing UP through LO leaves s4Mage IN bounds, which contradicts the second clause, so the event
is taken as s4Mage crossing INTO OOB with s6Mage still in bounds at that bar. BOTH readings are banked:
se_side records which boundary, so lo-only and either-side are both WHERE clauses.
  EVENT   s4Mage crosses into OOB (rising edge of |s4M| past HI/LO) AND s6Mage is IB at that same bar.
  TRADE   entry at the event bar, direction = the s4Mage OOB side (hi -> long, matching rpl_trades.tr_dr).
  EXIT    the same rule the existing pipeline uses: first s6x X s6Mage cross at wob 72 = 360 s with BOTH
          lines OOB on the breach side.
  se_kills_ms = the rpl_trades row this event would have closed (the open trade at that bar), if any.

LINES  s4Mage bb 37|0.70|close @TF4   s6Mage bb 37|0.70|close @TF6   s6x bb 5|0.37|close @TF6 (= L0 x6)
       HTF Mage bb 37|0.83|close at every TF 1..120 = L0's M line.
WINDOW 05-18 -> 07-31. Pre-05-18 is synthetic warmup, never analysis (rpl_walk.py:121, Joe 0729).

    python3 build_bob.py
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
DWELL, WOB = 6, 72                       # entry dwell 6 bars = 30 s;  exit cross wob 72 bars = 360 s
MOMO_STEP_BARS, MOMO_SAMPLES = 60, 12    # build_exhv2.py:41-42 — 60 bars = 5 min, 12 samples = 60 min
LADDER = list(range(1, 121))

DDL_SEQ = '''CREATE TABLE IF NOT EXISTS rpl_bob_seq (
    bs_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    bs_start_ms BIGINT, bs_start_utc VARCHAR(20),
    bs_last_ms  BIGINT, bs_last_utc  VARCHAR(20),
    bs_break_ms BIGINT, bs_break_utc VARCHAR(20), bs_break_bars INT,
    bs_side VARCHAR(2), bs_dr TINYINT,
    bs_n_exc INT, bs_span_bars INT,
    bs_s4m_min DOUBLE, bs_s4m_max DOUBLE, bs_s4m_at_start DOUBLE,
    bs_px_start DOUBLE, bs_px_break DOUBLE, bs_ret_to_break DOUBLE,
    bs_sum_ret DOUBLE, bs_worst_ret DOUBLE, bs_max_mae DOUBLE,
    UNIQUE KEY (bs_start_ms), KEY (bs_side), KEY (bs_n_exc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

DDL_HTF = '''CREATE TABLE IF NOT EXISTS rpl_bob_htf (
    bh_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    bh_seq BIGINT, bh_start_ms BIGINT, bh_tf INT,
    bh_mage DOUBLE, bh_state VARCHAR(2),
    bh_slope DOUBLE, bh_r2 DOUBLE,
    bh_dbrk_hi INT, bh_dbrk_lo INT,
    %s,
    UNIQUE KEY (bh_start_ms, bh_tf), KEY (bh_seq), KEY (bh_tf)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''' % ', '.join('bh_s%d DOUBLE' % k for k in range(MOMO_SAMPLES))

DDL_SE = '''CREATE TABLE IF NOT EXISTS rpl_s6exh (
    se_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    se_ms BIGINT, se_utc VARCHAR(20), se_side VARCHAR(2), se_dr TINYINT,
    se_s4m DOUBLE, se_s6m DOUBLE, se_s6x DOUBLE, se_px DOUBLE,
    se_exit_ms BIGINT, se_exit_utc VARCHAR(20), se_exit_px DOUBLE, se_hold_bars INT,
    se_ret DOUBLE, se_mae DOUBLE, se_mfe DOUBLE, se_no_cross TINYINT,
    se_kills_ms BIGINT, se_kills_ret DOUBLE, se_kills_ret_at_event DOUBLE,
    UNIQUE KEY (se_ms), KEY (se_side)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''


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


def heal(d, table, ddl):
    """CREATE TABLE IF NOT EXISTS does not ADD columns. Precedent build_rpl_jig.py:203-212."""
    d.execute(ddl)
    have = {r['COLUMN_NAME'].lower() for r in d.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
        "AND TABLE_NAME=%s", (table,), fetch=True)}
    body = ddl[ddl.index('(') + 1:ddl.rindex(')')]
    add = 0
    for part in body.split(','):
        p = part.strip()
        if not p or p.upper().startswith(('PRIMARY', 'UNIQUE', 'KEY', 'INDEX')):
            continue
        nm = p.split()[0]
        if nm.lower() not in have and nm.lower().startswith(table.split('_')[-1][:2]):
            d.execute('ALTER TABLE %s ADD COLUMN %s' % (table, p)); add += 1
    return add


def main(argv):
    t0 = time.time()
    L = R.L0; ts = np.asarray(L['ts'], np.int64); n = len(ts); E = L['E']
    print('L0 %d bars  %s -> %s   %.0f s' % (n, u(ts[0]), u(ts[-1]), time.time() - t0), flush=True)

    # --- the 0.70-mult Mages L0 does not carry, on L0's grid ---
    ovr = {}
    ovr.update(bbline('p4', 4.0, length=37, mult=0.70, src='close'))
    ovr.update(bbline('m6', 6.0, length=37, mult=0.70, src='close'))
    end_ms = int(ts[-1]) + 5000
    hrs = int((end_ms - TAPE0) / 3600000) + 2
    with Jig(end_ms, hours=hrs, warmup=180, overrides=ovr) as j:
        t2 = np.asarray(j.ts, np.int64); base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        srcv = IC.build_source(base, R.PXS_CFG['src']); ei = np.flatnonzero(evt)
        px_ = np.full(len(srcv), np.nan); px_[ei] = IC.dema(srcv[ei], int(R.PXS_CFG['len']))
        f = np.isfinite(px_); ixf = np.where(f, np.arange(len(px_)), 0); np.maximum.accumulate(ixf, out=ixf)
        px_ = px_[ixf]; px_[:int(np.argmax(f))] = px_[int(np.argmax(f))]
        M4_ = np.asarray(j.W.line('p4'), float); M6_ = np.asarray(j.W.line('m6'), float)
    off = int(np.searchsorted(ts, int(t2[0]))); k = min(len(t2), n - off)
    if int(ts[off]) != int(t2[0]) or not (ts[off:off + k] == t2[:k]).all():
        raise SystemExit('grid mismatch')
    lift = lambda a: np.concatenate([np.full(off, np.nan), a[:k], np.full(n - off - k, np.nan)])
    px, M4, M6 = lift(px_), lift(M4_), lift(M6_)
    print('fresh lines aligned at offset %d   %.0f s' % (off, time.time() - t0), flush=True)

    # --- exits: s6x X s6Mage at wob 72, both OOB (the pipeline's own rule, unchanged) ---
    cau = _Causal(None); X6 = E[6]['x']; dd = X6 - M6
    OH = (X6 >= HI) & (M6 >= HI); OL = (X6 <= LO) & (M6 <= LO)
    cdn = cau.cross_wob(dd, 0.0, -1, WOB); cup = cau.cross_wob(dd, 0.0, 1, WOB)
    EV = {1: np.flatnonzero((cdn & ~np.r_[False, cdn[:-1]]) & OH),
          -1: np.flatnonzero((cup & ~np.r_[False, cup[:-1]]) & OL)}

    # --- excursions, same definition as build_trades2 ---
    ALLR = []
    for side in ('hi', 'lo'):
        for a, b in runs_of((M4 >= HI) if side == 'hi' else (M4 <= LO)):
            ALLR.append((int(a), int(b), side))
    ALLR.sort()
    QUAL = [r for r in ALLR if (r[1] - r[0] + 1) > DWELL and int(ts[r[0]]) >= TAPE0]
    print('excursions dwell>%d, from %s: %d   %.0f s' % (DWELL, u(TAPE0), len(QUAL), time.time() - t0), flush=True)

    def outcome(x, sgn):
        nz = EV[sgn][EV[sgn] > x]
        e = int(nz[0]) if len(nz) else (n - 1)
        p0 = px[x]; seg = px[x + 1:e + 1]
        if not len(seg) or not np.isfinite(p0):
            return None
        return dict(e=e, p0=float(p0), ret=float(sgn * (px[e] - p0) / p0 * 100.0),
                    mae=float(abs(min(0.0, sgn * ((seg.min() if sgn > 0 else seg.max()) - p0) / p0 * 100.0))),
                    mfe=float(max(0.0, sgn * ((seg.max() if sgn > 0 else seg.min()) - p0) / p0 * 100.0)),
                    no_cross=int(not len(nz)))

    # --- BOBBING SEQUENCES: chain excursions until a 50-traverse or a side flip ---
    seqs = []; cur = [QUAL[0]]
    for i in range(1, len(QUAL)):
        x, y, side = QUAL[i]; px_, py_, pside = QUAL[i - 1]
        if pside != side:
            brk = True
        else:
            seg = M4[py_:x + 1]
            brk = bool((seg < 50).any() if side == 'hi' else (seg > 50).any())
        if brk:
            seqs.append(cur); cur = [QUAL[i]]
        else:
            cur.append(QUAL[i])
    seqs.append(cur)
    print('bobbing sequences: %d   %.0f s' % (len(seqs), time.time() - t0), flush=True)

    # --- per-TF Mage OOB crossing bars, once for the whole ladder ---
    XHI, XLO = {}, {}
    for tf in LADDER:
        Mg = E[tf]['M']
        oh = np.nan_to_num(Mg, nan=-1e9) >= HI
        ol = np.nan_to_num(Mg, nan=1e9) <= LO
        XHI[tf] = np.flatnonzero(oh & ~np.r_[False, oh[:-1]])
        XLO[tf] = np.flatnonzero(ol & ~np.r_[False, ol[:-1]])
    print('ladder OOB-cross index built (%d TFs)   %.0f s' % (len(LADDER), time.time() - t0), flush=True)

    def nearest(arr, b):
        """signed bars from break bar b to the nearest entry of arr; None if arr is empty."""
        if not len(arr):
            return None
        i = int(np.searchsorted(arr, b))
        cand = [int(arr[j]) - b for j in (i - 1, i) if 0 <= j < len(arr)]
        return min(cand, key=abs) if cand else None

    d = DatabaseManager(**get_db_config()); d.connect()
    for tb, ddl in (('rpl_bob_seq', DDL_SEQ), ('rpl_bob_htf', DDL_HTF), ('rpl_s6exh', DDL_SE)):
        a = heal(d, tb, ddl)
        d.execute('DELETE FROM %s' % tb)
        print('  %s ready (%d columns added)' % (tb, a), flush=True)

    SCOLS = ['bh_s%d' % z for z in range(MOMO_SAMPLES)]
    seq_rows, htf_rows = [], []
    for si, sq in enumerate(seqs):
        x0, y0, side = sq[0]; sgn = 1 if side == 'hi' else -1
        xl, yl, _ = sq[-1]
        # THE BREAK: first bar after the last excursion where s4Mage crosses 50 away from the cage side.
        tail = M4[yl:]
        w = np.flatnonzero((tail < 50) if side == 'hi' else (tail > 50))
        bb = int(yl + w[0]) if len(w) else None
        rets = [outcome(x, sgn) for x, y, s in sq]
        rets = [z for z in rets if z]
        seg4 = M4[x0:(bb if bb else n)]
        seg4 = seg4[np.isfinite(seg4)]
        seq_rows.append((int(ts[x0]), u(ts[x0]), int(ts[xl]), u(ts[xl]),
                         int(ts[bb]) if bb else None, u(ts[bb]) if bb else None,
                         int(bb - x0) if bb else None, side, sgn, len(sq), int(yl - x0 + 1),
                         float(seg4.min()) if len(seg4) else None,
                         float(seg4.max()) if len(seg4) else None, float(M4[x0]),
                         float(px[x0]) if np.isfinite(px[x0]) else None,
                         float(px[bb]) if bb and np.isfinite(px[bb]) else None,
                         float(sgn * (px[bb] - px[x0]) / px[x0] * 100.0) if bb and np.isfinite(px[x0]) else None,
                         float(sum(z['ret'] for z in rets)) if rets else None,
                         float(min(z['ret'] for z in rets)) if rets else None,
                         float(max(z['mae'] for z in rets)) if rets else None))
        # per-rung detail at the sequence START (= the trade open bar)
        for tf in LADDER:
            Mg = E[tf]['M']
            v = Mg[x0]
            if not np.isfinite(v):
                continue
            idx = x0 - np.arange(MOMO_SAMPLES - 1, -1, -1) * MOMO_STEP_BARS
            smp = [float(Mg[i]) if i >= 0 and np.isfinite(Mg[i]) else None for i in idx]
            good = [z for z in smp if z is not None]
            if len(good) == MOMO_SAMPLES:
                xx = np.arange(MOMO_SAMPLES, dtype=float); yy = np.array(good)
                sl, ic = np.polyfit(xx, yy, 1)
                res = ((yy - (sl * xx + ic)) ** 2).sum(); tot = ((yy - yy.mean()) ** 2).sum()
                r2 = float(1 - res / tot) if tot > 1e-12 else None
                sl = float(sl)
            else:
                sl = r2 = None
            st = 'hi' if v >= HI else ('lo' if v <= LO else 'ib')
            htf_rows.append(tuple([int(ts[x0]), int(tf), float(v), st, sl, r2,
                                   nearest(XHI[tf], bb) if bb else None,
                                   nearest(XLO[tf], bb) if bb else None] + smp))
    d.executemany(
        'INSERT INTO rpl_bob_seq (bs_start_ms,bs_start_utc,bs_last_ms,bs_last_utc,bs_break_ms,bs_break_utc,'
        'bs_break_bars,bs_side,bs_dr,bs_n_exc,bs_span_bars,bs_s4m_min,bs_s4m_max,bs_s4m_at_start,'
        'bs_px_start,bs_px_break,bs_ret_to_break,bs_sum_ret,bs_worst_ret,bs_max_mae) VALUES (%s)'
        % ','.join(['%s'] * 20), seq_rows, chunk=1000)
    print('rpl_bob_seq %d rows   %.0f s' % (len(seq_rows), time.time() - t0), flush=True)
    d.executemany(
        'INSERT INTO rpl_bob_htf (bh_start_ms,bh_tf,bh_mage,bh_state,bh_slope,bh_r2,bh_dbrk_hi,bh_dbrk_lo,%s)'
        ' VALUES (%s)' % (','.join(SCOLS), ','.join(['%s'] * (8 + MOMO_SAMPLES))), htf_rows, chunk=4000)
    d.execute('UPDATE rpl_bob_htf h JOIN rpl_bob_seq s ON s.bs_start_ms=h.bh_start_ms SET h.bh_seq=s.bs_pk')
    print('rpl_bob_htf %d rows   %.0f s' % (len(htf_rows), time.time() - t0), flush=True)

    # --- s6Mage EXHAUSTION REVERSE ---------------------------------------------------------------
    oob4 = {1: np.nan_to_num(M4, nan=-1e9) >= HI, -1: np.nan_to_num(M4, nan=1e9) <= LO}
    ib6 = (M6 > LO) & (M6 < HI)
    se_rows = []
    opens = sorted((int(z[0]), 1 if z[2] == 'hi' else -1) for z in QUAL)
    for sgn in (1, -1):
        o = oob4[sgn]
        cross = np.flatnonzero(o & ~np.r_[False, o[:-1]])
        for b in cross:
            b = int(b)
            if int(ts[b]) < TAPE0 or not (np.isfinite(M6[b]) and ib6[b]):
                continue
            r = outcome(b, sgn)
            if not r:
                continue
            prior = [z for z in opens if z[0] <= b]
            kms = kret = katev = None
            if prior:
                px0i, psg = prior[-1]
                po = outcome(px0i, psg)
                if po and po['e'] > b:
                    kms = int(ts[px0i]); kret = po['ret']
                    katev = float(psg * (px[b] - px[px0i]) / px[px0i] * 100.0)
            se_rows.append((int(ts[b]), u(ts[b]), 'hi' if sgn > 0 else 'lo', sgn,
                            float(M4[b]), float(M6[b]), float(X6[b]), r['p0'],
                            int(ts[r['e']]), u(ts[r['e']]), float(px[r['e']]), int(r['e'] - b),
                            r['ret'], r['mae'], r['mfe'], r['no_cross'], kms, kret, katev))
    se_rows.sort()
    d.executemany('INSERT IGNORE INTO rpl_s6exh (se_ms,se_utc,se_side,se_dr,se_s4m,se_s6m,se_s6x,se_px,'
                  'se_exit_ms,se_exit_utc,se_exit_px,se_hold_bars,se_ret,se_mae,se_mfe,se_no_cross,'
                  'se_kills_ms,se_kills_ret,se_kills_ret_at_event) VALUES (%s)' % ','.join(['%s'] * 19),
                  se_rows, chunk=2000)
    print('rpl_s6exh %d rows   total %.0f s' % (len(se_rows), time.time() - t0), flush=True)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
