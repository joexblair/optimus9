"""THE LINEAGE WALK — Joe's term, adopted 1007. The exit mech for the lazy-g port.

JOE'S RULINGS, verbatim:
  the open      *"there is no entry walk for this port of lazy-g. our port is signalling the open of
                 a trade _towards_ dr at every `no r block` event, so the trade is opened immediately
                 and the walk begins"*
  towards dr    *"if dr is +1, then `towards dr` is up, and the trade is LONG. inverse for -1dr"*
  exit-armed    *"at the first octo-sig that is NOT graded as `with-trend` or `no r block`"*  - JOE'S
                 NAME for that event, 1007: *"it's the `exit-armed` event"*. It is a START-LOOKING
                 bar, not the exit.
  the start     *"the walk starts on the trigger towards dr, and the `lineage walk` begins when it
                 finds ws1 momentum"*
  the exit      *"follow the momentum using the exact same mech that walks octo-sig forward - when
                 the momentum reaches it's final `stalled`, exit the trade"*
  the tag       *"if a rider has crossed to oob at any time, it takes a `waiting for stalled` tag
                 from the previous holder. that tag moves to the next TF (max riderTF+2) if the next
                 TF crosses to oob"* / *"the `waiting for stalled` line does not need to be oob when
                 `stalled` is printed"*
  upward only   *"it's important that the lineage walks TFs upward, never backwards"*
  the backstop  *"if the trade is LONG, the backstop is the flip to -1dr. if SHORT, backstop is the
                 flip to +1dr"* and 1007 *"the backstop is final and global"*
  momentum      *"momentum calcs remain based on `dr`, not `trade_side`"*
  empty ladder  *"if so, then the walk continues forward"*

THE WALK, as built:
  from `k_start` (the exit-armed bar), step forward ONE BAR AT A TIME:
    1. the backstop fires on a TRANSITION INTO the backstop dr (-1 for a LONG, +1 for a SHORT) and
       ends the walk. A trade already sitting on its backstop dr does NOT fire at bar 0 - dr must
       leave and come back.
    2. before the lineage has started: if ws1 is mom-true at this bar, the lineage STARTS with
       rider = ws1. Joe 1007. An empty r ladder is simply a bar where this has not happened yet.
    3. once started: a candidate in rider+1 .. rider+LIN_HOP whose r is oob takes the baton on that
       bar (the higher wins a same-bar tie - the walk is upward).
    4. the rider's `stalled` prints -> FINAL STALLED. That bar is the exit.

  A PER-BAR TEST, NOT A FORWARD SEARCH. Joe 1006: *"we're walking a forward loop, so the use of `IF
  this bar has condition THEN...` is an easy way out of lookahead"*. Nothing here reads a bar the
  walk has not reached.
"""
import sys, io
_e = sys.stderr; sys.stderr = io.StringIO()
import numpy as np
sys.stderr = _e


def rider_at(Rl, k, d, oob_hi, oob_lo, lin_tf):
    """The highest TF in `lin_tf` whose r is oob on the dr side at bar k, or None.

    NOT the lineage walk's start any more - Joe 1007 ruled the walk begins at ws1 momentum. Kept
    because it is still the honest answer to "which line is beyond the fence at this bar", which is
    what branchD's `blk` asks and what the `no r block` verdict reports.
    """
    out = None
    for t in lin_tf:
        v = float(Rl[t][k])
        if not np.isfinite(v): continue
        if (v >= oob_hi) if d > 0 else (v <= oob_lo):
            out = t
    return out


def walk(Rl, DRv, mom_true, stalled, k_start, d_sig, oob_hi, oob_lo, last_bar,
         lin_tf, lin_hop, trade_side):
    """Joe's lineage walk from `k_start` to the exit bar. -> dict.

        mom_true(t, k)  True when ws{t} is mom-true at bar k, read on `d_sig`
        stalled(t, k)   True when ws{t} is stalled at bar k, read on `d_sig`
        d_sig           the dr every MOMENTUM read uses. Never trade_side.
        trade_side      'LONG' or 'SHORT' - picks the BACKSTOP only.
    """
    back_dr = -1 if str(trade_side).upper() == 'LONG' else +1
    prev_dr = int(DRv[k_start])
    anchor = lin_tf[0]
    out = {'start_k': None, 'chain': [], 'exit_k': None, 'why': None, 'rider': None,
           'back_dr': back_dr, 'ties': 0, 'holder_oob_at_exit': None}
    oob = (lambda v: v >= oob_hi) if d_sig > 0 else (lambda v: v <= oob_lo)
    rider = None
    for k in range(k_start, last_bar + 1):
        dr_k = int(DRv[k])
        if dr_k == back_dr and prev_dr != back_dr:
            out['why'] = 'dr backstop'; out['exit_k'] = k; break
        prev_dr = dr_k
        if rider is None:
            if mom_true(anchor, k):                       # ws1 momentum starts the lineage
                rider = anchor
                out['start_k'] = k; out['chain'] = [(k, rider)]
            continue
        cand = [t for t in range(rider + 1, min(rider + lin_hop, lin_tf[-1]) + 1)
                if np.isfinite(Rl[t][k]) and oob(float(Rl[t][k]))]
        if cand:
            if len(cand) > 1: out['ties'] += 1
            rider = max(cand)                             # upward: the further step wins
            out['chain'].append((k, rider))
            continue
        if stalled(rider, k):
            v = float(Rl[rider][k])
            out['why'] = 'final stalled'; out['exit_k'] = k
            out['holder_oob_at_exit'] = bool(np.isfinite(v) and oob(v))
            break
    else:
        out['why'] = 'tape end'
    out['rider'] = rider
    return out
