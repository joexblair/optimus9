"""net_probe — the network path from WSL, probed every few seconds, so the next outage says which hop failed.

Joe 1002: *"bake all of your ideas and get them collecting inputs"* - item #4 of the outage list.
The 1002 05:08:30 outage left no record of whether the LAN, the WAN, DNS or Bybit's endpoint failed.

ONE JOB: probe and record. It changes nothing on the box and reconnects nothing.

    target                kind   what a failure isolates
    192.168.1.1           ping   pfSense LAN: WSL -> Windows NAT -> LAN
    1.1.1.1               ping   the internet past pfSense (the same address pfSense's cron pings)
    stream.bybit.com      dns    name resolution of the collector's websocket host
    stream.bybit.com:443  tcp    a TCP connect to the collector's websocket host
    stream.bytick.com:443 tcp    the same for Bybit's mirror host (the witness socket's host)
    api.bybit.com:443     tcp    the REST host kline_audit and the gap-fill read

Every probe of every round is one row in `o9_live.diag_net_probe`. A target whose result flips
(ok -> fail or fail -> ok) also writes one line to the errors log, which the /rc alert feed follows.
Timeouts: ping 1 s, DNS 4 s, TCP 3 s. Round every `EVERY_S` seconds.

    python3 -m optimus9.live.net_probe
"""
import re
import socket
import subprocess
import sys
import threading
import time

EVERY_S = 5.0
PING_W_S = 1
DNS_S = 4.0
TCP_S = 3.0
PROBES = [('192.168.1.1', 'ping'), ('1.1.1.1', 'ping'), ('stream.bybit.com', 'dns'),
          ('stream.bybit.com:443', 'tcp'), ('stream.bytick.com:443', 'tcp'), ('api.bybit.com:443', 'tcp')]

DDL = """CREATE TABLE IF NOT EXISTS diag_net_probe (
    np_pk      BIGINT AUTO_INCREMENT PRIMARY KEY,
    np_round_ms BIGINT NOT NULL,
    np_target  VARCHAR(64) NOT NULL,
    np_kind    VARCHAR(8) NOT NULL,
    np_ok      TINYINT NOT NULL,
    np_ms      DOUBLE NULL,
    np_err     VARCHAR(200) NULL,
    KEY k_round (np_round_ms), KEY k_target (np_target, np_round_ms)
)"""


def probe_ping(host):
    t = time.monotonic()
    p = subprocess.run(['ping', '-c', '1', '-W', str(PING_W_S), '-n', host], capture_output=True, text=True)
    m = re.search(r'time=([\d.]+) ms', p.stdout)
    if p.returncode == 0 and m:
        return True, float(m.group(1)), None
    return False, (time.monotonic() - t) * 1000, 'no reply (exit %d)' % p.returncode


def probe_dns(host):
    out = {}

    def go():
        t = time.monotonic()
        try:
            socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
            out['r'] = (True, (time.monotonic() - t) * 1000, None)
        except OSError as e:
            out['r'] = (False, (time.monotonic() - t) * 1000, str(e)[:200])
    th = threading.Thread(target=go, daemon=True)
    th.start(); th.join(DNS_S)
    return out.get('r', (False, DNS_S * 1000, 'timeout %.0f s' % DNS_S))


def probe_tcp(hostport):
    host, port = hostport.rsplit(':', 1)
    t = time.monotonic()
    try:
        with socket.create_connection((host, int(port)), timeout=TCP_S):
            return True, (time.monotonic() - t) * 1000, None
    except OSError as e:
        return False, (time.monotonic() - t) * 1000, str(e)[:200]


_FN = dict(ping=probe_ping, dns=probe_dns, tcp=probe_tcp)


def one_round():
    res = {}

    def go(tg, kind):
        try:
            res[(tg, kind)] = _FN[kind](tg)
        except Exception as e:                                  # a probe must never stop the loop
            res[(tg, kind)] = (False, None, 'probe error: %s' % str(e)[:180])
    ths = [threading.Thread(target=go, args=p, daemon=True) for p in PROBES]
    for th in ths:
        th.start()
    for th in ths:
        th.join(DNS_S + 1)
    return res


def main():
    from optimus9.config import get_db_config
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.live.feed_errors import write
    c = get_db_config(); c['database'] = 'o9_live'
    db = DatabaseManager(**c); db.connect()
    db.execute(DDL)
    state = {}
    print('net_probe: %d probes every %.0f s -> o9_live.diag_net_probe' % (len(PROBES), EVERY_S), flush=True)
    nxt = time.time()
    while True:
        rnd = int(nxt * 1000)
        res = one_round()
        rows = []
        for (tg, kind) in PROBES:
            ok, ms, err = res.get((tg, kind), (False, None, 'no result'))
            rows.append((rnd, tg, kind, int(ok), ms, err))
            if state.get((tg, kind)) is not None and state[(tg, kind)] != ok:
                write('net_probe', '%s %s %s' % (kind, tg, 'RECOVERED' if ok else 'FAILED'),
                      err or ('%.1f ms' % ms if ms is not None else ''))
            state[(tg, kind)] = ok
        try:
            for r in rows:
                db.execute('INSERT INTO diag_net_probe (np_round_ms, np_target, np_kind, np_ok, np_ms, np_err) '
                           'VALUES (%s, %s, %s, %s, %s, %s)', r)
        except Exception as e:
            write('net_probe', 'db write failed', str(e)[:300])
        nxt += EVERY_S
        time.sleep(max(0.0, nxt - time.time()))


if __name__ == '__main__':
    sys.exit(main())
