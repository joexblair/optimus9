"""The 500 / 22K / leveraged account, with the hold-out split and max_pyramid reported per level.

Joe 1023: *"choose your top 3 sweep centroids (net based) and compare all 4 summary results of
our 500/22k/leveraged account"*, then *"let's see how that plays out. if hedging is profitable and
causal, I'm not against it. it will need a safe max_pyramid setting that only the account
(leverage) can provide"*.

THE HOLD-OUT IS NOW APPLIED, AND IT HAD TO BE. The 1023 audit found this file selecting its three
configs from the full-tape no-hold-out measurement that `v4_rcfg_sweep.py:20` forbids selecting
from: *"No config may be selected from it."* So the centroids are ranked on the SWEEP half alone
and the hold-out half is reported beside them, never ranked on.
    sweep     2026-07-02 12:00:00 .. 2026-08-31 23:59:55
    hold-out  2026-09-01 00:00:00 .. the tape end
A trade belongs to the half its ENTRY bar falls in.

WHAT `centroid` MEANS HERE, AND IT IS A CHOICE. The sweep is a 3x3x3 grid in (k, rsi, stc). A
centroid scores as the MEAN SWEEP NET of the config and the cells one step away in exactly one
parameter, so a cell wins on its region rather than on being a lone peak. Neighbour counts differ
at the grid edge, and the mean is over whatever exists.

THE ACCOUNT. Start USDT 500, a fixed 22,000 coins a trade, leverage taken as an OUTPUT.
    the size does not compound   22,000 coins at that trade's own entry price
    the leverage is reported     open notional / equity at that moment, and its max
    exits settle before entries  within one bar, so a freed position funds the next
    the release is the EXIT      the position is closed at its exit value, not its entry notional
NO LIQUIDATION MODEL EXISTS. `blown` counts the exits that take equity to zero or below and is
PRINTED, because the 1023 audit found it computed and discarded.

`max_pyramid` IS JOE'S KNOB AND IS BANKED AT 2, 1023: *"including 2 max_pyramid"*. The headline
account table runs at the banked value; every level is still reported beside it, UNLIMITED
included, because that is the leverage curve he sets the number from.

usage: v4_accounts.py <out.md>
"""
import sys
import io
import os
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
import v4_knobs as K
import v4_fast as F
import v4_deferred_trades as DT
import v4_rcfg_sweep as RS
from v4_equity import (ledger, concurrency, peak_notional, cap_pyramid,
                        CAPTURE, PCT, CAP, COINS, START)
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.swing_detect import find_pivots
sys.stderr = _e

DRAGS = (('0.1100', 0.1100), ('0.1770', 0.1770), ('0.1975', 0.1975))
RANK_DRAG = 0.1975               # the figure measured AT 22,000 coins
SPLIT_TS = '2026-09-01 00:00:00'
PYRAMIDS = (1, 2, 3, 4, 5, 6, None)      # None = UNLIMITED, the default


def halves(L, split):
    """-> (sweep rows, hold-out rows), split on the ENTRY bar."""
    return [r for r in L if r['en'] < split], [r for r in L if r['en'] >= split]


def net_pct(rows, drag):
    """-> (trades, stopped, gross %, drag %, net %)"""
    n = len(rows)
    g = sum(r['od_g'] for r in rows)
    return n, sum(1 for r in rows if r['why'] == 'STOP'), g, n * drag, g - n * drag


def account(L, coins, start, drag):
    """The 500 / 22K / leveraged walk. -> a dict of the summary figures.

    Events are (bar, kind): an EXIT settles before an ENTRY on the same bar, so a position that
    closes frees its capital for the one that opens. The release is the position's EXIT value.
    """
    ev = []
    for i, r in enumerate(L):
        ev.append((r['xb'] + 1, 0, i))          # 0 sorts before 1: exits first
        ev.append((r['en'], 1, i))
    ev.sort()
    eq, opn, mx_lev, mx_lev_bar, mn_eq, blown = start, 0.0, 0.0, None, start, 0
    for b, kind, i in ev:
        r = L[i]
        notl = coins * r['px']
        if kind == 0:
            pnl = (r['od_g'] / 100.0) * notl
            cost = (drag / 100.0) * notl
            opn -= (notl + pnl)                 # the EXIT value, not the entry notional
            eq += pnl - cost
            mn_eq = min(mn_eq, eq)
            if eq <= 0:
                blown += 1
        else:
            opn += notl
            if eq > 0 and opn / eq > mx_lev:
                mx_lev, mx_lev_bar = opn / eq, b
    g = sum((r['od_g'] / 100.0) * coins * r['px'] for r in L)
    d = sum((drag / 100.0) * coins * r['px'] for r in L)
    pk, pb = peak_notional(L, coins)
    mc, mcb = concurrency(L)
    return {'trades': len(L), 'stopped': sum(1 for r in L if r['why'] == 'STOP'),
            'gross': g, 'drag': d, 'net': g - d, 'final': start + g - d,
            'mult': (start + g - d) / start, 'peak_notional': pk, 'peak_bar': pb,
            'max_conc': mc, 'max_lev': mx_lev, 'max_lev_bar': mx_lev_bar,
            'min_eq': mn_eq, 'blown': blown}


