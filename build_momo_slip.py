"""build_momo_slip - rpl_momo_slip, the candidate-cross tape for momo_ride_oob_slip (Joe 0801).

Joe: "IF r is within {momo_ride_oob_slip = 2, knob} and a x-cross is created THEN allow the x-cross to
      fire the signal ... keep your data in a db table for fast analysis"

GRAIN: one row per CANDIDATE CROSS, not per slip. A slip value is then a query, not a rebuild:

    -- the fire bar at slip S, per event
    SELECT ms_conf_ms, MIN(ms_cross_ms) FROM rpl_momo_slip WHERE ms_gap <= S GROUP BY ms_conf_ms;

THE RULE
  fire = first s15x X s15m cross in the trade direction at or after the WALK bar where
           max(s15r, s22r) >= HI - slip   (bull)
           min(s15r, s22r) <= LO + slip   (bear)
  ms_gap holds that distance, so `ms_gap <= slip` IS the test. Either r line, whichever is closer.
  LARGER slip = looser = fires EARLIER. slip 0 = strict OOB. slip inf = today's A ungated signal.

THE STASH-AND-TEST (Joe 0801)
  "s15's trigger is stashed and s22r's momentum is tested. if s22 momo is false, allow s15's trigger
   to fire."
  So momentum is re-read AT EVERY CANDIDATE CROSS, not once at the walk bar. ms_s15_state /
  ms_s22_state hold that verdict, from the module-level build_exhv2.momo() - the same producer the
  walk-bar verdict uses, not a copy.

    -- stash-and-test fire at slip S: first cross inside the slip where the OTHER line is not momo
    SELECT ms_conf_ms, MIN(ms_cross_ms) FROM rpl_momo_slip
     WHERE ms_gap <= S AND ms_s15_state <> 'momo' AND ms_s22_state <> 'momo' GROUP BY ms_conf_ms;

HOW FAR FORWARD
  walk bar -> the first cross where BOTH lines are strict-OOB (ms_gap15 <= 0 AND ms_gap22 <= 0) AND
  neither line reads momo, inclusive. Not a cap: at that bar every rule variant on the table - either
  line, both lines, stash-and-test - has already fired, so no later cross is selectable by any of them.
  If a row never reaches it, every cross to the end of the tape is stored.

POPULATION  rpl_exhv2 rows with v2_s15_state or v2_s22_state = 'momo'
SCORING     find_pivots(px, SWING_PCT), next favourable pivot, exit-independent - the outc() shape from
            build_exh_stat.py:56. NON-CAUSAL, scoring only; the cross bars themselves are causal.
LINES       exhv2's own set (spec §13). x bb 4|0.37, m bb 6|0.45, r s15/s22 kline 10|4|11|close.

    python3 build_momo_slip.py [--persist] [--pct 1.00]
"""
import sys, datetime as dt
import numpy as np
import build_exhaust as X
import optimus9.orchestration.rpl_walk as R
from build_exhv2 import momo as B_momo          # the SAME producer the walk-bar verdict uses
from optimus9.analysis.jig import bbline, kline
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.compute.swing_detect import find_pivots
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

SWING_PCT = 1.00            # swing_detect pivot size, % - the scoring tape Joe named
TFS = (4, 15, 22)
LINE_SPEC = {'x': dict(length=4, mult=0.37, src='close'),
             'm': dict(length=6, mult=0.45, src='close'),
             'M': dict(length=37, mult=0.7, src='close')}
R_SPEC = {4: dict(k_len=7, rsi=6, stc=11, src='close'),
          15: dict(k_len=10, rsi=4, stc=11, src='close'),
          22: dict(k_len=10, rsi=4, stc=11, src='close')}

