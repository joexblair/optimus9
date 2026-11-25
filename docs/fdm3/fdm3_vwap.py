"""fdm3-htf-oracle's VWAP columns - HIS 1124/1125.

HIS WORDS: *"research VWAP.  we'll be adding its data to the fdm3-htf-oracle table, in 2 new columns on the far right"* /
*"as a new pivot is discovered, the VWAP will anchor on the extremum just before the pivot"* / *"the bands are using the
standard deviation "bands calculation mode""* / *"each value represents the distance between each line, and price (not
pxs)"* / *"I'm using VWAP to validate the oracle's decisions, so 1m makes the most sense"*.

HIS 1125, AND WHAT CHANGED:
    the pivots    THE BANKED SWEEP-PIVOTS (his 1125 *"bank this sweep-pivots update and make it the machine"*): the
                  repaired four-read ws5 pivots, v4_sweep_pivots.pivots(5), whose rules are the jig's. This file owns
                  NO pivot logic - his *"there shouldn't be a standalone for sweep pivots"*. The anchor is the 1-minute
                  candle holding the pivot's extremum, as it stood at the row's read bar
    printing      *"it is silent: no values are printed by low vwap A until high vwap A is formed"* / *"when each
                  sameside vwap begins printing, its ancestor sameside vwap is dropped"*: with n pivots found by the
                  read bar, the newest (n-1) is silent and pivots n-2 and n-3 print - one LOW, one HIGH
    the bands     VWAP +/- MULT x the volume-weighted standard deviation of close since the anchor, *"change the band
                  multiplier to 1.7, on src:close"* - his chart's lines had been on src low (*"now I see the issue.  the
                  indicators I had were set to src:low"*); 1.82 before
    the column    ws5 only, his *"drop the ws10Mage column"*
    the diff      *"this column will show if the last row and the current row have reversed, by how much"*, his answer
                  *"The change flips from rising to falling, or back."*, and *"to test the idea of smoothing, build a 2nd
                  row (of the 3 column fixed width table) built on a DEMA len 2 smoothing line"*: per value, this row minus the last row - row 1 on the printed values, row 2 on
                  their DEMA (the jig's IndicatorComputer.dema, length DEMA_LEN). A reversal is a change whose
                  direction is opposite to the last non-zero change (MINE: a flat change carries the direction; the
                  direction is read off the printed 0.01 value)
    the cells     BANKED: the SHORT cell lo u, lo v, lo l and the LONG cell hi u, hi v, hi l - his *"I think I've
                  errored when I requested the swap of `lo l` and `hi l`"* and his clone on 8796, *"8796 is the correct
                  mech"*. His swap (*"swap the `lo l` table rows with `hi l`"*) is `swap=True`, kept for 8795 only. The
                  diff column follows the cell (*"Follow the swap"*)
    the distance  *"(price − line) / line"* x 100, the lines through the row's own 1-minute candle (the last one
                  closed at the x:55 read bar). PRICE IS THAT CANDLE'S WICK: *"the wicks must be included in the pct
                  calculations"* / *"always high for LONG, always low for SHORT"* - every line of the long cell from the
                  candle's high, every line of the short cell from its low. Until 1125 it was the x:55 close

CAUSAL, asserted: a row reads only pivots found by its read bar, their extremum as it stood then, and 1-minute candles
closed by then.

VOLUME: the tape carries none, so the 5 s volume comes from the database's kline_collection, once, into its own file
beside the fdm3-htf-oracle line cache, checked against the tape's own close bar for bar.
"""
import io
import json
import os
import sys
import time

import numpy as np

V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
for _p in ('/home/joe/thecodes', V4):
    if _p not in sys.path:
        sys.path.insert(0, _p)
ROOT = '/home/joe/thecodes/optimus9/orchestration/.rpl_cache/fdm3_htf'
TFS = (5,)                       # HIS 1125 *"drop the ws10Mage column"*
MULT = 1.7                       # HIS 1125 *"change the band multiplier to 1.7, on src:close"* (was 1.82, his *"use 1.82 as the band multiplier"*)
DEMA_LEN = 2                     # HIS 1125 *"a DEMA len 2 smoothing line"*
CANDLE_MS = 60000                # HIS 1125 1-minute candles
BLANK = -32768                   # int16: no value (no VWAP printing yet, or no last row)


def _ln():
    _e = sys.stderr; sys.stderr = io.StringIO()
    try:
        import ln
    finally:
        sys.stderr = _e
    return ln


def vol_path():
    ln = _ln()
    return os.path.join(ROOT, 'vol5s_em%d_n%d.npy' % (ln.EM, ln.N))


