"""build_exh_stat — rpl_exh_stat, one row per applied exhaustion event (Joe 0730).

Source is rpl_exh_applied (build_rplwalk2.applied). Per row: the confirmed exhaustion bar, current_tf,
the bar range it sits on, MFE/MAE to the next favourable pivot at 2.22% and 4.00%, the r-OOB breach
lifecycle on current_tf, and the pivot itself. Trade dir = -side; bull bias = hi OOB.

r-pred columns are left NULL here and filled by build_rpred.py (which owns rpl_rpred); the audit columns
are filled by audit_rpred.py. Order: build_rplwalk2 --applied --persist -> build_exh_stat -> build_rpred
-> audit_rpred.

    python3 build_exh_stat.py [--fresh] [--window 5-20 5-22]
      --fresh   DROP and rebuild. Required when the applied population changes (events appear/disappear),
                because a row keyed on a vanished exhaustion cannot be updated into a new one.
"""
import sys, datetime as dt
import numpy as np
import build_exhaust as X
import build_rpl_6of9 as _pin
import optimus9.orchestration.rpl_walk as R
from optimus9.compute.swing_detect import find_pivots
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TF4 = 240_000
DDL = '''CREATE TABLE IF NOT EXISTS rpl_exh_stat (
  es_pk BIGINT AUTO_INCREMENT PRIMARY KEY, es_created DATETIME DEFAULT CURRENT_TIMESTAMP,
  es_raw_ms BIGINT, es_raw_utc VARCHAR(11), es_conf_ms BIGINT, es_conf_utc VARCHAR(11),
  es_tf4_bar_ms BIGINT, es_bias VARCHAR(4), es_side INT, es_cur_tf INT,
  es_px DOUBLE, es_bar_rng_pct DOUBLE,
  es_mae_222 DOUBLE, es_mfe_222 DOUBLE, es_ratio_222 DOUBLE,
  es_mae_400 DOUBLE, es_mfe_400 DOUBLE, es_ratio_400 DOUBLE, es_mae_over_rng DOUBLE,
  es_rpred_ms BIGINT, es_rpred_utc VARCHAR(11),
  es_rpred_end_ms BIGINT, es_rpred_bars INT, es_rpred_label VARCHAR(16),
  es_rpred_last_ms BIGINT, es_rpred_last_utc VARCHAR(11),
  es_braw_ms BIGINT, es_braw_utc VARCHAR(11), es_bcur_ms BIGINT, es_bcur_utc VARCHAR(11),
  es_piv_ms BIGINT, es_piv_utc VARCHAR(11), es_piv_px DOUBLE, es_piv_bars INT,
  es_leg_amp_pct DOUBLE, es_in_pine TINYINT,
  es_rpred_r DOUBLE, es_rpred_m DOUBLE, es_rpred_mage DOUBLE,
  es_fence_exit_ms BIGINT, es_fence_exit_utc VARCHAR(11),
  es_rpred_audit TINYINT, es_rpred_audit_ms BIGINT, es_rpred_audit_utc VARCHAR(11),
  KEY(es_conf_ms), KEY(es_cur_tf), KEY(es_in_pine))'''


