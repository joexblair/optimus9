"""sweep_s46_exit — full-tape exit permutation engine. MAE + MFE + ret. Joe 0804.

    Joe: "using all of your new found ideas, run as many permutations that you can muster across the
    full ~12wk window ... don't sample, be precise. keep notes on what you add and what you remove"
    "don't try to fit the number - hold everything loose and light"
    "for this next task, you can use MAE and MFE"

POPULATION  every s46_run row passing gates 5 + 14, the full tape: 849 trades, 05-18 -> 07-31.
BASELINE    s6raw - the live strategy's exit (s6x crossing s6Mage, lb 72 bars, wob 3). Unchanged.
LINES       from lines_all.npz (build_s46_lines.py). exhv2 specs at TF15/22/30:
              x  bb  4|0.37|close      M  bb 37|0.70|close      r  kline 10|4|11|close

THREE ORTHOGONAL CONFIRMATION MECHANICS, composable. Each acts on the same crossed-side signal.

  1. HYSTERESIS  H, board points.  Joe 0804 research: the Schmitt trigger - two thresholds, not one.
     A time debounce costs lag on EVERY cross; a band costs nothing on a decisive move and everything
     on a marginal one. Latch: set when dd > +H, clear when dd < -H. H=0 is the plain cross.
     Evidence: the 03:03:25 pierce cleared its boundary by 0.572 points and reverted in 2 bars; the
     82-bar move at 03:07:20 cleared it by the same 0.572. So H alone will not separate those two -
     banked anyway because it is free and composes with the other two.

  2. CLOCK WOBBLE  n 5 s bars held. The existing mechanic. Costs n*5 s of lag unconditionally.

  3. EVENT WOBBLE  n EVENT BARS (volume > 0) elapsed while on the crossed side.  Joe 0804: "you're
     testing for crossovers in volitiale emerging bars". The decile census over 4,419 pierces put the
     busiest tenth of the tape at a 42.5% blip rate against 24.1% in the quietest, d10/d1 = 1.77 at
     EVERY window from 1 to 22 min. Lopez de Prado: time bars oversample ~70% of low-activity periods
     and undersample volatile ones; sample on activity instead. An event clock spends more
     confirmation exactly where the blips concentrate and less where they do not.

  DELIBERATELY NOT BUILT, and why:
   - efficiency-ratio / KAMA adaptation. Our own census kills it: `chop` (= 1/ER) separates blips from
     real moves at ratio 1.02 over 4,419 pierces. The literature's favourite answer is contradicted
     by our data, so building it would be following a citation instead of a measurement.
   - direction-change count. Runs BACKWARDS: 41.7% blip rate in the calmest decile vs 25.4% in the
     choppiest. Falsifies the "ton of retests" reading outright.
   - VPIN. Needs signed volume, which the tape does not carry. Noted for later, not built.

EXIT LEGS  (crossing line, target). LONG closes on a DOWN cross, SHORT on an UP cross - build_s46.py's
own rule, unchanged. Cross-TF targets carry Joe's "use a HTF to smooth the s15's volatility" idea:
s30r as a slower target measured 4.6x narrower in range than s15r and halved the sub-3-bar blips on
the s15 leg.
    x15b x15r x15M | x22b x22r x22M | x30b x30r x30M | x15r30 x22r30 x15M30 x22M30

MOMO GATE  optional. build_exhv2.momo() state, banked per bar per TF per direction. EITHER of the
chosen TFs in the chosen state set opens it; while open the s6 baseline exit is suppressed and the
race legs are armed. Joe 0804 locked: either-not-both, read every bar from entry, curl counts.

    python3 sweep_s46_exit.py --stage A     # every leg x every mechanic, in isolation
    python3 sweep_s46_exit.py --stage B     # + the momo gate
    python3 sweep_s46_exit.py --stage C     # leg subsets (races)
    python3 sweep_s46_exit.py --stage W     # 7-day rolling windows on the survivors
"""
import sys, os, json, itertools, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

NPZ = os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp/lines_all.npz'
HI, LO = 85.0, 15.0
EXIT_LB, EXIT_LINE, EXIT_WOB = 72, 's6x', 3
U = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')

# leg -> (crossing tf, target kind, target tf).  'b' = the 85/15 boundary.
LEGS = {
    'x15b': (15, 'b', 15), 'x15r': (15, 'r', 15), 'x15M': (15, 'M', 15),
    'x22b': (22, 'b', 22), 'x22r': (22, 'r', 22), 'x22M': (22, 'M', 22),
    'x30b': (30, 'b', 30), 'x30r': (30, 'r', 30), 'x30M': (30, 'M', 30),
    'x15r30': (15, 'r', 30), 'x22r30': (22, 'r', 30),
    'x15M30': (15, 'M', 30), 'x22M30': (22, 'M', 30),
}
HS = (0.0, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0)          # hysteresis band, board points
CW = (1, 2, 3, 6, 12, 24, 48, 96, 180, 360)              # clock wobble, 5 s bars
EW = (1, 2, 3, 6, 12, 24, 48, 96)                        # event wobble, event bars
DW = (1, 2, 3, 6, 12, 24, 48)                            # directional-event (run-bar) wobble
VW = (1, 2, 3, 6, 12, 24, 48, 96)                        # VOLUME clock, in multiples of median 5 s vol
XW = (1, 2, 3, 6, 12, 24, 48)                            # signed-volume run, same units
MODES = (('clock', CW), ('event', EW), ('direv', DW), ('vol', VW), ('dvol', XW))