def build_volume():
    """The 5 s volume on the tape's grid, from kline_collection, written once. -> array."""
    ln = _ln()
    import v4_backstop_trades as BT
    _e = sys.stderr; sys.stderr = io.StringIO()
    try:
        from optimus9.db.database_manager import DatabaseManager
        from optimus9.config import get_db_config
    finally:
        sys.stderr = _e
    ts = np.asarray(ln.ts, np.int64)
    db = DatabaseManager(**get_db_config()); db.connect()
    r = db.execute('SELECT kc_timestamp t, kc_close c, kc_volume v FROM kline_collection WHERE kc_tp_pk=1 AND '
                   'kc_timestamp >= %s AND kc_timestamp <= %s ORDER BY kc_timestamp', (int(ts[0]), int(ts[-1])), fetch=True)
    db.disconnect()
    t = np.asarray([x['t'] for x in r], np.int64)
    assert np.array_equal(t, ts), "kline_collection is not the tape's 5 s grid"
    c = np.asarray([float(x['c']) for x in r]); v = np.asarray([float(x['v']) for x in r])
    close = np.asarray(BT.prices()[0], float)
    assert np.array_equal(c, close), ('kline_collection close differs from the tape close on %d bars'
                                      % int((c != close).sum()))
    assert np.isfinite(v).all() and (v >= 0).all()
    os.makedirs(ROOT, exist_ok=True)
    p = vol_path()
    np.save(p + '.part.npy', v)
    os.rename(p + '.part.npy', p)
    json.dump({'n': int(len(v)), 'sum': float(v.sum()), 'ts0': int(ts[0]), 'ts1': int(ts[-1]),
               'control': 'kc_timestamp = tape ts and kc_close = tape close on every bar',
               'built_at': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}, open(p[:-4] + '.json', 'w'), indent=1)
    return v


def volume():
    """-> the 5 s volume, from its file (built once from the database), checked against its manifest."""
    p = vol_path()
    if not os.path.exists(p):
        build_volume()
    v = np.asarray(np.load(p), float)
    man = json.load(open(p[:-4] + '.json'))
    ln = _ln()
    assert len(v) == man['n'] == ln.N and float(v.sum()) == man['sum'], 'the 5 s volume file has changed'
    return v


def _jig():
    _e = sys.stderr; sys.stderr = io.StringIO()
    try:
        from optimus9.analysis import jig as J
    finally:
        sys.stderr = _e
    return J


def printing(piv, rd):
    """HIS 1125 the silent / printing / dropped schedule. -> {side: (pivot index or -1) per read bar}.

    With n pivots found by the read bar, pivot n-1 is silent and pivots n-2 and n-3 print, one per side."""
    F = np.asarray([p['found'] for p in piv], np.int64)
    assert (np.diff(F) > 0).all(), 'the pivots are not found in order'
    n = np.searchsorted(F, np.asarray(rd, np.int64), side='right')
    sides = np.asarray([p['side'] for p in piv], np.int64)
    out = {-1: np.full(len(rd), -1, np.int64), 1: np.full(len(rd), -1, np.int64)}
    for k in (2, 3):
        i = n - k
        ok = i >= 0
        for sd in (-1, 1):
            m = ok & (sides[np.maximum(i, 0)] == sd)
            out[sd][m] = i[m]
    for sd in (-1, 1):
        g = out[sd] >= 0
        assert (F[out[sd][g]] <= np.asarray(rd)[g]).all(), 'a row prints a pivot that is not found yet'
        assert (F[np.minimum(out[sd][g] + 1, len(F) - 1)] <= np.asarray(rd)[g]).all(), 'a row prints a silent VWAP'
    return out


