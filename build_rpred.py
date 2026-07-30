"""build_rpred — persist the r-pred MOMENT at the point predict_breach produces it, then report.

Joe 0730. predict_breach (optimus9/compute/breaching_line.py) emits a per-bar STATE {+1 hi, -1 lo, 0 none}
and nothing recorded WHEN it turned on, so every r-pred timestamp in the project was reconstructed after the
fact and each derive disagreed. The fix is at the source.

  PASS 1  rpl_walk.persist_rpred, fired from rpl_walk.py right after P is built (RPRED_PERSIST flag).
          Row = the first bar of a contiguous non-zero run of P[TF], per TF, per direction -> rpl_rpred.
          THE IF: written only if nothing has been written for that line since the last exhaustion on it.
          Causal - only exhaustions already past are read. From 05-18; pre-05-18 is synthetic warmup.
  PASS 2  rpl_exh_stat.es_rpred_* <- the rpl_rpred row on that line at or before the exhaustion. With the IF
          there is exactly one per armed span, so this is a lookup, not a search. UPDATE only, no DROP.

    python3 build_rpred.py [--ceiling 120] [--no-build] [--fresh]
      --no-build  skip pass 1, report on what is in rpl_rpred
      --fresh     DROP rpl_rpred first (schema change / re-derive). rpl_rpred is built by this script only.
"""
import sys, datetime as dt
import numpy as np
import optimus9.orchestration.rpl_walk as R
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

CEILING = 120


def build(ceiling, w1=None):
    """PASS 1 — flip the flag and rebuild, so build_lines writes rpl_rpred at the point P is produced.
    w1 caps the WRITE at the working window's end; the r-pred lookback still reaches back to RPRED_START."""
    import build_exhaust as X
    R.RPRED_PERSIST = True; R.RPRED_END = w1
    try:
        X.rebuild_cache(ceiling)
        if max(R.TFS) == ceiling:            # cache already at ceiling -> rebuild_cache is a no-op, force the write
            R.L0 = R.build_lines(R.L0['src'])
    finally:
        R.RPRED_PERSIST = False; R.RPRED_END = None


