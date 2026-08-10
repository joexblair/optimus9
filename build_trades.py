"""build_trades — the whole entry/exit/filter pipeline over the FULL tape, banked. Joe 0803 10:30.

    Joe: "do you think this idea has legs? I'm off to bed now so you have the con"

WHY THIS FIRST. Every number in the exit work sits on 07-21..07-31 — ten days, five two-day blocks. Four
separate results tonight looked significant on a short window and inverted on a wider one, so the honest
next step is not another idea, it is the same idea on 75 days. After this, every question is a query.

CHUNKED BUILD. A single Jig over 05-18..08-01 with 20 lines would need ~40 GB (measured: 40 lines over
247k bars held 14.7 GB). It runs in ~13-day windows with 60 h warmup each — enough for the 74 h a 37-bar
Bollinger needs at a 2 h bar — and the excursion records are concatenated. Overlap between windows is
de-duplicated on the entry bar timestamp.

WHAT IS BANKED, one row per s4Mage OOB excursion
  entry     bar, utc, side, direction, pxs
  filters   dwell bars; ALT-strict; ALT-loose50 (same side allowed if s4M traversed past 50 between);
            s1Mage continuous fuzzy-oob hold length before entry
  HTF       per rung 15/22/30/45/60/90/120: Mage value, r value, and the OPPOSED flag
            (Joe's BB-leads-K rule: BB above K reads bullish, so opposed = Mage < r on a long)
  exit      bar at wob 72 with both s6x and s6M out of bounds on the breach side
  outcome   return, MAE, MFE, hold bars
Nothing is filtered at build time. Every filter is a WHERE clause afterwards.

LINES  s4M bb37|0.70@4   s6M bb37|0.70@6   s6x bb5|0.37@6   s1M bb37|0.83@1
       HTF Mage bb37|0.83 at each rung, r = R.LN['r'] at each rung
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
TAPE0 = int(dt.datetime(2026, 5, 18, tzinfo=dt.timezone.utc).timestamp() * 1000)
TAPE1 = int(dt.datetime(2026, 8, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
RUNGS = [15, 22, 30, 45, 60, 90, 120]
DWELL, WOB = 6, 72
CHUNK_H, WARM_H = 13 * 24, 60

DDL = '''CREATE TABLE IF NOT EXISTS rpl_trades (
    tr_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    tr_ms BIGINT, tr_utc VARCHAR(20), tr_side VARCHAR(2), tr_dr TINYINT, tr_px DOUBLE,
    tr_dwell_bars INT, tr_alt_strict TINYINT, tr_alt_loose TINYINT, tr_s1hold INT,
    %s,
    tr_exit_ms BIGINT, tr_exit_utc VARCHAR(20), tr_exit_px DOUBLE, tr_hold_bars INT,
    tr_ret DOUBLE, tr_mae DOUBLE, tr_mfe DOUBLE, tr_no_cross TINYINT,
    UNIQUE KEY (tr_ms), KEY (tr_side), KEY (tr_alt_strict), KEY (tr_s1hold)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''' % ',\n    '.join(
    'tr_m%d DOUBLE, tr_r%d DOUBLE, tr_opp%d TINYINT' % (t, t, t) for t in RUNGS)


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
    idx = np.arange(len(m)); rst = np.where(m, 0, idx + 1)
    return (idx + 1) - np.maximum.accumulate(rst)


def build_chunk(end_ms, hours):
    HI, LO = R.HI, R.LO
    ovr = {}
    ovr.update(bbline('p4', 4.0, length=37, mult=0.70, src='close'))
    ovr.update(bbline('m6', 6.0, length=37, mult=0.70, src='close'))
    ovr.update(bbline('x6', 6.0, length=5, mult=0.37, src='close'))
    ovr.update(bbline('s1b', 1.0, length=37, mult=0.83, src='close'))
    for t in RUNGS:
        ovr.update(bbline('M%d' % t, float(t), length=37, mult=0.83, src='close'))
        ovr.update(R._mk('r%d' % t, float(t), R.LN['r']))
    with Jig(end_ms, hours=hours, warmup=WARM_H, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64); base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src']); ei = np.flatnonzero(evt)
        px = np.full(len(src), np.nan); px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        f = np.isfinite(px); ix = np.where(f, np.arange(len(px)), 0); np.maximum.accumulate(ix, out=ix)
        px = px[ix]; px[:int(np.argmax(f))] = px[int(np.argmax(f))]
        M4 = np.asarray(j.W.line('p4'), float); M6 = np.asarray(j.W.line('m6'), float)
        X6 = np.asarray(j.W.line('x6'), float); S1 = np.asarray(j.W.line('s1b'), float)
        MG = {t: np.asarray(j.W.line('M%d' % t), float) for t in RUNGS}
        RL_ = {t: np.asarray(j.W.line('r%d' % t), float) for t in RUNGS}
    n = len(ts)
    cau = _Causal(None); dd = X6 - M6
    OH = (X6 >= HI) & (M6 >= HI); OL = (X6 <= LO) & (M6 <= LO)
    cdn = cau.cross_wob(dd, 0.0, -1, WOB); cup = cau.cross_wob(dd, 0.0, 1, WOB)
    EV = {1: (cdn & ~np.r_[False, cdn[:-1]]) & OH, -1: (cup & ~np.r_[False, cup[:-1]]) & OL}
    HOLD = {'hi': runlen(S1 >= HI - 15), 'lo': runlen(S1 <= LO + 15)}
    ALLR = []
    for side in ('hi', 'lo'):
        for x, y in runs_of((M4 >= HI) if side == 'hi' else (M4 <= LO)):
            ALLR.append((int(x), int(y), side))
    ALLR.sort()
    QUAL = [r for r in ALLR if (r[1] - r[0] + 1) > DWELL]
    rows = []
    for k, (x, y, side) in enumerate(QUAL):
        sgn = 1 if side == 'hi' else -1
        prev = QUAL[k - 1] if k else None
        alt_s = int(prev is not None and prev[2] != side)
        if prev is None:
            alt_l = 0
        elif prev[2] != side:
            alt_l = 1
        else:
            seg = M4[prev[1]:x + 1]
            alt_l = int((seg < 50).any() if side == 'hi' else (seg > 50).any())
        nz = np.flatnonzero(EV[sgn][x + 1:])
        no_cross = int(not len(nz))
        e = (x + 1 + int(nz[0])) if len(nz) else (n - 1)
        p0 = px[x]; seg = px[x + 1:e + 1]
        if not len(seg):
            continue
        ret = sgn * (px[e] - p0) / p0 * 100.0
        mae = abs(min(0.0, sgn * (seg.min() if sgn > 0 else seg.max()) / p0 * 100.0
                      - sgn * p0 / p0 * 100.0)) if False else abs(min(
            0.0, sgn * ((seg.min() if sgn > 0 else seg.max()) - p0) / p0 * 100.0))
        mfe = max(0.0, sgn * ((seg.max() if sgn > 0 else seg.min()) - p0) / p0 * 100.0)
        htf = []
        for t in RUNGS:
            mv, rv = MG[t][x], RL_[t][x]
            if np.isfinite(mv) and np.isfinite(rv):
                opp = int((mv < rv) if sgn > 0 else (mv > rv))
                htf += [float(mv), float(rv), opp]
            else:
                htf += [None, None, None]
        rows.append(tuple([int(ts[x]), u(ts[x]), side, sgn, float(p0), int(y - x + 1),
                           alt_s, alt_l, int(HOLD[side][x - 1]) if x else 0] + htf +
                          [int(ts[e]), u(ts[e]), float(px[e]), int(e - x),
                           float(ret), float(mae), float(mfe), no_cross]))
    return rows, int(ts[0]), int(ts[-1])


def main(argv):
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute(DDL)
    d.execute('DELETE FROM rpl_trades')
    cols = (['tr_ms', 'tr_utc', 'tr_side', 'tr_dr', 'tr_px', 'tr_dwell_bars', 'tr_alt_strict',
             'tr_alt_loose', 'tr_s1hold'] +
            [c for t in RUNGS for c in ('tr_m%d' % t, 'tr_r%d' % t, 'tr_opp%d' % t)] +
            ['tr_exit_ms', 'tr_exit_utc', 'tr_exit_px', 'tr_hold_bars', 'tr_ret', 'tr_mae',
             'tr_mfe', 'tr_no_cross'])
    sql = ('INSERT IGNORE INTO rpl_trades (%s) VALUES (%s)'
           % (','.join(cols), ','.join(['%s'] * len(cols))))
    t0 = time.time(); tot = 0
    end = TAPE1
    while end > TAPE0:
        hrs = min(CHUNK_H, int((end - TAPE0) / 3600000) + 1)
        print('chunk ending %s   hours %d' % (u(end), hrs), flush=True)
        rows, s0, s1 = build_chunk(end, hrs)
        keep = [r for r in rows if TAPE0 <= r[0] < TAPE1]
        d.executemany(sql, keep, chunk=2000)
        tot += len(keep)
        print('  spans %s -> %s   rows %d   banked so far %d   %.0f s'
              % (u(s0), u(s1), len(keep), tot, time.time() - t0), flush=True)
        end -= CHUNK_H * 3600000
    got = d.execute('SELECT COUNT(*) n, MIN(tr_utc) lo, MAX(tr_utc) hi FROM rpl_trades', fetch=True)[0]
    print('rpl_trades rows %d   %s -> %s   total %.0f s' % (got['n'], got['lo'], got['hi'], time.time() - t0))
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
