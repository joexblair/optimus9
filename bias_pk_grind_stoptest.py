"""
bias_pk_grind_stoptest.py — validate the MAE stop-reconstruction against a REAL applied stop.

Re-runs the full grid (same configs as bias_pk_grind.py) at hard stop 1.0% and 0.5%, with
actual-tape fills, and compares the real rolled net$ per config to the MAE reconstruction
(bias_machine.stopped_net, derived from the no-stop trades). If they match → the "gather stats"
method is proven and we trust it; the gap = slippage past the stop on the 5s tape.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm

H = bm.H; STOPS = [1.0, 0.5]
def dd(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d')

S14_CFGS = [('s14', trig, None) for trig in bm.TFS]
_tf = set()
for etf in bm.TFS: _tf.add((12, etf)); _tf.add((6, etf))
for trig in bm.TFS: _tf.add((trig, trig))
CFGS = S14_CFGS + [('tf', trig, etf) for (trig, etf) in sorted(_tf)]
GATES = ('oob', 'vs50')

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()

# real[s][key] = list-of-per-window-net ; recon[s][key] = same via stopped_net(no-stop trades)
real = {s: {} for s in STOPS}; recon = {s: {} for s in STOPS}; nostop = {}; ntr = {}; win_ends = []
for wi, end in enumerate(ends):
    W = bm.BiasWindow(db, end); win_ends.append(W.W1)
    upcache = {(trig, gate): W.ups(W.trigs(trig), gate) for trig in bm.TFS for gate in GATES}
    for gate in GATES:
        for (kind, trig, etf) in CFGS:
            key = (kind, trig, etf, gate)
            ups = upcache[(trig, gate)]
            exit_signs = [W.s14m_sign] if kind == 's14' else [W.tf(etf)['m_sign'], W.tf(etf)['r_sign']]
            t0 = W.run(ups, exit_signs, stop=None)
            nostop.setdefault(key, []).append(sum(t['pnl'] for t in t0)); ntr.setdefault(key, []).append(len(t0))
            for s in STOPS:
                real[s].setdefault(key, []).append(sum(t['pnl'] for t in W.run(ups, exit_signs, stop=s)))
                recon[s].setdefault(key, []).append(bm.stopped_net(t0, s))
    print(f'  window {wi+1}/{len(ends)} → {dd(W.W1)} done')

# ── persist every (config, window, stop) so it can be queried/excel'd ──
def we(wi): return dtm.datetime.fromtimestamp(win_ends[wi] / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')
rows = []
for k in nostop:
    kind, trig, etf, gate = k
    for wi in range(len(ends)):
        rows.append([we(wi), kind, trig, etf, gate, 0.0, round(nostop[k][wi], 2), round(nostop[k][wi], 2), ntr[k][wi]])
        for s in STOPS:
            rows.append([we(wi), kind, trig, etf, gate, s, round(real[s][k][wi], 2), round(recon[s][k][wi], 2), ntr[k][wi]])
db.execute('DROP TABLE IF EXISTS bias_pk_grind_stops')
db.execute('''CREATE TABLE bias_pk_grind_stops (pk BIGINT AUTO_INCREMENT PRIMARY KEY, window_end DATETIME,
    exit_kind VARCHAR(4), trigger_tf INT, exit_tf INT, gate_mode VARCHAR(6), stop_pct DECIMAL(3,1),
    real_net FLOAT, recon_net FLOAT, trades INT)''')
db.executemany('INSERT INTO bias_pk_grind_stops (window_end,exit_kind,trigger_tf,exit_tf,gate_mode,stop_pct,real_net,recon_net,trades) '
               'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
db.disconnect()
print(f'\n→ db table bias_pk_grind_stops ({len(rows)} rows)')

# ── raw per-window dump for the configs in question ──
def dump(k):
    kind, trig, etf, gate = k
    print(f'\n{kind} trig{trig} exit{etf} gate={gate}  — per-window net$ (raw)')
    print(f'  {"window":>10} {"n":>4} | {"NO-STOP":>9} | {"1.0 real":>9} {"1.0 recon":>10} | {"0.5 real":>9} {"0.5 recon":>10}')
    for wi in range(len(ends)):
        print(f'  {dd(win_ends[wi]):>10} {ntr[k][wi]:>4} | {nostop[k][wi]:>+9.0f} | '
              f'{real[1.0][k][wi]:>+9.0f} {recon[1.0][k][wi]:>+10.0f} | {real[0.5][k][wi]:>+9.0f} {recon[0.5][k][wi]:>+10.0f}')
    print(f'  {"ROLLED":>10} {sum(ntr[k]):>4} | {sum(nostop[k]):>+9.0f} | '
          f'{sum(real[1.0][k]):>+9.0f} {sum(recon[1.0][k]):>+10.0f} | {sum(real[0.5][k]):>+9.0f} {sum(recon[0.5][k]):>+10.0f}')

dump(('tf', 6, 12, 'vs50'))      # the no-stop winner
dump(('tf', 12, 12, 'oob'))      # the "best real 1% stop" config I quoted

keys = list(nostop.keys())
def fmtkey(k): return f"{k[0]:>3} t{k[1]:<2} e{('-' if k[2] is None else k[2]):<2} {k[3]:>4}"

for s in STOPS:
    print(f'\n================  STOP {s:.1f}%  ================')
    rows = []
    for k in keys:
        rtot = sum(real[s][k]); rpos = sum(v > 0 for v in real[s][k])
        ctot = sum(recon[s][k])
        rows.append((rtot, rpos, ctot, sum(nostop[k]), k))
    rows.sort(reverse=True)
    print(f'  {"config":>16} | {"real$":>8} {"+wins":>6} | {"recon$":>8} {"Δ":>6} | {"no-stop$":>9}')
    for rtot, rpos, ctot, nstot, k in rows[:12]:
        print(f'  {fmtkey(k)} | {rtot:>+8.0f} {rpos:>3}/{len(ends)} | {ctot:>+8.0f} {rtot-ctot:>+6.0f} | {nstot:>+9.0f}')
    diffs = [abs(sum(real[s][k]) - sum(recon[s][k])) for k in keys]
    md = max(range(len(keys)), key=lambda i: diffs[i])
    print(f'  match: mean|Δ| ${np.mean(diffs):.0f} · max|Δ| ${diffs[md]:.0f} ({fmtkey(keys[md])}) '
          f'· real total vs recon total ${sum(sum(real[s][k]) for k in keys):.0f} / ${sum(sum(recon[s][k]) for k in keys):.0f}')

# headline winner across no-stop for reference
wk = max(keys, key=lambda k: sum(nostop[k]))
print(f'\nno-stop winner {fmtkey(wk)} = ${sum(nostop[wk]):+.0f}  ·  '
      + ' · '.join(f'stop{s}: real ${sum(real[s][wk]):+.0f} / recon ${sum(recon[s][wk]):+.0f}' for s in STOPS))
