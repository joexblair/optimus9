"""emit_dominoes_pine — the LTF-Mage "falling dominoes" filter as a pine overlay. Joe 0801.

WHAT IS DRAWN
  LABELS at the signal bar — DIRECTION, per Joe 0801 ("green and red to define if the signal is
    short or long"; a long firing half-way down a leg must not look like a short).
      green + label_up    LONG   (s4Mage crossed OOB on the LO side at the walk bar)
      red   + label_down  SHORT  (s4Mage crossed OOB on the HI side)
      text  FIRE/- . ret . mae . hold . MFE   (MFE = the row was truly on the MFE side)
  BGCOLOR spans — the FILTER'S CALL, over the trade window (signal bar -> exit bar):
      blue    strict dominoes FIRED
      yellow  no fire
  Colour families are orthogonal: green/red is ONLY direction, blue/yellow is ONLY the filter.

THE FILTER   strict dominoes, read AT the signal bar, causal (all three crossings are at/before it):
  the three LTF Mages entered IB fastest-first —  gcs15M < s30M < s1M  by OOB->IB crossing bar.
  lines: bb 37|0.83|close at TF 0.25 / 0.5 / 1.0 min (rpl_config baseline flavour).

THE SIGNAL   REWALK 2 + gcs15 confirm — the one approved configuration (Joe 0801 "we can't be using both").
  the s15x X s15m cross is the ANCHOR. The SIGNAL is the first gcs15x X gcs15m cross at/after it.
  gcs15x = bb 5|0.37|close, gcs15m = bb 6|0.45|close @ TF 0.25 min = 15 s (the gcs/RPL flavour).
  NOT exhv2's x bb 4|0.37, and NOT gcs15M (the 37|0.83 LTF Mage above — different line, similar name).
  rows with no gcs15 cross after the anchor are counted and printed, never dropped silently.

THE TRADE    Joe 0801: "place an immediate trade and close it when [s4M crosses] into OOB".
  ENTRY  the confirmed signal bar
  EXIT   the next bar at which s4Mage HAS BEEN OOB for 240 s (48 bars), strictly after entry.
         Tested on each bar, backward — causal. Was the CROSSING bar, which needed 240 s of future.
         s4Mage = exhv2's own M line, bb 37|0.7|close @ TF4 (build_exhv2.LINE_SPEC['M'])
  DIR    the s4Mage OOB side at the walk bar — NOT the bias, so there is no cycle (Joe 0801)

    python3 emit_dominoes_pine.py [--rewalk 2] [--out dominoes.pine]
"""
import sys, os, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np
import build_exhv2 as B
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import bbline, _Score
from optimus9.orchestration.rpl_cache import cache_jig_perline

MAGES = [('gcs15M', 0.25), ('s30M', 0.5), ('s1M', 1.0)]     # fastest first — the domino order
TF4 = 240_000                                                # bgcolor bucket, ms
I = dict(conf=0, confu=1, walk=4, walku=5, side=6, mfeside=7, sig=28, sigu=29)


