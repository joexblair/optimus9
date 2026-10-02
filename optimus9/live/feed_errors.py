"""feed_errors — the MVP1 errors log: tick, kline, fakeAPI and o9-live issues, one line each, for the recon.

Joe 1002: *"let's park the rewritten bars until MVP2. the critcal MVP1 task is recon - if we have tick
or kline issues in that time, then we have real data to make decsions on"*, then, asked whether that
also parks the blip-triggered reset: *"yes, create an errors log for fakeAPI and shell monitor the
log"*. So MVP1 RECORDS these issues and acts on none of them.

ONE JOB: copy what the existing machines already report into ONE append-only file. It changes none of
them - Joe 1002: *"I'd say the existing machines are enough. the kline_auditor.service is likely the
best source, but I would look at all 3"*.

    source          what is copied                                           from
    kline_audit     every verdict that is not 'live' (5 s) or 'match' (1 m):   the `kline_audit` table, by ka_pk
                    5 s 'frozen', 1 m 'variance' / 'incomplete', anything new
    klinecollect    WARNING / ERROR / CRITICAL lines, and the tick           `journalctl -u klinecollect.service`
                    collector's backfill lines (a reconnect)                  (TickCollector + BarBuilder)
    fakeapi         ERROR / Traceback / Exception lines                      the fakeAPI log file, when given
    o9live          ERROR / Traceback / Exception lines                      the o9-live log file, when given

One JSON line per issue: wall_ms, source, kind, detail, bar_ms (the bar it is about, or null).

    python3 -m optimus9.live.feed_errors run [--fakeapi-log P] [--o9live-log P]   # the watcher
    python3 -m optimus9.live.feed_errors wait --since N     # block until line N+1 exists, print it
    python3 -m optimus9.live.feed_errors show [--since N]
"""
import argparse
import json
import os
import subprocess
import sys
import threading
import time

PATH = os.environ.get('O9_ERRORS_LOG', '/home/joe/thecodes/o9live_errors.log')
SYMBOL = os.environ.get('O9_SYMBOL', 'FARTCOINUSDT')          # run_o9live.py's default
POLL_S = 5.0
_OK = ('live', 'match')
_LEVELS = ('WARNING', 'ERROR', 'CRITICAL')
_FILE_MARKS = ('ERROR', 'Traceback', 'Exception')
_lock = threading.Lock()


def write(source, kind, detail, bar_ms=None, path=PATH):
    line = json.dumps(dict(wall_ms=int(time.time() * 1000), source=source, kind=kind,
                           detail=str(detail)[:500], bar_ms=None if bar_ms is None else int(bar_ms)))
    with _lock, open(path, 'a') as fh:
        fh.write(line + '\n')
        fh.flush()
        os.fsync(fh.fileno())


def _audit_loop(path):
    sys.path.insert(0, '/home/joe/thecodes')
    from optimus9.config import get_db_config
    from optimus9.db.database_manager import DatabaseManager
    db = DatabaseManager(**get_db_config()); db.connect()
    tp = db.execute('SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s', (SYMBOL,),
                    fetch=True)[0]['tp_pk']
    last = db.execute('SELECT COALESCE(MAX(ka_pk), 0) m FROM kline_audit', fetch=True)[0]['m']
    while True:
        rows = db.execute('SELECT ka_pk, ka_tier, ka_verdict, ka_detail, ka_timestamp, ka_var_o, '
                          'ka_var_h, ka_var_l, ka_var_c FROM kline_audit WHERE ka_pk > %s AND '
                          'ka_tp_pk = %s ORDER BY ka_pk', (last, tp), fetch=True) or []
        for r in rows:
            last = max(last, int(r['ka_pk']))
            if r['ka_verdict'] in _OK:
                continue
            write('kline_audit', '%s %s' % (r['ka_tier'], r['ka_verdict']),
                  '%s | tick var o/h/l/c %s/%s/%s/%s' % (r['ka_detail'], r['ka_var_o'], r['ka_var_h'],
                                                         r['ka_var_l'], r['ka_var_c']),
                  r['ka_timestamp'], path)
        time.sleep(POLL_S)


def _journal_loop(path):
    p = subprocess.Popen(['journalctl', '-u', 'klinecollect.service', '-f', '-n', '0', '-o', 'cat'],
                         stdout=subprocess.PIPE, text=True, bufsize=1)
    for line in p.stdout:
        s = line.rstrip('\n')
        lvl = next((x for x in _LEVELS if (' %s ' % x) in s), None)
        if lvl is not None:
            write('klinecollect', lvl, s, None, path)
        elif 'backfill' in s:
            write('klinecollect', 'backfill', s, None, path)


def _file_loop(source, fpath, path):
    while not os.path.exists(fpath):
        time.sleep(POLL_S)
    with open(fpath) as fh:
        fh.seek(0, os.SEEK_END)                         # only what happens from now on
        while True:
            line = fh.readline()
            if not line:
                time.sleep(1.0)
                continue
            if any(m in line for m in _FILE_MARKS):
                write(source, 'error', line.rstrip('\n'), None, path)


def run(fakeapi_log=None, o9live_log=None, path=PATH):
    write('feed_errors', 'start', 'watching kline_audit (%s), klinecollect, fakeapi=%s, o9live=%s'
          % (SYMBOL, fakeapi_log, o9live_log), None, path)
    ts = [threading.Thread(target=_audit_loop, args=(path,), daemon=True),
          threading.Thread(target=_journal_loop, args=(path,), daemon=True)]
    if fakeapi_log:
        ts.append(threading.Thread(target=_file_loop, args=('fakeapi', fakeapi_log, path), daemon=True))
    if o9live_log:
        ts.append(threading.Thread(target=_file_loop, args=('o9live', o9live_log, path), daemon=True))
    for t in ts:
        t.start()
    while all(t.is_alive() for t in ts):
        time.sleep(POLL_S)
    write('feed_errors', 'stopped', 'a watcher thread died: %s'
          % [t.name for t in ts if not t.is_alive()], None, path)
    return 1


def _lines(path=PATH):
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [x for x in fh.read().splitlines() if x.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run'); r.add_argument('--fakeapi-log'); r.add_argument('--o9live-log')
    w = sub.add_parser('wait'); w.add_argument('--since', type=int, default=None)
    s = sub.add_parser('show'); s.add_argument('--since', type=int, default=0)
    a = ap.parse_args(argv)
    if a.cmd == 'run':
        return run(a.fakeapi_log, a.o9live_log)
    if a.cmd == 'show':
        for i, x in enumerate(_lines()[a.since:], a.since + 1):
            print('#%d %s' % (i, x))
        return 0
    since = len(_lines()) if a.since is None else a.since
    while len(_lines()) <= since:
        time.sleep(1.0)
    for i, x in enumerate(_lines()[since:], since + 1):
        print('#%d %s' % (i, x))
    return 0


if __name__ == '__main__':
    sys.exit(main())
