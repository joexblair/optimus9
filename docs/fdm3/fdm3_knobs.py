"""fdm3's knobs. BANKED MEANS THE DEFAULT MOVES AND AN OFF-RULED RUN REFUSES - Joe's standing rule.

Every value here is HIS, and every NAME here is his too: he wrote `fdm3-sideways-trigger`,
`fdm3-sideways-retest-scan-window` and `fdm3-sideways-retest-diff-pct` into the spec himself.

fdm3 IS A NEW GENERATION, not an addition to fdm2 - Joe 1114 confirmed the prefix. Its knobs live
here and NOT in v4_knobs, so a v4 run cannot be changed by an fdm3 ruling and vice versa. The
env override is W_FDM3_<NAME>.

An off-ruled run raises at import unless W_FDM3_EXPERIMENT=1.
"""
import os
import sys

EXPERIMENT = os.environ.get('W_FDM3_EXPERIMENT', '0') == '1'


def _knob(name, default, cast=float):
    return cast(os.environ.get('W_FDM3_' + name, str(default)))


#   ── fdm3-sideways ─────────────────────────────────────────────────────────────────────────────
#   HIS SPEC LINE: *"(ws{knob:5,`fdm3-sideways-trigger`}}b is not oob OR ws{`fdm3-sideways-trigger`}r
#   is not oob (both on closed-prev))"*. ONE timeframe, not a set - his 1114 clarification. Both
#   lines are read at that timeframe: ws{N}b and ws{N}r, closed-prev at N*60 s.
SIDEWAYS_TRIGGER = _knob('SIDEWAYS_TRIGGER', 5, int)      # his `fdm3-sideways-trigger`

#   HIS SPEC LINE: *"create a +/-12.5 minute window centered on"* each of the two retest bars, and
#   he named it on 1114. MINUTES, each side of the centre, so the span is twice this.
SIDEWAYS_RETEST_SCAN_WINDOW = _knob('SIDEWAYS_RETEST_SCAN_WINDOW', 12.5)   # his `...-scan-window`

#   HIS SPEC LINE: *"IF the abs(pxs diff) between pxs-retest-floater's ohlc "open extremum and
#   pxs-retest-anchor's ohlc "open" extermum is <={knob:0.88,`fdm3-sideways-retest-diff-pct`}%"*.
#   THE BASE IS THE EARLIER OF THE TWO OPENS, settled by his own 1114 measurement: he read 0.78%
#   between the 2026-09-23 04:24 and 04:27 ws1 closes with TradingView's price range tool, and of
#   the three candidate bases only the earlier value and the midpoint round to 0.78%. His tool
#   divides by the first price clicked, so the earlier value is the one that matches both.
SIDEWAYS_RETEST_DIFF_PCT = _knob('SIDEWAYS_RETEST_DIFF_PCT', 0.88)   # his `...-retest-diff-pct`

#   ── the fdm3 fence ───────────────────────────────────────────────────────────────────────────
#   HIS 1115: *"the 20/80 mom fence is now a 23/77 fence. this impacts the AW/TO(exf/inf)
#   timestamps"*, then *"keep it as a fdm3 fence"*. So v4_knobs FDM_FNC_2080 STAYS at 20.0 and
#   every fdm3 read of a towards/away ex-fence state uses this one instead - fdm2 step 1, the
#   reversal population, the handoff walk's candidate test and the re-entry keep 20/80.
#   THE SMALLER END OF THE PAIR, as FDM_FNC_2080 is: 23 -> (23.0, 77.0).
#   MY NAME, derived from his own `fdm-20-80-fnc` - he has not named this one yet.
MOM_FNC = _knob('MOM_FNC', 23.0)                # his `fdm3-23-77-fnc`, pending his own name

