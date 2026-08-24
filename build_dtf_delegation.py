"""build_dtf_delegation — every dtf-free delegation moment, with the wsf facing direction.

Joe 0823: "when dtf flips to dtf-free, it needs to delegate to wsf (who will manage the trade
creation)" and "the stub will capture only the dtf-free delegation moments".

WHAT A DELEGATION MOMENT IS. The first bar of a dtf-free run, after Joe's 25-second gate: "require
a minimum 25s `held`, ie gate any dtf states that hold for less then 25s". A state that holds under
25 s does not happen - the surrounding state runs through it.

WHAT IS READ AT THAT BAR, Joe 0823 question 2: "wsf's dr will be set by the positioing of
gcws30Mage, ws1Mage and ws2Mage - if they are all > {100 - knob:20 fence} then dr = +1", mirrored
below 20. No hold. jig.wsf_facing_dr is the producer.

THE STUB is every delegation moment where the three do NOT all agree - `dds_stub` = 1. Joe 0823:
"if the Mages don't agree then capture the moment in a stub and we can investigate". Recorded,
acted on by nothing.

EVERY PRODUCER IS IMPORTED. domtf.guide_wire_dr, domtf.blocking_at's tagged masks, jig.wsf_facing_dr.
"""
import os, sys
import datetime as dt
from datetime import timezone
import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, BBLine, override, mech_lines
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis import ws_strat as WS
from optimus9.analysis.jig import wsf_facing_dr
from optimus9.analysis.domtf import guide_wire_dr
import build_momo_landed as B

WIN_FROM, WIN_TO = '2026-08-04 00:00:00', '2026-08-05 00:00:00'
DOM = [t for t in B.TFS if 13 <= t <= 27]
GW_TF, GW_XWOB = 13, 6           # the guide-wire and its hold. Joe 0823
MAGE_KNOB = 20                   # Joe 0823: "{100 - knob:20 fence}" -> 80 / 20
MIN_HELD_S, GRID = 25, 5         # Joe 0823: "require a minimum 25s `held`"
NOM = 3                          # nested-opposition count, Joe 0813
FACE = ['gcws30Mage', 'ws1Mage', 'ws2Mage']     # Joe 0823, question 2

DDL = '''CREATE TABLE IF NOT EXISTS dtf_delegation (
    dds_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    dds_knobs   VARCHAR(96) NOT NULL,
    dds_seq     INT NOT NULL,
    dds_utc     DATETIME NOT NULL,      -- the delegation moment: first bar of a gated dtf-free run
    dds_held_s  INT NOT NULL,           -- how long that free run lasts, seconds
    dds_dtf_dr  TINYINT NOT NULL,       -- the dr the ended blocked state was carrying
    dds_g30Mage DOUBLE, dds_ws1Mage DOUBLE, dds_ws2Mage DOUBLE,
    dds_wsf_dr  TINYINT NOT NULL,       -- +1 all three above 80, -1 all three below 20, 0 = no dr
    dds_stub    TINYINT NOT NULL,       -- 1 = the three did not agree. Recorded, acted on by nothing
    UNIQUE KEY uq_dds (dds_knobs, dds_seq), KEY k_utc (dds_utc))'''
