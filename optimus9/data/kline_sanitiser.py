"""
kline_sanitiser.py (Joe 0627) — reconcile kline_collection OHLC against TradingView ground-truth CSVs.

Why: the multi-window backtest validation only stands if our klines == what we see on TV. Most of the tape
already matches (verified vs the Bybit feed); the soft spots are the SYNTHETIC gap-fills — the ruler-line
rows (identical 1m volume replicated across all twelve 5s bars + a flat/linear price ramp). Drop a TV CSV
into ./transfer/kline_sanitise/ and this overwrites the matching rows' OHLC with TV's truth.

Design (agreed):
  • Detect synth by the RULER-LINE volume — a minute whose 12 bars share ONE volume — for the report only;
    the overwrite applies to the whole CSV range (TV is truth; real rows are near-no-ops).
  • Volume (Joe 0804): was previously discarded by parse() and left untouched. That defeated
    filler_invisible (bias_machine.py:141-146), which hides a bar only when kc_volume == 0:
      - SyntheticBackfiller.split() gave every phantom 5s child unit_v = V/12, i.e. volume > 0
      - this sanitiser then repaired their OHLC but never zeroed the volume
      - result: 175,970 of 587,521 bars (30.0%) from 05-18 to 07-02 were flat carry-forward bars
        that the oscillators consumed as real trades, vs 11.3% in the collector-only period.
        That is what the 07-12 change point in the 0804 permutation run actually detected.
    Now: a `flat` carry-forward bar is by definition a NO-TRADE bar, so it is written with
    kc_volume = 0. A `tv` bar carries the CSV's own Volume on INSERT. Overwriting an EXISTING
    row's volume from TV stays OFF by default (write_tv_volume=False) — that is a behaviour change
    to a live service and is Joe's call; TV and collector volume measured identical to the unit on
    07-30/31, so it is low-risk if he wants it on.
  • Both TV and klinecollect are OPEN-labeled, so TV time*1000 == kc_timestamp directly.
  • klinecollect is 5s: a 5s CSV maps row-for-row; 1s aggregates to 5s; coarser is rejected (can't refine).
  • Every change → kline_sanitise_log (before→after, reversible). dry_run reports without writing.
"""
import csv
import datetime as dtm
from logger import get_logger


