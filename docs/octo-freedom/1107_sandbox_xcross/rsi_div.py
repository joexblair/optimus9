"""`bullish-rsi` / `bearish-rsi` over one day, on ws1r's and gcws30r's RSI. Joe 1107. -> a text file.

THE READER IS jig.rsi_divergence - this file only builds its inputs and prints its events.

    the bars     each line's OWN completed bars: 60 s for ws1r, 30 s for gcws30r. A bar's close is the
                 5 s close on its last 5 s bar; it PRINTS on the next 5 s bar, which is where
                 closed-prev shows it, so every event is stamped on that print bar
    the RSI      IndicatorComputer._rsi - the builder's own - at each line's RSI length, over the whole
                 tape so it carries the same warm-up the stored lines do
    the gate     JIG.RSIDIV_GATE, BANKED ws2b, closed-prev at its own 120 s, read on the print bar. The
                 gcws30b experiment reads v4_live_lines._g30b, that line's one routed home
    THE CONTROL  stoch(stc) of that RSI, then its k_len average, must reproduce the stored r line on
                 the print bars - if it does not, the RSI handed to the reader is not the r line's RSI

Usage:  python3 rsi_div.py 2026-08-25
"""
import io
import os
import sys

os.environ.setdefault('LG_TAPE_END', '2026-10-05')
V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, V4)
os.chdir(V4)
import numpy as np
import pandas as pd

_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import ln
    import v4_closed_prev as CP
    import v4_live_lines as LL
    from optimus9.analysis import jig as JIG
    from optimus9.compute.indicator_computer import IndicatorComputer as IC
    from optimus9.compute.line_config import LineStore, from_tuple
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.config import get_db_config
    from optimus9.orchestration.rpl_cache import _tape_key, TAPE_DIR
    from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
finally:
    sys.stderr = _e

OUT = os.path.dirname(os.path.abspath(__file__))
LINES = JIG.RSIDIV_LINES                          # HIS 1107: "ws1r and gcws30r", banked in the jig
#   THE GATE LINE IS THE JIG'S, BANKED ws2b - JIG.RSIDIV_GATE is its one home, so this driver cannot drift
#   from the producer's ruled set. gcws30b stays runnable as an experiment and writes its own files.
GATE = JIG.RSIDIV_GATE
GATE_TF = JIG.RSIDIV_GATE_TF


def gate_line(name):
    """The gate line on the 5 s grid, closed-prev at its own timeframe. gcws30b keeps its one routed home."""
    if name == 'gcws30b':
        return np.asarray(LL._g30b(), float)
    return np.asarray(CP.series(np.asarray(ln.line(name), float), GATE_TF[name]), float)


def table(rows):
    w = [max(len(str(r[i])) for r in rows) for i in range(len(rows[0]))]
    fmt = lambda r: '| ' + ' | '.join(str(c).ljust(w[i]) for i, c in enumerate(r)) + ' |'
    return [fmt(rows[0]), '|' + '|'.join('-' * (x + 2) for x in w) + '|'] + [fmt(r) for r in rows[1:]]


def line_spec(name):
    db = DatabaseManager(**get_db_config()); db.connect()
    try:
        tf, cfg = LineStore(db).resolve(name)
    finally:
        db.disconnect()
    return int(tf), from_tuple(cfg)


def stored(name, tf):
    """The stored r line on the 5 s grid, closed-prev at its own timeframe."""
    em = np.asarray(ln.line(name), float) if name.startswith('ws') else np.asarray(LL.sub_line(name), float)
    return np.asarray(CP.series(em, tf), float)


