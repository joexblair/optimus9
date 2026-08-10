"""exhv2 report - Joe's LOCKED format, read straight from rpl_exhv2. No rebuild, no build imports.

    r-pred | walk | bias | TF | s15 s22 act | branch cross | signal | MFE side

`signal` = the APPROVED signal: REWALK 2 + gcs15 confirm. The s15x X s15m cross is the ANCHOR; the signal
is the first gcs15x X gcs15m cross at/after it. Read from rpl_dominoes.dm_sig_utc, joined on conf_ms.
`v2_sig_utc` in rpl_exhv2 is the ANCHOR and is NOT reported here.
  - was `A ungated` (the anchor, reported as the signal) until 0802.

`MFE side` = v2_mfe_side. Joe 0802 added the column. It means the s4Mage OOB side is the OPPOSITE boundary
to the side the r-pred predicted, so the effective direction flips (build_exhv2._derive: mf = int(sd != wt),
ed = -dr if mf else dr). It does NOT mean price has already moved favourably.

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
    rows = d.execute("""SELECT v.*, s.es_rpred_utc, m.dm_sig_utc FROM rpl_exhv2 v
                        LEFT JOIN rpl_exh_stat s ON s.es_conf_ms = v.v2_conf_ms
                        LEFT JOIN rpl_dominoes m ON m.dm_conf_ms = v.v2_conf_ms
                        ORDER BY v.v2_conf_ms""", fetch=True)
    d.disconnect()
    H = ('   r-pred    |    walk     | bias | TF  | s15   s22   act  | branch  cross        |   signal       | MFE side')
    print(H); print('-' * len(H))
    for x in rows:
        cross = '%-4s s%-2s' % (x['v2_cross_tgt'], x['v2_cross_tf']) if x['v2_cross_tf'] else '-'
        line = ' %-11s | %-11s | %-4s | s%-3s| %-5s %-5s %-4s | %-6s  %-12s | %-12s | %-8s' % (
            x['es_rpred_utc'] or '', x['v2_walk_utc'], x['v2_eff_bias'], x['v2_cur_tf'],
            STATE.get(x['v2_s15_state'], '-'), STATE.get(x['v2_s22_state'], '-'), x['v2_action'],
            x['v2_branch'], cross, x['dm_sig_utc'] or '', 'MFE' if x['v2_mfe_side'] else '-')
        print(line)
    print('-' * len(H))
    nex = sum(1 for x in rows if x['v2_action'] == 'EXIT')
    nmf = sum(1 for x in rows if x['v2_mfe_side'])
    nns = sum(1 for x in rows if not x['dm_sig_utc'])
    print('%d rows | act: rev %d  EXIT %d | MFE side %d / not %d'
          % (len(rows), len(rows) - nex, nex, nmf, len(rows) - nmf))
    print('signal = REWALK 2 + gcs15 confirm (first gcs15x X gcs15m at/after the s15 anchor)'
          + ('  |  %d rows with no rpl_dominoes match, signal blank' % nns if nns else ''))
    # `err` vs the 14 marked targets is GONE (Joe 0802): "they were simply spec-dialing targets that helped
    # us build the foundational code. every change from here out is based on what we see at the end of each
    # re-build - so long as we retain our data tables, we have a better way to AB changes."
    # The columns v2_target_utc / v2_err_min still exist in rpl_exhv2 and are still written by the producer;
    # nothing reports them. Dropping the columns is a separate decision.


if __name__ == '__main__':
    main(sys.argv[1:])
