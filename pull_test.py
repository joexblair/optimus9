"""pull_test — which HTF lines reach Joe's reversal targets in ONE STRAIGHT LINE. Joe 0803 06:00.

    Joe: "lines that I see pulling s4M out to the rev targets (note there will be more than one TF
    creating the same pull):
        01:08 to 01:24  s22Mage
        04:44           s30Mage
        14:04           s60Mage
        18:52           s22Mage
     for a HTF line to be classified as 'pulling s4M out', it must hit the target time in one straight
     line (no bobbing)"

THE TEST. His criterion is a straightness condition, so it is measurable without any trade:

    STRAIGHTNESS = R-squared of a linear fit over the approach to the target, SIGNED by the direction
                   of the net move. 1.000 = a straight line; 0 = no trend.

    A FIRST VERSION USED |net| / sum|bar-to-bar| AND WAS WRONG. On the 5 s grid the bar-to-bar noise
    dominates the denominator, so a perfectly trending line scored 0.1-0.3 and nothing separated. R2 is
    scale-free and immune to the sampling rate, which is what "one straight line" actually means.

Every candidate HTF Mage is measured into each of his four targets over a swept approach window. If his
rule is real, the lines he named score near 1.0 and the ones he did not score lower.

THE s30Mage AMBIGUITY, RESOLVED BY MEASUREMENT NOT BY GUESS. "s30Mage" at 04:44 sits between s22Mage and
s60Mage, which reads as 30 MINUTES — but s30 has meant 30 SECONDS everywhere else in this project. Both
are measured; whichever comes in straight is the one he meant.

LINE SPEC — Joe 0803: s5/s6/gcs15/s30 all use bb 37 | 0.83 | close. Applied to every candidate here.

    python3 pull_test.py
    python3 pull_test.py --wins 60,180,360,720
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
D0 = dt.datetime(2026, 7, 31, tzinfo=dt.timezone.utc)

# every candidate. 's30sec' and 's30min' are both present precisely because Joe's label is ambiguous.
CAND = [('s5', 5.0), ('s6', 6.0), ('s8', 8.0), ('s10', 10.0), ('s12', 12.0), ('s15', 15.0),
        ('s18', 18.0), ('s22', 22.0), ('s30min', 30.0), ('s45', 45.0), ('s60', 60.0), ('s90', 90.0),
        ('s30sec', 0.5), ('gcs15', 0.25)]
# Joe's labelled reversal targets on 07-31, and the line he named for each
TARGETS = [('01:08', 's22'), ('01:24', 's22'), ('04:44', 's30min?'), ('14:04', 's60'), ('18:52', 's22')]


def hhmm(s):
    h, m = int(s[:2]), int(s[3:5])
    return int((D0 + dt.timedelta(hours=h, minutes=m)).timestamp() * 1000)


def main(argv):
    wins = [int(x) for x in (argv[argv.index('--wins') + 1].split(',') if '--wins' in argv
                             else '60,180,360,720'.split(','))]
    ovr = {}
    for nm, tf in CAND:
        ovr.update(bbline('c_%s' % nm, tf, length=37, mult=0.83, src='close'))
    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    d.disconnect()
    with Jig(end_ms, hours=int((end_ms - hhmm('00:00')) / 3600000) + 26,
             warmup=J.WIN_WARMUP, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        V = {nm: np.asarray(j.W.line('c_%s' % nm), float) for nm, _ in CAND}
    print('candidates %d   approach windows (bars): %s' % (len(CAND), wins))

    for tgt, named in TARGETS:
        t = hhmm(tgt)
        b = int(np.searchsorted(ts, t))
        print('\n--- target %s   Joe names: %s ---' % (tgt, named))
        print('   %-8s %8s %8s   %s' % ('line', 'val@tgt', 'net', '  '.join('R2@%d' % w for w in wins)))
        rowset = []
        for nm, tf in CAND:
            v = V[nm]
            cells = []
            for w in wins:
                a = max(0, b - w)
                seg = v[a:b + 1]
                if not np.isfinite(seg).all() or len(seg) < 3:
                    cells.append(np.nan); continue
                x = np.arange(len(seg), dtype=float)
                sl, ic = np.polyfit(x, seg, 1)
                res = ((seg - (sl * x + ic)) ** 2).sum(); tot = ((seg - seg.mean()) ** 2).sum()
                r2 = 1 - res / tot if tot > 1e-12 else np.nan
                cells.append(r2 * np.sign(sl))
            net180 = v[b] - v[max(0, b - 180)]
            rowset.append((nm, v[b], net180, cells))
        rowset.sort(key=lambda r: -(np.nanmean(np.abs(r[3])) if np.isfinite(r[3]).any() else -1))
        for nm, val, net, cells in rowset:
            star = ' <<<' if nm.startswith(named.rstrip('?')) else ''
            print('   %-8s %8.1f %+8.1f   %s%s'
                  % (nm, val, net, '  '.join(('%7.3f' % c) if np.isfinite(c) else '      -' for c in cells), star))


if __name__ == '__main__':
    main(sys.argv[1:])
