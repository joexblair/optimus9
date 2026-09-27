"""report_all_wsf_flatruns - spec_label 22_go_20260921.  Joe 0927: prints `all_wsf_flatruns` in the
shape of Sheet2 of 260924_strat_wsf_leash.xlsx.

FIVE ROWS PER sig_utc, stacked.  The first carries `awf_dr` and `awf_sig_utc`; the other four leave
`awf_dr` blank and put the row's LABEL in the `awf_sig_utc` column, exactly as Joe laid it out.
The table itself keeps both columns real on all five rows - they are NOT NULL and they are how the
five rows stay together and sort.  This module is the only place the blanking happens.

THE LABELS ARE JOE'S OWN WORDS, from Sheet2 and from his 0927 message:
  dir      "mage's incoming direction: 16min ago 8min ago 4min ago 2min ago 1min ago"
  mage     "mage val @ sig_utc"
  r        "r val @ sig_utc"
  xcross   "nearest (lookback or lookforth) ws{TF}x-cross-r"   <- assembled from his sentence; he has
           not named this row, so the label is provisional and his to set.

THE `dir` CELL HOLDS FIVE VALUES.  The table stores them newline-separated, which is what Excel needs
when a cell is pasted.  This report joins them with ' / ' on one line, because a pipe-delimited row
cannot carry a newline inside a field.  MINE, stated.

  --md    pipe-delimited, for pasting
  --day   YYYY-MM-DD, one day only
  --inst  v7 or v8, default v7
"""
import argparse, sys
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TABLE = 'all_wsf_flatruns'
TFS = range(1, 13)
LABEL = {'dir': "mage's incoming direction: 16min ago 8min ago 4min ago 2min ago 1min ago",
         'mage': 'mage val @ sig_utc',
         'r': 'r val @ sig_utc',
         'xcross': 'nearest (lookback or lookforth) ws{TF}x-cross-r'}


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument('--md', action='store_true')
    a.add_argument('--day')
    a.add_argument('--inst', default='v7', choices=('v7', 'v8'))
    o = a.parse_args(argv)

    db = DatabaseManager(**get_db_config()); db.connect()
    q = ("SELECT awf_kind,awf_n,awf_dr,awf_sig_utc,%s FROM %s WHERE awf_inst=%%s"
         % (','.join('awf_ws%d' % t for t in TFS), TABLE))
    p = [o.inst]
    if o.day:
        q += " AND DATE(awf_sig_utc)=%s"; p.append(o.day)
    q += " ORDER BY awf_sig_ms, awf_n"
    rows = db.execute(q, tuple(p), fetch=True)
    db.disconnect()

    head = ['awf_dr', 'awf_sig_utc'] + ['awf_ws%d' % t for t in TFS]
    W = [6, 76] + [24] * 12
    pr = ((lambda c: print('|'.join(str(v) for v in c))) if o.md else
          (lambda c: print('  ' + ''.join(str(v).ljust(W[i]) for i, v in enumerate(c)))))
    print('%s   %s   %d rows   %d sig_utc' % (TABLE, o.inst, len(rows), len(rows) // 5))
    print('  five rows per sig_utc; the dir cell is one line here, newline-stacked in the table')
    print('')
    pr(head)
    for r in rows:
        if r['awf_kind'] == 'flatrun':
            c = ['%+d' % int(r['awf_dr']), r['awf_sig_utc'].strftime('%Y-%m-%d %H:%M:%S')]
        else:
            c = ['', LABEL[r['awf_kind']]]
        for t in TFS:
            v = r['awf_ws%d' % t]
            c.append('' if v is None else v.replace('\n', ' / '))
        pr(c)
    return 0


if __name__ == '__main__':
    sys.exit(main())
