"""trade_walk — Joe 0929's trade rules, as a walk over already-decided events.

ONE JOB: given the bars that may open a trade and the dr stretches, say where every trade opens and
closes. It computes no gate, reads no line, touches no DB and prints nothing. The gate is
`rule1_gate.gate`, the dr is `dr_latch`, the signals are `wsf_leash.wsl_sig_utc`.

JOE'S RULES, VERBATIM 0929:
  "every ungated sig_utc timestamps create a trade reversal - ie it closes the existing trade and
   opens a new trade. it also opens a trade if there is no incoming trade, in contrast to the dr-flip
   mech"
  "rule#1 is applied to gate the non-trade sig_utc's"

A sig_utc CLOSES ONLY ON AN OPPOSING dr. Joe 0929, after spotting 09-01 03:40:05 - a SHORT - being
closed by the 04:26:00 sig_utc, which was ALSO a SHORT:

  "trades must be first closed by an opposing dr signal, and secondly by a dr-flip if there is not
   opposing dr signal"

So "reversal" in his rule above means a REVERSAL OF dr, not merely the next signal. This walk used
to close on any bar in `opens` with no dr comparison at all, and on the banked window that was 43 of
67 sig_utc closes - 64% of them - closing a trade into a signal of its own direction. A same-dr
sig_utc is now INERT: it cannot close (not opposing) and cannot open (one already runs that way).
Joe 0929, asked whether it should touch the trade at all - reset `left`, extend, anything:
*"for now, it's inert"*.
  "dr-flip is the backstop - if a open trade did not reach a sig_utc before dr-flip, then dr_flip
   creates a trade reversal (closes and opens). dr-flip can only open a new trade if dr-flip needed
   to close an incoming (back-stopped) trade"

THE dr-FLIP BACKSTOP CLOSES BUT NEVER OPENS. Joe 0929-late, SUPERSEDING the "closes and opens" half
of the rule he wrote above, after being shown that up to 94% of a swept config's trades were flip
opens:

  "now we have the data I can see that dr-flip as an open is not helpful. the cost is accceptable -
   it gives us space to apply other mechs (lazy-g for example)"

So at a backstop the position is closed and THE BOOK GOES FLAT. It still closes, or a trade would
run to the next opposing signal whatever happened. Over 09-01..09-06 the book is flat 43.8 h of
119.5 h - 36.6%.

THE BACKSTOP IS THE FLIP **BACK TO** THE TRADE'S OWN dr, NOT THE FLIP OUT OF IT.  Joe 0929 corrected
an earlier build that had it inverted:

  "trade 1 starts at +1dr, creating a SHORT trade. -dr1 is the target side for a SHORT trade, so
   SHORT must go deeper into -1dr to claim more profit. the true dr-flip backstop for a SHORT trade
   is when the trade leaves its target side (because no trade signal closed it) and climbs towards
   +1dr (the backstop dr-flip)"

So a trade opened at dr D is WORKING while the dr sits at -D, and the backstop is the flip back to D
- the END of the -D stretch that follows, two flips forward from the open. The inverted version
closed every trade at the flip INTO its target side and produced 37 trades on 09-01 against 22 here.

THAT CONSEQUENCE IS GONE. It used to read: at a backstop the dr is D again, so the trade the flip
opens carries the SAME direction as the one it just closed. Joe was shown exactly that, and it is
what he ruled out - see the flip-open ruling above. Nothing opens at a backstop.

dr +1 = SHORT, dr -1 = LONG. Joe 0925: *"here's the rule for trading: +dr = SHORT position, -dr =
LONG postition"*.

SAME-BAR PRIORITY IS THE dr-FLIP. Joe 0929, asked directly: *"same bar priority: dr-flip"*. The
flip is tested first and the bar is then DONE - a sig_utc on a backstop bar does not open. That is
what `sweep_mae_cap.py` measured, and it is where Joe's 753 trades / +0.3776 per trade come from.

THE STOP IS A THIRD EXIT AND IT RACES THE OTHER TWO. Joe 0929-late, correcting a build that had it
replacing them: *"research how a stop is applied in trading - you'll learn that it's both: (at its
signal or flip bar) OR (at the stop bar)"*. That is the OCO mechanic - every exit goes live when the
entry fills and the first to fire cancels the rest.

So an open trade carries THREE live exits: an opposing-dr sig_utc, the dr-flip backstop, and the
stop. Whichever comes first ends it. `mae_cap=None` removes the stop entirely and gives the
uncapped mech - a DIFFERENT mech, and not the one that is handed over.

THE CAP'S VALUE IS NOT IN THIS FILE. Joe 0929-late: *"move MAE_CAP to the DB"*. It is
`wsf_trade_config` v3 row `mae_cap`, 0.70. `mae_cap` is a REQUIRED argument here so that no caller
can pick up a default this module has no authority to set.

WHAT THE STOP CHANGES, MEASURED OVER 90 DAYS. No trade re-scores: a stopped trade is -cap either
way. What moves is its CLOSE BAR, and therefore when the book frees up. The book used to be held a
median 1177 bars - 98 minutes - past the stop bar; 216 ungated sig_utc bars sat inside those
windows, INERT because a position was open. Freeing them takes 753 trades to 894 and +0.3776 to
+0.3911 per trade.

SAME-BAR TIES: THE STOP WINS. Joe 0929-late, asked directly: *"use stop"*. Measured over the 90-day
window the tie never occurs - 0 stop-and-flip and 0 stop-and-sig_utc collisions across all 381
stops - so the rule is written for a window that does collide, not for this one.

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
is what the old `backstop()` returned. Verified over the banked window, identical every time; the
window as it stands closes 119 trades and leaves the 120th open at the 2026-09-06 00:00 edge.
"""


