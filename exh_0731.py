"""exh_0731 — s4Mage OOB episodes on 07-31, against Joe's labelled exit/reverse moments. Joe 0803 04:40.

    Joe: "what I really need to know is when to exit, or reverse, after s4Mage has crossed into OOB.
    if you can create a prediction on a higher TF, then we're on the right track to know when s4Mage is
    exhausted"

THE TARGET CHANGED. Every measurement before this one predicted whether an ENTRY would reach 1.3% with
<=0.65% MAE. This predicts the EXIT: given s4Mage is OOB, when is it exhausted.

JOE'S LABELS, 07-31, his own words, verbatim as given:
    00:40 hi oob -> 01:08 or 01:24
    02:12 lo oob -> 04:44
    08:36 to 10:16   grazes while consolidating. s4M oob dwell needed to gate consolidation
    10:16 hi oob -> 10:28
    10:48 or 10:56 lo oob -> 12:08
    13:40 lo oob -> 14:04
    16:56 hi oob -> 18:32 or 18:52
    19:28 lo oob -> 19:40
These are estimates read off the chart. Step one is to check them against the actual crossings before
anything is modelled on them.

LINE SPECS — Joe 0803: "s5Mage and s6Mage, gcs15 and s30 are all using 37|0.83|close"
    s4M      bb 37 | 0.70 | close @ TF 4 min    the walk producer, build_exhv2.LINE_SPEC['M'] — UNCHANGED
    s5M      bb 37 | 0.83 | close @ TF 5 min
    s6M      bb 37 | 0.83 | close @ TF 6 min
    gcs15M   bb 37 | 0.83 | close @ TF 0.25 min = 15 s
    s30M     bb 37 | 0.83 | close @ TF 0.5 min = 30 s

JOE'S TWO MODEL IDEAS, to be measured against the labels — not assumed
  1  s5M/s6M CONFLUENCE or REJECTION of s4M. Confluence = the s4M OOB moment is matched by 5 and 6.
     Rejection = it is not mirrored, e.g. s4M 92 while s6M 78 — and rejection is the exit/reverse.
  2  gcs15M/s30M WEAKNESS. They bob hi while s4M is hi-OOB, then start to bounce under 50 when s4M
     weakens. The OOB flip is the tell.

    python3 exh_0731.py
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import build_exhv2 as B
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
W0 = int(dt.datetime(2026, 7, 31, 0, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)
W1 = int(dt.datetime(2026, 8, 1, 0, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)

LABELS = [('00:40', 'hi', '01:08 or 01:24'), ('02:12', 'lo', '04:44'),
          ('08:36', '--', 'grazes while consolidating -> dwell gate'),
          ('10:16', 'hi', '10:28'), ('10:48 or 10:56', 'lo', '12:08'),
          ('13:40', 'lo', '14:04'), ('16:56', 'hi', '18:32 or 18:52'), ('19:28', 'lo', '19:40')]


def main(argv):
    HI, LO = R.HI, R.LO
    ovr = {}
    ovr.update(bbline('m4', 4.0, length=37, mult=0.70, src='close'))        # walk producer, 0.70
    ovr.update(bbline('m5', 5.0, length=37, mult=0.83, src='close'))
    ovr.update(bbline('m6', 6.0, length=37, mult=0.83, src='close'))
    ovr.update(bbline('g15', 0.25, length=37, mult=0.83, src='close'))
    ovr.update(bbline('s30', 0.5, length=37, mult=0.83, src='close'))

    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    d.disconnect()
    hours = int((end_ms - W0) / 3600000) + 26
    with Jig(end_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src'])
        ei = np.flatnonzero(evt)
        px = np.full(len(src), np.nan); px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        fin = np.isfinite(px)
        ix = np.where(fin, np.arange(len(px)), 0); np.maximum.accumulate(ix, out=ix)
        px = px[ix]; px[:int(np.argmax(fin))] = px[int(np.argmax(fin))]
        L = {k: np.asarray(j.W.line(k), float) for k in ('m4', 'm5', 'm6', 'g15', 's30')}
    w = (ts >= W0) & (ts < W1)
    print('window %s -> %s   bars in window %d   HI/LO %g/%g'
          % (dt.datetime.utcfromtimestamp(W0 / 1000).strftime('%m-%d %H:%M'),
             dt.datetime.utcfromtimestamp(W1 / 1000).strftime('%m-%d %H:%M'), int(w.sum()), HI, LO))

    M4 = L['m4']
    oob = (M4 >= HI) | (M4 <= LO)
    rise = np.flatnonzero(oob & ~np.r_[False, oob[:-1]])
    rise = [int(z) for z in rise if W0 <= ts[int(z)] < W1]
    QB = set(int(x) for x in np.flatnonzero(B.oob_qualified(M4, HI, LO)))
    # collapse crossings that belong to one episode: an episode ends when M4 comes back in-bounds and
    # STAYS in-bounds for at least DWELL bars. Joe: "s4M oob dwell needed to gate consolidation".
    DWELL = B.WALK_DWELL_BARS
    print('crossings into OOB inside the window: %d   qualified (%d-bar dwell) among them: %d\n'
          % (len(rise), DWELL, sum(1 for z in rise if any((z + k) in QB for k in range(0, DWELL + 1)))))

    print("JOE'S LABELS vs ACTUAL s4M CROSSINGS")
    print('  %-16s %-4s %-24s %s' % ('joe: cross', 'side', 'joe: exit/reverse', 'nearest actual crossing'))
    for lab, side, ex in LABELS:
        first = lab.split(' ')[0]
        hh, mm = int(first[:2]), int(first[3:5])
        t = W0 + (hh * 3600 + mm * 60) * 1000
        if not rise:
            continue
        near = min(rise, key=lambda z: abs(int(ts[z]) - t))
        dm = (int(ts[near]) - t) / 60000.0
        sd = 'hi' if M4[near] >= HI else 'lo'
        q = 'qualified' if any((near + k) in QB for k in range(0, DWELL + 1)) else 'NOT qualified'
        print('  %-16s %-4s %-24s %s  s4M %6.1f  %s  %+.1f min' % (lab, side, ex, u(ts[near]), M4[near], q, dm))

    print('\nALL s4M OOB CROSSINGS IN THE WINDOW')
    print('  %-10s %-4s %8s %8s %8s %8s %8s %10s' % ('utc', 'side', 's4M', 's5M', 's6M', 'gcs15M', 's30M', 'qualified'))
    for z in rise:
        sd = 'hi' if M4[z] >= HI else 'lo'
        q = 'yes' if any((z + k) in QB for k in range(0, DWELL + 1)) else 'no'
        print('  %-10s %-4s %8.1f %8.1f %8.1f %8.1f %8.1f %10s'
              % (u(ts[z]), sd, M4[z], L['m5'][z], L['m6'][z], L['g15'][z], L['s30'][z], q))


if __name__ == '__main__':
    main(sys.argv[1:])
