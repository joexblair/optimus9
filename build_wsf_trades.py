"""build_wsf_trades - the reference backtest for the o9-live recon. Joe 0929.

ONE ROW PER TRADE.  Every knob comes from `wsf_trade_config`; nothing is a module constant. The
mechanics are `trade_walk`, `rule1_gate` and `dr_latch` - this file loads, walks, banks and prints.

CAUSALITY, AND THE ONE PART THAT IS NOT.  `trade_walk.walk` is a strictly causal bar-by-bar loop
reading only `dr[k]` and `dr[k-1]`; `dr_latch` and `anchor_floater` read nothing above `k`.

**`rule1_gate` READS FORWARD.** Its window is `[k - tol_bars, k + tol_bars]` - 42 bars = 210 s of
FUTURE - and `longest_outside` additionally extends a run forward with no bound at all. So the gate
verdict at a signal bar is not knowable at that bar. See that module's docstring for the measured
cost of every causal alternative. Joe has not ruled it and nothing here works around it.

THE RULES ARE JOE'S, 0929, and `trade_walk`'s docstring carries them verbatim:
  - every UNGATED sig_utc is a reversal: closes the open trade and opens a new one, and opens one
    when nothing is open
  - rule#1 gates the non-trade sig_utcs
  - the dr flip is the backstop, and it is the flip BACK TO the trade's own dr, two flips forward
  - the dr flip may only open when it had something to close
  - a sig_utc landing on a flip bar loses to the flip

WHY THIS FILE EXISTS.  Joe 0929 wants o9-live reconciled against a backtest, and *"scratchpad: move
everything into the codebase, and db the knobs, configs, etc"*. A recon cannot lean on a scratchpad
script - the reference has to be reproducible from the tape and the DB alone. This is that reference.

CAUSALITY, AND THE ONE THING A LIVE CONSUMER MUST NOT COPY.  Every bar read is at or before the event
being decided. The backstop bar is in the future when the trade opens; the walk does not act on it
early, it waits for the bar. In o9-live that has to be a standing order, not knowledge.

MAE and MFE are percentages of the entry, both non-negative, and there is NO P&L. Joe 0917 closed
P&L and kept the excursions.

  --day YYYY-MM-DD   walk one day only; without it the whole window
  --drop             drop the table first
  --md               pipe-delimited
"""
import argparse
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.jig import Jig, anchor_floater                      # noqa: E402
from optimus9.compute import trade_config as TC                            # noqa: E402
from optimus9.compute.dr_latch import latch_wob                            # noqa: E402
from optimus9.compute.line_config import mech_lines, override              # noqa: E402
from optimus9.compute.rule1_gate import gate                               # noqa: E402
from optimus9.compute.trade_walk import mae_mfe, walk                      # noqa: E402
from optimus9.compute.v3_config import v3_config                           # noqa: E402
from optimus9.config import get_db_config                                  # noqa: E402
from optimus9.db.database_manager import DatabaseManager                   # noqa: E402
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP    # noqa: E402
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key  # noqa: E402

TABLE = 'wsf_trades'
WIN = '2026-09-01..2026-09-06'
WIN_MS = (1788220800000, 1788652800000)      # the leash bank's own window
INST = {'v7': 'v7_coil_lines[gcws30,ws1]_confirm_lag_s180_exit_anchornamed_bar_gap_fill1'
              '_lookback_s240_support_min23',
        'v8': 'v8_coil_lines[ws2,ws3]_confirm_lag_s180_exit_anchornamed_bar_gap_fill1'
              '_lookback_s240_support_min23'}
DDL = '''CREATE TABLE IF NOT EXISTS %s (
    wt_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wt_key       VARCHAR(60) NOT NULL,
    wt_win       VARCHAR(48) NOT NULL,
    wt_n         INT         NOT NULL,
    wt_dr        TINYINT     NOT NULL,
    wt_side      VARCHAR(5)  NOT NULL,
    wt_open_utc  DATETIME(3) NOT NULL,
    wt_open_ms   BIGINT      NOT NULL,
    wt_close_utc DATETIME(3) NULL,
    wt_close_ms  BIGINT      NULL,
    wt_opened_by VARCHAR(8)  NOT NULL,
    wt_closed_by VARCHAR(8)  NULL,
    wt_open_px   DOUBLE      NOT NULL,
    wt_close_px  DOUBLE      NULL,
    wt_mae_pct   DOUBLE      NULL,
    wt_mfe_pct   DOUBLE      NULL,
    UNIQUE KEY uq_wt (wt_key, wt_win, wt_open_ms),
    KEY k_open (wt_open_ms))''' % TABLE