def walk(opens, dr, px, start, end, mae_cap):
    """-> ([trade], open_trade or None). Bar by bar, reading only `dr[k]` and `dr[k-1]`.

    opens    the bars that may open a trade. Already gated - this walk does not gate
    dr       the dr series
    px       the price series the stop reads. `pxs` = DEMA(close, 2) on the event tape
    start    the first bar to walk. Must be >= 1, because the backstop test reads `dr[k-1]`
    end      the last bar to walk
    mae_cap  the stop, % of entry. REQUIRED - read it from `wsf_trade_config`, never
             hard-code it. None removes the stop and gives a DIFFERENT mech

    A trade is a dict: open, close, dr, opened_by, closed_by. `opened_by` is 'sig_utc';
    `closed_by` is 'sig_utc', 'dr-flip' or 'stop'.
    """
    O = set(int(x) for x in opens)
    start = max(1, int(start))
    out = []
    pos = None
    for k in range(start, int(end) + 1):
        if pos is not None:
            d = int(dr[k])
            if mae_cap is not None:
                e = float(px[pos['open']])
                adv = -((float(px[k]) - e) / e * 100.0) * pos['dr']
                if -adv >= mae_cap:
                    out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                    opened_by=pos['opened_by'], closed_by='stop'))
                    pos = None
                    continue                             # Joe 0929: the STOP wins the bar
            if d == -pos['dr'] and d != 0:
                pos['left'] = True                       # the trade has reached its target side
            if pos['left'] and d == pos['dr'] and d != int(dr[k - 1]):
                out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                opened_by=pos['opened_by'], closed_by='dr-flip'))
                pos = None                               # the flip CLOSES but never OPENS - Joe 0929
                continue                                 # same-bar priority: the flip wins
        if k in O:
            d = int(dr[k])
            if pos is not None and not (d == -pos['dr'] and d != 0):
                continue                                 # same-dr sig_utc is INERT - Joe 0929
            if pos is not None:
                out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                opened_by=pos['opened_by'], closed_by='sig_utc'))
            pos = dict(open=k, dr=d, opened_by='sig_utc', left=False)
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
