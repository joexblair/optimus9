"""rpred_row — the r-pred time for one exhaustion row, computed from scratch (Joe 0730).

No shortcut on current_tf: builds at RPL_TF_CEILING so any rung 1..120 is served the same way.
Nothing here reads rpl_rpred - it recomputes, so it also serves as the check on that table.

  r-pred run = latch(set = predict_breach rising edge, reset = the x/r cross on the same line)
  r-pred     = the start of the run live at, or most recently before, the exhaustion bar

    RPL_TF_CEILING=120 python3 rpred_row.py '0520 10:26'
    RPL_TF_CEILING=120 python3 rpred_row.py --window 5-20 5-22
"""
import sys, time, datetime as dt
import numpy as np

T0 = time.time()
import optimus9.orchestration.rpl_walk as R
from optimus9.compute.breaching_line import predict_breach
from optimus9.analysis.jig import _latch_with_reset
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
T_IMPORT = time.time() - T0

u = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
CACHE = {}


def episodes(tf, dr):
    """(run_start_idx, run_end_idx_exclusive) for every r-pred episode on the line, cached per line."""
    if (tf, dr) not in CACHE:
        E = R.L0['E'][tf]
        P = predict_breach(E['r'], E['m'], E['M'], R.HI, R.LO, R.FH, R.FL, 0.0)
        pr = (P == dr)
        fx = np.asarray((R.L0['fx_bull'] if dr > 0 else R.L0['fx_bear'])[tf], bool)
        s = _latch_with_reset(pr & ~np.r_[False, pr[:-1]], fx)
        ch = np.flatnonzero(s[1:] != s[:-1]) + 1
        st = np.r_[0, ch]; en = np.r_[ch, len(s)]
        k = s[st]
        CACHE[(tf, dr)] = (st[k], en[k])
    return CACHE[(tf, dr)]


def one(ts, conf_ms, tf, dr):
    st, en = episodes(tf, dr)
    i = int(np.searchsorted(ts, conf_ms))
    hit = np.flatnonzero(st <= i)
    if not len(hit):
        return None
    j = int(hit[-1]); a, b = int(st[j]), int(en[j])
    return dict(rpred=int(ts[a]), end=int(ts[b - 1]), bars=b - a,
                lead=(conf_ms - int(ts[a])) / 60000, live=(b - 1) >= i)


def main(argv):
    ms = lambda m, d_: int(dt.datetime(2026, m, d_, tzinfo=dt.timezone.utc).timestamp() * 1000)
    q = "SELECT es_conf_utc, es_conf_ms, es_cur_tf, es_bias FROM rpl_exh_stat"
    if '--window' in argv:
        i = argv.index('--window')
        w0 = ms(*[int(v) for v in argv[i + 1].split('-')]); w1 = ms(*[int(v) for v in argv[i + 2].split('-')])
        q += ' WHERE es_conf_ms >= %d AND es_conf_ms < %d' % (w0, w1)
    else:
        q += " WHERE es_conf_utc = '%s'" % argv[0]
    d = DatabaseManager(**get_db_config()); d.connect()
    rows = d.execute(q + ' ORDER BY es_conf_ms', fetch=True)
    d.disconnect()
    ts = np.asarray(R.L0['ts'], np.int64)
    t1 = time.time()
    print('  %-19s %-5s %-4s | %-19s %-19s | %6s %8s %5s | %8s'
          % ('exhaustion', 'tf', 'bias', 'r-pred', 'r-pred end', 'bars', 'run min', 'live', 'lead min'))
    for x in rows:
        tf = int(x['es_cur_tf']); dr = 1 if x['es_bias'] == 'bull' else -1
        r_ = one(ts, int(x['es_conf_ms']), tf, dr)
        if r_ is None:
            print('  %-19s s%-4d %-4s | no r-pred episode on this line' % (u(int(x['es_conf_ms'])), tf, x['es_bias']))
            continue
        print('  %-19s s%-4d %-4s | %-19s %-19s | %6d %8.1f %5s | %8.0f'
              % (u(int(x['es_conf_ms'])), tf, x['es_bias'], u(r_['rpred']), u(r_['end']),
                 r_['bars'], r_['bars'] * 5 / 60, 'YES' if r_['live'] else 'no', r_['lead']))
    print('\nimport+L0 (ceiling %d) %.1f s | compute %.2f s | total %.1f s'
          % (max(R.TFS), T_IMPORT, time.time() - t1, time.time() - T0))


if __name__ == '__main__':
    main(sys.argv[1:])
