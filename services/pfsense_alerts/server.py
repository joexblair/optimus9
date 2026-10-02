"""pfsense_alerts — a webservice pfSense posts alerts to. Each request is one JSON line in the alerts log.

Joe 1002: *"build a webservice (as a service) on this box that pfsense can send alerts to ... you'll see
the alert via a shell monitor"* and *"pfsense is a seperate box, and this OS is wsl. we'll need to expose
the webservice via my windows box"*.

ONE JOB: receive and record. It judges nothing and forwards nothing; the shell monitor reads the log.

    POST <any path>   the body is recorded as text, with the path and the client address -> 200 "ok"
    GET  /health      -> 200 "ok", records nothing

THE PATH IN. pfSense -> Windows 192.168.1.48:8097 (netsh portproxy + a firewall rule allowing only
pfSense) -> WSL 172.22.243.167:8097 -> this server. So `client` is the Windows host's WSL-side address
(172.22.240.1), never pfSense's own; the Windows firewall rule is what limits who can post.

One line per alert in ALERTS (JSON): received_utc, wall_ms, client, path, body.
"""
import datetime as dt
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.environ.get('PFSENSE_ALERTS_HOST', '0.0.0.0')
PORT = int(os.environ.get('PFSENSE_ALERTS_PORT', '8097'))
ALERTS = os.environ.get('PFSENSE_ALERTS_LOG', '/home/joe/thecodes/pfsense_alerts.log')
MAX_BODY = 65536                    # bytes read from one request; an alert is one short line
_lock = threading.Lock()


def record(client, path, body):
    """Append one alert line. -> the dict written."""
    now = dt.datetime.now(dt.timezone.utc)
    row = dict(received_utc=now.strftime('%Y-%m-%d %H:%M:%S'), wall_ms=int(now.timestamp() * 1000),
               client=client, path=path, body=body)
    with _lock, open(ALERTS, 'a') as fh:
        fh.write(json.dumps(row) + '\n')
    return row


class Handler(BaseHTTPRequestHandler):
    server_version = 'pfsense-alerts/1'

    def _reply(self, code, text):
        data = (text + '\n').encode()
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._reply(200 if self.path == '/health' else 404, 'ok' if self.path == '/health' else 'not found')

    def do_POST(self):
        n = min(int(self.headers.get('Content-Length') or 0), MAX_BODY)
        body = self.rfile.read(n).decode('utf-8', 'replace').strip() if n > 0 else ''
        row = record(self.client_address[0], self.path, body)
        print('ALERT %s %s %s' % (row['received_utc'], row['path'], row['body']), flush=True)
        self._reply(200, 'ok')

    def log_message(self, fmt, *args):
        pass                        # one ALERT line per post is the log; skip the per-request access line


def main():
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print('pfsense-alerts listening on %s:%d, writing %s' % (HOST, PORT, ALERTS), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