def main(argv):
    X.rebuild_cache(120)
    ts = np.asarray(R.L0['ts'], np.int64); px = np.asarray(R.L0['src'].pxs, float)
    E = R.L0['E']
    u = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%m%d %H:%M')
    W0 = int(dt.datetime(2026, 5, 20, tzinfo=dt.timezone.utc).timestamp() * 1000); W1 = W0 + 7 * 86_400_000
    PV = {}
    for p in (2.22, 4.00):
        Q = find_pivots(px, p); PV[p] = ([z[0] for z in Q], [z[1] for z in Q])
    J = _pin.J3

    def outc(i, side, pct):
        pv, kd = PV[pct]; want = 'L' if side > 0 else 'H'
        b = next((bb for bb, k in zip(pv, kd) if bb > i and k == want), None)
        if b is None:
            return None
        seg = px[i:b + 1]
        if side > 0:
            return (px[i] - np.nanmin(seg)) / px[i] * 100, (np.nanmax(seg) - px[i]) / px[i] * 100, int(b)
        return (np.nanmax(seg) - px[i]) / px[i] * 100, (px[i] - np.nanmin(seg)) / px[i] * 100, int(b)

    def leg(i):
        pv, _ = PV[4.00]
        j = next((k for k in range(len(pv) - 1) if pv[k] <= i < pv[k + 1]), None)
        return None if j is None else abs((px[pv[j + 1]] - px[pv[j]]) / px[pv[j]] * 100)

    CACHE = {}

    def breach(tf, side, i):
        """(raw r-OOB episode start containing i, wob-confirmed rising edge at/before i)."""
        key = (tf, side)
        if key not in CACHE:
            p = R._polar('bull' if side > 0 else 'bear')
            r = E[tf]['r']; oob = p['oob_climb'](r); idx = np.arange(len(r))
            rst = np.where(oob, 0, idx + 1)
            dw = (idx + 1) - np.maximum.accumulate(rst)
            start = np.where(oob, idx - dw + 1, -1)
            conf = J.causal.cross_wob(r - p['CB'], 0.0, 1 if side > 0 else -1, R.WOBN)
            CACHE[key] = (np.flatnonzero(conf & ~np.r_[False, conf[:-1]]), start)
        ce, start = CACHE[key]
        last = int(ce[ce <= i][-1]) if len(ce[ce <= i]) else None
        return (int(start[i]) if start[i] >= 0 else None), last

    d = DatabaseManager(**get_db_config()); d.connect()
    q = '''SELECT ea_raw_ms, ea_conf_ms, ea_bias, ea_cur_tf, ea_rpred_ms, ea_rpred_utc,
                  ea_rpred_end_ms, ea_rpred_bars, ea_rpred_label FROM rpl_exh_applied'''
    if '--window' in argv:                       # Joe 0730: scope the EXHAUSTIONS. r-pred is stamped upstream
        k = argv.index('--window')               # and is NOT bounded by this.
        _m = lambda v: int(dt.datetime(2026, *[int(z) for z in v.split('-')],
                                       tzinfo=dt.timezone.utc).timestamp() * 1000)
        q += ' WHERE ea_conf_ms >= %d AND ea_conf_ms < %d' % (_m(argv[k + 1]), _m(argv[k + 2]))
        print('exhaustion window: %s .. %s' % (argv[k + 1], argv[k + 2]))
    rows = d.execute(q + ' ORDER BY ea_conf_ms', fetch=True)
    seen, OUT = set(), []
    for r_ in rows:
        k = (r_['ea_conf_ms'], r_['ea_cur_tf'], r_['ea_bias'])
        if k in seen:
            continue
        seen.add(k)
        tf = int(r_['ea_cur_tf']); c = int(r_['ea_conf_ms']); i = int(np.searchsorted(ts, c))
        side = 1 if r_['ea_bias'] == 'bull' else -1
        o4 = outc(i, side, 4.00)
        if o4 is None:
            continue
        o2 = outc(i, side, 2.22)
        w = tf * 60_000; b0 = (c // w) * w
        a, b = int(np.searchsorted(ts, b0)), int(np.searchsorted(ts, b0 + w))
        sg = px[a:max(b, a + 1)]
        rng = float((np.nanmax(sg) - np.nanmin(sg)) / np.nanmin(sg) * 100) if len(sg) else None
        br, bc = breach(tf, side, i)
        T = lambda x: int(ts[x]) if x is not None else None
        U = lambda x: u(int(ts[x])) if x is not None else None
        OUT.append((int(r_['ea_raw_ms']), u(int(r_['ea_raw_ms'])), c, u(c), (c // TF4) * TF4,
                    r_['ea_bias'], side, tf, float(px[i]), rng,
                    o2[1] if o2 else None, o2[0] if o2 else None,
                    (o2[0] / o2[1]) if (o2 and o2[1] > 1e-9) else None,
                    o4[1], o4[0], (o4[0] / o4[1]) if o4[1] > 1e-9 else None,
                    (o4[1] / rng) if rng and rng > 1e-9 else None,
                    T(br), U(br), T(bc), U(bc),
                    int(ts[o4[2]]), u(int(ts[o4[2]])), float(px[o4[2]]), int(o4[2] - i),
                    leg(i), 1 if W0 <= c < W1 else 0,
                    r_['ea_rpred_ms'], u(int(r_['ea_rpred_ms'])) if r_['ea_rpred_ms'] else None,
                    r_['ea_rpred_end_ms'], r_['ea_rpred_bars'], r_['ea_rpred_label']))
    if '--fresh' in argv:
        d.execute('DROP TABLE IF EXISTS rpl_exh_stat')
    d.execute(DDL)
    d.execute('DELETE FROM rpl_exh_stat')
    d.executemany('''INSERT INTO rpl_exh_stat (es_raw_ms,es_raw_utc,es_conf_ms,es_conf_utc,es_tf4_bar_ms,
     es_bias,es_side,es_cur_tf,es_px,es_bar_rng_pct,es_mae_222,es_mfe_222,es_ratio_222,
     es_mae_400,es_mfe_400,es_ratio_400,es_mae_over_rng,es_braw_ms,es_braw_utc,es_bcur_ms,es_bcur_utc,
     es_piv_ms,es_piv_utc,es_piv_px,es_piv_bars,es_leg_amp_pct,es_in_pine,
     es_rpred_ms,es_rpred_utc,es_rpred_end_ms,es_rpred_bars,es_rpred_label)
     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', OUT)
    n = d.execute('SELECT COUNT(*) c, SUM(es_in_pine) p, COUNT(es_rpred_ms) r FROM rpl_exh_stat', fetch=True)[0]
    # SUM() over an empty table is NULL, not 0, so this print raised TypeError ("%d ... not NoneType") and
    # the real fault — an exhaustion window that matched nothing — was never named. Coalesce, then abort
    # LOUDLY: a downstream chain must not run on an empty rpl_exh_stat and report it as a measurement.
    # Precedent for raising rather than falling back silently: rpl_walk.py's unknown-RPL_TAPE check.
    c, p, r = int(n['c'] or 0), int(n['p'] or 0), int(n['r'] or 0)
    print('rpl_exh_stat: %d rows, %d es_in_pine, es_rpred_ms set on %d' % (c, p, r))
    d.disconnect()
    if c == 0:
        raise SystemExit('build_exh_stat: 0 exhaustions in the window. rpl_exh_applied holds %d rows; '
                         'check that rpl_exhaust was rebuilt on THIS tape (build_exhaust.py --persist).'
                         % len(rows))


if __name__ == '__main__':
    main(sys.argv[1:])
