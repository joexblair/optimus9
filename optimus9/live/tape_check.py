"""tape_check — the tape o9-live read, held against an INDEPENDENT price, bar by bar. Reads only.

Joe 1002: *"bake all of your ideas and get them collecting inputs"* - item #2 of the outage list. The
recon recomputes the backtest from the SAME tape o9-live read (`kline_collection`), so a tape that
stays wrong - the 1002 05:08:35-05:25:35 frozen span - gives the same answer on both sides and the
recon cannot see it. Recon run 15 covered those bars and showed 0 mismatches.

THE INDEPENDENT PRICE is `kline_audit` (kline_auditor.service): a REST sample of Bybit every second,
rolled into one row per 5 s bar, with the auditor's own verdict on the collector's bar. What counts as
a bad bar is the AUDITOR's definition, not this module's:

    5 s verdict 'frozen'    the collector's close was static for 6 bars while the REST price moved
                            more than 3 ticks (`kline_auditor.py:84-94`, `_FREEZE_BARS`, `_FREEZE_TICKS`)
    5 s verdict 'missing'   the collector wrote no bar
    a bar with no audit row the auditor itself was down - reported, never assumed good

ONE JOB: `check()` returns every bar in [start, end] the auditor did not call 'live', grouped into
spans of consecutive bars, each with the dump lines whose bar falls inside it. Tick gaps between the
tape close and the REST close are carried on every flagged bar.
"""
TICK = 1e-5                         # FARTCOINUSDT price step, as kline_auditor's tick variance uses
BAR_MS = 5000


def check(db, tp_pk, start_ms, end_ms, dump=()):
    """-> dict(bars, audited, audit_last, flagged=[bar rows], spans=[span dicts]).

    Bars newer than the auditor's newest 5 s row are not checked yet - the auditor writes a bar after
    it closes - so `end_ms` is cut to that row. A later run checks them.
    """
    m = db.execute("SELECT MAX(ka_timestamp) m FROM kline_audit WHERE ka_tp_pk=%s AND ka_tier='5s'",
                   (tp_pk,), fetch=True)[0]['m']
    end_ms = min(int(end_ms), int(m)) if m is not None else int(start_ms) - 1
    kc = db.execute('SELECT kc_timestamp t, kc_close c, kc_volume v FROM kline_collection WHERE kc_tp_pk=%s '
                    'AND kc_timestamp BETWEEN %s AND %s', (tp_pk, start_ms, end_ms), fetch=True)
    ka = db.execute("SELECT ka_timestamp t, ka_verdict v, ka_audit_close a FROM kline_audit WHERE ka_tp_pk=%s "
                    "AND ka_tier='5s' AND ka_timestamp BETWEEN %s AND %s", (tp_pk, start_ms, end_ms), fetch=True)
    tape = {int(r['t']): (float(r['c']), float(r['v'])) for r in kc}
    aud = {int(r['t']): (r['v'], None if r['a'] is None else float(r['a'])) for r in ka}
    flagged = []
    for t in sorted(tape):
        v, a = aud.get(t, ('no audit row', None))
        if v == 'live':
            continue
        c, vol = tape[t]
        flagged.append(dict(bar_ms=t, verdict=v, tape_close=c, tape_vol=vol, rest_close=a,
                            ticks=None if a is None else int(round((c - a) / TICK))))
    for t in sorted(set(aud) - set(tape)):
        flagged.append(dict(bar_ms=t, verdict='no tape bar (%s)' % aud[t][0], tape_close=None, tape_vol=None,
                            rest_close=aud[t][1], ticks=None))
    flagged.sort(key=lambda r: r['bar_ms'])
    spans = []
    for r in flagged:
        if spans and r['bar_ms'] - spans[-1]['last'] <= BAR_MS:
            s = spans[-1]
            s['last'] = r['bar_ms']; s['bars'] += 1
            s['verdicts'][r['verdict']] = s['verdicts'].get(r['verdict'], 0) + 1
            if r['ticks'] is not None:
                s['max_ticks'] = max(s['max_ticks'] or 0, abs(r['ticks']))
        else:
            spans.append(dict(first=r['bar_ms'], last=r['bar_ms'], bars=1, verdicts={r['verdict']: 1},
                              max_ticks=None if r['ticks'] is None else abs(r['ticks'])))
    for s in spans:
        s['dump'] = [d for d in dump if s['first'] <= int(d['bar_ms']) <= s['last']]
    return dict(bars=len(tape), audited=len(set(tape) & set(aud)), audit_last=end_ms, flagged=flagged,
                spans=spans)
