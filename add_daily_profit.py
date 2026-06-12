"""
add_daily_profit — per combo in gate_both_top300, at the realistic in-zone stop 0.33
(Joe's manual stop; the math-optimum 0.05 is a smoothed-px mirage), compute:
  profit_033  = avg net %/trade   (the "winning bucket value")
  daily_033   = profit_033 × per_day   (expected total daily profit, % per day)
Same win-vs-stop race as add_optimum_stop, stop fixed at 0.33, take W = 0.9% swing.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.orchestration import bl_group_grind as G
from optimus9.orchestration.gate_signal_sweep import pine_aligned_signals
from optimus9.analysis.bl_detect import GCA5M_RAW
from optimus9.analysis.bl_grind import walk

NAMES = ['b6b', 'hb15b', 'hb9b', 'hs15r', 'hs9r', 's18b', 's30r', 's90b']
STOP = 0.33
HORIZON = 2160
TABLE = 'gate_both_top300'


def main():
    G.prepare(); G.precompute()
    db = DatabaseManager(**get_db_config()); db.connect()
    base, mask = G._CTX['base'], G._CTX['mask']
    idx, dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=True, gate_bb=True, gate_k=True)
    full = np.zeros(len(mask), np.int8); full[idx] = dirs
    raw = full[mask]
    piv, lb = G._CTX['pivots'], G._CTX['pk_lookback']
    W = float(G.active_config()['bgc_swing_pct'])
    day = float(G.active_config()['bgc_window_days'])
    px = np.asarray(G._CTX['px'], float)

    cache = {}
    def outcome(i, d):
        if (i, d) not in cache:
            seg = px[i + 1:i + 1 + HORIZON]
            if len(seg) == 0:
                cache[(i, d)] = 0.0
            else:
                rel = (seg - px[i]) / px[i] * 100.0 * d
                adv = np.maximum.accumulate(np.maximum(0.0, -rel))
                won = rel >= W
                if won.any():
                    wi = int(np.argmax(won)); mbw = float(adv[:wi].max()) if wi > 0 else 0.0
                    cache[(i, d)] = W if STOP > mbw else -STOP
                else:
                    cache[(i, d)] = -STOP if STOP <= float(adv[-1]) else 0.0
        return cache[(i, d)]

    rows = db.execute(f'SELECT combo, per_day FROM {TABLE}', fetch=True)
    upd = []
    for r in rows:
        vals = [int(x) for x in r['combo'].split(',')]
        states = [G._STATES[(NAMES[i], vals[i])] for i in range(len(NAMES))]
        trades = walk(G._refold(states), raw, px, piv, lb)
        ents = [(t['open_i'], t['dir']) for t in trades]
        if not ents:
            upd.append((None, None, r['combo'])); continue
        ppt = sum(outcome(*e) for e in ents) / len(ents)
        upd.append((round(ppt, 4), round(ppt * (r['per_day'] or 0), 4), r['combo']))

    for col in ('profit_033', 'daily_033'):
        if col not in [c['Field'] for c in db.execute(f'SHOW COLUMNS FROM {TABLE}', fetch=True)]:
            db.execute(f'ALTER TABLE {TABLE} ADD COLUMN {col} FLOAT')
    for ppt, dly, combo in upd:
        db.execute(f'UPDATE {TABLE} SET profit_033=%s, daily_033=%s WHERE combo=%s', (ppt, dly, combo))
    db.execute(f'DROP VIEW IF EXISTS v_{TABLE}')
    db.execute(f'CREATE VIEW v_{TABLE} AS SELECT * FROM {TABLE} ORDER BY daily_033 DESC')
    db.disconnect()

    ok = [(c, p, d) for p, d, c in upd if p is not None]
    pa = np.array([p for _, p, _ in ok]); da = np.array([d for _, _, d in ok])
    print(f'{len(ok)} combos · profit_033/trade med {np.median(pa):+.3f} · daily_033 med {np.median(da):+.2f}%/day')
    print('top 5 by daily_033 (expected daily % profit @ 0.33 stop):')
    for c, p, d in sorted(ok, key=lambda x: -x[2])[:5]:
        print(f'  {c:<22} profit/trade {p:+.3f}  daily {d:+.2f}%')


if __name__ == '__main__':
    main()
