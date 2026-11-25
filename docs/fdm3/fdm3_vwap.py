"""fdm3-htf-oracle's two VWAP columns - HIS 1124/1125.

HIS WORDS: *"research VWAP.  we'll be adding its data to the fdm3-htf-oracle table, in 2 new columns on the far right"* /
*"the anchors will be retrospectively set based on the ws10Mage and ws5Mage ib to opposing ib sweep-pivots. there will
always be exactly 2 VWAPs for both ws10 and ws5, and they will also be exactly 1 pivot apart (the full swing).  there will
always be a pair of vwap anchors: the lowside and the following highside anchored-vwap, for both ws10 and ws5"* /
*"as a new pivot is discovered, the VWAP will anchor on the extremum just before the pivot"* / *"the walkback will jump
back in 3 TF-bars at a time, with a final 4 TF-bar confirmation"* / *"the bands are using the standard deviation "bands
calculation mode""* / *"the bands multiplier is 2, the source is closed"* / *"each value represents the distance between
each line, and price (not pxs)"* / *"I'm using VWAP to validate the oracle's decisions, so 1m makes the most sense"*.

HIS ANSWERS, 1124/1125:
    the columns   ws5 and ws10 ("ws10"), *"Both, 6 rows per cell"*, *"Low VWAP on top"*, *"Taller rows"*
    the pivots    *"there's a mode that builds pivots from "cross to ib" to opposing "cross to ib""* on *"Closed Mage
                  bars"*: an oob run of the closed ws{TF}Mage (15/85) counts only when it goes more than DEPTH points
                  past the fence, his *"0.5"* - it drops the ws10 2026-09-06 06:30 dip (0.19 deep), *"good catch - my eyes
                  didn't see the small-dwell at 0630"*. A pivot is the closed bar the Mage is back in ib on. Each new
                  pivot of one side replaces that side's anchor, so the pair is *"Latest low + latest high"*
    the anchor    the walk from the pivot bar (below), *"Pivot bar is enough"*; then the extreme 1-minute candle inside
                  the TF bar the walk lands on - his chart anchor 2026-09-05 04:13 for the ws10 low in the 04:10 bar
    the VWAP      on 1-minute candles from the anchor candle, source close, bands = VWAP +/- 2 x the volume-weighted
                  standard deviation of close since the anchor (*"Use it, I'll send a reading"*). His seven chart
                  readings off the 2026-09-05 04:13 anchor match to within 0.08% (scratchpad vwap/check_1124.py)
    the distance  *"(price − line) / line"* x 100, price the close of the x:55 bar (*"Close of the x:55 bar"*), the
                  close of the last closed 1-minute candle - the one the lines run through

THE WALK, MY READING of his rule, flagged until he rules on it: from the pivot bar, jump back WALK_STEP (3) TF-bars at a
time while that block holds a lower low (LOW) / higher high (HIGH) than the best so far; then look WALK_CONF (4) bars
further back as the confirmation; the anchor bar is the most extreme bar from there up to the pivot bar. It reproduces
all four of his eyeballed anchors (ws10 2026-09-05 04:10 low and 2026-09-06 12:40 high, ws5 2026-09-05 11:40 low and
12:55 high). MINE too: the first candle on a tie.

CAUSAL: a pivot is knowable from the 5 s bar after its closed TF bar ends; a row uses only pivots knowable at its read
bar (the x:55 bar), and the lines run through the last 1-minute candle closed at that bar. Both are asserted.

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
TFS = (5, 10)                    # HIS 1124 the two columns, ws5 then ws10
DEPTH = 0.5                      # HIS 1125 points past 15 / 85 an oob run must go beyond to count
WALK_STEP, WALK_CONF = 3, 4      # HIS 1124 TF-bars per jump, and the final confirmation
MULT = 2.0                       # HIS 1124 the bands multiplier
CANDLE_MS = 60000                # HIS 1125 1-minute candles
BLANK = -32768                   # int16: no value (no pair of anchors yet)


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


def _tf_bars(tf, ts):
    """Closed TF bars on the midnight grid. -> (first 5 s bar, last 5 s bar) per TF bar."""
    s = tf * 60000
    b0 = (ts // s) * s
    st = np.concatenate([[0], np.flatnonzero(np.diff(b0)) + 1])
    en = np.concatenate([st[1:], [len(ts)]]) - 1
    return st, en


def pivots(tf, mage, ts):
    """HIS cross-to-ib pivots on the CLOSED ws{tf}Mage. -> [(pivot TF bar, side -1 LOW / +1 HIGH)], in order.

    A run of closed bars at or under 15 (LOW) / at or over 85 (HIGH) counts when it goes more than DEPTH past the fence;
    its pivot is the first closed bar back in ib after it. A run that ends on a NaN, or runs into the other oob, makes
    no pivot (MINE)."""
    st, en = _tf_bars(tf, ts)
    M = np.asarray(mage, float)[en]
    out, i = [], 0
    while i < len(M):
        if not np.isfinite(M[i]) or 15.0 < M[i] < 85.0:
            i += 1
            continue
        sd = -1 if M[i] <= 15.0 else 1
        j = i
        while j + 1 < len(M) and np.isfinite(M[j + 1]) and ((M[j + 1] <= 15.0) if sd < 0 else (M[j + 1] >= 85.0)):
            j += 1
        seg = M[i:j + 1]
        depth = (15.0 - seg.min()) if sd < 0 else (seg.max() - 85.0)
        k = j + 1
        if depth > DEPTH and k < len(M) and np.isfinite(M[k]) and 15.0 < M[k] < 85.0:
            out.append((k, sd))
        i = j + 1
    return out


def walk(P, p, side):
    """MY reading of his walk-back. P the TF bars' lows (LOW) or highs (HIGH), p the pivot bar. -> the anchor TF bar."""
    better = (lambda a, b: a < b) if side < 0 else (lambda a, b: a > b)
    best, k = P[p], p
    while k - WALK_STEP >= 0:
        blk = P[k - WALK_STEP:k]
        v = blk.min() if side < 0 else blk.max()
        if better(v, best):
            best, k = v, k - WALK_STEP
            continue
        break
    c0 = max(0, k - WALK_CONF)
    blk = P[c0:k]
    if blk.size and better(blk.min() if side < 0 else blk.max(), best):
        k = c0
    seg = P[k:p + 1]
    return k + int(np.argmin(seg) if side < 0 else np.argmax(seg))


