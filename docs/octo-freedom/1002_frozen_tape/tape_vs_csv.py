"""Joe's TV export (BYBIT:FARTCOINUSDT.P 5S) vs the stored tape (kline_collection), bar for bar. Reads only."""
import sys, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9.db.database_manager import DatabaseManager
from optimus9.db.kline_loader import KlineLoader

CSV = '/home/joe/thecodes/transfer/BYBIT_FARTCOINUSDT.P, 5S_d6c05.csv'
TICK = 1e-5
h = lambda t: dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
tv = pd.read_csv(CSV)
tv['ts'] = tv['time'].astype(np.int64) * 1000
db = DatabaseManager(**get_db_config()); db.connect()
tp = db.execute("SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit='FARTCOINUSDT'", fetch=True)[0]['tp_pk']
t0, t1 = int(tv.ts.iloc[0]), int(tv.ts.iloc[-1])
kc = KlineLoader(db).load_window(tp, t0, t1 + 5000)
for c in ('open', 'high', 'low', 'close', 'volume'):
    kc[c] = kc[c].astype(float)
kc['timestamp'] = kc['timestamp'].astype(np.int64)
print('TV rows', len(tv), h(t0), '->', h(t1), '| grid slots', (t1 - t0) // 5000 + 1)
print('kc rows', len(kc), '| kc V>0', int((kc.volume > 0).sum()), '| kc V=0', int((kc.volume == 0).sum()))
# alignment check: exact-close match rate at three offsets, on kc V>0 bars
for off in (-5000, 0, 5000):
    m = kc[kc.volume > 0].merge(tv.assign(ts=tv.ts + off), left_on='timestamp', right_on='ts', suffixes=('', '_tv'))
    eq = (np.round((m.close - m.close_tv) / TICK) == 0).mean()
    print('offset %+d ms: joined %d, close equal %.4f' % (off, len(m), eq))
grid = pd.DataFrame({'ts': np.arange(t0, t1 + 5000, 5000, dtype=np.int64)})
g = grid.merge(kc.rename(columns={'timestamp': 'ts'}), on='ts', how='left').merge(
    tv[['ts', 'open', 'high', 'low', 'close']].rename(columns=lambda c: c if c == 'ts' else c + '_tv'), on='ts', how='left')
has_kc = g.close.notna(); has_tv = g.close_tv.notna(); vpos = g.volume.fillna(0) > 0
d = np.zeros(len(g), int)
for c in ('open', 'high', 'low', 'close'):
    dd = np.abs(np.round((g[c] - g[c + '_tv']) / TICK)).fillna(0).astype(int).to_numpy()
    d = np.maximum(d, dd)
cat = np.full(len(g), '', object)
cat[~has_kc] = 'kc missing'
cat[has_kc & vpos & has_tv & (d == 0)] = 'equal'
cat[has_kc & vpos & has_tv & (d > 0)] = 'kc V>0, OHLC differs'
cat[has_kc & ~vpos & ~has_tv] = 'kc V=0, no TV row'
cat[has_kc & ~vpos & has_tv] = 'kc V=0, TV row present'
cat[has_kc & vpos & ~has_tv] = 'kc V>0, no TV row'
g['cat'] = cat; g['d'] = d
print('--- per slot')
print(g.cat.value_counts().to_string())
eqd = g[g.cat == 'kc V>0, OHLC differs'].d
if len(eqd):
    print('--- max tick diff on "kc V>0, OHLC differs" bars:', eqd.value_counts().sort_index().to_string())
bad = ~g.cat.isin(['equal', 'kc V=0, no TV row'])
print('--- runs of consecutive disagreeing slots (any category other than equal / kc V=0 no TV row)')
runs = []; j = 0; n = len(g); b = bad.to_numpy()
while j < n:
    if b[j]:
        k = j
        while k + 1 < n and b[k + 1]:
            k += 1
        sub = g.iloc[j:k + 1]
        runs.append((h(sub.ts.iloc[0]), h(sub.ts.iloc[-1]), k - j + 1, dict(sub.cat.value_counts()), int(sub.d.max())))
        j = k + 1
    else:
        j += 1
print('runs', len(runs), '| run length counts', pd.Series([r[2] for r in runs]).value_counts().sort_index().to_dict())
for r in sorted(runs, key=lambda r: -r[2])[:25]:
    print(r)
g.to_csv('/home/joe/.claude/jobs/639244ab/tmp/tape_vs_csv.grid.csv', index=False)
