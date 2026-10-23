"""The trades v4-ws5rbackstop creates, chained. Joe 1022: *"I need to see the trades it creates
before giving it the green light"*.

THE EXIT IS AN ASSUMPTION, AND IT IS THE ONLY ONE HERE. No exit mech exists for the backstop: #17
the open mech is held back and v4saviour is a separate mech. `rev-trade` closes the incoming trade
on the fill bar, so if the backstop is the ONLY mech running, each fire closes the trade the
PREVIOUS fire opened. That is what is scored below - a self-chaining sequence, not the machine.
Every other number is measured.

PRICES. Entry and exit take the tape's __close__, the RAW unsmoothed source. MAE and MFE take the
klines' high and low over the holding bars. Both come off disk; nothing is modelled.

usage: v4_backstop_trades.py '2026-08-30 00:00:00' '2026-09-06 23:59:55' window
"""
import sys
import datetime as dt
import io
import os

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import ln
import v4_knobs as K
import v4_backstop as BS
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.orchestration.rpl_cache import TAPE_DIR, CACHE_DIR, _tape_key
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e

EM = int(dt.datetime.strptime(os.environ.get('LG_TAPE_END', '2026-10-05'), '%Y-%m-%d')
         .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def prices():
    """-> (close, hi, lo) on the 5 s grid, all read off disk."""
    _s = sys.stderr; sys.stderr = io.StringIO()
    db = DatabaseManager(**get_db_config()); db.connect()
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system '
                    'WHERE sys_pk=1', fetch=True)[0]
    db.disconnect(); sys.stderr = _s
    z = np.load(os.path.join(TAPE_DIR, _tape_key(EM, HOURS, WARMUP,
                {'src': sy['s'], 'len': sy['l']}) + '.npz'))
    close = np.asarray(z['__close__'], float)
    y = np.load(os.path.join(CACHE_DIR, 'klines_hl.npz'))
    j = np.searchsorted(np.asarray(y['t'], np.int64), ln.ts, side='right') - 1
    ok = j >= 0
    hi = np.full(len(ln.ts), np.nan); lo = np.full(len(ln.ts), np.nan)
    hi[ok] = np.asarray(y['h'], float)[j[ok]]
    lo[ok] = np.asarray(y['l'], float)[j[ok]]
    return close, hi, lo


def chain(fires, close, hi, lo):
    """Each fire closes the trade the previous fire opened. -> the closed trades, chronological."""
    out = []
    for a, b in zip(fires, fires[1:]):
        en, ex = a['fire'] + 1, b['fire']          # rev-trade opens the bar AFTER the fill
        if ex <= en:
            continue
        d = 1 if a['dir'] == 'LONG' else -1
        p0, p1 = float(close[en]), float(close[ex])
        h = float(np.nanmax(hi[en:ex + 1])); l = float(np.nanmin(lo[en:ex + 1]))
        net = (p1 - p0) / p0 * 100.0 * d
        mfe = ((h - p0) if d > 0 else (p0 - l)) / p0 * 100.0
        mae = ((l - p0) if d > 0 else (p0 - h)) / p0 * 100.0
        out.append({'en': en, 'ex': ex, 'dir': a['dir'], 'p0': p0, 'p1': p1,
                    'net': net, 'mfe': mfe, 'mae': mae,
                    'bars': ex - en + 1, 'why_in': a, 'why_out': b})
    return out


if __name__ == '__main__':
    A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
    ow = sys.argv[3]
    R = {t: ln.line('ws%dr' % t) for t in (1, 2, 3, 5)}
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    f = BS.scan(A, B, R, MG, ln.U, 'lift', ow)
    tr = chain(f, close, hi, lo)
    print('# control ws5r 2026-09-03 00:35:00 = %.2f (DB-ruled known-good 12.48; the BANKED k6 rsi8 stc6 line reads 6.77 there)'
          % R[5][ln.K('2026-09-03 00:35:00')])
    print('# RULED_OK %s. oob_when %r. %s .. %s' % (K.RULED_OK, ow, ln.U(A), ln.U(B)))
    print('# THE EXIT IS THE NEXT BACKSTOP FIRE. No exit mech exists - this is the backstop')
    print('#   chained to itself, not the machine.')
    print()
    print('| the entry | dir | entry px | the exit | exit px | bars | net %% | MFE %% | MAE %% |')
    print('|---|---|---|---|---|---|---|---|---|')
    for t in tr:
        print('| %s | %s | %.5f | %s | %.5f | %d | %+.3f | %+.3f | %+.3f |'
              % (ln.U(t['en']), t['dir'], t['p0'], ln.U(t['ex']), t['p1'], t['bars'],
                 t['net'], t['mfe'], t['mae']))
    if not tr:
        sys.exit(0)
    n = np.array([t['net'] for t in tr]); mf = np.array([t['mfe'] for t in tr])
    ma = np.array([t['mae'] for t in tr]); bb = np.array([t['bars'] for t in tr])
    print()
    print('| the summary | value |')
    print('|---|---|')
    print('| trades | %d |' % len(tr))
    print('| the last fire is still open | %s |' % ln.U(f[-1]['fire'] + 1))
    print('| net, summed | %+.3f%% |' % n.sum())
    print('| net, mean | %+.4f%% |' % n.mean())
    print('| winners | %d of %d |' % (int((n > 0).sum()), len(n)))
    print('| the best | %+.3f%% |' % n.max())
    print('| the worst | %+.3f%% |' % n.min())
    print('| MFE, mean | %+.3f%% |' % mf.mean())
    print('| MAE, mean | %+.3f%% |' % ma.mean())
    print('| MFE over MAE, on the means | %.2f |' % (mf.mean() / abs(ma.mean())))
    print('| the hold, median | %d bars = %d s |' % (int(np.median(bb)), int(np.median(bb)) * 5))
    print('| LONG trades | %d, net %+.3f%% |'
          % (sum(1 for t in tr if t['dir'] == 'LONG'),
             sum(t['net'] for t in tr if t['dir'] == 'LONG')))
    print('| SHORT trades | %d, net %+.3f%% |'
          % (sum(1 for t in tr if t['dir'] == 'SHORT'),
             sum(t['net'] for t in tr if t['dir'] == 'SHORT')))
