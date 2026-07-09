"""ohlc_watch.py — Joe's method (0708): each monitor wake, capture kline_collection OHLC of recent bars, and DIFF
against the previous capture to catch the live klines MUTATING (raw collected -> sanitiser overwrites with TV truth)
after the live loop already read the raw value. That mutation is the o9-live<->backtest BB desync (backtest=TV=correct,
live=raw=wrong). State in ohlc_capture.json. Run:  python3 ohlc_watch.py"""
import json, os, datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

SF = '/home/joe/thecodes/ohlc_capture.json'
hm = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%H:%M:%S')


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    tp = dev.execute('SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s', ('FARTCOINUSDT',), fetch=True)[0]['tp_pk']
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    rows = dev.execute('SELECT kc_timestamp t,kc_open o,kc_high h,kc_low l,kc_close c,kc_volume v FROM kline_collection '
                       'WHERE kc_tp_pk=%s AND kc_timestamp>=%s ORDER BY kc_timestamp', (tp, now - 25 * 60000), fetch=True)
    cur = {int(r['t']): [float(r['o']), float(r['h']), float(r['l']), float(r['c']), float(r['v'])] for r in rows}
    if os.path.exists(SF):
        prev = json.load(open(SF)); pcap = prev['cap']
        muts = [(int(ts), v, cur[int(ts)]) for ts, v in pcap.items() if int(ts) in cur and cur[int(ts)] != v]
        print("prev capture @ %s (%d bars) — MUTATED since: %d" % (hm(prev['t']), len(pcap), len(muts)))
        for ts, old, new in sorted(muts)[:12]:
            df = ['%s:%g->%g' % (f, o, n) for f, o, n in zip('OHLCV', old, new) if o != n]
            print("  bar %s  %s" % (hm(ts), ", ".join(df)))
        if not muts:
            print("  (no bar mutated between the two captures)")
    else:
        print("first run — captured %d bars, will diff on next wake" % len(cur))
    json.dump({'t': now, 'cap': {str(k): v for k, v in cur.items()}}, open(SF, 'w'))
    dev.disconnect()


if __name__ == "__main__":
    main()
