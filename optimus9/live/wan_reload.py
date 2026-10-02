"""wan_reload — the second rung after the socket auto-restart: reload pfSense's WAN when a socket restart
does not bring trades back within 50 s. Every episode is recorded, because the record IS the diagnosis.

Joe 1002: *"if the websocket reset makes no diff for another 50s, then restart the wan connection"*; how:
*"SSH, one command"*; guard: *"Trades only, no limit. the reason why is something you'll want to bank: if
the tick flow begins everytime the int is reset, then we have infra issues to troubleshoot"*.

THE RULE, per episode:
    starts   the first `stall-restart` event either tick socket writes (the client's 60 s auto-restart)
    resolved trades arrive on ANY socket within 50 s of that restart - the socket restart was enough
    reload   none did -> ssh to pfSense with the reload key, whose forced command is
             `/usr/local/sbin/pfSctl -c 'interface reload wan'`; no limit on how often
    after    the seconds until the first trade after the reload are recorded - Joe's infra signal

Reads `ws_liveness_collector.log` / `ws_liveness_collector2.log` (one line per socket per second, plus
events). Writes `o9_live.diag_wan_reload` and one errors-log line per reload (the /rc alert feed).

    python3 -m optimus9.live.wan_reload
"""
import json
import os
import subprocess
import sys
import time

LOGS = [p for p in os.environ.get('O9_WAN_RELOAD_LOGS', '/home/joe/thecodes/ws_liveness_collector.log,'
                                  '/home/joe/thecodes/ws_liveness_collector2.log').split(',') if p]
AFTER_RESTART_S = 50.0                     # Joe 1002: "for another 50s"
SSH_TARGET = os.environ.get('O9_PFSENSE_SSH', 'admin@192.168.1.1')
SSH_KEY = os.path.expanduser(os.environ.get('O9_PFSENSE_SSH_KEY', '~/.ssh/pfsense_wan_reload'))

DDL = """CREATE TABLE IF NOT EXISTS diag_wan_reload (
    wr_pk          INT AUTO_INCREMENT PRIMARY KEY,
    last_trade_ms  BIGINT NULL,
    restart_ms     BIGINT NOT NULL,
    outcome        VARCHAR(24) NOT NULL,
    decided_ms     BIGINT NOT NULL,
    ssh_rc         INT NULL,
    ssh_out        VARCHAR(255) NULL,
    first_trade_ms BIGINT NULL,
    recovery_s     DOUBLE NULL
)"""


class Episodes:
    """The rule as a state machine over liveness rows. `feed(row)` then `tick(now_ms)` -> actions."""

    def __init__(self, after_s=AFTER_RESTART_S):
        self.after_ms = int(after_s * 1000)
        self.last_trade_ms = None
        self.open = None                   # dict(restart_ms, last_trade_ms) while an episode is undecided
        self.waiting = None                # dict(...) after a reload, until the first trade

    def feed(self, row):
        out = []
        if row.get('ev') == 'stall-restart' and self.open is None and self.waiting is None:
            self.open = dict(restart_ms=int(row['t_ms']), last_trade_ms=self.last_trade_ms)
        elif row.get('trades'):
            t = int(row['t_ms'])
            self.last_trade_ms = max(self.last_trade_ms or 0, t)
            if self.open is not None and t >= self.open['restart_ms']:
                out.append(('resolved', dict(self.open, first_trade_ms=t)))
                self.open = None
            if self.waiting is not None and t >= self.waiting['decided_ms']:
                w = self.waiting
                out.append(('recovered', dict(w, first_trade_ms=t,
                                              recovery_s=round((t - w['decided_ms']) / 1000.0, 1))))
                self.waiting = None
        return out

    def tick(self, now_ms):
        if self.open is not None and now_ms - self.open['restart_ms'] >= self.after_ms:
            ep = dict(self.open, decided_ms=int(now_ms))
            self.open = None
            self.waiting = ep
            return [('reload', ep)]
        return []


class Follow:
    def __init__(self, path):
        self.path, self.buf = path, ''
        self.pos = os.path.getsize(path) if os.path.exists(path) else 0

    def rows(self):
        if not os.path.exists(self.path):
            return []
        if os.path.getsize(self.path) < self.pos:
            self.pos = 0
        with open(self.path) as fh:
            fh.seek(self.pos)
            data = fh.read()
            self.pos = fh.tell()
        self.buf += data
        *done, self.buf = self.buf.split('\n')
        out = []
        for d in done:
            try:
                out.append(json.loads(d))
            except ValueError:
                pass
        return out


def reload_wan():
    """-> (returncode, output). The key's forced command on pfSense IS the reload; nothing else can run."""
    p = subprocess.run(['ssh', '-i', SSH_KEY, '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5',
                        '-o', 'StrictHostKeyChecking=accept-new', SSH_TARGET, 'reload'],
                       capture_output=True, text=True, timeout=60)
    return p.returncode, (p.stdout + p.stderr).strip()[:255]


def main():
    from optimus9.config import get_db_config
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.live.feed_errors import write
    c = get_db_config(); c['database'] = 'o9_live'
    db = DatabaseManager(**c); db.connect()
    db.execute(DDL)
    eps, fol = Episodes(), [Follow(p) for p in LOGS]
    print('wan_reload: watching %s; reload after %.0f s with no trades past a socket restart -> %s'
          % (', '.join(LOGS), AFTER_RESTART_S, SSH_TARGET), flush=True)

    def bank(kind, ep, rc=None, out=None):
        db.execute('INSERT INTO diag_wan_reload (last_trade_ms, restart_ms, outcome, decided_ms, ssh_rc, ssh_out, '
                   'first_trade_ms, recovery_s) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                   (ep.get('last_trade_ms'), ep['restart_ms'], kind, ep.get('decided_ms', int(time.time() * 1000)),
                    rc, out, ep.get('first_trade_ms'), ep.get('recovery_s')))

    while True:
        acts = []
        for f in fol:
            for r in f.rows():
                acts += eps.feed(r)
        acts += eps.tick(int(time.time() * 1000))
        for kind, ep in acts:
            if kind == 'resolved':
                bank('socket restart enough', ep)
            elif kind == 'reload':
                rc, out = reload_wan()
                ep['ssh_rc'] = rc
                bank('wan reloaded' if rc == 0 else 'wan reload failed', ep, rc, out)
                write('wan_reload', 'WAN reloaded' if rc == 0 else 'WAN reload FAILED',
                      'no trades %.0f s after the socket restart; ssh rc %s %s' % (AFTER_RESTART_S, rc, out))
            elif kind == 'recovered':
                bank('trades back after reload', ep)
                write('wan_reload', 'trades back after WAN reload', '%.1f s after the reload' % ep['recovery_s'])
        time.sleep(1.0)


if __name__ == '__main__':
    sys.exit(main())
