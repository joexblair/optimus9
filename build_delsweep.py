"""build_delsweep — sweep the DELEGATE SPLIT's catch-many TF for one chain, to see where its 6-of-9 lands.

The delegate split (rpl_walk.delegate_tf) picks the provisional's delegate from the exhaustion TF:
above `xpred_thresh` the -5 lookback applies; at or below it, `catch_many_tf`. This sweeps
`catch_many_tf` through a candidate list and reports the resulting flip-finisher timestamp per TF, so a
better-placed entry can be dialled in per chain.

SRP: the RULE lives in rpl_walk.delegate_tf (one definition, config-fed). This script only ORCHESTRATES —
it varies one knob and reads the chain out. Engine knobs live in rpl_config; this script's own inputs
(which TFs to try, which chain, which day) live in rpl_delsweep_conf, active row.

    python3 build_delsweep.py                 # run the active rpl_delsweep_conf row
    python3 build_delsweep.py --seed          # create/seed the conf table, then run
"""
import sys, datetime as dt
import optimus9.orchestration.rpl_walk as R
import build_rpl_6of9 as B
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

DDL = '''CREATE TABLE IF NOT EXISTS rpl_delsweep_conf (
    dsc_pk         BIGINT AUTO_INCREMENT PRIMARY KEY,
    dsc_created_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
    dsc_candidates VARCHAR(64),                      -- catch-many TFs to try, e.g. '5-60'
    dsc_day        VARCHAR(10),                      -- the walk day, e.g. '2026-06-13'
    dsc_target     VARCHAR(16),                      -- chain selector: rpl_micro.m_tid, e.g. '0613_01'
    dsc_is_active  TINYINT DEFAULT 0)'''
SEED = ('5-60', '2026-06-13', '0613_01')

# --- results: parent run + per-candidate cells (history accumulates; nothing is replaced) ---
DDL_RUN = '''CREATE TABLE IF NOT EXISTS rpl_delsweep (
    ds_pk          BIGINT AUTO_INCREMENT PRIMARY KEY,
    ds_conf_pk     BIGINT,                           -- -> rpl_delsweep_conf.dsc_pk (candidates + target that ran)
    ds_created_dt  DATETIME DEFAULT CURRENT_TIMESTAMP,
    ds_day         VARCHAR(10), ds_tid VARCHAR(16),  -- the chain swept
    ds_fire        VARCHAR(14), ds_tf INT, ds_branch VARCHAR(2), ds_de INT,
    ds_etf         INT,                              -- exhaustion TF (drives the delegate split)
    ds_current_tf  INT,                              -- climb rung at exhaustion ("EXHAUST cur=sNN")
    ds_candidates  VARCHAR(64),                      -- the spec as run
    ds_base_catch  INT,                              -- catch_many_tf in force at run time
    ds_split       INT,                              -- xpred_thresh in force at run time
    ds_market_cond VARCHAR(32),                      -- NULL until swing_detect supplies it
    INDEX (ds_day, ds_tid))'''
DDL_CELL = '''CREATE TABLE IF NOT EXISTS rpl_delsweep_cell (
    dsr_pk         BIGINT AUTO_INCREMENT PRIMARY KEY,
    dsr_run_pk     BIGINT NOT NULL,                  -- -> rpl_delsweep.ds_pk
    dsr_cand_tf    INT,                              -- the swept catch-many TF
    dsr_del_tf     INT,                              -- delegate TF it resolved to (differs above the split)
    dsr_rank       INT,                              -- 1..5 by LOWEST MAE; NULL outside the top 5
    dsr_outcome    VARCHAR(32),                      -- fire / dead-end / no gate open / no >=6-of-9
    dsr_prov_ms    BIGINT, dsr_prov_utc  VARCHAR(8), -- delegate cross (provisional)
    dsr_gate_ms    BIGINT, dsr_gate_utc  VARCHAR(8), dsr_gate_path VARCHAR(2),
    dsr_fire_ms    BIGINT, dsr_fire_utc  VARCHAR(8), -- the 6-of-9 fire
    dsr_lag_bars   INT,                              -- event bars, exhaustion -> delegate cross ("violence")
    dsr_xr         FLOAT,                            -- (x - r) on the delegate TF at the cross
    dsr_xr_slope   FLOAT,                            -- d(x-r)/bar over the preceding XR_SLOPE_LB bars
    dsr_vote       INT, dsr_vote_parts VARCHAR(64),  -- 6-of-9 count + per-set breakdown at the fire
    dsr_cap_bars   INT,                              -- bars from fire to the hs60x opposing breach (cap)
    dsr_px_prov    FLOAT, dsr_px_gate FLOAT, dsr_px_fire FLOAT,
    dsr_mfe        FLOAT, dsr_mae FLOAT, dsr_net FLOAT,
    INDEX (dsr_run_pk), INDEX (dsr_rank),
    CONSTRAINT fk_delsweep_cell_run FOREIGN KEY (dsr_run_pk) REFERENCES rpl_delsweep (ds_pk) ON DELETE CASCADE)'''
