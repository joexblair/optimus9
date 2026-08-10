"""rsd_case — open ONE rsd signal and show why the direction failed. Joe 0802 21:31.

    Joe: "pick one timestamp that didn't correctly predict a direction"

Takes a signal bar from rpl_rsd_24h and rebuilds the same window rsd_s4_24h.py used, then prints:
  1. the 5 rsd rungs + s4Mage at the CROSS bar and at the SIGNAL bar, under both readings
  2. every rung pair and whether it agreed
  3. the price path from the signal bar to the pivot — where it went, when, and whether it ever
     went the predicted way at all
  4. the rungs sampled forward, so the moment the reading would have flipped is visible

Rebuild is a Jig over the same geometry (hours + WARMUP_H, ending at the same kline) so the numbers are
the ones rsd actually read. Nothing is re-derived; the rung specs and DWELL come from rsd_s4_24h.

    python3 rsd_case.py 26                    # by rs_pk
    python3 rsd_case.py 26 --steps 24         # forward samples of the rung table
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from rsd_s4_24h import RUNGS, PAIRS, DWELL, WARMUP_H, _side_lastoob

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')


def main(argv):
    pk = int(argv[0])
    steps = int(argv[argv.index('--steps') + 1]) if '--steps' in argv else 16
    hours = int(argv[argv.index('--hours') + 1]) if '--hours' in argv else 24

    d = DatabaseManager(**get_db_config()); d.connect()
    row = d.execute('SELECT * FROM rpl_rsd_24h WHERE rs_pk=%s', (pk,), fetch=True)[0]
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    d.disconnect()
    HI, LO = R.HI, R.LO

    ovr = {}
    ovr.update(bbline('rsdM4', 4, length=37, mult=0.7, src='close'))
    for nm, tf in RUNGS:
        ovr.update(bbline(nm, tf, length=37, mult=0.7, src='close'))
    with Jig(end_ms, hours=hours, warmup=WARMUP_H, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src'])
        ei = np.flatnonzero(evt)
        px = np.full(len(src), np.nan)
        px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        fin = np.isfinite(px)
        ix = np.where(fin, np.arange(len(px)), 0)
        np.maximum.accumulate(ix, out=ix)
        px = px[ix]; px[:int(np.argmax(fin))] = px[int(np.argmax(fin))]
        M4 = np.asarray(j.W.line('rsdM4'), float)
        V = {nm: np.asarray(j.W.line(nm), float) for nm, _ in RUNGS}
    LAST = {nm: _side_lastoob(V[nm], HI, LO) for nm, _ in RUNGS}
    MID = {nm: np.sign(V[nm] - 50.0).astype(np.int8) for nm, _ in RUNGS}

    zb = int(np.searchsorted(ts, int(row['rs_cross_ms'])))
    sb = int(np.searchsorted(ts, int(row['rs_sig_ms'])))
    pb = int(np.searchsorted(ts, int(row['rs_piv_ms']))) if row['rs_piv_ms'] else len(ts) - 1

    print('== SIGNAL #%d ==' % pk)
    print('  cross  %s   s4Mage %.2f   side %s' % (u(ts[zb]), M4[zb], row['rs_side']))
    print('  signal %s   s4Mage %.2f   +%d bars = %d s   still OOB %d'
          % (u(ts[sb]), M4[sb], DWELL, DWELL * 5, row['rs_still_oob']))
    print('  claim  %s   from pxs %.8f' % (row['rs_dir'], px[sb]))
    print('  pivot  %s %s   %d bars = %.1f min   move %+.3f%%   mae %.3f%%'
          % (u(ts[pb]), row['rs_piv_kind'], pb - sb, row['rs_piv_min'], row['rs_move_pct'], row['rs_mae_pct']))

    print('\n== THE 5 RUNGS AT THE SIGNAL BAR ==')
    print('  %-8s %8s %8s %7s %6s' % ('rung', 'value', 'TF', 'lastoob', 'mid'))
    for nm, tf in RUNGS:
        tfs = '%.2f min' % tf if tf >= 0.25 else '5 s'
        print('  %-8s %8.2f %8s %7d %6d' % (nm, V[nm][sb], tfs, LAST[nm][sb], MID[nm][sb]))
    print('  %-8s %8.2f %8s' % ('rsdM4', M4[sb], '4.00 min'))

    print('\n== THE 4 PAIRS AT THE SIGNAL BAR  (disagree = 1) ==')
    print('  %-16s %9s %6s' % ('pair', 'lastoob', 'mid'))
    for k, (a, b) in enumerate(PAIRS):
        na, nb = RUNGS[a][0], RUNGS[b][0]
        print('  p%d %-13s %9d %6d' % (k, '%s|%s' % (na[3:], nb[3:]),
                                       int(LAST[na][sb] != LAST[nb][sb]), int(MID[na][sb] != MID[nb][sb])))
    print('  lastoob_n %d   mid_n %d' % (row['rs_lastoob_n'], row['rs_mid_n']))

    print('\n== PRICE PATH, signal -> pivot ==')
    seg = px[sb:pb + 1]
    sgn = -1.0 if row['rs_side'] == 'hi' else 1.0
    fav = sgn * (seg - px[sb]) / px[sb] * 100.0
    bi = int(np.nanargmax(fav))
    print('  best FAVOURABLE  %+.3f%%  at %s  (%d bars = %.1f min after the signal)'
          % (fav[bi], u(ts[sb + bi]), bi, bi * 5 / 60.0))
    wi = int(np.nanargmin(fav))
    print('  worst ADVERSE    %+.3f%%  at %s  (%d bars = %.1f min after the signal)'
          % (fav[wi], u(ts[sb + wi]), wi, wi * 5 / 60.0))
    print('  bars favourable  %d / %d = %.1f%%'
          % (int((fav > 0).sum()), len(fav), 100.0 * (fav > 0).sum() / len(fav)))

    print('\n== RUNGS SAMPLED FORWARD FROM THE SIGNAL  (lastoob reading, n = pairs disagreeing) ==')
    span = pb - sb
    step = max(1, span // steps)
    print('  %-11s %8s %8s %8s %8s %8s %8s %5s %9s'
          % ('utc', 'M5', 'M15', 'M30', 'M1', 'M2', 'rsdM4', 'n', 'fav%'))
    for i in range(sb, pb + 1, step):
        n_ = sum(int(LAST[RUNGS[a][0]][i] != LAST[RUNGS[b][0]][i]) for a, b in PAIRS)
        print('  %-11s %8.2f %8.2f %8.2f %8.2f %8.2f %8.2f %5d %+9.3f'
              % (u(ts[i])[6:], V['rsdM5'][i], V['rsdM15'][i], V['rsdM30'][i], V['rsdM1'][i],
                 V['rsdM2'][i], M4[i], n_, sgn * (px[i] - px[sb]) / px[sb] * 100.0))


if __name__ == '__main__':
    main(sys.argv[1:])