COLS = ('wt_key', 'wt_win', 'wt_n', 'wt_dr', 'wt_side', 'wt_open_utc', 'wt_open_ms',
        'wt_close_utc', 'wt_close_ms', 'wt_opened_by', 'wt_closed_by',
        'wt_open_px', 'wt_close_px', 'wt_mae_pct', 'wt_mfe_pct')


def _specs(db):
    """role -> (src, mode), as build_wsf_dtf_v3 reads them. Same shape report_rule1_gate uses."""
    spec = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in spec:
            _t, s_, m_ = g['override']
            spec[g['role']] = (s_, m_)
    return spec


def load(db, C):
    """Every line this producer needs, all on the 5 s tape grid.

    -> (ts, r1, r2, r3, g30r, x_next, px, m1, mx). The first seven are exactly what
    `report_rule1_gate.load` returns and are built the same way so the gate cannot drift between the
    two. `m1` and `mx` are the dr latch's pair - ws1Mage and ws{latch_tf}m.
    """
    import os
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system '
                    'WHERE sys_pk=1', fetch=True)[0]
    spec = _specs(db)
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                 {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
    cached = lambda tf, role: np.load(os.path.join(                                  # noqa: E731
        LINE_DIR, _line_key(END_MS, HOURS, WARMUP, override(tf * 60, *spec[role])) + '.npy'))
    with Jig(END_MS, hours=HOURS, warmup=WARMUP) as J:
        jt = np.asarray(J.ts, dtype=np.int64)
        g30r = np.asarray(J.causal.line('gcws30r'), float)
        px = np.asarray(J.px, float)
    idx = np.clip(np.searchsorted(jt, ts), 0, len(jt) - 1)
    px = np.asarray([v for v in px], float)
    good = np.isfinite(px)
    if not good.all():
        px = np.interp(np.arange(len(px)), np.flatnonzero(good), px[good])
    dtf = int(C['div_tf'])
    return (ts, cached(1, 'r'), cached(2, 'r'), cached(3, 'r'), g30r[idx],
            cached(dtf + 1, 'x'), px[idx],
            cached(1, 'Mage'), cached(int(C['latch_tf']), 'm'))


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument('--day')
    a.add_argument('--drop', action='store_true')
    a.add_argument('--md', action='store_true')
    o = a.parse_args(argv)

    db = DatabaseManager(**get_db_config()); db.connect()
    TC.seed(db)
    C = TC.load(db)
    V3 = v3_config(db)
    KEY = TC.key(C)
    if o.drop:
        db.execute("DROP TABLE IF EXISTS %s" % TABLE)
    db.execute(DDL)

    ts, r1, r2, r3, g30r, xn, px, m1, mx = load(db, C)
    n = len(ts)
    U = lambda i: __import__('datetime').datetime.fromtimestamp(                    # noqa: E731
        int(ts[i]) / 1000, __import__('datetime').timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    dr = latch_wob(m1, mx, 0, n - 1, wob=int(C['latch_wob']),
                   hi=float(C['mage_fence_hi']), lo=float(C['mage_fence_lo']))

    sql = ("SELECT wsl_sig_ms FROM wsf_leash WHERE wsl_knobs=%s AND wsl_sig_ms IS NOT NULL")
    args = [INST[C['leash_instance']]]
    if o.day:
        sql += " AND DATE(wsl_sig_utc)=%s"; args.append(o.day)
    sql += " ORDER BY wsl_sig_ms"
    sig = db.execute(sql, tuple(args), fetch=True)

    fence = (float(C['rule1_fence_lo']), float(C['rule1_fence_hi']))
    oob = (float(C['oob_lo']), float(C['oob_hi']))
    tol = int(float(C['rule1_tol_min']) * 60 / 5 / 2)
    dwell_bars = int(C['div_tf']) * int(V3['dwell_min_per_tf']) * 12
    blk = int(V3['block'])

    opens = []
    gated = []
    for s_ in sig:
        k = int(np.searchsorted(ts, int(s_['wsl_sig_ms'])))
        res = anchor_floater(r1, px, int(dr[k]), k, block=blk, mid=50.0, xn=xn,
                             dwell_bars=dwell_bars, oob=oob)
        g = gate(r1, r2, r3, g30r, int(dr[k]), k, tol, fence, oob,
                 0 if res is None else int(res['fired']))
        (opens if g['open'] else gated).append(k)
    # wsf_leash can hold several rows on one sig bar - the sheet has a dozen. The walk dedupes
    # anyway (a repeat bar hits the `pos['open'] == k` guard), but the printed count must be the
    # DISTINCT BAR count or it reads as more signals than there are.
    nrow_open, nrow_gate = len(opens), len(gated)
    opens = sorted(set(opens)); gated = sorted(set(gated))

    hi = n - 1
    if o.day:
        import datetime as _dt
        d0 = _dt.datetime.strptime(o.day, '%Y-%m-%d').replace(tzinfo=_dt.timezone.utc)
        hi = int(np.searchsorted(ts, int((d0 + _dt.timedelta(days=1)).timestamp() * 1000)))
    trades, still = walk(opens, dr, min(opens) if opens else 1, hi)

    win = o.day or WIN
    p = ((lambda *c: print('|'.join(str(v) for v in c))) if o.md else
         (lambda *c: print('  ' + ''.join(str(v).ljust(w) for v, w in
          zip(c, (4, 21, 6, 9, 21, 9, 7, 11, 11, 8, 8, 4))))))
    print('%s   %s   win %s   %d trades' % (TABLE, KEY, win, len(trades)))
    print('  sig_utc  %d distinct bars from %d leash rows   gated out %d bars (%d rows)'
          % (len(opens) + len(gated), nrow_open + nrow_gate, len(gated), nrow_gate))
    print('')
    p('#', 'OPEN', 'dir', 'opened by', 'CLOSE', 'closed by', 'min',
      'entry px', 'exit px', 'MAE %', 'MFE %', 'w')
    pay = []
    for i, t in enumerate(trades, 1):
        mae, mfe = mae_mfe(px, t['open'], t['close'], t['dr'])
        side = 'SHORT' if t['dr'] > 0 else 'LONG'
        p(i, U(t['open']), side, t['opened_by'], U(t['close']), t['closed_by'],
          '%.1f' % ((t['close'] - t['open']) * 5 / 60.0), '%.6f' % px[t['open']],
          '%.6f' % px[t['close']], '%.3f' % mae, '%.3f' % mfe, 'Y' if mfe > mae else '.')
        pay.append((KEY, win, i, t['dr'], side, U(t['open']), int(ts[t['open']]),
                    U(t['close']), int(ts[t['close']]), t['opened_by'], t['closed_by'],
                    float(px[t['open']]), float(px[t['close']]), mae, mfe))
    if still:
        p(len(trades) + 1, U(still['open']), 'SHORT' if still['dr'] > 0 else 'LONG',
          still['opened_by'], 'STILL OPEN', '-', '-', '%.6f' % px[still['open']], '-', '-', '-', '-')
        pay.append((KEY, win, len(trades) + 1, still['dr'],
                    'SHORT' if still['dr'] > 0 else 'LONG', U(still['open']),
                    int(ts[still['open']]), None, None, still['opened_by'], None,
                    float(px[still['open']]), None, None, None))

    have = db.execute("SELECT COUNT(*) c FROM %s WHERE wt_key=%%s AND wt_win=%%s" % TABLE,
                      (KEY, win), fetch=True)[0]['c']
    if have:
        print('')
        print('  %d rows already banked at this key and window - nothing written' % have)
    else:
        db.executemany("INSERT INTO %s (%s) VALUES (%s)"
                       % (TABLE, ','.join(COLS), ','.join(['%s'] * len(COLS))), pay)
        print('')
        print('  banked %d rows at %s / %s' % (len(pay), KEY, win))

    mm = [mae_mfe(px, t['open'], t['close'], t['dr']) for t in trades]
    print('')
    print('  closed %d   opened by sig_utc %d  dr-flip %d   closed by sig_utc %d  dr-flip %d'
          % (len(trades), sum(1 for t in trades if t['opened_by'] == 'sig_utc'),
             sum(1 for t in trades if t['opened_by'] == 'dr-flip'),
             sum(1 for t in trades if t['closed_by'] == 'sig_utc'),
             sum(1 for t in trades if t['closed_by'] == 'dr-flip')))
    if mm:
        print('  MFE > MAE  %d of %d' % (sum(1 for a, b in mm if b > a), len(mm)))
        print('  MAE mean %.3f  median %.3f  max %.3f'
              % (np.mean([a for a, _ in mm]), np.median([a for a, _ in mm]),
                 max(a for a, _ in mm)))
        print('  MFE mean %.3f  median %.3f  max %.3f'
              % (np.mean([b for _, b in mm]), np.median([b for _, b in mm]),
                 max(b for _, b in mm)))
        for d, lab in ((1, 'SHORT (dr +1)'), (-1, 'LONG  (dr -1)')):
            g = [x for x, t in zip(mm, trades) if t['dr'] == d]
            if g:
                print('  %s  n %-3d MAE mean %.3f  MFE mean %.3f  MFE > MAE %d'
                      % (lab, len(g), np.mean([a for a, _ in g]), np.mean([b for _, b in g]),
                         sum(1 for a, b in g if b > a)))
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
