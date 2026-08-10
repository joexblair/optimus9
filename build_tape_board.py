"""build_tape_board — bank the JIG BOARD across the whole tape. Joe 0802.

WHY. Joe 0802 20:26: *"this morning I realised that using the tape data will massively improve your
predictions, so that is the mechanic now"*. The analogue scan (handover §3.2, idea §9.1) needs a live
board vector compared against a GROUP of similar historical boards. `rpl_jig` only holds today's
heartbeats — 2.8 months of tape exists only as a `Jig` rebuild, and a rebuild cannot run inside a 5-min
prediction cycle. So the board gets banked once, here, and queried thereafter.

MEASURED COST (probe 0802 20:24, this machine)
  import build_rpl_jig            105.8 s   ONE-OFF — this is the 2 min the handover warns about
  Jig build,  51,840 bars           1.8 s
  Jig build, 155,520 bars           4.6 s   -> ~34k bars/s, roughly linear
  full tape, 1,518,108 bars        ~45 s    expected

WHAT IT BANKS, per bar, to `rpl_tape_board` — a NEW table. It touches none of Joe's tables.
  - all 33 lines in J.LINES. `rpl_jig` banks only 21 of them as columns, so the tape carries a SUPERSET.
    A similarity vector can only use the 21 present in BOTH. The other 12 (jm4 jx4 jm22 jx22 js1x js1m
    js30x js30m jg5x jg5m jg5r jg15r) are banked because they are free at build time.
  - `pxs`, derived by the IDENTICAL code path as build_rpl_jig.py:241-251 — dema over event bars,
    forward-filled onto the 5 s grid. Not re-derived, copied.
  - the GATHER spread + signed boundary distance per small TF, same formula as build_rpl_jig.py:270-280.

WHAT IT DOES NOT BANK — deliberately.
  NO forward outcome. No "did it reach 0.9%", no MFE, no horizon column. Those are computed at QUERY time
  from the banked pxs. Two reasons: one source of truth, and storing a forward measure would freeze a
  horizon into the table — Joe's standing rule is no cap/horizon/window unless he specifies one.

CAUSALITY. Every row is a board AS AT its own bar. The scan reads rows strictly BEFORE the live bar.
Nothing here can leak forward, because no forward quantity is written.

WARMUP CAVEAT. Pre-05-07 klines were synthetic and were deleted 0802. The Jig's 48 h of warmup therefore
falls off the front of the data, so the earliest bars carry warming lines. They are banked as-is, NaN and
all — no truncation. The scan drops non-finite rows naturally.

    python3 build_tape_board.py            # full tape, ~05-07 00:00 -> now
    python3 build_tape_board.py --hours 24 # smoke test over a short window
    python3 build_tape_board.py --npz-only # skip the DB write, refresh the cache only
"""
import os, sys, time, re
os.environ.setdefault('RPL_TF_CEILING', '4')     # same ceiling the jig uses — momo/oob do not need TFS
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

HI, LO = 85.0, 15.0
NPZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tape_board.npz')
NAMES = sorted(J.LINES)                          # 33 line names, stable order — the vector's column order


def col(n):
    """Line name -> column name. MySQL column names are CASE-INSENSITIVE, so jM4/jm4, jM15/jm15 and
    jM22/jm22 collide as-is. Each uppercase letter becomes '_' + lowercase, which is deterministic and
    reversible: jM4 -> tb_j_m4 (s4Mage), jm4 -> tb_jm4 (s4m). The npz keeps the ORIGINAL names."""
    return 'tb_' + re.sub(r'([A-Z])', lambda m: '_' + m.group(1).lower(), n)

DDL = '''CREATE TABLE IF NOT EXISTS rpl_tape_board (
    tb_ms   BIGINT PRIMARY KEY,
    tb_utc  VARCHAR(20),
    tb_pxs  DOUBLE, tb_close DOUBLE,
    %s,
    tb_gsp_g5 DOUBLE, tb_gsp_g15 DOUBLE, tb_gsp_s30 DOUBLE, tb_gsp_s1 DOUBLE,
    tb_gbd_g5 DOUBLE, tb_gbd_g15 DOUBLE, tb_gbd_s30 DOUBLE, tb_gbd_s1 DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''' % ',\n    '.join('%s DOUBLE' % col(n) for n in NAMES)

SMALL_TF = ('g5', 'g15', 's30', 's1')
MG_OF = {'g5': 'jMg5', 'g15': 'jMg15', 's30': 'jMg30', 's1': 'jMg1'}