XR_SLOPE_LB = 6                                      # bars back for the x-r slope at the delegate cross
TOP_N = 5                                            # ranked by LOWEST mae (Joe 0727)

hm = lambda t: dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime('%H:%M:%S')


def parse_tfs(spec):
    """'12-17,22-27' -> [12..17, 22..27]. Inclusive ends."""
    out = []
    for part in spec.split(','):
        p = part.strip()
        if '-' in p:
            a, b = p.split('-'); out += list(range(int(a), int(b) + 1))
        elif p:
            out.append(int(p))
    return out


def load_conf(db, seed=False):
    """The ONE active sweep config. `seed` creates the table + an active row if none exists."""
    db.execute(DDL)
    if seed and not db.execute('SELECT 1 FROM rpl_delsweep_conf WHERE dsc_is_active=1', fetch=True):
        db.execute('INSERT INTO rpl_delsweep_conf (dsc_candidates,dsc_day,dsc_target,dsc_is_active) '
                   'VALUES (%s,%s,%s,1)', SEED)
    row = db.execute('SELECT * FROM rpl_delsweep_conf WHERE dsc_is_active=1 ORDER BY dsc_pk DESC LIMIT 1',
                     fetch=True)
    if not row:
        raise KeyError('no active rpl_delsweep_conf row — run with --seed')
    return row[0]


def activate(db, pk):
    """Exactly one active row (the gr_is_live pattern): promoting one demotes its siblings."""
    db.execute('UPDATE rpl_delsweep_conf SET dsc_is_active=0')
    db.execute('UPDATE rpl_delsweep_conf SET dsc_is_active=1 WHERE dsc_pk=%s', (pk,))


