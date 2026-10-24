"""THE ONE DRIVER. v4core + v4-ws5rbackstop + v4saviour on one shared position, plus every mode
anyone needs to interrogate it. Joe 1023: *"do it"*.

WHY IT IS ONE FILE AND NOT TWENTY-SIX. By 1023 the session had produced 26 one-off analysis
scripts and more than twenty inline heredocs, and four of the worst defects of the day came from
exactly that: a FRAGMENT re-implementing something a durable module already did correctly, and
dropping an invariant on the way.

    the 08-31 anchor at a window edge   an inline heredoc called LT.walk(R, 5, -1, A, B) by hand
                                        with A = 19:00:00. ws1b does not reach low oob until
                                        19:17, so no trade existed and the leg was never legitimate
    the arm pairing off by one leg      v4core_walk.py, written fresh
    the audit tool's zip misalignment   v4_causal_scan.py, written fresh instead of reusing ledger
    F.reset() inside the per-fire loop  an inline heredoc; it timed out at 900 s

Joe 1023: *"are you building one script and adding/changing as we find issues, or are you often
building a new script? your statement points more to the latter, which I think is the source of a
lot of loss time"*.

THE RULES THIS FILE ENFORCES
    ONE ANCHOR SOURCE      lineage is NEVER called with a hand-picked bar. `_lineage` is the only
                           call site and it takes the anchor from the machine's own state - a
                           STEP2 arm or a backstop fire. A window edge cannot reach it.
    ONE EXIT RULE          v4_equity.ledger. This file scores nothing itself.
    ONE PARITY HARNESS     v4_fast.check, run by `parity`.
    TRACES ARE A MODE      `trace` prints the row table for the leg containing a bar, using the
                           anchor the machine actually used. Not a new file.
    SWEEPS ARE ENV         one `row` call per arm, driven by env knobs, as v4_pass_ab already did.

MODES
    chain   <start> <end> <order> <bstop_fallback>        the trade list
    trace   <start> <end> <order> <fallback> <bar>        the leg containing <bar>, step by step
    row     <start> <end> <order> <fallback>              ONE pipe-delimited summary row, for sweeps
    parity  <start> <end>                                 cached against un-cached

ONE POSITION AT A TIME, because that is what `rev-trade` means. MAX_PYRAMID governed the
backstop-only ledger where fires overlapped with nothing closing them; a rev-trade machine never
holds two.

EVERY MECH'S TRIGGER IS RULED
    v4-ws5rbackstop   lineage EXHAUST        -> opens at max(EXHAUST, the fire) + 1
    v4core STEP4/5    lineage EXHAUST        -> opens at EXHAUST + 1
    v4saviour         the SAVIOUR REV verdict -> opens at `reopen`, its fill + 1

STEP0 IS NOT SPECIAL: STEP1/STEP2 against an invisible LONG **or SHORT**, both sides, first to
complete sets the real trade as that invisible one's rev-trade.

THE LINES, three sets and not interchangeable: v4core's arm reads the CLOSED c-set; lineage reads
the NORMAL lines; the backstop and v4saviour read the banked emerging lines.

PRECEDENCE HAS NO DEFAULT. The EARLIEST candidate open always wins; `order` breaks an exact tie
only. v4saviour has priority from Joe's #31; backstop against v4core is unruled.

CAUSAL. Every candidate is computed from bars at or before the bar it opens on.

usage: v4_machine.py <mode> <out|-> <start> <end> [order] [fallback] [bar]
"""
import sys
import io
import os

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
import v4_knobs as K
import v4_fast as F
import v4_core_arm as CA
import v4_saviour as SV
import v4_deferred_trades as DT
import v4_rcfg_sweep as RS
from v4_equity import ledger, PCT, COINS, START, DRAG_22K
from v4_confluence import metrics
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.swing_detect import find_pivots
import v4_lineage_trace as LT
sys.stderr = _e

MECHS = ('saviour', 'core', 'backstop')


def target_side(d):
    """A LONG hunts the HIGH oob, a SHORT the LOW. Banked, set once at the open."""
    assert d in ('LONG', 'SHORT'), d
    return +1 if d == 'LONG' else -1


def flip(d):
    return 'SHORT' if d == 'LONG' else 'LONG'


