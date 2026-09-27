"""report_all_wsf_flatruns - spec_label 22_go_20260921.  Joe 0927: prints `all_wsf_flatruns` in the
shape of Sheet2 of 260924_strat_wsf_leash.xlsx.

EIGHT ROWS PER sig_utc.  The first carries `awf_dr` and `awf_sig_utc`; the other four leave `awf_dr`
blank and put the row's LABEL in the `awf_sig_utc` column, exactly as Joe laid it out.  The table
keeps both columns real on all five rows - they are NOT NULL and they are how the five rows stay
together and sort.  This module is the only place the blanking happens.

THE `dir` CELL IS ONE MULTILINE CELL.  Joe 0927: *"you can create multiline excel cells. for HID
input, i use alt-enter"*, and *"stack the dir data vertically"*.  So the five band readings are one
cell holding five lines, not five cells and not a joined string.

  --xlsx  writes a real workbook with `wrapText` set on the value cells.  USE THIS ONE.  A CSV
          carries no cell formatting, so Excel holds the newlines but renders the cell on one line
          until you edit it - Joe 0927: *"when I refresh the dataset, it looks like a horizontal
          string. when I double click on the cell, it rearranges to vertical"*.  That is Wrap Text
          being off, not a missing newline.  Setting it here removes the step.
  --csv   writes a CSV whose fields are quoted, so the embedded newlines arrive in Excel as
          alt-enter content in a single cell.  The newlines are correct but unwrapped - see above.
  default onscreen, the multiline cells laid out across physical lines.

THE awf_sig_utc COLUMN IS DEDUPED.  Joe 0927: *"dedup the awf_sig_utc column"*.  A value prints once
and is blank on the lines beneath it, so nothing repeats down a stacked cell or a sig_utc block.

THE LABELS ARE JOE'S OWN WORDS, from Sheet2 and from his 0927 message:
  dir      "mage's incoming direction:" then the five band multipliers, then "0.75 x TF (p)" - the
           de-poisoned last mile, anchored 30 s before the ws1Mage reversal instead of at sig_utc.
           Joe 0927 asked for the `(p)` suffix: *"sufix it with '(p)' so that I don't forget"*
  mage     "mage val @ sig_utc"
  r        "r val @ sig_utc"
  xcross   "nearest (lookback or lookforth) ws{TF}x-cross-r"   <- assembled from his sentence; he has
           not named this row, so the label is provisional and his to set.

  --day   YYYY-MM-DD, one day only
  --inst  v7 or v8, default v7
  --out   the CSV path, default ./all_wsf_flatruns_<inst>.csv
"""
import argparse, csv, sys
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TABLE = 'all_wsf_flatruns'
TFS = range(1, 13)
DIR_HEAD = "mage's incoming direction:"
# the lookbacks are Joe's base set scaled by TF, so the minutes differ per column and the shared
# label column names the MULTIPLIER instead. The bottom line is the last mile, read from its
# dr-side extrema - build_all_wsf_flatruns has the mech.
DIR_BANDS = ('12 x TF', '6 x TF', '3 x TF', '1.5 x TF', '0.75 x TF', '0.75 x TF (p)')
LABEL = {'mage': 'mage val @ sig_utc',
         'r': 'r val @ sig_utc',
         'xcross': 'nearest (lookback or lookforth) ws{TF}x-cross-r',
         'blank1': '',
         'blank2': '',
         'rtraj': 'trajectory direction of r'}
# blank1 and blank2 carry no label and no values - Joe notates them in the xlsx and they keep every
# sig_utc block the same height so his notation survives a future row being added.


def blocks(rows):
    """-> [(dr, sig_utc, {kind: [12 cells]})], grouped on awf_first_ms.

    NOT grouped by position. Two wsf_leash rows can share one wsl_sig_ms - the sheet has several -
    and then ordering by sig_ms interleaves their kinds, so a positional group loses cells.
    `awf_first_ms` is the moment key and is what the table's own unique key groups on.
    """
    seen = {}
    out = []
    for r in rows:
        fm = int(r['awf_first_ms'])
        if fm not in seen:
            seen[fm] = ['%+d' % int(r['awf_dr']), r['awf_sig_utc'].strftime('%Y-%m-%d %H:%M:%S'), {}]
            out.append(seen[fm])
        seen[fm][2][r['awf_kind']] = [r['awf_ws%d' % t] for t in TFS]
    return out


