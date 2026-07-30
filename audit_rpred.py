"""audit_rpred — independent re-derivation of every es_rpred_utc in rpl_exh_stat (Joe 0730).

Per row, on current_tf:
  1. collect r, m, Mage at the stored r-pred timestamp
  2. walk BACK from there to the bar r left the 30/70 fence (last bar inside [FL, FH], +1)
  3. walk FORWARD from the fence exit, calling predict_breach every 15 min, until a non-zero return
  4. if the stored timestamp is not inside that 15-min slot, flag the row and move on

predict_breach is called directly on scalars -- the audit must not read the same P array it is auditing.
Right bound on the forward walk is the exhaustion bar (the row's own scope), not a cap.
Writes via ALTER + UPDATE only. No DROP, no re-CREATE, 142 rows unchanged.

    python3 audit_rpred.py
"""
import sys, datetime as dt
import numpy as np
import build_exhaust as X
import optimus9.orchestration.rpl_walk as R
from optimus9.compute.breaching_line import predict_breach
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

STEP_MS = 15 * 60 * 1000                                   # Joe: test the calcs every 15 minutes
ADD = '''ALTER TABLE rpl_exh_stat
  ADD COLUMN es_rpred_r DOUBLE, ADD COLUMN es_rpred_m DOUBLE, ADD COLUMN es_rpred_mage DOUBLE,
  ADD COLUMN es_fence_exit_ms BIGINT, ADD COLUMN es_fence_exit_utc VARCHAR(11),
  ADD COLUMN es_rpred_audit TINYINT, ADD COLUMN es_rpred_audit_ms BIGINT,
  ADD COLUMN es_rpred_audit_utc VARCHAR(11)'''


def main():
    X.rebuild_cache(120)
    ts = np.asarray(R.L0['ts'], np.int64); E = R.L0['E']
    HI, LO, FH, FL = R.HI, R.LO, R.FH, R.FL
    u = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%m%d %H:%M')
    d = DatabaseManager(**get_db_config()); d.connect()
    have = {c['Field'] for c in d.execute('DESCRIBE rpl_exh_stat', fetch=True)}
    if 'es_rpred_audit' not in have:
        d.execute(ADD)
    rows = d.execute('''SELECT es_conf_ms, es_cur_tf, es_bias, es_rpred_ms, es_rpred_utc, es_conf_utc,
                               es_in_pine FROM rpl_exh_stat ORDER BY es_conf_ms''', fetch=True)
    print('boundary HI %.0f LO %.0f | fence FH %.0f FL %.0f | probe step %d min | %d rows\n'
          % (HI, LO, FH, FL, STEP_MS // 60000, len(rows)))
    up, D = [], []
    for x in rows:
        tf = int(x['es_cur_tf']); dr = 1 if x['es_bias'] == 'bull' else -1
        rp = int(x['es_rpred_ms']); c = int(x['es_conf_ms'])
        i = int(np.searchsorted(ts, rp)); ci = int(np.searchsorted(ts, c))
        r = E[tf]['r']; m = E[tf]['m']; M = E[tf]['M']
        inside = (r > FL) & (r < FH)
        back = np.flatnonzero(inside[:i + 1])                       # last bar r was INSIDE the fence
        fx = int(back[-1]) + 1 if len(back) and int(back[-1]) + 1 <= i else 0
        hit = None
        t = int(ts[fx])
        while t <= int(ts[ci]):
            p = int(np.searchsorted(ts, t))
            if p >= len(ts):
                break
            v = int(predict_breach(np.array([r[p]]), np.array([m[p]]), np.array([M[p]]),
                                   HI, LO, FH, FL, 0.0)[0])
            if v != 0:
                hit = int(ts[p]); break
            t += STEP_MS
        if hit is None:
            fl = 2
        elif hit <= rp < hit + STEP_MS:
            fl = 0
        else:
            fl = 1
        up.append((float(r[i]), float(m[i]), float(M[i]), int(ts[fx]), u(int(ts[fx])),
                   fl, hit, u(hit) if hit else None, c, tf, x['es_bias']))
        D.append((x['es_conf_utc'], tf, x['es_bias'], x['es_rpred_utc'], u(int(ts[fx])),
                  u(hit) if hit else None, fl, float(r[i]), float(m[i]), float(M[i]),
                  (rp - hit) / 60000 if hit else None, int(x['es_in_pine'] or 0)))
    d.executemany('''UPDATE rpl_exh_stat SET es_rpred_r=%s, es_rpred_m=%s, es_rpred_mage=%s,
        es_fence_exit_ms=%s, es_fence_exit_utc=%s, es_rpred_audit=%s, es_rpred_audit_ms=%s,
        es_rpred_audit_utc=%s WHERE es_conf_ms=%s AND es_cur_tf=%s AND es_bias=%s''', up)
    n = d.execute('''SELECT SUM(es_rpred_audit=0) ok, SUM(es_rpred_audit=1) bad,
                            SUM(es_rpred_audit=2) none, COUNT(*) c FROM rpl_exh_stat''', fetch=True)[0]
    d.disconnect()
    print('AUDIT  match %d | MISMATCH %d | no non-zero before the exhaustion %d | of %d\n'
          % (n['ok'], n['bad'], n['none'], n['c']))
    print('  %-11s %-5s %-4s | %-11s %-11s %-11s | %8s | %7s %7s %7s | %s'
          % ('exhaustion', 'tf', 'bias', 'stored', 'fence exit', 'probe hit', 'delta min',
             'r', 'm', 'Mage', 'flag'))
    for cu, tf, bs, st, fx, hh, fl, rr, mm, MM, dl, pin in D:
        print('  %-11s s%-4d %-4s | %-11s %-11s %-11s | %8s | %7.2f %7.2f %7.2f | %s%s'
              % (cu, tf, bs, st, fx, hh or '-', ('%.0f' % dl) if dl is not None else '-',
                 rr, mm, MM, ('MATCH' if fl == 0 else ('MISMATCH' if fl == 1 else 'NO-HIT')),
                 '  Y' if pin else ''))


if __name__ == '__main__':
    main()
