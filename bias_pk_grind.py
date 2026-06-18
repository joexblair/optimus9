"""
bias_pk_grind.py — the bias-machine grind sweep (first consumer of bias_machine.py).

Rolling 8×7d windows (5d step). Per window, per config, runs the no-stop strategy and records
per-trade MAE/MFE → stops are reconstructed analytically (no stop axis, continuous resolution).

Configs (TF7 excluded = s14 slot; TFS = 4,5,6,8,9,10,11,12):
  • s14   exit — trigger ∈ TFS, exit = opposite s30 wob with s14m OOB
  • tf     exit — exit = opposite s30 wob with s{etf}m AND s{etf}r OOB, over:
      item1 trigger=12 × etf∈TFS · item2 trigger=6 × etf∈TFS · item3 trigger=etf (in-sync)
  × gate {oob, vs50}.  Dups across items deduped.
Writes bias_pk_grind (no-stop summary) + bias_pk_grind_trades (per-trade ledger w/ MAE/MFE).
Prints the stop-reconstruction leaderboard (best rolled stop + robustness).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm

H = bm.H
STOP_GRID = [None] + [round(s, 1) for s in np.arange(0.3, 4.01, 0.1)]
def dd(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d')
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')

# ── config list (deduped) ──
S14_CFGS = [('s14', trig, None) for trig in bm.TFS]
_tf = set()
for etf in bm.TFS: _tf.add((12, etf)); _tf.add((6, etf))     # item1, item2
for trig in bm.TFS: _tf.add((trig, trig))                    # item3 (in-sync)
TF_CFGS = [('tf', trig, etf) for (trig, etf) in sorted(_tf)]
CFGS = S14_CFGS + TF_CFGS
GATES = ('oob', 'vs50')

# ── windows ──
db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()
print(f'klines {dts(earliest)} → {dts(latest)} · {len(ends)} windows · {len(CFGS)*len(GATES)} configs/window')

# ── run ──
# results[(kind,trig,etf,gate)] = list over windows of trade-lists
results = {}; win_ends = []
for wi, end in enumerate(ends):
    W = bm.BiasWindow(db, end); win_ends.append(W.W1)
    upcache = {(trig, gate): W.ups(W.trigs(trig), gate) for trig in bm.TFS for gate in GATES}
    for gate in GATES:
        for (kind, trig, etf) in CFGS:
            ups = upcache[(trig, gate)]
            if kind == 's14':
                exit_signs = [W.s14m_sign]
            else:
                d = W.tf(etf); exit_signs = [d['m_sign'], d['r_sign']]
            tr = W.run(ups, exit_signs)
            results.setdefault((kind, trig, etf, gate), []).append(tr)
    print(f'  window {wi+1}/{len(ends)} → {dd(W.W1)} done')

# ── durable tables ──
sum_rows, trade_rows = [], []
for (kind, trig, etf, gate), per_win in results.items():
    for wi, tr in enumerate(per_win):
        we = dts(win_ends[wi])
        net = sum(t['pnl'] for t in tr); wins = sum(t['pnl'] > 0 for t in tr); eod = sum(t['eod'] for t in tr)
        sum_rows.append([we, kind, trig, etf, gate, len(tr), wins, round(net, 2), eod])
        for t in tr:
            trade_rows.append([we, kind, trig, etf, gate, dts(t['et']), dts(t['xt']),
                               'LONG' if t['bd'] == 1 else 'SHORT', round(t['ep'], 5), round(t['xp'], 5),
                               round(t['pnl'], 2), round(t['mae'], 3), round(t['mfe'], 3), int(t['eod'])])
db.execute('DROP TABLE IF EXISTS bias_pk_grind')
db.execute('''CREATE TABLE bias_pk_grind (pk BIGINT AUTO_INCREMENT PRIMARY KEY, window_end DATETIME,
    exit_kind VARCHAR(4), trigger_tf INT, exit_tf INT, gate_mode VARCHAR(6),
    trades INT, wins INT, net_usd FLOAT, eod_exits INT)''')
db.executemany('INSERT INTO bias_pk_grind (window_end,exit_kind,trigger_tf,exit_tf,gate_mode,trades,wins,net_usd,eod_exits) '
               'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', sum_rows)
db.execute('DROP TABLE IF EXISTS bias_pk_grind_trades')
db.execute('''CREATE TABLE bias_pk_grind_trades (pk BIGINT AUTO_INCREMENT PRIMARY KEY, window_end DATETIME,
    exit_kind VARCHAR(4), trigger_tf INT, exit_tf INT, gate_mode VARCHAR(6), entry_time DATETIME, exit_time DATETIME,
    direction VARCHAR(5), entry_px FLOAT, exit_px FLOAT, pnl_usd FLOAT, mae_pct FLOAT, mfe_pct FLOAT, eod TINYINT)''')
db.executemany('''INSERT INTO bias_pk_grind_trades (window_end,exit_kind,trigger_tf,exit_tf,gate_mode,entry_time,exit_time,
    direction,entry_px,exit_px,pnl_usd,mae_pct,mfe_pct,eod) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', trade_rows)
db.disconnect()

# ── stop reconstruction leaderboard ──
def best_stop(per_win):
    best = (None, -9e18, 0)                                   # (stop, rolled_total, +windows)
    for s in STOP_GRID:
        nets = [bm.stopped_net(tr, s) for tr in per_win]
        tot = sum(nets); pos = sum(n > 0 for n in nets)
        if tot > best[1]: best = (s, tot, pos)
    return best

lb = []
for key, per_win in results.items():
    nostop = sum(sum(t['pnl'] for t in tr) for tr in per_win)
    s, tot, pos = best_stop(per_win)
    lb.append((tot, pos, s, nostop, key))
lb.sort(reverse=True)

print(f'\nLEADERBOARD — best rolled net$ across {len(ends)} windows (stop reconstructed from MAE)')
print(f'  {"kind":>4} {"trig":>4} {"exit":>4} {"gate":>4} | {"stop%":>5} {"rolled$":>9} {"+wins":>6} | {"no-stop$":>9}')
for tot, pos, s, nostop, (kind, trig, etf, gate) in lb[:15]:
    st = 'none' if s is None else f'{s:.1f}'
    et = '-' if etf is None else str(etf)
    print(f'  {kind:>4} {trig:>4} {et:>4} {gate:>4} | {st:>5} {tot:>+9.0f} {pos:>3}/{len(ends)} | {nostop:>+9.0f}')

# winner detail + stop curve
tot, pos, s, nostop, key = lb[0]; kind, trig, etf, gate = key; per_win = results[key]
print(f'\nWINNER  {kind} trig{trig} exit{etf} {gate}  ·  best stop {s} → rolled ${tot:+.0f} ({pos}/{len(ends)})')
print('  stop curve (rolled net$):  ' + ' '.join(
    f'{("none" if sc is None else f"{sc:.1f}")}:{sum(bm.stopped_net(tr, sc) for tr in per_win):+.0f}'
    for sc in (None, 0.5, 1.0, 1.5, 2.0, 3.0)))
print('  per-window @best stop: ' + ' '.join(f'{dd(win_ends[wi])}:{bm.stopped_net(tr, s):+.0f}' for wi, tr in enumerate(per_win)))

# MAE picture: winners vs losers (no-stop), pooled over the winner config
allt = [t for tr in per_win for t in tr]
wl = np.array([t['mae'] for t in allt if t['pnl'] > 0]); ll = np.array([t['mae'] for t in allt if t['pnl'] <= 0])
print(f'  MAE median — winners {np.median(wl):.2f}% · losers {np.median(ll):.2f}%  (n {len(allt)})')
print(f'\n→ db: bias_pk_grind ({len(sum_rows)} rows), bias_pk_grind_trades ({len(trade_rows)} rows)')