#   ── which oracle the scenarios read ──────────────────────────────────────────────────────────
#   HIS 1116, asked which instance is the live read: *"8789"*. 8789 carries his fdm3-fence-reset-TO
#   at 33/67 - the flip at 50, the 50 reset and the void all move to the fence's target-side line,
#   67 on a HIGH target-side and 33 on a LOW one - and has the A buttons locked at ws1-ws6 on.
#   8788 is the committed `o9-fdm3-oracle` unit and has neither.
#
#   WHAT 8789 IS, and he should know it: an UNCOMMITTED copy of fdm3_oracle.py running from another
#   session's scratchpad under /tmp, with no systemd unit. It does not survive a reboot or a /tmp
#   clean, and the file behind it is not the one in git.
#   HIS 1117: *"bank 8790 and make this config the machine"*. 8790 runs THE REPO FILE, so the bank
#   is that page's CONFIG, not its address: a port serving this config passes, any other page fails.
#   8790 is a plain process in this session, not a unit - 8788 runs the same file as the
#   `o9-fdm3-oracle` unit and becomes this config the moment he restarts it.
ORACLE_PORT = _knob('ORACLE_PORT', 8790, int)
FENCE_RESET_TO = _knob('FENCE_RESET_TO', 33.0)   # his `fdm3-fence-reset-TO`, banked on the page
ORACLE_FENCE = _knob('ORACLE_FENCE', 23.0)       # the ex-fence fence, locked on the page since 1115
ORACLE_SHIFT = _knob('ORACLE_SHIFT', 30, int)    # his 1117 pivot offset button, minutes - was 15
MNR_TOPS = tuple(int(x) for x in os.environ.get('W_FDM3_MNR_TOPS', '15,25').split(','))
#   his 1117 two M-no-rev columns: mnr1 ws1..ws25's lower ceiling, mnr2 the higher one
MNR_LO = _knob('MNR_LO', 1, int)                 # his *"we'll settle on ws1 to ws25"*
#   HIS 1118 the Mage's side of 50 on the ws1..ws15 cells: he picked the paint strength by eye off a
#   test that stepped 100% down to 0% in tens - *"the setting at 0726 is perfect"*, and 07:26 fell
#   in the 20% step. The page publishes it in /meta so this value and the page cannot drift apart.
#   THE READ IS EMERGING, his 1118 *"my bad: use emerging"*.
ORACLE_MAGE50_PCT = _knob('ORACLE_MAGE50_PCT', 20, int)
#   HIS 1118: *"lines move all the time and there is no gaurantee that they will be available for the
#   reset. the only workable answer is B"*. B = a ws{TF}x race re-opens when the line crosses back
#   over ANY of its three race lines, not only over the one that won. HIS ws{TF}x ROW ONLY: the
#   ws{TF}e race keeps his 1109 4B until he rules on it, and so does lift-off's e path.
ORACLE_X_REOPEN = os.environ.get('W_FDM3_ORACLE_X_REOPEN', 'any')
ORACLE_E_REOPEN = os.environ.get('W_FDM3_ORACLE_E_REOPEN', 'winner')

