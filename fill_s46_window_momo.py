"""fill_s46_window_momo — add and populate sw_momo_activated / sw_momo_ended on s46_window. Joe 0804.

WHAT IT MARKS, per s46_window row, between sw_entry_ms and sw_exit_ms inclusive:

    sw_momo_activated_ms/_utc   first bar where SAME-BIAS momo is detected on s15 OR s22
    sw_momo_ended_ms/_utc       first bar at or after that where s15r OR s22r reaches the level
    sw_momo_r_ext               the extreme of EITHER r line, FURTHEST TOWARD the boundary.
                                NOT bounded by the exit (Joe 0804) - see call 7.
    sw_momo_r_ext_ms/_utc       the bar that extreme occurred on
    sw_r_entry_near             of r15/r22 AT THE ENTRY BAR, the one closest to the boundary

JOE'S CALLS (0804), one per ambiguity:
  1 "momo detected" = state 1 (momo) OR state 2 (curl)          -> BOTH
  2 the end condition watches whichever line reaches first       -> NOT necessarily the activator
  3 the level is DIRECTION MATCHED                               -> dr -1: r <= 18 | dr +1: r >= 82
  4 momo activates but never reaches the level before the exit   -> NULL
  5 both s15 and s22 activate                                    -> EARLIEST
  6 the extreme is FURTHEST TOWARD the boundary                  -> dr -1: MIN | dr +1: MAX
      Joe's worked rule and his 78/79 example disagreed; he chose toward-the-boundary, which is
      the same operator sw_r_entry_near uses, so both columns read in the same direction.
  7 the extreme span is NOT bounded by the exit                  -> entry -> first MID recross
      "look forward from sw_exit_utc ... the actual extrema of the lines' progression". The span
      ends when that line crosses back through 50 AWAY from its target, exclusive of the crossing
      bar; each TF gets its own span. No crossing -> run to the end of the tape. No horizon imposed.
      sw_r_entry_near is UNAFFECTED - it is a point reading on the entry bar.

Bias tag matches gate_open (sweep_s46_exit.py:222): dr +1 -> 'p', dr -1 -> 'n'.
momo state int8 encoding (build_s46_lines.py:14): 0 none | 1 momo | 2 curl | 3 sideways.
r15 / r22 are the kline 10|4|11|close lines at TF15 / TF22 — the same lines momo() is computed on.

RE-RUN AFTER build_s46_window.py. That script does `DELETE FROM s46_window` (line 108) and
re-inserts, so the columns survive but their values do not. This script is idempotent.

    python3 fill_s46_window_momo.py            # add columns if absent, then fill
    python3 fill_s46_window_momo.py --dry      # report without writing
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import datetime as dt
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

NPZ = os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp/lines_all.npz'
MOMO_STATES = (1, 2)          # Joe 0804 call 1: momo AND curl both count as detected
MID = 50.0                    # Joe 0804 call 7: the forward span ends when r crosses back
                              # through 50 away from the target. Already momo()'s own level gate.
LO_LEVEL = 18.0               # Joe 0804 call 3: dr -1 watches r <= 18
HI_LEVEL = 82.0               #                  dr +1 watches r >= 82
TFS = (15, 22)                # the two boards whose momo and r are consulted

COLS = (('sw_momo_activated_ms', 'BIGINT'), ('sw_momo_activated_utc', 'VARCHAR(20)'),
        ('sw_momo_ended_ms', 'BIGINT'), ('sw_momo_ended_utc', 'VARCHAR(20)'),
        ('sw_momo_r_ext', 'DOUBLE'), ('sw_momo_r_ext_ms', 'BIGINT'),
        ('sw_momo_r_ext_utc', 'VARCHAR(20)'), ('sw_r_entry_near', 'DOUBLE'))

u = lambda ms: dt.datetime.utcfromtimestamp(ms / 1000).strftime('%m-%d %H:%M:%S')


def main(argv):
    dry = '--dry' in argv
    d = np.load(NPZ)
    ts = d['ts'].astype(np.int64)
    G = {tf: {'p': d['g%d_p' % tf], 'n': d['g%d_n' % tf]} for tf in TFS}
    R = {tf: d['r%d' % tf].astype(float) for tf in TFS}
    print('npz %s' % NPZ)
    print('  bars %d   %s -> %s' % (len(ts), u(int(ts[0])), u(int(ts[-1]))))

    db = DatabaseManager(**get_db_config()); db.connect()
    for c, t in COLS:                                  # additive; precedent kline_sanitiser.py:52-56
        try:
            db.execute('ALTER TABLE s46_window ADD COLUMN %s %s' % (c, t))
            print('  + column %s %s' % (c, t))
        except Exception:
            pass                                       # already present
    rows = db.execute('SELECT sw_pk,sw_n,sw_entry_ms,sw_exit_ms,sw_dr,sw_entry_utc,sw_exit_utc '
                      'FROM s46_window ORDER BY sw_n', fetch=True)
    print('  s46_window rows %d' % len(rows))

    upd = []
    print()
    print('  %-4s %-16s %-3s %-16s %-16s %6s %8s %-16s %8s %8s %8s'
          % ('n', 'entry utc', 'dr', 'momo activated', 'momo ended', 'gap',
             'r ext', 'r ext utc', 'r15 in', 'r22 in', 'near in'))
    for r in rows:
        a = int(np.searchsorted(ts, int(r['sw_entry_ms'])))
        b = int(np.searchsorted(ts, int(r['sw_exit_ms'])))
        dr = int(r['sw_dr']); tag = 'p' if dr > 0 else 'n'
        act_ms = end_ms = None
        ext = ext_ms = near = None
        r15_in = r22_in = float('nan')
        if a < len(ts) and b < len(ts) and b >= a:
            # call 6 + call 7: the extreme FURTHEST TOWARD the boundary. NOT bounded by the exit
            # (Joe 0804) - the span runs from the ENTRY bar forward to the first bar where that line
            # crosses back through MID away from the target, exclusive of the crossing bar. Each TF
            # gets its OWN span, since r15 and r22 turn at different times. No crossing -> run to the
            # end of the tape; no horizon is imposed.
            best = None
            for tf in TFS:
                rr = R[tf]
                s = rr[a:]
                if len(s) < 2:
                    continue
                # "crosses back through 50" = crosses AWAY from this row's target
                cx = ((s[:-1] <= MID) & (s[1:] > MID)) if dr < 0 else ((s[:-1] >= MID) & (s[1:] < MID))
                w = np.flatnonzero(cx)
                end = a + int(w[0]) + 1 if len(w) else len(rr)      # exclusive: stop AT the cross bar
                seg_r = rr[a:end]
                if not len(seg_r) or not np.isfinite(seg_r).any():
                    continue
                j = int(np.nanargmin(seg_r) if dr < 0 else np.nanargmax(seg_r))
                v = float(seg_r[j])
                if best is None or (v < best[0] if dr < 0 else v > best[0]):
                    best = (v, a + j)
            if best is not None:
                ext, ext_ms = best[0], int(ts[best[1]])
            # column 3: of r15/r22 AT THE ENTRY BAR, the one closest to the boundary.
            # Same operator as the extreme, so the two columns read in the same direction.
            r15_in, r22_in = float(R[15][a]), float(R[22][a])
            vin = [v for v in (r15_in, r22_in) if np.isfinite(v)]
            if vin:
                near = min(vin) if dr < 0 else max(vin)
        if a < len(ts) and b < len(ts) and b >= a:
            seg = slice(a, b + 1)
            # call 1 + call 5: momo OR curl, on s15 OR s22 — the OR takes the EARLIEST bar of either
            m = np.zeros(b - a + 1, bool)
            for tf in TFS:
                v = G[tf][tag][seg]
                for st in MOMO_STATES:
                    m |= (v == st)
            w = np.flatnonzero(m)
            if len(w):
                ai = a + int(w[0]); act_ms = int(ts[ai])
                # call 2 + call 3: whichever line reaches the DIRECTION-MATCHED level first,
                # searched from activation to the exit bar. call 4: none found -> stays None.
                lv = np.zeros(b - ai + 1, bool)
                for tf in TFS:
                    rr = R[tf][ai:b + 1]
                    lv |= ((rr <= LO_LEVEL) if dr < 0 else (rr >= HI_LEVEL))
                z = np.flatnonzero(lv)
                if len(z):
                    end_ms = int(ts[ai + int(z[0])])
        gap = '' if (act_ms is None or end_ms is None) else str(int((end_ms - act_ms) / 5000))
        f = lambda v: ('%8.2f' % v) if (v is not None and np.isfinite(v)) else '       -'
        print('  %-4d %-16s %-3d %-16s %-16s %6s %s %-16s %s %s %s'
              % (r['sw_n'], r['sw_entry_utc'], dr,
                 u(act_ms) if act_ms else '-', u(end_ms) if end_ms else 'NULL', gap,
                 f(ext), u(ext_ms) if ext_ms else '-', f(r15_in), f(r22_in), f(near)))
        upd.append((act_ms, u(act_ms) if act_ms else None,
                    end_ms, u(end_ms) if end_ms else None,
                    ext, ext_ms, u(ext_ms) if ext_ms else None, near, int(r['sw_pk'])))

    n_act = sum(1 for x in upd if x[0] is not None)
    n_end = sum(1 for x in upd if x[2] is not None)
    ex = np.array([x[4] for x in upd if x[4] is not None], float)
    print()
    print('  momo activated %d of %d rows   momo ended %d   NULL ended %d'
          % (n_act, len(upd), n_end, n_act - n_end))
    for d_, lab, lv in ((-1, 'dr -1 (target %.0f)' % LO_LEVEL, LO_LEVEL),
                        (1, 'dr +1 (target %.0f)' % HI_LEVEL, HI_LEVEL)):
        v = np.array([x[4] for x, rr in zip(upd, rows) if x[4] is not None and int(rr['sw_dr']) == d_], float)
        if not len(v):
            continue
        reach = int((v <= lv).sum() if d_ < 0 else (v >= lv).sum())
        print('  %-20s n %2d   r ext  best %6.2f  median %6.2f  worst %6.2f   reached target %d'
              % (lab, len(v), (v.min() if d_ < 0 else v.max()), float(np.median(v)),
                 (v.max() if d_ < 0 else v.min()), reach))
    if not dry:
        db.executemany('UPDATE s46_window SET sw_momo_activated_ms=%s, sw_momo_activated_utc=%s, '
                       'sw_momo_ended_ms=%s, sw_momo_ended_utc=%s, sw_momo_r_ext=%s, '
                       'sw_momo_r_ext_ms=%s, sw_momo_r_ext_utc=%s, sw_r_entry_near=%s '
                       'WHERE sw_pk=%s', upd)
        print('  written')
    else:
        print('  DRY — nothing written')
    db.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
