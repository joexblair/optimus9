"""tape_stability.py — does kline_collection MUTATE for bars that are already finalized? Capture OHLCV of the last
~45min of bars, wait 180s, re-read the SAME bars, and report mutations bucketed by bar AGE. If bars >30min old still
change, the tape is being rewritten (sanitiser) and no read-grace can fix the desync — the fix is upstream. If only
fresh (<1-2min) bars change, a longer settling grace can close it. Run:  python3 tape_stability.py"""
import time, datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

WAIT_S = 180


def snap(dev, tp, lo):
    rows = dev.execute('SELECT kc_timestamp t,kc_open o,kc_high h,kc_low l,kc_close c,kc_volume v FROM kline_collection '
                       'WHERE kc_tp_pk=%s AND kc_timestamp>=%s ORDER BY kc_timestamp', (tp, lo), fetch=True)
    return {int(r['t']): (float(r['o']), float(r['h']), float(r['l']), float(r['c']), float(r['v'])) for r in rows}


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    tp = dev.execute('SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s', ('FARTCOINUSDT',), fetch=True)[0]['tp_pk']
    t0 = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    a = snap(dev, tp, t0 - 45 * 60 * 1000)
    time.sleep(WAIT_S)
    dev.disconnect(); dev.connect()
    b = snap(dev, tp, t0 - 45 * 60 * 1000)
    buckets = {'<2min': [0, 0], '2-10min': [0, 0], '10-30min': [0, 0], '>30min': [0, 0]}  # [mutated, total]
    examples = []
    for ts, va in a.items():
        age = (t0 - ts) / 60000.0
        bk = '<2min' if age < 2 else '2-10min' if age < 10 else '10-30min' if age < 30 else '>30min'
        buckets[bk][1] += 1
        if ts in b and b[ts] != va:
            buckets[bk][0] += 1
            if bk in ('10-30min', '>30min') and len(examples) < 8:
                df = ['%s:%g->%g' % (f, o, n) for f, o, n in zip('OHLCV', va, b[ts]) if o != n]
                examples.append('  age %.0fmin bar %s: %s' % (age, dtm.datetime.fromtimestamp(ts / 1000, timezone.utc).strftime('%H:%M:%S'), ', '.join(df)))
    print('=== tape stability: bars mutated over %ds, by age ===' % WAIT_S)
    for bk, (m, t) in buckets.items():
        print('  %-9s : %d/%d mutated' % (bk, m, t))
    if examples:
        print('FINALIZED bars (>10min old) that STILL changed — the smoking gun:')
        print('\n'.join(examples))
    else:
        print('VERDICT: no bar >10min old changed → finalized bars are STABLE (grace can fix; fresh-bar settling only)')
    dev.disconnect()


if __name__ == "__main__":
    main()