#   ── orac-exhaust (HIS 1118 spec) ─────────────────────────────────────────────────────────────
#   HIS 1118, asked which oracle its "2 rows" and "3 rows" count: *"1, 30sec"*. So this mech reads
#   the 30 SECOND page, not the 60 second one every other fdm3 read uses. ORACLE_PORT stays at
#   8790 - his 1117 bank - and orac-exhaust alone reads this one.
ORAC_EXHAUST_PORT = _knob('ORAC_EXHAUST_PORT', 8791, int)
ORAC_EXHAUST_ROW_S = _knob('ORAC_EXHAUST_ROW_S', 30, int)   # seconds per row, asserted against /meta
#   HIS 1118: *"allow 4 rows to build 6x, and make it seven ws1-7 distinct x crosses"*
ORAC_6X_ROWS = _knob('ORAC_6X_ROWS', 4, int)         # was his 2, now his 4
ORAC_6X_HITS = _knob('ORAC_6X_HITS', 7, int)         # his 1118 *"seven ws1-7 distinct x crosses"*
ORAC_ROWS = _knob('ORAC_ROWS', 3, int)               # his *"must qualify within 3 rows"*
ORAC_LOW_HI = _knob('ORAC_LOW_HI', 7, int)           # his *"lowband is ws1-ws7"*
ORAC_HIGH_HI = _knob('ORAC_HIGH_HI', 15, int)        # his *"highband is ws8-ws15"*
ORAC_LOW_AW = _knob('ORAC_LOW_AW', 5, int)           # his *"lowband is printing >=5 AW(any)"*
ORAC_LOW_FLIPS = _knob('ORAC_LOW_FLIPS', 2, int)     # his 1118 *"OR >=2 AW flips"*
#   HIS 1118 LATER: he rewrote states 2 and 3 to find the denominator - the conditional highband
#   and its three conditions are NOT in the spec he is working from now. These four keep his
#   values for when he builds out from the denominator; nothing reads them in the meantime.
ORAC_HIGH_AW = _knob('ORAC_HIGH_AW', 3, int)         # his *">=3 AW(any) are required if"*
ORAC_HIGH_XE = _knob('ORAC_HIGH_XE', 1, int)         # his *"highband must print ... >=1 x/e cross"*
#   HIS 1118 STATE 3, REWRITTEN: *"IF >=6 AWs print in lowband at the 3rd row / -highband has 5
#   minutes (walk forward) grace to produce >=2 AW flips and a maximum of 1 TOexf"*. The two knobs
#   above belong to the state 3 he replaced and nothing reads them now.
#   HIS 1118 CORRECTED MECH: *"IF >=4 AWs print in lowband at the 3rd row"*. His 6 became 4 once he
#   settled the counting - *"AW, TO, x, e prints are all per distinct TF"*. Read on the 3rd row
#   alone, as his spec text says; his 00:08:30 reaches exactly 4 distinct lowband TFs there.
ORAC_LOW_AW_3RD = _knob('ORAC_LOW_AW_3RD', 4, int)     # his *">=4 AWs print in lowband"*
#   HIS 1118, after ws2Mage missed the 15 fence by 1.08 at 09:20 and stranded ws3..ws15 behind it:
#   *"jumps of 2 should be allowed to make it more sane"*. The oob climb steps over one missing
#   timeframe; a gap of two or more stops it.
ORAC_OOB_JUMP = _knob('ORAC_OOB_JUMP', 2, int)         # timeframes the climb may step at once
#   HIS 1118: *"I need 0606 to be low pivot ... 1205 is another low pivot"*. ws2Mage, the line the
#   pseudo trades pivot on, holds outside the 15 fence through both windows - its lowest readings
#   are 19.22 at 06:02:00 and 16.82 at 12:02:05 - so it has no oob run to leave and no cross at
#   either, at any hold length. ws1Mage crosses LOW at 06:03:10 and 12:02:10, 2m50s before each of
#   his times. SCORING ONLY: the pseudo trades stay on ws2Mage, untouched.
#   HIS 1118 LEG MODE: *"I thought sweep-pivots went from 'last cross to ib' to opposing side
#   'last-cross to ib'"*, then *"don't rebuild it - create a mode for this new mech so that the
#   existing pivots remain untouched in any now or future fdm3-oracle updates"*. The banked leg
#   rule is unchanged; v4_sweep_pivots.legs takes mode='last_cross' for this one.
ORAC_LEG_MODE = os.environ.get('W_FDM3_ORAC_LEG_MODE', 'last_cross')
#   BACK TO ws2Mage. ws1Mage was only ever chosen because ws2Mage had no cross at his 06:06 and
#   12:05 under the BANKED leg rule. Under his own rule ws2Mage reads both as LOW legs, so the
#   reason for ws1Mage is gone and the scoring line is the one the pseudo trades already pivot on.
ORAC_MAEMFE_LINE = os.environ.get('W_FDM3_ORAC_MAEMFE_LINE', 'ws2Mage')
#   HIS 1118: *"I take your recommendation"* - rank by MFE over abs(MAE), not by MAE alone, so a
#   row with a tiny MAE AND a tiny MFE does not score as a winner. Ranked inside each side.
ORAC_RANK_BY = os.environ.get('W_FDM3_ORAC_RANK_BY', 'mfe_over_mae')
ORAC_GRACE_MIN = _knob('ORAC_GRACE_MIN', 5.0)          # his *"5 minutes (walk forward) grace"*
ORAC_HIGH_FLIPS = _knob('ORAC_HIGH_FLIPS', 2, int)     # his *">=2 AW flips"* in highband
ORAC_HIGH_TOEXF_MAX = _knob('ORAC_HIGH_TOEXF_MAX', 1, int)   # his *"a maximum of 1 TOexf"*
ORAC_TOEXF_GATE = _knob('ORAC_TOEXF_GATE', 1, int)   # his condition1 *"TO(exf): {>1}"* - strictly above
ORAC_MAGE_OOB = _knob('ORAC_MAGE_OOB', 3, int)       # his condition2 *"more than 3 Mages"* - strictly above
ORAC_MAGE_HI = _knob('ORAC_MAGE_HI', 15, int)        # his 1118 *"contains the in-use TFs to ws1-ws15"*

