"""
kline_sanitiser.py (Joe 0627) — reconcile kline_collection OHLC against TradingView ground-truth CSVs.

Why: the multi-window backtest validation only stands if our klines == what we see on TV. Most of the tape
already matches (verified vs the Bybit feed); the soft spots are the SYNTHETIC gap-fills — the ruler-line
rows (identical 1m volume replicated across all twelve 5s bars + a flat/linear price ramp). Drop a TV CSV
into ./transfer/kline_sanitise/ and this overwrites the matching rows' OHLC with TV's truth.

Design (agreed):
  • Detect synth by the RULER-LINE volume — a minute whose 12 bars share ONE volume — for the report only;
    the overwrite applies to the whole CSV range (TV is truth; real rows are near-no-ops).
  • Volume is left untouched (optional system-wide).
  • Both TV and klinecollect are OPEN-labeled, so TV time*1000 == kc_timestamp directly.
  • klinecollect is 5s: a 5s CSV maps row-for-row; 1s aggregates to 5s; coarser is rejected (can't refine).
  • Every change → kline_sanitise_log (before→after, reversible). dry_run reports without writing.
"""
import csv
import datetime as dtm
from logger import get_logger


class KlineSanitiser:
    def __init__(self, db, tp_pk=1):
        self._db = db
        self._tp = tp_pk
        self._log = get_logger('KlineSanitiser')
        db.execute('''CREATE TABLE IF NOT EXISTS kline_sanitise_log (
            ksl_pk BIGINT AUTO_INCREMENT PRIMARY KEY, ksl_at DATETIME, ksl_source VARCHAR(120),
            ksl_timestamp BIGINT, was_synth TINYINT, action VARCHAR(8),
            old_o DOUBLE, old_h DOUBLE, old_l DOUBLE, old_c DOUBLE,
            new_o DOUBLE, new_h DOUBLE, new_l DOUBLE, new_c DOUBLE, INDEX(ksl_timestamp))''')

    @staticmethod
    def parse(path):
        """TV CSV → (resolution_seconds, sorted [(t_ms, o, h, l, c)]). Resolution = the modal (min) bar gap."""
        rows = []
        with open(path) as f:
            r = csv.reader(f); next(r)
            for x in r:
                if len(x) < 5 or x[1] in ('', 'nan'):
                    continue
                rows.append((int(x[0]) * 1000, float(x[1]), float(x[2]), float(x[3]), float(x[4])))
        rows.sort()
        gaps = [rows[i + 1][0] - rows[i][0] for i in range(min(200, len(rows) - 1)) if rows[i + 1][0] != rows[i][0]]
        return (min(gaps) // 1000 if gaps else 0), rows

    @staticmethod
    def _to_5s(res, rows):
        """Normalise to 5s. 5s → as-is; 1s → aggregate (O=first,H=max,L=min,C=last); coarser → None."""
        if res == 5:
            return rows
        if res == 1:
            buckets = {}
            for t, o, h, l, c in rows:
                b = (t // 5000) * 5000
                if b in buckets:
                    v = buckets[b]; v[1] = max(v[1], h); v[2] = min(v[2], l); v[3] = c
                else:
                    buckets[b] = [o, h, l, c]
            return [(b, v[0], v[1], v[2], v[3]) for b, v in sorted(buckets.items())]
        return None

    def _synth_minutes(self, lo, hi):
        """Minutes whose 12 5s bars share ONE volume — the synthetic ruler-line signature."""
        rows = self._db.execute(
            '''SELECT (kc_timestamp DIV 60000) * 60000 m FROM kline_collection
               WHERE kc_tp_pk = %s AND kc_timestamp >= %s AND kc_timestamp < %s
               GROUP BY m HAVING COUNT(*) >= 12 AND COUNT(DISTINCT kc_volume) = 1''',
            (self._tp, (lo // 60000) * 60000, hi + 60000), fetch=True)
        return {r['m'] for r in rows}

    def reconcile(self, path, dry_run=False):
        res, rows = self.parse(path)
        norm = self._to_5s(res, rows)
        src = path.split('/')[-1]
        if norm is None:
            self._log.warning(f'{src}: resolution {res}s coarser than 5s — cannot refine klinecollect; skipped')
            return {'source': src, 'skipped': f'{res}s coarser than 5s'}
        lo, hi = norm[0][0], norm[-1][0]
        existing = {r['t']: (float(r['o']), float(r['h']), float(r['l']), float(r['c']))
                    for r in self._db.execute(
                        '''SELECT kc_timestamp t, kc_open o, kc_high h, kc_low l, kc_close c FROM kline_collection
                           WHERE kc_tp_pk = %s AND kc_timestamp >= %s AND kc_timestamp <= %s''',
                        (self._tp, lo, hi), fetch=True)}
        synth_mins = self._synth_minutes(lo, hi)
        tv = {t: (o, h, l, c) for t, o, h, l, c in norm}
        now = dtm.datetime.utcnow()
        counts = {'tv': 0, 'flat': 0, 'insert': 0, 'synth': 0, 'noop': 0}
        logs = []; last_c = None
        # walk the FULL 5s grid for the range: TV's bar where it traded, else carry-forward FLAT (a no-trade
        # bar is flat — leaving the synth ramp there would forge volatility the market never had, Joe 0627)
        for t in range(lo, hi + 1, 5000):
            if t in tv:
                o, h, l, c = tv[t]; last_c = c; kind = 'tv'
            elif last_c is not None:
                o = h = l = c = last_c; kind = 'flat'
            else:
                continue
            old = existing.get(t)
            if old is not None and max(abs(old[0] - o), abs(old[1] - h), abs(old[2] - l), abs(old[3] - c)) < 1e-9:
                counts['noop'] += 1; continue
            action = 'insert' if old is None else kind
            isyn = int(((t // 60000) * 60000) in synth_mins)
            counts[action] += 1; counts['synth'] += isyn
            logs.append((now, src, t, isyn, action,
                         old[0] if old else None, old[1] if old else None, old[2] if old else None, old[3] if old else None,
                         o, h, l, c))
            if not dry_run:
                if old is None:
                    self._db.execute('''INSERT INTO kline_collection
                        (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
                        VALUES (%s, %s, %s, %s, %s, %s, 0)''', (self._tp, t, o, h, l, c))
                else:
                    self._db.execute('UPDATE kline_collection SET kc_open=%s, kc_high=%s, kc_low=%s, kc_close=%s '
                                     'WHERE kc_tp_pk=%s AND kc_timestamp=%s', (o, h, l, c, self._tp, t))
        if logs and not dry_run:
            self._db.executemany('''INSERT INTO kline_sanitise_log
                (ksl_at, ksl_source, ksl_timestamp, was_synth, action, old_o, old_h, old_l, old_c, new_o, new_h, new_l, new_c)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', logs)
        report = {'source': src, 'resolution_s': res, 'tv_overwritten': counts['tv'], 'flat_filled': counts['flat'],
                  'inserted': counts['insert'], 'noop': counts['noop'], 'synth_touched': counts['synth'],
                  'dry_run': dry_run,
                  'range': (str(dtm.datetime.utcfromtimestamp(lo / 1000)), str(dtm.datetime.utcfromtimestamp(hi / 1000)))}
        self._log.info(f"{'DRY ' if dry_run else ''}sanitise {src}: tv {counts['tv']} · flat {counts['flat']} · "
                       f"ins {counts['insert']} · synth {counts['synth']} · noop {counts['noop']}")
        return report
