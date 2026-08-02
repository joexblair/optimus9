"""build_s33curl — s33r curl moments by TOPOLOGICAL PERSISTENCE. Joe 0801.

WHY PERSISTENCE (researched 0801, replacing a band+separation detector)
  s33r is a 33-minute line rendered on the 5 s grid, so it has a local extreme near every bar close.
  The previous detector thinned those with a 33-min separation filter, which produced runs of up to
  11 events at EXACTLY 33-min spacing — 100% of its gaps were 33 +- 1 min. The cadence, not the line,
  was doing the work.
  Superlevel-set persistence removes the artefact by construction: an intra-bar wiggle is born and
  dies within a fraction of an r-unit, so a single threshold in r-units filters it. At threshold 12
  the 33-min gap share drops from 100% to 0.0%.
    birth       the value of a local maximum, as a descending level reaches it
    death       the value of the lower local minimum where its island merges into a taller one
    PERSISTENCE birth - death, in r-units on 0..100
    pairing     at a saddle, the island with the LOWER birth dies into the higher
  One parameter, nested (raising it only removes), no window, no smoothing, no separation. O(n log n).
  Refs: Weinkauf's persistence1d (csc.kth.se/~weinkauf/notes/persistence1d.html),
        Huber, "Persistent Topology for Peak Detection" (sthu.org/blog/13-perstopology-peakdetection).

CAUSALITY
  Persistence as implemented is NON-CAUSAL — it sorts every index by value before pairing. That is
  correct for RETROSPECTIVE marking, which is what this dataset and the pine are for.
  The online counterpart is exact rather than approximate: a maximum has persistence >= M the moment
  the series falls M below it. That is a retrace rule, past data only, confirmed late — same M, same
  event set. bp50 live would use that form.

  line       s33r = kline 10|5|12|close at TF33  (Joe 0801)
  PRIMARY    persistence >= P_PRIMARY   — red (peak) / green (trough)
  SECONDARY  P_SECONDARY <= p < P_PRIMARY — blue (peak) / yellow (trough)

NOTE: there is no persistence producer in the repo (`find_pivots` is a percentage ZigZag on price),
so `persistence()` below is new logic, not a fork. If adopted it belongs in the jig.

    python3 build_s33curl.py [--persist] [--start 2026-05-24] [--days 7] [--p1 20] [--p2 8]
"""
import sys, os, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np
import optimus9.orchestration.rpl_walk as R
from optimus9.orchestration.rpl_cache import cache_jig_perline, _line_key, _tape_key, LINE_DIR, TAPE_DIR
from optimus9.analysis.jig import kline, _Score
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

END_MS, HOURS, WARMUP = int(dt.datetime(2026, 8, 1, tzinfo=dt.timezone.utc).timestamp() * 1000), 40, 1248
S33R = kline('s33r', 33, k_len=10, rsi=5, stc=12, src='close')
TF4 = 240_000
OUT = 's33curl_tf4.pine'

DDL = '''CREATE TABLE IF NOT EXISTS rpl_s33curl (
    sc_pk     BIGINT AUTO_INCREMENT PRIMARY KEY, sc_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    sc_ms     BIGINT, sc_utc VARCHAR(20),
    sc_tier   VARCHAR(9), sc_kind VARCHAR(6),
    sc_r      DOUBLE, sc_dist DOUBLE,
    sc_persist DOUBLE,                          -- birth - death, r-units
    sc_prev_ms BIGINT, sc_gap_min DOUBLE,
    sc_line   VARCHAR(32), sc_p1 DOUBLE, sc_p2 DOUBLE,
    KEY (sc_ms), KEY (sc_tier), KEY (sc_persist))'''


def persistence(v):
    """Superlevel-set persistence of the local MAXIMA of v -> [(idx, persistence)].
    Descending water level: an island is born at a local max, dies where it merges into a taller
    island at a saddle. persistence = birth - death. Global max -> +inf. O(n log n) via union-find."""
    n = len(v)
    comp = np.full(n, -1, np.int64)
    birth, out = {}, []

    def find(x):
        while comp[x] != x:
            comp[x] = comp[comp[x]]; x = comp[x]
        return x

    for i in np.argsort(-v, kind='stable'):
        i = int(i)
        L = i - 1 if i > 0 and comp[i - 1] != -1 else None
        Rt = i + 1 if i < n - 1 and comp[i + 1] != -1 else None
        if L is None and Rt is None:
            comp[i] = i; birth[i] = v[i]
        elif Rt is None:
            comp[i] = find(L)
        elif L is None:
            comp[i] = find(Rt)
        else:
            a, b = find(L), find(Rt)
            hi, dead = (a, b) if birth[a] >= birth[b] else (b, a)
            out.append((dead, float(birth[dead] - v[i])))
            comp[dead] = hi; comp[i] = hi
    for r_ in {find(i) for i in range(n)}:
        out.append((r_, float('inf')))
    return out


def extrema(v):
    """maxima and minima with persistence -> [(idx, persistence, kind)] sorted by idx."""
    return sorted([(i, p, 'peak') for i, p in persistence(v)]
                  + [(i, p, 'trough') for i, p in persistence(-v)])


