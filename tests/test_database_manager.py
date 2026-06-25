"""DatabaseManager L1 self-healing — reconnect on connection-loss, fail-fast on SQL errors."""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import mysql.connector
from optimus9.db.database_manager import DatabaseManager


class _FakeCursor:
    def __init__(self, conn): self._conn = conn
    def execute(self, sql, params=()): self._conn._exec(sql)
    def fetchall(self): return [{'ok': 1}]
    def close(self): pass
    @property
    def lastrowid(self): return 7


class _FakeConn:
    """Dies on first execute, succeeds after a reconnect (new _FakeConn)."""
    def __init__(self, alive=True, die_once=False):
        self.alive = alive; self.die_once = die_once; self.closed = False
    def cursor(self, dictionary=False): return _FakeCursor(self)
    def _exec(self, sql):
        if self.die_once:
            self.die_once = False
            raise mysql.connector.errors.InterfaceError('MySQL Connection not available.')
        if 'BADSQL' in sql:
            raise mysql.connector.errors.ProgrammingError('1064 syntax error')
    def is_connected(self): return self.alive and not self.closed
    def close(self): self.closed = True


def _mgr(conns):
    """DatabaseManager whose _open pops the next conn from `conns`."""
    m = DatabaseManager(host='x', user='x', password='x', database='x')
    def fake_open(first=False): m._conn = conns.pop(0)
    m._open = fake_open
    return m


def test_reconnects_and_retries_on_connection_loss():
    # conn 1 dies once on execute; reconnect yields a healthy conn 2 → op succeeds
    m = _mgr([_FakeConn(die_once=True), _FakeConn()])
    m.connect()
    assert m.execute('SELECT 1', fetch=True) == [{'ok': 1}]   # retried after reconnect


def test_sql_error_fails_fast_no_retry():
    # a ProgrammingError must propagate, NOT trigger reconnect
    conn = _FakeConn()
    m = _mgr([conn])
    m.connect()
    reconnected = {'n': 0}
    orig = m._reconnect
    m._reconnect = lambda *a, **k: (reconnected.__setitem__('n', reconnected['n'] + 1), orig(*a, **k))
    try:
        m.execute('BADSQL')
        assert False, 'expected ProgrammingError'
    except mysql.connector.errors.ProgrammingError:
        pass
    assert reconnected['n'] == 0, 'SQL error must not reconnect'


if __name__ == '__main__':
    test_reconnects_and_retries_on_connection_loss()
    test_sql_error_fails_fast_no_retry()
    print('ok')
