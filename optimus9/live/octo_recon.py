"""octo_recon — the recon job: o9-live's octo-freedom actions held against the backtest, bar for bar.

Joe 0929: MVP1's one job is *"ensuring the backtest signals matches the live signal"*. Procedure:
`docs/o9-live-recon/RECON.md`. Joe 1002: *"yes"* to building it, after the live start.

ONE JOB: re-run the octo-freedom chain over a window, compare it with what o9-live wrote, bank both
and the differences. It changes nothing in o9-live, the exchange or the ledger.

THE REFERENCE is the chain `RECON.md` step 3 names (Joe 1002, *"A is the only choice - causal all the
way"*): `leash_walk` + `arm_state` on inputs assembled as `report_leash_walk.py` assembles them, rule#1
at `gate_open(k, 60)`, `trade_walk` for the exits - here `optimus9/live/octo_freedom.OctoFreedom` over
ONE window, whose code is the live producer's. Its lines are built from the DB tape AS IT STANDS AT
RECON TIME with the line cache's own recipe (`octo_inputs.line_overrides`). The 94.5-day line cache
(`build_ws_lines.TAPE_END` 2026-09-30) does not reach today; recomputing from the stored tape is what
Joe 0929 asked the cache to test: *"is cache and real-time kline collection in sync"*.

THE WINDOW: the trade book starts 24 h before o9-live's first live bar (Joe 1002: *"24 hours
before"*), with 104 h of warmup behind that (Joe 1001: *"#3 window is approved"*), and runs to the
newest closed bar.

THE COMPARISON, three parts, per bar at or after o9-live's first live bar:
    A. SIGNALS - MVP1's core. Every reference WALK FIRES FROM bar against every bar where the live dump
       has an `open` line (`octo-sig` or `non-trading octo-sig` - every fire writes one).
    B. ACTIONS - the live dump against the book o9-live SHOULD have run: empty at its first live bar
       (Joe 1002: stay flat), fed the reference's signals, same rules. `RECON.md` step 4 order: an
       action on the bar, same side, same reason, same open/close role.
    C. PRE-START - Joe's trade list starting 24 h earlier (Joe 1002: *"24 hours before"*) against that
       live-start book. Differences here are the stay-flat ruling at work, labelled, not counted.

THE FOUR CLASSES (`RECON.md`): `selection` and `stop` are decided here. `causality` is the 24-hour
re-validation: every verdict this run banks is compared with the same bar's verdict from the previous
run; a verdict that moves on the same bars is the lookahead signature. `cache` needs o9-live's own
per-bar inputs, which it does not record yet - reported as not measured.

    python3 -m optimus9.live.octo_recon                       # one job, now
    python3 -m optimus9.live.octo_recon --live-start MS       # o9-live's first live bar, if not in the log
    python3 -m optimus9.live.octo_recon --watch               # the monitor: one job per new dump line

THE MONITOR (`RECON.md`'s wake mechanism): `--watch` runs a job whenever the dump grows. Lines that
arrive while a job runs are covered by the next one, because every job compares the whole window.
A session watches `o9live_recon.log` for MISMATCH / MOVED lines instead of being held open per signal.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')

from optimus9.live.octo_freedom import BAR_MS, LABEL, OctoFreedom  # noqa: E402
from optimus9.live.octo_loop import LATE_OPEN_MS, side_of  # noqa: E402

DUMP = os.environ.get('O9_TRADE_SIGNAL_DUMP', '/home/joe/thecodes/o9live_trade_signal_dump.log')
RUNLOG = os.environ.get('O9_OCTO_RUNLOG', '/home/joe/thecodes/o9live_octo.log')
REPORT = os.environ.get('O9_RECON_REPORT', '/home/joe/thecodes/o9live_recon.log')
PRE_START_MS = 24 * 3600 * 1000            # Joe 1002: the recon's backtest trade list starts 24 h before
WARMUP_H = 104                             # Joe 1001: "#3 window is approved"

DDL = [
    """CREATE TABLE IF NOT EXISTS octo_recon_run (
        run_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
        run_ms      BIGINT NOT NULL,
        live_start  BIGINT NOT NULL,
        book_start  BIGINT NOT NULL,
        last_bar    BIGINT NOT NULL,
        cfg_key     VARCHAR(80) NOT NULL,
        tape_sha1   CHAR(40) NOT NULL,
        tape_bars   INT NOT NULL,
        ref_fires   INT NOT NULL,
        live_lines  INT NOT NULL,
        matched     INT NOT NULL,
        mismatched  INT NOT NULL,
        pre_start   INT NOT NULL,
        moved       INT NOT NULL,
        secs        DOUBLE NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS octo_recon_verdict (
        run_id   BIGINT NOT NULL,
        bar_ms   BIGINT NOT NULL,
        hit      TINYINT NOT NULL,
        emitted  TINYINT NULL,
        fires    TINYINT NOT NULL,
        arm_ms   BIGINT NULL,
        arm_dr   TINYINT NULL,
        events   VARCHAR(255) NOT NULL,
        PRIMARY KEY (run_id, bar_ms))""",
    """CREATE TABLE IF NOT EXISTS octo_recon_mismatch (
        run_id   BIGINT NOT NULL,
        bar_ms   BIGINT NOT NULL,
        cls      VARCHAR(16) NOT NULL,
        ref      VARCHAR(255) NULL,
        live     VARCHAR(255) NULL,
        detail   VARCHAR(255) NULL,
        KEY k_run (run_id))""",
]


def _hms(ms):
    return dt.datetime.fromtimestamp(int(ms) / 1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def live_start_from_log(path=RUNLOG):
    """o9-live's first live bar: the first 'bar <ms> ...' line after the LAST startup banner."""
    first = None
    with open(path) as fh:
        for line in fh:
            if line.startswith('o9-live REALTIME'):
                first = None
            elif line.startswith('bar ') and first is None and 'producer=octo' not in line:
                first = int(line.split()[1])
    if first is None:
        raise RuntimeError('no decided bar after the last o9-live banner in %s' % path)
    return first


def read_dump(path=DUMP):
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [json.loads(x) for x in fh if x.strip()]


def reference(db, cfg, bias_cfg, book_start, last_bar):
    """Run the chain over one window. -> (records from book_start on, window ts, tape sha1)."""
    hours = (int(last_bar) - int(book_start)) / 3600000.0 + 1.0 / 720
    prod = OctoFreedom(db, cfg, bias_cfg, lookback_h=hours, warmup_h=WARMUP_H)
    W, inp = prod.window(int(last_bar) + 1)
    if int(inp.ts[-1]) != int(last_bar):
        raise RuntimeError('reference window ends at %s, not %s' % (_hms(inp.ts[-1]), _hms(last_bar)))
    base = W.base[['timestamp', 'open', 'high', 'low', 'close', 'volume']].to_numpy(dtype=float)
    sha = hashlib.sha1(np.ascontiguousarray(base).tobytes()).hexdigest()
    recs = prod.advance(inp, int(book_start))
    return [r for r in recs if r['ts'] >= int(book_start)], inp, sha


def live_shaped(recs, inp, cfg, live_start):
    """The trade book o9-live SHOULD have run: empty at its first live bar (Joe 1002: stay flat), fed the
    reference's signals with the same rules. -> [(bar_ms, event)]."""
    from optimus9.compute.trade_walk import TradeBook
    fires = {r['ts']: r['arm_dr'] for r in recs if r['fires']}
    book = TradeBook(cfg.mae_cap, LABEL)
    ts = inp.ts
    out = []
    for j in range(int(np.searchsorted(ts, live_start)), len(ts)):
        t = int(ts[j])
        sig = t in fires
        for ev in book.step(t // BAR_MS, int(inp.DR[j]), int(inp.DR[j - 1]), float(inp.px[j]), sig,
                            fires[t] if sig else None):
            out.append((t, ev))
    return out


def expected_lines(events, gap):
    """The dump lines a book's events imply. -> {bar_ms: [(action, side, reason)]}."""
    exp, how = {}, {}
    for t, ev in events:
        if ev[0] == 'open':
            reason = 'non-trading octo-sig' if gap.get(t, False) else LABEL
            exp.setdefault(t, []).append(('open', side_of(ev[1]['dr']), reason))
            how[t] = reason
        elif ev[0] == 'close':
            tr = ev[1]
            if how.get(int(tr['open']) * BAR_MS) == 'non-trading octo-sig':
                continue                                  # an open without a close - Joe 1002
            exp.setdefault(t, []).append(('close', side_of(tr['dr']), tr['closed_by']))
        elif ev[0] == 'inert':
            exp.setdefault(t, []).append(('open', side_of(ev[2]), 'non-trading octo-sig'))
    return exp


def run(live_start=None, out=REPORT):
    import bias_machine as bm
    from sweep_eval import BASE_BIAS
    from optimus9.config import get_db_config
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.compute import trade_config as TC
    from optimus9.live.octo_inputs import OctoConfig
    t0 = time.perf_counter()
    dev = DatabaseManager(**get_db_config()); dev.connect()
    c = get_db_config(); c['database'] = 'o9_live'
    o9 = DatabaseManager(**c); o9.connect()
    for d in DDL:
        o9.execute(d)
    cfg = OctoConfig(dev)
    live_start = int(live_start) if live_start is not None else live_start_from_log()
    book_start = live_start - PRE_START_MS
    last_bar = int(dev.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1',
                               fetch=True)[0]['m'])
    dump = [d for d in read_dump() if live_start <= int(d['bar_ms']) <= last_bar]
    gap = {int(d['bar_ms']): (int(d['wall_ms']) - int(d['bar_ms'])) >= LATE_OPEN_MS for d in dump}
    recs, inp, sha = reference(dev, cfg, bm.BiasConfig(**BASE_BIAS), book_start, last_bar)
    ts = inp.ts
    got = {}
    for d in dump:
        got.setdefault(int(d['bar_ms']), []).append((d['action'], d['side'], d['reason']))
    mism, matched = [], 0
    # A. SIGNALS - MVP1's core: every reference WALK FIRES FROM bar vs every bar with a live open line
    ref_sig = {r['ts'] for r in recs if r['fires'] and r['ts'] >= live_start}
    live_sig = {b for b, ls in got.items() if any(x[0] == 'open' for x in ls)}
    for b in sorted(ref_sig ^ live_sig):
        mism.append((b, 'selection', 'signal' if b in ref_sig else '-', 'signal' if b in live_sig else '-',
                     'WALK FIRES FROM on one side only'))
    # B. ACTIONS - the live dump vs the book o9-live should have run (empty at its first live bar)
    exp = expected_lines(live_shaped(recs, inp, cfg, live_start), gap)
    for b in sorted(set(exp) | set(got)):
        e, g = exp.get(b, []), got.get(b, [])
        if e == g:
            matched += len(e)
            continue
        cls = 'stop' if any(x[2] == 'stop' for x in e + g) else 'selection'
        mism.append((b, cls, json.dumps(e), json.dumps(g), 'action'))
    # C. PRE-START - Joe's 24-h-earlier trade list vs the live-start book, after the live start
    joes = expected_lines([(r['ts'], ev) for r in recs if r['ts'] >= live_start for ev in r['events']], gap)
    pre = [(b, 'Joe\'s 24-h-earlier list %s vs live-start book %s' % (joes.get(b, []), exp.get(b, [])))
           for b in sorted(set(joes) | set(exp)) if joes.get(b, []) != exp.get(b, [])]
    prev = o9.execute('SELECT MAX(run_id) r FROM octo_recon_run', fetch=True)[0]['r']
    rows = [(r['ts'], int(r['hit']), None if r['emitted'] is None else int(r['emitted']), int(r['fires']),
             None if r['arm'] is None else int(r['arm']) * BAR_MS, r['arm_dr'],
             json.dumps([[str(x) for x in ev[:1]] + [ev[1] if ev[0] == 'inert' else
                                                    {k: v for k, v in ev[1].items() if k != 'opened_by'}]
                         for ev in r['events']], default=str)[:255])
            for r in recs if r['hit'] or r['events']]
    moved = []
    if prev is not None:
        old = {int(x['bar_ms']): x for x in o9.execute(
            'SELECT * FROM octo_recon_verdict WHERE run_id=%s', (prev,), fetch=True)}
        new = {r[0]: r for r in rows}
        lo = max(min(old) if old else book_start, book_start)
        hi = max(old) if old else book_start
        for b in sorted(set(old) | set(new)):
            if not (lo <= b <= hi):
                continue
            o, n = old.get(b), new.get(b)
            ov = None if o is None else (int(o['hit']), o['emitted'], int(o['fires']), o['events'])
            nv = None if n is None else (n[1], n[2], n[3], n[6])
            if ov != nv:
                near = b > hi - 4 * BAR_MS           # the bar builder rewrites each bar for 3 cycles
                moved.append((b, 'causality', json.dumps(nv, default=str), json.dumps(ov, default=str),
                              'verdict moved since run %s%s' % (prev, ' - within 3 bars of that run\'s last '
                                                                 'bar, so a bar rewrite is possible' if near else '')))
    o9.execute('INSERT INTO octo_recon_run (run_ms, live_start, book_start, last_bar, cfg_key, tape_sha1, '
               'tape_bars, ref_fires, live_lines, matched, mismatched, pre_start, moved, secs) '
               'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
               (int(time.time() * 1000), live_start, book_start, last_bar, TC.key(cfg.walk), sha, len(ts),
                sum(1 for r in recs if r['fires'] and r['ts'] >= live_start), len(dump), matched,
                len(mism), len(pre), len(moved), round(time.perf_counter() - t0, 1)))
    run_id = o9.execute('SELECT MAX(run_id) r FROM octo_recon_run', fetch=True)[0]['r']
    if rows:
        o9.executemany('INSERT INTO octo_recon_verdict (run_id, bar_ms, hit, emitted, fires, arm_ms, arm_dr, '
                       'events) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', [(run_id,) + r for r in rows])
    for m in mism + moved:
        o9.execute('INSERT INTO octo_recon_mismatch (run_id, bar_ms, cls, ref, live, detail) '
                   'VALUES (%s,%s,%s,%s,%s,%s)', (run_id,) + tuple(str(x)[:255] for x in m))
    lines = ['RECON run %s | live start %s | book start %s | last bar %s | tape %s bars sha1 %s'
             % (run_id, _hms(live_start), _hms(book_start), _hms(last_bar), len(ts), sha[:12]),
             'RECON matched %d | mismatched %d | pre-start %d | moved since run %s: %d | cache: not measured '
             '(o9-live does not record its per-bar inputs) | %.0f s'
             % (matched, len(mism), len(pre), prev, len(moved), time.perf_counter() - t0)]
    for b, cls, e, g, _d in mism:
        lines.append('MISMATCH %s | %s | backtest %s | live %s' % (_hms(b), cls, e, g))
    for b, cls, nv, ov, d in moved:
        lines.append('MOVED %s | %s | now %s | before %s' % (_hms(b), d, nv, ov))
    for b, why in pre:
        lines.append('PRE-START %s | %s' % (_hms(b), why))
    with open(out, 'a') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('\n'.join(lines), flush=True)
    dev.disconnect(); o9.disconnect()
    return 0 if not mism and not moved else 1


def watch(live_start=None, poll_s=2.0):
    seen = len(read_dump())
    while True:
        n = len(read_dump())
        if n > seen:
            seen = n
            try:
                run(live_start)
            except Exception as e:                       # a failed job is a line in the report, not a dead monitor
                with open(REPORT, 'a') as fh:
                    fh.write('RECON ERROR %s | %s: %s\n' % (_hms(time.time() * 1000), type(e).__name__, e))
        time.sleep(poll_s)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--live-start', type=int, default=None)
    ap.add_argument('--watch', action='store_true')
    a = ap.parse_args(argv)
    if a.watch:
        return watch(a.live_start)
    return run(a.live_start)


if __name__ == '__main__':
    sys.exit(main())