def main(argv):
    g = lambda f, d: (type(d)(argv[argv.index(f) + 1]) if f in argv else d)
    start, days = g('--start', '2026-05-24'), g('--days', 7)
    P1, P2 = g('--p1', 20.0), g('--p2', 8.0)
    a_ms = int(dt.datetime(*[int(x) for x in start.split('-')], tzinfo=dt.timezone.utc).timestamp() * 1000)
    b_ms = a_ms + days * 86_400_000
    u = lambda t: dt.datetime.fromtimestamp(int(t) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')

    cache_jig_perline(END_MS, HOURS, WARMUP, S33R, pxs_cfg=R.PXS_CFG)
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP, R.PXS_CFG) + '.npz'))['__ts__']
    s = np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP, S33R['s33r']) + '.npy'))
    A, B = int(np.searchsorted(ts, a_ms)), int(np.searchsorted(ts, b_ms))
    v = s[A:B]
    print('s33r %r' % (S33R['s33r'],))
    print('window %s .. %s  (%d bars, %.1f d)  persistence tiers: primary >= %.0f, secondary >= %.0f'
          % (u(ts[A]), u(ts[B - 1]), B - A, (ts[B - 1] - ts[A]) / 86400000, P1, P2))

    ex = [(i, p, k) for i, p, k in extrema(v) if np.isfinite(p) and p >= P2]
    OUTR = []
    for tier, sel in (('primary', [e for e in ex if e[1] >= P1]),
                      ('secondary', [e for e in ex if e[1] < P1])):
        prev = None
        for i, p, k in sel:
            t = int(ts[A + i]); r = float(v[i])
            OUTR.append((t, u(t), tier, k, r, min(abs(r - 85.0), abs(r - 15.0)), p,
                         prev, ((t - prev) / 60000.0 if prev else None),
                         'kline 10|5|12|close @TF33', P1, P2))
            prev = t

    for tier in ('primary', 'secondary'):
        rows = [o for o in OUTR if o[2] == tier]
        gaps = [o[8] for o in rows if o[8]]
        print('')
        print('  %s — %d events (%.1f/day)%s' % (tier.upper(), len(rows), len(rows) / days,
              ('  gaps: median %.0f min, %.1f%% at 33+-1' %
               (np.median(gaps), 100.0 * np.mean([(32 < x < 34) for x in gaps])) if gaps else '')))
        print('   utc                 | kind   |  s33r | dist 85/15 | persist | gap min')
        for o in rows:
            print('   %s | %-6s | %5.2f | %10.2f | %7.2f | %s'
                  % (o[1], o[3], o[4], o[5], o[6], ('%.0f' % o[8]) if o[8] else '-'))

    if '--persist' in argv:
        d = DatabaseManager(**get_db_config()); d.connect()
        d.execute('DROP TABLE IF EXISTS rpl_s33curl')      # schema changed: sc_persist replaces sc_band/sc_sep_min
        d.execute(DDL)
        d.executemany('''INSERT INTO rpl_s33curl (sc_ms,sc_utc,sc_tier,sc_kind,sc_r,sc_dist,sc_persist,
            sc_prev_ms,sc_gap_min,sc_line,sc_p1,sc_p2) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', OUTR)
        print('')
        print('persisted %d rows to rpl_s33curl' % len(OUTR))
        d.disconnect()

    bkt = lambda m: (int(m) // TF4) * TF4
    pick = lambda tier, kind: [bkt(o[0]) for o in OUTR if o[2] == tier and o[3] == kind]
    streams = [                                        # order IS priority — primary paints over secondary
        {'name': 'sec_peak',    'ts': pick('secondary', 'peak'),   'color': 'color.blue'},
        {'name': 'sec_trough',  'ts': pick('secondary', 'trough'), 'color': 'color.yellow'},
        {'name': 'curl_peak',   'ts': pick('primary', 'peak'),     'color': 'color.red'},
        {'name': 'curl_trough', 'ts': pick('primary', 'trough'),   'color': 'color.green'},
    ]
    notes = ('s33curl | red=PRIMARY peak  green=PRIMARY trough  blue=secondary peak  yellow=secondary trough'
             ' | TF4 buckets | s33r kline 10|5|12|close @TF33 | TOPOLOGICAL PERSISTENCE (birth-death,'
             ' r-units): primary >= %.0f, secondary %.0f..%.0f | no window, no separation filter'
             ' | window %s .. %s | NON-CAUSAL (retrospective marking); the causal form is a retrace at'
             ' the same threshold' % (P1, P2, P1, u(a_ms)[:5], u(b_ms)[:5]))
    total = _Score(None).emit_bgcolor(streams, OUT, 's33r curl moments (TF4)', notes=notes)
    print('')
    print('%s  ->  %d painted bars' % (OUT, total))
    for nm, st in zip(('curl_peak   red   ', 'curl_trough green ', 'sec_peak    blue  ', 'sec_trough  yellow'),
                      (streams[2], streams[3], streams[0], streams[1])):
        print('  %-19s %3d events -> %3d distinct TF4 bars' % (nm, len(st['ts']), len(set(st['ts']))))
    return OUTR


if __name__ == '__main__':
    main(sys.argv[1:])
