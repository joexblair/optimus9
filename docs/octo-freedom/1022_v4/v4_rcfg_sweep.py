"""STEP 2: does the r-line CONFIG move the trade list at all? 27 configs, the mech knobs at the bank.

Joe 1022: *"how long would it take to build a cache that sweeps the r line config?  ranges of 3
(current, current-1, current+1)"* / *"I'm fine with 27 configs alone"*.

THE AXIS. The banked ws{tf}r spec is `(tf*60, ('k', 5, 8, 7, 'close'), 'emerging')`. This sweeps
(k, rsi, stc) at +/-1 each, 3 x 3 x 3 = 27, over ws1r..ws30r. 726 of the 810 line arrays are not
in the cache and are built first - measured at 0.49 s a line, 24 to a Jig context.

WHAT IS HELD, and all of it deliberately:
  the mech knobs   every v4 knob stays at the bank. This asks ONE question - whether the r config
                   moves anything - and crossing it with the mech axes is the 6-hour run.
  the Mage lines   the cascade reads ws1Mage-ws12Mage at the BANKED Mage spec. This sweep moves the
                   r lines only, so a config's cascade verdict is read off un-swept Mage. Flagged
                   to Joe rather than silently crossed.
  the scorer       swing pct 2.0 and the pseudo stop 1.1. Sweeping them would optimise the scorer,
                   not the mech - the two-stage rule.

THIS IS A MEASUREMENT, NOT A RESULT. It runs the FULL TAPE with no hold-out, because the question
is "does this axis matter", not "which config is best". No config may be selected from it.

usage: v4_rcfg_sweep.py <out.md>
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
import v4_swing_score as SS
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.line_config import override, KLine
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
from optimus9.orchestration.rpl_cache import cache_jig_perline, LINE_DIR, _line_key
sys.stderr = _e

EM = int(dt.datetime.strptime('2026-10-05', '%Y-%m-%d')
         .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
K0, R0, S0 = K.R_RSI, K.R_STC, K.R_KLEN    # the trip slots: (rsi, stc, k_len) - BANKED 1023
#   Joe 1023: *"bank k6 rsi8 stc6"*. It lives in the knob bank so an off-ruled config REFUSES
#   like every other knob. `cfgs()` is centred on it, so the grid moved with the bank: k 5/6/7 and
#   stc 5/6/7 now, where it was k 4/5/6 and stc 6/7/8. The k7 and stc5 arrays are NOT built - the
#   1023 sweep in out/accounts.md is the OLD grid and is not re-run here.
TFS = list(range(1, 31))
PCT, CAP = 2.0, 1.1                        # HELD


def cfgs():
    return [(k, r, s) for k in (K0-1, K0, K0+1) for r in (R0-1, R0, R0+1) for s in (S0-1, S0, S0+1)]


def spec(tf, trip):
    """One line override for a trip. `trip` is (rsi, stc, k_len) - the LEGACY TUPLE'S OWN ORDER.

    BUILT THROUGH THE NAMED FORM so it cannot transpose again. The hand-written positional tuple
    here is what reintroduced the exact bug line_config.py was written to kill, and the 1023 audit
    found every sweep column labelled with the wrong parameter for a day. KLine names what it
    means; the tuple it emits is byte-identical to what was built, so no cached array moves.
    """
    rsi, stc, k_len = trip
    return override(tf * 60, KLine(k_len=k_len, rsi=rsi, stc=stc, src='close'), 'emerging')


def build(trips, log):
    """build every missing line array, in Jig contexts of 24."""
    ovr = {}
    for trip in trips:
        for tf in TFS:
            ovr['sw%d_%d_%d_%d' % (tf, trip[0], trip[1], trip[2])] = spec(tf, trip)
    miss = [n for n in ovr
            if not os.path.exists(os.path.join(LINE_DIR,
                                               _line_key(EM, HOURS, WARMUP, ovr[n]) + '.npy'))]
    log('# %d line arrays wanted, %d already cached, %d to build'
        % (len(ovr), len(ovr) - len(miss), len(miss)))
    t0 = time.time()
    done = 0
    for i in range(0, len(miss), 24):
        batch = {n: ovr[n] for n in miss[i:i + 24]}
        _s = sys.stderr; sys.stderr = io.StringIO()
        cache_jig_perline(EM, HOURS, WARMUP, batch, pxs_cfg={'src': 'close', 'len': 2})
        sys.stderr = _s
        done += len(batch)
        log('# built %d of %d, %.0f s elapsed' % (done, len(miss), time.time() - t0))
    log('# the build took %.0f s' % (time.time() - t0))


def load(trip):
    """ws1r..ws30r at one config, read off disk."""
    out = {}
    for tf in TFS:
        p = os.path.join(LINE_DIR, _line_key(EM, HOURS, WARMUP, spec(tf, trip)) + '.npy')
        out[tf] = np.asarray(np.load(p, mmap_mode='r'), float)[:ln.N]
    return out


def arm(R, MG, close, A, B):
    """one config -> the trade stats. The mech knobs are the bank's."""
    F.reset()
    f = F.scan(A, B, R, MG, 'window')
    rows = []
    for d in f:
        v, bar = F.walk(R, 5, d['side'], d['rev'], B)
        unres = (v == 'EXHAUST' and bar is not None and bar >= B - 1)
        rows.append({'fire': d['fire'], 'rev': d['rev'], 'side': d['side'], 'dir': d['dir'],
                     'verdict': 'UNRESOLVED' if unres else v,
                     'exh': None if unres else bar})
    acc = DT.accept(rows)
    sc, _ = SS.score(acc, close, PCT)
    st = [dict(t) for t in sc]
    for t in st:
        t['stopped'] = t['mae'] <= -CAP
        if t['stopped']:
            t['mae'], t['mfe'] = -CAP, 0.0
    if not st:
        return {'fires': len(f), 'exh': sum(1 for r in rows if r['verdict'] == 'EXHAUST'),
                'trades': 0, 'pos': 0, 'mfe': 0.0, 'mae': 0.0, 'ratio': 0.0}
    mf = np.array([t['mfe'] for t in st]); ma = np.array([t['mae'] for t in st])
    return {'fires': len(f), 'exh': sum(1 for r in rows if r['verdict'] == 'EXHAUST'),
            'trades': len(st), 'pos': int(sum(1 for t in st if not t['stopped'])),
            'mfe': float(mf.mean()), 'mae': float(ma.mean()),
            'ratio': float(mf.mean() / abs(ma.mean())) if ma.mean() else 0.0}


