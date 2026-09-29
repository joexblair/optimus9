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

CAUSAL, WITH ONE THING TO KNOW. Every bar this walk reads is at or before the event it is deciding.
The dr stretch END it uses as a backstop is a FUTURE bar at the moment the trade opens - but the walk
never acts on it early: it only closes the trade when that bar arrives. A live consumer must treat
the backstop as a standing order, not as knowledge.
"""


def backstop(stretches, bar):
    """The bar that back-stops a trade opened at `bar`. -> bar or None.

    `stretches` is `test_points.stretches`, [(start, end, dr)] with end exclusive. The trade's own
    stretch is the one containing `bar`; the backstop is the END of the NEXT stretch, which is the
    flip back to the trade's own dr. None when the tape runs out first.
    """
    i = next((j for j, s in enumerate(stretches) if s[0] <= bar < s[1]), None)
    if i is None or i + 1 >= len(stretches):
        return None
    return int(stretches[i + 1][1])


def walk(opens, stretches, dr, end):
    """-> ([trade], open_trade or None).

    opens      the bars that may open a trade, ASCENDING. Already gated - this walk does not gate.
    stretches  `test_points.stretches`
    dr         the dr series, read at whatever bar a trade opens on
    end        the last bar the walk may reach

    A trade is a dict: open, close, dr, opened_by, closed_by. `opened_by` and `closed_by` are
    'sig_utc' or 'dr-flip'.
    """
    out = []
    pos = None
    for k in sorted(int(x) for x in opens):
        if k > int(end):
            break
        if pos is None:
            pos = dict(open=k, dr=int(dr[k]), opened_by='sig_utc', bs=backstop(stretches, k))
            continue
        while pos['bs'] is not None and pos['bs'] <= k:          # the backstop bites first
            b = pos['bs']
            out.append(dict(open=pos['open'], close=b, dr=pos['dr'],
                            opened_by=pos['opened_by'], closed_by='dr-flip'))
            pos = dict(open=b, dr=int(dr[b]), opened_by='dr-flip', bs=backstop(stretches, b))
        if pos['open'] == k:                                     # the flip landed on this same bar
            continue
        out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                        opened_by=pos['opened_by'], closed_by='sig_utc'))
        pos = dict(open=k, dr=int(dr[k]), opened_by='sig_utc', bs=backstop(stretches, k))
    while pos is not None and pos['bs'] is not None and pos['bs'] <= int(end):
        b = pos['bs']
        out.append(dict(open=pos['open'], close=b, dr=pos['dr'],
                        opened_by=pos['opened_by'], closed_by='dr-flip'))
        pos = dict(open=b, dr=int(dr[b]), opened_by='dr-flip', bs=backstop(stretches, b))
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