COLS = ['dds_knobs','dds_seq','dds_utc','dds_held_s','dds_dtf_dr','dds_g30Mage','dds_ws1Mage',
        'dds_ws2Mage','dds_wsf_dr','dds_stub']


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary h, lo_boundary lo '
                    'FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(sy['h']), float(sy['lo'])
    MHI, MLO = 100.0 - MAGE_KNOB, float(MAGE_KNOB)
    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in set(list(WS.LINES) + FACE)}
    for g in mech_lines(db, 'wsf'):
        tf = g['tf_seconds'] // 60
        if f'ws{tf}{g["role"]}' in FACE:
            ovr[f'ws{tf}{g["role"]}'] = g['override']
    ovr[f'x{GW_TF}'] = override(GW_TF * 60, BBLine(length=5, mult=0.35, src='close'), 'emerging')
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr,
                          pxs_cfg={'src': sy['s'], 'len': sy['l']}, rebuild=False)
    ts = np.asarray(J.ts)
    i0 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_FROM)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    i1 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_TO)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    DR = guide_wire_dr(np.asarray(J.W.line(f'x{GW_TF}'), float), HI, LO, GW_XWOB)
    MG = [np.asarray(J.W.line(n), float) for n in FACE]
    WDR = wsf_facing_dr(MG, MHI, MLO)

    TAGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'optimus9', 'orchestration', '.ws_cache', 'tagged')
    TAG = {}
    for d, c in ((+1, 'u'), (-1, 'd')):
        for tf in DOM:
            f = os.path.join(TAGDIR, f'tag_{tf}_{c}_{B.K_WINDOW}_21_{i0}_{i1}.npy')
            if not os.path.exists(f):
                print(f'  MISSING cached mask {f}', flush=True); return 1
            TAG[(d, tf)] = np.load(f)

    def blocked(k):
        d = int(DR[k])
        if d == 0:
            return d, False
        b = [tf for tf in DOM if TAG[(d, tf)][k]]
        if b and sum(1 for tf in DOM if TAG[(-d, tf)][k] and tf < max(b)) >= NOM:
            b = []
        return d, bool(b)

    n = i1 - i0
    raw = np.zeros(n, bool); DRb = np.zeros(n, np.int8)
    for j, k in enumerate(range(i0, i1)):
        DRb[j], raw[j] = blocked(k)

    def runs_of(a):
        out = []; s = 0
        for j in range(1, len(a)):
            if a[j] != a[j - 1]:
                out.append([s, j, bool(a[s])]); s = j
        out.append([s, len(a), bool(a[s])]); return out

    g = raw.copy()
    while True:                                   # THE GATE. Repeated: absorbing one short run
        R = runs_of(g)                            # can leave a neighbour short
        short = [r for r in R if (r[1] - r[0]) * GRID < MIN_HELD_S]
        if not short:
            break
        r = short[0]; g[r[0]:r[1]] = not r[2]
    R = runs_of(g)

    knobs = (f'w0804_gw{GW_TF}_gx{GW_XWOB}_hi{HI:.0f}_lo{LO:.0f}_mk{MAGE_KNOB}'
             f'_mh{MIN_HELD_S}_no{NOM}')
    db.execute(DDL)
    had = db.execute('SELECT COUNT(*) c FROM dtf_delegation WHERE dds_knobs=%s',
                     (knobs,), fetch=True)[0]['c']
    if had:
        print(f'  replacing {had} rows at these knobs', flush=True)
        db.execute('DELETE FROM dtf_delegation WHERE dds_knobs=%s', (knobs,))

    rows = []; last_dr = 0; seq = 0
    for s, e, isb in R:
        if isb:
            d = next((int(DRb[j]) for j in range(s, e) if DRb[j] != 0), 0)
            if d: last_dr = d
            continue
        k = i0 + s; seq += 1
        rows.append((knobs, seq,
                     dt.datetime.fromtimestamp(int(ts[k]) / 1000, timezone.utc)
                       .strftime('%Y-%m-%d %H:%M:%S'),
                     (e - s) * GRID, last_dr,
                     float(MG[0][k]), float(MG[1][k]), float(MG[2][k]),
                     int(WDR[k]), int(WDR[k] == 0)))
    db.executemany(f'INSERT INTO dtf_delegation ({",".join(COLS)}) VALUES '
                   f'({",".join(["%s"] * len(COLS))})', rows)
    stub = sum(r[9] for r in rows)
    print(f'  dtf_delegation : {len(rows)} delegation moments   '
          f'wsf dr set {len(rows)-stub}   STUB {stub}   knobs {knobs}', flush=True)
    S = lambda v: {-1: '-1', 1: '+1', 0: 'none'}[v]
    print(f"\n  {'#':<4}{'delegated':<11}{'free held':>11}{'dtf dr':>8}{'gcws30Mage':>12}"
          f"{'ws1Mage':>10}{'ws2Mage':>10}{'wsf dr':>8}{'stub':>7}", flush=True)
    for r in rows:
        print(f"  {r[1]:<4}{r[2][11:]:<11}{f'{r[3]}s':>11}{S(r[4]):>8}{r[5]:>12.2f}"
              f"{r[6]:>10.2f}{r[7]:>10.2f}{S(r[8]):>8}{('yes' if r[9] else ''):>7}", flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