#   ── the oracle A state, fdm3-wide ────────────────────────────────────────────────────────────
#   HIS 1116: *"the A ws1-ws6 button is enabled now - I've found it to be better than having it
#   disabled. bank this as the live machine"*, and earlier the same day *"the oracles 'A ws1-ws6
#   button': this sits outside of the scenarion building. that button is underlying an
#   infrastructure decision"*. So it is NOT a per-scenario knob: it is the state EVERY fdm3 read of
#   the oracle's rows is taken at, and it lives here once.
#
#   A ON means every r line in that band takes its lift-off reads - natural and e-cross - off the
#   window extreme on every bar of the span, which moves that line's AW and the scenario-2 test of
#   the lines above it. It cannot move an x or an e cross: fdm3_oracle.build() makes those bits
#   outside its state loop, from the lift-off race alone.
#   MY NAMES, derived from his own button labels - he has not named these two.
A_WS1_WS6 = _knob('A_WS1_WS6', 1, int)
A_WS7_WS15 = _knob('A_WS7_WS15', 0, int)

#   ── fdm3-ltf-xcross ──────────────────────────────────────────────────────────────────────────
#   HIS SPEC LINE: *">={knob:6,`fdm3-ltf-xcross-hits`} TFs are populated with an x-cross, inside of
#   {knob:2,`fdm3-ltf-xcross-rows`} rows, within the ws1-ws{knob:8,`fdm3-ltf-xcross-maxTF`} fields"*.
#   AN X-CROSS ALONE - he wrote "e-cross or x-cross" in his other two scenarios and "an x-cross" here.
LTF_XCROSS_HITS = _knob('LTF_XCROSS_HITS', 6, int)
LTF_XCROSS_ROWS = _knob('LTF_XCROSS_ROWS', 2, int)
LTF_XCROSS_MAXTF = _knob('LTF_XCROSS_MAXTF', 8, int)

#   HIS SPEC LINE: *"AND the fdm3-ltf-xcross-rows are contained within {knob:3,
#   `fdm3-ltf-xcross-nof15-rows`} consecutive rows printing 13of15"*. Read COLLECTIVELY over those
#   rows, settled by his own five examples: not one of 09-24 2230, 2248, 2259 or 09-25 0118, 0315
#   has all three rows carrying 13 on its own.
LTF_XCROSS_NOF15_ROWS = _knob('LTF_XCROSS_NOF15_ROWS', 3, int)

