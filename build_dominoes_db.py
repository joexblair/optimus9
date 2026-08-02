"""build_dominoes_db — bank the LTF-Mage dominoes dataset so questions are DB queries, not 90 s re-runs.

Joe 0801: "make your data rich and durable in a db table for optimised replies".

THE CONFIGURATION IS FIXED AND SINGULAR (Joe 0801: "we can't be using both")
  REWALK 2         walk to the next held s4Mage OOB crossing while s22 reads momo; repeat until it doesn't
  gcs15 confirm    the s15x X s15m cross is the ANCHOR, not the signal. The SIGNAL is the next
                   gcs15x X gcs15m cross at/after it.  gcs15 = x bb 5|0.37|close, m bb 6|0.45|close @ TF15s
                   (the gcs/RPL flavour gcs5 and s30 already use; gcs15 was cloned from s30).
                   Measured on 87 rows: MAE med 0.38 -> 0.28, ratio med 3.30 -> 4.19, +2.7 min lag.
  Nothing else is banked. REWALK 0 and the ungated s15 cross are NOT in these tables.

TWO TABLES, TWO GRAINS
  rpl_dominoes   one row per exhv2 SIGNAL. r-pred / walk / direction / branch / signal / exit, the three
                 LTF-Mage OOB->IB crossing bars, the dominoes verdicts, the divergence states, and the
                 trade scored under BOTH exit rules.
  rpl_walkcand   one row per s4Mage crossing into OOB inside a row's lifetime (r-pred bar -> exit bar),
                 HELD and poke alike, with s15/s22 momentum read at that bar and a flag for the one the
                 walk landed on. This is the table that answers "why did the walk land at X and not Y".

BANKED FOR BOTH REWALK 0 AND REWALK 2 (dm_rewalk / wc_rewalk). Nothing is chosen here.

THE EXIT LOOKAHEAD (Joe 0801, measured)
  held[z] requires the OOB run starting at z to last WALK_DWELL_BARS = 48 bars = 240 s. That verdict is
  only knowable at z+48, so taking the exit price at z uses 240 s of future. Both are banked:
    dm_exit_*  / dm_ret  / dm_mae   exit AT the crossing bar        (uses +240 s of future)
    dm_cexit_* / dm_cret / dm_cmae  exit at crossing + 48 bars      (confirmable live)

LINES
  s4Mage    build_exhv2.LINE_SPEC['M'] = bb 37|0.7|close @ TF4      the walk/exit producer
  LTF Mages gcs15M / s30M / s1M = bb 37|0.83|close @ TF 0.25/0.5/1.0 min   (rpl_config baseline flavour)
  s15r/s22r build_exhv2.R_SPEC                                       momentum, via build_exhv2.momo()
  DIVERGENCE  jig.pk_state core, L_DIV = 24 bars = 120 s, slope_floor = 0.5 (trade_book.py:39)

    python3 build_dominoes_db.py            # rebuild both tables
"""
import sys, os, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np
import build_exhv2 as B
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import bbline, kline
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.compute.pk5s_gate_computer import Pk5sGateComputer
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

MAGES = [('gcs15M', 0.25), ('s30M', 0.5), ('s1M', 1.0)]   # fastest first — the domino order
L_DIV, FLOOR = 24, 0.5
I = dict(conf=0, confu=1, tf=2, bias=3, walk=4, walku=5, side=6, mfeside=7, eff=8,
         branch=23, act=24, xtf=25, sig=28, sigu=29)