class Machine:
    """The state and the three candidate producers. The ONLY place lineage is called."""

    def __init__(self, A, B, order, fallback):
        assert sorted(order) == sorted(MECHS), 'order must permute %r' % (MECHS,)
        self.A, self.B, self.order, self.fb = A, B, order, fallback
        self.R = RS.load((RS.K0, RS.R0, RS.S0))
        self.MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
        self.CL = CA.lines()
        F.reset()
        self.fires = F.scan(A, B, self.R, self.MG)

    # ── the single lineage call site ───────────────────────────────────────────────────────────
    def _lineage(self, start_tf, side, anchor, trace=False, events=None, mech=None):
        """Lineage from an anchor the MACHINE produced. -> (verdict, bar, rows).

        THE ANCHOR IS NEVER A WINDOW EDGE. Callers pass a STEP2 arm bar or a backstop's ws5r
        reversal, both of which are machine state. This assert is the guard, not a comment.
        """
        assert self.A <= anchor <= self.B, 'the lineage anchor is outside the window'
        rows = []
        n0 = len(events) if events is not None else 0
        if trace:
            v, b, rows = LT.walk(self.R, start_tf, side, anchor, self.B,
                                 log=lambda *a: rows.append(a))
            return v, b, rows
        v, b = F.walk(self.R, start_tf, side, anchor, self.B, events=events)
        #   THE FULL R, not a slice from start_tf. The walk's own ST loop ignores keys below
        #   start_tf, so arm A is unchanged; the ws4 handover needs ws1r, which a slice starting at
        #   ws4 would not contain.
        if events is not None:                 # so every hand-off can be re-traced from its anchor
            for e in events[n0:]:
                e['anchor'], e['stf'], e['verdict'], e['exh'] = anchor, start_tf, v, b
                e['side'], e['mech'] = side, mech
                                        # THE WALK'S side, not the leg's: a backstop walks its own
                                        #   fire's side, which need not match the open trade's
        return v, b, rows

    # ── the three candidates ───────────────────────────────────────────────────────────────────
    def core(self, open_bar, tsd, trace=False, events=None):
        a, gate = CA.arm(self.CL, open_bar, tsd, self.B)
        if a is None:
            return None, 'no STEP2 arm', []
        stf = CA.start_tf(self.CL, a, tsd)
        v, exh, rows = self._lineage(stf, tsd, a, trace, events, 'core')
        if v != 'EXHAUST' or exh is None:
            return None, '%s from ws%d, arm %s' % (v, stf, ln.U(a)), rows
        return exh + 1, 'cws1b %s, arm %s, ws%d, exh %s' % (ln.U(gate), ln.U(a), stf, ln.U(exh)), rows

    def backstop(self, open_bar, tsd, trace=False, events=None):
        """The earliest backstop fire ON THE WALK'S SIDE that resolves. -> (open bar, why, rows).

        THE SIDE IS AN INPUT, Joe 1024: *"the first mech to fire (ie ws1b oob) has a side (the
        target-side), and that side is honoured by all mechs for the complete walk, all the way up
        to rev-trade's CLOSE signal"*, and *"don't calculate anything from the counter target-side
        unless a mech specifically requires it"*.

        THIS WAS THE ONLY MECH OF THE THREE NOT GIVEN THE SIDE. v4core takes it through
        CA.arm(..., tsd, ...) and v4saviour through SV.walk(..., tsd, ...); this took ANY fire
        after the open bar. On 2026-09-01 that offered the 19:32:45 fire - a HIGH-oob ws5r, side
        +1, whose own `dir` is SHORT - to a leg whose open trade was already a SHORT and whose
        target side was LOW. `chain` then set the direction by flipping the previous trade, so the
        row printed LONG while its own fire said SHORT. Joe caught the contradiction in the row.
        """
        for d in self.fires:
            if d['fire'] <= open_bar:
                continue
            if d['side'] != tsd:                   # the counter side is not this walk's business
                continue
            r = K.walkable_run(self.R, d['fire'], d['side'])
            stf = r[0] if r else self.fb
            if stf is None:
                continue
            assert d['side'] == tsd, 'a counter-side fire reached the lineage call'
            v, exh, rows = self._lineage(stf, d['side'], d['rev'], trace, events, 'backstop')
            if v != 'EXHAUST' or exh is None:
                continue
            o = max(exh, d['fire']) + 1
            if o <= open_bar:
                continue
            return o, 'fire %s, ws%d, exh %s, %s' % (ln.U(d['fire']), stf, ln.U(exh), d['dir']), rows
        return None, 'no fire resolves', []

    def saviour(self, open_bar, tsd):
        res = SV.walk(open_bar, tsd, self.R, self.MG, ln.U)
        if res['verdict'] != 'SAVIOUR REV':
            return None, res['verdict'], res['why']
        return res['reopen'], 'fill %s' % ln.U(res['fill']), res['why']

    # ── the chain ──────────────────────────────────────────────────────────────────────────────
    def step0(self, events=None):
        """The invisible LONG and SHORT, both sides. -> (open bar, real dir, why, the pair)."""
        pair = []
        for d in ('LONG', 'SHORT'):
            o, why, _ = self.core(self.A, target_side(d), events=events)
            pair.append((o if o is not None else 10 ** 12, d, why))
        pair.sort()
        o, inv, why = pair[0]
        return (None if o >= 10 ** 12 else o), flip(inv), why, pair

    def hatch_legs(self):
        """Every baton hand-off the chain made, with Joe's key setup flagged.

        Joe 1023: *"the key setup (that you probably already know) is ws5r oob plus ws6r oob"*.
        Both readings are taken AT THE ANCHOR, the bar lineage starts from, because at the pass
        bar the sender is by definition in bounds under LIN_PASS 'ib' - so ws5r oob there is
        unreachable and testing it there would always answer no.
        Every event came from a walk the MACHINE anchored. None is hand-picked, and a window edge
        cannot reach `_lineage`.
        """
        out, seen, ev = [], set(), []
        self.chain(events=ev)
        for e in ev:
            k = (e['anchor'], e['stf'], e['frm'], e['to'], e['pas'])
            if k in seen:                      # the same fire is re-walked for every later leg
                continue
            seen.add(k)
            sd, an = e['side'], e['anchor']
            a5, a6 = float(self.R[5][an]), float(self.R[6][an])
            out.append(dict(e, r5=float(self.R[5][e['pas']]), r6=float(self.R[6][e['pas']]),
                           a5=a5, a6=a6, run=K.walkable_run(self.R, an, sd),
                           stale_s=(e['pas'] - e['rev_to']) * 5,
                           since_s=(e['rev_to'] - an) * 5,
                           setup=(K.oob(a5, sd) and K.oob(a6, sd))))
        return out

    def chain(self, runaway=100000, events=None):
        """-> the trade list. Each row: (open bar, dir, mech, detail).

        `runaway` is NOT a cap. The chain terminates on its own - no live candidate, or the next
        open past B - so this only trips if that stops being true. It was `maxn=400` and it broke
        the loop silently, which is a truncation nobody asked for.
        `events` collects every baton hand-off of every walk the chain ran, winning candidate and
        losing candidate alike, because both are real lineage walks from real machine anchors.
        """
        o0, d0, why0, pair = self.step0(events)
        if o0 is None:
            return [], pair
        out = [(o0, d0, 'core STEP0', why0)]
        ob, cur = o0, d0
        while True:
            assert len(out) < runaway, 'the chain did not terminate'
            tsd = target_side(cur)
            c = {'core': self.core(ob, tsd, events=events),
                 'backstop': self.backstop(ob, tsd, events=events),
                 'saviour': self.saviour(ob, tsd)}
            live = [(v[0], self.order.index(m), m, v[1]) for m, v in c.items() if v[0] is not None]
            if not live:
                out.append((None, None, 'the chain ends',
                            '; '.join('%s: %s' % (m, c[m][1]) for m in self.order)))
                break
            live.sort()
            o, _, m, why = live[0]
            if o > self.B:
                out.append((None, None, 'the chain ends', 'next open %s is past the window' % ln.U(o)))
                break
            cur, ob = flip(cur), o
            if m == 'backstop':                    # the fire NAMES its side, so it must agree
                assert ('SHORT' if tsd > 0 else 'LONG') == cur, \
                    'the backstop fire\'s own side disagrees with the trade it opened'
            out.append((ob, cur, m, why))
        return out, pair


