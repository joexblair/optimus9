"""
cf15_superscope.py (Joe 0628) — the 8-window baseline of the cf15 latch-release edge, on TV-true klines.
Runs cf15_rig.run_window across 8 windows (5 days each, 05-18 → 06-27) + applies the costed metric per
window (WON = mfe>=0.7% take-profit; Bybit taker 0.11% RT + 0.20% slip; 66k coins / x50 / $500) — so we
see whether the edge holds OUT of the 06-17→06-22 window it was found in.

  python3 cf15_superscope.py
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from cf15_rig import run_window


def ms(s): return int(dtm.datetime.strptime('2026-' + s, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)


# 8 windows × 5 days over the sanitised range (W1's warmup precedes 05-18, on real-but-pre-sanitise klines)
WINDOWS = [('05-18', '05-23'), ('05-23', '05-28'), ('05-28', '06-02'), ('06-02', '06-07'),
           ('06-07', '06-12'), ('06-12', '06-17'), ('06-17', '06-22'), ('06-22', '06-27')]
WON_TARGET = 0.7; FEE = 0.00055 * 2; SLIP = 0.002; COINS = 66000; CAP = 500
NET_PCT = WON_TARGET / 100 - FEE - SLIP

db = DatabaseManager(**get_db_config()); db.connect()
print(f'cf15 SUPERSCOPE — WON = mfe>={WON_TARGET}%  ·  net {NET_PCT*100:.2f}%/trade  ·  {COINS} coins x50 ${CAP}')
print(f"{'window':<16}{'trades':>7}{'hit%':>6}{'net$':>9}{'ret%':>7}")
tn = tq = 0; tnet = 0.0
for a, b in WINDOWS:
    rows = run_window(db, ms(a), ms(b))
    n = len(rows); q = [r for r in rows if r[5] >= WON_TARGET]
    net = sum(NET_PCT * COINS * r[8] for r in q)
    hit = 100 * len(q) / n if n else 0
    print(f"{a}->{b:<9}{n:>7}{hit:>5.0f}%{net:>9.0f}{100*net/CAP:>6.0f}%")
    tn += n; tq += len(q); tnet += net
print(f"{'TOTAL (8w)':<16}{tn:>7}{(100*tq/tn if tn else 0):>5.0f}%{tnet:>9.0f}{100*tnet/CAP:>6.0f}%")
db.disconnect()
