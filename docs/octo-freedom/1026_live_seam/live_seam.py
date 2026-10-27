"""live_seam - read A (emerging) against read B (seam-5s) on the LIVE tape, at Joe's four events. 1026.

THE TASK, relayed by ac06c2, `sidegigs/1/log.jsonl` #4. Joe: *"we need to be 100% sure that 'seam - 5s'
calculations will match the live tape. spin up a test that reads the live klines, and validate these
4 events when they fire"* / *"send an update whenever one of the 4 events fire so I can see what it
looks like on the charts, in realtime"*.

THE TWO READS, per line, per 5 s bar
    A  the EMERGING value at the bar, computed the moment the bar lands on the live tape
    B  `v4_closed_prev.series` over the A values this harness recorded: the A value at the last 5 s
       bar of the previous COMPLETED bucket of the line's TF, midnight grid, held forward

THE FOUR EVENTS, each run once on the A series and once on the B series
    #1  ws1b oob -> ib. The raw cross bar: `jig.oob_ib_cross` at xwob 1. Both sides
    #2  baton pass ws{t}r -> ws{t+1}r, both sides. ws{t}r is at a pass bar - oob -> ib, or
        ex-fence -> in-fence, `v4_lineage2._pass_bars`' two rules - AND ws{t+1}r is ex-fence on that
        side AND `v4_lineage2.towards` that side. `towards` reads a `v4_l2_proxy.Board` whose ladder is
        the series the run is on.
        WIDENED, Joe 1026 via ac06c2 #34: t in PASS_TFS = 1..11, every adjacent pair.
        ac06c2 #9: EVERY pass bar is a row - kind 'no receiver' when ws{t+1}r does not
        qualify - with the rung scan ws{t+1}r..ws12r (value, ex-fence, towards)
        and the most recent EMERGING reversal of the handing and receiving lines, raw bar and stamp
    #3  ws{t}Mage into oob, t in 5..12, the raw cross bar, both sides
    #4  ws{t}r into oob, t in 5..12, the raw cross bar, both sides
No wob anywhere. Joe has not ruled one for #3 and #4; the report carries each firing's dwell so a wob
he rules later applies to the recorded data without re-running.

THE SOURCE IS THE LIVE TAPE: `kline_collection`, the table o9-live's `RealtimeDriver` reads. The loop
wakes at each 5 s seam + 301 ms, the driver's own grace. Every new row is built into the window
o9-live builds - `BiasWindow` over `octo_freedom.LOOKBACK_H` + `WARMUP_H`, the lines from
`octo_inputs.line_overrides` - and A is the last value of each emerging line.

EVERY BAR records the OHLCV as received, all 21 read A and read B values, the B source bars, and
pxs - `BiasWindow.px`, the global 5 s DEMA(close, 2). Events go to events.jsonl; `live_seam_db`
banks them in `l2_live_seam_event`. The chat gets a start line, a status line every STATUS_BARS
bars, any problem at once, and an end line - Joe 1026: *"there's no need to alert us on every event"*.
Each run writes its own folder, out/run_<last seeded bar>.

SEEDED BARS. The first window's emerging arrays fill the history before the first live bar, so B and
`towards` have history from the first live bar on. Those bars are flagged `seeded`: they were computed
at start-up, not observed at their own seam.

READ-ONLY. Nothing here writes the DB. Untouched: o9-live, lp_config, the .npy caches, v4_knobs,
replay.py.

    python3 live_seam.py run [--hours 4]
    python3 live_seam.py report <run_dir>
"""
import argparse
import datetime as dt
import importlib.util
import io
import json
import os
import sys
import time
import traceback

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
_e = sys.stderr; sys.stderr = io.StringIO()
import bias_machine as bm
import v4_knobs as K
import v4_closed_prev as CP
import v4_lineage2 as L2
from v4_l2_proxy import Board
from optimus9 import DatabaseManager
from optimus9.config import get_db_config
from optimus9.analysis.jig import lift_off, oob_ib_cross
from optimus9.live.octo_freedom import LOOKBACK_H, WARMUP_H
from optimus9.live.octo_inputs import line_overrides
sys.stderr = _e

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('LIVE_SEAM_OUT', os.path.join(HERE, 'out'))     # a smoke test points this elsewhere
STATUS_BARS = 360                   # a chat status line every 360 live bars = 30 min, ac06c2 #22


