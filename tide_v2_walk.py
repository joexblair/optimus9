"""tide_v2_walk.py — rebuild v2_walk from the GREENFIELD causal machine (tide_machine, no arm_delay) and add a hard
STOP, choosing the stop value that maximises final compounding equity. Reuses the v2_walk PnL model: dynamic 5x sizing
(notional=LEV*acct, capped MAX_LOT coins), compounding, 0.20% RT cost. The stop is applied via per-trade MAE — a resting
order at -S fills the moment price hits it, so r = -S if mae<=-S else ret (causal: the level is pre-set). Sweeps the
stop, reports the equity-vs-stop curve + the profit-max stop, then writes the v2_walk table at that stop.
Run:  python3 tide_v2_walk.py   (report only, no DB write:  python3 tide_v2_walk.py dry)"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from tide_machine import run_config

S10 = lambda tf, src: {'s10r': (tf, ('k', 6, 6, 5, src), 'emerging')}
CONFIGS = [                                                     # (name, ovr, cfg) — top configs from the minimax sweep
    ('ride 2,2 600/hl2 oob',  S10(600, 'hl2'),   dict(exit_gate='oob', wait_breach=True, fin_lb=12, fin_fwd=12)),
    ('ride 1,1 600/hl2 oob',  S10(600, 'hl2'),   dict(exit_gate='oob', wait_breach=True, fin_lb=6, fin_fwd=6)),
    ('ride 4,2 600/hl2 oob',  S10(600, 'hl2'),   dict(exit_gate='oob', wait_breach=True, fin_lb=24, fin_fwd=12)),
    ('scalp 2,1 720 mid',     S10(720, 'close'), dict(exit_gate='mid', wait_breach=False, fin_lb=12, fin_fwd=6)),
    ('scalp 2,1 360 mid',     S10(360, 'close'), dict(exit_gate='mid', wait_breach=False, fin_lb=12, fin_fwd=6)),
    ('default 1,1 600 oob',   S10(600, 'close'), dict(exit_gate='oob', wait_breach=True)),
]
SPAN_D = 30                                                     # continuous window for the compounding equity
START, LEV, MAX_LOT, COST = 500.0, 5.0, 66000, 0.20            # v2_walk PnL model (unchanged)
dt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc)


def get_trades(ovr, cfg):
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    J = Jig(now, hours=SPAN_D * 24, warmup=48, overrides=ovr)
    m = run_config(J, cfg); ts, px = J.ts, J.px
    tr = []
    for e, x, side, ret, mae, route in m['trades']:
        d = 1 if side == 'long' else -1
        seg = (px[e:x + 1] - px[e]) / px[e] * 100.0 * d
        tr.append(dict(ms=int(ts[e]), exms=int(ts[x]), dir=d, epx=float(px[e]),
                       ret=float(ret), mae=float(mae), mfe=float(np.nanmax(seg)), reason=route))
    J.close()
    return sorted(tr, key=lambda t: t['ms'])


def walk(trades, stop):
    acct = START; liq = False; rows = []
    for t in trades:
        if acct <= 0:
            liq = True; break
        r = -stop if (stop is not None and t['mae'] <= -stop) else t['ret']
        lot = min(MAX_LOT, acct * LEV / t['epx']); notional = lot * t['epx']
        pnl = notional * (r - COST) / 100.0; acct += pnl
        rows.append((t, r, lot, notional, pnl, acct))
    return acct, liq, rows


def best_stop(trades):
    stops = [None] + [round(0.2 + 0.05 * k, 2) for k in range(0, 37)]      # None, 0.20 .. 2.00
    best = (None, -1e9, None)
    for s in stops:
        acct, liq, rows = walk(trades, s)
        if not liq and acct > best[1]:
            best = (s, acct, rows)
    return best


def main():
    dry = len(sys.argv) > 1 and sys.argv[1] == 'dry'
    print("=== config x stop joint sweep — max final compounding equity ($%d, %gx, %g%% cost, %dd) ===" % (START, LEV, COST, SPAN_D))
    print("%-24s %4s | %8s %8s | %8s" % ("config", "n", "no-stop$", "beststop", "equity$"))
    results = []
    for name, ovr, cfg in CONFIGS:
        trades = get_trades(ovr, cfg)
        nostop = walk(trades, None)[0]
        bs, bacct, brows = best_stop(trades)
        results.append((name, ovr, cfg, trades, bs, bacct, brows))
        print("%-24s %4d | %8.0f %8s | %8.0f (%.2fx)" %
              (name, len(trades), nostop, "none" if bs is None else "%.2f%%" % bs, bacct, bacct / START))
    results.sort(key=lambda r: -r[5])
    winner = results[0]
    print("\nWINNER: %-24s stop=%s -> $%.0f (%.2fx)" %
          (winner[0], "none" if winner[4] is None else "%.2f%%" % winner[4], winner[5], winner[5] / START))
    profitable = [r for r in results if r[5] > START]
    print("configs net-PROFITABLE (equity > $%d): %d / %d" % (START, len(profitable), len(results)))
    if dry:
        print("[dry] — v2_walk table not written")
        return
    _, _, _, trades, bs, bacct, brows = winner
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute('DROP TABLE IF EXISTS v2_walk')
    db.execute('''CREATE TABLE v2_walk (trade_ms BIGINT, trade_dt DATETIME, trade_dir TINYINT, mae FLOAT, mfe FLOAT,
        exit_dt DATETIME, exit_pct FLOAT, reason VARCHAR(8), entry_px DECIMAL(14,8), lot INT, notional FLOAT,
        pnl_usdt FLOAT, equity FLOAT)''')
    rows = [(t['ms'], dt(t['ms']), t['dir'], round(t['mae'], 3), round(t['mfe'], 3), dt(t['exms']),
             round(r, 3), t['reason'], round(t['epx'], 8), int(lot), round(notional, 2), round(pnl, 2), round(acct, 2))
            for (t, r, lot, notional, pnl, acct) in brows]
    db.executemany('INSERT INTO v2_walk VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
    print("v2_walk written: %d rows @ stop=%s (greenfield causal producer, no arm_delay)" %
          (len(rows), "none" if bs is None else "%.2f%%" % bs))
    db.disconnect()


if __name__ == "__main__":
    main()