def main(day):
    for k_, live, ruled, ok in JIG.rsidiv_check():                 # printed FIRST, refuses off-ruled
        print('%-16s live %-6s ruled %-6s %s' % (k_, live, ruled, 'ok' if ok else 'OFF THE BANK'))
    z = np.load(os.path.join(TAPE_DIR, _tape_key(ln.EM, HOURS, WARMUP,
                                                 {'src': ln._sy['s'], 'len': ln._sy['l']}) + '.npz'))
    close5 = z['__close__'][:ln.N].astype(float)
    ts = np.asarray(ln.ts, np.int64)
    assert (np.diff(ts) == 5000).all(), 'the 5 s grid has a gap - the bar closes below would misalign'
    gate5 = gate_line(GATE)
    A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
    events, ctl, spec = [], [], {}
    for name in LINES:
        tf, cfg = line_spec(name)                                    # the line's own timeframe, from its DB row
        want = int(name[4:-1]) if name.startswith('gcws') else int(name[2:-1]) * 60    # gcws30r 30 s, ws1r 60 s
        assert tf == want, '%s resolves to %d s, not %d s' % (name, tf, want)
        spec[name] = (tf, cfg)
        last = np.flatnonzero(((ts + 5000) % (tf * 1000)) == 0)     # each bar's last 5 s bar
        last = last[last + 1 < ln.N]
        prt = last + 1                                               # where closed-prev prints it
        c = close5[last]
        rsi = IC._rsi(c, int(cfg.rsi))
        k = pd.Series(IC._stoch(rsi, int(cfg.stc))).rolling(int(cfg.k_len)).mean().to_numpy()
        ref = stored(name, tf)[prt]
        day_bars = (prt >= A) & (prt <= B)
        d = np.abs(k[day_bars] - ref[day_bars])
        ctl.append((name, int(day_bars.sum()), float(np.nanmax(d)), int(np.isnan(k[day_bars]).sum())))
        #   on=True: RSIDIV_ON is BANKED OFF, so the read claims nothing by default. This report switches it on
        #   for its own run - the option he chose - and the legend says so.
        for ev in JIG.rsi_divergence(c, rsi, gate5[prt], (K.OOB_LO, K.OOB_HI), on=True):
            if A <= prt[ev['i']] <= B:
                ev.update(line=name, tf=tf, prt=int(prt[ev['i']]),
                          bar_i=int(last[ev['i']] - (tf // 5 - 1)), bar_j=int(last[ev['j']] - (tf // 5 - 1)))
                events.append(ev)
    events.sort(key=lambda e: (e['prt'], e['line']))
    leg = [('the read', 'value'),
           ('the day', day),
           ('the tape', '%d bars, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1))),
           ('the reader', 'jig.rsi_divergence, labels bullish-rsi (low side) / bearish-rsi (high side)'),
           ('RSIDIV_ON', 'banked %d (off) - this report switches the read on for its own run' % JIG.RSIDIV_ON)]
    for name, (tf, cfg) in spec.items():
        leg.append(('the %s RSI' % name, 'RSI(%d) of %d s closes - the RSI under %s (%d|%d|%d|%s)'
                    % (cfg.rsi, tf, name, cfg.k_len, cfg.rsi, cfg.stc, cfg.src)))
    for name, n, dmax, nn in ctl:
        leg.append(('CONTROL: %s rebuilt from that RSI' % name,
                    'max |rebuilt - stored| %.6f over %d bars of the day, %d NaN' % (dmax, n, nn)))
    leg += [('the gate', '%s same-side oob at the anchor only (his ruling), oob %g/%g, closed-prev at %d s%s'
             % (GATE, K.OOB_LO, K.OOB_HI, GATE_TF[GATE],
                ', routed read %s' % K.LIN2_CP_GCWS30B if GATE == 'gcws30b' else '')),
            ('the earlier point', 'the most recent low (high): strictly higher (lower) close on both sides'),
            ('fires', 'bullish-rsi: anchor close below that low AND its RSI above the low\'s RSI. '
             'bearish-rsi: the mirror'),
            ('event bar', 'the first anchor bar per earlier point; stamped on the print bar'),
            ('RSI level gate', 'RSIDIV_LVL_GATE %d (%s), RSIDIV_LVL %g -> %g/%g. MY knob names, my default 0'
             % (JIG.RSIDIV_LVL_GATE, 'off - %s oob only' % GATE if not JIG.RSIDIV_LVL_GATE else 'on',
                JIG.RSIDIV_LVL, JIG.RSIDIV_LVL, 100 - JIG.RSIDIV_LVL)),
            ('price', 'the raw close (his 0711 finding: a smoothed price slope ruins the read)')]
    rows = [('printed at', 'label', 'line', 'anchor bar', 'earlier point bar',
             'close earlier -> anchor', 'RSI earlier -> anchor', '%s at the print' % GATE)]
    for e in events:
        rows.append((ln.U(e['prt']), e['label'], e['line'], ln.U(e['bar_i']), ln.U(e['bar_j']),
                     '%.6f -> %.6f' % (e['close_j'], e['close_i']), '%.2f -> %.2f' % (e['rsi_j'], e['rsi_i']),
                     '%.2f' % e['gate_i']))
    out = ['# bullish-rsi / bearish-rsi, %s, gate %s' % (day, GATE), ''] + table(leg) + ['', '%d events' % len(events), ''] + table(rows)
    p = os.path.join(OUT, 'rsi_div_%s.txt' % day if GATE == 'gcws30b' else 'rsi_div_%s_%s.txt' % (day, GATE))
    with open(p, 'w') as fh:
        fh.write('\n'.join(out) + '\n')
    print(p, len(events), 'events')
    for c_ in ctl:
        print('control', c_)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '2026-08-25')
