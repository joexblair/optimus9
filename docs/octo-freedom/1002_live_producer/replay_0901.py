"""replay_0901 — drive `optimus9/live/octo_freedom.py` bar by bar over 09-01 the way o9-live would, and
hold it against `report_leash_walk.py`, the acceptance test.

Every bar gets a FRESH 104 h `BiasWindow` built from DB klines ending at that bar - the live path, not
the line cache. The window's end is `ts + 1` ms (`kline_loader.load_window` is half-open), and the
script ASSERTS the window's last bar is the bar being decided, so a replay over history cannot read a
bar o9-live would not yet have.

    python3 replay_0901.py                          # the whole day, 17,280 bars - the proof
    python3 replay_0901.py --from 00:20:00 --to 00:35:00     # a slice, for shaking the code out

The whole day is asserted against the acceptance test's own numbers: MECH 2768 / rule#1 cut 1673 /
EMITTED 1095 / runs 23, the 23 `WALK FIRES FROM` bars with their arm bar and arm dr, and Joe's 9
validated bars among them. A slice prints its signal bars beside the acceptance test's for that span
and asserts nothing.

Writes one JSON line per decided bar to `replay_0901.<from>-<to>.jsonl` beside this script.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time

sys.path.insert(0, '/home/joe/thecodes')

DAY = dt.datetime(2026, 9, 1, tzinfo=dt.timezone.utc)
# report_leash_walk.py on 09-01, tape END_MS 2026-09-08 - the R| rows: (WALK FIRES FROM, last, arm bar, arm dr)
ACCEPT_RUNS = [('00:27:35', '00:31:20', '00:19:20', 1), ('02:40:35', '02:44:20', '02:38:10', -1),
               ('03:38:00', '03:42:25', '03:36:55', 1), ('05:44:10', '05:47:05', '05:30:05', 1),
               ('07:00:40', '07:04:25', '06:57:25', -1), ('08:09:15', '08:09:30', '08:06:20', -1),
               ('08:12:45', '08:16:30', '08:06:20', -1), ('09:02:15', '09:06:30', '08:06:20', -1),
               ('11:30:20', '11:34:05', '10:32:30', 1), ('11:34:15', '11:34:55', '10:32:30', 1),
               ('11:37:00', '11:42:30', '10:32:30', 1), ('13:05:25', '13:11:20', '13:01:55', -1),
               ('13:54:20', '13:55:55', '13:49:15', 1), ('14:50:00', '14:53:45', '14:48:00', 1),
               ('15:13:00', '15:15:00', '15:10:50', -1), ('16:16:10', '16:19:20', '16:08:45', -1),
               ('16:21:20', '16:26:00', '16:08:45', -1), ('17:59:25', '18:03:55', '17:58:30', -1),
               ('18:11:35', '18:18:00', '17:58:30', -1), ('18:20:00', '18:24:40', '17:58:30', -1),
               ('22:24:10', '22:27:55', '21:10:15', -1), ('23:18:50', '23:27:10', '21:10:15', -1),
               ('23:27:20', '23:31:10', '21:10:15', -1)]
ACCEPT_SHAPE = dict(mech=2768, cut=1673, emitted=1095, runs=23)
VALIDATED = ['00:27:35', '02:40:35', '03:38:00', '09:02:15', '14:50:00', '17:59:25', '18:20:00',
             '22:24:10', '23:18:50']


def _ms(hms):
    h, m, s = (int(x) for x in hms.split(':'))
    return int((DAY + dt.timedelta(hours=h, minutes=m, seconds=s)).timestamp() * 1000)


def _hms(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%H:%M:%S')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--from', dest='frm', default='00:00:00')
    ap.add_argument('--to', default='23:59:55')
    a = ap.parse_args()
    import bias_machine as bm
    from sweep_eval import BASE_BIAS
    from optimus9.config import get_db_config
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.live.octo_freedom import OctoFreedom
    from optimus9.live.octo_inputs import OctoConfig

    db = DatabaseManager(**get_db_config()); db.connect()
    cfg = OctoConfig(db)
    prod = OctoFreedom(db, cfg, bm.BiasConfig(**BASE_BIAS))
    t0, t1 = _ms(a.frm), _ms(a.to)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'replay_0901.%s-%s.jsonl' % (a.frm.replace(':', ''), a.to.replace(':', '')))
    fh = open(out, 'w')
    whole_day = (a.frm, a.to) == ('00:00:00', '23:59:55')
    hits = emitted = 0
    fires = []
    trades = []
    noted = []
    tick = time.perf_counter()
    for i, ts in enumerate(range(t0, t1 + 1, 5000)):
        b = time.perf_counter()
        W, inp = prod.window(ts + 1)
        if int(inp.ts[-1]) != ts:
            raise RuntimeError('window ends at %s, not %s - the replay would read the wrong bar'
                               % (_hms(int(inp.ts[-1])), _hms(ts)))
        recs = prod.advance(inp, t0)
        r = recs[-1]
        assert r['ts'] == ts and r['live']
        hits += r['hit']
        emitted += bool(r['emitted'])
        if r['fires']:
            fires.append((ts, r['arm'] * 5000, r['arm_dr']))
        for ev in r['events']:
            if ev[0] == 'close':
                trades.append(ev[1])
            elif ev[0] == 'inert':
                noted.append((ev[1] * 5000, ev[2]))
        fh.write(json.dumps(dict(ts=ts, utc=_hms(ts), bars_stepped=len(recs), hit=r['hit'],
                                 emitted=r['emitted'], fires=r['fires'], arm=r['arm'],
                                 arm_dr=r['arm_dr'], events=[list(map(str, e)) for e in r['events']],
                                 secs=round(time.perf_counter() - b, 3))) + '\n')
        if i % 120 == 0:
            fh.flush()
            print('%s  bars %d  mech %d  emitted %d  fires %d  %.2f s/bar' % (
                _hms(ts), i + 1, hits, emitted, len(fires), (time.perf_counter() - tick) / (i + 1)),
                flush=True)
    fh.close()
    lo, hi = _hms(t0), _hms(t1)
    want = [x for x in ACCEPT_RUNS if lo <= x[0] <= hi]
    got = [(_hms(f), _hms(a_), d) for f, a_, d in fires]
    print('RESULT|bars %d|mech %d|emitted %d|runs %d|secs %.0f'
          % ((t1 - t0) // 5000 + 1, hits, emitted, len(fires), time.perf_counter() - tick))
    print('FIRES|replay|' + ', '.join('%s arm %s %+d' % g for g in got))
    print('FIRES|accept|' + ', '.join('%s arm %s %+d' % (w[0], w[2], w[3]) for w in want))
    print('TRADES|closed %d|noted same-dr %d|open at end %s' % (len(trades), len(noted),
                                                              prod.book.pos if prod.book else None))
    for tr in trades:
        print('TRADE|%s|%s|%+d|%s|%s' % (_hms(tr['open'] * 5000), _hms(tr['close'] * 5000), tr['dr'],
                                         tr['opened_by'], tr['closed_by']))
    if not whole_day:
        print('SLICE|nothing asserted - the acceptance numbers are for the whole day')
        return 0
    bad = []
    shape = dict(mech=hits, cut=hits - emitted, emitted=emitted, runs=len(fires))
    for k_, v in ACCEPT_SHAPE.items():
        if shape[k_] != v:
            bad.append('%s: acceptance %d, replay %d' % (k_, v, shape[k_]))
    if [(w[0], w[2], w[3]) for w in want] != got:
        bad.append('the WALK FIRES FROM bars differ')
    miss = [v for v in VALIDATED if v not in {g[0] for g in got}]
    if miss:
        bad.append('validated bars missing: ' + ', '.join(miss))
    for b_ in bad:
        print('M|FAIL|' + b_)
    print('M|PASS|the live path reproduces the acceptance test on 09-01' if not bad else
          'M|FAIL|%d difference(s)' % len(bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
