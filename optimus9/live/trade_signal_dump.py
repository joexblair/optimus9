"""trade_signal_dump — o9-live's trade-signal dump: one line per trade action, append-only.

Joe 0929: *"I would build a o9-live trade-signal dump to log and consume via a shell monitor"*.
ONE JOB: append one JSON line per action to a dedicated file - not `o9live_run.log`, which carries
everything. It never rewrites or deletes a line. `docs/o9-live-recon/RECON.md` reads it.

THE FIVE FIELDS ARE RULED, AND THERE ARE NO OTHERS. Joe 0929-late: *"I'm confirming the list so that
the recon-loop can start"* (`RECON.md:21-30`):

    wall_ms   wall-clock ms when o9-live decided. Joe 0929: *"o9-live has no choice - it must use
              wall-clock"*
    action    'open' or 'close'
    side      'Buy' or 'Sell' - the side of the position being opened or closed
    reason    'octo-sig', 'dr-flip', 'stop', or 'non-trading octo-sig'
    bar_ms    the bar it believes it acted on, so a bar-vs-wall-clock gap is visible without inference

`non-trading octo-sig` IS AN OPEN WITH NO CLOSE. Joe 1002, on the same-dr octo-sig the book does not
act on: *"technically it's an open without a close. can you notate (in the log) in a way that steers
you towards reconcilling the non-trading octo-sig?"*. The recon reads it as: match the signal bar,
expect no order, no fill and no close line. An octo-sig that falls in a feed gap of 5 min or more is
written the same way, and `wall_ms - bar_ms` shows why.
"""
import json
import os
import time

REASONS = ('octo-sig', 'dr-flip', 'stop', 'non-trading octo-sig')
DEFAULT_PATH = os.environ.get('O9_TRADE_SIGNAL_DUMP',
                              '/home/joe/thecodes/o9live_trade_signal_dump.log')


class TradeSignalDump:
    def __init__(self, path=DEFAULT_PATH):
        self.path = path

    def write(self, action, side, reason, bar_ms, wall_ms=None):
        """Append one line. Raises on a value outside the ruled set rather than writing it."""
        if action not in ('open', 'close'):
            raise ValueError('dump action must be open or close, got %r' % (action,))
        if side not in ('Buy', 'Sell'):
            raise ValueError('dump side must be Buy or Sell, got %r' % (side,))
        if reason not in REASONS:
            raise ValueError('dump reason must be one of %r, got %r' % (REASONS, reason))
        line = json.dumps(dict(wall_ms=int(wall_ms if wall_ms is not None else time.time() * 1000),
                               action=action, side=side, reason=reason, bar_ms=int(bar_ms)))
        with open(self.path, 'a') as fh:
            fh.write(line + '\n')
            fh.flush()
            os.fsync(fh.fileno())
        return line
