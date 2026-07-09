"""recon_arm_gate.py — live vs backtest recon for ONLY the arm + s3s4_gate events (Joe 0705).

Backtest = v2_cascade run as a batch over the tape NOW (hindsight window — arm@unlatch, gate@open per arm).
Live     = o9_state_log arm/s3s4_gate occurrences (per-bar causal, what the loop actually saw).
Strict-time chronological: each event one row; a row filled on ONE side = a divergence. Writes to
o9_live.arm_gate_recon (id ASC = chronological). Query:
    SELECT backtest_dt, backtest_event, o9_dt, o9_event FROM arm_gate_recon ORDER BY id;
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.live.strategy import StrategyLoop
from optimus9.analysis.lr_v2 import v2_cascade

SYM = 'FARTCOINUSDT'


def dt(ms):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(ms) / 1000))


def main():
    o9db = DatabaseManager(**{**get_db_config(), 'database': 'o9_live'}); o9db.connect()
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev)

    # --- live events (o9_state_log): arm + s3s4_gate ---
    live = o9db.execute("SELECT kline_ms, state, new_v, meta FROM o9_state_log "
                        "WHERE state IN ('arm','s3s4_gate') ORDER BY kline_ms, sl_id", fetch=True)
    lo = int(live[0]['kline_ms']) if live else 0
    hi = int(live[-1]['kline_ms']) if live else 0

    # --- backtest events (v2_cascade batch over a window covering the live span) ---
    strat = StrategyLoop(dev, bm.BiasConfig(**BASE_BIAS), cfg, SYM, buffer_hours=8, warmup_hours=6)
    W = strat.window(int(time.time() * 1000)); ts = W.ts
    bt = []
    for (i, es, bd, cap, src, gb, gr, tk, path) in v2_cascade(W, cfg):
        if lo <= int(ts[i]) <= hi:
            bt.append((int(ts[i]), 'arm %+d %s' % (es, src)))
        if gb is not None and lo <= int(ts[gb]) <= hi:
            bt.append((int(ts[gb]), 's3s4_gate %+d %s' % (es, gr)))

    # --- dedup (v2_arm emits duplicate setups) + merge into chronological rows ---
    ev = []                                              # (ms, 'bt'|'o9', event_str)
    for ms, s in set(bt):
        ev.append((ms, 'bt', s))
    for r in live:
        ev.append((int(r['kline_ms']), 'o9', '%s %+d %s' % (r['state'], r['new_v'], r['meta'] or '')))
    seen = set(); uniq = []
    for row in ev:
        if row not in seen:
            seen.add(row); uniq.append(row)
    uniq.sort(key=lambda x: (x[0], 0 if x[1] == 'bt' else 1))

    # --- write to DB (id ASC = chronological; one side per row, other NULL) ---
    o9db.execute("""CREATE TABLE IF NOT EXISTS arm_gate_recon (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        backtest_dt DATETIME NULL, backtest_event VARCHAR(32) NULL,
        o9_dt DATETIME NULL, o9_event VARCHAR(32) NULL)""")
    o9db.execute("TRUNCATE TABLE arm_gate_recon")
    for ms, side, s in uniq:
        if side == 'bt':
            o9db.execute("INSERT INTO arm_gate_recon (backtest_dt, backtest_event) VALUES (%s,%s)", (dt(ms), s))
        else:
            o9db.execute("INSERT INTO arm_gate_recon (o9_dt, o9_event) VALUES (%s,%s)", (dt(ms), s))
    print('wrote %d rows -> o9_live.arm_gate_recon  (span %s -> %s)' % (len(uniq), dt(lo), dt(hi)))
    o9db.disconnect(); dev.disconnect()


if __name__ == '__main__':
    main()