def u(ms):
    import datetime as dt
    return dt.datetime.utcfromtimestamp(ms / 1000).strftime('%m-%d %H:%M:%S')


def main():
    argv = sys.argv[1:]
    hours = int(argv[argv.index('--hours') + 1]) if '--hours' in argv else None
    npz_only = '--npz-only' in argv

    d = DatabaseManager(**get_db_config()); d.connect()
    row = d.execute('SELECT MIN(kc_timestamp) lo, MAX(kc_timestamp) hi FROM kline_collection', fetch=True)[0]
    lo_ms, hi_ms = int(row['lo']), int(row['hi'])
    if hours is None:
        hours = int((hi_ms - lo_ms) / 3600000) + 1
    print('tape %s .. %s   hours=%d' % (u(lo_ms), u(hi_ms), hours), flush=True)

    t0 = time.time()
    with Jig(hi_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=J.LINES) as j:
        ts = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src'])
        ei = np.flatnonzero(evt)
        pxs = np.full(len(src), np.nan)
        pxs[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        fin = np.isfinite(pxs)
        if fin.any():                                    # forward-fill onto the 5 s grid, as rpl_cache does
            ix = np.where(fin, np.arange(len(pxs)), 0)
            np.maximum.accumulate(ix, out=ix)
            pxs = pxs[ix]
            pxs[:int(np.argmax(fin))] = pxs[int(np.argmax(fin))]
        close = base['close'].to_numpy(float)
        L = {n: np.asarray(j.W.line(n), float) for n in NAMES}
    print('jig build %.1f s   bars %d   lines %d' % (time.time() - t0, len(ts), len(NAMES)), flush=True)

    # GATHER, vectorised — same measure as build_rpl_jig.py:270-280, one column set per small TF.
    # spread = max-min of {r, m, x, Mage}; bnd-dist = signed distance from the set median to its NEAR
    # boundary, negative once already through it.
    GSP, GBD = {}, {}
    for n in SMALL_TF:
        S = np.vstack([L['j%sr' % n], L['j%sm' % n], L['j%sx' % n], L[MG_OF[n]]])
        GSP[n] = np.nanmax(S, axis=0) - np.nanmin(S, axis=0)
        c = np.nanmedian(S, axis=0)
        GBD[n] = np.where(np.abs(c - LO) <= np.abs(c - HI), c - LO, HI - c)

    M = np.vstack([L[n] for n in NAMES]).T                 # (bars, 33) — the board vector, NAMES order
    np.savez_compressed(NPZ, ts=ts, pxs=pxs, close=close, board=M, names=np.array(NAMES),
                        gsp=np.vstack([GSP[n] for n in SMALL_TF]).T,
                        gbd=np.vstack([GBD[n] for n in SMALL_TF]).T)
    print('npz %s  %.0f MB' % (NPZ, os.path.getsize(NPZ) / 1e6), flush=True)
    if npz_only:
        d.disconnect(); return

    d.execute(DDL)
    cols = ['tb_ms', 'tb_utc', 'tb_pxs', 'tb_close'] + [col(n) for n in NAMES] \
           + ['tb_gsp_%s' % n for n in SMALL_TF] + ['tb_gbd_%s' % n for n in SMALL_TF]
    sql = 'INSERT IGNORE INTO rpl_tape_board (%s) VALUES (%s)' % (','.join(cols), ','.join(['%s'] * len(cols)))

    def nz(v):
        f = float(v)
        return None if not np.isfinite(f) else f

    t1 = time.time(); done = 0
    CH = 20000
    for a in range(0, len(ts), CH):
        b = min(a + CH, len(ts))
        rows = [tuple([int(ts[i]), u(ts[i]), nz(pxs[i]), nz(close[i])]
                      + [nz(M[i, k]) for k in range(M.shape[1])]
                      + [nz(GSP[n][i]) for n in SMALL_TF]
                      + [nz(GBD[n][i]) for n in SMALL_TF]) for i in range(a, b)]
        d.executemany(sql, rows, chunk=5000)
        done += len(rows)
        print('  banked %d / %d   %.0f s' % (done, len(ts), time.time() - t1), flush=True)
    n = d.execute('SELECT COUNT(*) n FROM rpl_tape_board', fetch=True)[0]['n']
    print('rpl_tape_board rows %d   total %.0f s' % (n, time.time() - t0), flush=True)
    d.disconnect()


if __name__ == '__main__':
    main()