#   HIS SPEC LINE: *">={knob:4, `fdm3-min-aw-prints`} fields prints `AW(*)` in ws1-ws15 AND
#   >={knob:2,`fdm3-min_aw_flips`} new AW's have printed inside of ws1-ws15"*.
#   HIS 1115 RULING ON THE FIRST: *"4 distinct TFs reading AW(*) anywhere in the 3 rows"* - so the
#   AW(*) gate counts TIMEFRAMES, while the new-AW gate counts PRINTS.
MIN_AW_PRINTS = _knob('MIN_AW_PRINTS', 4, int)
MIN_AW_FLIPS = _knob('MIN_AW_FLIPS', 2, int)

#   ── fdm3-ltf-5aw-6x ──────────────────────────────────────────────────────────────────────────
#   HIS 1115: this scenario reads the LTF-xcross knobs - *"the knob reprints are not duplications -
#   this mech uses the same values"* - EXCEPT the x-cross hit window. He wrote 1 against
#   fdm3-ltf-xcross-rows, which is banked at 2, then ruled: *"I need to replace fdm3-ltf-xcross-rows
#   in the mech. use this new knob: fdm3-ltf-5aw-6x-xcross-rows, value=1"*.
LTF_5AW_6X_XCROSS_ROWS = _knob('LTF_5AW_6X_XCROSS_ROWS', 1, int)

#   HIS SPEC LINE: *">={knob:10, `fdm3-ltf-5aw-6x-min-aw-prints`} fields prints `AW(*)` in ws1-ws15
#   AND >={knob:5,`fdm3-ltf-5aw-6x-min-aw-flips`} new AW's have printed inside of ws1-ws15"*.
#   THE AW(*) READING IS SETTLED: he banked the 09-20..09-23 run that counts DISTINCT TIMEFRAMES -
#   *"bank docs/fdm3/out/ltf_5aw_6x_0920_0923_A_ws1_ws6.txt as a confirmed aw-exhaust scenario"* -
#   so distinct timeframes is the reading, and the cell count is not an option any more.
LTF_5AW_6X_MIN_AW_PRINTS = _knob('LTF_5AW_6X_MIN_AW_PRINTS', 10, int)
LTF_5AW_6X_MIN_AW_FLIPS = _knob('LTF_5AW_6X_MIN_AW_FLIPS', 5, int)



#   ── fdm3-4-ltf-aws ───────────────────────────────────────────────────────────────────────────
#   HIS SPEC LINE: *">=4 AW flips on the same row, on TFs that are between ws1 and
#   {knob:6,'fdm3-4-ltf-aws-maxTF'} AND are contained within no more than {knob:4,'4-ltf-aws-rows'}
#   consecutive rows"*. HIS 1114: both names carry the fdm3- prefix.
AWS4_MAXTF = _knob('AWS4_MAXTF', 6, int)
AWS4_ROWS = _knob('AWS4_ROWS', 4, int)

