"""trade_walk — Joe 0929's trade rules, as a walk over already-decided events.

ONE JOB: given the bars that may open a trade and the dr stretches, say where every trade opens and
closes. It computes no gate, reads no line, touches no DB and prints nothing. The gate is
`rule1_gate.gate`, the dr is `dr_latch`, the signals are `wsf_leash.wsl_sig_utc`.

JOE'S RULES, VERBATIM 0929:
  "every ungated sig_utc timestamps create a trade reversal - ie it closes the existing trade and
   opens a new trade. it also opens a trade if there is no incoming trade, in contrast to the dr-flip
   mech"
  "rule#1 is applied to gate the non-trade sig_utc's"
  "dr-flip is the backstop - if a open trade did not reach a sig_utc before dr-flip, then dr_flip
   creates a trade reversal (closes and opens). dr-flip can only open a new trade if dr-flip needed
   to close an incoming (back-stopped) trade"

THE BACKSTOP IS THE FLIP **BACK TO** THE TRADE'S OWN dr, NOT THE FLIP OUT OF IT.  Joe 0929 corrected
an earlier build that had it inverted:

  "trade 1 starts at +1dr, creating a SHORT trade. -dr1 is the target side for a SHORT trade, so
   SHORT must go deeper into -1dr to claim more profit. the true dr-flip backstop for a SHORT trade
   is when the trade leaves its target side (because no trade signal closed it) and climbs towards
   +1dr (the backstop dr-flip)"

So a trade opened at dr D is WORKING while the dr sits at -D, and the backstop is the flip back to D
- the END of the -D stretch that follows, two flips forward from the open. The inverted version
closed every trade at the flip INTO its target side and produced 37 trades on 09-01 against 22 here.

A CONSEQUENCE, AND IT IS JOE'S RULE NOT MY CHOICE: at a backstop the dr is D again, so the trade the
flip opens carries the SAME direction as the one it just closed. Joe was shown this.

dr +1 = SHORT, dr -1 = LONG. Joe 0925: *"here's the rule for trading: +dr = SHORT position, -dr =
LONG postition"*.

SAME-BAR PRIORITY IS THE dr-FLIP. Joe 0929, asked directly: *"same bar priority: dr-flip"*.

STRICTLY CAUSAL, AND IT IS A BAR-BY-BAR LOOP FOR THAT REASON.  Joe 0929: *"make this causal before we
handover to a new session. ie, IF this bar has dr-flip THEN"*.

An earlier build computed each trade's backstop bar AT OPEN TIME, from the dr stretch list. That bar
is in the FUTURE when the trade opens. The walk never acted on it early, so the banked trades were
correct - but the SHAPE was lookahead, and a live implementation copying it would hold knowledge it
cannot have. Worse, that lookahead would be invisible to the recon, because both sides would agree.

The walk now carries two pieces of state per open trade and reads only `dr[k]` and `dr[k-1]`:

    dr      the trade's own dr, D, fixed at the open bar
    left    has the dr been -D at any bar since the open

At each bar, in this order:
    1  if dr[k] == -D            -> left = True          the trade is working
    2  if left and dr[k] == D and dr[k] != dr[k-1]  -> THIS BAR IS THE BACKSTOP
    3  else if this bar is an ungated sig_utc       -> reversal

Step 2 before step 3 is Joe's same-bar priority. Nothing reads past `k`.

It produces the same trades as the lookahead shape, and that is provable rather than lucky: the dr
latch alternates strictly - a change bar needs `d[k] != d[k-1]` and `d[k] != 0`, and the latch never
returns to 0 once set - so the first bar back at D after being -D IS the end of the -D stretch, which
is what the old `backstop()` returned. Verified over the banked window: 142 trades, identical.
"""


def walk(opens, dr, start, end):
    """-> ([trade], open_trade or None). Bar by bar, reading only `dr[k]` and `dr[k-1]`.

    opens  the bars that may open a trade. Already gated - this walk does not gate
    dr     the dr series
    start  the first bar to walk. Must be >= 1, because the backstop test reads `dr[k-1]`
    end    the last bar to walk

    A trade is a dict: open, close, dr, opened_by, closed_by. `opened_by` and `closed_by` are
    'sig_utc' or 'dr-flip'.
    """
    O = set(int(x) for x in opens)
    start = max(1, int(start))
    out = []
    pos = None
    for k in range(start, int(end) + 1):
        if pos is not None:
            d = int(dr[k])
            if d == -pos['dr'] and d != 0:
                pos['left'] = True                       # the trade has reached its target side
            if pos['left'] and d == pos['dr'] and d != int(dr[k - 1]):
                out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                opened_by=pos['opened_by'], closed_by='dr-flip'))
                pos = dict(open=k, dr=d, opened_by='dr-flip', left=False)
                continue                                 # same-bar priority: the flip wins
        if k in O:
            if pos is not None:
                out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                opened_by=pos['opened_by'], closed_by='sig_utc'))
            pos = dict(open=k, dr=int(dr[k]), opened_by='sig_utc', left=False)
    return out, pos


def mae_mfe(px, o, c, dr):
    """The excursions over [o, c] as PERCENTAGES of the entry, both non-negative. -> (mae, mfe).

    dr +1 is SHORT, so a rise is adverse and a fall is favourable. dr -1 is LONG, the other way.
    Joe 0917 closed P&L and kept MAE/MFE; this module reports excursions and never a return.
    """
    import numpy as np
    seg = np.asarray(px[int(o):int(c) + 1], float)
    e = float(px[int(o)])
    hi = float(np.nanmax(seg)); lo = float(np.nanmin(seg))
    if int(dr) > 0:
        return (hi - e) / e * 100.0, (e - lo) / e * 100.0
    return (e - lo) / e * 100.0, (hi - e) / e * 100.0
