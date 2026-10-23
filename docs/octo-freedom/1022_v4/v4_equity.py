"""The per-trade ledger and the day-by-day account, banked r-config only.

Joe 1022: *"what would the account be now if it started at USDT500? show the day-by-day updates"*.

THE EXIT IS JOE'S, 1022: *"exit:  90% of MFE"*, with the -1.100% pseudo stop beside it.

THE ORDER OF THE TWO EXITS IS MINE AND STATED. v4_net.py booked a stop whenever the segment's
minimum reached -CAP, regardless of WHEN. A trade that ran to +3% and then fell to -1.2% before
its pivot was booked at -1.100%, although the 90%-of-MFE exit would already have fired. Here the
two rules are read in BAR ORDER:
    level = 0.90 x MFE over the segment
    the 90% bar = the first bar the move reaches `level`
    the stop bar = the first bar the move reaches -CAP
    whichever bar comes FIRST is the exit
Both readings are reported so the move is visible.

THE 90% LEVEL STILL NEEDS THE MFE, WHICH IS ONLY KNOWN AFTERWARDS. The ordering repairs an
inconsistency; it does not make the exit causal. This is still a SCORED ledger.

THE ACCOUNT. One knob is missing and it is Joe's: the notional per trade. This file reports
    - the day-by-day sum of net %, which needs no size at all
    - the concurrency, which is what decides whether a size is even spendable
and it compounds at NOTIONAL_MULT x equity per trade, which is a placeholder, not a ruling.

usage: v4_equity.py <out.md>
"""
import sys
import io
import os
import datetime as dt
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
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.swing_detect import find_pivots
sys.stderr = _e

PCT, CAP = 2.0, 1.1
CAPTURE = 0.90
DRAG = 0.1770                    # taker/taker round trip: 0.110 fee + 0.067 slip
DRAG_22K = 0.1975                # the banked conservative: (5.50 fee + 4.375 slip) x 2 legs,
#                                  which is the figure measured AT 22,000 coins
COINS = 22000.0                  # Joe 1023: *"I'm assuming no leverage and 22K coins"*
START = 500.0                    # Joe 1022: USDT 500


def ledger(acc, close, piv):
    """-> one row per trade, with BOTH exit readings. Chronological by entry.

    THREE BARS PER ROW, 1023. Every row carries
        info   the bar the trade is KNOWABLE on: max(the backstop fire, the lineage confirm bar)
        en     the entry bar, which is info + 1 and nothing else
        xb     the scoring bar, where the exit rule lands
    and `assert info < en` carries the claim instead of a comment. The entry used to be
    `exh + 1` alone, which opened 36 of 356 trades at or before the backstop fire that signalled
    them - the fire waits for the oob pool and can land after the reversal the walk starts from.
    max(), never a swap.
    """
    out = []
    for r in acc:
        info = max(int(r['exh']), int(r['fire']))
        en = info + 1
        assert info < en, 'the entry bar is not after the information bar'
        assert en > int(r['fire']), 'the trade opens at or before its own backstop fire'
        assert en > int(r['stamp']), 'the trade opens at or before its own reversal stamp'
        if en >= len(close):
            continue
        d = 1 if r['dir'] == 'LONG' else -1
        fav = 'H' if d > 0 else 'L'
        nxt = next((pi for pi, pk in piv if pi > en and pk == fav), None)
        p0 = float(close[en])
        if p0 <= 0:
            continue
        hiB = (nxt + 1) if nxt is not None else len(close)
        dd = (np.asarray(close[en:hiB], float) - p0) / p0 * 100.0 * d
        mfe = float(dd.max())
        level = CAPTURE * mfe
        b90 = int(np.argmax(dd >= level)) if (dd >= level).any() and level > 0 else None
        bst = int(np.argmax(dd <= -CAP)) if (dd <= -CAP).any() else None
        # the unordered reading, exactly as v4_net.py booked it
        un_g = -CAP if float(dd.min()) <= -CAP else level
        # the bar-ordered reading
        if bst is not None and (b90 is None or bst < b90):
            od_g, xb, why = -CAP, en + bst, 'STOP'
        elif b90 is not None:
            od_g, xb, why = level, en + b90, '90%MFE'
        else:
            od_g, xb, why = float(dd[-1]), hiB - 1, 'PIVOT'
        # the pivot-close exit, read in bar order against the same stop
        pv_g = -CAP if bst is not None else float(dd[-1])
        out.append({'en': en, 'info': info, 'fire': int(r['fire']), 'stamp': int(r['stamp']),
                    'exh': int(r['exh']),
                    'xb': xb, 'dir': r['dir'], 'px': p0, 'mfe': mfe,
                    'mae': float(dd.min()),
                    'why': why, 'un_g': un_g, 'od_g': od_g, 'pv_g': pv_g,
                    'un_n': un_g - DRAG, 'od_n': od_g - DRAG, 'pv_n': pv_g - DRAG,
                    'mfe_n': (-CAP if bst is not None and (b90 is None or bst < b90)
                              else mfe) - DRAG})
    return out


