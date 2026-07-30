"""build_trade_report_hs60 — the hs60-confluence trade report (Joe 0724). SAVED so it survives compaction.

Mechanics stack (Joe-confirmed):
  1. Trade signal = xm_cross(BASE): {B}x×{B}m wob=8 → side-specific sustained-OOB dwell (min_dwell=180s,
     LONG needs {B}m held LO-OOB / SHORT HI-OOB) → opposite-side guard → align gate [s8m, hs30m] both-OOB same-side.
  2. Cadence = xm_cross(base='s8', wob=6): s8x×s8m, SAME dwell+guard OOB logic, wob dialed to 6. hs60 sampling clock.
  3. Weakness sample: at each trade, the last s8 cadence marker → hs60x, hs60m, |x-50|, |m-50|, gap=|x-50|-|m-50|.
  4. episode = span where hs60x is OOB on the trade-side (LONG→LO / SHORT→HI) containing that cadence; ep-ext =
     min(LONG)/max(SHORT) of each of the 5 values independently over that episode's cadence marks. NULL if the
     last cadence's hs60x is not OOB on the trade's favourable side.
  5. MAE/MFE = linelab.mae (find_pivots on px_smooth event bars — the sweep's _leg_net basis).

TRADE CROSS band swapped s11 -> s9 (Joe 0724). Cadence stays s8.
"""
import sys, time
import numpy as np
from datetime import datetime, timezone
import linelab as LL
import optimus9.orchestration.rpl_walk as R
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

BASE  = sys.argv[1] if len(sys.argv) > 1 else 's9'      # trade-cross band
WRITE = '--write' in sys.argv
S = int(datetime(2026, 6, 25, 12, 0, tzinfo=timezone.utc).timestamp() * 1000)
E = int(datetime(2026, 6, 27,  0, 0, tzinfo=timezone.utc).timestamp() * 1000)
FMT = lambda ms: time.strftime('%m-%d %H:%M', time.gmtime(ms / 1000))


def build(base):
    cache, ets, epx, names = LL.warm()
    ts = cache.ts
    trades = LL.xm_cross(cache, base, wob=8, lookback_tf=3, min_dwell_s=180,
                         align_line=['s8m', 'hs30m'], start=S, end=E)
    cad = LL.xm_cross(cache, 's8', wob=6, lookback_tf=3, min_dwell_s=180,
                      align_line=None, start=S, end=E)
    cad_ts = np.array([t for t, _ in cad], dtype=np.int64)
    maes = LL.mae(ets, epx, trades, swing_pct=1.0)
    hx = LL.line(cache, 'hs60x'); hm = LL.line(cache, 'hs60m')

    rows = []
    for (tms, bd), (_, drx, mae, mfe) in zip(trades, maes):
        prev = cad_ts[cad_ts <= tms]
        lastcad = int(prev[-1]) if len(prev) else None
        row = dict(tr_ts=tms, tr_time=FMT(tms), tr_dir=('long' if bd == 1 else 'short'),
                   tr_mae=round(mae, 4), tr_mfe=round(mfe, 4),
                   tr_lastcad=(FMT(lastcad) if lastcad else None),
                   tr_hs60x=None, tr_hs60m=None, tr_dx=None, tr_dm=None, tr_gap=None,
                   tr_epx=None, tr_epm=None, tr_epdx=None, tr_epdm=None, tr_epgap=None)
        if lastcad is not None:
            ci = int(np.searchsorted(ts, lastcad))
            x, m = float(hx[ci]), float(hm[ci])
            dx, dm = abs(x - 50), abs(m - 50); gap = dx - dm
            row.update(tr_hs60x=round(x, 2), tr_hs60m=round(m, 2),
                       tr_dx=round(dx, 2), tr_dm=round(dm, 2), tr_gap=round(gap, 2))
            oob = (hx <= R.LO) if bd == 1 else (hx >= R.HI)   # trade-side favourable OOB
            if oob[ci]:
                lo = ci
                while lo > 0 and oob[lo - 1]:
                    lo -= 1
                hi = ci
                while hi < len(oob) - 1 and oob[hi + 1]:
                    hi += 1
                inep = cad_ts[(cad_ts >= ts[lo]) & (cad_ts <= ts[hi])]
                eci = np.searchsorted(ts, inep)
                exs, ems = hx[eci], hm[eci]
                agg = np.min if bd == 1 else np.max          # LO-OOB episode -> MIN raw; HI-OOB -> MAX raw
                ex, em = float(agg(exs)), float(agg(ems))    # aggregate the RAW x,m ONLY (pre-gap), Joe 0724:
                edx, edm = abs(ex - 50), abs(em - 50)         #   the deepest x,m show 'true nature' before the calc
                row.update(tr_epx=round(ex, 2), tr_epm=round(em, 2),   # distances DERIVED from the aggregated raws
                           tr_epdx=round(edx, 2), tr_epdm=round(edm, 2), tr_epgap=round(edx - edm, 2))
        rows.append(row)
    return rows


