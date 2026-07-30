"""build_gap_report — multi-TF x-m gap report at each s8 cadence (Joe 0724, smoke v1). SAVED.

SPEC (as I read it — flagged choices marked ★, easy to change):
  At each s8 cadence marker (xm_cross base='s8' wob=6), capture the x-m gap for s4, s12, s15, s22.
  s4 episode mechanic (established ep-ext): episode = the most recent contiguous s4x-OOB run on the MARKER's side
    (long->s4x<=LO / short->s4x>=HI); T* = the episode EXTREME (argmin s4x for long / argmax for short) = one timestamp.
  ★ single timestamp: s4's x-extreme defines T*; s4m is read at T* too (spec wants ONE timestamp for HTF sampling).
  HTF (s12/s15/s22) are NOT given their own (wide) episodes — their x,m are SAMPLED AT T* (avoids s22 engulfing s4 twitches).
  Lines: bb %B, x=len5/mult0.37, m=len6/mult0.45 (★ the hs-sampling mid convention; say if you want trade-cross 0.43).
  ★ LOOKBACK 18min: if no s4x-OOB(side) run within 18min before the marker -> row's captures are NULL
    (18 not 30 so a stale prior twitch can't mask s4x genuinely failing to breach recently).

COLUMNS per marker (value + the diffs):
  gap value  = x - m           (%B percentage-points)                        [gapval_<tf>]
  gap pct    = (x - m)/m * 100  (gap relative to m; NULL if |m|<1)            [gappct_<tf>]
  diff(now,last)     = gapval_now  - gapval_prev_marker   (pp)               [dtime_<tf>]    ★ pp, not %-change
  diff(now, now(s4)) = gapval[tf]  - gapval[s4]  at T*    (pp; s4==0)         [dtf_now_<tf>]  (front, heavy lifter)
  diff(last, last(s4))= prev gapval[tf] - prev gapval[s4] (pp; s4==0)         [dtf_prev_<tf>] (front, heavy lifter)
  raw (far right): x_<tf>, m_<tf> at T*
Smoke window: 06-26 03:00 .. 06-26 09:00.
"""
import sys, time
import numpy as np
from datetime import datetime, timezone, timedelta
import linelab as LL
import optimus9.orchestration.rpl_walk as R
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TFS = ['s4', 's12', 's15', 's22']
WRITE = '--write' in sys.argv
_dayarg = next((a for a in sys.argv[1:] if a[:1].isdigit()), None)   # 'YYYY-MM-DD' -> that full UTC day
if _dayarg:
    _d = datetime.strptime(_dayarg, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    S = int(_d.timestamp() * 1000); E = int((_d + timedelta(days=1)).timestamp() * 1000)
else:                                                               # default: the 06-26 03:00..09:00 smoke slice
    S = int(datetime(2026, 6, 26, 3, 0, tzinfo=timezone.utc).timestamp() * 1000)
    E = int(datetime(2026, 6, 26, 9, 0, tzinfo=timezone.utc).timestamp() * 1000)
LOOKBACK_BARS = int(18 * 60 / 5)     # 18 min (Joe 0724: was 30; shorter so a stale prior s4x twitch can't
                                     # mask s4x genuinely failing to breach recently -> row goes NULL instead)
FMT = lambda ms: time.strftime('%m-%d %H:%M:%S', time.gmtime(ms / 1000))
r2 = lambda v: (None if v is None else round(float(v), 2))


def build():
    cache, ets, epx, names = LL.warm()
    ts = cache.ts
    cad = LL.xm_cross(cache, 's8', wob=6, lookback_tf=3, min_dwell_s=180, align_line=None, start=S, end=E)
    X = {tf: LL.line(cache, tf + 'x') for tf in TFS}
    M = {tf: LL.line(cache, tf + 'm') for tf in TFS}
    s4x = X['s4']

    def s4_extreme(t, bd):
        """T* = the extreme index of the most recent s4x-OOB(side) run at/before t (within LOOKBACK). None if none."""
        i = int(np.searchsorted(ts, t))
        oob = (s4x <= R.LO) if bd == 1 else (s4x >= R.HI)
        j = i
        while j >= 0 and j > i - LOOKBACK_BARS and not oob[j]:
            j -= 1
        if j < 0 or j <= i - LOOKBACK_BARS or not oob[j]:
            return None
        lo = j
        while lo > 0 and oob[lo - 1]:
            lo -= 1
        hi = j
        while hi < len(oob) - 1 and oob[hi + 1]:
            hi += 1
        seg = s4x[lo:hi + 1]
        return (lo + (int(np.argmin(seg)) if bd == 1 else int(np.argmax(seg))))

    rows = []
    prev_gap = None                      # previous marker's {tf: gapval}
    for tms, bd in cad:
        star = s4_extreme(tms, bd)
        row = dict(gr_ts=tms, gr_time=FMT(tms), gr_dir=('long' if bd == 1 else 'short'),
                   gr_ext_ts=(int(ts[star]) if star is not None else None),
                   gr_ext_time=(FMT(ts[star]) if star is not None else None))
        gap = {}
        for tf in TFS:
            if star is None:
                row.update({f'x_{tf}': None, f'm_{tf}': None, f'gapval_{tf}': None, f'gappct_{tf}': None})
                gap[tf] = None
                continue
            x, m = float(X[tf][star]), float(M[tf][star]); g = x - m
            gap[tf] = g
            row[f'x_{tf}'] = r2(x); row[f'm_{tf}'] = r2(m); row[f'gapval_{tf}'] = r2(g)
            row[f'gappct_{tf}'] = (r2(g / m * 100) if abs(m) >= 1 else None)
        g4 = gap['s4']
        for tf in TFS:
            g = gap[tf]
            row[f'dtf_now_{tf}'] = (r2(g - g4) if (g is not None and g4 is not None) else None)        # TF vs s4, now
            pg = prev_gap.get(tf) if prev_gap else None
            row[f'dtime_{tf}'] = (r2(g - pg) if (g is not None and pg is not None) else None)          # now vs last MARKER
            pg4 = prev_gap.get('s4') if prev_gap else None
            row[f'dtf_prev_{tf}'] = (r2(pg - pg4) if (pg is not None and pg4 is not None) else None)   # TF vs s4, last marker
        rows.append(row)
        if star is not None:
            prev_gap = gap
    return rows


# dtf_now_/dtf_prev_ (TF-vs-s4) sit right after gr_dir — the heavy lifters (Joe 0724).
COLS = (['gr_ts', 'gr_time', 'gr_dir']
        + [f'dtf_now_{tf}' for tf in TFS] + [f'dtf_prev_{tf}' for tf in TFS]
        + ['gr_ext_ts', 'gr_ext_time']
        + [f'{p}_{tf}' for tf in TFS for p in ('gapval', 'gappct', 'dtime')]
        + [f'{p}_{tf}' for tf in TFS for p in ('x', 'm')])


def write_db(rows):
    d = DatabaseManager(**get_db_config()); d.connect()
    defs = []
    for c in COLS:
        if c in ('gr_time', 'gr_ext_time', 'gr_dir'):
            defs.append(f'{c} VARCHAR(20)')
        elif c in ('gr_ts', 'gr_ext_ts'):
            defs.append(f'{c} BIGINT')
        else:
            defs.append(f'{c} DOUBLE')
    d.execute('DROP TABLE IF EXISTS gap_report')
    d.execute('CREATE TABLE gap_report (gr_id INT AUTO_INCREMENT PRIMARY KEY, %s)' % ','.join(defs))
    ph = ','.join(['%s'] * len(COLS))
    for r in rows:
        d.execute('INSERT INTO gap_report (%s) VALUES (%s)' % (','.join(COLS), ph), tuple(r.get(c) for c in COLS))
    d.disconnect()
    ncap = sum(1 for r in rows if r['gr_ext_ts'] is not None)
    print('WROTE %d markers (%d with s4 episode / %d null) -> gap_report' % (len(rows), ncap, len(rows) - ncap))


if __name__ == '__main__':
    rows = build()
    print('=== gap report %s .. %s: %d cadence markers ===' % (FMT(S), FMT(E), len(rows)))
    print('marker(dir) | T*(s4 ext) | gapval s4/s12/s15/s22 | dnow(vs s4) s12/s15/s22')
    for r in rows:
        if r['gr_ext_ts'] is None:
            print('  %s %-5s | (no s4 episode in 30min)' % (r['gr_time'][6:], r['gr_dir'])); continue
        gv = lambda tf: ('%+6.1f' % r[f'gapval_{tf}']) if r[f'gapval_{tf}'] is not None else '   -  '
        dn = lambda tf: ('%+6.1f' % r[f'dtf_now_{tf}']) if r[f'dtf_now_{tf}'] is not None else '   -  '
        print('  %s %-5s | %s | %s %s %s %s | %s %s %s' % (
            r['gr_time'][6:], r['gr_dir'], r['gr_ext_time'][6:],
            gv('s4'), gv('s12'), gv('s15'), gv('s22'), dn('s12'), dn('s15'), dn('s22')))
    if WRITE:
        write_db(rows)