def paths(rd):
    """One run's files, in its own folder `rd`. -> (meta, seed, bars, events)."""
    return tuple(os.path.join(rd, f) for f in ('meta.json', 'seed.npz', 'bars.jsonl', 'events.jsonl'))

SYMBOL = os.environ.get('O9_SYMBOL', 'FARTCOINUSDT')
BAR_MS = 5000
DELAY_MS = 301                      # RealtimeDriver's seam grace, driver.py `delay_ms=301`
CHAT = '/home/joe/thecodes/sidegigs/1/chat.py'
CHAT_NAME = 'claude-639244ab'

R_TFS = list(range(1, 13))
PASS_TFS = list(range(1, 12))     # #2's handing lines: every adjacent pair ws1..ws12. Joe 1026 via ac06c2 #34:
#                                   *"go for it - more data can't hurt us"*. Was 1..3, then 1..4 with ws4r as
#                                   'no receiver' only (#9)
M_TFS = list(range(5, 13))
NAMES = ['ws1b'] + ['ws%dr' % t for t in R_TFS] + ['ws%dMage' % t for t in M_TFS]
EV_NAME = {1: '#1 ws1b oob -> ib', 2: '#2 baton pass', 3: '#3 Mage into oob', 4: '#4 r into oob'}
SIDE = {1: 'HIGH', -1: 'LOW'}


def tf_of(name):
    """'ws12Mage' -> 12."""
    s = name[2:]
    i = 0
    while s[i].isdigit():
        i += 1
    return int(s[:i])


