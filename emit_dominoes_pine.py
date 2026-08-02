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
  measured lift over the MFE-side base rate: 1.41x ALL / 1.44x OLD / 1.55x FRESH (REWALK 2).

THE TRADE    Joe 0801: "place an immediate trade and close it when [s4M crosses] into OOB".
  ENTRY  the signal bar (v2_sig_ms)
  EXIT   the next HELD s4Mage OOB crossing strictly after entry
         held = the OOB run lasts >= WALK_DWELL_BARS (48 bars = 240 s), build_exhv2.py:272-286
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
    J4 = cache_jig_perline(R.end_ms, 40, 600, bbline('exhv2M4', 4, **_msp), pxs_cfg=R.PXS_CFG)
    M4 = np.asarray(J4.W.line('exhv2M4'), float)

    # held s4Mage OOB crossings — build_exhv2.py:269-286, replicated
    o = (M4 >= HI) | (M4 <= LO)
    rise = o & ~np.r_[False, o[:-1]]
    held = np.zeros(n, bool)
    for z in np.flatnonzero(rise):
        k = z
        while k < n and o[k]:
            k += 1
        if k - z >= B.WALK_DWELL_BARS:
            held[z] = True
    XB = np.flatnonzero(held)

    ovr = {}
    for nm, tf in MAGES:
        ovr.update(bbline(nm, tf, length=37, mult=0.83, src='close'))
    JM = cache_jig_perline(R.end_ms, 40, 600, ovr, pxs_cfg=R.PXS_CFG)
    LNM = {nm: np.asarray(JM.W.line(nm), float) for nm, _ in MAGES}

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
    for ro in OUT:
        if ro[I['sig']] is None:
            continue
        side = ro[I['side']]                       # 'hi' -> SHORT, 'lo' -> LONG
        sb = int(np.searchsorted(ts, ro[I['sig']]))

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
        # TWO LINES (Joe 0801). '\\n' emits the two characters \ n into the pine string literal, which Pine
        # reads as a newline escape; a real newline char would be a raw newline inside "..." and not parse.
        # Line 2 carries the SIGNAL TIMESTAMP to seconds: the TF4 bucket is 240 s wide, so a label read off
        # the chart at minute precision cannot be matched back to its row.
        hms = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
        rp = RP.get(int(ro[0]))
        l0 = 'rpred %s' % (hms(rp) if rp else '-')
        l1 = '%s %s' % ('LONG' if long_ else 'SHORT', 'FIRE' if dom else '-')
        l2 = ''
        if ret is not None:
            l1 += ' ret %+.2f' % ret
            l2 = 'mae %.2f ' % mae
        l2 += dt.datetime.fromtimestamp(int(ts[sb]) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
        if ro[I['mfeside']]:
            l2 += ' MFE'
        labels.append(dict(ts=int(ts[sb]), y=float(px[sb]), text=l0 + '\\n' + l1 + '\\n' + l2,
                           green=bool(long_), up=bool(long_)))

    streams = [{'name': 'no_fire', 'ts': sorted(set(none_sp)), 'color': 'color.yellow'},
               {'name': 'dominoes_fire', 'ts': sorted(set(fire_sp)), 'color': 'color.blue'}]
    # LEGEND FIRST. jig.py:611 splits `notes` on newlines and prefixes each with '// ', so the header is a
    # comment BLOCK, not one long line. Joe 0801: the colour definitions were ~230 chars into a single
    # 700-char line and unreadable in the pine editor without horizontal scrolling.
    notes = '\n'.join([
        'dominoes filter  —  LEGEND',
        '',
        '  EVERY LABEL IS A SIGNAL. All %d rows produced one. The bgcolor says whether the strict-dominoes' % len(labels),
        '  DETECTOR fired on that row — it does NOT say whether a signal exists, and it is NOT the MFE-side flag.',
        '',
        '  BGCOLOR = the DETECTOR, painted over the trade window (signal bar -> exit bar)',
        '    BLUE    strict dominoes detector FIRED       (%d rows, %d TF4 buckets)' % (nf, len(set(fire_sp))),
        '    YELLOW  strict dominoes detector did NOT fire (%d rows, %d TF4 buckets)' % (len(labels) - nf, len(set(none_sp))),
        '    MFE-side is NOT a colour — it is the "MFE" suffix on text line 3.',
        '',
        '  LABELS = DIRECTION, set AT the walk bar = the s4Mage crossing into OOB (NOT the bias, NOT the signal)',
        '    GREEN + arrow up    LONG    (s4Mage crossed OOB on the LO side)   %d rows' % nl,
        '    RED   + arrow down  SHORT   (s4Mage crossed OOB on the HI side)   %d rows' % (len(labels) - nl),
        '    ORDER OF EVENTS:  r-pred  ->  walk to s4Mage-cross-OOB (direction set here)  ->  SIGNAL  ->',
        '                      exit at the NEXT s4Mage-cross-OOB',
        '    text line 1:  rpred HH:MM:SS  (the walk origin)',
        '    text line 2:  LONG/SHORT  FIRE|-  ret %',
        '    text line 3:  mae %  SIGNAL TIMESTAMP (to seconds)  MFE(=row was truly on the MFE side)',
        '',
        'MECHANICS',
        '  strict dominoes  gcs15M < s30M < s1M by OOB->IB crossing bar, all at/before the signal bar',
        '                   lines bb 37|0.83|close at TF 15s / 30s / 60s',
        '  ENTRY  the signal bar',
        '  EXIT   the next HELD s4Mage OOB crossing after entry',
        '         s4Mage = bb 37|0.7|close @TF4;  held = OOB run >= %d bars = %d s' % (
            B.WALK_DWELL_BARS, B.WALK_DWELL_BARS * 5),
        '  REWALK %d   |   bgcolor bucket TF4 = 240 s   |   %d rows, 05-18..06-14' % (mode, len(labels)),
    ])

    nlab, nbg = _Score(None).emit_overlay(labels, streams, out, 'dominoes filter (REWALK %d)' % mode,
                                          notes=notes)
    print('')
    print('%s  ->  %d labels, %d painted TF4 bars' % (out, nlab, nbg))
    print('  rows            %d   LONG %d / SHORT %d' % (len(labels), nl, len(labels) - nl))
    print('  dominoes FIRED  %d (%.1f%%)' % (nf, 100.0 * nf / len(labels)))
    print('  blue  buckets   %d' % len(streams[1]['ts']))
    print('  yellow buckets  %d' % len(streams[0]['ts']))
    return labels, streams


if __name__ == '__main__':
    main(sys.argv[1:])
