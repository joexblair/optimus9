"""build_wsf_marker_tf_view — the eight timeframes side by side, one row per marker and rung.

Joe 0820: "the entire finisher logic relies on comparision between TFs. start again and build a full
TF view of the data, per marker".

WHAT CHANGED. `wsf_marker_snapshot` holds one row per (marker, rung, timeframe), so every question
asked of it was a question about ONE timeframe at a time. Nothing in it could compare ws3 against
ws4. This view pivots the same rows so all eight timeframes sit on one line and the comparison
between them is readable.

NOTHING IS RECOMPUTED. This is a view over `wsf_marker_snapshot`. No second copy of the data.

WHAT IS ON A ROW.
  the marker, its f or d tag, its side, the rung, and the bar
  ws1 to ws8, for each of: the Mage value, whether Mage is out of bounds on the marker's side,
    the r value, whether r is inside both fences, the points r has still to travel to its fence,
    and the momentum verdict on r
  the adjacent-timeframe differences - Joe 0819: "inter-TF diff is how we measure weak-mage and
    weak-r". ws1 minus ws2, ws2 minus ws3, and so on to ws7 minus ws8, for Mage and for r.
"""
import sys
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

MEASURES = [('mage',     'wms_mage',     'Mage value'),
            ('mage_oob', 'wms_mage_oob', 'Mage out of bounds on the marker side'),
            ('r',        'wms_r',        'r value'),
            ('r_ib',     'wms_r_ib',     'r inside both fences'),
            ('r_dist',   'wms_r_dist',   'points r still has to travel to its fence'),
            ('momo',     'wms_momo',     'momentum verdict on r')]


def build_sql():
    cols = []
    for short, col, _ in MEASURES:
        for tf in range(1, 9):
            cols.append(f'  MAX(CASE WHEN wms_tf={tf} THEN {col} END) AS ws{tf}_{short}')
    # the adjacent-timeframe differences. Joe 0819: inter-TF diff.
    for short, col in (('mage', 'wms_mage'), ('r', 'wms_r')):
        for tf in range(1, 8):
            cols.append(f'  MAX(CASE WHEN wms_tf={tf} THEN {col} END) - '
                        f'MAX(CASE WHEN wms_tf={tf + 1} THEN {col} END) AS d{short}_{tf}_{tf + 1}')
    return ('CREATE OR REPLACE VIEW v_wsf_marker_tf AS SELECT\n'
            '  wms_win_from, wms_hi, wms_lo, wms_k_window, wms_fixed_samples, wms_ladder,\n'
            '  wms_marker, wms_tag, wms_side, wms_offset_s, wms_bar_utc,\n'
            + ',\n'.join(cols)
            + '\nFROM wsf_marker_snapshot\n'
              'GROUP BY wms_win_from, wms_hi, wms_lo, wms_k_window, wms_fixed_samples, wms_ladder,\n'
              '         wms_marker, wms_tag, wms_side, wms_offset_s, wms_bar_utc')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(build_sql())
    n = db.execute('SELECT COUNT(*) c FROM v_wsf_marker_tf', fetch=True)[0]['c']
    ncol = len(db.execute('SHOW COLUMNS FROM v_wsf_marker_tf', fetch=True))
    print(f'  v_wsf_marker_tf : {n:,} rows, {ncol} columns', flush=True)
    print(f'    = 121 markers x 15 rungs, eight timeframes on every row', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
