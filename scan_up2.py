"""scan_up2 — the momo CEILING up the Mage ladder, with the level gate swept. Joe 0803 07:00.

    Joe: "maybe 50 is too low of a bar for Mage momo"

HE IS RIGHT AND THE FIRST RUN SHOWS IT. build_exhv2.momo() gates the level at 50, which was set for r
lines. Mage values in the 07-31 traces run 91 to 148, so a 50 gate passes everything: at Joe's 01:08 exit
40 rungs out of 40 read momo. A test everything passes identifies nothing.

    LVL is now SWEPT: 50 / 60 / 70 / 85 / 100. Symmetric about mid-board — a hi bob needs val >= LVL, a
    lo bob needs val <= 100 - LVL. Nothing is picked; every threshold is reported.

WHAT IS REPORTED IS THE CEILING, NOT A PER-LINE VERDICT. Three separate measures have now failed for the
same reason — straightness R2, extreme timing, and per-rung momo — because every Mage is a smoothing of
one price series, so they move together and no absolute per-line test separates them. The CEILING is
relative to the ladder rather than to a line: how far up strength has propagated. In the first run it went
0 of 40 at Joe's 00:40 bob to 40 of 40 at his 01:08 exit, and 23 to 31 on the 02:12 bob.

BOB BARS ARE THE ACTUAL CROSSINGS. The first run read Joe's rounded label times and found s4M at 55.0 for
a "hi oob" bob. Each label now resolves to the nearest real s4Mage OOB crossing, and the offset is printed
so any mismatch is visible rather than silent.

STRENGTH = build_exhv2.momo()'s own slope and R2 at the bar, with the level gate replaced by LVL. Joe's
"sampled line values that indicate strength" is momo's 12-sample fit; only the level bar moves.

LADDER — Joe 0803: step 3 from 120 down to 30, plus the faster rungs he named by hand.
NAMING — the 30-second line is gcs30. s30 here means 30 MINUTES.

    python3 scan_up2.py
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
LVLS = [50, 60, 70, 85, 100]
BOBS = [('00:40', 'hi', ['01:08', '01:24']), ('02:12', 'lo', ['04:44']),
        ('10:16', 'hi', ['10:28']), ('10:48', 'lo', ['12:08']),
        ('13:40', 'lo', ['14:04']), ('16:56', 'hi', ['18:32', '18:52']),
        ('19:28', 'lo', ['19:40'])]


def hhmm(s):
    h, m = int(s[:2]), int(s[3:5])
    return int((D0 + dt.timedelta(hours=h, minutes=m)).timestamp() * 1000)


def main(argv):
    HI, LO = R.HI, R.LO
    ovr = {}
    ovr.update(bbline('m4', 4.0, length=37, mult=0.70, src='close'))
    for tf in LADDER:
        ovr.update(bbline('L%d' % tf, float(tf), length=37, mult=0.83, src='close'))
    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    d.disconnect()
    with Jig(end_ms, hours=int((end_ms - hhmm('00:00')) / 3600000) + 26, warmup=120, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        M4 = np.asarray(j.W.line('m4'), float)
        V = {tf: np.asarray(j.W.line('L%d' % tf), float) for tf in LADDER}
    oob = (M4 >= HI) | (M4 <= LO)
    cross = np.flatnonzero(oob & ~np.r_[False, oob[:-1]])
    print('ladder %d rungs s5..s120   LVL sweep %s   HI/LO %g/%g' % (len(LADDER), LVLS, HI, LO))

    def strength(tf, dr, bar, lvl):
        v = V[tf]
        if not np.isfinite(v[bar]):
            return False
        st, sl, r2, rw = B.momo(v, dr, bar)
        if not (np.isfinite(sl) and np.isfinite(r2)):
            return False
        lvl_ok = (rw >= lvl) if dr > 0 else (rw <= 100 - lvl)
        aligned = (sl > 0) if dr > 0 else (sl < 0)
        return bool(lvl_ok and aligned and r2 >= B.MOMO_R2_MIN)

    for lab, side, exits in BOBS:
        dr = 1 if side == 'hi' else -1
        t = hhmm(lab)
        b0 = int(min(cross, key=lambda z: abs(int(ts[z]) - t)))
        off = (int(ts[b0]) - t) / 60000.0
        print('\n--- s4M %s bob   JOE %s -> actual crossing %s (%+.1f min)   s4M %.1f   JOE exit %s ---'
              % (side, lab, u(ts[b0]), off, M4[b0], ' or '.join(exits)))
        print('   %-12s %7s   %s' % ('bar', 's4M', '  '.join('n@%d / top' % L for L in LVLS)))
        for tag, bar in [('bob', b0)] + [('exit ' + e, int(np.searchsorted(ts, hhmm(e)))) for e in exits]:
            cells = []
            for lvl in LVLS:
                hits = [tf for tf in LADDER if strength(tf, dr, bar, lvl)]
                cells.append('%2d / %s' % (len(hits), ('s%d' % max(hits)) if hits else '-'))
            print('   %-12s %7.1f   %s' % (tag, M4[bar], '   '.join(cells)))


if __name__ == '__main__':
    main(sys.argv[1:])
