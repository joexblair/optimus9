"""
add_limit_counts — model Joe's limit-at-px_smooth entry per combo, and count the 7
per-row triggers from the steelman/strawman (3 structural points excluded).

Mechanic (lo-breach long; short mirrors): on the trade's same-dir PK, post a buy limit
at px_smooth; re-post to the new px_smooth on each later same-dir PK while unfilled; FILL
when raw price crosses under the limit (long: bar low <= L). Entry = L. Order lives from
the gate-open signal until filled OR the next gate-open trade supersedes it (cap 3h).
After fill, race +0.9 take / -0.33 stop on raw intrabar high/low.

Columns (per combo, counts over its trades):
  no_fill          P3  signals that never filled (no-loss skips)
  maker_fills      P4  fills (rebate-eligible)
  better_entry     P2  fills where the limit beat the signal-bar close
  knife_stops      C2  fills that then hit the 0.33 stop
  filled_no_profit C5  fills that never reached +0.9 (stopped or undecided)
  missed_winners   C1  no-fill signals a MARKET entry would have won  <= adverse-selection decider
  marginal_fills   C4  fills where price only grazed the limit (close back on the wrong side)
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
TAKE, STOP, HORIZON, CAP = 0.9, 0.33, 2160, 2160
TABLE = 'gate_both_top300'
COLS = ['no_fill', 'maker_fills', 'better_entry', 'knife_stops',
        'filled_no_profit', 'missed_winners', 'marginal_fills']


def race(hi, lo, start, entry, d):
    h = hi[start:start + HORIZON]; l = lo[start:start + HORIZON]
    if len(h) == 0:
        return 0
    if d == 1:
        wt = h >= entry * (1 + TAKE / 100); ws = l <= entry * (1 - STOP / 100)
    else:
        wt = l <= entry * (1 - TAKE / 100); ws = h >= entry * (1 + STOP / 100)
    it = int(np.argmax(wt)) if wt.any() else 1 << 30
    iss = int(np.argmax(ws)) if ws.any() else 1 << 30
    return 0 if it == iss == 1 << 30 else (1 if it <= iss else -1)


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

    rows = db.execute(f'SELECT combo FROM {TABLE}', fetch=True)
    upd = {}
    for r in rows:
        vals = [int(x) for x in r['combo'].split(',')]
        states = [G._STATES[(NAMES[i], vals[i])] for i in range(len(NAMES))]
        trades = walk(G._refold(states), raw_pk, px_s, piv, lb)
        opens = [(t['open_i'], t['dir']) for t in trades]
        c = dict.fromkeys(COLS, 0)
        for k, (oi, d) in enumerate(opens):
            w_end = min(opens[k + 1][0] if k + 1 < len(opens) else N, oi + CAP, N)
            L = px_s[oi]; fb = -1
            for b in range(oi + 1, w_end):
                if raw_pk[b] == d:
                    L = px_s[b]
                if (d == 1 and lo[b] <= L) or (d == -1 and hi[b] >= L):
                    fb = b; break
            if fb < 0:
                c['no_fill'] += 1
                if race(hi, lo, oi, cl[oi], d) == 1:      # market entry would've won
                    c['missed_winners'] += 1
                continue
            c['maker_fills'] += 1
            if (d == 1 and L < cl[oi]) or (d == -1 and L > cl[oi]):
                c['better_entry'] += 1
            if (d == 1 and cl[fb] > L) or (d == -1 and cl[fb] < L):
                c['marginal_fills'] += 1
            res = race(hi, lo, fb, L, d)
            if res == -1:
                c['knife_stops'] += 1
            if res != 1:
                c['filled_no_profit'] += 1
        upd[r['combo']] = c

    for col in COLS:
        if col not in [x['Field'] for x in db.execute(f'SHOW COLUMNS FROM {TABLE}', fetch=True)]:
            db.execute(f'ALTER TABLE {TABLE} ADD COLUMN {col} INT')
    for combo, c in upd.items():
        db.execute(f"UPDATE {TABLE} SET {','.join(f'{k}=%s' for k in COLS)} WHERE combo=%s",
                   [c[k] for k in COLS] + [combo])
    db.execute(f'DROP VIEW IF EXISTS v_{TABLE}')
    db.execute(f'CREATE VIEW v_{TABLE} AS SELECT * FROM {TABLE} ORDER BY daily_033 DESC')
    db.disconnect()

    agg = {k: sum(c[k] for c in upd.values()) for k in COLS}
    fills = agg['maker_fills']; sig = fills + agg['no_fill']
    print(f'{len(upd)} combos · totals across all combos:')
    for k in COLS:
        print(f'  {k:<18} {agg[k]:>8}')
    miss = agg['missed_winners']; nf = max(agg['no_fill'], 1); worked = fills - agg['filled_no_profit']
    print(f'\n  fill rate: {fills/max(sig,1)*100:.1f}%  ({fills}/{sig} signals)')
    print(f'  ADVERSE SELECTION: {miss}/{agg["no_fill"]} skips were winners = {miss/nf*100:.1f}%')
    print(f'  fills that reached +0.9: {worked}/{fills} = {worked/max(fills,1)*100:.1f}%')


if __name__ == '__main__':
    main()
