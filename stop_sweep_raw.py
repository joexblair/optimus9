"""
stop_sweep_raw — under the limit-entry mechanic on RAW intrabar price, sweep the stop
to see all sides of the coin: win% + net/trade at each fixed stop, plus the swing-
anchored stop (Joe's real one = distance to the last adverse pivot). Take fixed at 0.9.

Entries (limit fills) computed once per combo; per fill we precompute the raw race
structure (reached +0.9?, worst dip before it, worst dip overall) so every stop is O(1).
Pools all 300 combos' fills for the aggregate landscape.
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
TAKE, HORIZON, CAP = 0.9, 2160, 2160
SWEEP = [0.2, 0.33, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
TABLE = 'gate_both_top300'


def main():
    G.prepare(); G.precompute()
    db = DatabaseManager(**get_db_config()); db.connect()
    base, mask = G._CTX['base'], G._CTX['mask']
    idx, dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=True, gate_bb=True, gate_k=True)
    full = np.zeros(len(mask), np.int8); full[idx] = dirs
    raw_pk = full[mask]
    px_s = np.asarray(G._CTX['px'], float)
    hi = base['high'].to_numpy(float)[mask]; lo = base['low'].to_numpy(float)[mask]
    cl = base['close'].to_numpy(float)[mask]
    piv, lb = G._CTX['pivots'], G._CTX['pk_lookback']
    N = len(px_s)
    lows = [p for p, k in piv if k == 'L']; highs = [p for p, k in piv if k == 'H']

    def swing_dist(oi, E, d):
        cand = [p for p in (lows if d == 1 else highs) if p < oi]
        if not cand:
            return None
        sp = px_s[cand[-1]]
        dist = (E - sp) / E * 100 * d
        return dist if dist > 0 else None

    def race_struct(fb, E, d):
        h = hi[fb:fb + HORIZON]; l = lo[fb:fb + HORIZON]
        if len(h) == 0:
            return None
        if d == 1:
            take = E * (1 + TAKE / 100); adv = np.maximum(0.0, (E - l) / E * 100); th = h >= take
        else:
            take = E * (1 - TAKE / 100); adv = np.maximum(0.0, (h - E) / E * 100); th = l <= take
        cum = np.maximum.accumulate(adv)
        if th.any():
            tt = int(np.argmax(th))
            return (True, float(cum[:tt].max()) if tt > 0 else 0.0, float(cum[-1]))
        return (False, np.inf, float(cum[-1]))

    fills = []         # (reached, mae_to_take, mae_overall, swing_dist)
    n_fill = n_sig = 0
    for r in db.execute(f'SELECT combo FROM {TABLE}', fetch=True):
        vals = [int(x) for x in r['combo'].split(',')]
        states = [G._STATES[(NAMES[i], vals[i])] for i in range(len(NAMES))]
        opens = [(t['open_i'], t['dir']) for t in walk(G._refold(states), raw_pk, px_s, piv, lb)]
        for k, (oi, d) in enumerate(opens):
            n_sig += 1
            w_end = min(opens[k + 1][0] if k + 1 < len(opens) else N, oi + CAP, N)
            L = px_s[oi]; fb = -1
            for b in range(oi + 1, w_end):
                if raw_pk[b] == d:
                    L = px_s[b]
                if (d == 1 and lo[b] <= L) or (d == -1 and hi[b] >= L):
                    fb = b; break
            if fb < 0:
                continue
            rs = race_struct(fb, L, d)
            if rs is None:
                continue
            n_fill += 1
            fills.append((*rs, swing_dist(oi, L, d)))
    db.disconnect()

    def outcome(reached, mtt, mo, S):
        if reached:
            return TAKE if S > mtt else -S
        return -S if S <= mo else 0.0

    print(f'limit fills: {n_fill}/{n_sig} signals ({n_fill/max(n_sig,1)*100:.1f}%)  ·  take {TAKE}, RAW intrabar')
    print(f'\n{"stop":>7} {"win%":>6} {"stop%":>6} {"net/trade":>10} {"daily~":>8}')
    perday = n_fill / 300 / 9.0     # avg fills/combo/day
    for S in SWEEP:
        outs = np.array([outcome(*f[:3], S) for f in fills])
        won = int((outs == TAKE).sum()); st = int((outs == -S).sum()); dec = won + st
        net = outs.mean()
        print(f'{S:>7.2f} {won/max(dec,1)*100:>6.1f} {st/max(dec,1)*100:>6.1f} {net:>+10.4f} {net*perday:>+8.2f}')
    # swing-anchored stop (per-trade S = distance to last adverse pivot)
    sw = [(f, f[3]) for f in fills if f[3] is not None]
    outs = np.array([outcome(*f[:3], S) for f, S in sw])
    won = int((outs == TAKE).sum()); st = int((outs < 0).sum()); dec = won + st
    dists = np.array([S for _, S in sw])
    print(f'\nswing-anchored stop (avg {dists.mean():.2f}%, median {np.median(dists):.2f}%, n={len(sw)}):')
    print(f'  win% {won/max(dec,1)*100:.1f}  net/trade {outs.mean():+.4f}  daily~ {outs.mean()*perday:+.2f}')
    print(f'\n(~{perday:.1f} fills/combo/day · daily~ = net/trade × that)')


if __name__ == '__main__':
    main()