def load():
    d = np.load(NPZ)
    L = {k: d[k] for k in d.files}
    db = DatabaseManager(**get_db_config()); db.connect()
    PX = db.execute('SELECT px_ms,px_v FROM s46_px ORDER BY px_ms', fetch=True)
    EX = db.execute('''SELECT sx_ms,sx_dir FROM s46_exit WHERE sx_line=%s AND sx_lb_min<=%s
                       AND sx_run_bars>=%s ORDER BY sx_ms''',
                    (EXIT_LINE, EXIT_LB, EXIT_WOB), fetch=True)
    RUN = db.execute('''SELECT sr_ms,sr_dr FROM s46_run WHERE sr_ib_bars>24 AND sr_s1hold>24
                        ORDER BY sr_ms''', fetch=True)
    # REAL VOLUME, straight from kline_collection. The npz 'evt' flag built from the jig base was
    # 1.000 for the whole of May and 0.676 in late July - a jig-window artefact, not the tape. The
    # DB says 10.9% of the tape's 5 s bars carry zero volume. Volume MAGNITUDE varies everywhere
    # (median 401, p90 17,460), so the volume clock is the sounder construction of the two.
    VOL = db.execute('SELECT kc_timestamp t,kc_volume v FROM kline_collection '
                     'WHERE kc_timestamp BETWEEN %s AND %s ORDER BY kc_timestamp',
                     (int(L['ts'][0]), int(L['ts'][-1])), fetch=True)
    db.disconnect()
    ts = L['ts']
    pm = np.array([r['px_ms'] for r in PX], np.int64)
    pv = np.array([r['px_v'] for r in PX], float)
    px = np.full(len(ts), np.nan)
    k = np.searchsorted(pm, ts)
    ok = (k < len(pm)) & (pm[np.minimum(k, len(pm) - 1)] == ts)
    px[ok] = pv[k[ok]]
    sh = (EXIT_WOB - 1) * 5000
    s6 = {1: np.array(sorted(r['sx_ms'] + sh for r in EX if r['sx_dir'] == 1), np.int64),
          -1: np.array(sorted(r['sx_ms'] + sh for r in EX if r['sx_dir'] == -1), np.int64)}
    vm = np.array([r['t'] for r in VOL], np.int64)
    vv = np.array([float(r['v']) for r in VOL], float)
    vol = np.zeros(len(ts))
    kk = np.searchsorted(vm, ts)
    okv = (kk < len(vm)) & (vm[np.minimum(kk, len(vm) - 1)] == ts)
    vol[okv] = vv[kk[okv]]
    L['vol'] = vol
    L['evt'] = (vol > 0).astype(np.int8)
    L['medvol'] = float(np.median(vol[vol > 0])) if (vol > 0).any() else 1.0
    trades = []
    for r in RUN:
        i = int(np.searchsorted(ts, int(r['sr_ms'])))
        if i < len(ts) and ts[i] == int(r['sr_ms']) and np.isfinite(px[i]):
            trades.append((i, int(r['sr_dr'])))
    return L, ts, px, s6, trades


def latch(dd, H):
    """Schmitt trigger. set when dd > +H, clear when dd < -H, hold otherwise. Returns bool per bar."""
    hi = dd > H
    lo = dd < -H
    st = np.where(hi, 1, np.where(lo, 0, -1))
    idx = np.where(st >= 0, np.arange(len(st)), 0)
    np.maximum.accumulate(idx, out=idx)
    out = st[idx] == 1
    out[:int(np.argmax(st >= 0))] = False
    return out


def run_len(b):
    """consecutive-True count ending at each bar - cross_wob's own idiom (jig.py:261-263)."""
    b = np.asarray(b, bool)
    i = np.arange(len(b))
    reset = np.where(b, 0, i + 1)
    return (i + 1) - np.maximum.accumulate(reset)


def tick_rule(px):
    """Lopez de Prado's tick rule: sign of the price change, zeros carried forward. +1 up, -1 down."""
    d = np.sign(np.diff(px, prepend=px[0]))
    d[~np.isfinite(d)] = 0
    i = np.where(d != 0, np.arange(len(d)), 0)
    np.maximum.accumulate(i, out=i)
    return d[i]


def event_len(b, evt):
    """EVENT bars elapsed inside the current True run, ending at each bar."""
    b = np.asarray(b, bool)
    ce = np.concatenate([[0], np.cumsum(evt.astype(np.int64))])
    i = np.arange(len(b))
    reset = np.where(b, 0, i + 1)
    start = np.maximum.accumulate(reset)          # index of the run's first bar
    return ce[i + 1] - ce[start]


def direv_len(b, evt, tick, dr):
    """RUN-BAR WOBBLE. Count only the event bars inside the run whose tick agrees with the exit
    direction. Lopez de Prado's run bars close on bursts of ONE-SIDED activity even when the other
    side is also active; the plain event count cannot tell a one-sided burst from two-sided churn.
    LONG exits on a DOWN cross so agreement is tick -1; SHORT exits UP so agreement is tick +1."""
    b = np.asarray(b, bool)
    a = (evt.astype(bool) & (tick == -dr)).astype(np.int64)
    ca = np.concatenate([[0], np.cumsum(a)])
    i = np.arange(len(b))
    reset = np.where(b, 0, i + 1)
    start = np.maximum.accumulate(reset)
    return ca[i + 1] - ca[start]


def vol_len(b, vol):
    """VOLUME CLOCK. Cumulative traded volume inside the current run, ending at each bar.
    Lopez de Prado / Easley-O'Hara: 'if prices are information, then volume indicates the speed with
    which it arrives'. Reported in multiples of the tape's median non-zero 5 s volume so the knob is
    scale-free and directly comparable to the clock wobble."""
    b = np.asarray(b, bool)
    cv = np.concatenate([[0.0], np.cumsum(vol)])
    i = np.arange(len(b))
    reset = np.where(b, 0, i + 1)
    start = np.maximum.accumulate(reset)
    return cv[i + 1] - cv[start]


