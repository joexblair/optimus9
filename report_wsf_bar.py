"""report_wsf_bar — THE wsf-model-report. One bar, one table. Joe 0820.

THE FORMAT IS NAMED AND FIXED. Joe 0820: "bank this format as wsf-model-report", and gave the
column list verbatim:

    line | r value | heading | r IB | verdict | stalled | 50 gate | blocked by 50 | last-verdict |
    last-verdict-dwell | Mage value | lb-mage-oob | weak-mage

Columns are not added, removed or reordered without Joe saying so.

EXTENDED 0821, Joe: "if the six new columns pass the test, add them to the formal wsf-model-report".
They passed - 84 truncation checks, 0 mismatches. Seven columns were stored, not six; the extra one
is the developing stoch reading that Joe's own question about emerging lines produced.

    stoch now   the DEVELOPING stoch reading, updated every 5 s
    stoch out   THE INCOMING THRESHOLD - the oldest closed stoch still inside the seven-bar
                average, the one that leaves when this line's next bar closes. r rises only if the
                incoming beats it. (stoch now - stoch out) / 7 is the move r is taking right now
    sat clock   bars of this line since RSI last SET its 8-bar extreme on the side read. The
                DEVELOPING bar is bar 0 and competes for it, so a fresh extreme reads 0
    sat left    bars before that extreme must roll out of the window and the stoch must fall
    RSI         RSI(5) on the developing bar
    RSI lo/hi   the window the stoch divides by. hi minus lo is the amplifier - a narrow window
                turns a small RSI move into a large stoch move

    python3 report_wsf_bar.py 07:36:20            the bar's own side, from ws_fin_9of12
    python3 report_wsf_bar.py 07:36:20 up         force the upward read
    python3 report_wsf_bar.py 07:36:20 down       force the downward read

Reads only what is already banked - wsf_line_bar for the r line and its momentum, wsf_bar_tf for
Mage and the weak-mage scan. Nothing is recomputed, so a request is a query.

THE COLUMNS, and where each comes from.
  r value        ws{tf}r at this bar.
  verdict        the momentum verdict on that line, read on this bar's side, AFTER Joe 0820's rule:
                 a momentum-true r line that is out of bounds or stalled reads none. The producer's
                 own answer is kept alongside in wflb_ungated and is not what this column shows.
  stalled        the STALL_N 6 mechanic: 6 lattice samples in a row with no new extreme.
  Mage value     ws{tf}Mage at this bar.
  lb-mage-oob    Mage is out of bounds on this side now, OR was inside the last 120 seconds.
                 That tolerance is the spec's WMT_LOOKBACK_S.
  weak-mage      the one line the scan stops at: ws1 upward, the first Mage the tolerance does not
                 count as out. Only that row is marked.
  heading        MY RULE, fitted to Joe's read at 07:36:20 and matching all seven lines he called:
                   a line already past its fence is heading AWAY - it has made the cross already
                   otherwise the sign of the momentum fit's slope says which way it points
                 Every value it reads is printed at or before this bar. Joe's own explanation used
                 the bar's CLOSE, which at 07:36:20 had not printed yet.
  r IB           r is inside the fence. Joe 0820 first asked for "1) inside the fence and 2)
                 heading away", then withdrew the second condition: "I can't rely on `heading` to
                 support `r IB`. the reason: r lines cannot be relied on - sometimes they are
                 crossing out of the fence later that wsf9of12, and sometimes they don't exit the
                 fence at all". So heading no longer gates it.
                 THE FENCE HERE IS STILL 85/15. Joe moved `heading` onto momo-fence-r and has not
                 moved this one. It changes only lines sitting between 83 and 85.
  50 gate        the level test inside momo_core. The line must be on the far side of 50 for its
                 direction, but the gate SLACKENS by up to LEVEL_SLACK 13.9 points in proportion to
                 how cleanly the line tracks: slack = 13.9 x r2 x min(1, |slope| / MOMO_SLOPE_MIN 1.0).
                 A line that tracks perfectly can sit 13.9 points the wrong side of 50 and still pass.
                 This column prints the level the line actually had to reach at this bar.
  blocked by 50  yes when this gate is what turned the verdict to none. Joe 0820 read ws8r at
                 07:36:20 as "not over 50 ... therefore momentum = false".

THE FOOTER, Joe 0820: "add a footer row that reports the wsf-momoc/momo-none/exhaust state".
It is the reading AT THIS BAR and carries nothing forward:
    domTF is blocking          -> wsf-momo-none.  Joe 0820: "'none' occurs when a trade fires, or
                                  when domTF blocks (overrides excluded)"
    else any of ws4r..ws8r carries momentum   -> wsf-momoc, and the footer names that group
    else any of ws1r..ws3r carries momentum   -> wsf-momoc, and the footer names that group
    else                                      -> wsf-exhaust
Momentum means the verdict is momo or curl - Joe 0817: "(curl or momo) create wsf-momoc".
NOT A STATE MACHINE. Joe's flow is wsf-momoc -> wsf-exhaust -> wsf-momo-none -> wsf-momoc, and five
questions on it are still open: what acquiring wsf-momoc means, whether the all-in-bounds reset
fires momo-none, whether a domTF block is a moment or a stretch, the starting state, and whether one
bar can hold two changes. Until those land this footer reads one bar and holds no history.

NOT REPORTED. The wsf momentum state - momoc, exhaust, momo-none. The three-state flow has five
open questions and nothing here invents it.
"""
import sys
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

