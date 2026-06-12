"""
add_optimum_stop — for each combo in gate_both_top300, find the stop value that
maximises realised profit on ITS OWN trades, via the win-vs-stop RACE (cluster_scoring
semantics) against a fixed +W% target (W = the 0.9% swing threshold):
  per entry: walk px forward (horizon H); does it hit +W% before −S%?
    reached +W (with worst dip mae_before_win):  +W if S > mae_before_win else −S
    never reached +W (worst dip mae_overall):     −S if S <= mae_overall else 0
  net(S) = Σ entries; best_stop = argmax_S; best_stop_profit = net averaged per trade.
Adds two columns to gate_both_top300 (+ rebuilds the view).
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
STOPS = np.round(np.arange(0.05, 2.001, 0.05), 2)      # candidate stop grid (fine)
HORIZON = 2160                                          # 3h, matches cluster_scoring
TABLE = 'gate_both_top300'


def main():
    G.prepare(); G.precompute()
    db = DatabaseManager(**get_db_config()); db.connect()
    base, mask = G._CTX['base'], G._CTX['mask']
    idx, dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=True, gate_bb=True, gate_k=True)
    full = np.zeros(len(mask), np.int8); full[idx] = dirs
    raw = full[mask]
    px, piv, lb = G._CTX['px'], G._CTX['pivots'], G._CTX['pk_lookback']
    W = float(G.active_config()['bgc_swing_pct'])       # profit target = the swing threshold (0.9)
    px = np.asarray(px, float); n = len(px)

    # per-entry race params, cached by (i, dir)
    cache = {}
    def params(i, d):
        if (i, d) in cache:
            return cache[(i, d)]
        seg = px[i + 1:i + 1 + HORIZON]
        if len(seg) == 0:
            cache[(i, d)] = None; return None
        rel = (seg - px[i]) / px[i] * 100.0 * d         # directional return path (% , + = profit)
        adv = np.maximum.accumulate(np.maximum(0.0, -rel))   # running worst adverse excursion
        won = rel >= W
        if won.any():
            wi = int(np.argmax(won))
            r = (True, float(adv[:wi].max()) if wi > 0 else 0.0, float(adv[-1]))
        else:
            r = (False, 0.0, float(adv[-1]))
        cache[(i, d)] = r; return r

    def net_at(entries, S):
        tot = 0.0
        for e in entries:
            p = params(*e)
            if p is None:
                continue
            reached, mbw, mo = p
            tot += (W if S > mbw else -S) if reached else (-S if S <= mo else 0.0)
        return tot

    combos = [r['combo'] for r in db.execute(f'SELECT combo FROM {TABLE}', fetch=True)]
    out = {}
    ts_win = None
    for combo in combos:
        vals = [int(x) for x in combo.split(',')]
        states = [G._STATES[(NAMES[i], vals[i])] for i in range(len(NAMES))]
        trades = walk(G._refold(states), raw, px, piv, lb)
        entries = [(t['open_i'], t['dir']) for t in trades]
        if not entries:
            out[combo] = (None, None); continue
        nets = [net_at(entries, S) for S in STOPS]
        j = int(np.argmax(nets))
        out[combo] = (float(STOPS[j]), round(nets[j] / len(entries), 4))

    for col in ('best_stop', 'best_stop_profit'):
        if col not in [c['Field'] for c in db.execute(f'SHOW COLUMNS FROM {TABLE}', fetch=True)]:
            db.execute(f'ALTER TABLE {TABLE} ADD COLUMN {col} FLOAT')
    for combo, (bs, bp) in out.items():
        db.execute(f'UPDATE {TABLE} SET best_stop=%s, best_stop_profit=%s WHERE combo=%s', (bs, bp, combo))
    db.execute(f'DROP VIEW IF EXISTS v_{TABLE}')
    db.execute(f'CREATE VIEW v_{TABLE} AS SELECT * FROM {TABLE} ORDER BY total_net DESC')
    db.disconnect()

    ok = [(c, bs, bp) for c, (bs, bp) in out.items() if bs is not None]
    print(f'{len(ok)}/{len(combos)} combos got an optimum stop')
    bs_all = np.array([bs for _, bs, _ in ok])
    print(f'best_stop distribution: min {bs_all.min():.2f} median {np.median(bs_all):.2f} max {bs_all.max():.2f}')
    print('top 5 by best_stop_profit:')
    for c, bs, bp in sorted(ok, key=lambda x: -x[2])[:5]:
        print(f'  {c:<22} best_stop {bs:.2f}  profit/trade {bp:+.3f}')


if __name__ == '__main__':
    main()