RULED = {
    'MOM_FNC': (23.0, 'his 1115 fence, kept inside fdm3 - v4_knobs FDM_FNC_2080 stays 20.0'),
    'LTF_XCROSS_HITS': (6, 'his `fdm3-ltf-xcross-hits` - TFs carrying an X-CROSS, not an e-cross'),
    'LTF_XCROSS_ROWS': (2, 'his `fdm3-ltf-xcross-rows` - the window those hits sit in'),
    'LTF_XCROSS_MAXTF': (8, 'his `fdm3-ltf-xcross-maxTF` - the hits count on ws1..ws8'),
    'LTF_XCROSS_NOF15_ROWS': (3, 'his `fdm3-ltf-xcross-nof15-rows` - the outer window, and the '
                                 '13of15 inside it is read collectively'),
    'MIN_AW_PRINTS': (4, 'his `fdm3-min-aw-prints` - DISTINCT TFs reading AW(*), his 1115 ruling'),
    'MIN_AW_FLIPS': (2, 'his `fdm3-min-aw-flips` - new AW PRINTS, the TO -> AW flip'),
    'LTF_5AW_6X_XCROSS_ROWS': (1, 'his `fdm3-ltf-5aw-6x-xcross-rows` - this scenario\'s own x-cross '
                                  'hit window, replacing fdm3-ltf-xcross-rows in it'),
    'LTF_5AW_6X_MIN_AW_PRINTS': (10, 'his `fdm3-ltf-5aw-6x-min-aw-prints` - DISTINCT timeframes '
                                     'reading AW(*), settled by his 1116 bank'),
    'ORACLE_PORT': (8790, 'where the banked config is served, his 1117 *"bank 8790"*. A locator, '
                          'not the bank: the CONFIG below is what a run asserts'),
    'FENCE_RESET_TO': (33.0, 'his `fdm3-fence-reset-TO`, the fence the flip, the 50 reset and the '
                             'void read - asserted against the page on every run'),
    'ORACLE_FENCE': (23.0, 'the ex-fence fence, locked on the page at his 1115 word'),
    'ORACLE_SHIFT': (30, 'his 1117 pivot offset button, minutes - *"instead of +15, make it +30"*'),
    'MNR_TOPS': ((15, 25), 'his 1117 two M-no-rev ceilings, mnr1 then mnr2'),
    'MNR_LO': (1, 'the M-no-rev floor, his *"we\'ll settle on ws1 to ws25"*'),
    'ORACLE_X_REOPEN': ('any', 'his 1118 B - the ws{TF}x race re-opens on crossing back over ANY '
                               'of its three race lines: *"the only workable answer is B"*'),
    'ORACLE_E_REOPEN': ('winner', 'his 1109 4B, unchanged - the ws{TF}e race re-opens only on '
                                  'crossing back over the line that won. Not yet re-ruled'),
    'ORACLE_MAGE50_PCT': (20, 'the Mage-side-of-50 paint strength on the oracle\'s ws1..ws15 '
                              'cells, per cent - his 1118 *"the setting at 0726 is perfect"*'),
    'ORAC_EXHAUST_PORT': (8791, 'orac-exhaust reads the 30 second oracle - his 1118 *"1, 30sec"*'),
    'ORAC_EXHAUST_ROW_S': (30, 'seconds per row on the page orac-exhaust reads, his 1118 *"30sec"*'),
    'ORAC_6X_ROWS': (4, 'his 1118 *"allow 4 rows to build 6x"* - was the 2 of *"six '
                        'x-crosses printing in 2 rows in lowband"*'),
    'ORAC_6X_HITS': (7, 'his 1118 *"make it seven ws1-7 distinct x crosses"* - was six'),
    'ORAC_ROWS': (3, 'his *"the next 2 must qualify within 3 rows, and those 3 rows encompass 6x"*'),
    'ORAC_LOW_HI': (7, 'his *"lowband is ws1-ws7"*'),
    'ORAC_HIGH_HI': (15, 'his *"highband is ws8-ws15"*'),
    'ORAC_LOW_AW': (5, 'his state 2: *"lowband is printing >=5 AW(any)"*'),
    'ORAC_LOW_FLIPS': (2, 'his 1118 state 2, the other side of the OR: *"(>=5 AW(any) OR '
                          '>=2 AW flips)"*. An AW flip is the TO -> AW flip, his *"new AW"*'),
    'ORAC_HIGH_AW': (3, 'his state 3: *">=3 AW(any) are required if any of these conditions qualify"*'),
    'ORAC_LEG_MODE': ('last_cross', 'his 1118 leg rule as a MODE on v4_sweep_pivots.legs - last '
                                    'cross to ib, to the opposing side\'s last cross to ib. The '
                                    'banked rule is untouched'),
    'ORAC_MAEMFE_LINE': ('ws2Mage', 'the line whose sweep-pivot legs score MAE/MFE. Under his '
                                    '1118 leg mode it reads his 06:06 and 12:05 as LOW legs, and '
                                    'it is the line the pseudo trades already pivot on'),
    'ORAC_RANK_BY': ('mfe_over_mae', 'his 1118 *"I take your recommendation"* - rank on MFE '
                                     'over abs(MAE), per side, not on MAE alone'),
    'ORAC_OOB_JUMP': (2, 'his 1118 *"jumps of 2 should be allowed to make it more sane"* - the '
                         'max-oob climb steps over one missing timeframe, not two'),
    'ORAC_LOW_AW_3RD': (4, 'his 1118 state 3 gate: *">=4 AWs print in lowband at the 3rd row"*, '
                           'distinct TFs, read on the 3rd row alone'),
    'ORAC_GRACE_MIN': (5.0, 'his 1118 *"highband has 5 minutes (walk forward) grace"*, minutes'),
    'ORAC_HIGH_FLIPS': (2, 'his 1118 *">=2 AW flips"* in highband inside the grace'),
    'ORAC_HIGH_TOEXF_MAX': (1, 'his 1118 *"a maximum of 1 TOexf"* in highband'),
    'ORAC_HIGH_XE': (1, 'his state 3 fall-through: *"highband must print 0 TOexf and >=1 x/e cross"*'),
    'ORAC_TOEXF_GATE': (1, 'his condition1 `toexf-gate`: the two sum columns\' TO(exf) counts added '
                           'together, STRICTLY ABOVE this - *"TO(exf): {>1}"*, his 1118 *"the sum of '
                           'the 2 columns"*'),
    'ORAC_MAGE_OOB': (3, 'his condition2: *"more than 3 Mages have been oob during the trade"*, so '
                         'strictly above 3 distinct timeframes'),
    'ORAC_MAGE_HI': (15, 'his 1118 *"this new spec intentionaly contains the in-use TFs to '
                         'ws1-ws15"*, so condition2 counts ws1..ws15 Mages'),
    'A_WS1_WS6': (1, 'the oracle A ws1-ws6 button - ON, his 1116 *"bank this as the live machine"*. '
                     'fdm3-wide: infrastructure, not a scenario gate'),
    'A_WS7_WS15': (0, 'the oracle A ws7-ws15 button - OFF. He banked the first one only'),
    'LTF_5AW_6X_MIN_AW_FLIPS': (5, 'his `fdm3-ltf-5aw-6x-min-aw-flips` - new AW PRINTS'),
    'AWS4_MAXTF': (6, 'his `fdm3-4-ltf-aws-maxTF` - the AW flips count on ws1..ws6'),
    'AWS4_ROWS': (4, 'his `fdm3-4-ltf-aws-rows` - the window both 4-ltf-aws gates sit inside'),
    'SIDEWAYS_TRIGGER': (5, 'his `fdm3-sideways-trigger` - the ONE timeframe whose b and r lines '
                            'the sideways trigger reads, closed-prev'),
    'SIDEWAYS_RETEST_SCAN_WINDOW': (12.5, 'his `fdm3-sideways-retest-scan-window` - minutes each '
                                          'side of the centre, so a 25 minute span'),
    'SIDEWAYS_RETEST_DIFF_PCT': (0.88, 'his `fdm3-sideways-retest-diff-pct` - the open-extremum '
                                       'gap ceiling, as a percent of the EARLIER open'),
}


def live():
    """-> [(name, value)], every knob this module reads. A report prints these beside its rows."""
    return [(k, globals()[k]) for k in sorted(RULED)]


def check(out=None):
    """THE RULED CHECK. Refuses an off-ruled run unless W_FDM3_EXPERIMENT=1. Called at import."""
    out = out or sys.stderr
    off = [(k, globals()[k], v, why) for k, (v, why) in RULED.items() if globals()[k] != v]
    if not off:
        return True
    msg = '; '.join('%s is %r, ruled %r (%s)' % (k, got, want, why) for k, got, want, why in off)
    if not EXPERIMENT:
        raise RuntimeError('OFF-RULED fdm3 run refused. ' + msg
                           + '. Set W_FDM3_EXPERIMENT=1 to run it as an experiment.')
    out.write('# W_FDM3_EXPERIMENT=1 - THIS IS NOT THE MACHINE. %d knob(s) off the bank: %s\n'
              % (len(off), msg))
    return False


RULED_OK = check()
