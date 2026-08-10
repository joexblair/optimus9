"""scan_rcross — the momo bar as MAGE CROSSING r TOWARDS BIAS, up the ladder. Joe 0803 07:20.

    Joe: "maybe the momo bar is Mage crossing r towards bias?"

WHY THIS IS THE RIGHT SHAPE OF TEST. Three measures have failed tonight for one reason: straightness R2,
extreme timing, and per-rung momo at a level gate. Every Mage is a smoothing of the same price series, so
they move together and no ABSOLUTE per-line test separates them — at Joe's 01:08 exit, 40 rungs out of 40
read momo. Mage-against-its-own-r is RELATIVE: it compares two different transforms of the same TF, so
co-movement across the ladder is no longer the thing being measured.

THE TEST, per rung
    hi bob (bias up)   Mage > r          — the band has crossed above its own oscillator
    lo bob (bias down) Mage < r
Both the STATE (which side it is on now) and the EVENT (bars since it crossed that way) are reported, so
"crossing" can be read either as a condition or as a moment without me choosing which Joe meant.

LINES, per rung
    Mage  bb 37 | 0.83 | close             Joe 0803
    r     R.LN['r'] = kline k_len 7, rsi 5, stc 11, close    the generic r spec at that TF
LADDER — Joe 0803: step 3 from 120 down to 30, plus the faster rungs he named. 40 rungs, 80 lines.
NAMING — the 30-second line is gcs30. s30 here means 30 MINUTES.

MEMORY. scan_up.py held 14.7 GB with 40 lines because the window ran from Joe's day to NOW with a 120 h
warmup. This ends at 08-01 00:00 — the end of Joe's own window — with warmup 60 h, giving a 144 h span
that still covers the 74 h a 37-bar Bollinger needs at a 2 h bar. Half the bars, twice the lines.

    python3 scan_rcross.py
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
D0 = dt.datetime(2026, 7, 31, tzinfo=dt.timezone.utc)
W1 = int(dt.datetime(2026, 8, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
LADDER = [5, 6, 8, 10, 12, 15, 18, 22, 25] + list(range(30, 121, 3))
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
        ovr.update(bbline('M%d' % tf, float(tf), length=37, mult=0.83, src='close'))
        ovr.update(R._mk('r%d' % tf, float(tf), R.LN['r']))
    with Jig(W1, hours=24, warmup=60, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        M4 = np.asarray(j.W.line('m4'), float)
        MG = {tf: np.asarray(j.W.line('M%d' % tf), float) for tf in LADDER}
        RR = {tf: np.asarray(j.W.line('r%d' % tf), float) for tf in LADDER}
    n = len(ts)
    print('bars %d   ladder %d rungs (%d lines)   HI/LO %g/%g' % (n, len(LADDER), 2 * len(LADDER), HI, LO))
    fin = {tf: int(np.isfinite(MG[tf]).sum()) for tf in (108, 114, 120)}
    print('finite Mage bars: s108 %d  s114 %d  s120 %d' % (fin[108], fin[114], fin[120]))

    # bars since the Mage last crossed r in each direction, per rung
    AGE = {}
    for tf in LADDER:
        dd = MG[tf] - RR[tf]
        sg = np.sign(np.nan_to_num(dd, nan=0.0))
        up = np.r_[False, (sg[1:] > 0) & (sg[:-1] <= 0)]
        dn = np.r_[False, (sg[1:] < 0) & (sg[:-1] >= 0)]
        idx = np.arange(n)
        for tag, ev in (('up', up), ('dn', dn)):
            last = np.maximum.accumulate(np.where(ev, idx, -1))
            AGE[(tf, tag)] = np.where(last >= 0, idx - last, -1)

    oob = (M4 >= HI) | (M4 <= LO)
    cross = np.flatnonzero(oob & ~np.r_[False, oob[:-1]])
    for lab, side, exits in BOBS:
        dr = 1 if side == 'hi' else -1
        tag = 'up' if dr > 0 else 'dn'
        t = hhmm(lab)
        inwin = [z for z in cross if ts[z] >= ts[0]]
        b0 = int(min(inwin, key=lambda z: abs(int(ts[z]) - t)))
        print('\n--- s4M %s bob  JOE %s -> crossing %s (%+.1f min)  s4M %.1f  JOE exit %s ---'
              % (side, lab, u(ts[b0]), (int(ts[b0]) - t) / 60000.0, M4[b0], ' or '.join(exits)))
        print('   %-12s %7s %6s %-8s %s' % ('bar', 's4M', 'n/40', 'top', 'rungs where Mage is past r toward bias'))
        for nm, bar in [('bob', b0)] + [('exit ' + e, int(np.searchsorted(ts, hhmm(e)))) for e in exits]:
            on = [tf for tf in LADDER
                  if np.isfinite(MG[tf][bar]) and np.isfinite(RR[tf][bar])
                  and ((MG[tf][bar] > RR[tf][bar]) if dr > 0 else (MG[tf][bar] < RR[tf][bar]))]
            fresh = [tf for tf in on if 0 <= AGE[(tf, tag)][bar] <= 720]
            print('   %-12s %7.1f %6s %-8s fresh(<60min): %s'
                  % (nm, M4[bar], '%d' % len(on), ('s%d' % max(on)) if on else '-',
                     ','.join('s%d' % t_ for t_ in fresh[:12]) if fresh else 'none'))


if __name__ == '__main__':
    main(sys.argv[1:])
