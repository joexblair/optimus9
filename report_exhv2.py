"""exhv2 report - Joe's LOCKED format, read straight from rpl_exhv2. No rebuild, no build imports.

    r-pred | walk | bias | TF | s15 s22 act | branch cross | signal

`signal` = A ungated: the first s15x X s15m cross at or after the WALK bar, in the trade direction, with
no qualify and no gate. Joe 0731 adopted it on ALL rows ("I was using exit generically for exit and rev").

The branch race bar is still stored as v2_race_ms / v2_race_utc - it decides `act` (rev vs EXIT) and stays
in rpl_exhv2 for forensics - but it is NOT reportable. Joe 0731: "race column is not as valuable, so can
be dropped"; Joe 0731 again, on seeing it in a --race paste: remove it. The --race flag is gone, so the
column cannot appear.

    python3 report_exhv2.py            # the locked format, the only format
"""
import sys
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

STATE = {'momo': 'momo', 'sideways': 'side', 'none': 'none', 'curl': 'curl'}


def main(argv):
    d = DatabaseManager(**get_db_config()); d.connect()
    rows = d.execute("""SELECT v.*, s.es_rpred_utc FROM rpl_exhv2 v
                        LEFT JOIN rpl_exh_stat s ON s.es_conf_ms = v.v2_conf_ms
                        ORDER BY v.v2_conf_ms""", fetch=True)
    d.disconnect()
    H = ('   r-pred    |    walk     | bias | TF  | s15   s22   act  | branch  cross      |   signal    ')
    print(H); print('-' * len(H))
    for x in rows:
        cross = '%-4s s%-2s' % (x['v2_cross_tgt'], x['v2_cross_tf']) if x['v2_cross_tf'] else '-'
        line = ' %-11s | %-11s | %-4s | s%-3s| %-5s %-5s %-4s | %-6s  %-10s | %-11s ' % (
            x['es_rpred_utc'] or '', x['v2_walk_utc'], x['v2_eff_bias'], x['v2_cur_tf'],
            STATE.get(x['v2_s15_state'], '-'), STATE.get(x['v2_s22_state'], '-'), x['v2_action'],
            x['v2_branch'], cross, x['v2_sig_utc'] or '')
        print(line)
    print('-' * len(H))
    nex = sum(1 for x in rows if x['v2_action'] == 'EXIT')
    print('%d rows | act: rev %d  EXIT %d | signal = A ungated (first s15x X s15m at/after walk, no gate)'
          % (len(rows), len(rows) - nex, nex))
    err = [x['v2_err_min'] for x in rows if x['v2_err_min'] is not None]
    if err:
        import statistics as st
        a = [abs(v) for v in err]
        print('vs Joe\'s %d marked targets: mean %+.1f  median %+.1f  mean|err| %.1f  median|err| %.1f'
              % (len(err), st.mean(err), st.median(err), st.mean(a), st.median(a)))


if __name__ == '__main__':
    main(sys.argv[1:])