WIN_FROM = '2026-08-04 00:00:00'
DAY      = '2026-08-04'
HI, LO   = 85.0, 15.0
LEVEL_SLACK = 13.9   # momo_core. How far the 50 gate can slacken for a cleanly tracking line
SLOPE_MIN   = 1.0    # momo_core MOMO_SLOPE_MIN, r-units per sample
MOMO_KILL    = 'state'  # which reading of Joe 0820's rule to read back. See build_wsf_line_bar.py
MOMO_FENCE_R = 17       # momo-fence-r, Joe 0820: 100 - 17 = 83 at the top, 17 at the bottom
MOMO_XWOB    = 4        # 5 s bars held outside the fence before an exit counts. Joe 0821
WMT_TF_LO    = 2        # the weak-mage scan's lowest timeframe. Joe 0821 moved it from 1 to 2
KNOBS = ('kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_'
         f'mk{MOMO_KILL}_mf{MOMO_FENCE_R}_xw{MOMO_XWOB}')
# THE JOIN MUST PIN EVERY KNOB ON BOTH TABLES. Both now hold several knob sets side by side - that
# is what the unique keys are for - so a join that pins only some of them returns one row per
# COMBINATION. Unpinned, this report printed four rows per line.


def _n(v):
    return '' if v is None else f'{float(v):.2f}'


def _i(v):
    return '' if v is None else str(int(v))


