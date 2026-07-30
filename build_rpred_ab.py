"""build_rpred_ab — the r-pred timestamp for every event under BOTH arms of the cancel A/B (Joe 0730).

Reads the banked stage-1 events (ab_rpred_stage1.json) and derives, per arm, the r-pred that the
insert-time IF would have written for each exhaustion.

  ARM A  r-pred run = contiguous run of (P[tf] == CS)
  ARM B  r-pred run = contiguous run of latch(set = P rising edge, reset = x/r cross)
         -> a run ENDS at the cross, so the next r-pred is a new run start. Run boundaries differ
            between arms, not just the choice of which run wins.
  IF     both arms: first run start on the line since that arm's last exhaustion on that line;
         from 05-18 (RPRED_START). Causal.

    python3 build_rpred_ab.py [--fresh]
"""
import json, os, sys, datetime as dt
import numpy as np
import build_exhaust as X
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import _latch_with_reset
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

IN = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'ab_rpred_stage1.json')
DDL = '''CREATE TABLE IF NOT EXISTS rpl_rpred_ab (
    ab_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    ab_arm       CHAR(1),                             -- A live | B x/r cross cancels r-pred
    ab_conf_ms   BIGINT, ab_conf_utc VARCHAR(11),     -- the exhaustion
    ab_cur_tf    INT, ab_bias VARCHAR(4), ab_dir TINYINT, ab_leg VARCHAR(1),
    ab_rpred_ms  BIGINT, ab_rpred_utc VARCHAR(11),    -- the r-pred the IF writes under this arm
    ab_rpred_end_ms BIGINT, ab_rpred_end_utc VARCHAR(11), ab_run_bars INT,
    ab_lead_min  DOUBLE,                              -- exhaustion - r-pred
    ab_live_at_exh TINYINT,                           -- was the r-pred run still true at the exhaustion
    ab_prev_exh_ms BIGINT,                            -- the exhaustion on this line that re-armed the write
    ab_in_other_arm TINYINT,                          -- 1 = this event exists in the other arm too
    KEY (ab_arm), KEY (ab_conf_ms), KEY (ab_cur_tf, ab_dir))'''


def runs_A(t, p):
    return (R.L0['P'][t] == p['CS'])


def runs_B(t, p):
    pr = (R.L0['P'][t] == p['CS'])
    edge = pr & ~np.r_[False, pr[:-1]]
    fx = R.L0['fx_bull'] if p['BULL'] else R.L0['fx_bear']
    return _latch_with_reset(edge, np.asarray(fx[t], bool))


def arm_rows(events, series, ts, other):
    """Per line, walk forward: an exhaustion re-arms the write; the first run start while armed wins."""
    u = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%m%d %H:%M')
    EX = {}
    for e in events:
        EX.setdefault((e['cur_tf'], 1 if e['bias'] == 'bull' else -1), []).append(int(e['conf']))
    for k in EX:
        EX[k].sort()
    WRITE = {}
    for (tf, dr), confs in EX.items():
        p = R._polar('bull' if dr > 0 else 'bear')
        s = np.asarray(series(tf, p), bool)
        ch = np.flatnonzero(s[1:] != s[:-1]) + 1
        st = np.r_[0, ch]; en = np.r_[ch, len(s)]
        keep = s[st] & (ts[st] >= R.RPRED_START)
        st = st[keep]; en = en[keep]
        j = 0; armed = True; prev = None; W = []
        for a, b in zip(st.tolist(), en.tolist()):
            t0 = int(ts[a])
            while j < len(confs) and confs[j] <= t0:
                armed = True; prev = confs[j]; j += 1
            if not armed:
                continue
            W.append((t0, int(ts[b - 1]), int(b - a), prev)); armed = False
        WRITE[(tf, dr)] = W
    out = []
    for e in events:
        tf = e['cur_tf']; dr = 1 if e['bias'] == 'bull' else -1; c = int(e['conf'])
        cand = [w for w in WRITE.get((tf, dr), []) if w[0] <= c]
        if not cand:
            continue
        t0, t1, nb, prev = cand[-1]
        out.append((u(c), c, tf, e['bias'], dr, e['leg'], t0, u(t0), t1, u(t1), nb,
                    (c - t0) / 60000, 1 if t1 >= c else 0, prev,
                    1 if (c, tf, e['bias']) in other else 0))
    return out


def main(argv):
    D = json.load(open(IN))
    X.rebuild_cache(120)
    ts = np.asarray(R.L0['ts'], np.int64)
    ka = {(e['conf'], e['cur_tf'], e['bias']) for e in D['A']}
    kb = {(e['conf'], e['cur_tf'], e['bias']) for e in D['B']}
    d = DatabaseManager(**get_db_config()); d.connect()
    if '--fresh' in argv:
        d.execute('DROP TABLE IF EXISTS rpl_rpred_ab')
    d.execute(DDL); d.execute('DELETE FROM rpl_rpred_ab')
    for arm, ev, ser, oth in (('A', D['A'], runs_A, kb), ('B', D['B'], runs_B, ka)):
        rows = arm_rows(ev, ser, ts, oth)
        d.executemany('''INSERT INTO rpl_rpred_ab (ab_conf_utc,ab_conf_ms,ab_cur_tf,ab_bias,ab_dir,ab_leg,
            ab_rpred_ms,ab_rpred_utc,ab_rpred_end_ms,ab_rpred_end_utc,ab_run_bars,ab_lead_min,
            ab_live_at_exh,ab_prev_exh_ms,ab_in_other_arm, ab_arm)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,''' + "'%s')" % arm, rows)
        print('arm %s: %d of %d events given an r-pred' % (arm, len(rows), len(ev)))
    print()
    for x in d.execute('''SELECT ab_arm, COUNT(*) n, ROUND(AVG(ab_lead_min)) av, ROUND(MIN(ab_lead_min)) mn,
        ROUND(MAX(ab_lead_min)) mx, SUM(ab_live_at_exh) live, ROUND(AVG(ab_run_bars)) rb,
        SUM(ab_prev_exh_ms IS NOT NULL) armed FROM rpl_rpred_ab GROUP BY ab_arm''', fetch=True):
        print('  arm %s | n %3d | lead avg %6d  min %4d  max %6d min | live at exh %2d | avg run %4d bars | re-armed %3d'
              % (x['ab_arm'], x['n'], x['av'], x['mn'], x['mx'], x['live'], x['rb'], x['armed']))
    print('\n  shared events, r-pred side by side (first 25):')
    print('  %-11s %-5s %-4s | %-11s %8s | %-11s %8s | %s'
          % ('exhaustion', 'tf', 'bias', 'A r-pred', 'A lead', 'B r-pred', 'B lead', 'delta min'))
    for x in d.execute('''SELECT a.ab_conf_utc, a.ab_cur_tf, a.ab_bias, a.ab_rpred_utc ra, a.ab_lead_min la,
        b.ab_rpred_utc rb, b.ab_lead_min lb FROM rpl_rpred_ab a JOIN rpl_rpred_ab b
        ON b.ab_arm='B' AND b.ab_conf_ms=a.ab_conf_ms AND b.ab_cur_tf=a.ab_cur_tf AND b.ab_bias=a.ab_bias
        WHERE a.ab_arm='A' ORDER BY a.ab_conf_ms LIMIT 25''', fetch=True):
        print('  %-11s s%-4d %-4s | %-11s %8.0f | %-11s %8.0f | %+9.0f'
              % (x['ab_conf_utc'], x['ab_cur_tf'], x['ab_bias'], x['ra'], x['la'], x['rb'], x['lb'],
                 x['lb'] - x['la']))
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
