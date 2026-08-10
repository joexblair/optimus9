"""scan_up — when s4Mage bobs, scan UPWARD for momo in the Mage ladder. Joe 0803 06:30.

    Joe: "I would look at this in reverse (ie upward). if s4Mage is bobbing hi, scan upwards for `momo` in
    s{scan_target}Mage, (ie >50 and sampled line values that indicate strength)"

    and: "the episode is inconsistent per s4Mage excursion (the bob). measuring them individually and
    manually will give a better feel of the data"

SO NO EPISODE THRESHOLD. The dwell sweep is abandoned as a way to define an episode — Joe's excursions are
not a fixed length and he wants them read one at a time. Each of his eight labelled bobs on 07-31 is
traced individually against the ladder above it.

    Joe's 07-31 labels, verbatim:
        00:40 hi oob -> 01:08 or 01:24
        02:12 lo oob -> 04:44
        08:36 to 10:16   grazes while consolidating
        10:16 hi oob -> 10:28
        10:48 or 10:56 lo oob -> 12:08
        13:40 lo oob -> 14:04
        16:56 hi oob -> 18:32 or 18:52
        19:28 lo oob -> 19:40

THE LADDER — Joe 0803: "h30, h45, h60, h90 <- these were only examples. I think a step=3 sweep during
modelling, from 120min to 30min". So 30,33,...,120 = 31 lines, plus the faster ones he has named by hand
(s5 s6 s8 s10 s12 s15 s18 s22 s25) so the scan is continuous from just above s4.
All bb 37 | 0.83 | close. s4Mage itself stays bb 37 | 0.70.
NAMING — Joe 0803: the 30-SECOND line is `gcs30`. `s30` in this file always means 30 MINUTES.

WHAT IS SCANNED, per ladder rung, at the bob start and at Joe's exit target
    val        the Mage value
    momo       build_exhv2.momo(line, dr, bar) with dr = the bob side. Joe's "momo" is this function:
               a level gate at 50 slackened by tracking quality, plus a slope floor and an R2 floor.
    R2         R-squared of a linear fit over the approach — "1.000 = perfectly monotone", Joe's words.
               Straightness measured this way because |net|/sum|bar-to-bar| on the 5 s grid measures tick
               noise and separated nothing.

TF120 NEEDS 74 h OF WARMUP. bb length 37 at a 2 h bar = 37 x 2 h. build_rpl_jig refuses TF120 for exactly
this reason at its 72 h window. Warmup here is set to 120 h so the top of the ladder is real, not NaN.

    python3 scan_up.py
    python3 scan_up.py --win 360
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_exhv2 as B
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
D0 = dt.datetime(2026, 7, 31, tzinfo=dt.timezone.utc)
LADDER = [5, 6, 8, 10, 12, 15, 18, 22, 25] + list(range(30, 121, 3))
BOBS = [('00:40', 'hi', ['01:08', '01:24']), ('02:12', 'lo', ['04:44']),
        ('10:16', 'hi', ['10:28']), ('10:48', 'lo', ['12:08']),
        ('13:40', 'lo', ['14:04']), ('16:56', 'hi', ['18:32', '18:52']),
        ('19:28', 'lo', ['19:40'])]


def hhmm(s):
    h, m = int(s[:2]), int(s[3:5])
    return int((D0 + dt.timedelta(hours=h, minutes=m)).timestamp() * 1000)


def r2_of(v, b, w):
    a = max(0, b - w)
    seg = v[a:b + 1]
    if len(seg) < 3 or not np.isfinite(seg).all():
        return np.nan, np.nan
    x = np.arange(len(seg), dtype=float)
    sl, ic = np.polyfit(x, seg, 1)
    res = ((seg - (sl * x + ic)) ** 2).sum(); tot = ((seg - seg.mean()) ** 2).sum()
    return (1 - res / tot if tot > 1e-12 else np.nan), sl


def main(argv):
    win = int(argv[argv.index('--win') + 1]) if '--win' in argv else 360     # 360 bars = 30 min
    ovr = {}
    ovr.update(bbline('m4', 4.0, length=37, mult=0.70, src='close'))
    for tf in LADDER:
        ovr.update(bbline('L%d' % tf, float(tf), length=37, mult=0.83, src='close'))
    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    d.disconnect()
    hrs = int((end_ms - hhmm('00:00')) / 3600000) + 26
    with Jig(end_ms, hours=hrs, warmup=120, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        M4 = np.asarray(j.W.line('m4'), float)
        V = {tf: np.asarray(j.W.line('L%d' % tf), float) for tf in LADDER}
    fin = {tf: int(np.isfinite(V[tf]).sum()) for tf in LADDER}
    print('ladder %d rungs  s5..s120   R2 window %d bars = %d min   HI/LO %g/%g'
          % (len(LADDER), win, win * 5 // 60, R.HI, R.LO))
    print('finite bars at the top of the ladder: s108 %d  s114 %d  s120 %d  (of %d)'
          % (fin[108], fin[114], fin[120], len(ts)))

    for start, side, exits in BOBS:
        dr = 1 if side == 'hi' else -1
        b0 = int(np.searchsorted(ts, hhmm(start)))
        print('\n--- s4Mage %s bob from %s   s4M %.1f   JOE exit: %s ---'
              % (side, start, M4[b0], ' or '.join(exits)))
        for tag, bar in [('bob', b0)] + [('exit ' + e, int(np.searchsorted(ts, hhmm(e)))) for e in exits]:
            hits = []
            for tf in LADDER:
                v = V[tf]
                if not np.isfinite(v[bar]):
                    continue
                st, sl, r2m, rw = B.momo(v, dr, bar)
                rr, slope = r2_of(v, bar, win)
                lvl_ok = (rw > 50) if dr > 0 else (rw < 50)
                straight = np.isfinite(rr) and rr >= 0.90 and (slope > 0) == (dr > 0)
                if st == 'momo' or (lvl_ok and straight):
                    hits.append((tf, rw, st, rr, slope))
            print('   %-11s s4M %6.1f   rungs with momo or (level+straight R2>=0.90): %d'
                  % (tag, M4[bar], len(hits)))
            for tf, rw, st, rr, slope in hits[:14]:
                print('        s%-4d val %7.1f  momo %-8s R2 %6.3f  slope %+8.4f' % (tf, rw, st, rr, slope))


if __name__ == '__main__':
    main(sys.argv[1:])