class KlineSanitiser:
    _WRITE_CHUNK = 5000     # one executemany of a whole file blows InnoDB's lock table (1206)

    def __init__(self, db, tp_pk=1, write_tv_volume=False):
        self._db = db
        self._tp = tp_pk
        # Joe 0804, ESCALATED not decided: should a TV bar overwrite an EXISTING row's kc_volume?
        # The original design left volume untouched deliberately. TV and collector volume measured
        # identical to the unit on 07-30/31 (229,590,365 both ways), so turning this on is low-risk
        # — but it is a behaviour change to a live service, so it defaults OFF. INSERTs always carry
        # the CSV's volume regardless; this flag only governs UPDATEs of rows that already exist.
        self.write_tv_volume = bool(write_tv_volume)
        self._log = get_logger('KlineSanitiser')
        db.execute('''CREATE TABLE IF NOT EXISTS kline_sanitise_log (
            ksl_pk BIGINT AUTO_INCREMENT PRIMARY KEY, ksl_at DATETIME, ksl_source VARCHAR(120),
            ksl_timestamp BIGINT, was_synth TINYINT, action VARCHAR(8),
            old_o DOUBLE, old_h DOUBLE, old_l DOUBLE, old_c DOUBLE,
            new_o DOUBLE, new_h DOUBLE, new_l DOUBLE, new_c DOUBLE,
            old_v DOUBLE, new_v DOUBLE, INDEX(ksl_timestamp))''')
        for _c in ('old_v', 'new_v'):                     # additive on an existing table (Joe 0804)
            try:
                db.execute(f'ALTER TABLE kline_sanitise_log ADD COLUMN {_c} DOUBLE')
            except Exception:
                pass                                       # already present

    @staticmethod
    def parse(path):
        """TV CSV → (resolution_seconds, sorted [(t_ms, o, h, l, c, v)]). Resolution = the modal (min) gap.

        Volume (Joe 0804): the 6th column IS read now, by NAME not position — TV exports are
        inconsistent about it. 21 of 33 files in processed/ carry `BB1,BB2,K2` or `DEMA,BB1,BB2,K2`
        where Volume should be, so taking x[5] blindly would import a Bollinger value as volume.
        Missing/unnamed volume → 0.0, which reads as a no-trade bar; that is the safe direction."""
        rows = []
        with open(path) as f:
            r = csv.reader(f)
            hdr = next(r)
            vi = next((i for i, h in enumerate(hdr) if h.strip().lower() == 'volume'), None)
            for x in r:
                if len(x) < 5 or x[1] in ('', 'nan'):
                    continue
                v = 0.0
                if vi is not None and vi < len(x) and x[vi] not in ('', 'nan'):
                    v = float(x[vi])
                rows.append((int(x[0]) * 1000, float(x[1]), float(x[2]), float(x[3]), float(x[4]), v))
        rows.sort()
        gaps = [rows[i + 1][0] - rows[i][0] for i in range(min(200, len(rows) - 1)) if rows[i + 1][0] != rows[i][0]]
        return (min(gaps) // 1000 if gaps else 0), rows

    @staticmethod
    def _to_5s(res, rows):
        """Normalise to 5s. 5s → as-is; 1s → aggregate (O=first,H=max,L=min,C=last,V=SUM); coarser → None."""
        if res == 5:
            return rows
        if res == 1:
            buckets = {}
            for t, o, h, l, c, vol in rows:
                b = (t // 5000) * 5000
                if b in buckets:
                    q = buckets[b]; q[1] = max(q[1], h); q[2] = min(q[2], l); q[3] = c; q[4] += vol
                else:
                    buckets[b] = [o, h, l, c, vol]
            return [(b, q[0], q[1], q[2], q[3], q[4]) for b, q in sorted(buckets.items())]
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
        self._log.info(f'{src}  ·  range {dtm.datetime.utcfromtimestamp(lo / 1000)} → '
                       f'{dtm.datetime.utcfromtimestamp(hi / 1000)}  ({res}s)')
        existing = {r['t']: (float(r['o']), float(r['h']), float(r['l']), float(r['c']), float(r['v']))
                    for r in self._db.execute(
                        '''SELECT kc_timestamp t, kc_open o, kc_high h, kc_low l, kc_close c, kc_volume v
                           FROM kline_collection
                           WHERE kc_tp_pk = %s AND kc_timestamp >= %s AND kc_timestamp <= %s''',
                        (self._tp, lo, hi), fetch=True)}
        synth_mins = self._synth_minutes(lo, hi)
        tv = {t: (o, h, l, c, v) for t, o, h, l, c, v in norm}
        now = dtm.datetime.utcnow()
        counts = {'tv': 0, 'flat': 0, 'insert': 0, 'synth': 0, 'noop': 0}
        logs = []; ins = []; upd = []; last_c = None
        # walk the FULL 5s grid for the range: TV's bar where it traded, else carry-forward FLAT (a no-trade
        # bar is flat — leaving the synth ramp there would forge volatility the market never had, Joe 0627)
        for t in range(lo, hi + 1, 5000):
            if t in tv:
                o, h, l, c, v = tv[t]; last_c = c; kind = 'tv'
            elif last_c is not None:
                o = h = l = c = last_c; v = 0.0; kind = 'flat'   # no-trade bar -> ZERO volume (Joe 0804)
            else:
                continue
            old = existing.get(t)
            # a flat row is only a no-op if its volume is ALREADY 0 — otherwise filler_invisible
            # cannot see it, which is the whole defect this fixes.
            if old is not None and max(abs(old[0] - o), abs(old[1] - h), abs(old[2] - l), abs(old[3] - c)) < 1e-9 \
                    and not (kind == 'flat' and old[4] != 0.0):
                counts['noop'] += 1; continue
            action = 'insert' if old is None else kind
            isyn = int(((t // 60000) * 60000) in synth_mins)
            counts[action] += 1; counts['synth'] += isyn
            # volume actually written: insert -> the CSV's own (0 for a flat bar); update -> 0 on a
            # flat row, else the existing value unless write_tv_volume is on.
            newv = v if old is None else (0.0 if kind == 'flat' else (v if self.write_tv_volume else old[4]))
            logs.append((now, src, t, isyn, action,
                         old[0] if old else None, old[1] if old else None, old[2] if old else None, old[3] if old else None,
                         o, h, l, c, old[4] if old else None, newv))
            if not dry_run:
                (ins if old is None else upd).append(
                    (self._tp, t, o, h, l, c, newv) if old is None else (o, h, l, c, newv, self._tp, t))
        # BATCHED (Joe 0804). Was one round-trip per bar: a 2-day file is 34,560 statements and the
        # 16-file 0804 refit measured ~4k rows/min => 2h+. Same semantics, chunked executemany.
        # kc_volume is now always written on UPDATE — `newv` already carries the existing value when
        # nothing should change, so the single statement is equivalent to the old three branches.
        if not dry_run:
            for i in range(0, len(ins), self._WRITE_CHUNK):
                self._db.executemany('''INSERT INTO kline_collection
                    (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)''', ins[i:i + self._WRITE_CHUNK])
            for i in range(0, len(upd), self._WRITE_CHUNK):
                self._db.executemany('''UPDATE kline_collection
                    SET kc_open=%s, kc_high=%s, kc_low=%s, kc_close=%s, kc_volume=%s
                    WHERE kc_tp_pk=%s AND kc_timestamp=%s''', upd[i:i + self._WRITE_CHUNK])
        if logs and not dry_run:
            self._db.executemany('''INSERT INTO kline_sanitise_log
                (ksl_at, ksl_source, ksl_timestamp, was_synth, action, old_o, old_h, old_l, old_c,
                 new_o, new_h, new_l, new_c, old_v, new_v)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', logs)
        report = {'source': src, 'resolution_s': res, 'tv_overwritten': counts['tv'], 'flat_filled': counts['flat'],
                  'inserted': counts['insert'], 'noop': counts['noop'], 'synth_touched': counts['synth'],
                  'dry_run': dry_run,
                  'range': (str(dtm.datetime.utcfromtimestamp(lo / 1000)), str(dtm.datetime.utcfromtimestamp(hi / 1000)))}
        self._log.info(f"{'DRY ' if dry_run else ''}sanitise {src}: tv {counts['tv']} · flat {counts['flat']} · "
                       f"ins {counts['insert']} · synth {counts['synth']} · noop {counts['noop']}")
        return report
