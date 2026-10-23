"""Confluence: do the ws13r-ws30r trajectories separate the winners from the stopped-out trades?

Joe 1022: *"for each lineage open timestamp, scan all of the ws{13-30}r lines and find the cluster
of TFs that mostly match their `r` trajectory with the positive trades"* / *"to make this a proper
confluence test, we need a pseudo "stop": if MAE >=1.1, cap the MAE at 1.1 and set MFE to zero"*.
Joe 1023: *"we landed on the sweep because we wanted to find confluence for the backstop trades,
in an attempt to increase the win rate"* / *"it would be good to see both, and also a third target
that balances the net and win rate"*.

THE CLUSTER IS PICKED ON THE SWEEP HALF AND SCORED ON THE HOLD-OUT HALF. The first pass picked
ws18-ws23 from the very trades it then scored, and reported a 65% -> 80% lift on FIVE trades. That
is the same defect the 1023 audit found in the config pick, and it is why the split is now
enforced here rather than mentioned.
    sweep     2026-07-02 12:00:00 .. 2026-08-31 23:59:55
    hold-out  2026-09-01 00:00:00 .. the tape end
A trade belongs to the half its ENTRY bar falls in.

THE FIVE COLUMNS PER CELL, Joe 1023. `net / worst drawdown` is the third target and the reason is
his own question about leverage: it rises when wins get bigger OR when the loss path gets
shallower, so it balances the two without me weighting them.
    trades            the episode count. No rate is printed without it
    win rate          net-positive trades after drag, over trades
    net               USDT at 22,000 coins, and net %
    net / worst DD    the third target
    profit factor     sum of winners / |sum of losers|, path-independent
    worst losing run  consecutive losers and what the run cost - the number max_pyramid survives

THE PSEUDO STOP IS HIS and lives in v4_equity.ledger now, as the -1.100% leg of the bar-ordered
exit. There is one copy of the exit rule and this file does not own another.

THE PRODUCER IS Joe 0924's `rule2_trajectory.trajectory`. ITS WIDTH IS v4's AND PER-TF:
`TRAJ_WIDTH` 21 bars per TF-minute, so the block is 1.75 of each line's OWN bar. Joe 0924's fixed
block of 60 bars was 0.38 of a ws13 bar and 0.17 of a ws30 bar - the walk was measuring inside a
single candle of the line it was measuring, which he spotted: *"we're using the same small-sized
sampling across the board.  for every DTF line, that's less than half a TF bar"*.

THE TWO HELD KNOBS COME DUE HERE. Joe 1022: *"keep 'I swept the block only. min_bars has its own
optimum and I have not looked for it' up your sleeve - we can add it after the first pass at the
trade list"*. `TRAJ_MIN_FRAC` and `TRAJ_MIN_TRAVEL` are swept, and both only gate the FINAL test -
`opposed_extrema` depends on the block alone - so one producer call per (trade, TF) serves every
combination.

ITS dr IS THE LINE'S DIRECTION, NOT THE TRADE FRAME. The producer's own docstring: *"dr +1 -> the
block minimum"*, so dr +1 is a line travelling UP. A LONG passes +1 and a SHORT -1. That is the
opposite of the banked trade frame where dr -1 = LONG, and conflating the two is a known trap.

CAUSAL. `trajectory` reads strictly before the bar, and the bar is the trade's entry. Nothing here
reads forward of a trade's own entry. The SCORING is forward by construction and is stage two.

usage: v4_confluence.py <out.md>
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
from v4_equity import ledger, cap_pyramid, PCT, CAP, COINS, START, DRAG_22K
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.rule2_trajectory import opposed_extrema
from optimus9.compute.swing_detect import find_pivots
sys.stderr = _e

TF_LO, TF_HI = 13, 30
SPLIT_TS = '2026-09-01 00:00:00'
FRACS = (0.25, 0.5, 0.75, 1.0)            # TRAJ_MIN_FRAC, held at 0.5
TRAVELS = (0.0, 2.0, 5.0, 10.0)           # TRAJ_MIN_TRAVEL, held at 0.0
MIN_N = 20                                # cells below this episode count are printed, not ranked


def raw_traj(rows, RR):
    """opposed_extrema once per (trade, TF). -> rows with 'bars' and 'travel' per TF.

    The `has` test is applied later, because TRAJ_MIN_FRAC and TRAJ_MIN_TRAVEL gate only that test
    while the block walk depends on the block alone.
    """
    for t in rows:
        dr = 1 if t['dir'] == 'LONG' else -1
        t['tj'] = {}
        for tf in range(TF_LO, TF_HI + 1):
            bi, best, _ = opposed_extrema(RR[tf], dr, t['en'], K.traj_block(tf))
            if bi is None:
                t['tj'][tf] = (0, float('nan'), False)
                continue
            travel = float(RR[tf][t['en']]) - best
            t['tj'][tf] = (int(t['en']) - int(bi), travel,
                           (travel > 0) if dr > 0 else (travel < 0))
    return rows


def has(t, tf, frac, travel_min):
    """the trajectory test at this (frac, min_travel), from the cached walk."""
    bars, travel, towards = t['tj'][tf]
    if not towards or not np.isfinite(travel):
        return False
    return bars > max(1, int(K.traj_block(tf) * frac)) and abs(travel) >= float(travel_min)


def metrics(rows, coins, drag):
    """-> the five columns plus the supporting ones. Never divides by zero."""
    n = len(rows)
    if n == 0:
        return None
    usd = [(r['od_g'] / 100.0 - drag / 100.0) * coins * r['px'] for r in rows]
    pct = [r['od_g'] - drag for r in rows]
    wins = [u for u in usd if u > 0]
    losses = [u for u in usd if u <= 0]
    # the drawdown walks the equity in EXIT order, which is the order the account sees
    order = [u for _, u in sorted(zip([r['xb'] for r in rows], usd))]
    eq, peak, dd = START, START, 0.0
    for u in order:
        eq += u
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    run, worst_run, run_usd, worst_run_usd = 0, 0, 0.0, 0.0
    for u in order:
        if u <= 0:
            run += 1; run_usd += u
            if run > worst_run or (run == worst_run and run_usd < worst_run_usd):
                worst_run, worst_run_usd = run, run_usd
        else:
            run, run_usd = 0, 0.0
    return {'n': n, 'wins': len(wins), 'win_rate': 100.0 * len(wins) / n,
            'stopped': sum(1 for r in rows if r['why'] == 'STOP'),
            'net_usd': float(np.sum(usd)), 'net_pct': float(np.sum(pct)),
            'per_trade_pct': float(np.mean(pct)), 'dd': dd,
            'ndd': (float(np.sum(usd)) / dd) if dd > 0 else float('inf'),
            'pf': (float(np.sum(wins)) / abs(float(np.sum(losses)))) if losses else float('inf'),
            'run': worst_run, 'run_usd': worst_run_usd}


def row(label, m):
    if m is None:
        return '| %s | 0 | - | - | - | - | - | - | - | - |' % label
    nd = '%.2f' % m['ndd'] if np.isfinite(m['ndd']) else 'no DD'
    pf = '%.2f' % m['pf'] if np.isfinite(m['pf']) else 'no losers'
    return ('| %s | %d | %d | %.1f | %+.2f | %+.2f | %.2f | %s | %s | %d, %+.2f |'
            % (label, m['n'], m['wins'], m['win_rate'], m['net_usd'], m['net_pct'], m['dd'],
               nd, pf, m['run'], m['run_usd']))


HEAD = ('| the cell | trades | wins | win rate %% | net USDT | net %% | worst DD USDT | '
        'net / worst DD | profit factor | worst losing run |')
RULE = '|---|---|---|---|---|---|---|---|---|---|'


if __name__ == '__main__':
    out = open(sys.argv[1], 'w', buffering=1)

    def log(s):
        out.write(s + '\n'); print(s, flush=True)

    t0 = time.time()
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    piv = find_pivots(close, PCT)
    A, B = 0, ln.N - 1
    SPLIT = ln.K(SPLIT_TS)
    trip = (RS.K0, RS.R0, RS.S0)
    R = RS.load(trip)
    # THE dtf LINES COME FROM THE SAME CONFIG AS THE TRADES. They used to come from ln.line, which
    # reads the DB's mech_lines('wsf') ruling - it matched while the bank was k5 rsi8 stc7 and
    # would have silently diverged the moment the bank moved to k6 rsi8 stc6.
    RR = {t: R[t] for t in range(TF_LO, TF_HI + 1)}
    F.reset()
    f = F.scan(A, B, R, MG, 'window')
    rows_in = []
    for d in f:
        v, bar = F.walk(R, 5, d['side'], d['rev'], B)
        un = (v == 'EXHAUST' and bar is not None and bar >= B - 1)
        rows_in.append({'fire': d['fire'], 'rev': d['rev'], 'stamp': d['stamp'],
                        'side': d['side'], 'dir': d['dir'],
                        'verdict': 'UNRESOLVED' if un else v, 'exh': None if un else bar})
    ALL = ledger(DT.accept(rows_in), close, piv)
    L = raw_traj(cap_pyramid(ALL, K.MAX_PYRAMID), RR)
    SW = [r for r in L if r['en'] < SPLIT]
    HO = [r for r in L if r['en'] >= SPLIT]

    log('# CONFLUENCE on the backstop trades. banked r-config k%d rsi%d stc%d.' % trip)
    log('# the 1023 causality repair is in. max_pyramid %d banked: %d of %d trades carried.'
        % (K.MAX_PYRAMID, len(L), len(ALL)))
    log('# %d trades: %d sweep, %d hold-out.' % (len(L), len(SW), len(HO)))
    log('# RULED_OK %s. the full tape, %d bars = %.0f days. %d pivots at %.1f%%.'
        % (K.RULED_OK, ln.N, ln.N * 5 / 86400.0, len(piv), PCT))
    _cb = R[5][ln.K(K.CONTROL_TS)]
    _cd = ln.line('ws5r')[ln.K(K.CONTROL_TS)]
    log('# control ws5r %s: banked config %.2f (known-good %.2f), DB-ruled line %.2f'
        ' (known-good %.2f)' % (K.CONTROL_TS, _cb, K.CONTROL_BANK, _cd, K.CONTROL_DB))
    assert abs(_cd - K.CONTROL_DB) < 0.01, 'the DB-ruled line has drifted - the cache is suspect'
    assert abs(_cb - K.CONTROL_BANK) < 0.01, 'the BANKED line has drifted - the cache is suspect'
    log('# THE SPLIT: cells are RANKED on the sweep half and SCORED on the hold-out half.')
    log('# %d coins a trade, start USDT %.2f, drag %.4f%%. trajectory block = TRAJ_WIDTH %.1f'
        % (COINS, START, DRAG_22K, K.TRAJ_WIDTH))
    log('#   bars per TF-minute: ws%d %d bars, ws%d %d bars.'
        % (TF_LO, K.traj_block(TF_LO), TF_HI, K.traj_block(TF_HI)))
    log('')
    log('# THE LEGEND, because a column defined only in the docstring is not defined.')
    log('')
    log('| the column | what it is |')
    log('|---|---|')
    log('| trades | the episode count. No rate is printed without it |')
    log('| wins | trades whose NET is positive after %.4f%% drag' % DRAG_22K + ' |')
    log('| win rate % | wins / trades |')
    log('| net USDT | at %d coins a trade, no compounding |' % COINS)
    log('| worst DD USDT | the worst peak-to-trough of the equity walked in EXIT order |')
    log('| net / worst DD | the third target, Joe 1023 |')
    log('| profit factor | sum of winning USDT / absolute sum of losing USDT |')
    log('| worst losing run | consecutive losers, and what the run cost in USDT |')
    log('')

    log('# 1  THE BASELINE: every trade, no confluence gate.')
    log('')
    log(HEAD % ()); log(RULE)
    log(row('all trades, full tape', metrics(L, COINS, DRAG_22K)))
    log(row('sweep half', metrics(SW, COINS, DRAG_22K)))
    log(row('hold-out half', metrics(HO, COINS, DRAG_22K)))
    log('')

    log('# 2  THE HELD KNOBS, swept. TRAJ_MIN_FRAC %.2f and TRAJ_MIN_TRAVEL %.1f are the held'
        % (K.TRAJ_MIN_FRAC, K.TRAJ_MIN_TRAVEL))
    log('#    values. The gate here is ALL of ws%d-ws%d agreeing, on the SWEEP half.'
        % (TF_LO, TF_HI))
    log('')
    log(HEAD % ()); log(RULE)
    for fr in FRACS:
        for tv in TRAVELS:
            keep = [r for r in SW if all(has(r, tf, fr, tv) for tf in range(TF_LO, TF_HI + 1))]
            log(row('frac %.2f, travel %.1f' % (fr, tv), metrics(keep, COINS, DRAG_22K)))
    log('')

    log('# 3  EVERY CONTIGUOUS TF BAND at the held knobs, on the SWEEP half. %d or more trades to'
        % MIN_N)
    log('#    be ranked; smaller cells are printed below the rule, never ranked.')
    log('')
    cells = []
    for i in range(TF_LO, TF_HI + 1):
        for j in range(i, TF_HI + 1):
            band = list(range(i, j + 1))
            keep = [r for r in SW
                    if all(has(r, tf, K.TRAJ_MIN_FRAC, K.TRAJ_MIN_TRAVEL) for tf in band)]
            m = metrics(keep, COINS, DRAG_22K)
            if m:
                cells.append((band, m))
    big = [c for c in cells if c[1]['n'] >= MIN_N]
    big.sort(key=lambda c: -c[1]['ndd'])
    log(HEAD % ()); log(RULE)
    for band, m in big[:20]:
        log(row('ws%d-ws%d' % (band[0], band[-1]), m))
    log('')
    log('# the same cells ranked on WIN RATE instead, so the two targets can be compared.')
    log('')
    log(HEAD % ()); log(RULE)
    for band, m in sorted(big, key=lambda c: -c[1]['win_rate'])[:20]:
        log(row('ws%d-ws%d' % (band[0], band[-1]), m))
    log('')
    log('# the same cells ranked on NET USDT.')
    log('')
    log(HEAD % ()); log(RULE)
    for band, m in sorted(big, key=lambda c: -c[1]['net_usd'])[:20]:
        log(row('ws%d-ws%d' % (band[0], band[-1]), m))
    log('')

    log('# 4  THE HOLD-OUT. the top cell on each of the three targets, scored on data it never saw.')
    log('')
    log(HEAD % ()); log(RULE)
    base_ho = metrics(HO, COINS, DRAG_22K)
    log(row('hold-out, no gate', base_ho))
    seen = set()
    for tag, key in (('net / worst DD', lambda c: -c[1]['ndd']),
                     ('win rate', lambda c: -c[1]['win_rate']),
                     ('net USDT', lambda c: -c[1]['net_usd'])):
        if not big:
            break
        band = sorted(big, key=key)[0][0]
        k = (band[0], band[-1])
        keep = [r for r in HO
                if all(has(r, tf, K.TRAJ_MIN_FRAC, K.TRAJ_MIN_TRAVEL) for tf in band)]
        log(row('ws%d-ws%d, picked on %s' % (band[0], band[-1], tag),
                metrics(keep, COINS, DRAG_22K)))
        seen.add(k)
    log('')
    log('# 5  THE PER-TF SEPARATION on the SWEEP half, at the held knobs. No band, one line each.')
    log('')
    pos = [r for r in SW if (r['od_g'] - DRAG_22K) > 0]
    stp = [r for r in SW if (r['od_g'] - DRAG_22K) <= 0]
    log('| the TF | net-positive agreeing | of %d | net-negative agreeing | of %d | separation |'
        % (len(pos), len(stp)))
    log('|---|---|---|---|---|---|')
    for tf in range(TF_LO, TF_HI + 1):
        a = sum(1 for r in pos if has(r, tf, K.TRAJ_MIN_FRAC, K.TRAJ_MIN_TRAVEL))
        b = sum(1 for r in stp if has(r, tf, K.TRAJ_MIN_FRAC, K.TRAJ_MIN_TRAVEL))
        pa = a / len(pos) if pos else 0.0
        pb = b / len(stp) if stp else 0.0
        log('| ws%d | %d | %.0f%% | %d | %.0f%% | %+.0f pp |'
            % (tf, a, 100 * pa, b, 100 * pb, 100 * (pa - pb)))
    log('')
    log('# the cells under %d trades, printed and NOT ranked.' % MIN_N)
    log('')
    log(HEAD % ()); log(RULE)
    for band, m in sorted([c for c in cells if c[1]['n'] < MIN_N], key=lambda c: -c[1]['n']):
        log(row('ws%d-ws%d' % (band[0], band[-1]), m))
    log('# took %.0f s' % (time.time() - t0))
    out.close()
