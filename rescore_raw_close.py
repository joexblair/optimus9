"""
rescore_raw_close — step 1 of the validation plan: re-score the gate-both grind on RAW
CLOSE (not px_smooth), market entry on the PK signal. Kills the smoothing mirage.

  (a) re-run the fold on raw close → bl_group_results_both_raw (BL swing metrics, raw)
  (b) for the top-300 by raw avg_stop, the SCALPER-real net: stop 0.33 / take 0.9,
      close-to-close race, market entry at the gate-open. → bl_both_raw_scored.
Compares avg_stop raw vs px_smooth (the mirage magnitude).
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
from optimus9.compute.swing_detect import find_pivots

NAMES = ['b6b', 'hb15b', 'hb9b', 'hs15r', 'hs9r', 's18b', 's30r', 's90b']
TAKE, STOP, H = 0.9, 0.33, 2160


def main():
    c = G.prepare(); G.precompute()
    db = DatabaseManager(**get_db_config()); db.connect()
    base, mask = G._CTX['base'], G._CTX['mask']
    idx, dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=True, gate_bb=True, gate_k=True)
    full = np.zeros(len(mask), np.int8); full[idx] = dirs
    raw_pk = full[mask]
    rc = base['close'].to_numpy(float)[mask]
    day = float(c['bgc_window_days'])

    # (a) swap the grind context to raw close + re-fold
    G._CTX['px'] = rc
    G._CTX['pivots'] = sorted(find_pivots(rc, float(c['bgc_swing_pct'])))
    G._CTX['raw_pk'] = raw_pk
    res = G.run_round()
    G.persist(res, table='bl_group_results_both_raw')

    # (b) scalper-real 0.33/0.9 net on raw close, top-300 by raw avg_stop
    cache = {}
    def outc(i, d):
        if (i, d) not in cache:
            seg = rc[i + 1:i + 1 + H]
            if len(seg) == 0:
                cache[(i, d)] = 0.0
            else:
                rel = (seg - rc[i]) / rc[i] * 100 * d
                iw = int(np.argmax(rel >= TAKE)) if (rel >= TAKE).any() else 1 << 30
                il = int(np.argmax(rel <= -STOP)) if (rel <= -STOP).any() else 1 << 30
                cache[(i, d)] = TAKE if iw < il else (-STOP if il < iw else 0.0)
        return cache[(i, d)]

    ok = [r for r in res if r['n'] and r['avg_stop'] is not None]
    top = sorted(ok, key=lambda r: r['avg_stop'])[:300]
    piv = G._CTX['pivots']
    scored = []
    for r in top:
        vals = [int(x) for x in r['combo'].split(',')]
        states = [G._STATES[(NAMES[i], vals[i])] for i in range(len(NAMES))]
        ents = [(t['open_i'], t['dir']) for t in walk(G._refold(states), raw_pk, rc, piv, G._CTX['pk_lookback'])]
        if not ents:
            continue
        outs = np.array([outc(*e) for e in ents])
        won = int((outs == TAKE).sum()); st = int((outs == -STOP).sum()); dec = won + st
        ppt = float(outs.mean())
        scored.append((r['combo'], len(ents), round(len(ents)/day, 2), r['avg_stop'],
                       round(won/max(dec,1)*100, 1), round(ppt, 4), round(ppt*len(ents)/day, 3)))

    db.execute('DROP TABLE IF EXISTS bl_both_raw_scored')
    db.execute('''CREATE TABLE bl_both_raw_scored (combo VARCHAR(160), n INT, per_day FLOAT,
        raw_avg_stop FLOAT, win033 FLOAT, net033 FLOAT, daily033 FLOAT)''')
    db.executemany('INSERT INTO bl_both_raw_scored VALUES (%s,%s,%s,%s,%s,%s,%s)', scored)
    db.disconnect()

    arr = np.array([s[5] for s in scored]); dl = np.array([s[6] for s in scored]); wn = np.array([s[4] for s in scored])
    pos = int((arr > 0).sum())
    print(f'RE-SCORE ON RAW CLOSE (stop {STOP} / take {TAKE}, market entry) — top 300 by raw avg_stop')
    print(f'  net/trade: med {np.median(arr):+.4f}  [{arr.min():+.3f},{arr.max():+.3f}]  ·  positive: {pos}/{len(arr)}')
    print(f'  win%: med {np.median(wn):.1f}  ·  daily: med {np.median(dl):+.2f}%/day')
    print('  top 5 by daily033:')
    for s in sorted(scored, key=lambda x: -x[6])[:5]:
        print(f'    {s[0]:<22} day{s[2]:>5.1f} win{s[4]:>5.1f} net/trade{s[5]:+.4f} daily{s[6]:+.2f}%')


if __name__ == '__main__':
    main()