def cap_pyramid(L, mx):
    """The rows that survive a max_pyramid of `mx`. -> rows, in entry order.

    A trade that would be the (mx+1)th open position is NOT opened. `None` keeps everything and
    applies no cap. JOE'S KNOB AND JOE'S NUMBER - K.MAX_PYRAMID, banked at 2 on 1023 - so the
    value is never chosen here.

    CAUSAL: the decision at a trade's entry bar reads only the exit bars of positions already
    open, which are in the past or are the open positions themselves.
    """
    if mx is None:
        return list(L)
    out, open_until = [], []
    for r in sorted(L, key=lambda q: q['en']):
        open_until = [x for x in open_until if x >= r['en']]
        if len(open_until) >= int(mx):
            continue
        out.append(r)
        open_until.append(r['xb'])
    return out


def concurrency(rows):
    """-> (max open at once, the bar it peaks on)."""
    ev = []
    for r in rows:
        ev.append((r['en'], +1)); ev.append((r['xb'] + 1, -1))
    ev.sort()
    cur, mx, mb = 0, 0, None
    for b, s in ev:
        cur += s
        if cur > mx:
            mx, mb = cur, b
    return mx, mb


def peak_notional(rows, coins):
    """The most USDT held in open positions at once. NO LEVERAGE means the account must cover it.

    Each open position's size is `coins` bought at that trade's own entry price, so the figure is
    the sum of the open entry notionals, walked bar by bar over the entry/exit events.
    """
    ev = []
    for r in rows:
        v = coins * r['px']
        ev.append((r['en'], +v)); ev.append((r['xb'] + 1, -v))
    ev.sort()
    cur, mx, mb = 0.0, 0.0, None
    for b, v in ev:
        cur += v
        if cur > mx:
            mx, mb = cur, b
    return mx, mb