if __name__ == '__main__':
    out = open(sys.argv[1], 'w', buffering=1)

    def log(s):
        out.write(s + '\n'); print(s, flush=True)

    trips = cfgs()
    log('# the r-config sweep, %d configs, the mech knobs at the bank. RULED_OK %s'
        % (len(trips), K.RULED_OK))
    log('# HELD: swing pct %.1f, the pseudo stop %.1f, the Mage spec, every v4 knob.' % (PCT, CAP))
    log('# the FULL TAPE, no hold-out. This is a measurement of whether the axis matters.')
    build(trips, log)
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    A, B = 0, ln.N - 1
    log('')
    log('| k | rsi | stc | fires | EXHAUST | trades | positives | MFE mean %% | MAE mean %% | MFE over MAE |')
    log('|---|---|---|---|---|---|---|---|---|---|')
    t0 = time.time()
    for i, trip in enumerate(trips, 1):
        R = load(trip)
        q = arm(R, MG, close, A, B)
        mark = ' <- BANKED' if trip == (K0, R0, S0) else ''
        log('| %d | %d | %d%s | %d | %d | %d | %d | %+.3f | %+.3f | %.3f |'
            % (trip[0], trip[1], trip[2], mark, q['fires'], q['exh'], q['trades'], q['pos'],
               q['mfe'], q['mae'], q['ratio']))
        print('# arm %d of %d, %.0f s elapsed' % (i, len(trips), time.time() - t0), flush=True)
    log('# the sweep took %.0f s' % (time.time() - t0))
    out.close()