def heading(out_fence, slope):
    """Left momo-fence-r -> away. Otherwise the slope's sign against the direction read.

    Joe 0820: "apply the fence to this mech". The test was against the global 85/15 boundary; it is
    now against momo-fence-r, 83/17."""
    if out_fence:
        return 'away'
    return 'toward' if slope > 0 else 'away' if slope < 0 else 'flat'


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    t = sys.argv[1]
    bar = f'{DAY} {t}' if len(t) <= 8 else t
    force = sys.argv[2].lower() if len(sys.argv) > 2 else None

    db = DatabaseManager(**get_db_config()); db.connect()
    sig = db.execute("SELECT wsf_side s, wsf_domtf d FROM ws_fin_9of12 WHERE wsf_utc=%s "
                     "AND wsf_ho_rule='median' AND wsf_line_hcap='ws1b:1'", (bar,), fetch=True)
    if force in ('up', 'down'):
        dr = 1 if force == 'up' else -1
    elif sig:
        dr = int(sig[0]['s'])
    else:
        print(f'  {bar} is not a wsf9of12 signal bar, so it carries no side of its own.')
        print(f'  Re-run with "up" or "down" to pick the read.')
        db.disconnect()
        return 1

    rows = db.execute("""SELECT b.wbt_tf tf, b.wbt_r r, b.wbt_mage mg, b.wbt_mage_oob_tol mt,
              b.wbt_weak_mage_tf wmt, l.wflb_verdict u, l.wflb_stalled sl, l.wflb_slope sp,
              l.wflb_mfr_out ob, l.wflb_fit fi, l.wflb_level lv, l.wflb_verdict_dwell vdw, l.wflb_last_verdict lv2,
              b.wbt_stoch_now sn, b.wbt_stoch_out so, b.wbt_sat_bars sb, b.wbt_sat_left sl2,
              b.wbt_rsi rsi, b.wbt_rsi_lo rlo, b.wbt_rsi_hi rhi
         FROM wsf_bar_tf b
         JOIN wsf_line_bar l ON l.wflb_utc=b.wbt_utc AND l.wflb_tf=b.wbt_tf AND l.wflb_dr=b.wbt_dr
        WHERE b.wbt_win_from=%s AND b.wbt_utc=%s AND b.wbt_dr=%s AND l.wflb_knobs=%s
              AND b.wbt_wmt_tf_lo=%s ORDER BY b.wbt_tf""",
        (WIN_FROM, bar, dr, KNOBS, WMT_TF_LO), fetch=True)
    if not rows:
        print(f'    no rows banked for {bar}. The dataset covers {DAY} only.')
        db.disconnect()
        return 1

    print(f'\n  BAR {bar}')
    print(f'    a wsf9of12 signal bar: {"yes" if sig else "no"}'
          + (f'   domTF reads {sig[0]["d"]}' if sig else ''))
    print('    read ' + ('upward, so the fence each line can reach is 85'
                         if dr > 0 else 'downward, so the fence each line can reach is 15'))
    wmt = rows[0]['wmt']
    print()
    print('    line | r value | heading | r IB | verdict  | stalled | 50 gate | blocked by 50 |'
          ' last-verdict | last-verdict-dwell | Mage value | lb-mage-oob | weak-mage |'
          ' stoch now | stoch out | sat clock | sat left |   RSI  | RSI lo | RSI hi')
    for x in rows:
        tf = int(x['tf']); rv = float(x['r'])
        h = heading(bool(x['ob']), float(x['sp']))
        rib = 'yes' if LO < rv < HI else ''
        # the slack the level gate earned at this bar, recomputed from the stored fit
        trk = max(0.0, min(1.0, float(x['fi']) * min(1.0, abs(float(x['sp'])) / SLOPE_MIN)))
        gate = (50 - LEVEL_SLACK * trk) if dr > 0 else (50 + LEVEL_SLACK * trk)
        blocked = '' if int(x['lv']) else 'yes'
        print(f"    ws{tf}  | {rv:>7.2f} | {h:<7} | {rib:<4} | {x['u']:<8} |"
              f"  {'yes' if x['sl'] else '':<5}  |  {gate:>6.2f} |      {blocked:<4}     |"
              f"  {(x['lv2'] or ''):<8}    |       {int(x['vdw']):>5} s      |"
              f"   {float(x['mg']):>6.2f}   |"
              f"    {'yes' if x['mt'] else '':<4}     |   {'yes' if wmt == tf else '':<3}     |"
              f"  {_n(x['sn']):>7} |  {_n(x['so']):>7} |    {_i(x['sb']):>3}    |   {_i(x['sl2']):>3}    |"
              f" {_n(x['rsi']):>6} | {_n(x['rlo']):>6} | {_n(x['rhi']):>6}")

    mom = {int(x['tf']) for x in rows if x['u'] in ('momo', 'curl')}
    hi_grp = sorted(t for t in mom if t >= 4)
    lo_grp = sorted(t for t in mom if t <= 3)
    if sig and sig[0]['d'] == 'BLOCKED':
        state, why = 'wsf-momo-none', 'domTF is blocking at this bar'
    elif hi_grp:
        state, why = 'wsf-momoc', 'momentum on ' + ', '.join(f'ws{t}r' for t in hi_grp) + ' (the ws4 to ws8 group)'
    elif lo_grp:
        state, why = 'wsf-momoc', 'momentum on ' + ', '.join(f'ws{t}r' for t in lo_grp) + ' (the ws1 to ws3 group)'
    else:
        state, why = 'wsf-exhaust', 'no r line from ws1 to ws8 carries momentum'
    print(f'    STATE AT THIS BAR: {state}   -   {why}')
    print()
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