def sweep(cfg):
    day, tid = cfg['dsc_day'], cfg['dsc_target']
    cands = parse_tfs(cfg['dsc_candidates'])
    S = int(dt.datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    E = S + 24 * 3600 * 1000
    d = DatabaseManager(**get_db_config()); d.connect()
    hit = d.execute('SELECT DISTINCT m_fire,m_tf FROM rpl_micro WHERE m_day=%s AND m_tid=%s', (day, tid), fetch=True)
    d.disconnect()
    if not hit:
        raise KeyError(f'{tid} not in rpl_micro for {day} — run build_rpl_6of9.py --persist {day} first')
    want = (hit[0]['m_fire'], hit[0]['m_tf'])
    chain = next((c for c in B._fires(S, E)
                  if (dt.datetime.fromtimestamp(B.BP.te[c[2]] / 1000, dt.timezone.utc).strftime('%m%d %H:%M:%S'),
                      c[3]) == want), None)
    if chain is None:
        raise KeyError(f'no live chain matches {tid} ({want}) — rpl_micro may be stale')
    oi, de, ti, tf, br, tev = chain
    print('chain %s: fire %s s%d %s de%+d  | baseline catch_many_tf=%d, split at xpred_thresh=%d\n'
          % (tid, hm(B.BP.te[ti]), tf, br, de, R.CATCHMANY, R.XPRED_THRESH))
    saved, rows = R.CATCHMANY, []
    for c in cands:
        R.CATCHMANY = c
        mode, rec = B.trace_fire(oi, de, ti, tf, br, tev)
        rows.append(_cell(rec, c, de))
    R.CATCHMANY = saved
    ranked = sorted([r for r in rows if r['mae'] is not None], key=lambda r: r['mae'])[:TOP_N]
    for n, r in enumerate(ranked, 1):
        r['rank'] = n
    _persist(cfg, rows, dict(day=day, tid=tid, fire=hm(B.BP.te[ti]), tf=tf, br=br, de=de,
                             etf=rows[0]['etf'], cur=rows[0]['cur'], cands=cfg['dsc_candidates']))
    print('  %-6s | %-32s' % ('TF', '6of9 timestamp'))
    print('  %s-+-%s' % ('-' * 6, '-' * 32))
    for r in rows:
        note = '' if (r['del_tf'] is None or r['del_tf'] == r['cand']) else \
            '   (delegate resolved to s%d — above the split)' % r['del_tf']
        rk = '' if not r.get('rank') else '   #%d lowest MAE' % r['rank']
        print('  s%-5d | %-32s%s%s' % (r['cand'], r['stamp'], note, rk))
    return rows


def _cell(rec, cand, de):
    """One swept candidate -> every field the results table stores. Reads the chain trace only (no re-walk)."""
    import numpy as np
    get = lambda mech, sub=None: next(((tms, dec) for (_, m, tms, dec, _) in rec
                                       if m == mech and (sub is None or sub in dec)), (None, None))
    xt, xdec = get('x-cross-pred')
    pt, pdec = get('flip_provisional')
    gt, gdec = get('gate-open')
    ft, fdec = get('flip_finisher')
    etf = int(xdec.split(':')[0][1:]) if xdec else None
    cur = int(xdec.split('cur=s')[1]) if xdec and 'cur=s' in xdec else None
    dtf = int(pdec.split('del s')[1]) if pdec and 'del s' in pdec else None
    if ft is not None:                              stamp = hm(ft)
    elif dtf is None:                               stamp = 'dead-end (no delegate reversal)'
    elif any(m == 'gate' and 'NO GATE OPEN' in d for (_, m, _, d, _) in rec):
                                                    stamp = 'no gate open'
    else:                                           stamp = 'no >=6-of-9 before cap'
    px = lambda ms: None if ms is None else float(B.BP.epx[int(np.searchsorted(B.BP.te, ms))])
    gi = lambda ms: None if ms is None else int(np.searchsorted(B.gts, ms))
    xr = xrs = lag = None
    if dtf is not None and pt is not None:
        E = R.L0['E']; k = gi(pt)
        d_xr = np.asarray(E[dtf]['x'], float) - np.asarray(E[dtf]['r'], float)
        xr = float(d_xr[k])
        if k >= XR_SLOPE_LB:
            xrs = float((d_xr[k] - d_xr[k - XR_SLOPE_LB]) / XR_SLOPE_LB)
        lag = k - gi(xt) if xt is not None else None
    vote = parts = capb = mfe = mae = net = None
    if ft is not None:
        if 'vote ' in fdec:
            vote = int(fdec.split('vote ')[1].split('/')[0])
            parts = fdec.split('[')[1].split(']')[0] if '[' in fdec else None
        capb = B.cap_of(gi(ft), de) - gi(ft)
        _, mfe, mae = B.BP.lab.score(int(ft), -de); net = mfe - mae
    return dict(cand=cand, del_tf=dtf, rank=None, outcome=stamp.split(' (')[0], stamp=stamp,
                etf=etf, cur=cur, prov=pt, gate=gt, gate_path=(gdec.split('path ')[1].split(' ')[0] if gdec else None),
                fire=ft, lag=lag, xr=xr, xr_slope=xrs, vote=vote, parts=parts, cap_bars=capb,
                px_prov=px(pt), px_gate=px(gt), px_fire=px(ft), mfe=mfe, mae=mae, net=net)


def _persist(cfg, rows, meta):
    """Append one parent run + every cell. History accumulates — nothing is replaced."""
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute(DDL_RUN); d.execute(DDL_CELL)
    pk = d.execute('''INSERT INTO rpl_delsweep (ds_conf_pk,ds_day,ds_tid,ds_fire,ds_tf,ds_branch,ds_de,
                      ds_etf,ds_current_tf,ds_candidates,ds_base_catch,ds_split)
                      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                   (cfg['dsc_pk'], meta['day'], meta['tid'], meta['fire'], meta['tf'], meta['br'],
                    int(meta['de']), meta['etf'], meta['cur'], meta['cands'], R.CATCHMANY, R.XPRED_THRESH))
    d.executemany('''INSERT INTO rpl_delsweep_cell (dsr_run_pk,dsr_cand_tf,dsr_del_tf,dsr_rank,dsr_outcome,
        dsr_prov_ms,dsr_prov_utc,dsr_gate_ms,dsr_gate_utc,dsr_gate_path,dsr_fire_ms,dsr_fire_utc,
        dsr_lag_bars,dsr_xr,dsr_xr_slope,dsr_vote,dsr_vote_parts,dsr_cap_bars,
        dsr_px_prov,dsr_px_gate,dsr_px_fire,dsr_mfe,dsr_mae,dsr_net)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        [(pk, r['cand'], r['del_tf'], r['rank'], r['outcome'],
          r['prov'], hm(r['prov']) if r['prov'] else None,
          r['gate'], hm(r['gate']) if r['gate'] else None, r['gate_path'],
          r['fire'], hm(r['fire']) if r['fire'] else None,
          r['lag'], r['xr'], r['xr_slope'], r['vote'], r['parts'], r['cap_bars'],
          r['px_prov'], r['px_gate'], r['px_fire'], r['mfe'], r['mae'], r['net']) for r in rows])
    d.disconnect()
    print('  -> rpl_delsweep ds_pk=%d + %d cells\n' % (pk, len(rows)))


if __name__ == '__main__':
    seed = '--seed' in sys.argv
    db = DatabaseManager(**get_db_config()); db.connect()
    cfg = load_conf(db, seed=seed)
    db.disconnect()
    print('conf pk=%d  candidates=%s  day=%s  target=%s\n' % (
        cfg['dsc_pk'], cfg['dsc_candidates'], cfg['dsc_day'], cfg['dsc_target']))
    sweep(cfg)
