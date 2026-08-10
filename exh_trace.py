"""exh_trace — per-episode trace of s4M OOB against s5M/s6M/gcs15M/gcs30M, on Joe's labelled day.

    Joe 0803: "what I really need to know is when to exit, or reverse, after s4Mage has crossed into OOB"

WHY AN EPISODE DEFINITION IS NEEDED FIRST. 07-31 has 189 crossings into OOB and Joe reads 8 episodes.
The 48-bar dwell cuts it to 35, still four times too many. His own note says why: "08:36 to 10:16 grazes
while consolidating. s4M oob dwell needed to gate consolidation". A brief return in-bounds is a GRAZE, not
the end of the excursion.

  EPISODE = an OOB run on one side lasting at least MIN_DWELL bars. Shorter runs are GRAZES and are
            DROPPED. Joe 0803 corrected an inverted first version of this: the graze is a brief poke OUT
            of bounds during consolidation, not a brief return in-bounds.

LINE SPECS — Joe 0803
  s4M     bb 37 | 0.70 | close @ TF 4 min    the walk producer, unchanged
  s5M s6M bb 37 | 0.83 | close @ TF 5 / 6 min
  gcs15M  bb 37 | 0.83 | close @ TF 0.25 min = 15 s
  gcs30M  bb 37 | 0.83 | close @ TF 0.5 min = 30 s  (Joe 0803: relabelled from s30)

JOE'S TWO IDEAS, traced not assumed
  1  s5M/s6M CONFLUENCE vs REJECTION of s4M. gap = s4M - s6M signed toward the OOB side: positive means
     s4M is further out than s6M, i.e. NOT mirrored.
  2  gcs15M/gcs30M WEAKNESS: they bob on the same side while s4M holds, then bounce past 50 the other way.
     mid-cross = the bar where gcs15M or gcs30M crosses 50 against the episode side.

The trace prints one block per episode with Joe's labelled exit marked, so the two can be read against
each other rather than scored before the event is agreed.

    python3 exh_trace.py                 # MIN_DWELL 48 bars = 240 s
    python3 exh_trace.py --dwell 120
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
W0 = int(dt.datetime(2026, 7, 31, 0, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)
W1 = int(dt.datetime(2026, 8, 1, 0, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)
JOE = {'00:40': '01:08 or 01:24', '02:12': '04:44', '08:36': 'consolidation, gate it',
       '10:16': '10:28', '10:48': '12:08', '13:40': '14:04', '16:56': '18:32 or 18:52', '19:28': '19:40'}


def episodes(oob_side, min_dwell):
    """Runs of consecutive OOB bars lasting at least `min_dwell`. SHORTER RUNS ARE GRAZES AND ARE DROPPED.

    Joe 0803, correcting me: "this is inverted. consolidation will create small OOB grazes". I had defined
    a graze as a brief return IN-bounds that should not break an episode. It is the opposite — during
    consolidation s4Mage pokes OUT of bounds briefly, and those pokes are not episodes at all. This is his
    own note applied the right way round: "s4M oob dwell needed to gate consolidation"."""
    idx = np.flatnonzero(oob_side)
    if not len(idx):
        return []
    runs = []
    a = idx[0]; prev = idx[0]
    for i in idx[1:]:
        if i != prev + 1:
            runs.append((a, prev)); a = i
        prev = i
    runs.append((a, prev))
    return [(x, y) for x, y in runs if (y - x + 1) >= min_dwell]


def main(argv):
    graze = int(argv[argv.index('--dwell') + 1]) if '--dwell' in argv else 48
    HI, LO = R.HI, R.LO
    ovr = {}
    ovr.update(bbline('m4', 4.0, length=37, mult=0.70, src='close'))
    for nm, tf in (('m5', 5.0), ('m6', 6.0), ('g15', 0.25), ('gcs30', 0.5)):
        ovr.update(bbline(nm, tf, length=37, mult=0.83, src='close'))
    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    d.disconnect()
    with Jig(end_ms, hours=int((end_ms - W0) / 3600000) + 26, warmup=J.WIN_WARMUP, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src'])
        ei = np.flatnonzero(evt)
        px = np.full(len(src), np.nan); px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        f = np.isfinite(px); ix = np.where(f, np.arange(len(px)), 0); np.maximum.accumulate(ix, out=ix)
        px = px[ix]; px[:int(np.argmax(f))] = px[int(np.argmax(f))]
        L = {k: np.asarray(j.W.line(k), float) for k in ('m4', 'm5', 'm6', 'g15', 'gcs30')}
    M4 = L['m4']
    inw = (ts >= W0) & (ts < W1)
    EPS = []
    for side, sgn in (('hi', 1), ('lo', -1)):
        o = (M4 >= HI) if side == 'hi' else (M4 <= LO)
        for a, b in episodes(o, graze):
            if inw[a]:
                EPS.append((int(a), int(b), side, sgn))
    EPS.sort()
    print('MIN_DWELL %d bars = %d s   episodes in window: %d   (Joe reads 8)' % (graze, graze * 5, len(EPS)))
    print('\nBlow-by-blow of each s4Mage OOB episode:\n')
    for a, b, side, sgn in EPS:
        dur = (b - a) * 5 / 60.0
        lab = JOE.get(u(ts[a])[:5], '')
        print('--- %s   s4M %s OOB   %.1f min   ends %s%s ---'
              % (u(ts[a]), side, dur, u(ts[b]), ('   JOE: exit ' + lab) if lab else ''))
        step = max(1, (b - a) // 8)
        print('   %-9s %7s %7s %7s %7s %7s %8s %9s'
              % ('utc', 's4M', 's5M', 's6M', 'gcs15M', 'gcs30M', 'gap4-6', 'pxs'))
        for i in range(a, b + 1, step):
            gap = sgn * (M4[i] - L['m6'][i])
            print('   %-9s %7.1f %7.1f %7.1f %7.1f %7.1f %+8.1f %9.6f'
                  % (u(ts[i]), M4[i], L['m5'][i], L['m6'][i], L['g15'][i], L['gcs30'][i], gap, px[i]))
        seg5 = sgn * (M4[a:b + 1] - L['m5'][a:b + 1]); seg6 = sgn * (M4[a:b + 1] - L['m6'][a:b + 1])
        g15 = L['g15'][a:b + 1]; s30 = L['gcs30'][a:b + 1]
        midx = np.flatnonzero((g15 - 50) * sgn < 0)
        mids = np.flatnonzero((s30 - 50) * sgn < 0)
        print('   gap s4-s5: entry %+.1f  min %+.1f  max %+.1f  exit %+.1f'
              % (seg5[0], seg5.min(), seg5.max(), seg5[-1]))
        print('   gap s4-s6: entry %+.1f  min %+.1f  max %+.1f  exit %+.1f'
              % (seg6[0], seg6.min(), seg6.max(), seg6[-1]))
        print('   gcs15M first crosses 50 against the side at %s   gcs30M at %s'
              % (u(ts[a + midx[0]]) if len(midx) else 'never',
                 u(ts[a + mids[0]]) if len(mids) else 'never'))
        print()


if __name__ == '__main__':
    main(sys.argv[1:])