DDL_D = '''CREATE TABLE IF NOT EXISTS rpl_dominoes (
    dm_pk BIGINT AUTO_INCREMENT PRIMARY KEY, dm_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    dm_rewalk    TINYINT,                              -- 0 or 2, banked side by side
    dm_conf_ms   BIGINT, dm_conf_utc  VARCHAR(11),     -- the v1 exhaustion this ran from
    dm_cur_tf    INT,    dm_bias      VARCHAR(4),
    dm_rpred_ms  BIGINT, dm_rpred_utc VARCHAR(20),     -- the walk origin (rpl_exh_stat.es_rpred_ms)
    dm_walk_ms   BIGINT, dm_walk_utc  VARCHAR(20),     -- the HELD s4Mage crossing into OOB the walk landed on
    dm_walk_side VARCHAR(2), dm_dir VARCHAR(5),        -- hi->SHORT, lo->LONG. DIRECTION IS SET HERE.
    dm_walk_s4m  DOUBLE,  dm_hops INT,                 -- s4Mage at the walk bar; REWALK hops taken
    dm_mfe_side  TINYINT,                              -- s4Mage OOB side != the side the r-pred predicted
    dm_branch    VARCHAR(16), dm_action VARCHAR(4), dm_cross_tf INT,
    dm_sig_ms    BIGINT, dm_sig_utc VARCHAR(20), dm_sig_px DOUBLE,
    dm_walk_lead_min DOUBLE,                           -- signal minus walk bar
    dm_gcs15m_x_ms BIGINT, dm_s30m_x_ms BIGINT, dm_s1m_x_ms BIGINT,   -- OOB->IB crossing bar per LTF Mage
    dm_dom_strict TINYINT, dm_dom_loose TINYINT, dm_dom_reverse TINYINT,
    dm_div_gcs15m DOUBLE, dm_div_s30m DOUBLE, dm_div_s1m DOUBLE,      -- side-normalised pk_state
    dm_exit_ms  BIGINT, dm_exit_utc VARCHAR(20), dm_exit_px DOUBLE,
    dm_ret  DOUBLE, dm_mae  DOUBLE, dm_mfe  DOUBLE, dm_hold_min  DOUBLE,
    dm_cexit_ms BIGINT, dm_cexit_utc VARCHAR(20), dm_cexit_px DOUBLE,
    dm_cret DOUBLE, dm_cmae DOUBLE, dm_cmfe DOUBLE, dm_chold_min DOUBLE,
    KEY (dm_rewalk), KEY (dm_sig_ms), KEY (dm_dom_strict), KEY (dm_mfe_side), KEY (dm_conf_ms))'''

DDL_W = '''CREATE TABLE IF NOT EXISTS rpl_walkcand (
    wc_pk BIGINT AUTO_INCREMENT PRIMARY KEY, wc_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    wc_rewalk  TINYINT,
    wc_conf_ms BIGINT, wc_conf_utc VARCHAR(11), wc_rpred_ms BIGINT,
    wc_idx     INT,                                    -- position in the crossing chain after the r-pred
    wc_ms      BIGINT, wc_utc VARCHAR(20),
    wc_s4m     DOUBLE, wc_side VARCHAR(2),
    wc_run_bars INT,   wc_run_min DOUBLE,              -- length of the OOB run starting at this crossing
    wc_held    TINYINT,                                -- run >= WALK_DWELL_BARS (48 bars = 240 s)
    wc_chosen  TINYINT,                                -- the walk landed here
    wc_s15_state VARCHAR(8), wc_s15_slope DOUBLE, wc_s15_r2 DOUBLE, wc_s15_r DOUBLE,
    wc_s22_state VARCHAR(8), wc_s22_slope DOUBLE, wc_s22_r2 DOUBLE, wc_s22_r DOUBLE,
    KEY (wc_rewalk), KEY (wc_conf_ms), KEY (wc_ms), KEY (wc_held), KEY (wc_chosen))'''