def utc(ms):
    return dt.datetime.fromtimestamp(int(ms) / 1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def b_source(ts, j, tf):
    """The bar `CP.series` reads for bar `j` of a TF-minute line. -> index, or -1 before any bucket closed.

    Located only for the print. `step` asserts that the value at this bar equals `CP.series`' own,
    so this and the module that owns the rule cannot disagree.
    """
    tf_ms = int(tf) * 60_000
    t = int(ts[j])
    day = (t // 86_400_000) * 86_400_000
    bo = day + ((t - day) // tf_ms) * tf_ms
    return int(np.searchsorted(ts[:j + 1], bo, side='left')) - 1


class _Names:
    """The shape `octo_inputs.line_overrides` reads: an object with `names()`."""

    def names(self):
        return list(NAMES)


def _chat():
    spec = importlib.util.spec_from_file_location('sidegig_chat', CHAT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Tape:
    """Every bar this harness holds, seeded and live, with the A value of every line."""

    def __init__(self, cap):
        self.n = 0
        self.ts = np.zeros(cap, np.int64)
        self.A = {n: np.full(cap, np.nan) for n in NAMES}

    def _grow(self):
        cap = len(self.ts) * 2
        self.ts = np.r_[self.ts, np.zeros(cap - len(self.ts), np.int64)]
        for n in NAMES:
            self.A[n] = np.r_[self.A[n], np.full(cap - len(self.A[n]), np.nan)]

    def append(self, t, vals):
        if self.n == len(self.ts):
            self._grow()
        self.ts[self.n] = int(t)
        for n in NAMES:
            self.A[n][self.n] = vals[n]
        self.n += 1

    def a(self):
        return {n: self.A[n][:self.n] for n in NAMES}

    def b(self):
        ts = self.ts[:self.n]
        return {n: CP.series(self.A[n][:self.n], tf_of(n) * 60, ts=ts) for n in NAMES}


def last_rev(E, tf, side, j):
    """The most recent emerging reversal of `E` on `side` KNOWABLE at bar `j`. -> (raw bar, stamp) or None.

    The banked mech, `jig.lift_off` with `v4_fast.revs`' own knobs (LIFT_PTS, gap_for(tf), LIFT_TOL,
    LIFT_WOB). Run on E[:j+1], so it keeps only lift-offs whose hold has completed by `j`: the stamp,
    K.lift_stamp(b) = b + LIFT_WOB - 1, is at or before `j`. The raw bar is the reversal's identity
    and the stamp is when it is knowable - two columns, never collapsed.
    """
    L = lift_off(E[:j + 1], side, K.LIFT_PTS, K.gap_for(tf), K.LIFT_TOL, K.LIFT_WOB)
    if not len(L):
        return None
    b = int(L[-1])
    assert K.lift_stamp(b) <= j
    return b, int(K.lift_stamp(b))


def fires(X, j):
    """#1, #3 and #4 at bar `j` on ONE read's series `X` ({name: array}). -> [dict]."""
    out = []
    v = X['ws1b']
    for c, _cf, s in oob_ib_cross(v[j - 1:j + 1], K.OOB_HI, K.OOB_LO, 1):
        if c == 1:
            out.append(dict(ev=1, kind='fire', lines=['ws1b'], side=int(s)))
    for role, ev in (('Mage', 3), ('r', 4)):
        for t in M_TFS:
            n = 'ws%d%s' % (t, role)
            v = X[n]
            if not (np.isfinite(v[j - 1]) and np.isfinite(v[j])):
                continue
            for s in (1, -1):
                if K.oob(v[j], s) and not K.oob(v[j - 1], s):
                    out.append(dict(ev=ev, kind='fire', lines=[n], side=s))
    return out


def passes(X, j, E, tfs=None):
    """#2 at bar `j` on ONE read's series `X`: every pass bar of ws{t}r, t in `tfs`. -> [dict].

    `E` is the A series. ac06c2 #9, Joe 1025: the reversal read stays EMERGING in both runs.
    kind 'fire' = ws{t+1}r is ex-fence on the row's side AND `towards` it; 'no receiver' otherwise.
    Each row carries the rung scan ws{t+1}r..ws12r: value, ex-fence, `towards`.
    """
    tfs = PASS_TFS if tfs is None else tfs
    out = []
    bd = Board({t: X['ws%dr' % t][:j + 1] for t in R_TFS}, {t: X['ws%dr' % t][:j + 1] for t in R_TFS})
    for t in tfs:
        h = X['ws%dr' % t]
        for s in (1, -1):
            why = []
            if any(c == 1 and sd == s for c, _cf, sd in oob_ib_cross(h[j - 1:j + 1], K.OOB_HI, K.OOB_LO, 1)):
                why.append('oob -> ib')
            if K.ex_fence(h[j - 1], s) and not K.ex_fence(h[j], s):
                why.append('ex-fence -> in-fence')
            if not why:
                continue
            rungs = []
            for u in range(t + 1, R_TFS[-1] + 1):
                ex = bd.ex_fence(u, j, s)
                rungs.append(dict(line='ws%dr' % u, value=_f(bd.value(u, j)), ex_fence=bool(ex),
                                  towards=bool(L2.towards(bd, u, j, s))))
            got = rungs[0]['ex_fence'] and rungs[0]['towards']
            rv_h = last_rev(E['ws%dr' % t], t, s, j)
            rv_r = last_rev(E['ws%dr' % (t + 1)], t + 1, s, j) if got else None
            out.append(dict(ev=2, kind='fire' if got else 'no receiver',
                            lines=['ws%dr' % t, 'ws%dr' % (t + 1)] if got else ['ws%dr' % t],
                            side=s, why=' + '.join(why), rungs=rungs,
                            rev_hand=None if rv_h is None else dict(raw=rv_h[0], stamp=rv_h[1]),
                            rev_recv=None if rv_r is None else dict(raw=rv_r[0], stamp=rv_r[1])))
    return out


def events_at(X, j, E):
    """Every row at bar `j` on ONE read's series `X`: #1, #3, #4 and every #2 pass bar. -> [dict]."""
    return fires(X, j) + passes(X, j, E)


def decorate(e, read, j, ts, A, B):
    """Stamp a row with its read, its bar, and both reads of its lines with read B's source. -> e."""
    t = int(ts[j])
    for k in ('rev_hand', 'rev_recv'):
        if e.get(k):
            e[k].update(raw_utc=utc(ts[e[k]['raw']]), stamp_utc=utc(ts[e[k]['stamp']]))
    src = {n: b_source(ts, j, tf_of(n)) for n in e['lines']}
    e.update(read=read, ts=t, utc=utc(t), a={n: _f(A[n][j]) for n in e['lines']},
             b={n: _f(B[n][j]) for n in e['lines']},
             b_src={n: (utc(ts[src[n]]) if src[n] >= 0 else None) for n in e['lines']},
             b_age={n: ((t - int(ts[src[n]])) // 1000 if src[n] >= 0 else None) for n in e['lines']})
    return e


def _f(x):
    return None if not np.isfinite(x) else float(x)


def _tp_pk(db):
    r = db.execute('SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s', (SYMBOL,), fetch=True)
    return int(r[0]['tp_pk'])


def window(db, ovr, bar_ts):
    """o9-live's window whose LAST bar is `bar_ts`. -> BiasWindow."""
    W = bm.BiasWindow(db, int(bar_ts) + BAR_MS, lookback=LOOKBACK_H, warmup=WARMUP_H, cfg=bm.BiasConfig(),
                      line_overrides=ovr, lean=True)
    assert int(W.ts[-1]) == int(bar_ts), 'window ends at %d, not the bar %d' % (int(W.ts[-1]), int(bar_ts))
    return W


def _ohlcv(W):
    r = W.base.iloc[-1]
    return [float(r['open']), float(r['high']), float(r['low']), float(r['close']), float(r['volume'])]


def _say(chat, text):
    try:
        chat.post(CHAT_NAME, text)
    except Exception as e:                       # a chat failure must not stop the measurement
        print('chat post failed: %s' % e, flush=True)


def run(hours):
    db = DatabaseManager(**get_db_config()); db.connect()
    tp = _tp_pk(db)
    ovr = line_overrides(db, _Names())
    chat = _chat()
    newest = int(db.execute('SELECT MAX(kc_timestamp) t FROM kline_collection WHERE kc_tp_pk=%s', (tp,),
                            fetch=True)[0]['t'])
    W = window(db, ovr, newest)
    rd = os.path.join(OUT, 'run_' + utc(newest).replace('-', '').replace(':', '').replace(' ', '_'))
    os.makedirs(rd)
    META, SEED, BARS, EVENTS = paths(rd)
    E = {n: np.asarray(W._line_emerging(n), float) for n in NAMES}
    tape = Tape(len(W.ts) + int(hours * 3600_000 // BAR_MS) + 1)
    for i in range(len(W.ts)):
        tape.append(int(W.ts[i]), {n: E[n][i] for n in NAMES})
    np.savez(SEED, ts=np.asarray(W.ts, np.int64), px=np.asarray(W.px, float), **{n: E[n] for n in NAMES})
    meta = dict(symbol=SYMBOL, tp_pk=tp, seed_from=utc(W.ts[0]), seed_to=utc(W.ts[-1]), seed_bars=len(W.ts),
                hours=hours, lookback_h=LOOKBACK_H, warmup_h=WARMUP_H, delay_ms=DELAY_MS,
                filler_invisible=bool(W._filler_invisible), overrides={n: list(map(str, ovr[n])) for n in NAMES},
                oob=(K.OOB_LO, K.OOB_HI), fence=K.fence(), started_utc=utc(time.time() * 1000))
    with open(META, 'w') as fh:
        json.dump(meta, fh, indent=1)
    first = newest + BAR_MS
    end = first + int(hours * 3600_000)
    _say(chat, 'live_seam STARTED. Seeded to %s. First live bar %s, last live bar %s (%s h). Files: %s. '
         'No per-firing posts; a status line every %d bars.' % (utc(newest), utc(first), utc(end - BAR_MS), hours,
                                                              rd, STATUS_BARS))
    print('seeded %d bars to %s; live %s .. %s' % (len(W.ts), utc(newest), utc(first), utc(end - BAR_MS)),
          flush=True)
    last = newest
    n_bars = n_missed = n_err = 0
    rows_by = {}
    bfh = open(BARS, 'a')
    efh = open(EVENTS, 'a')
    while last < end - BAR_MS:
        now = int(time.time() * 1000)
        time.sleep(max(0.0, ((now // BAR_MS + 1) * BAR_MS + DELAY_MS - now) / 1000.0))
        try:
            rows = db.execute('SELECT kc_timestamp t FROM kline_collection WHERE kc_tp_pk=%s AND kc_timestamp>%s '
                              'ORDER BY kc_timestamp', (tp, last), fetch=True)
        except Exception as e:
            print('%s DB read failed: %s' % (utc(time.time() * 1000), e), flush=True)
            continue
        for row in rows:
            t = int(row['t'])
            if t >= end:
                break
            recv = int(time.time() * 1000)
            rec = dict(ts=t, utc=utc(t), recv_ms=recv, late_ms=recv - (t + BAR_MS), gap_bars=(t - last) // BAR_MS - 1)
            try:
                W = window(db, ovr, t)
                vals = {n: float(np.asarray(W._line_emerging(n), float)[-1]) for n in NAMES}
                rec['ohlcv'] = _ohlcv(W)
                rec['pxs'] = float(np.asarray(W.px, float)[-1])   # global 5 s DEMA(close, 2), bl_detect
            except Exception as e:
                vals = {n: np.nan for n in NAMES}
                rec['error'] = '%s: %s' % (type(e).__name__, e)
                traceback.print_exc()
            tape.append(t, vals)
            j = tape.n - 1
            A, B = tape.a(), tape.b()
            ts = tape.ts[:tape.n]
            src = {}
            for n in NAMES:
                k = b_source(ts, j, tf_of(n))
                ok = (k >= 0 and (A[n][k] == B[n][j] or (np.isnan(A[n][k]) and np.isnan(B[n][j])))) or \
                     (k < 0 and np.isnan(B[n][j]))
                assert ok, 'b_source disagrees with CP.series on %s at %s' % (n, utc(t))
                src[n] = k
            rec['a'] = {n: _f(A[n][j]) for n in NAMES}
            rec['b'] = {n: _f(B[n][j]) for n in NAMES}
            rec['b_src'] = {n: (utc(ts[src[n]]) if src[n] >= 0 else None) for n in NAMES}
            rec['done_ms'] = int(time.time() * 1000)
            fired = [decorate(e, read, j, ts, A, B) for read, X in (('A', A), ('B', B))
                     for e in events_at(X, j, A)]
            bfh.write(json.dumps(rec) + '\n'); bfh.flush()
            for e in fired:
                efh.write(json.dumps(e) + '\n')
            efh.flush()
            n_bars += 1
            n_missed += max(0, rec['gap_bars'])
            for e in fired:
                k = '%s %s %s' % (EV_NAME[e['ev']].split(' ')[0], e['kind'], e['read'])
                rows_by[k] = rows_by.get(k, 0) + 1
            if rec['gap_bars'] > 0 or 'error' in rec:
                n_err += 'error' in rec
                _say(chat, 'live_seam PROBLEM at %s: %s' % (utc(t), rec.get('error') or
                                                            '%d bar(s) missing on the tape before it' % rec['gap_bars']))
            if n_bars % STATUS_BARS == 0:
                _say(chat, 'live_seam status: %d bars processed, %d missing on the tape, %d compute errors, newest %s.\n\n'
                     '| event kind read | rows |\n|---|---|\n%s' % (n_bars, n_missed, n_err, utc(t),
                     '\n'.join('| %s | %d |' % (k, v) for k, v in sorted(rows_by.items()))))
            print('%s late %d ms compute %d ms firings %d pass rows %d%s' % (
                utc(t), rec['late_ms'], rec['done_ms'] - recv, sum(e['kind'] == 'fire' for e in fired),
                sum(e['ev'] == 2 for e in fired),
                ' ERROR' if 'error' in rec else ''), flush=True)
            last = t
    bfh.close(); efh.close()
    _say(chat, 'live_seam FINISHED at %s, %d bars. Files: %s' % (utc(last), n_bars, rd))
    print('done', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run'); r.add_argument('--hours', type=float, default=4.0)
    rp = sub.add_parser('report'); rp.add_argument('run_dir')
    a = ap.parse_args()
    if a.cmd == 'run':
        run(a.hours)
    else:
        import live_seam_report
        live_seam_report.main(a.run_dir)
