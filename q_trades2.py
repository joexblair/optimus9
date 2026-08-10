"""q_trades2 — read Joe's four ideas out of rpl_trades. Joe 0803 12:10.

Every cut is a WHERE clause over the full 75-day tape (05-18 -> 07-31). Nothing here computes a line;
build_trades2.py banked the raw values so the thresholds live in SQL and can be changed without a rebuild.

BLOCKS, NOT BARS. The 10-day window that produced tonight's HTF-opposed result had 5 two-day blocks and
the result inverted on 75 days. So every headline number here is also reported as a per-block mean with a
t on the BLOCK series, not on the trade series — 5,954 trades is not 5,954 independent observations.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

RV = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 22, 25, 30, 45, 60, 90, 120]
LTF = ['g5', 'g15', 'g30', 's1', 's2']
SETS = [('ALL', '1=1'), ('ALT-loose', 'tr_alt_loose=1'), ('ALT-strict', 'tr_alt_strict=1')]
BLK = 'FLOOR((tr_ms - %d)/(2*86400000))' % 1747526400000      # 2-day blocks from 05-18


def blockstat(d, where, col='tr_ret'):
    """mean of the per-block means + t on the BLOCK series (n = blocks, not trades)."""
    r = d.execute("SELECT %s b, AVG(%s) m, COUNT(*) n FROM rpl_trades WHERE %s GROUP BY b "
                  "HAVING n>=3 ORDER BY b" % (BLK, col, where), fetch=True)
    if len(r) < 3:
        return None
    v = np.array([x['m'] for x in r], float)
    t = v.mean() / (v.std(ddof=1) / np.sqrt(len(v))) if v.std(ddof=1) > 1e-12 else 0.0
    return v.mean(), t, len(v), float((v > 0).mean() * 100)


def band(d, lab, rows, hdr):
    print('\n  %s' % lab)
    print('    ' + hdr)
    for r in rows:
        print('    ' + r)


def main(argv):
    d = DatabaseManager(**get_db_config()); d.connect()
    Q = lambda s: d.execute(s, fetch=True)

    def line(lab, where, extra=''):
        r = Q("SELECT COUNT(*) n,AVG(tr_ret) m,SUM(tr_ret) s,MIN(tr_ret) w,MAX(tr_mae) x,"
              "AVG(tr_ret<0)*100 l FROM rpl_trades WHERE %s" % where)[0]
        if not r['n']:
            return None
        b = blockstat(d, where)
        return ('%-22s %6d %8.3f %9.1f %8.3f %8.3f %6.0f%%  %8s %7s %6s%s'
                % (lab, r['n'], r['m'], r['s'], r['w'], r['x'], r['l'],
                   ('%.3f' % b[0]) if b else '-', ('%+.2f' % b[1]) if b else '-',
                   ('%d' % b[2]) if b else '-', extra))

    HDR = ('%-22s %6s %8s %9s %8s %8s %7s  %8s %7s %6s'
           % ('cut', 'n', 'mean', 'total', 'worst', 'maxMAE', 'loss%', 'blk-mean', 'blk-t', 'blks'))

    for sname, sw in SETS:
        print('\n' + '=' * 118)
        print('SET %s' % sname)
        print('=' * 118)
        print(HDR)
        print(line('baseline', sw))

        print('\n--- A. r on a side of 50 at entry (bias side = with the trade) ---')
        out = []
        for tf in RV:
            for tag, cond in (('r bias-side', '(tr_dr=1 AND tr_rv%d>50) OR (tr_dr=-1 AND tr_rv%d<50)' % (tf, tf)),
                              ('r against',   '(tr_dr=1 AND tr_rv%d<50) OR (tr_dr=-1 AND tr_rv%d>50)' % (tf, tf))):
                z = line('s%-4d %s' % (tf, tag), '%s AND (%s)' % (sw, cond))
                if z:
                    out.append(z)
        print('\n'.join(out))

        print('\n--- D. RPL init scan at entry: highest TF with OOB r or r-pred, ceiling 120 ---')
        for tag, cond in (
                ('with trend  (bull>bear on a long)',
                 '(tr_dr=1 AND tr_init_bull>tr_init_bear) OR (tr_dr=-1 AND tr_init_bear>tr_init_bull)'),
                ('AGAINST trend',
                 '(tr_dr=1 AND tr_init_bear>tr_init_bull) OR (tr_dr=-1 AND tr_init_bull>tr_init_bear)'),
                ('tie', 'tr_init_bull=tr_init_bear')):
            z = line(tag, '%s AND (%s)' % (sw, cond))
            if z:
                print(z)
        print('  ceiling 90:')
        for tag, cond in (
                ('with trend (c90)',
                 '(tr_dr=1 AND tr_init_bull90>tr_init_bear90) OR (tr_dr=-1 AND tr_init_bear90>tr_init_bull90)'),
                ('AGAINST trend (c90)',
                 '(tr_dr=1 AND tr_init_bear90>tr_init_bull90) OR (tr_dr=-1 AND tr_init_bull90>tr_init_bear90)')):
            z = line(tag, '%s AND (%s)' % (sw, cond))
            if z:
                print(z)
        print('  by the winning TF\'s height (with-trend only):')
        for a, b in ((1, 8), (9, 22), (23, 45), (46, 90), (91, 120)):
            cond = ('((tr_dr=1 AND tr_init_bull>tr_init_bear AND tr_init_bull BETWEEN %d AND %d) OR '
                    '(tr_dr=-1 AND tr_init_bear>tr_init_bull AND tr_init_bear BETWEEN %d AND %d))'
                    % (a, b, a, b))
            z = line('trend TF s%d-s%d' % (a, b), '%s AND %s' % (sw, cond))
            if z:
                print(z)

        print('\n--- C. LTF confirming x-cross-Mage entry (both OOB), delayed entry ---')
        for tag in LTF:
            r = Q("""SELECT COUNT(*) n, AVG(tr_c%s_bars>=0)*100 hit, AVG(NULLIF(tr_c%s_bars,-1))*5/60 mins
                     FROM rpl_trades WHERE %s""" % (tag, tag, sw))[0]
            r2 = Q("""SELECT COUNT(*) n, AVG(tr_dr*(tr_exit_px-tr_c%s_px)/tr_c%s_px*100) m,
                      SUM(tr_dr*(tr_exit_px-tr_c%s_px)/tr_c%s_px*100) s,
                      MIN(tr_dr*(tr_exit_px-tr_c%s_px)/tr_c%s_px*100) w,
                      AVG(tr_dr*(tr_exit_px-tr_c%s_px)/tr_c%s_px*100<0)*100 l
                      FROM rpl_trades WHERE %s AND tr_c%s_bars>=0"""
                  % ((tag,) * 8 + (sw, tag)))[0]
            base = Q("SELECT AVG(tr_ret) m FROM rpl_trades WHERE %s AND tr_c%s_bars>=0" % (sw, tag))[0]
            if not r2['n']:
                continue
            bb = blockstat(d, '%s AND tr_c%s_bars>=0' % (sw, tag))
            print('    %-6s cross fires %5.1f%% of trades, mean wait %5.1f min | delayed n %5d '
                  'mean %7.3f (same rows entered at OOB: %7.3f) total %8.1f worst %7.3f loss %3.0f%%  blk-t %s'
                  % (tag, r['hit'] or 0, r['mins'] or 0, r2['n'], r2['m'], base['m'], r2['s'], r2['w'],
                     r2['l'], ('%+.2f' % bb[1]) if bb else '-'))

        print('\n--- B. s15/s22 momo at the s6 EXIT bar -> hold to the 2nd / 3rd exit ---')
        print('    %-26s %6s %9s %9s %9s %9s' % ('momo state at exit', 'n', 'ret@exit1', 'ret@exit2',
                                                 'ret@exit3', 'best'))
        for ln in ('m15', 'm22', 'r15', 'r22'):
            for st, sl in ((3, 'momo'), (2, 'curl'), (1, 'sideways'), (0, 'none')):
                r = Q("""SELECT COUNT(*) n, AVG(tr_ret) a, AVG(tr_ret2) b, AVG(tr_ret3) c
                         FROM rpl_trades WHERE %s AND tr_x%s_st=%d""" % (sw, ln, st))[0]
                if not r['n'] or r['n'] < 20:
                    continue
                vals = [r['a'], r['b'], r['c']]
                best = ['exit1', 'exit2', 'exit3'][int(np.argmax([v if v is not None else -9e9 for v in vals]))]
                print('    %-26s %6d %9.3f %9.3f %9.3f %9s'
                      % ('%s %s' % (ln, sl), r['n'], r['a'] or 0, r['b'] or 0, r['c'] or 0, best))
        print('    %-26s %6s %9s %9s %9s' % ('-- level sweep, Mage momo --', 'n', 'ret@exit1', 'ret@exit2', 'ret@exit3'))
        for ln in ('m15', 'm22'):
            for lv in (50, 70, 85, 100, 115):
                cond = ('((tr_dr=1 AND tr_x%s_rw>=%d) OR (tr_dr=-1 AND tr_x%s_rw<=%d)) AND tr_x%s_st=3'
                        % (ln, lv, ln, 200 - lv, ln))
                r = Q("SELECT COUNT(*) n,AVG(tr_ret) a,AVG(tr_ret2) b,AVG(tr_ret3) c "
                      "FROM rpl_trades WHERE %s AND %s" % (sw, cond))[0]
                if r['n'] and r['n'] >= 20:
                    print('    %-26s %6d %9.3f %9.3f %9.3f'
                          % ('%s momo lvl>=%d' % (ln, lv), r['n'], r['a'] or 0, r['b'] or 0, r['c'] or 0))
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