DDL = '''CREATE TABLE IF NOT EXISTS rpl_momo_slip (
    ms_pk        BIGINT AUTO_INCREMENT PRIMARY KEY, ms_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    ms_v2_pk     BIGINT,                              -- the rpl_exhv2 row this cross belongs to
    ms_conf_ms   BIGINT, ms_conf_utc VARCHAR(11),     -- the v1 exhaustion
    ms_walk_ms   BIGINT, ms_walk_utc VARCHAR(11), ms_walk_side VARCHAR(2),
    ms_eff_bias  VARCHAR(4), ms_branch VARCHAR(16),
    ms_walk_s15_state VARCHAR(8), ms_walk_s22_state VARCHAR(8),   -- the verdict AT THE WALK BAR
    ms_side      INT,                               -- +1 SHORT (hi walk) / -1 LONG (lo walk)
    ms_sig_ms    BIGINT, ms_sig_utc VARCHAR(11),      -- today's A ungated signal
    ms_cross_line VARCHAR(4),                         -- 's15' = s15x X s15m | 's4' = s4x X s4m
    ms_cross_seq INT,                                 -- 0-based within its own line, from the walk bar
    ms_cross_ms  BIGINT, ms_cross_utc VARCHAR(14),    -- THE CANDIDATE FIRE BAR
    ms_lag_min   DOUBLE,                              -- cross - today's signal, minutes
    ms_s15r      DOUBLE, ms_s22r DOUBLE,
    ms_gap       DOUBLE,                              -- r-units short of the boundary = the slip needed
    ms_gap15     DOUBLE, ms_gap22 DOUBLE,             -- the same, per line
    ms_s15_state VARCHAR(8), ms_s15_slope DOUBLE, ms_s15_r2 DOUBLE,   -- momentum AT THIS CROSS BAR
    ms_s22_state VARCHAR(8), ms_s22_slope DOUBLE, ms_s22_r2 DOUBLE,
    ms_s4m_val   DOUBLE, ms_s4r_val DOUBLE,           -- s4Mage / s4r at this cross bar
    ms_s4m_oob   TINYINT, ms_s4r_oob TINYINT,         -- 1 = OOB on the WALK SIDE (Joe 0801 patch)
    ms_is_sig    TINYINT,                             -- 1 = this cross IS today's signal bar
    ms_px        DOUBLE,
    ms_mfe       DOUBLE, ms_mae DOUBLE, ms_ratio DOUBLE,
    ms_piv_ms    BIGINT, ms_piv_utc VARCHAR(14), ms_piv_px DOUBLE,
    ms_swing_pct DOUBLE,
    KEY (ms_conf_ms), KEY (ms_gap), KEY (ms_v2_pk), KEY (ms_cross_ms))'''