def cells(b):
    """One block -> the five report rows, each (label_cell, [12 value cells], onscreen_offset).

    The cells are the TRUE cell contents - the dir cell holds exactly five lines. `onscreen_offset`
    is how far down to push the value lines when laying the block out on physical lines, because the
    dir label block carries a header line above its five band labels. It is a rendering number only
    and never reaches the CSV.
    """
    dr, sig, k = b
    lab = '\n'.join((DIR_HEAD,) + DIR_BANDS)
    blank = [''] * 12
    return [(sig, k.get('flatrun', blank), 0),
            (lab, ['' if v is None else v for v in k.get('dir', blank)], 1),
            (LABEL['mage'], k.get('mage', blank), 0),
            (LABEL['r'], k.get('r', blank), 0),
            (LABEL['xcross'], ['' if v is None else v for v in k.get('xcross', blank)], 0),
            (LABEL['blank1'], blank, 0),
            (LABEL['blank2'], blank, 0),
            (LABEL['rtraj'], ['' if v is None else v for v in k.get('rtraj', blank)], 0)]


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument('--csv', action='store_true')
    a.add_argument('--xlsx', action='store_true')
    a.add_argument('--day')
    a.add_argument('--inst', default='v7', choices=('v7', 'v8'))
    a.add_argument('--out')
    o = a.parse_args(argv)

    db = DatabaseManager(**get_db_config()); db.connect()
    q = ("SELECT awf_kind,awf_n,awf_dr,awf_sig_utc,awf_first_ms,%s FROM %s WHERE awf_inst=%%s"
         % (','.join('awf_ws%d' % t for t in TFS), TABLE))
    p = [o.inst]
    if o.day:
        q += " AND DATE(awf_sig_utc)=%s"; p.append(o.day)
    q += " ORDER BY awf_sig_ms, awf_first_ms, awf_n"
    rows = db.execute(q, tuple(p), fetch=True)
    db.disconnect()
    B = blocks(rows)
    head = ['awf_dr', 'awf_sig_utc'] + ['awf_ws%d' % t for t in TFS]

    if o.xlsx:
        import openpyxl
        from openpyxl.styles import Alignment
        from openpyxl.utils import get_column_letter
        wb = openpyxl.Workbook(); sh = wb.active; sh.title = 'all_wsf_flatruns'
        sh.append(head)
        top = Alignment(vertical='top')
        wrap = Alignment(wrapText=True, vertical='top')
        for b in B:
            for i, (lab, vals, _off) in enumerate(cells(b)):
                sh.append([b[0] if i == 0 else ''] + [lab] + list(vals))
                r = sh.max_row
                for c in range(1, 15):
                    sh.cell(row=r, column=c).alignment = wrap if c >= 2 else top
        sh.freeze_panes = 'C2'
        sh.column_dimensions['A'].width = 7
        sh.column_dimensions['B'].width = 30
        for t in TFS:
            sh.column_dimensions[get_column_letter(2 + t)].width = 11
        path = o.out or './all_wsf_flatruns_%s.xlsx' % o.inst
        wb.save(path)
        print('%s   %s   %d sig_utc x 8 rows -> %s' % (TABLE, o.inst, len(B), path))
        print('  wrapText is set on every value cell, so the stacked cells render without editing')
        return 0

    if o.csv:
        path = o.out or './all_wsf_flatruns_%s.csv' % o.inst
        with open(path, 'w', newline='') as f:
            w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            w.writerow(head)
            for b in B:
                for i, (lab, vals, _off) in enumerate(cells(b)):
                    w.writerow([b[0] if i == 0 else ''] + [lab] + list(vals))
        print('%s   %s   %d sig_utc x 8 rows -> %s' % (TABLE, o.inst, len(B), path))
        print('  fields are quoted, so the dir cell arrives in Excel as one alt-enter cell')
        return 0

    W = [6, 50] + [10] * 12
    print('%s   %s   %d sig_utc x 8 rows' % (TABLE, o.inst, len(B)))
    print('  the dir cell is ONE cell holding five lines; awf_sig_utc is deduped down each stack')
    print('')
    print('  ' + ''.join(h.ljust(W[i]) for i, h in enumerate(head)))
    for b in B:
        for i, (lab, vals, off) in enumerate(cells(b)):
            L = lab.split('\n')
            V = [([''] * off) + str(v).split('\n') for v in vals]
            h = max([len(L)] + [len(x) for x in V])
            for ln in range(h):
                c = [b[0] if (i == 0 and ln == 0) else '', L[ln] if ln < len(L) else '']
                c += [V[t][ln] if ln < len(V[t]) else '' for t in range(12)]
                print('  ' + ''.join(str(v).ljust(W[j]) for j, v in enumerate(c)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
