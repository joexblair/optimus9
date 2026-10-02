"""rc_alerts — the alert lines that go to Joe's device through the /rc channel (Remote Control).

Joe 1002: *"for #3, send to the /rc channel so I see it on my device"*. A Claude session runs this under
its shell Monitor; every line printed here is one event the session pushes to Joe's device.

ONE JOB: follow the files that already record problems and print one short line per problem. It
writes nothing and judges nothing - what counts as a problem is the writer's definition:

    o9live_errors.log    every line (feed_errors: kline_audit non-live/match verdicts, collector
                         journal warnings and errors, fakeAPI / o9-live errors, diag alarms)
    pfsense_alerts.log   posts to /alert (pfSense: ping 1.1.1.1 no reply). Other paths are records
                         (e.g. /gateway status every minute), not alerts

REPEATS. The 1002 outage wrote a `5s frozen` line every 5 s for 17 min (202 lines). The first line of
each (source, kind) prints at once; while the same (source, kind) keeps arriving, ONE line per
`REPEAT_S` prints with the count since the last print. Every line stays in the source files.

    python3 -m optimus9.live.rc_alerts            # resumes where the last run stopped (STATE)

A shell Monitor lasts at most 30 min, so the feed is re-armed again and again. Each run saves its read
positions to STATE and the next run starts there, so a line written between two runs is not skipped.
"""
import json
import os
import sys
import time

ERRORS = os.environ.get('O9_ERRORS_LOG', '/home/joe/thecodes/o9live_errors.log')
PFSENSE = os.environ.get('PFSENSE_ALERTS_LOG', '/home/joe/thecodes/pfsense_alerts.log')
STATE = os.environ.get('O9_RC_ALERTS_STATE', '/home/joe/thecodes/rc_alerts.state.json')
REPEAT_S = 60.0                     # one summary line per minute while one (source, kind) repeats
POLL_S = 0.5


class Follow:
    """New complete lines of one file, from its end at start. A file that shrinks is re-read from 0."""

    def __init__(self, path, pos=None):
        self.path = path
        end = os.path.getsize(path) if os.path.exists(path) else 0
        self.pos = end if pos is None or pos > end else int(pos)
        self.buf = ''

    def lines(self):
        if not os.path.exists(self.path):
            return []
        size = os.path.getsize(self.path)
        if size < self.pos:
            self.pos = 0
        if size == self.pos:
            return []
        with open(self.path) as fh:
            fh.seek(self.pos)
            data = fh.read()
            self.pos = fh.tell()
        self.buf += data
        *done, self.buf = self.buf.split('\n')
        return [d for d in done if d.strip()]


def _hms(ms):
    return time.strftime('%H:%M:%S', time.gmtime(ms / 1000.0)) if ms else '-'


def main():
    try:
        with open(STATE) as fh:
            st = json.load(fh)
    except (OSError, ValueError):
        st = {}
    fe, fp = Follow(ERRORS, st.get(ERRORS)), Follow(PFSENSE, st.get(PFSENSE))
    seen = {}                       # (source, kind) -> [last print time, count since]
    print('rc_alerts following %s and %s' % (ERRORS, PFSENSE), flush=True)
    while True:
        now = time.time()
        for line in fe.lines():
            try:
                r = json.loads(line)
            except ValueError:
                print('ALERT errors-log unparsed: %s' % line[:160], flush=True)
                continue
            key = (r.get('source'), r.get('kind'))
            s = seen.get(key)
            if s is None or now - s[0] >= REPEAT_S:
                extra = ' (+%d more since %s)' % (s[1], time.strftime('%H:%M:%S', time.gmtime(s[0]))) \
                    if s and s[1] else ''
                print('ALERT %s %s | bar %s | %s%s' % (key[0], key[1], _hms(r.get('bar_ms')),
                                                      str(r.get('detail'))[:110], extra), flush=True)
                seen[key] = [now, 0]
            else:
                s[1] += 1
        for line in fp.lines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get('path', '').startswith('/alert'):
                print('ALERT pfsense %s | %s' % (r.get('received_utc'), str(r.get('body'))[:140]), flush=True)
        for key, s in seen.items():
            if s[1] and now - s[0] >= REPEAT_S:
                print('ALERT %s %s still repeating: %d more in the last %ds' % (key[0], key[1], s[1],
                                                                               int(now - s[0])), flush=True)
                s[0], s[1] = now, 0
        try:
            with open(STATE, 'w') as fh:
                json.dump({ERRORS: fe.pos - len(fe.buf), PFSENSE: fp.pos - len(fp.buf)}, fh)
        except OSError:
            pass
        time.sleep(POLL_S)


if __name__ == '__main__':
    sys.exit(main())