if __name__ == '__main__':
    out = open(sys.argv[1], 'w', buffering=1)

    def log(s):
        out.write(s + '\n'); print(s, flush=True)

    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    piv = find_pivots(close, PCT)
    A, B = 0, ln.N - 1
    trip = (RS.K0, RS.R0, RS.S0)
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
    acc = DT.accept(rows)
    L = ledger(acc, close, piv)
    mx, mb = concurrency(L)

    log('# the LEDGER and the DAY-BY-DAY ACCOUNT. banked r-config k%d rsi%d stc%d.' % trip)
    log('# the full tape, %d bars = %.0f days. %d pivots at %.1f%%.' % (ln.N, ln.N * 5 / 86400.0,
                                                                        len(piv), PCT))
    log('# THE EXIT, Joe 1022: a stopped trade at -%.3f%%, a positive at %.0f%% of its MFE.' %
        (CAP, CAPTURE * 100))
    log('# drag %.4f%% per round trip, taker/taker. start USDT %.2f.' % (DRAG, START))
    log('# MAX CONCURRENT OPEN TRADES %d, first reached at bar %d = %s'
        % (mx, mb, ln.U(min(mb, ln.N - 1))))
    log('')

    # ── the two exit readings, side by side ──────────────────────────────────────────────────
    un = np.array([r['un_n'] for r in L]); od = np.array([r['od_n'] for r in L])
    log('| reading | trades | stopped | sum net % | per trade net % |')
    log('|---|---|---|---|---|')
    log('| the stop wins whenever it is touched (v4_net.py) | %d | %d | %+.2f | %+.4f |'
        % (len(L), sum(1 for r in L if r['un_g'] == -CAP), un.sum(), un.mean()))
    log('| the two exits read in bar order | %d | %d | %+.2f | %+.4f |'
        % (len(L), sum(1 for r in L if r['why'] == 'STOP'), od.sum(), od.mean()))
    log('')
    log('# WHAT THE FORESIGHT IS WORTH. the same trades, the same stop, three exits.')
    log('# THE -%.3f%% STOP IS THE ONLY CAUSAL LEG. all three win-side rules need the pivot,'
        % CAP)
    log('#   and a %.1f%% pivot is only confirmed once price has retraced %.1f%% off it.'
        % (PCT, PCT))
    pv = np.array([r['pv_n'] for r in L]); mf = np.array([r['mfe_n'] for r in L])
    log('| exit rule | what it must know in advance | trades | stopped | sum net % | '
        'per trade net % |')
    log('|---|---|---|---|---|---|')
    log('| the next favourable 2%% pivot close | that the bar IS the pivot | %d | %d | %+.2f | '
        '%+.4f |'
        % (len(L), sum(1 for r in L if r['pv_g'] == -CAP), pv.sum(), pv.mean()))
    log('| 90%% of MFE, Joe 1022 | the whole excursion | %d | %d | %+.2f | %+.4f |'
        % (len(L), sum(1 for r in L if r['why'] == 'STOP'), od.sum(), od.mean()))
    log('| 100%% of MFE, the ceiling | the whole excursion | %d | %d | %+.2f | %+.4f |'
        % (len(L), sum(1 for r in L if r['why'] == 'STOP'), mf.sum(), mf.mean()))
    log('')
    log('# THE EXIT THAT FIRED, bar-ordered reading.')
    log('| why | trades |')
    log('|---|---|')
    for w in ('STOP', '90%MFE', 'PIVOT'):
        log('| %s | %d |' % (w, sum(1 for r in L if r['why'] == w)))
    log('')

    # ── the day-by-day ──────────────────────────────────────────────────────────────────────
    days = {}
    for r in L:
        k = ln.U(r['xb'])[:10]
        g = days.setdefault(k, {'n': 0, 'st': 0, 'un': 0.0, 'od': 0.0, 'op': 0})
        g['n'] += 1; g['un'] += r['un_n']; g['od'] += r['od_n']
        g['st'] += 1 if r['why'] == 'STOP' else 0
    for r in L:
        days.setdefault(ln.U(r['en'])[:10], {'n': 0, 'st': 0, 'un': 0.0, 'od': 0.0, 'op': 0})
        days[ln.U(r['en'])[:10]]['op'] += 1

    log('| date | opened | exited | stopped | day net % ordered | day net % v4_net | '
        'equity USDT at 1.0x | equity USDT at 0.5x | equity USDT at 0.25x |')
    log('|---|---|---|---|---|---|---|---|---|')
    MULTS = (1.0, 0.5, 0.25)
    eq = {m: START for m in MULTS}
    byx = sorted(L, key=lambda r: r['xb'])          # compound in EXIT order
    i = 0
    for k in sorted(days):
        g = days[k]
        while i < len(byx) and ln.U(byx[i]['xb'])[:10] == k:
            for m in MULTS:
                eq[m] *= (1.0 + m * byx[i]['od_n'] / 100.0)
            i += 1
        log('| %s | %d | %d | %d | %+.3f | %+.3f | %.2f | %.2f | %.2f |'
            % (k, g['op'], g['n'], g['st'], g['od'], g['un'], eq[1.0], eq[0.5], eq[0.25]))
    log('')
    log('| start USDT | notional per trade | final equity USDT | multiple |')
    log('|---|---|---|---|')
    for m in MULTS:
        log('| %.2f | %.2fx equity | %.2f | %.1fx |' % (START, m, eq[m], eq[m] / START))

    # ── Joe 1023: no leverage, 22,000 coins a trade ─────────────────────────────────────────
    pk, pb = peak_notional(L, COINS)
    px = np.array([r['px'] for r in L])
    log('')
    log('# FIXED SIZE, Joe 1023: *"I\'m assuming no leverage and 22K coins"*.')
    log('# the size is %d coins a trade, bought at that trade\'s own entry price.' % COINS)
    log('# drag %.4f%% - the banked conservative figure, which is the one measured AT %d coins.'
        % (DRAG_22K, COINS))
    log('')
    log('| item | value |')
    log('|---|---|')
    log('| %d coins at the cheapest entry %.6f | USDT %.2f |' % (COINS, px.min(),
                                                                 COINS * px.min()))
    log('| %d coins at the mean entry %.6f | USDT %.2f |' % (COINS, px.mean(),
                                                             COINS * px.mean()))
    log('| %d coins at the dearest entry %.6f | USDT %.2f |' % (COINS, px.max(),
                                                                COINS * px.max()))
    log('| max concurrent open trades | %d |' % mx)
    log('| PEAK OPEN NOTIONAL, all open trades at once | USDT %.2f |' % pk)
    log('| the bar it peaks on | %s |' % ln.U(min(pb, ln.N - 1)))
    log('| THE CAPITAL FLOOR, no leverage | USDT %.2f |' % pk)
    log('| Joe\'s start | USDT %.2f |' % START)
    log('| the start as a fraction of the floor | %.3f |' % (START / pk))
    log('')

    # the USDT stream. NO TRADE IS DROPPED - the underfunded ones are flagged, not skipped.
    byx2 = sorted(L, key=lambda r: r['xb'])
    for r in L:
        r['notional'] = COINS * r['px']
        r['g_usd'] = (r['od_g'] / 100.0) * r['notional']
        r['d_usd'] = (DRAG_22K / 100.0) * r['notional']
        r['n_usd'] = r['g_usd'] - r['d_usd']
    tot_g = sum(r['g_usd'] for r in L)
    tot_d = sum(r['d_usd'] for r in L)
    log('| item | value |')
    log('|---|---|')
    log('| trades | %d |' % len(L))
    log('| gross USDT | %+.2f |' % tot_g)
    log('| drag USDT | %.2f |' % tot_d)
    log('| drag as %% of gross | %.1f |' % (100.0 * tot_d / tot_g))
    log('| net USDT | %+.2f |' % (tot_g - tot_d))
    log('| net USDT per trade | %+.2f |' % ((tot_g - tot_d) / len(L)))
    log('| equity from the floor USDT %.2f | %.2f |' % (pk, pk + tot_g - tot_d))
    log('| multiple on the floor | %.2fx |' % ((pk + tot_g - tot_d) / pk))
    log('')
    log('| date | opened | exited | stopped | day gross USDT | day drag USDT | day net USDT | '
        'equity from the floor USDT | equity from USDT 500 |')
    log('|---|---|---|---|---|---|---|---|---|')
    e_fl, e_500 = pk, START
    j = 0
    for k in sorted(days):
        g = days[k]
        dg = dd_ = 0.0
        while j < len(byx2) and ln.U(byx2[j]['xb'])[:10] == k:
            dg += byx2[j]['g_usd']; dd_ += byx2[j]['d_usd']
            j += 1
        e_fl += dg - dd_; e_500 += dg - dd_
        log('| %s | %d | %d | %d | %+.2f | %.2f | %+.2f | %.2f | %.2f |'
            % (k, g['op'], g['n'], g['st'], dg, dd_, dg - dd_, e_fl, e_500))
    out.close()
