"""mfe_0721 — s4Mage OOB excursions 07-21..07-31 with MFE > 0.75% to the next 1% pivot. Joe 0803 07:40.

    Joe: "between 07-21 and 07-31, when every s4Mage crosses into oob and dwells >30 seconds, find the
    number of excursions that are > 0.75 MFE to the swing detect 1% pivot"

DECISIONS, stated
  s4Mage    bb 37 | 0.70 | close @ TF 4 min — the walk producer
  dwell     > 30 s = the OOB run must last MORE THAN 6 bars at the 5 s grid
  direction MFE is measured in the BREACH direction: hi -> up, lo -> down. Joe 0802: "the side s4M
            breaches on is the gauranteed bias direction". No other direction is specified in the ask.
  from      the CROSSING bar. The dwell-satisfied bar (+6) is reported alongside so both are visible.
  to        the next swing_detect.find_pivots(pxs, pct=1.0) pivot at or after the bar. No horizon.
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import build_rpl_jig as J
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.swing_detect import find_pivots
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
u = lambda m: dt.datetime.fromtimestamp(int(m)/1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
W0 = int(dt.datetime(2026,7,21,tzinfo=dt.timezone.utc).timestamp()*1000)
W1 = int(dt.datetime(2026,7,31,tzinfo=dt.timezone.utc).timestamp()*1000)
DWELL, PCT, BAR = 6, 1.0, 0.75

ovr = {}; ovr.update(bbline('m4', 4.0, length=37, mult=0.70, src='close'))
with Jig(W1, hours=int((W1-W0)/3600000), warmup=24, overrides=ovr) as j:
    ts = np.asarray(j.ts, np.int64); base = j.W.base
    evt = base['volume'].to_numpy(dtype=float) > 0
    src = IC.build_source(base, R.PXS_CFG['src']); ei = np.flatnonzero(evt)
    px = np.full(len(src), np.nan); px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
    f = np.isfinite(px); ix = np.where(f, np.arange(len(px)), 0); np.maximum.accumulate(ix, out=ix)
    px = px[ix]; px[:int(np.argmax(f))] = px[int(np.argmax(f))]
    M4 = np.asarray(j.W.line('m4'), float)
n = len(ts); HI, LO = R.HI, R.LO
piv = find_pivots(px, pct=PCT); pv = np.array([p[0] for p in piv], int)
print('window %s -> %s   bars %d   1%% pivots %d' % (u(W0), u(W1), n, len(pv)))
res = []
for side, sgn in (('hi', 1), ('lo', -1)):
    o = (M4 >= HI) if side == 'hi' else (M4 <= LO)
    idx = np.flatnonzero(o)
    if not len(idx): continue
    runs = []; a = idx[0]; prev = idx[0]
    for i in idx[1:]:
        if i != prev+1: runs.append((a, prev)); a = i
        prev = i
    runs.append((a, prev))
    for x, y in runs:
        if (y - x + 1) <= DWELL: continue          # dwell must EXCEED 30 s
        if not (W0 <= ts[x] < W1): continue
        for tag, b in (('cross', x), ('dwell', min(x+DWELL, n-1))):
            nx = pv[pv > b]
            if not len(nx): continue
            p0 = px[b]; seg = px[b:int(nx[0])+1]
            mfe = ((np.nanmax(seg)-p0) if sgn > 0 else (p0-np.nanmin(seg)))/p0*100.0
            res.append((tag, side, int(ts[x]), (y-x+1)*5, float(mfe)))
for tag in ('cross', 'dwell'):
    R_ = [r for r in res if r[0] == tag]
    m = np.array([r[4] for r in R_])
    print('\nfrom the %s bar   excursions %d   dwell > %d s' % (tag.upper(), len(R_), DWELL*5))
    print('  MFE > %.2f%% : %d  (%.1f%%)' % (BAR, int((m > BAR).sum()), 100*(m > BAR).mean()))
    print('  MFE median %.3f%%   mean %.3f%%   p75 %.3f%%   p90 %.3f%%   max %.3f%%'
          % (np.median(m), m.mean(), np.percentile(m,75), np.percentile(m,90), m.max()))
    for s in ('hi','lo'):
        g = np.array([r[4] for r in R_ if r[1]==s])
        print('  %-3s n %4d   MFE > %.2f%% : %4d (%.1f%%)   median %.3f%%'
              % (s, len(g), BAR, int((g>BAR).sum()), 100*(g>BAR).mean(), np.median(g)))
    dw = np.array([r[3] for r in R_])
    print('  OOB run seconds: median %.0f  p90 %.0f  max %.0f' % (np.median(dw), np.percentile(dw,90), dw.max()))
