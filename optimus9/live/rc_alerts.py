"""rc_alerts — the alert lines that go to Joe's device through the /rc channel (Remote Control).

Joe 1002: *"for #3, send to the /rc channel so I see it on my device"*. A Claude session runs this under
its shell Monitor; every line printed here is one event the session pushes to Joe's device.

ONE JOB: follow the files that already record problems and print one short line per problem. It
writes nothing and judges nothing - what counts as a problem is the writer's definition:

    o9live_errors.log    every line (feed_errors: kline_audit non-live/match verdicts, collector
                         journal warnings and errors, fakeAPI / o9-live errors, diag alarms)
    pfsense_alerts.log   posts to /alert (pfSense: ping 1.1.1.1 no reply). Other paths are records
                         (e.g. /gateway status every minute), not alerts

5 s FROZEN, Joe 1002: *"5s frozen alert doen't need to be so twitchy now"*. Every verdict is still in the
errors log; the ALERT prints only when `FROZEN_RUN_BARS` consecutive bars are frozen - 12 bars = 60 s, the
tick sockets' auto-restart threshold, so it means a freeze the restart did not clear. Since 09-25: 40
single frozen bars, one 3-bar run, one 201-bar run (05:08) - only the last reaches 12.

1m INCOMPLETE FROM THE API THROTTLE, Joe 1007: *"instead of firing on the api throttle event, fire on the
api throttle event + any downstream issue"*. A `1m incomplete` line whose own tape and official bar are
complete (`kc=12/12 official=True`) is a gap on the auditor's REST side only - Bybit's 10006 replies in the
first seconds of a minute (accepted, `docs/o9-live-recon/OPEN.md` 1007). That line alone no longer alerts.
It alerts, as ONE line naming both, when any other kline_audit verdict lands on a bar inside the same
minute - before or after it. A `1m incomplete` with our tape or the official bar short alerts as before.

REPEATS. The 1002 outage wrote a `5s frozen` line every 5 s for 17 min (202 lines). The first line of
each (source, kind) prints at once; while the same (source, kind) keeps arriving, ONE line per
`REPEAT_S` prints with the count since the last print. Every line stays in the source files.

    python3 -m optimus9.live.rc_alerts            # resumes where the last run stopped (STATE)

A shell Monitor lasts at most 30 min, so the feed is re-armed again and again. Each run saves its read
positions to STATE and the next run starts there, so a line written between two runs is not skipped.
"""
import json
import os
import re
import sys
import time

ERRORS = os.environ.get('O9_ERRORS_LOG', '/home/joe/thecodes/o9live_errors.log')
PFSENSE = os.environ.get('PFSENSE_ALERTS_LOG', '/home/joe/thecodes/pfsense_alerts.log')
STATE = os.environ.get('O9_RC_ALERTS_STATE', '/home/joe/thecodes/rc_alerts.state.json')
REPEAT_S = 60.0                     # one summary line per minute while one (source, kind) repeats
FROZEN_RUN_BARS = 12                # 60 s of consecutive 5 s frozen bars before the alert (Joe 1002)
POLL_S = 0.5
_INCOMPLETE = re.compile(r'audit=(\d+)/(\d+) kc=(\d+)/(\d+) official=(True|False)')
MINUTE_MS = 60_000


class ThrottleGate:
    """The 1m-incomplete rule (Joe 1007). feed() takes every errors-log record and returns
    (alert, detail): alert False = stay silent; True = print, with detail replacing the record's own.

    A throttle-only minute is one whose `1m incomplete` line shows kc and official complete. Every other
    kline_audit verdict is remembered by the minute its bar falls in, so a downstream verdict that
    arrived first (5 s verdicts land during the minute, the 1m line ~80 s after it starts) still pairs.
    Memory keeps the minutes within KEEP_MS of the newest bar seen - lines for a minute arrive within
    about 2 minutes of it, so 10 minutes holds every pairing with room to spare."""

    KEEP_MS = 10 * MINUTE_MS

    def __init__(self):
        self.throttled = {}                     # minute -> the 1m incomplete record
        self.verdicts = {}                      # minute -> [(kind, bar_ms, detail)]
        self.newest = 0

    def _prune(self):
        for d in (self.throttled, self.verdicts):
            for m in [m for m in d if m < self.newest - self.KEEP_MS]:
                del d[m]

    def feed(self, r):
        if r.get('source') != 'kline_audit' or not r.get('bar_ms'):
            return None                         # not this rule's record: the normal path decides
        b = int(r['bar_ms']); m = b - b % MINUTE_MS
        self.newest = max(self.newest, b); self._prune()
        if r.get('kind') == '1m incomplete':
            g = _INCOMPLETE.search(str(r.get('detail', '')))
            if not g or int(g.group(3)) < int(g.group(4)) or g.group(5) != 'True':
                return None                     # our tape or the official bar is short: alert as before
            self.throttled[m] = r
            seen = self.verdicts.get(m)
            if not seen:
                return (False, None)            # throttle only: silent
            return (True, 'API throttle at %s (%s) + %d downstream: %s' % (
                _hms(m), g.group(0).split(' kc')[0], len(seen),
                '; '.join('%s %s %s' % (k, _hms(x), d[:40]) for k, x, d in seen[:3])))
        self.verdicts.setdefault(m, []).append((r.get('kind'), b, str(r.get('detail', ''))))
        t = self.throttled.get(m)
        if t is None:
            return None
        return (True, 'API throttle at %s + downstream %s %s | %s' % (
            _hms(m), r.get('kind'), _hms(b), str(r.get('detail', ''))[:60]))


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
    frozen = dict(n=0, last=None, first=None)   # the current run of consecutive 5 s frozen bars
    gate = ThrottleGate()
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
            g = gate.feed(r)
            if g is not None and g[0] is False:
                continue                                    # throttle-only 1m incomplete: silent
            if g is not None:                               # throttle + downstream: one line, always
                print('ALERT %s %s | bar %s | %s' % (key[0], key[1], _hms(r.get('bar_ms')), g[1][:180]),
                      flush=True)
                if key == ('kline_audit', '5s frozen'):     # keep the frozen-run count true
                    b = r.get('bar_ms')
                    run = frozen['n'] + 1 if (b and frozen['last'] and int(b) - frozen['last'] == 5000) else 1
                    frozen.update(n=run, last=int(b) if b else None, first=frozen['first'] if run > 1 else b)
                continue
            if key == ('kline_audit', '5s frozen'):
                b = r.get('bar_ms')
                run = frozen['n'] + 1 if (b and frozen['last'] and int(b) - frozen['last'] == 5000) else 1
                frozen.update(n=run, last=int(b) if b else None, first=frozen['first'] if run > 1 else b)
                if run < FROZEN_RUN_BARS:
                    continue
                r = dict(r, detail='%d bars in a row since %s | %s' % (run, _hms(frozen['first']), r.get('detail')))
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