def rows(prt, ts, close, hi, lo, vol, piv, swap=False):
    """The ws5 VWAP column and its diff. -> dict:
         pct    int16 [rows, 6]  the SHORT cell lo u, lo v, hi l from the candle's low, then the LONG cell hi u, hi v,
                                 lo l from its high - % x 100
         raw    int16 [rows, 6]  this row's printed value minus the last row's
         dema   int16 [rows, 6]  the same on the DEMA_LEN DEMA of each value
         flags  uint16 [rows]    bit q (raw) and bit 6 + q (dema): a reversal
         lo, hi                  each row's printing pivot index per side (-1 none)

    `prt` the rows' print bars; each row reads the bar before it (x:55) and the 1m candles closed there.
    `swap` False, THE BANK (his 1125 *"8796 can be banked"*): his clone *"swap `lo l` and `hi l` back to their original
    trades (short and long respectively)"* - the short cell lo u, lo v, lo l from the low, the long cell hi u, hi v, hi l
    from the high. True is the swap he retracted, *"swap the `lo l` table rows with `hi l`"* (8795)."""
    J = _jig()
    cst, cen = J.tf_bars(ts, CANDLE_MS // 60000)
    C = close[cen]
    V = np.add.reduceat(vol, cst)
    cv = np.concatenate([[0.0], np.cumsum(C * V)])
    cw = np.concatenate([[0.0], np.cumsum(V)])
    cvv = np.concatenate([[0.0], np.cumsum(V * C * C)])
    rd = np.asarray(prt, np.int64) - 1                              # the read bar, x:55
    last = np.searchsorted(cen, rd, side='right') - 1              # the last 1m candle closed at the read bar
    assert (cen[last] <= rd).all(), 'a row reads a candle that has not closed'
    CHc = np.maximum.reduceat(np.asarray(hi, float), cst)[last]   # HIS 1125 the row's 1m candle's wicks
    CLc = np.minimum.reduceat(np.asarray(lo, float), cst)[last]
    assert np.isfinite(CHc).all() and np.isfinite(CLc).all() and (CHc >= CLc).all(), 'a 1m candle has no high / low'
    sched = printing(piv, rd)
    LN = {}                                                          # (side, 'u'/'v'/'l') -> the line per row
    for j, sd in enumerate((-1, 1)):
        idx = sched[sd]
        ext = np.full(len(rd), -1, np.int64)
        for i in np.unique(idx[idx >= 0]):
            m = idx == i
            hb = np.asarray([b for b, _ in piv[i]['hist']], np.int64)
            he = np.asarray([e for _, e in piv[i]['hist']], np.int64)
            k = np.searchsorted(hb, rd[m], side='right') - 1
            assert (k >= 0).all(), 'a row reads a pivot extremum before it was found'
            ext[m] = he[k]
        ok = ext >= 0
        assert (ext[ok] <= rd[ok]).all(), 'an anchor extremum is after the read bar'
        a = np.searchsorted(cst, np.maximum(ext, 0), side='right') - 1      # the 1m candle holding the extremum
        assert (a[ok] <= last[ok]).all(), 'an anchor candle is after the last closed candle'
        w = cw[last + 1] - cw[np.maximum(a, 0)]
        ok &= w > 0
        with np.errstate(invalid='ignore', divide='ignore'):
            vw = (cv[last + 1] - cv[np.maximum(a, 0)]) / w
            sdv = np.sqrt(np.maximum((cvv[last + 1] - cvv[np.maximum(a, 0)]) / w - vw * vw, 0.0))
            for nm, line in zip('uvl', (vw + MULT * sdv, vw, vw - MULT * sdv)):   # upper, vwap, lower
                LN[(sd, nm)] = np.where(ok, line, np.nan)
    pct = np.full((len(rd), 6), BLANK, np.int16)
    flt = np.full((len(rd), 6), np.nan)
    CELLS = ((CLc, ((-1, 'u'), (-1, 'v'), (1 if swap else -1, 'l'))),    # SHORT: lo u, lo v, hi l (lo l) from the low
             (CHc, ((1, 'u'), (1, 'v'), (-1 if swap else 1, 'l'))))     # LONG: hi u, hi v, lo l (hi l) from the high
    for c, (px, cell) in enumerate(CELLS):
        for q, key in enumerate(cell):
            line = LN[key]
            with np.errstate(invalid='ignore', divide='ignore'):
                d = (px - line) / line * 100.0
            good = np.isfinite(d)
            assert (np.abs(d[good]) * 100 < 32767).all(), 'a distance x 100 does not fit an int16'
            flt[good, 3 * c + q] = d[good]
            pct[good, 3 * c + q] = np.round(d[good] * 100.0).astype(np.int16)
    from optimus9.compute.indicator_computer import IndicatorComputer as IC
    raw = np.full((len(rd), 6), BLANK, np.int16)
    dem = np.full((len(rd), 6), BLANK, np.int16)
    flags = np.zeros(len(rd), np.uint16)
    for q in range(6):
        x = pct[:, q].astype(np.int64)
        okx = x != BLANK
        dr = np.full(len(rd), np.nan)
        both = okx[1:] & okx[:-1]
        dr[1:][both] = (x[1:] - x[:-1])[both]
        sm = np.asarray(IC.dema(flt[:, q], DEMA_LEN), float)
        dd = np.full(len(rd), np.nan)
        dd[1:] = np.round((sm[1:] - sm[:-1]) * 100.0)
        dd[~okx] = np.nan
        for r, (arr, out) in enumerate(((dr, raw), (dd, dem))):
            g = np.isfinite(arr)
            out[g, q] = arr[g].astype(np.int16)
            sg = np.where(g, np.sign(np.nan_to_num(arr)), 0).astype(np.int64)
            prev, rev = 0, np.zeros(len(rd), bool)
            for t in np.flatnonzero(sg):
                if prev and sg[t] != prev:
                    rev[t] = True
                prev = sg[t]
            flags |= (rev.astype(np.uint16) << np.uint16(6 * r + q))
    return {'pct': pct, 'raw': raw, 'dema': dem, 'flags': flags, 'lo': sched[-1], 'hi': sched[1]}


if __name__ == '__main__':
    t0 = time.time()
    v = volume()
    print('5 s volume: %d bars, sum %.0f, %s in %.1f s' % (len(v), v.sum(), vol_path(), time.time() - t0))