def main(argv):
    global SWING_PCT
    if '--pct' in argv:
        SWING_PCT = float(argv[argv.index('--pct') + 1])
    X.rebuild_cache(120)
    ts = np.asarray(R.L0['ts'], np.int64)
    px = np.asarray(R.L0['src'].pxs, float)
    S = R.L0['src']
    ovr = {}
    for tf in TFS:
        for k, sp in LINE_SPEC.items():
            ovr.update(bbline('exhv2%s%d' % (k, tf), tf, **sp))
        ovr.update(kline('exhv2r%d' % tf, tf, **R_SPEC[tf]))
    J = cache_jig_perline(R.end_ms, 40, 600, ovr, pxs_cfg=R.PXS_CFG)
    EX = {tf: {k: np.asarray(J.W.line('exhv2%s%d' % (k, tf)), float) for k in ('x', 'm', 'M', 'r')}
          for tf in TFS}
    u = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%m%d %H:%M')
    us = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%m%d %H:%M:%S')

    Q = find_pivots(px, SWING_PCT)
    PV = [z[0] for z in Q]; KD = [z[1] for z in Q]

    def outc(i, side):
        """(mfe, mae, pivot_bar) to the next FAVOURABLE pivot. side +1 SHORT wants a Low."""
        want = 'L' if side > 0 else 'H'
        b = next((bb for bb, k in zip(PV, KD) if bb > i and k == want), None)
        if b is None:
            return None
        seg = px[i:b + 1]
        if side > 0:
            return (px[i] - np.nanmin(seg)) / px[i] * 100, (np.nanmax(seg) - px[i]) / px[i] * 100, int(b)
        return (np.nanmax(seg) - px[i]) / px[i] * 100, (px[i] - np.nanmin(seg)) / px[i] * 100, int(b)

    XC = {}

    def crosses(tf, xdr):
        """rising edge of s{tf}x crossing s{tf}m, cross_wob debounced at WOBN = 9 bars = 45 s."""
        k = (tf, xdr)
        if k not in XC:
            c = S.causal.cross_wob(EX[tf]['x'] - EX[tf]['m'], 0.0, xdr, R.WOBN)
            XC[k] = np.flatnonzero(c & ~np.r_[False, c[:-1]])
        return XC[k]

    d = DatabaseManager(**get_db_config()); d.connect()
    rows = d.execute('''SELECT v2_pk, v2_conf_ms, v2_conf_utc, v2_walk_ms, v2_walk_utc, v2_walk_side,
                               v2_eff_bias, v2_branch, v2_s15_state, v2_s22_state, v2_sig_ms, v2_sig_utc
                        FROM rpl_exhv2 WHERE v2_sig_ms IS NOT NULL
                          AND (v2_s15_state = 'momo' OR v2_s22_state = 'momo')
                        ORDER BY v2_sig_ms''', fetch=True)
    d.disconnect()

    OUT = []
    for r_ in rows:
        wb = int(np.searchsorted(ts, int(r_['v2_walk_ms'])))
        sb = int(np.searchsorted(ts, int(r_['v2_sig_ms'])))
        bull = r_['v2_eff_bias'] == 'bull'
        side = 1 if r_['v2_walk_side'] == 'hi' else -1
        xdr = -1 if r_['v2_walk_side'] == 'hi' else 1
        edr = 1 if bull else -1
        gp = lambda a: (R.HI - a) if bull else (a - R.LO)
        ob = lambda a: (a >= R.HI) if bull else (a <= R.LO)
        c15 = crosses(15, xdr); c15 = c15[c15 >= wb]
        c4 = crosses(4, xdr); c4 = c4[c4 >= wb]
        # --- SPAN END, slip-independent -------------------------------------------------------------
        # (a) the s15 stop: both r lines strict-OOB, neither reading momo, s4M + s4r both OOB
        # (b) the first s4x X s4m cross with s4M + s4r both OOB at/after the slip-0 stash (the LATEST
        #     stash any slip can produce, since a bigger slip stashes earlier)
        # span end = the LATER of the two, so every slip's fire bar is inside. Not a cap.
        gg15 = gp(EX[15]['r']); gg22 = gp(EX[22]['r'])
        end_a = len(ts) - 1
        for b in c15:
            b = int(b)
            if (gg15[b] <= 0 and gg22[b] <= 0 and ob(EX[4]['M'][b]) and ob(EX[4]['r'][b])
                    and B_momo(EX[15]['r'], edr, b)[0] != 'momo'
                    and B_momo(EX[22]['r'], edr, b)[0] != 'momo'):
                end_a = b; break
        z0 = c15[np.minimum(gg15[c15], gg22[c15]) <= 0.0]
        stash0 = int(z0[0]) if len(z0) else int(c15[-1]) if len(c15) else wb
        end_b = len(ts) - 1
        for b in c4[c4 >= stash0]:
            b = int(b)
            if ob(EX[4]['M'][b]) and ob(EX[4]['r'][b]):
                end_b = b; break
        span = max(end_a, end_b)
        seq = {'s15': 0, 's4': 0}
        cand = sorted([(int(b), 's15') for b in c15 if b <= span]
                      + [(int(b), 's4') for b in c4 if b <= span])
        for b, ln in cand:
            q = seq[ln]; seq[ln] += 1
            o = outc(b, side)
            g15 = gg15[b]; g22 = gg22[b]; gap = min(g15, g22)
            # momentum RE-READ at this cross bar, via the module-level producer (Joe 0801)
            m15 = B_momo(EX[15]['r'], edr, b)
            m22 = B_momo(EX[22]['r'], edr, b)
            # s4Mage / s4r OOB on the WALK SIDE - Joe 0801's patch: "IF s15x triggers AND s4M is oob
            # AND s4r is oob (all same-side) THEN fire"
            s4m = float(EX[4]['M'][b]); s4r = float(EX[4]['r'][b])
            o4m = int(ob(s4m)); o4r = int(ob(s4r))
            OUT.append((int(r_['v2_pk']), int(r_['v2_conf_ms']), r_['v2_conf_utc'],
                        int(r_['v2_walk_ms']), r_['v2_walk_utc'], r_['v2_walk_side'],
                        r_['v2_eff_bias'], r_['v2_branch'], r_['v2_s15_state'], r_['v2_s22_state'],
                        side, int(r_['v2_sig_ms']), r_['v2_sig_utc'], ln, q,
                        int(ts[b]), us(int(ts[b])), (int(ts[b]) - int(ts[sb])) / 60000.0,
                        float(EX[15]['r'][b]), float(EX[22]['r'][b]), float(gap),
                        float(g15), float(g22),
                        m15[0], float(m15[1]), float(m15[2]),
                        m22[0], float(m22[1]), float(m22[2]),
                        s4m, s4r, o4m, o4r,
                        1 if (b == sb and ln == 's15') else 0, float(px[b]),
                        (float(o[0]) if o else None), (float(o[1]) if o else None),
                        (float(o[0] / o[1]) if (o and o[1] > 1e-9) else None),
                        (int(ts[o[2]]) if o else None), (us(int(ts[o[2]])) if o else None),
                        (float(px[o[2]]) if o else None), SWING_PCT))
    print('rpl_momo_slip: %d candidate crosses across %d momo rows | swing_detect %.2f%%'
          % (len(OUT), len(rows), SWING_PCT))
    g = np.array([o[20] for o in OUT], float)
    print('  by line: s15 %d   s4 %d' % (sum(1 for o in OUT if o[13] == 's15'),
                                         sum(1 for o in OUT if o[13] == 's4')))
    print('  ms_gap r-units: min %.2f  median %.2f  max %.2f' % (g.min(), np.median(g), g.max()))
    print('  momo at the cross bar: s15 %d  s22 %d  either %d  of %d crosses'
          % (sum(1 for o in OUT if o[23] == 'momo'), sum(1 for o in OUT if o[26] == 'momo'),
             sum(1 for o in OUT if o[23] == 'momo' or o[26] == 'momo'), len(OUT)))
    print('  s4M oob %d   s4r oob %d   both %d'
          % (sum(1 for o in OUT if o[31]), sum(1 for o in OUT if o[32]),
             sum(1 for o in OUT if o[31] and o[32])))
    print('  crosses per row: min %d  median %.0f  max %d'
          % (min(sum(1 for o in OUT if o[0] == p) for p in set(o[0] for o in OUT)),
             np.median([sum(1 for o in OUT if o[0] == p) for p in set(o[0] for o in OUT)]),
             max(sum(1 for o in OUT if o[0] == p) for p in set(o[0] for o in OUT))))
    if '--persist' in argv:
        d = DatabaseManager(**get_db_config()); d.connect()
        # rpl_momo_slip is this mechanic's own table, created 0801 in this session and read by nothing
        # else. The schema grew (per-cross momentum), so drop-and-recreate rather than ALTER. No table
        # Joe uses is touched.
        d.execute('DROP TABLE IF EXISTS rpl_momo_slip')
        d.execute(DDL)
        d.executemany('''INSERT INTO rpl_momo_slip (ms_v2_pk,ms_conf_ms,ms_conf_utc,ms_walk_ms,
            ms_walk_utc,ms_walk_side,ms_eff_bias,ms_branch,ms_walk_s15_state,ms_walk_s22_state,ms_side,
            ms_sig_ms,ms_sig_utc,ms_cross_line,ms_cross_seq,ms_cross_ms,ms_cross_utc,ms_lag_min,
            ms_s15r,ms_s22r,ms_gap,ms_gap15,ms_gap22,ms_s15_state,ms_s15_slope,ms_s15_r2,
            ms_s22_state,ms_s22_slope,ms_s22_r2,ms_s4m_val,ms_s4r_val,ms_s4m_oob,ms_s4r_oob,
            ms_is_sig,ms_px,ms_mfe,ms_mae,ms_ratio,ms_piv_ms,ms_piv_utc,ms_piv_px,ms_swing_pct)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', OUT)
        print('persisted %d rows to rpl_momo_slip' % len(OUT))
        d.disconnect()
    return OUT


if __name__ == '__main__':
    main(sys.argv[1:])
