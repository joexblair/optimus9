"""
oos_validate — step 2: out-of-sample. Take the raw-close top combos (in-sample winners)
and score them on OTHER 9-day windows of the tape, same scalper config (0.33/0.9, raw
close, market entry). Robust edge holds across windows; overfit collapses.

Windows = end_ms at 0/9/18/27 days back from data_max (skip any lacking warmup data).
Line-states are window-specific → precompute per window.
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
DAY_MS = 86400000
OFFSETS = [0, 9, 18, 27]      # days back from data_max


def score_window(end_ms, combos, swing):
    G.prepare(end_ms=end_ms); G.precompute()
    db = DatabaseManager(**get_db_config()); db.connect()
    base, mask = G._CTX['base'], G._CTX['mask']
    idx, dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=True, gate_bb=True, gate_k=True)
    full = np.zeros(len(mask), np.int8); full[idx] = dirs
    db.disconnect()
    raw_pk = full[mask]
    rc = base['close'].to_numpy(float)[mask]
    piv = sorted(find_pivots(rc, swing))
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
    out = {}
    for combo in combos:
        vals = [int(x) for x in combo.split(',')]
        states = [G._STATES[(NAMES[i], vals[i])] for i in range(len(NAMES))]
        ents = [(t['open_i'], t['dir']) for t in walk(G._refold(states), raw_pk, rc, piv, G._CTX['pk_lookback'])]
        if not ents:
            out[combo] = (0, 0.0, 0.0); continue
        o = np.array([outc(*e) for e in ents])
        won = int((o == TAKE).sum()); dec = won + int((o == -STOP).sum())
        out[combo] = (len(ents), won / max(dec, 1) * 100, float(o.mean()))
    return out


def main():
    cfg_db = DatabaseManager(**get_db_config()); cfg_db.connect()
    swing = float(cfg_db.execute('SELECT bgc_swing_pct s FROM bl_grind_config WHERE bgc_is_active=1', fetch=True)[0]['s'])
    dmax = int(cfg_db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])
    combos = [r['combo'] for r in cfg_db.execute(
        'SELECT combo FROM bl_both_raw_scored ORDER BY daily033 DESC LIMIT 15', fetch=True)]
    cfg_db.disconnect()

    results = {}    # offset -> {combo: (n, win, net)}
    for off in OFFSETS:
        end = dmax - off * DAY_MS
        try:
            results[off] = score_window(end, combos, swing)
        except Exception as e:
            print(f'  window -{off}d skipped: {e}')

    day = 9.0
    print(f'\nOUT-OF-SAMPLE — {len(combos)} raw-close top combos × {len(results)} windows (0.33/0.9, raw close)')
    hdr = '  '.join(f'-{o}d' for o in results)
    print(f'{"combo":<22} ' + '  '.join(f'{"-"+str(o)+"d":>14}' for o in results) + '   (net/trade · daily%)')
    for combo in combos:
        cells = []
        for o in results:
            n, win, net = results[o][combo]
            cells.append(f'{net:+.3f}/{net*n/day:+.2f}')
        print(f'{combo:<22} ' + '  '.join(f'{c:>14}' for c in cells))
    print('\nper-window median net/trade:')
    for o in results:
        nets = [results[o][c][2] for c in combos]
        print(f'  -{o}d: {np.median(nets):+.4f}  (in-sample = -0d)')


if __name__ == '__main__':
    main()