def main(argv):
    ts = np.asarray(R.L0['ts'], np.int64)
    px = np.asarray(R.L0['src'].pxs, float)
    n = len(ts)
    HI, LO, D = R.HI, R.LO, B.WALK_DWELL_BARS
    u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')

    # --- lines -----------------------------------------------------------------------------------
    ovr = {}
    for k, (kd, sp) in B.LINE_SPEC.items():
        ovr.update(bbline('exhv2%s4' % k, 4, **sp))
    for tf in (15, 22):
        ovr.update(kline('exhv2r%d' % tf, tf, **B.R_SPEC[tf]))
    for nm, tf in MAGES:
        ovr.update(bbline(nm, tf, length=37, mult=0.83, src='close'))
    J = cache_jig_perline(R.end_ms, 40, 600, ovr, pxs_cfg=R.PXS_CFG)
    M4 = np.asarray(J.W.line('exhv2M4'), float)
    RL = {tf: np.asarray(J.W.line('exhv2r%d' % tf), float) for tf in (15, 22)}
    LNM = {nm: np.asarray(J.W.line(nm), float) for nm, _ in MAGES}

    # --- every s4Mage crossing into OOB, with its run length --------------------------------------
    o = (M4 >= HI) | (M4 <= LO)
    rise = o & ~np.r_[False, o[:-1]]
    RUN, held = {}, np.zeros(n, bool)
    for z in np.flatnonzero(rise):
        q = z
        while q < n and o[q]:
            q += 1
        RUN[int(z)] = q - z
        if q - z >= D:
            held[z] = True
    XB = np.flatnonzero(held)
    ALLX = np.flatnonzero(rise)

    # --- divergence, side-agnostic; normalised per row later ---------------------------------------
    ps = np.zeros(n); ps[L_DIV:] = px[L_DIV:] - px[:-L_DIV]
    DIV = {}
    for nm, _ in MAGES:
        v = LNM[nm]
        ls = np.zeros(n); ls[L_DIV:] = v[L_DIV:] - v[:-L_DIV]
        DIV[nm] = np.asarray(Pk5sGateComputer._pk_state_from_slopes(ls, ps, FLOOR), float)

    d = DatabaseManager(**get_db_config()); d.connect()
    RP = {int(z['es_conf_ms']): z['es_rpred_ms']
          for z in d.execute('SELECT es_conf_ms, es_rpred_ms FROM rpl_exh_stat', fetch=True)}

    ROWS_D, ROWS_W = [], []
    for mode in (0, 2):
        B.REWALK_HOPS = {}
        OUT = B.main(['--rewalk', str(mode)])
        HOPS = dict(B.REWALK_HOPS)
        for ro in OUT:
            if ro[I['sig']] is None:
                continue
            side = ro[I['side']]
            hi_side = (side == 'hi')
            sgn = -1.0 if hi_side else 1.0                 # hi -> SHORT
            sb = int(np.searchsorted(ts, ro[I['sig']]))
            wb = int(np.searchsorted(ts, ro[I['walk']]))
            rp = RP.get(int(ro[I['conf']]))

            # LTF-Mage OOB->IB crossing bar, read AT the signal bar (causal)
            j = []
            for nm, _ in MAGES:
                v = LNM[nm]
                oo = (v >= HI) if hi_side else (v <= LO)
                kk = np.flatnonzero(oo[:sb])
                j.append(None if oo[sb] or not len(kk) else int(kk[-1]) + 1)
            ok3 = all(x is not None for x in j)
            strict = ok3 and j[0] < j[1] < j[2]
            loose = ok3 and j[0] <= j[1] <= j[2]
            rev = ok3 and j[2] <= j[1] <= j[0]
            dsg = -1.0 if hi_side else 1.0
            dv = [float(DIV[nm][sb]) * dsg for nm, _ in MAGES]

            # trade, under both exit rules
            nx = XB[XB > sb]
            cells = {}
            for tag, off in (('', 0), ('c', D)):
                if not len(nx):
                    cells[tag] = (None, None, None, None, None, None, None)
                    continue
                eb = min(int(nx[0]) + off, n - 1)
                seg = px[sb:eb + 1]
                up = (np.nanmax(seg) - px[sb]) / px[sb] * 100.0
                dn = (px[sb] - np.nanmin(seg)) / px[sb] * 100.0
                cells[tag] = (int(ts[eb]), u(ts[eb]), float(px[eb]),
                              float(sgn * (px[eb] - px[sb]) / px[sb] * 100.0),
                              float(up if hi_side else dn), float(dn if hi_side else up),
                              (int(ts[eb]) - int(ts[sb])) / 60000.0)
            e, c = cells[''], cells['c']

            ROWS_D.append((mode, int(ro[I['conf']]), ro[I['confu']], ro[I['tf']], ro[I['bias']],
                           rp, u(rp) if rp else None,
                           int(ro[I['walk']]), u(ro[I['walk']]), side, 'SHORT' if hi_side else 'LONG',
                           float(M4[wb]), int(HOPS.get(ro[I['confu']], 0)), int(ro[I['mfeside']]),
                           ro[I['branch']], ro[I['act']], ro[I['xtf']],
                           int(ro[I['sig']]), u(ro[I['sig']]), float(px[sb]),
                           (int(ts[sb]) - int(ts[wb])) / 60000.0,
                           (int(ts[j[0]]) if j[0] is not None else None),
                           (int(ts[j[1]]) if j[1] is not None else None),
                           (int(ts[j[2]]) if j[2] is not None else None),
                           int(strict), int(loose), int(rev), dv[0], dv[1], dv[2],
                           e[0], e[1], e[2], e[3], e[4], e[5], e[6],
                           c[0], c[1], c[2], c[3], c[4], c[5], c[6]))

            # --- candidate chain: every crossing in the row's lifetime (r-pred bar -> exit bar) -----
            if rp is None:
                continue
            i0 = int(np.searchsorted(ts, int(rp)))
            i1 = int(np.searchsorted(ts, e[0])) if e[0] else n - 1
            dr = 1 if ro[I['bias']] == 'bull' else -1
            wt = 'hi' if dr > 0 else 'lo'
            for q, z in enumerate(ALLX[(ALLX > i0) & (ALLX <= i1)]):
                z = int(z)
                sd = 'hi' if M4[z] >= HI else 'lo'
                ed = (-dr if sd != wt else dr)
                s15 = B.momo(RL[15], ed, z); s22 = B.momo(RL[22], ed, z)
                ROWS_W.append((mode, int(ro[I['conf']]), ro[I['confu']], int(rp), q,
                               int(ts[z]), u(ts[z]), float(M4[z]), sd,
                               int(RUN[z]), RUN[z] * 5 / 60.0, int(bool(held[z])), int(z == wb),
                               s15[0], float(s15[1]), float(s15[2]), float(s15[3]),
                               s22[0], float(s22[1]), float(s22[2]), float(s22[3])))

    d.execute('DROP TABLE IF EXISTS rpl_dominoes'); d.execute(DDL_D)
    d.execute('DROP TABLE IF EXISTS rpl_walkcand'); d.execute(DDL_W)
    d.executemany('INSERT INTO rpl_dominoes (dm_rewalk,dm_conf_ms,dm_conf_utc,dm_cur_tf,dm_bias,'
                  'dm_rpred_ms,dm_rpred_utc,dm_walk_ms,dm_walk_utc,dm_walk_side,dm_dir,dm_walk_s4m,'
                  'dm_hops,dm_mfe_side,dm_branch,dm_action,dm_cross_tf,dm_sig_ms,dm_sig_utc,dm_sig_px,'
                  'dm_walk_lead_min,dm_gcs15m_x_ms,dm_s30m_x_ms,dm_s1m_x_ms,dm_dom_strict,dm_dom_loose,'
                  'dm_dom_reverse,dm_div_gcs15m,dm_div_s30m,dm_div_s1m,dm_exit_ms,dm_exit_utc,dm_exit_px,'
                  'dm_ret,dm_mae,dm_mfe,dm_hold_min,dm_cexit_ms,dm_cexit_utc,dm_cexit_px,dm_cret,dm_cmae,'
                  'dm_cmfe,dm_chold_min) VALUES (' + ','.join(['%s'] * 44) + ')', ROWS_D)
    d.executemany('INSERT INTO rpl_walkcand (wc_rewalk,wc_conf_ms,wc_conf_utc,wc_rpred_ms,wc_idx,wc_ms,'
                  'wc_utc,wc_s4m,wc_side,wc_run_bars,wc_run_min,wc_held,wc_chosen,wc_s15_state,'
                  'wc_s15_slope,wc_s15_r2,wc_s15_r,wc_s22_state,wc_s22_slope,wc_s22_r2,wc_s22_r)'
                  ' VALUES (' + ','.join(['%s'] * 21) + ')', ROWS_W)
    print('')
    print('rpl_dominoes  %d rows  (REWALK 0 and 2, %d each)' % (len(ROWS_D), len(ROWS_D) // 2))
    print('rpl_walkcand  %d rows  (every s4Mage crossing into OOB in each row lifetime)' % len(ROWS_W))
    for m in (0, 2):
        q = d.execute('SELECT COUNT(*) n, SUM(dm_dom_strict) s, SUM(dm_mfe_side) f, '
                      'SUM(dm_dir="SHORT") sh FROM rpl_dominoes WHERE dm_rewalk=%s', (m,), fetch=True)[0]
        print('  REWALK %d: %d signals, %d strict-dominoes, %d MFE-side, %d SHORT'
              % (m, q['n'], q['s'], q['f'], q['sh']))
    d.disconnect()
    return ROWS_D, ROWS_W


if __name__ == '__main__':
    main(sys.argv[1:])
