"""octo_freedom — `octo-freedom`'s live producer: the walk, rule#1, the signal bar and the trade book,
carried bar to bar. Shape B in `docs/octo-freedom/1001_rebuild_timing.md`.

JOE'S RULINGS THIS IMPLEMENTS
    shape B      1002, *"B"*: carry the arm / walk / trade-book state; rebuild the lines each bar.
                 Measured: a full 104 h rebuild costs ~80 s per bar against a 5 s budget; the lines
                 alone cost 1.27-1.45 s and the walk step 0.59 ms average
    the window   1001, *"#3 window is approved"*: 104 h = lookback 24 h + warmup 80 h
                 (`strategy.py:23` defaults). Minimum measured 72.47 h (`1001_warmup.md`)
    the signal   `WALK FIRES FROM` - the first bar of each run of consecutive emitted bars
                 (`leash_walk.walk_fires_from`), opened as `octo-sig` (Joe 1001)
    rule#1       `gate_open(k, 60)`, `walk_rule1_back_min` 5.0 min - NOT the bare 84-bar call
    the dr       the trade book reads `rig.DR`, the walk's dr (Joe 1001: *"it's the dr in this
                 report"*); a trade opens on the ARM's dr (Joe 1001: *"I think we do the same for dr"*)
    same-dr      Joe 1002: *"for this first MVP, no pyramid trades. note the signal for recon and keep
                 walking"* - `TradeBook` returns it as an 'inert' event
    startup      Joe 1002: *"stay flat ... walking the bars until a octo-sig prints. that's when the
                 first trade will opened"*. The walk is rebuilt over the whole first window; the trade
                 book starts EMPTY at the first live bar

ONE JOB: turn a window's arrays into per-bar records - did the walk pass, did rule#1 pass, is it a
signal bar, what did the trade book do. It sizes nothing, places nothing and logs nothing; turning
records into orders and dump lines is the caller's.

THE BAR NUMBER IS GLOBAL. Every window has its own index grid, so the carried steppers are fed
`ts // 5000`, which is consecutive across windows exactly when the bars are. `LeashWalk.step` and
`TradeBook.step` raise on a skipped number, so a hole in the tape stops the producer rather than
being stepped over.

PARKED TO MVP2 BY JOE 1002 (`docs/o9-live-recon/MVP2.md` item 6): bars the bar builder rewrites after
the walk consumed them (it rewrites each bar for its next 3 cycles, `bar_builder.py:50`), and the
blip-triggered reset. MVP1 records tick and kline issues in `o9live_errors.log` and acts on none.
"""
import numpy as np

from optimus9.compute.leash_walk import LeashWalk, step_bar
from optimus9.compute.trade_walk import TradeBook
from optimus9.live.octo_inputs import Inputs

BAR_MS = 5000
LABEL = 'octo-sig'                  # Joe 1001 / 1002 - what opens a trade, and what an opposing one closes it as
LOOKBACK_H, WARMUP_H = 24, 80       # Joe 1001: "#3 window is approved" - strategy.py:23's defaults


class OctoFreedom:
    """Carried state across windows. Call `window(end_ms)` then `advance(inp, live_from_ts)` each bar."""

    def __init__(self, db, cfg, bias_cfg, lookback_h=LOOKBACK_H, warmup_h=WARMUP_H):
        self.db = db
        self.cfg = cfg
        self.bias_cfg = bias_cfg
        self.lookback_h = lookback_h
        self.warmup_h = warmup_h
        self.walk = LeashWalk(cfg.ladder, **cfg.knobs)
        self.book = None                    # created at the first LIVE bar - Joe 1002: stay flat
        self._last_ts = None
        self._prev_emitted = False

    def window(self, end_ms):
        """The 104 h window whose LAST bar is the newest bar strictly before `end_ms`. -> (W, Inputs)."""
        import bias_machine as bm
        W = bm.BiasWindow(self.db, int(end_ms), lookback=self.lookback_h, warmup=self.warmup_h,
                          cfg=self.bias_cfg, line_overrides=self.cfg.overrides, lean=True)
        return W, Inputs(W, self.cfg)

    def advance(self, inp, live_from_ts):
        """Step every bar of `inp` after the last one stepped. -> [record], one per bar stepped.

        On the first call every bar of the window is stepped, which rebuilds the walk's state.
        Bars at or after `live_from_ts` also step the trade book; bars before it are warm-up only.
        rule#1 is evaluated where the walk passes, and during warm-up only on the bar before the
        first live bar - the only warm-up verdict a live bar reads (the run-first test). rule#1
        carries no state, so skipping the rest of the warm-up changes nothing.
        """
        ts = inp.ts
        if self._last_ts is None:
            j0 = 0
        else:
            j0 = int(np.searchsorted(ts, self._last_ts)) + 1
            if j0 < 1 or j0 > len(ts) or int(ts[j0 - 1]) != self._last_ts:
                raise RuntimeError('octo_freedom: the window does not contain the last stepped bar '
                                   '%d, so the carried state cannot be continued' % self._last_ts)
        recs = []
        for j in range(j0, len(ts)):
            t_j = int(ts[j])
            k = t_j // BAR_MS
            first = (j == 0)
            hit = step_bar(self.walk, k, float(inp.mage[j]), None if first else float(inp.mage[j - 1]),
                           int(inp.DR[j]), None if first else int(inp.DR[j - 1]),
                           float(inp.CC[j]), None if first else float(inp.CC[j - 1]),
                           (lambda t, a, _j=j: inp.mom_at(t, _j, a)),
                           (lambda t, a, _j=j: inp.fr_at(t, _j, a)),
                           (lambda a, _j=j: bool(inp.rev[a][_j]) if a in inp.rev else False))
            live = t_j >= int(live_from_ts)
            judged = live or t_j >= int(live_from_ts) - BAR_MS
            emitted = bool(hit) and judged and inp.gate_open(j, self.cfg.r1_back)
            fires = emitted and not self._prev_emitted
            st = dict(self.walk.state) if hit else None
            events = []
            if live:
                if self.book is None:
                    self.book = TradeBook(self.cfg.mae_cap, LABEL)
                events = self.book.step(k, int(inp.DR[j]), int(inp.DR[j - 1]), float(inp.px[j]),
                                        fires, st['arm_dr'] if fires else None)
            recs.append(dict(ts=t_j, k=k, live=live, hit=bool(hit),
                             emitted=emitted if judged else None, fires=fires,
                             arm=st['arm'] if st else None, arm_dr=st['arm_dr'] if st else None,
                             events=events))
            self._prev_emitted = emitted
            self._last_ts = t_j
        return recs