def validate_vs_db(rows):
    d = DatabaseManager(**get_db_config()); d.connect()
    db = {r['tr_ts']: r for r in d.execute('SELECT * FROM trade_report_hs60', fetch=True)}
    d.disconnect()
    cols = ['tr_time', 'tr_dir', 'tr_lastcad', 'tr_hs60x', 'tr_hs60m', 'tr_dx', 'tr_dm', 'tr_gap',
            'tr_epx', 'tr_epm', 'tr_epdx', 'tr_epdm', 'tr_epgap', 'tr_mae', 'tr_mfe']
    print('reconstructed %d rows | db %d rows' % (len(rows), len(db)))
    miss = [r['tr_ts'] for r in rows if r['tr_ts'] not in db]
    print('ts not in db:', len(miss))
    ncells = nbad = 0
    for r in rows:
        b = db.get(r['tr_ts'])
        if not b:
            continue
        for c in cols:
            rv, bv = r[c], b[c]
            ncells += 1
            if isinstance(rv, float) or isinstance(bv, (float, int)) and c not in ():
                ok = (rv is None and bv is None) or (rv is not None and bv is not None and abs(float(rv) - float(bv)) <= 0.02)
            else:
                ok = (rv == bv)
            if not ok:
                nbad += 1
                if nbad <= 12:
                    print('  MISMATCH %s %s: recon=%s db=%s' % (r['tr_time'], c, rv, bv))
    print('cells %d | mismatches %d | match %.1f%%' % (ncells, nbad, 100 * (ncells - nbad) / max(ncells, 1)))


def write_db(rows):
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute('DELETE FROM trade_report_hs60')
    cols = ['tr_ts', 'tr_time', 'tr_dir', 'tr_mae', 'tr_mfe', 'tr_lastcad', 'tr_hs60x', 'tr_hs60m',
            'tr_dx', 'tr_dm', 'tr_gap', 'tr_epx', 'tr_epm', 'tr_epdx', 'tr_epdm', 'tr_epgap']
    ph = ','.join(['%s'] * len(cols))
    for r in rows:
        d.execute('INSERT INTO trade_report_hs60 (%s) VALUES (%s)' % (','.join(cols), ph),
                  tuple(r[c] for c in cols))
    d.disconnect()
    nl = sum(1 for r in rows if r['tr_dir'] == 'long')
    nep = sum(1 for r in rows if r['tr_epx'] is not None)
    print('WROTE %d rows (long %d / short %d) | %d with ep-ext -> trade_report_hs60' % (len(rows), nl, len(rows) - nl, nep))


if __name__ == '__main__':
    rows = build(BASE)
    print('=== build base=%s: %d trades ===' % (BASE, len(rows)))
    if BASE == 's11' and not WRITE:
        validate_vs_db(rows)
    if WRITE:
        write_db(rows)