def anchors(tf, ts, hi, lo, mage):
    """Every anchor of one TF. -> [(knowable 5 s bar, side, anchor candle index, pivot TF bar, anchor TF bar)]."""
    st, en = _tf_bars(tf, ts)
    H, L = np.maximum.reduceat(hi, st), np.minimum.reduceat(lo, st)
    cst, cen = _tf_bars(CANDLE_MS // 60000, ts)
    CH, CL = np.maximum.reduceat(hi, cst), np.minimum.reduceat(lo, cst)
    out = []
    for p, sd in pivots(tf, mage, ts):
        k = walk(L if sd < 0 else H, p, sd)
        a, z = np.searchsorted(cst, st[k]), np.searchsorted(cst, en[k], side='right')   # the 1m candles inside bar k
        seg = CL[a:z] if sd < 0 else CH[a:z]
        cand = a + int(np.argmin(seg) if sd < 0 else np.argmax(seg))
        out.append((int(en[p]) + 1, sd, int(cand), int(p), int(k)))
    return out


def rows(prt, ts, close, hi, lo, vol, mage_of):
    """The two columns. -> {tf: int16 [rows, 6]}: lo udist, lo vdist, lo ldist, hi udist, hi vdist, hi ldist, % x 100.

    `prt` the rows' print bars; each row reads the bar before it (x:55) and the 1m candles closed there."""
    cst, cen = _tf_bars(CANDLE_MS // 60000, ts)
    C = close[cen]
    V = np.add.reduceat(vol, cst)
    cv = np.concatenate([[0.0], np.cumsum(C * V)])
    cw = np.concatenate([[0.0], np.cumsum(V)])
    cvv = np.concatenate([[0.0], np.cumsum(V * C * C)])
    rd = np.asarray(prt, np.int64) - 1                              # the read bar, x:55
    last = np.searchsorted(cen, rd, side='right') - 1              # the last 1m candle closed at the read bar
    assert (cen[last] <= rd).all(), 'a row reads a candle that has not closed'
    px = close[rd]
    out = {}
    for tf in TFS:
        an = anchors(tf, ts, hi, lo, mage_of(tf))
        res = np.full((len(rd), 6), BLANK, np.int16)
        for j, sd in enumerate((-1, +1)):                           # HIS "Low VWAP on top"
            kn = np.asarray([x[0] for x in an if x[1] == sd], np.int64)
            ca = np.asarray([x[2] for x in an if x[1] == sd], np.int64)
            i = np.searchsorted(kn, rd, side='right') - 1           # the latest pivot of this side knowable at the row
            ok = i >= 0
            a = np.where(ok, ca[np.maximum(i, 0)], 0)
            assert (kn[np.maximum(i, 0)][ok] <= rd[ok]).all(), 'a row reads a pivot before it is knowable'
            assert (a[ok] <= last[ok]).all(), 'an anchor candle is after the last closed candle'
            w = cw[last + 1] - cw[a]
            ok &= w > 0
            with np.errstate(invalid='ignore', divide='ignore'):
                vw = (cv[last + 1] - cv[a]) / w
                sdv = np.sqrt(np.maximum((cvv[last + 1] - cvv[a]) / w - vw * vw, 0.0))
                for q, line in enumerate((vw + MULT * sdv, vw, vw - MULT * sdv)):   # upper, vwap, lower
                    d = np.round((px - line) / line * 100.0 * 100.0)
                    good = ok & np.isfinite(d)
                    assert (np.abs(d[good]) < 32767).all(), 'a distance x 100 does not fit an int16'
                    res[good, 3 * j + q] = d[good].astype(np.int16)
        out[tf] = res
    return out


if __name__ == '__main__':
    t0 = time.time()
    v = volume()
    print('5 s volume: %d bars, sum %.0f, %s in %.1f s' % (len(v), v.sum(), vol_path(), time.time() - t0))