def main(argv):
    g = lambda f, d: (type(d)(argv[argv.index(f) + 1]) if f in argv else d)
    mode, out = g('--rewalk', 2), g('--out', 'dominoes.pine')
    HI, LO = R.HI, R.LO

    OUT = B.main(['--rewalk', str(mode)])
    ts = np.asarray(R.L0['ts'], np.int64)
    px = np.asarray(R.L0['src'].pxs, float)
    n = len(ts)

    # s4Mage, built exactly as build_exhv2.py:179-187 does
    _kind, _msp = B.LINE_SPEC['M']
    J4 = cache_jig_perline(R.end_ms, R.HOURS, R.WARMUP, bbline('exhv2M4', 4, **_msp), pxs_cfg=R.PXS_CFG)
    M4 = np.asarray(J4.W.line('exhv2M4'), float)

    # the 240 s test, ON EACH BAR (Joe 0802). B.oob_qualified is the single producer — this file used to
    # carry a hand-copied forward loop, which is how the lookahead survived in three places at once.
    XB = np.flatnonzero(B.oob_qualified(M4, HI, LO))

    ovr = {}
    for nm, tf in MAGES:
        ovr.update(bbline(nm, tf, length=37, mult=0.83, src='close'))
    ovr.update(bbline('gcs15x', 15.0 / 60.0, length=5, mult=0.37, src='close'))   # bbline tf is MINUTES
    ovr.update(bbline('gcs15m', 15.0 / 60.0, length=6, mult=0.45, src='close'))
    JM = cache_jig_perline(R.end_ms, R.HOURS, R.WARMUP, ovr, pxs_cfg=R.PXS_CFG)
    LNM = {nm: np.asarray(JM.W.line(nm), float) for nm, _ in MAGES}

    # gcs15 confirm — rising edges both directions, hoisted out of the row loop (side is the only input)
    GX = np.asarray(JM.W.line('gcs15x'), float); GM = np.asarray(JM.W.line('gcs15m'), float)
    GXC = {}
    for xdr in (-1, 1):                                      # hi walk -> SHORT -> xdr -1
        _c = R.L0['src'].causal.cross_wob(GX - GM, 0.0, xdr, R.WOBN)     # wob_n = 9 bars = 45 s
        GXC[xdr] = np.flatnonzero(_c & ~np.r_[False, _c[:-1]])

    # THE R-PRED — the walk's origin. build_exhv2 reads es_rpred_ms at :262 but does not emit it, so it is
    # re-read here and joined on es_conf_ms = v2_conf_ms. A label needing a field is not a reason to change
    # the producer's schema (Joe 0801).
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.config import get_db_config
    _d = DatabaseManager(**get_db_config()); _d.connect()
    RP = {int(z['es_conf_ms']): z['es_rpred_ms']
          for z in _d.execute('SELECT es_conf_ms, es_rpred_ms FROM rpl_exh_stat', fetch=True)}
    _d.disconnect()

    labels, fire_sp, none_sp = [], [], []
    nf = nl = 0
    nsig = lost = 0
    for ro in OUT:
        if ro[I['sig']] is None:
            continue
        nsig += 1
        side = ro[I['side']]                       # 'hi' -> SHORT, 'lo' -> LONG

        # THE CONFIRM. ro[I['sig']] is the ANCHOR; the SIGNAL is the first gcs15 cross at/after it.
        anchor = int(np.searchsorted(ts, ro[I['sig']]))
        _nc = GXC[-1 if side == 'hi' else 1]
        _nc = _nc[_nc >= anchor]
        if not len(_nc):
            lost += 1
            continue
        sb = int(_nc[0])

        j = []                                     # OOB->IB crossing bar per Mage, at/before the signal
        for nm, _ in MAGES:
            v = LNM[nm]
            oo = (v >= HI) if side == 'hi' else (v <= LO)
            kk = np.flatnonzero(oo[:sb])
            j.append(None if oo[sb] or not len(kk) else int(kk[-1]) + 1)
        dom = all(x is not None for x in j) and j[0] < j[1] < j[2]

        nx = XB[XB > sb]
        eb = int(nx[0]) if len(nx) else None
        if eb is None:
            ret = mae = hold = None
        else:
            seg = px[sb:eb + 1]
            sgn = -1.0 if side == 'hi' else 1.0
            ret = sgn * (px[eb] - px[sb]) / px[sb] * 100.0
            up = (np.nanmax(seg) - px[sb]) / px[sb] * 100.0
            dn = (px[sb] - np.nanmin(seg)) / px[sb] * 100.0
            mae = up if side == 'hi' else dn
            hold = (int(ts[eb]) - int(ts[sb])) / 60000.0
            span = [(int(m) // TF4) * TF4 for m in ts[sb:eb + 1]]
            (fire_sp if dom else none_sp).extend(span)

        long_ = (side == 'lo')
        nl += long_; nf += dom
        # THREE LINES, one fact each. Line 3 carries the SIGNAL TIMESTAMP to seconds: the TF4 bucket is
        # 240 s wide, so a label read off the chart at minute precision cannot be matched back to its row.
        hms = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
        rp = RP.get(int(ro[0]))
        l1 = '%s %s' % ('LONG' if long_ else 'SHORT', 'FIRE' if dom else '-')
        l2 = ''
        if ret is not None:
            l1 += ' ret %+.2f' % ret
            l2 = 'mae %.2f ' % mae
        l2 += dt.datetime.fromtimestamp(int(ts[sb]) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
        if ro[I['mfeside']]:
            l2 += ' MFE'
        labels.append(dict(ts=int(ts[sb]), y=float(px[sb]), long=bool(long_),
                           lines=['rpred %s' % (hms(rp) if rp else '-'), l1, l2]))

    streams = [{'name': 'no_fire', 'ts': none_sp, 'color': 'color.yellow',
                'meaning': 'strict dominoes detector did NOT fire'},
               {'name': 'dominoes_fire', 'ts': fire_sp, 'color': 'color.blue',
                'meaning': 'strict dominoes detector FIRED'}]
    mech = [
        'EVERY LABEL IS A CONFIRMED SIGNAL.  %d s15 anchors -> %d gcs15-confirmed signals.' % (nsig, len(labels)),
        '%d anchors had no gcs15 cross after them and are NOT drawn.' % lost,
        'The bgcolor is the DETECTOR. It is NOT the MFE-side flag — that is the "MFE" suffix on line 3.',
        '',
        'ORDER OF EVENTS  r-pred -> walk to s4Mage-cross-OOB (DIRECTION SET HERE) -> s15 ANCHOR ->',
        '                 gcs15 CONFIRM = the SIGNAL -> exit at the NEXT s4Mage-cross-OOB',
        'strict dominoes  gcs15M < s30M < s1M by OOB->IB crossing bar, all at/before the signal bar',
        '                 lines bb 37|0.83|close at TF 15s / 30s / 60s',
        'gcs15 confirm    gcs15x bb 5|0.37|close, gcs15m bb 6|0.45|close @ TF 15s',
        'EXIT             s4Mage = bb 37|0.7|close @TF4;  held = OOB run >= %d bars = %d s' % (
            B.WALK_DWELL_BARS, B.WALK_DWELL_BARS * 5),
        # span DERIVED from the labels, not a literal. It read '05-18..06-14' — the dial-in tape's range —
        # so any rebuild on a different tape emitted a legend that named the wrong dates.
        'REWALK %d   |   %d rows, %s..%s   |   tape %s' % (
            mode, len(labels),
            dt.datetime.fromtimestamp(min(z['ts'] for z in labels) / 1000, dt.timezone.utc).strftime('%m-%d'),
            dt.datetime.fromtimestamp(max(z['ts'] for z in labels) / 1000, dt.timezone.utc).strftime('%m-%d'),
            R.TAPE) if labels else 'REWALK %d   |   0 rows' % mode,
    ]
    nlab, nbg = _Score(None).emit_direction_overlay(
        labels, streams, out, 'dominoes filter (REWALK %d)' % mode, mechanics=mech, bucket_ms=TF4)
    print('')
    print('%s  ->  %d labels, %d painted TF4 bars' % (out, nlab, nbg))
    print('  anchors         %d   no gcs15 cross after anchor: %d (DROPPED)' % (nsig, lost))
    print('  rows            %d   LONG %d / SHORT %d' % (len(labels), nl, len(labels) - nl))
    print('  dominoes FIRED  %d (%.1f%%)' % (nf, 100.0 * nf / len(labels)))
    # streams carry RAW 5s stamps; emit_direction_overlay buckets a copy. Bucket here too, for the count.
    print('  blue  buckets   %d' % len(_Score.bucket_spans(streams[1]['ts'], TF4)))
    print('  yellow buckets  %d' % len(_Score.bucket_spans(streams[0]['ts'], TF4)))
    return labels, streams


if __name__ == '__main__':
    main(sys.argv[1:])
