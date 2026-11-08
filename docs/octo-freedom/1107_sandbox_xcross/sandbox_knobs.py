"""`fdm2-xcv`'s knobs, BANKED. Joe 1108: *"bank, update specs and make knobs durable"*, and
*"take ownership of the files. bank them as the fdm2-xcv mech"*.

BANKED MEANS THE DEFAULT MOVES AND AN OFF-RULED RUN REFUSES. Joe's standing rule, in v4_knobs' own form.
Every value below is one he set in the 1107 sandbox work; a run with any of them overridden refuses
unless it declares itself an experiment with W_SBX_EXPERIMENT=1, and check() returns every knob so the
caller prints them first.

THE LABELS ARE MINE, the values are his. Env overrides are W_SBX_<NAME>.

NOT RE-DECLARED HERE, each banked in its one home:
    - the cadence, the ex-20/80 fence, the race's wob and the director range are v4_fdm2's, in v4_knobs.
      The report prints v4's knob hash and its off-the-bank list beside these knobs.
    - the walk back to look forward (MC_GAP) is the Jig's.
    - the RSI divergence's knobs (RSIDIV_*) are the Jig's, beside its producer.
"""
import os

EXPERIMENT = os.environ.get('W_SBX_EXPERIMENT', '0') == '1'


def _knob(name, default, cast=float):
    return cast(os.environ.get('W_SBX_' + name, str(default)))


# ── the report. HIS 1107: *"report the ws30r to ws10r emerging values in a 22 column table"* ─────────
REPORT_TF_HI = _knob('REPORT_TF_HI', 30, int)       # the report's first r column, ws30r
REPORT_TF_LO = _knob('REPORT_TF_LO', 10, int)       # the report's last r column, ws10r
#   THE SECOND r BLOCK, HIS 1107: *"drop the r2 rows, and replace them with r rows that were calculated on
#   ws5x"* - the same race and walk back on ws5x, whatever TF the cadence selected. BANKED 1108: *"bank the latest
#   version, the one that has ws5x as a static line for each table"*
WS5X_TF = _knob('WS5X_TF', 5, int)    # HIS 1108: the ONE x line - his `ws{knob:5}x`
#   HIS 1108, withdrawing his own earlier words: *"this is on me - the top rows (the dynamic xcross
#   and the ws4 xcross) were' just for my ref. ws5x is the one all of my timestamps were based
#   on"*. So the report carries ONE x line and `WS5X_TF` is the knob his spec writes as
#   `ws{knob:5}x`. My XCV_TFS '4,5' knob, added hours earlier for the two-line ruling he has now
#   withdrawn, is REMOVED - two knobs holding one x line is a drift trap.

# ── ws{TF}r2, HIS 1107: *"create a new `ws{TF}r2` stochrsi line: klen:6, rsilen:6, stochrange:10, src close"*
#   built in memory by sandbox_xcross.r2_lines(); not read by the report since he dropped its rows
R2_KLEN = _knob('R2_KLEN', 6, int)
R2_RSI = _knob('R2_RSI', 6, int)
R2_STC = _knob('R2_STC', 10, int)
R2_SRC = _knob('R2_SRC', 'close', str)

# ── ws{TF}e, HIS 1107: *"a BB%B line with len 4 and multi 0.5, src: close"*, *"going forward I'll refer to
#   this line as ws{TF}e"*. Built in memory by sandbox_xcross.e_line(tf); no report reads it
E_LEN = _knob('E_LEN', 4, int)
E_MULT = _knob('E_MULT', 0.5)
E_SRC = _knob('E_SRC', 'close', str)

# ── the fake cadence, HIS 1107 EXPERIMENTAL: *"fake a cadence event whenever ws1b crosses to ib, while
#   ws1Mage was oob during ws1b's oob excursion, from 1745 to 1920. these will all be high side events"*.
#   The side is not a knob: he ruled every one HIGH, and the code reads the high oob only
FAKE_DAY = _knob('FAKE_DAY', '2026-08-25', str)
FAKE_FROM = _knob('FAKE_FROM', '17:45:00', str)
FAKE_TO = _knob('FAKE_TO', '19:20:00', str)

#   THE RULED REGISTRY: knob -> (ruled value, units, his words). check() compares the live value to it.
RULED = {
    'REPORT_TF_HI': (30, 'TF', '"report the ws30r to ws10r emerging values in a 22 column table"'),
    'REPORT_TF_LO': (10, 'TF', '"report the ws30r to ws10r emerging values in a 22 column table"'),
    'WS5X_TF': (5, 'TF', '"replace them with r rows that were calculated on ws5x", then 1108 "bank the latest '
                         'version, the one that has ws5x as a static line for each table"'),
    'R2_KLEN': (6, 'bars', '"klen:6"'),
    'R2_RSI': (6, 'bars', '"rsilen:6"'),
    'R2_STC': (10, 'bars', '"stochrange:10"'),
    'R2_SRC': ('close', 'source', '"src close"'),
    'E_LEN': (4, 'bars', '"a BB%B line with len 4"'),
    'E_MULT': (0.5, 'std devs', '"multi 0.5"'),
    'E_SRC': ('close', 'source', '"src: close"'),
    'FAKE_DAY': ('2026-08-25', 'day', 'MINE - his window named no day; every 1107 sandbox read was on 2026-08-25'),
    'FAKE_FROM': ('17:45:00', 'UTC time', '"from 1745 to 1920"'),
    'FAKE_TO': ('19:20:00', 'UTC time', '"from 1745 to 1920"'),
}


def live():
    """-> {knob: live value}, every knob in RULED."""
    g = globals()
    return {k: g[k] for k in RULED}


def check():
    """THE RULED CHECK. Refuses an off-ruled run unless W_SBX_EXPERIMENT=1. -> [(knob, live, ruled, ok)]."""
    lv = live()
    rows = [(k, lv[k], RULED[k][0], str(lv[k]) == str(RULED[k][0])) for k in RULED]
    off = [r for r in rows if not r[3]]
    if off and not EXPERIMENT:
        raise SystemExit('REFUSED - sandbox knobs off the bank: %s. Set W_SBX_EXPERIMENT=1 to run them.'
                         % ', '.join('%s=%s (ruled %s)' % r[:3] for r in off))
    assert REPORT_TF_HI >= REPORT_TF_LO, 'the report columns run from REPORT_TF_HI down to REPORT_TF_LO'
    return rows


def table():
    """The knob table, markdown. -> [str]."""
    out = ['| the knob | value | units | ruled | Joe\'s words |', '|---|---|---|---|---|']
    for k, lv, ruled, ok in check():
        out.append('| `%s` | %s | %s | %s | %s |' % (k, lv, RULED[k][1], 'YES' if ok else 'OFF THE BANK',
                                                    RULED[k][2].replace('|', '\\|')))
    return out


if __name__ == '__main__':
    print('\n'.join(table()))
