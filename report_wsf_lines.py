"""report_wsf_lines — THE WSF LINE REPORT. ws1r to ws8r at one bar.

Joe 0818: "give this report a name so that I can easily request it".

    python3 report_wsf_lines.py 11:34:00
    python3 report_wsf_lines.py 11:34:00 up        # read the lines upward instead
    python3 report_wsf_lines.py 11:26:50 11:34:00  # several bars, one block each

Reads wsf_line_bar. Nothing is computed here - build_wsf_line_bar.py owns the measurement.

DIRECTION. With no direction given the report uses the bar's own wsf9of12 direction when the bar
is a signal bar, and read-downward otherwise. Pass `up` or `down` to force it.

The column labels follow the direction, because both the stall and the boundary do:
  read downward -> the stall looks for new LOWS  and the boundary tested is the LOW one
  read upward   -> the stall looks for new HIGHS and the boundary tested is the HIGH one
"""
import sys

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DAY = '2026-08-04'


def one(db, utc, force=None):
    sig = db.execute('SELECT side FROM v_ws_fin_walk WHERE g30_marker=%s', (utc,), fetch=True)
    is_sig = bool(sig)
    if force is not None:
        dr = force
    elif is_sig:
        dr = int(sig[0]['side'])
    else:
        dr = -1
    rows = db.execute(
        'SELECT wflb_tf tf, wflb_dr dr, wflb_r, wflb_stalled, wflb_since, wflb_ungated, '
        'wflb_curl_ends, wflb_bend, wflb_arc, wflb_vtx, wflb_oob, wflb_hi, wflb_lo '
        'FROM wsf_line_bar WHERE wflb_utc=%s AND wflb_dr=%s ORDER BY wflb_tf',
        (utc, dr), fetch=True)
    if not rows:
        print(f'no rows in wsf_line_bar for {utc} read {"upward" if dr > 0 else "downward"}')
        return
    hi, lo = rows[0]['wflb_hi'], rows[0]['wflb_lo']
    word = 'high' if dr > 0 else 'low'
    fence = f'at or over {hi:.0f}' if dr > 0 else f'at or under {lo:.0f}'
    tag = 'wsf9of12 signal bar' if is_sig else 'not a signal bar'
    print(f'\nWSF LINE REPORT   {DAY} {utc[-8:]}   read {"upward" if dr > 0 else "downward"}   ({tag})')
    print(f'{"line":<6} {"dr":>3} {"value":>7} {"stalled":>8} {"samples since a new "+word:>24} '
          f'{"wsf verdict":>12} {"curl ends":>10} {"bend":>9} {"arc":>8} {"turning point":>14} {fence:>15}')
    for r in rows:
        print(f'ws{r["tf"]}r{"":<2} {r["dr"]:>+3d} {r["wflb_r"]:7.2f} '
              f'{("yes" if r["wflb_stalled"] else "no"):>8} '
              f'{("-" if r["wflb_since"] is None else str(r["wflb_since"])):>24} '
              f'{r["wflb_ungated"]:>12} {(r["wflb_curl_ends"] or "-"):>10} '
              f'{r["wflb_bend"]:9.2f} {r["wflb_arc"]:8.3f} {r["wflb_vtx"]:14.3f} '
              f'{("yes" if r["wflb_oob"] else "no"):>15}')


def main(argv):
    force = None
    args = []
    for a in argv:
        if a.lower() in ('up', 'upward'):
            force = +1
        elif a.lower() in ('down', 'downward'):
            force = -1
        else:
            args.append(a)
    if not args:
        print(__doc__)
        return 2
    db = DatabaseManager(**get_db_config()); db.connect()
    for a in args:
        utc = a if len(a) > 8 else f'{DAY} {a}'
        one(db, utc, force)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
