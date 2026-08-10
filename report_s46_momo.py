"""report_s46_momo — the momo mechanic's result, MAE only. Joe 0804.

PURE READER over s46_momo + s46_momo_leg. The race is a SUBSET CHOICE made here, not in the builder:
every one of the six legs was banked with its own fire bar and its own MAE, so

    mechanic exit = min(s6gated, chosen race legs)

is a query. `s6raw` is the baseline - the current strategy's exit, ungated, unchanged.

    LEGS   x15r x15b x15M x22r x22b x22M   (x = the TF's x line, target = r / boundary / Mage)
    --legs x15b,x15M          Joe's original two, s15 only
    --legs all                all six
    --rwob 1                  race-leg wobble in bars

    python3 report_s46_momo.py [--legs all] [--rwob 1] [--trade 07-29 03:03:15]
"""
import sys, os, itertools, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

# Joe 0804: "now that I'm investigating the earlier-than 00:40 signal, I see that s15Mage and s22Mage
# should not be involved in the exit race". x15M / x22M stay BANKED in s46_momo_leg - the builder is
# unchanged - but they are out of the subset universe. --withmage puts them back.
ALL = ('x15r', 'x15b', 'x22r', 'x22b')
MAGE = ('x15M', 'x22M')


def main(argv):
    g = lambda f, d: (argv[argv.index(f) + 1] if f in argv else d)
    rwob, gwob = int(g('--rwob', '1')), int(g('--gwob', '1'))
    universe = (ALL + MAGE) if '--withmage' in argv else ALL
    legs = universe if g('--legs', 'all') == 'all' else tuple(g('--legs', 'all').split(','))
    d = DatabaseManager(**get_db_config()); d.connect()
    T = d.execute('SELECT * FROM s46_momo WHERE mo_rwob=%s AND mo_gwob=%s ORDER BY mo_entry_ms',
                  (rwob, gwob), fetch=True)
    L = d.execute('SELECT * FROM s46_momo_leg WHERE ml_rwob=%s AND ml_gwob=%s', (rwob, gwob), fetch=True)
    grid = d.execute('SELECT DISTINCT ml_rwob,ml_gwob FROM s46_momo_leg ORDER BY ml_gwob,ml_rwob',
                     fetch=True)
    GL = d.execute('SELECT ml_entry_ms,ml_rwob,ml_gwob,ml_leg,ml_mae,ml_hold_bars,ml_fire_ms '
                   'FROM s46_momo_leg', fetch=True)
    d.disconnect()
    if not T:
        raise SystemExit('s46_momo has no rows at rwob %d gwob %d' % (rwob, gwob))
    M = {}
    for r in L:
        M.setdefault(r['ml_entry_ms'], {})[r['ml_leg']] = r
    print('%d trades   race wobble %d bar(s) = %d s   gate wobble %d bar(s) = %d s   legs: %s'
          % (len(T), rwob, rwob * 5, gwob, gwob * 5, ','.join(legs)))
    print()
    print('  %-3s %-18s %-6s %-18s %-6s %-18s %-8s %6s %6s %8s %8s'
          % ('#', 'entry utc', 'side', 'gate opens', 'src', 'exit utc', 'leg', 'hold',
             'holdb', 'MAE', 'MAEbase'))
    mech, base, mh, bh = [], [], [], []
    for i, r in enumerate(T, 1):
        m = M.get(r['mo_entry_ms'], {})
        if 's6raw' not in m:
            continue
        b = m['s6raw']; base.append(b['ml_mae']); bh.append(b['ml_hold_bars'])
        pool = {k: m[k] for k in (('s6gated',) + tuple(legs)) if k in m}
        k = min(pool, key=lambda z: pool[z]['ml_fire_ms']) if pool else 's6raw'
        w = pool[k] if pool else b
        mech.append(w['ml_mae']); mh.append(w['ml_hold_bars'])
        print('  %-3d %-18s %-6s %-18s %-6s %-18s %-8s %6d %6d %8.3f %8.3f'
              % (i, r['mo_entry_utc'], 'LONG' if r['mo_dr'] > 0 else 'SHORT',
                 r['mo_gate_utc'] or '-', r['mo_gate_src'], w['ml_fire_utc'], k,
                 w['ml_hold_bars'], b['ml_hold_bars'], w['ml_mae'], b['ml_mae']))
    mech, base = np.array(mech), np.array(base)
    mh, bh = np.array(mh), np.array(bh)
    print()
    print('  MAE  baseline (s6raw) mean %.3f  median %.3f  max %.3f'
          % (base.mean(), np.median(base), base.max()))
    print('  MAE  mechanic         mean %.3f  median %.3f  max %.3f'
          % (mech.mean(), np.median(mech), mech.max()))
    print('  HOLD baseline         mean %.0f  median %.0f bars   |   mechanic mean %.0f  median %.0f'
          % (bh.mean(), np.median(bh), mh.mean(), np.median(mh)))
    print('  changed %d of %d   cut %d   raised %d   |   shorter %d   longer %d   '
          'exits inside 12 bars = 60 s: base %d  mech %d'
          % (int((mech != base).sum()), len(base), int((mech < base).sum()),
             int((mech > base).sum()), int((mh < bh).sum()), int((mh > bh).sum()),
             int((bh <= 12).sum()), int((mh <= 12).sum())))

    # --- the whole (gwob x rwob x leg-subset) grid, MAE with hold alongside ----------------------
    G = {}
    for r in GL:
        G.setdefault((r['ml_rwob'], r['ml_gwob']), {}).setdefault(r['ml_entry_ms'], {})[r['ml_leg']] = r
    print()
    print('=== every gate wobble x race wobble x leg subset, ranked by MAE mean ===')
    print('  %-5s %-5s %-28s %5s %8s %8s %8s %8s'
          % ('GWOB', 'RWOB', 'legs', 'chgd', 'MAEmean', 'MAEmed', 'MAEmax', 'holdmed'))
    out = []
    for (rw, gw), MM in G.items():
        bmae = np.array([MM[e]['s6raw']['ml_mae'] for e in MM if 's6raw' in MM[e]])
        for k in range(0, len(universe) + 1):
            for sub in itertools.combinations(universe, k):
                v, hh = [], []
                for e, m in MM.items():
                    if 's6raw' not in m:
                        continue
                    pool = {q: m[q] for q in (('s6gated',) + sub) if q in m}
                    z = min(pool.values(), key=lambda y: y['ml_fire_ms']) if pool else m['s6raw']
                    v.append(z['ml_mae']); hh.append(z['ml_hold_bars'])
                v, hh = np.array(v), np.array(hh)
                out.append((v.mean(), np.median(v), v.max(), int((v != bmae).sum()),
                            np.median(hh), gw, rw, ','.join(sub) if sub else '(s6gated only)'))
    for r in sorted(out)[:20]:
        print('  %-5d %-5d %-28s %5d %8.3f %8.3f %8.3f %8.0f'
              % (r[5], r[6], r[7], r[3], r[0], r[1], r[2], r[4]))
    print('  %-5s %-5s %-28s %5d %8.3f %8.3f %8.3f %8.0f'
          % ('-', '-', 'BASELINE s6raw', 0, base.mean(), np.median(base), base.max(), np.median(bh)))
    print()
    print('  grid: %s' % ', '.join('gwob %d/rwob %d' % (r['ml_gwob'], r['ml_rwob']) for r in grid))


if __name__ == '__main__':
    main(sys.argv[1:])