def neighbours(trip, all_trips):
    """The cells one step away in exactly one parameter. -> a list of trips."""
    out = []
    for j in range(3):
        for d in (-1, +1):
            t = list(trip); t[j] += d; t = tuple(t)
            if t in all_trips:
                out.append(t)
    return out


if __name__ == '__main__':
    out = open(sys.argv[1], 'w', buffering=1)

    def log(s):
        out.write(s + '\n'); print(s, flush=True)

    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    piv = find_pivots(close, PCT)
    A, B = 0, ln.N - 1
    SPLIT = ln.K(SPLIT_TS)
    banked = (RS.K0, RS.R0, RS.S0)
    trips = list(RS.cfgs())
    tset = set(trips)

    log('# THE 500 / 22K / LEVERAGED ACCOUNT, hold-out applied. the full tape, %d bars = %.0f days.'
        % (ln.N, ln.N * 5 / 86400.0))
    log('# THE 1023 CAUSALITY REPAIR IS IN: reversals act on their stamp, the ib dwell acts on its')
    log('#   confirm bar, a receiver with no reversal in the data is NO REVERSAL not EXHAUST, and')
    log('#   the entry bar is max(the backstop fire, the lineage confirm) + 1.')
    log('# THE EXIT, Joe 1022: a stopped trade at -%.3f%%, a positive at %.0f%% of its MFE, read in'
        % (CAP, CAPTURE * 100))
    log('#   BAR ORDER, on CLOSE only - Joe 1023: *"the only option we have is `close`"*.')
    log('# THE SIZE, Joe 1023: %d coins a trade, no compounding, start USDT %.2f, drag %.4f%%.'
        % (COINS, START, RANK_DRAG))
    log('# THE SPLIT: sweep %s .. %s, hold-out %s .. %s. Ranked on the SWEEP half ONLY.'
        % (ln.U(0), ln.U(SPLIT - 1), ln.U(SPLIT), ln.U(B)))
    log('')

    t0 = time.time()
    L_by, sw_by, ho_by = {}, {}, {}
    log('| k | rsi | stc | sweep trades | sweep stopped | sweep NET %% | hold-out trades | '
        'hold-out stopped | hold-out NET %% | full trades | full NET %% |')
    log('|---|---|---|---|---|---|---|---|---|---|---|')
    for i, trip in enumerate(trips, 1):
        R = RS.load(trip)
        F.reset()
        f = F.scan(A, B, R, MG, 'window')
        rows = []
        for d in f:
            v, bar = F.walk(R, 5, d['side'], d['rev'], B)
            un = (v == 'EXHAUST' and bar is not None and bar >= B - 1)
            rows.append({'fire': d['fire'], 'rev': d['rev'], 'stamp': d['stamp'],
                         'side': d['side'], 'dir': d['dir'],
                         'verdict': 'UNRESOLVED' if un else v, 'exh': None if un else bar})
        L = ledger(DT.accept(rows), close, piv)
        L_by[trip] = L
        sw, ho = halves(L, SPLIT)
        sw_by[trip], ho_by[trip] = sw, ho
        a = net_pct(sw, RANK_DRAG); b = net_pct(ho, RANK_DRAG); c = net_pct(L, RANK_DRAG)
        mark = ' <- BANKED' if trip == banked else ''
        log('| %d | %d | %d%s | %d | %d | %+.2f | %d | %d | %+.2f | %d | %+.2f |'
            % (trip[0], trip[1], trip[2], mark, a[0], a[1], a[4], b[0], b[1], b[4], c[0], c[4]))
        print('# arm %d of %d, %.0f s' % (i, len(trips), time.time() - t0), flush=True)
    log('')

    cent = {}
    sweep_net = {t: net_pct(sw_by[t], RANK_DRAG)[4] for t in trips}
    for trip in trips:
        vals = [sweep_net[trip]] + [sweep_net[t] for t in neighbours(trip, tset)]
        cent[trip] = float(np.mean(vals))
    log('# THE CENTROID SCORE: the mean SWEEP-half NET of the config and its one-step neighbours.')
    log('')
    log('| k | rsi | stc | own sweep NET %% | neighbours | centroid mean sweep NET %% |')
    log('|---|---|---|---|---|---|')
    for trip in trips:
        mark = ' <- BANKED' if trip == banked else ''
        log('| %d | %d | %d%s | %+.2f | %d | %+.2f |'
            % (trip[0], trip[1], trip[2], mark, sweep_net[trip],
               len(neighbours(trip, tset)), cent[trip]))
    log('')

    top3 = [t for t in sorted(cent, key=lambda t: -cent[t]) if t != banked][:3]
    picks = [banked] + top3
    log('# THE 4 CONFIGS. the banked one, then the top 3 centroids BY THE SWEEP HALF.')
    log('')
    log('| config | role | centroid mean sweep NET %% | own sweep NET %% | own hold-out NET %% |')
    log('|---|---|---|---|---|')
    for trip in picks:
        role = 'BANKED' if trip == banked else 'centroid %d' % (top3.index(trip) + 1)
        log('| k%d rsi%d stc%d | %s | %+.2f | %+.2f | %+.2f |'
            % (trip[0], trip[1], trip[2], role, cent[trip], sweep_net[trip],
               net_pct(ho_by[trip], RANK_DRAG)[4]))
    log('')

    log('# THE ACCOUNT at the BANKED max_pyramid %d. the full tape, hold-out half as the tail.'
        % K.MAX_PYRAMID)
    log('')
    log('| config | trades | stopped | stop rate %% | gross USDT | drag USDT | net USDT | '
        'final equity USDT | multiple on 500 | peak open notional USDT | max concurrent | '
        'peak leverage x | lowest equity USDT | blown |')
    log('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for trip in picks:
        a = account(cap_pyramid(L_by[trip], K.MAX_PYRAMID), COINS, START, RANK_DRAG)
        log('| k%d rsi%d stc%d | %d | %d | %.1f | %+.2f | %.2f | %+.2f | %.2f | %.2fx | %.2f | '
            '%d | %.1f | %.2f | %d |'
            % (trip[0], trip[1], trip[2], a['trades'], a['stopped'],
               100.0 * a['stopped'] / max(1, a['trades']), a['gross'], a['drag'], a['net'],
               a['final'], a['mult'], a['peak_notional'], a['max_conc'], a['max_lev'],
               a['min_eq'], a['blown']))
    log('')

    log('# MAX_PYRAMID PER LEVEL, Joe 1023. BANKED at %d; UNLIMITED applies no cap.'
        % K.MAX_PYRAMID)
    log('')
    log('| config | max_pyramid | trades | net USDT | peak open notional USDT | peak leverage x | '
        'lowest equity USDT | blown |')
    log('|---|---|---|---|---|---|---|---|')
    for trip in picks:
        for mx in PYRAMIDS:
            rows = cap_pyramid(L_by[trip], mx)
            if not rows:
                continue
            a = account(rows, COINS, START, RANK_DRAG)
            log('| k%d rsi%d stc%d | %s | %d | %+.2f | %.2f | %.1f | %.2f | %d |'
                % (trip[0], trip[1], trip[2], 'UNLIMITED' if mx is None else str(mx),
                   a['trades'], a['net'], a['peak_notional'], a['max_lev'], a['min_eq'],
                   a['blown']))
    log('')
    log('| config | the bar peak notional lands on | the bar peak leverage lands on |')
    log('|---|---|---|')
    for trip in picks:
        a = account(cap_pyramid(L_by[trip], K.MAX_PYRAMID), COINS, START, RANK_DRAG)
        log('| k%d rsi%d stc%d | %s | %s |'
            % (trip[0], trip[1], trip[2], ln.U(min(a['peak_bar'], ln.N - 1)),
               ln.U(min(a['max_lev_bar'], ln.N - 1))))
    log('# took %.0f s' % (time.time() - t0))
    out.close()