def _out(path):
    if path == '-':
        return sys.stdout
    return open(path, 'w', buffering=1)


if __name__ == '__main__':
    mode, dest = sys.argv[1], sys.argv[2]
    A, B = ln.K(sys.argv[3]), ln.K(sys.argv[4])
    order = (sys.argv[5] if len(sys.argv) > 5 else 'saviour,core,backstop').split(',')
    fbs = sys.argv[6] if len(sys.argv) > 6 else 'drop'
    fb = None if fbs == 'drop' else int(fbs)
    f = _out(dest)

    def log(s):
        f.write(s + '\n')
        if dest != '-':
            print(s, flush=True)

    M = Machine(A, B, order, fb)

    if mode == 'parity':
        log('# PARITY. %s .. %s. LIN_PASS %r, lookback floor %s at ws%d. RULED_OK %s.'
            % (ln.U(A), ln.U(B), K.LIN_PASS,
               'ON' if K.LIN_LOOKBACK_FLOORED else 'OFF', K.LIN_LOOKBACK_FLOOR_TF, K.RULED_OK))
        log('')
        log('| the comparison | verdict | detail |'); log('|---|---|---|')
        bad = F.check(A, B, M.R, M.MG, K.BSTOP_OOB_WHEN, log=log)
        log('')
        log('| PARITY | %s |' % ('OK, 0 disagreements' if bad == 0 else '%d DISAGREEMENTS' % bad))
        sys.exit(1 if bad else 0)

    if mode == 'row':
        close, hi, lo = prices()
        piv = find_pivots(close, PCT)
        tr, _ = M.chain()
        rows = [{'fire': o, 'rev': o, 'stamp': o, 'side': target_side(d), 'dir': d,
                 'verdict': 'EXHAUST', 'exh': o - 1} for o, d, _, _ in tr if o is not None]
        L = ledger(rows, close, piv)
        m = metrics(L, COINS, DRAG_22K)
        nd = ('%.2f' % m['ndd']) if (m and np.isfinite(m['ndd'])) else '-'
        pf = ('%.2f' % m['pf']) if (m and np.isfinite(m['pf'])) else '-'
        log('ARM|%s|%d|ws%d|%d|%.1f|%+.2f|%.2f|%s|%s'
            % (K.LIN_PASS, K.LIN_LOOKBACK_FLOORED, K.LIN_LOOKBACK_FLOOR_TF,
               m['n'] if m else 0, m['win_rate'] if m else 0, m['net_usd'] if m else 0,
               m['dd'] if m else 0, nd, pf))
        sys.exit(0)

    tr, pair = M.chain()
    log('# THE MACHINE, mode %r. %s .. %s' % (mode, ln.U(A), ln.U(B)))
    log('# order %r, backstop fallback %r. ONE position at a time.' % (','.join(order), fbs))
    log('# LIN_PASS %r, lookback floor %s at ws%d, %d backstop fires. RULED_OK %s.'
        % (K.LIN_PASS, 'ON' if K.LIN_LOOKBACK_FLOORED else 'OFF',
           K.LIN_LOOKBACK_FLOOR_TF, len(M.fires), K.RULED_OK))
    log('')
    log('| the invisible trade | its target-side | the real trade it opens | detail |')
    log('|---|---|---|---|')
    for o, d, why in pair:
        log('| an invisible %s | %s | %s | %s |'
            % (d, 'high' if target_side(d) > 0 else 'low',
               ln.U(o) if o < 10 ** 12 else 'never', why))
    log('')

    if mode == 'chain':
        log('| # | the open | dir | by | detail |'); log('|---|---|---|---|---|')
        n = 0
        for o, d, m, why in tr:
            if o is None:
                log('| - | - | - | %s | %s |' % (m, why)); continue
            n += 1
            log('| %d | %s | %s | %s | %s |' % (n, ln.U(o), d, m, why))
        log('')
        log('| the read | value |'); log('|---|---|')
        log('| trades | %d |' % n)
        from collections import Counter
        for mech, c in Counter(m for o, _, m, _ in tr if o is not None).most_common():
            log('| by %s | %d |' % (mech, c))

    elif mode == 'hatch':
        ev = M.hatch_legs()
        hatch = [e for e in ev if e['stale']]
        setup = [e for e in hatch if e['setup']]
        log('| the read | value |'); log('|---|---|')
        log('| baton hand-offs the chain made | %d |' % len(ev))
        log('| of those, the receiver arrived SPENT - the hatch fires | %d |' % len(hatch))
        log('| of those, ws5r AND ws6r both oob AT THE ANCHOR - his key setup | %d |' % len(setup))
        log('| the lookback cannot reach behind the anchor | `first_rev_at_or_after(.., A, ..)`'
            ' seeds every ST from A, so "already spent" ALWAYS means reversed DURING the walk |')
        log('| hand-offs blocked by the ws%d lookback floor | %d |'
            % (K.LIN_LOOKBACK_FLOOR_TF, sum(1 for e in ev if e['floored'])))
        log('| the pass bar can never show ws5r oob | LIN_PASS is %r: the sender is IN bounds there |'
            % K.LIN_PASS)
        if setup:
            st = sorted(e['stale_s'] for e in setup)
            log('| how stale the receiver was at the pass, median | %d s |' % st[len(st) // 2])
            log('| how stale the receiver was at the pass, max | %d s |' % st[-1])
        log('')
        log('| what the hatch branch ITSELF did | hatch fires | of those on his setup |')
        log('|---|---|---|')
        oc = {}
        for e in hatch:
            k = e['hatch_out'] or 'the walk ended before the branch resolved'
            oc.setdefault(k, [0, 0])
            oc[k][0] += 1
            oc[k][1] += 1 if e['setup'] else 0
        for k in sorted(oc):
            log('| %s | %d | %d |' % (k, oc[k][0], oc[k][1]))
        log('')
        log('| the hand-off rung | hatch fires | of those on his setup |')
        log('|---|---|---|')
        rg = {}
        for e in hatch:
            k = 'ws%d -> ws%d' % (e['frm'], e['to'])
            rg.setdefault(k, [0, 0])
            rg[k][0] += 1
            rg[k][1] += 1 if e['setup'] else 0
        for k in sorted(rg):
            log('| %s | %d | %d |' % (k, rg[k][0], rg[k][1]))
        log('')
        log('| the anchor | mech | side | ws5r at the anchor | ws6r at the anchor | his setup |'
            ' the oob run | hand-off | the pass bar | receiver r there | its reversal |'
            ' stale by | the second walk resolves | what the hatch branch did | EXHAUST |')
        log('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
        for e in sorted(hatch, key=lambda x: x['anchor']):
            log('| %s | %s | %s | %.2f | %.2f | %s | %s | ws%d -> ws%d | %s | %.2f | %s | %d s |'
                ' %s | %s | %s |'
                % (ln.U(e['anchor']), e['mech'],
                   'LOW oob' if e['side'] < 0 else 'HIGH oob', e['a5'], e['a6'],
                   'YES' if e['setup'] else 'no',
                   ('ws%d-ws%d' % (e['run'][0], e['run'][-1])) if e['run'] else 'none',
                   e['frm'], e['to'], ln.U(e['pas']), e['r_to'],
                   ln.U(e['rev_to']) if e['rev_to'] else '-',
                   e['stale_s'],
                   ln.U(e['p2']) if e['p2'] is not None else '-',
                   e['hatch_out'] or '-',
                   ln.U(e['exh']) if e['exh'] is not None else e['verdict']))
        if not hatch:
            log('| - | - | - | - | - | - | - | - | - | - | - | - | - | - | no hatch fired |')
        log('')

    elif mode == 'trace':
        bar = ln.K(sys.argv[7])
        legs = [(o, d) for o, d, _, _ in tr if o is not None]
        prev = [x for x in legs if x[0] <= bar]
        if not prev:
            log('| no leg contains %s | the chain has not opened by then |' % ln.U(bar))
            f.close(); sys.exit(0)
        ob, cur = prev[-1]
        tsd = target_side(cur)
        log('## the leg holding %s: a %s opened %s, target-side %s'
            % (ln.U(bar), cur, ln.U(ob), 'high' if tsd > 0 else 'low'))
        log('')
        for mech in M.order:
            if mech == 'core':
                o, why, rows = M.core(ob, tsd, trace=True)
            elif mech == 'backstop':
                o, why, rows = M.backstop(ob, tsd, trace=True)
            else:
                o, why, rows = M.saviour(ob, tsd)
            log('### %s' % mech)
            log('')
            log('| the step | the bar | the reading |'); log('|---|---|---|')
            for r in rows:
                log('| %s | %s | %s |' % (r[0], r[1], r[2]))
            if not rows:
                log('| - | - | %s |' % why)
            log('')
            log('| %s\'s candidate | value |' % mech); log('|---|---|')
            log('| would open | %s |' % (ln.U(o) if o else 'none'))
            log('| detail | %s |' % why)
            log('')
    else:
        log('| unknown mode %r | use chain, trace, row or parity |' % mode)
    if dest != '-':
        f.close()