def dvol_len(b, vol, tick, dr):
    """SIGNED-VOLUME RUN. Only the volume whose tick agrees with the exit direction. This is the
    run-bar idea proper: run bars close on bursts of ONE-SIDED activity even when the other side is
    also active, which a plain volume clock cannot distinguish from two-sided churn."""
    b = np.asarray(b, bool)
    a = np.where(tick == -dr, vol, 0.0)
    ca = np.concatenate([[0.0], np.cumsum(a)])
    i = np.arange(len(b))
    reset = np.where(b, 0, i + 1)
    start = np.maximum.accumulate(reset)
    return ca[i + 1] - ca[start]


def fires(L, ts, leg, dr, H, mode, n):
    """Confirmed-cross bar indices for one leg/direction/hysteresis/wobble config."""
    ctf, kind, ttf = LEGS[leg]
    x = L['x%d' % ctf]
    tgt = (np.full(len(x), HI if dr > 0 else LO) if kind == 'b' else L['%s%d' % (kind, ttf)])
    dd = (x - tgt) * (-1.0 if dr > 0 else 1.0)     # >0 means past the target in the EXIT direction
    st = latch(dd, H)
    if mode == 'clock':
        ok = run_len(st) >= max(1, n)
    else:
        ok = st & (event_len(st, L['evt']) >= max(1, n))
    return np.flatnonzero(ok & ~np.r_[False, ok[:-1]])


def gate_open(L, dr, tfs, states, gwob):
    """momo gate: EITHER chosen TF in the chosen state set, held gwob consecutive bars."""
    tag = 'p' if dr > 0 else 'n'
    g = np.zeros(len(L['ts']), bool)
    for tf in tfs:
        v = L['g%d_%s' % (tf, tag)]
        for s in states:
            g |= (v == s)
    return run_len(g) >= max(1, gwob)


def score(px, a, b, dr):
    p0 = px[a]; seg = px[a + 1:b + 1]
    if not len(seg) or not np.isfinite(p0) or p0 == 0:
        return None
    worst = np.nanmin(seg) if dr > 0 else np.nanmax(seg)
    best = np.nanmax(seg) if dr > 0 else np.nanmin(seg)
    return (float(abs(min(0.0, dr * (worst - p0) / p0 * 100))),
            float(max(0.0, dr * (best - p0) / p0 * 100)),
            float(dr * (px[b] - p0) / p0 * 100), int(b - a))


def evaluate(ts, px, trades, firemap, s6=None, gate=None, arm_at_gate=True, s6_mode='race'):
    """firemap[dr] = sorted fire-bar indices. Returns per-trade (mae, mfe, ret, hold, exit_i).

    s6_mode='race'      s6 competes with the leg; exit = whichever is earlier. s6 can only pull IN.
    s6_mode='fallback'  s6 is used ONLY when the leg never fires. The leg is then free to exit LATER
                        than s6, which is the whole point of a hold-longer mechanic, while every
                        trade still terminates so mean ret stays comparable across configs.
    """
    out = []
    for a, dr in trades:
        start = a
        if gate is not None:
            g = gate[dr]
            nz = np.flatnonzero(g[a:])
            if not len(nz):
                start = None
            elif arm_at_gate:
                start = a + int(nz[0])
        cand = []
        if start is not None and firemap is not None:
            f = firemap[dr]
            j = np.searchsorted(f, start)
            if j < len(f):
                cand.append(int(f[j]))
        if s6 is not None and not (s6_mode == 'fallback' and cand):
            sm = s6[dr]
            j = np.searchsorted(sm, ts[a], side='right')
            while j < len(sm):
                bi = int(np.searchsorted(ts, sm[j]))
                if bi < len(ts) and ts[bi] == sm[j]:
                    if gate is None or not gate[dr][bi]:
                        cand.append(bi); break
                j += 1
        if not cand:
            out.append(None); continue
        b = min(cand)
        sc = score(px, a, b, dr)
        out.append(None if sc is None else sc + (b,))
    return out


def agg(res, trades, ts, label):
    v = [r for r in res if r is not None]
    if not v:
        return None
    mae = np.array([r[0] for r in v]); mfe = np.array([r[1] for r in v])
    ret = np.array([r[2] for r in v]); hold = np.array([r[3] for r in v])
    ex = np.array([r[4] for r in v])
    return dict(label=label, n=len(v), nmiss=len(res) - len(v),
                mae=float(mae.mean()), mae_med=float(np.median(mae)), mae_max=float(mae.max()),
                mfe=float(mfe.mean()), mfe_med=float(np.median(mfe)),
                ret=float(ret.mean()), ret_med=float(np.median(ret)),
                ret_sum=float(ret.sum()), win=float((ret > 0).mean() * 100),
                hold=float(hold.mean()), hold_med=float(np.median(hold)),
                capture=float((ret / np.maximum(mfe, 1e-9)).clip(-5, 5).mean()),
                nexit=int(len(set(ex.tolist()))))


# ---------------------------------------------------------------------------------------------
# STAGE DRIVERS.  Memory discipline: the latch + run-length + event-length arrays are built one
# (leg, dr, H) at a time and discarded, because holding all 208 of them at once is ~2.3 GB.
# ---------------------------------------------------------------------------------------------
def side_arrays(L, leg, dr, H, tick=None):
    """-> dict of the five confirmation accumulators for one leg/direction/hysteresis."""
    ctf, kind, ttf = LEGS[leg]
    x = L['x%d' % ctf]
    tgt = (np.full(len(x), HI if dr > 0 else LO) if kind == 'b' else L['%s%d' % (kind, ttf)])
    dd = (x - tgt) * (-1.0 if dr > 0 else 1.0)
    st = latch(dd, H)
    mv = L['medvol']
    A = {'st': st,
         'clock': run_len(st).astype(np.int32),
         'event': event_len(st, L['evt']).astype(np.int32)}
    if tick is not None:
        A['direv'] = direv_len(st, L['evt'], tick, dr).astype(np.int32)
        A['dvol'] = (dvol_len(st, L['vol'], tick, dr) / mv).astype(np.float32)
    A['vol'] = (vol_len(st, L['vol']) / mv).astype(np.float32)
    return A


