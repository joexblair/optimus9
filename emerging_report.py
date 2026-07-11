"""emerging_report.py (Joe 0705) — emerging line values per 5s bar, 0705 09:00:00 UTC → now (no warmup shown).

Writes pk_optimizer.emerging_report. Columns (Joe's order, with blank spacer columns for readability):
  utc_dt, s5m, _, s5Mage, _, s3m, _, s3Mage, _, s3r, _, s4m, _, s4Mage, _, s4r, _, s2Mage
Mage lines are s?M in code (s5Mage=s5M etc). Values are EMERGING (W.line, value_mode-honoured / causal).
"""
import sys, time, calendar
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.live.strategy import StrategyLoop

SYM = 'FARTCOINUSDT'
START_MS = int(time.time() * 1000) - 24 * 3600 * 1000    # LAST 24 HOURS (dynamic; was date-pinned)
# label -> code line name (Joe's Mage = s?M)
COLS = [('s30Mage', 's30M'),('s30m', 's30m'),('s15Mage', 's15M'),('s15m', 's15m'),('s5m', 's5m'), ('s5Mage', 's5M'), ('s3m', 's3m'), ('s3Mage', 's3M'), ('s3r', 's3r'),
        ('s4m', 's4m'), ('s4Mage', 's4M'), ('s4r', 's4r'), ('s2Mage', 's2M')]


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    strat = StrategyLoop(dev, bm.BiasConfig(**BASE_BIAS), lr_config(dev), SYM, buffer_hours=30, warmup_hours=6)
    W = strat.window(int(time.time() * 1000))
    ts = W.ts
    series = {lbl: W.line(code) for lbl, code in COLS}

    # build table: value cols interleaved with blank spacer cols (blank1..blank8)
    valcols = [lbl for lbl, _ in COLS]
    coldefs = ['utc_dt DATETIME']
    insert_cols = ['utc_dt']
    bn = 0
    for i, lbl in enumerate(valcols):
        coldefs.append('`%s` FLOAT' % lbl); insert_cols.append('`%s`' % lbl)
        if i < len(valcols) - 1:
            bn += 1; coldefs.append('blank%d VARCHAR(1)' % bn); insert_cols.append('blank%d' % bn)
    dev.execute('DROP TABLE IF EXISTS emerging_report')
    dev.execute('CREATE TABLE emerging_report (id BIGINT AUTO_INCREMENT PRIMARY KEY, %s)' % ', '.join(coldefs))

    ph = ','.join(['%s'] * len(insert_cols))
    sql = 'INSERT INTO emerging_report (%s) VALUES (%s)' % (','.join(insert_cols), ph)
    rows = []
    for k in range(len(ts)):
        if int(ts[k]) < START_MS:
            continue
        dt = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(ts[k]) / 1000))
        vals = [dt]
        for j, lbl in enumerate(valcols):
            vals.append(round(float(series[lbl][k]), 2))
            if j < len(valcols) - 1:
                vals.append(None)               # blank spacer
        rows.append(tuple(vals))
    if rows:
        dev.executemany(sql, rows)
    print('wrote %d rows -> pk_optimizer.emerging_report  (%s -> %s)'
          % (len(rows), rows[0][0] if rows else '-', rows[-1][0] if rows else '-'))
    dev.disconnect()


if __name__ == '__main__':
    main()