def report(d, w0=None, w1=None):
    """PASS 2 — es_rpred_* <- the r-pred on that line at or before the exhaustion, then print.
    w0/w1 (Joe 0730) scope the EXHAUSTIONS only. The r-pred lookup is not bounded by them."""
    u = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%m%d %H:%M')
    src = {}
    for r in d.execute('SELECT rp_ts, rp_tf, rp_dir, rp_run_bars, rp_end_ts, rp_r FROM rpl_rpred ORDER BY rp_ts',
                       fetch=True):
        src.setdefault((int(r['rp_tf']), int(r['rp_dir'])), []).append(r)
    q = 'SELECT es_conf_ms, es_cur_tf, es_bias FROM rpl_exh_stat'
    if w0:
        q += ' WHERE es_conf_ms >= %d AND es_conf_ms < %d' % (w0, w1)
    st = d.execute(q, fetch=True)
    up, miss = [], 0
    for r in st:
        c = int(r['es_conf_ms']); dr = 1 if r['es_bias'] == 'bull' else -1
        cand = [x for x in src.get((int(r['es_cur_tf']), dr), []) if int(x['rp_ts']) <= c]
        if not cand:
            miss += 1; up.append((None, None, c, int(r['es_cur_tf']), r['es_bias'])); continue
        t = int(cand[-1]['rp_ts'])
        up.append((t, u(t), c, int(r['es_cur_tf']), r['es_bias']))
    d.executemany('''UPDATE rpl_exh_stat SET es_rpred_ms=%s, es_rpred_utc=%s
                     WHERE es_conf_ms=%s AND es_cur_tf=%s AND es_bias=%s''', up)
    n = d.execute('SELECT COUNT(*) c, COUNT(es_rpred_ms) r FROM rpl_exh_stat', fetch=True)[0]
    print('\nrpl_exh_stat: %d rows, es_rpred_ms set on %d (no r-pred on this line before the event: %d)'
          % (n['c'], n['r'], miss))
    q2 = '''SELECT s.es_conf_utc, s.es_cur_tf, s.es_bias, s.es_rpred_utc, s.es_rpred_ms, s.es_conf_ms,
                   s.es_mae_400, s.es_mfe_400, s.es_in_pine, p.rp_run_bars, p.rp_end_ts,
                   p.rp_prev_exh_ms, ROUND(p.rp_r, 2) rr_, ROUND(p.rp_margin, 2) mg
            FROM rpl_exh_stat s LEFT JOIN rpl_rpred p ON p.rp_ts = s.es_rpred_ms
              AND p.rp_tf = s.es_cur_tf AND p.rp_dir = (CASE WHEN s.es_bias='bull' THEN 1 ELSE -1 END)'''
    if w0:
        q2 += ' WHERE s.es_conf_ms >= %d AND s.es_conf_ms < %d' % (w0, w1)
    rr = d.execute(q2 + ' ORDER BY s.es_conf_ms', fetch=True)
    print('\n  %-11s %-5s %-4s | %-11s %8s | %6s %8s %6s | %6s %6s | %s'
          % ('exhaustion', 'tf', 'bias', 'r-pred', 'lead min', 'run', 'run min', 'live', 'MAE4', 'MFE4', 'armed by'))
    for x in rr:
        lead = (int(x['es_conf_ms']) - int(x['es_rpred_ms'])) / 60000 if x['es_rpred_ms'] else None
        rb = x['rp_run_bars']
        print('  %-11s s%-4d %-4s | %-11s %8s | %6s %8s %6s | %6.2f %6.2f | %s'
              % (x['es_conf_utc'], x['es_cur_tf'], x['es_bias'], x['es_rpred_utc'] or '-',
                 ('%.0f' % lead) if lead is not None else '-',
                 rb if rb is not None else '-',
                 ('%.1f' % (rb * 5 / 60)) if rb is not None else '-',
                 ('YES' if x['rp_end_ts'] and int(x['rp_end_ts']) >= int(x['es_conf_ms']) else 'no') if rb else '-',
                 x['es_mae_400'], x['es_mfe_400'],
                 u(int(x['rp_prev_exh_ms'])) if x['rp_prev_exh_ms'] else 'tape start'))


def main(argv):
    ceiling = CEILING; w0 = w1 = None
    ms = lambda m, dd: int(dt.datetime(2026, m, dd, tzinfo=dt.timezone.utc).timestamp() * 1000)
    for i, a in enumerate(argv):
        if a == '--ceiling' and i + 1 < len(argv):
            ceiling = int(argv[i + 1])
        if a == '--window' and i + 2 < len(argv):     # Joe 0730: scope the EXHAUSTIONS, not the r-pred
            w0 = ms(*[int(v) for v in argv[i + 1].split('-')])
            w1 = ms(*[int(v) for v in argv[i + 2].split('-')])
    if '--fresh' in argv:
        d = DatabaseManager(**get_db_config()); d.connect()
        d.execute('DROP TABLE IF EXISTS rpl_rpred')       # built by this script only; never a Joe artifact
        d.disconnect()
        print('rpl_rpred dropped (--fresh)')
    if '--no-build' not in argv:
        build(ceiling, w1)
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute(R.RPRED_DDL)
    t = d.execute('''SELECT COUNT(*) c, COUNT(DISTINCT rp_tf) tf, MIN(rp_utc) a, MAX(rp_utc) b,
                            SUM(rp_ts < %s) pre FROM rpl_rpred''', (R.RPRED_START,), fetch=True)[0]
    print('rpl_rpred: %d rows over %d TFs | %s .. %s | pre-05-18 %s' % (t['c'], t['tf'], t['a'], t['b'], t['pre']))
    if w0:
        print('exhaustion window: %s .. %s   (r-pred lookup NOT bounded by it)'
              % (dt.datetime.fromtimestamp(w0 / 1000, dt.timezone.utc).strftime('%m-%d'),
                 dt.datetime.fromtimestamp(w1 / 1000, dt.timezone.utc).strftime('%m-%d')))
    report(d, w0, w1)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