def confirm(A, mode, n):
    """bars where the chosen accumulator has reached n inside the current run."""
    if mode == 'clock':
        return A['clock'] >= max(1, n)
    return A['st'] & (A[mode] >= n)


def edges(ok):
    return np.flatnonzero(ok & ~np.r_[False, ok[:-1]])


def split(trades, ts):
    K = len(trades) // 2
    return K


def report(rows, key, top, hdr_note=''):
    if not rows:
        print('  (none)'); return
    print('  %-46s %5s %7s %7s %7s %7s %7s %7s %6s %7s %6s'
          % ('config', 'n', 'MAEmn', 'MAEmax', 'MFEmn', 'RETmn', 'RETsum', 'win%', 'hold', 'cap', 'exits'))
    for r in sorted(rows, key=key)[:top]:
        print('  %-46s %5d %7.3f %7.3f %7.3f %+7.3f %+7.1f %7.1f %6.0f %7.2f %6d'
              % (r['label'], r['n'], r['mae'], r['mae_max'], r['mfe'], r['ret'], r['ret_sum'],
                 r['win'], r['hold'], r['capture'], r['nexit']))


TICK = None          # set once in __main__ from px; the tick rule needs price, not lines


def stage_A(L, ts, px, s6, trades, argv):
    K = split(trades, ts)
    IS, OOS = trades[:K], trades[K:]
    print('POPULATION %d trades   IS 1..%d (%s -> %s)   OOS %d..%d (%s -> %s)'
          % (len(trades), K, U(ts[trades[0][0]]), U(ts[trades[K-1][0]]),
             K+1, len(trades), U(ts[trades[K][0]]), U(ts[trades[-1][0]])))
    base = evaluate(ts, px, trades, None, s6=s6)
    bA = agg(base, trades, ts, 'BASELINE s6raw')
    bI = agg(evaluate(ts, px, IS, None, s6=s6), IS, ts, 'BASELINE IS')
    bO = agg(evaluate(ts, px, OOS, None, s6=s6), OOS, ts, 'BASELINE OOS')
    print()
    print('=== BASELINE (the live s6 exit, unchanged) ===')
    report([bA, bI, bO], lambda r: 0, 3)
    rows = []
    for leg in LEGS:
        for H in HS:
            fm = {}
            arr = {dr: side_arrays(L, leg, dr, H, TICK) for dr in (1, -1)}
            for mode, NS in MODES:
                for n in NS:
                    for dr in (1, -1):
                        fm[dr] = edges(confirm(arr[dr], mode, n))
                    lbl = '%s H%g %s%d' % (leg, H, mode, n)
                    ev = evaluate(ts, px, trades, fm, s6=s6, s6_mode='fallback')
                    r = agg(ev, trades, ts, lbl)
                    if r is None: continue
                    ri = agg(ev[:K], IS, ts, lbl); ro = agg(ev[K:], OOS, ts, lbl)
                    r['is_ret'] = ri['ret'] if ri else np.nan
                    r['oos_ret'] = ro['ret'] if ro else np.nan
                    r['is_mae'] = ri['mae'] if ri else np.nan
                    r['oos_mae'] = ro['mae'] if ro else np.nan
                    r['leg'], r['H'], r['mode'], r['wn'] = leg, H, mode, n
                    rows.append(r)
            del arr
    json.dump(rows, open(os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp/stageA.json', 'w'))
    print()
    print('=== %d configs. TOP 25 by mean RET (full tape) ===' % len(rows))
    report(rows, lambda r: -r['ret'], 25)
    print()
    print('=== TOP 25 by mean MAE (lowest) ===')
    report(rows, lambda r: r['mae'], 25)
    print()
    print('=== TOP 25 by mean MFE (highest) ===')
    report(rows, lambda r: -r['mfe'], 25)
    print()
    print('=== IS/OOS: top 25 by IS mean ret, with OOS alongside ===')
    print('  %-46s %8s %8s %8s %8s %7s' % ('config', 'IS ret', 'OOS ret', 'IS mae', 'OOS mae', 'held?'))
    for r in sorted(rows, key=lambda r: -r['is_ret'])[:25]:
        print('  %-46s %+8.3f %+8.3f %8.3f %8.3f %7s'
              % (r['label'], r['is_ret'], r['oos_ret'], r['is_mae'], r['oos_mae'],
                 'YES' if r['oos_ret'] > (bO['ret'] if bO else 0) else 'no'))
    bt = bO['ret'] if bO else 0
    beat_is = [r for r in rows if r['is_ret'] > (bI['ret'] if bI else 0)]
    held = [r for r in beat_is if r['oos_ret'] > bt]
    print()
    print('  configs beating baseline IS ret: %d of %d = %.1f%%' % (len(beat_is), len(rows),
                                                                   100.0*len(beat_is)/len(rows)))
    print('  of those, also beating baseline OOS ret: %d = %.1f%%'
          % (len(held), 100.0*len(held)/max(1, len(beat_is))))
    ir = np.array([r['is_ret'] for r in rows]); orr = np.array([r['oos_ret'] for r in rows])
    m = np.isfinite(ir) & np.isfinite(orr)
    print('  IS/OOS mean-ret correlation across all configs: %+.3f' % np.corrcoef(ir[m], orr[m])[0, 1])
    print()
    print('=== mechanic marginals: mean RET by wobble mode and size, pooled over legs and H ===')
    for mode, NS in MODES:
        print('  %s' % mode)
        for n in NS:
            s = [r for r in rows if r['mode'] == mode and r['wn'] == n]
            if s:
                print('    n=%-4d %4d cfg  ret %+7.3f  mae %6.3f  mfe %6.3f  hold %6.0f  win %5.1f%%'
                      % (n, len(s), np.mean([x['ret'] for x in s]), np.mean([x['mae'] for x in s]),
                         np.mean([x['mfe'] for x in s]), np.mean([x['hold'] for x in s]),
                         np.mean([x['win'] for x in s])))
    print('  hysteresis H')
    for H in HS:
        s = [r for r in rows if r['H'] == H]
        if s:
            print('    H=%-5g %4d cfg  ret %+7.3f  mae %6.3f  mfe %6.3f  hold %6.0f  win %5.1f%%'
                  % (H, len(s), np.mean([x['ret'] for x in s]), np.mean([x['mae'] for x in s]),
                     np.mean([x['mfe'] for x in s]), np.mean([x['hold'] for x in s]),
                     np.mean([x['win'] for x in s])))
    print('  leg')
    for leg in LEGS:
        s = [r for r in rows if r['leg'] == leg]
        if s:
            print('    %-8s %4d cfg  ret %+7.3f  mae %6.3f  mfe %6.3f  hold %6.0f  win %5.1f%%'
                  % (leg, len(s), np.mean([x['ret'] for x in s]), np.mean([x['mae'] for x in s]),
                     np.mean([x['mfe'] for x in s]), np.mean([x['hold'] for x in s]),
                     np.mean([x['win'] for x in s])))
    return rows



# ---------------------------------------------------------------------------------------------
# STAGE B — the momo gate on top of the surviving legs.
#   ADDED   gate on/off, TF set, state set (momo | momo+curl), gate wobble, and whether the s6
#           baseline stays live as a second exit while the gate is shut.
#   Joe 0804 locked: EITHER of the chosen TFs opens it, read every bar from entry, curl counts.
# ---------------------------------------------------------------------------------------------
GATE_TFS = ((15,), (22,), (30,), (15, 22), (15, 22, 30))
GATE_ST = (('momo',), ('momo', 'curl'))
GATE_W = (1, 12, 24, 72)
ST_ID = {'momo': 1, 'curl': 2}


def stage_B(L, ts, px, s6, trades, argv, seeds):
    K = split(trades, ts)
    IS, OOS = trades[:K], trades[K:]
    bO = agg(evaluate(ts, px, OOS, None, s6=s6), OOS, ts, 'base')
    bI = agg(evaluate(ts, px, IS, None, s6=s6), IS, ts, 'base')
    rows = []
    for leg, H, mode, n in seeds:
        fm = {}
        for dr in (1, -1):
            fm[dr] = edges(confirm(side_arrays(L, leg, dr, H, TICK), mode, n))
        for tfs in GATE_TFS:
            for sts in GATE_ST:
                ids = tuple(ST_ID[x] for x in sts)
                for gw in GATE_W:
                    gt = {dr: gate_open(L, dr, tfs, ids, gw) for dr in (1, -1)}
                    for with6 in (False, True):
                        lbl = ('%s H%g %s%d | G%s %s gw%d %s'
                               % (leg, H, mode, n, '+'.join(str(t) for t in tfs),
                                  '+'.join(s[0] for s in sts), gw, 's6' if with6 else '-'))
                        MD = dict(s6=s6, gate=gt, s6_mode=('race' if with6 else 'fallback'))
                        ev = evaluate(ts, px, trades, fm, **MD)
                        r = agg(ev, trades, ts, lbl)
                        if r is None: continue
                        ri = agg(ev[:K], IS, ts, lbl); ro = agg(ev[K:], OOS, ts, lbl)
                        r['is_ret'] = ri['ret'] if ri else np.nan
                        r['oos_ret'] = ro['ret'] if ro else np.nan
                        r['is_mae'] = ri['mae'] if ri else np.nan
                        r['oos_mae'] = ro['mae'] if ro else np.nan
                        r['cfg'] = dict(leg=leg, H=H, mode=mode, n=n, tfs=tfs, sts=sts, gw=gw, s6=with6)
                        rows.append(r)
    json.dump(rows, open(os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp/stageB.json', 'w'), default=str)
    print()
    print('=== STAGE B: %d gate configs over %d seed legs ===' % (len(rows), len(seeds)))
    print('  baseline  IS ret %+.3f   OOS ret %+.3f' % (bI['ret'], bO['ret']))
    print()
    print('--- top 25 by full-tape mean ret ---')
    report(rows, lambda r: -r['ret'], 25)
    print()
    print('--- top 25 by IS ret, OOS alongside ---')
    print('  %-46s %8s %8s %8s %8s %7s' % ('config', 'IS ret', 'OOS ret', 'IS mae', 'OOS mae', 'held?'))
    for r in sorted(rows, key=lambda r: -r['is_ret'])[:25]:
        print('  %-46s %+8.3f %+8.3f %8.3f %8.3f %7s'
              % (r['label'][:46], r['is_ret'], r['oos_ret'], r['is_mae'], r['oos_mae'],
                 'YES' if r['oos_ret'] > bO['ret'] else 'no'))
    bi = [r for r in rows if r['is_ret'] > bI['ret']]
    hd = [r for r in bi if r['oos_ret'] > bO['ret']]
    print()
    print('  beat baseline IS: %d of %d = %.1f%%   of those held OOS: %d = %.1f%%'
          % (len(bi), len(rows), 100.0*len(bi)/max(1, len(rows)), len(hd),
             100.0*len(hd)/max(1, len(bi))))
    return rows


# ---------------------------------------------------------------------------------------------
# STAGE C — leg subsets (a race: first leg to confirm wins).
#   ADDED   every subset of the surviving legs, at each leg's own best mechanic.
# ---------------------------------------------------------------------------------------------
def stage_C(L, ts, px, s6, trades, argv, seeds, gate=None):
    K = split(trades, ts)
    IS, OOS = trades[:K], trades[K:]
    bI = agg(evaluate(ts, px, IS, None, s6=s6), IS, ts, 'base')
    bO = agg(evaluate(ts, px, OOS, None, s6=s6), OOS, ts, 'base')
    F = {}
    for leg, H, mode, n in seeds:
        fm = {}
        for dr in (1, -1):
            fm[dr] = edges(confirm(side_arrays(L, leg, dr, H, TICK), mode, n))
        F['%s H%g %s%d' % (leg, H, mode, n)] = fm
    names = list(F)
    rows = []
    for k in range(1, len(names) + 1):
        for sub in itertools.combinations(names, k):
            fm = {dr: np.sort(np.concatenate([F[s][dr] for s in sub])) for dr in (1, -1)}
            for with6 in (False, True):
                lbl = ' + '.join(x.split(' ')[0] for x in sub) + (' | s6' if with6 else '')
                MD = dict(s6=s6, gate=gate, s6_mode=('race' if with6 else 'fallback'))
                ev = evaluate(ts, px, trades, fm, **MD)
                r = agg(ev, trades, ts, lbl[:46])
                if r is None: continue
                ri = agg(ev[:K], IS, ts, lbl); ro = agg(ev[K:], OOS, ts, lbl)
                r['is_ret'] = ri['ret'] if ri else np.nan
                r['oos_ret'] = ro['ret'] if ro else np.nan
                r['nlegs'] = k
                rows.append(r)
    json.dump(rows, open(os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp/stageC.json', 'w'), default=str)
    print()
    print('=== STAGE C: %d leg-subset races ===' % len(rows))
    print('  baseline  IS ret %+.3f   OOS ret %+.3f' % (bI['ret'], bO['ret']))
    print()
    report(rows, lambda r: -r['ret'], 25)
    print()
    print('  by subset size: ')
    for k in sorted(set(r['nlegs'] for r in rows)):
        s = [r for r in rows if r['nlegs'] == k]
        print('    %d legs  %4d cfg   best ret %+.3f   mean ret %+.3f   best OOS %+.3f'
              % (k, len(s), max(x['ret'] for x in s), np.mean([x['ret'] for x in s]),
                 max(x['oos_ret'] for x in s)))
    return rows


# ---------------------------------------------------------------------------------------------
# STAGE W — 7-day windows. Joe 0804: "the way to get around stagnate OOS, is to start testing
#   12 x 7 day windows (or 24 x 7 windows with overlap), to find the dates that need more help
#   than a simple knob tweak".  Both are built: 11 non-overlapping and 21 overlapping at 3.5 d.
# ---------------------------------------------------------------------------------------------
def binseg(y, k=6, minlen=20):
    """Binary segmentation change-point detection on a 1-D series. Greedy top-down: repeatedly split
    the segment whose split most reduces within-segment SSE. The PELT/BinSeg family is the standard
    tool for exactly the question Joe is asking - 'find the dates that need more help than a simple
    knob tweak'. BinSeg rather than PELT because it needs no penalty tuning and k is explicit."""
    y = np.asarray(y, float)
    segs = [(0, len(y))]
    cps = []
    for _ in range(k):
        best = None
        for si, (a, b) in enumerate(segs):
            if b - a < 2 * minlen:
                continue
            seg = y[a:b]
            n = len(seg)
            c1 = np.cumsum(seg); c2 = np.cumsum(seg ** 2)
            tot = c2[-1] - c1[-1] ** 2 / n
            i = np.arange(minlen, n - minlen)
            l = c2[i - 1] - c1[i - 1] ** 2 / i
            rc1 = c1[-1] - c1[i - 1]; rc2 = c2[-1] - c2[i - 1]
            r = rc2 - rc1 ** 2 / (n - i)
            gain = tot - (l + r)
            if not len(gain) or not np.isfinite(gain).any():
                continue
            j = int(np.nanargmax(gain))
            if best is None or gain[j] > best[0]:
                best = (gain[j], si, a + int(i[j]))
        if best is None:
            break
        _, si, cp = best
        a, b = segs.pop(si)
        segs += [(a, cp), (cp, b)]
        segs.sort()
        cps.append(cp)
    return sorted(cps)


def stage_W(L, ts, px, s6, trades, argv, cfgs):
    T0 = ts[trades[0][0]]; T1 = ts[trades[-1][0]]
    DAY = 86400000
    wins = []
    a = T0
    while a < T1:
        wins.append(('nolap', a, a + 7 * DAY)); a += 7 * DAY
    a = T0
    while a < T1:
        wins.append(('olap', a, a + 7 * DAY)); a += int(3.5 * DAY)
    base = evaluate(ts, px, trades, None, s6=s6)
    per = {}
    for lbl, fm, gt, with6 in cfgs:
        per[lbl] = evaluate(ts, px, trades, fm, s6=s6, gate=gt,
                            s6_mode=('race' if with6 else 'fallback'))
    tms = np.array([ts[a] for a, _ in trades])
    print()
    print('=== STAGE W: %d windows (%d non-overlapping + %d overlapping at 3.5 d) ==='
          % (len(wins), sum(1 for w in wins if w[0] == 'nolap'), sum(1 for w in wins if w[0] == 'olap')))
    for kind in ('nolap', 'olap'):
        print()
        print('--- %s ---' % kind)
        print('  %-6s %-14s %-14s %5s %9s %9s   %s'
              % ('win', 'from', 'to', 'n', 'BASE ret', 'BASE mae', '  '.join(l[:18] for l in per)))
        wi = 0
        for k, a, b in wins:
            if k != kind: continue
            wi += 1
            m = np.flatnonzero((tms >= a) & (tms < b))
            if not len(m): continue
            bv = [base[i] for i in m if base[i] is not None]
            if not bv: continue
            br = np.mean([x[2] for x in bv]); bm = np.mean([x[0] for x in bv])
            cells = []
            for lbl in per:
                cv = [per[lbl][i] for i in m if per[lbl][i] is not None]
                cells.append('%+9.3f' % np.mean([x[2] for x in cv]) if cv else '        -')
            print('  w%-5d %-14s %-14s %5d %+9.3f %9.3f   %s'
                  % (wi, U(a)[:11], U(b)[:11], len(m), br, bm, '  '.join(cells)))
    # --- CHANGE POINTS: where does the tape's behaviour actually shift? -------------------------
    print()
    print('=== CHANGE POINTS on the per-trade ret series (binary segmentation, k=6, min 20 trades) ===')
    for nm, series in [('BASELINE s6raw', base)] + [(l, per[l]) for l in per]:
        y = np.array([r[2] if r is not None else 0.0 for r in series])
        cps = binseg(y, k=6, minlen=20)
        bounds = [0] + cps + [len(y)]
        print('  %s' % nm)
        print('    %-6s %-14s %-14s %6s %9s %9s %9s'
              % ('seg', 'from', 'to', 'n', 'ret mean', 'ret sum', 'win%'))
        for i in range(len(bounds) - 1):
            a2, b2 = bounds[i], bounds[i + 1]
            yy = y[a2:b2]
            print('    s%-5d %-14s %-14s %6d %+9.3f %+9.1f %9.1f'
                  % (i + 1, U(ts[trades[a2][0]])[:11], U(ts[trades[b2 - 1][0]])[:11],
                     b2 - a2, yy.mean(), yy.sum(), 100.0 * (yy > 0).mean()))
    # --- per-window WINNERS: which config is best in each window, and by how much ---------------
    print()
    print('=== per 7-day window: does ONE config win everywhere, or do different windows want '
          'different mechanics? ===')
    names = list(per)
    if names:
        print('  %-6s %-14s %5s %10s   %s' % ('win', 'from', 'n', 'BASE ret', 'best config (ret)'))
        wi = 0
        for k, a, b in wins:
            if k != 'nolap': continue
            wi += 1
            m = np.flatnonzero((tms >= a) & (tms < b))
            if not len(m): continue
            bv = [base[i] for i in m if base[i] is not None]
            br = np.mean([x[2] for x in bv]) if bv else float('nan')
            sc = []
            for lbl in names:
                cv = [per[lbl][i] for i in m if per[lbl][i] is not None]
                sc.append((np.mean([x[2] for x in cv]) if cv else -9e9, lbl))
            sc.sort(reverse=True)
            print('  w%-5d %-14s %5d %+10.3f   %s (%+.3f)  [2nd %s %+.3f]'
                  % (wi, U(a)[:11], len(m), br, sc[0][1][:22], sc[0][0],
                     sc[1][1][:16] if len(sc) > 1 else '-', sc[1][0] if len(sc) > 1 else 0))
    return per



# ---------------------------------------------------------------------------------------------
# STAGE D — price-path exits, layered UNDER the line exits.
#   ADDED   TP (take profit), STOP, and TRAIL (give-back from running MFE).
#   Joe's own inventory, never built until now:
#     item 12  "which TP would produce the most return if we had a 0.3 or 0.4 stop"
#     item 11  "> 0.75 MFE to the swing detect 1% pivot"  - TRAIL is the causal cousin of this
#   TRAIL only arms once the trade is in profit, so it can never fire before the first favourable
#   bar. NO HORIZON CAP: the s6 baseline is always a candidate, so every trade terminates without a
#   truncation being imposed.
# ---------------------------------------------------------------------------------------------
TPS = (None, 0.15, 0.20, 0.30, 0.40, 0.50, 0.75, 1.00, 1.50, 2.00, 3.00)
STOPS = (None, 0.15, 0.20, 0.30, 0.40, 0.50, 0.75, 1.00)
TRAILS = (None, 0.10, 0.15, 0.20, 0.30, 0.50, 0.75, 1.00)
# PROPORTIONAL trail: exit when ret falls below f x the running MFE peak. The trade-journal
# literature reports a 50% pullback-from-MFE trail beating a fixed target by ~29% per winner, and
# notes most exits capture under 50% of available favourable movement. This is that rule.
TRAILF = (None, 0.50, 0.60, 0.70, 0.80, 0.90)


def path_exit(px, a, dr, hard, tp, stop, trail, trailf=None):
    """first bar in (a, hard] hit by tp / stop / trail; hard is the line-or-s6 exit. -> bar index."""
    p0 = px[a]
    seg = px[a + 1:hard + 1]
    if not len(seg):
        return hard
    ret = dr * (seg - p0) / p0 * 100.0
    cand = [hard]
    if tp is not None:
        w = np.flatnonzero(ret >= tp)
        if len(w): cand.append(a + 1 + int(w[0]))
    if stop is not None:
        w = np.flatnonzero(ret <= -stop)
        if len(w): cand.append(a + 1 + int(w[0]))
    if trail is not None:
        rm = np.maximum.accumulate(ret)
        w = np.flatnonzero((rm > 0) & ((rm - ret) >= trail))
        if len(w): cand.append(a + 1 + int(w[0]))
    if trailf is not None:
        rm = np.maximum.accumulate(ret)
        w = np.flatnonzero((rm > 0) & (ret <= trailf * rm))
        if len(w): cand.append(a + 1 + int(w[0]))
    return min(cand)


def stage_D(L, ts, px, s6, trades, argv, seeds):
    K = split(trades, ts)
    IS, OOS = trades[:K], trades[K:]
    bI = agg(evaluate(ts, px, IS, None, s6=s6), IS, ts, 'base')
    bO = agg(evaluate(ts, px, OOS, None, s6=s6), OOS, ts, 'base')
    bases = [('s6only', None)]
    for leg, H, mode, n in seeds[:3]:
        fm = {}
        for dr in (1, -1):
            fm[dr] = edges(confirm(side_arrays(L, leg, dr, H, TICK), mode, n))
        bases.append(('%s H%g %s%d' % (leg, H, mode, n), fm))
    rows = []
    for bl, fm in bases:
        hard = evaluate(ts, px, trades, fm, s6=s6, s6_mode='fallback')
        for tp in TPS:
            for stop in STOPS:
                for trail, trailf in [(t, None) for t in TRAILS] + [(None, f) for f in TRAILF[1:]]:
                    if tp is None and stop is None and trail is None and trailf is None:
                        continue
                    out = []
                    for (a, dr), h in zip(trades, hard):
                        if h is None:
                            out.append(None); continue
                        b = path_exit(px, a, dr, h[4], tp, stop, trail, trailf)
                        sc = score(px, a, b, dr)
                        out.append(None if sc is None else sc + (b,))
                    lbl = '%s|tp%s st%s tr%s tf%s' % (bl[:18],
                                                       '-' if tp is None else '%.2f' % tp,
                                                       '-' if stop is None else '%.2f' % stop,
                                                       '-' if trail is None else '%.2f' % trail,
                                                       '-' if trailf is None else '%.2f' % trailf)
                    r = agg(out, trades, ts, lbl)
                    if r is None: continue
                    r['is_ret'] = float(np.mean([out[i][2] for i in range(K) if out[i]]))
                    r['oos_ret'] = float(np.mean([out[i][2] for i in range(K, len(out)) if out[i]]))
                    r['base'], r['tp'], r['stop'] = bl, tp, stop
                    r['trail'], r['trailf'] = trail, trailf
                    rows.append(r)
    json.dump(rows, open(os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp/stageD.json', 'w'), default=str)
    print()
    print('=== STAGE D: %d TP/stop/trail configs over %d exit bases ===' % (len(rows), len(bases)))
    print('  baseline  IS ret %+.3f   OOS ret %+.3f' % (bI['ret'], bO['ret']))
    print()
    print('--- top 30 by full-tape mean ret ---')
    report(rows, lambda r: -r['ret'], 30)
    print()
    print('--- top 25 by IS ret, OOS alongside ---')
    print('  %-46s %8s %8s %7s' % ('config', 'IS ret', 'OOS ret', 'held?'))
    for r in sorted(rows, key=lambda r: -r['is_ret'])[:25]:
        print('  %-46s %+8.3f %+8.3f %7s'
              % (r['label'][:46], r['is_ret'], r['oos_ret'],
                 'YES' if r['oos_ret'] > bO['ret'] else 'no'))
    print()
    print('--- marginals: mean ret by TP, by STOP, by TRAIL (pooled) ---')
    for nm, vals, key in (('TP', TPS, 'tp'), ('STOP', STOPS, 'stop'), ('TRAIL', TRAILS, 'trail'),
                          ('TRAILF (frac of MFE peak)', TRAILF, 'trailf')):
        print('  %s' % nm)
        for v in vals:
            sset = [r for r in rows if r[key] == v]
            if sset:
                print('    %-6s %5d cfg  ret %+7.3f  mae %6.3f  mfe %6.3f  win %5.1f%%  hold %6.0f'
                      % ('none' if v is None else '%.2f' % v, len(sset),
                         np.mean([x['ret'] for x in sset]), np.mean([x['mae'] for x in sset]),
                         np.mean([x['mfe'] for x in sset]), np.mean([x['win'] for x in sset]),
                         np.mean([x['hold'] for x in sset])))
    return rows


if __name__ == '__main__':
    av = sys.argv[1:]
    stg = av[av.index('--stage') + 1] if '--stage' in av else 'A'
    L, ts, px, s6, trades = load()
    TICK = tick_rule(px)
    globals()['TICK'] = TICK
    print('lines %d bars  %s -> %s   evt density %.3f   trades %d'
          % (len(ts), U(ts[0]), U(ts[-1]), L['evt'].mean(), len(trades)))
    if stg == 'A':
        stage_A(L, ts, px, s6, trades, av)
    elif stg == 'ALL':
        A = stage_A(L, ts, px, s6, trades, av)
        # SEEDS: the single best mechanic per leg, by full-tape mean ret. One per leg so stage B and C
        # explore the gate and the race rather than re-exploring the wobble.
        best = {}
        for r in A:
            if r['leg'] not in best or r['ret'] > best[r['leg']]['ret']:
                best[r['leg']] = r
        order = sorted(best.values(), key=lambda r: -r['ret'])
        seeds = [(r['leg'], r['H'], r['mode'], r['wn']) for r in order[:6]]
        print()
        print('=== SEEDS carried into stage B and C (best mechanic per leg, top 6 legs by ret) ===')
        for r in order[:6]:
            print('  %-46s ret %+7.3f  mae %6.3f  mfe %6.3f  hold %5.0f  IS %+6.3f  OOS %+6.3f'
                  % (r['label'], r['ret'], r['mae'], r['mfe'], r['hold'], r['is_ret'], r['oos_ret']))
        B = stage_B(L, ts, px, s6, trades, av, seeds)
        C = stage_C(L, ts, px, s6, trades, av, seeds)
        D = stage_D(L, ts, px, s6, trades, av, seeds)
        # WINDOWS: baseline + the best of A, the best of B, the best of C, all by full-tape ret.
        cfgs = []
        def mk(leg, H, mode, n):
            fm = {}
            for dr in (1, -1):
                fm[dr] = edges(confirm(side_arrays(L, leg, dr, H, TICK), mode, n))
            return fm
        bA = max(A, key=lambda r: r['ret'])
        cfgs.append(('A:' + bA['label'], mk(bA['leg'], bA['H'], bA['mode'], bA['wn']), None, False))
        if B:
            bB = max(B, key=lambda r: r['ret']); c = bB['cfg']
            gt = {dr: gate_open(L, dr, c['tfs'], tuple(ST_ID[x] for x in c['sts']), c['gw'])
                  for dr in (1, -1)}
            cfgs.append(('B:' + bB['label'][:24], mk(c['leg'], c['H'], c['mode'], c['n']), gt, c['s6']))
        stage_W(L, ts, px, s6, trades, av, cfgs)
