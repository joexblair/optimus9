"""The websocket client's auto-restart (Joe 1002), against a local server that goes SILENT but keeps the
connection open - the shape of the 1002 22:06 outage: no error, pings sent, nothing received.

S1  a socket with no topic message for stall_s is aborted and reconnected; on_connect(True) on the reconnect
S2  ping replies do NOT count as liveness (they arrived on 22:06's dead sockets' last connection too)
S3  two sockets sharing a RestartGate never restart within its offset of each other
S4  with stall_s None the client never restarts (fakeAPI tests, the default)
"""
import asyncio
import json
import sys
import threading
import time

sys.path.insert(0, '/home/joe/thecodes')
import websockets  # noqa: E402

from optimus9.data.bybit_websocket_client import BybitWebSocketClient, RestartGate  # noqa: E402


class SilentServer:
    """Sends `n_topic` topic messages per connection, answers pings if `pong`, then stays silent."""

    def __init__(self, n_topic=2, pong=False):
        self.n_topic, self.pong = n_topic, pong
        self.connects = []
        self.loop = asyncio.new_event_loop()
        self.port = None
        ready = threading.Event()
        threading.Thread(target=self._run, args=(ready,), daemon=True).start()
        ready.wait(5)

    async def _handler(self, ws):
        self.connects.append(time.monotonic())
        await ws.recv()                                             # the subscribe
        for i in range(self.n_topic):
            await ws.send(json.dumps({'topic': 'publicTrade.X', 'data': [{'T': i, 'p': '1', 'v': '1'}]}))
        try:
            async for raw in ws:
                if self.pong and json.loads(raw).get('op') == 'ping':
                    await ws.send(json.dumps({'op': 'ping', 'ret_msg': 'pong', 'success': True}))
        except websockets.ConnectionClosed:
            pass

    def _run(self, ready):
        asyncio.set_event_loop(self.loop)

        async def main():
            srv = await websockets.serve(self._handler, '127.0.0.1', 0)
            self.port = srv.sockets[0].getsockname()[1]
            ready.set()
            await asyncio.Future()
        self.loop.run_until_complete(main())


def _client(url, **kw):
    c = BybitWebSocketClient(url=url, **kw)
    threading.Thread(target=c.stream, args=('publicTrade.X', lambda m: None), daemon=True).start()
    return c


def test_s1_stall_aborts_and_reconnects_with_on_connect():
    srv = SilentServer()
    calls = []
    _client('ws://127.0.0.1:%d' % srv.port, stall_s=2, on_connect=calls.append)
    time.sleep(7.5)
    assert len(srv.connects) >= 3, srv.connects               # connect at 0, restart ~3 s, ~6 s
    gaps = [b - a for a, b in zip(srv.connects, srv.connects[1:])]
    assert all(2.0 <= g <= 4.5 for g in gaps), gaps            # stall 2 s + the 1 s watchdog tick
    assert calls[0] is False and all(c is True for c in calls[1:]), calls


def test_s2_ping_replies_do_not_count():
    srv = SilentServer(pong=True)
    c = _client('ws://127.0.0.1:%d' % srv.port, stall_s=2)
    c._PING_INTERVAL_S = 0.5                                  # replies every 0.5 s, still no topic message
    time.sleep(5.5)
    assert len(srv.connects) >= 2, srv.connects


def test_s3_gate_staggers_parallel_sockets():
    srv = SilentServer()
    gate = RestartGate(offset_s=3.0)
    _client('ws://127.0.0.1:%d/a' % srv.port, stall_s=2, restart_gate=gate)
    _client('ws://127.0.0.1:%d/b' % srv.port, stall_s=2, restart_gate=gate)
    time.sleep(9.0)
    later = sorted(srv.connects[2:])                           # the first two are the initial connects
    assert len(later) >= 2, srv.connects
    gaps = [b - a for a, b in zip(later, later[1:])]
    assert all(g >= 2.9 for g in gaps), gaps                   # never two restarts inside the 3 s offset


def test_s4_no_stall_s_never_restarts():
    srv = SilentServer()
    _client('ws://127.0.0.1:%d' % srv.port)
    time.sleep(4.0)
    assert len(srv.connects) == 1, srv.connects
