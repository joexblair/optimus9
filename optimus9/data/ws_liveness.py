"""ws_liveness — what one Bybit websocket connection received, second by second. RECORDS ONLY.

Joe 1002: *"no auto reconnect yet. bake all of your ideas and get them collecting inputs"* - item #1 of
the outage list. The 1002 05:08:30 outage: the collector's socket delivered nothing for 16 min, and
nothing noticed until a send failed at 05:24:35, because nothing checks that messages keep arriving
(`bybit_websocket_client.py`: pings are sent every 20 s, no reply is ever checked, and the library's
own keepalive is off). This module watches; it decides nothing and reconnects nothing.

ONE LINE PER SECOND, written by its own thread, so a silent socket still produces lines (msgs 0) and a
missing line means the recorder itself stopped:

    t_ms           the second's start (wall clock)
    label          which connection ('collector', 'witness')
    msgs           websocket messages received in that second
    trades         trades inside the topic messages
    last_msg_age   ms since the last message of any kind, at the end of the second
    last_trade_T   Bybit's own timestamp `T` of the newest trade received so far
    pings          our {"op":"ping"} sends in that second
    replies        Bybit's ping replies ({"op":"ping","ret_msg":"pong"}) in that second
    rtt_ms         round trip of the newest reply, ms
    pong_err       Bybit's {"op":"pong","success":false} answers to the client's own pong reply (the
                   1002 Bybit check's I15 / M4: Bybit rejects it every 20 s). Counted, not fixed

EVENT LINES (`ev`): connect, subscribed (the ack and its success flag), error (the reconnect message),
stall-restart (the client's auto-restart fired),
other (any op message that is none of the above, first 200 chars).
"""
import json
import threading
import time


class WsLiveness:
    def __init__(self, path, label):
        self.path = path
        self.label = label
        self._lock = threading.Lock()
        self._msgs = self._trades = self._pings = self._replies = self._pong_err = 0
        self._rtt = None
        self._last_msg = None
        self._last_T = None
        self._ping_at = None
        th = threading.Thread(target=self._tick, daemon=True, name='ws_liveness_' + label)
        th.start()

    # --- called from the websocket loop -----------------------------------------------------
    def connected(self, url):
        self._event('connect', url)

    def error(self, text):
        self._event('error', text)

    def stalled(self, idle_s):
        self._event('stall-restart', 'no topic message for %.0f s - socket aborted, reconnecting' % idle_s)

    def ping_sent(self):
        with self._lock:
            self._pings += 1
            self._ping_at = time.time()

    def message(self, msg):
        now = time.time()
        with self._lock:
            self._msgs += 1
            self._last_msg = now
            if 'topic' in msg:
                d = msg.get('data')
                d = d if isinstance(d, list) else []    # a trade topic carries a list; a book topic a dict
                self._trades += len(d)
                ts = [x.get('T') for x in d if isinstance(x, dict) and x.get('T')]
                if ts:
                    self._last_T = max(ts)
                return
            op, ret = msg.get('op'), msg.get('ret_msg')
            if op == 'ping' and ret == 'pong':
                self._replies += 1
                if self._ping_at is not None:
                    self._rtt = round((now - self._ping_at) * 1000.0, 1)
                return
            if op == 'pong' and msg.get('success') is False:
                self._pong_err += 1
                return
        if msg.get('op') == 'subscribe':
            self._event('subscribed', json.dumps(msg)[:200])
        else:
            self._event('other', json.dumps(msg)[:200])

    # --- the per-second writer --------------------------------------------------------------
    def _tick(self):
        nxt = int(time.time()) + 1
        while True:
            time.sleep(max(0.0, nxt - time.time()))
            now = time.time()
            with self._lock:
                row = dict(t_ms=(nxt - 1) * 1000, label=self.label, msgs=self._msgs, trades=self._trades,
                           last_msg_age=None if self._last_msg is None else int((now - self._last_msg) * 1000),
                           last_trade_T=self._last_T, pings=self._pings, replies=self._replies, rtt_ms=self._rtt,
                           pong_err=self._pong_err)
                self._msgs = self._trades = self._pings = self._replies = self._pong_err = 0
            self._write(row)
            nxt += 1

    def _event(self, ev, detail):
        self._write(dict(t_ms=int(time.time() * 1000), label=self.label, ev=ev, detail=str(detail)[:300]))

    def _write(self, row):
        try:
            with open(self.path, 'a') as fh:
                fh.write(json.dumps(row) + '\n')
        except OSError:
            pass                                    # recording must never break the socket it watches
