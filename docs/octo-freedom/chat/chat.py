"""chat — a message log shared by Joe and the Claude sessions working on octo-freedom.

ONE JOB: append messages to one file and read them back. It decides nothing, summarises nothing and
never rewrites a line. The log is `log.jsonl` beside this file, one JSON object per line, append-only
— the same shape as the o9-live trade-signal dump in `docs/o9-live-recon/RECON.md`, consumed the same
way: a session waits on the file and wakes when a line arrives.

    python3 chat.py say NAME "text"          # post. No text, or "-", reads stdin (for long messages)
    python3 chat.py show [--since N] [--last N]
    python3 chat.py wait NAME [--since N]    # block until someone OTHER than NAME posts, print it, exit
    python3 chat.py repl NAME                # interactive: type to post, others' messages print live

A CLAUDE SESSION WAKES ON `wait`. Run it as a background command; it exits when a message from
someone else lands, and the session is re-invoked with the message as the command's output. Pass
`--since` the last `#n` you have read so nothing that arrived in between is skipped.

`OCTO_CHAT_LOG` overrides the log path, so a test never writes the real log.
"""
import argparse
import datetime as dt
import fcntl
import json
import os
import sys
import threading
import time

LOG = os.environ.get('OCTO_CHAT_LOG',
                     os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log.jsonl'))
POLL_S = 1.0


def _read():
    """Every message in the log, in order. -> list of dicts."""
    if not os.path.exists(LOG):
        return []
    out = []
    with open(LOG) as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def post(name, text):
    """Append one message under an exclusive lock, so two writers cannot take the same number."""
    if not text.strip():
        raise SystemExit('chat: empty message, nothing posted')
    with open(LOG, 'a+') as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        n = sum(1 for line in fh if line.strip()) + 1
        msg = {'n': n, 'utc': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
               'from': name, 'text': text.rstrip('\n')}
        fh.write(json.dumps(msg) + '\n')
        fh.flush()
        os.fsync(fh.fileno())
        fcntl.flock(fh, fcntl.LOCK_UN)
    return msg


def fmt(m):
    body = '\n'.join('    ' + ln for ln in m['text'].splitlines()) or '    '
    return '#%d · %s UTC · %s\n%s\n' % (m['n'], m['utc'], m['from'], body)


def last_n():
    msgs = _read()
    return msgs[-1]['n'] if msgs else 0


def wait(name, since):
    """Block until a message numbered above `since` from someone other than `name`. -> those messages.

    No timeout: the caller owns how long to wait. Messages from `name` itself are skipped, not lost —
    they stay in the log and `show` prints them.
    """
    while True:
        new = [m for m in _read() if m['n'] > since and m['from'] != name]
        if new:
            return new
        time.sleep(POLL_S)


def repl(name):
    seen = last_n()
    for m in _read():
        sys.stdout.write(fmt(m))
    print('-- posting as %s. Type a line and press enter; /quit to leave. --' % name)
    lock = threading.Lock()

    def follow():
        nonlocal seen
        while True:
            new = [m for m in _read() if m['n'] > seen]
            if new:
                with lock:
                    for m in new:
                        if m['from'] != name:
                            sys.stdout.write('\n' + fmt(m))
                    seen = new[-1]['n']
                sys.stdout.flush()
            time.sleep(POLL_S)

    threading.Thread(target=follow, daemon=True).start()
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            break
        if line.strip() == '/quit':
            break
        if line.strip():
            post(name, line)


def main(argv=None):
    ap = argparse.ArgumentParser(description='shared chat log for octo-freedom sessions')
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('say'); s.add_argument('name'); s.add_argument('text', nargs='*')
    sh = sub.add_parser('show'); sh.add_argument('--since', type=int, default=0)
    sh.add_argument('--last', type=int, default=None)
    w = sub.add_parser('wait'); w.add_argument('name'); w.add_argument('--since', type=int, default=None)
    r = sub.add_parser('repl'); r.add_argument('name')
    a = ap.parse_args(argv)

    if a.cmd == 'say':
        text = ' '.join(a.text)
        if not a.text or text == '-':
            text = sys.stdin.read()
        m = post(a.name, text)
        print('posted #%d' % m['n'])
    elif a.cmd == 'show':
        msgs = [m for m in _read() if m['n'] > a.since]
        if a.last is not None:
            msgs = msgs[-a.last:]
        for m in msgs:
            sys.stdout.write(fmt(m))
    elif a.cmd == 'wait':
        since = last_n() if a.since is None else a.since
        for m in wait(a.name, since):
            sys.stdout.write(fmt(m))
    elif a.cmd == 'repl':
        repl(a.name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
