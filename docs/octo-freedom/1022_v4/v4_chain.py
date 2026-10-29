"""THE CHAIN: its open, its legs, and their scoring. ONE copy of the loop.

WHY IT EXISTS. The chain loop was written out three times - in 1027_pseudo_closed/legs_blocks.py,
1029_exfnc_latch/latch_validate.py and 1029_exfnc_latch/sweep1_mintf.py - and each copy carried its
own idea of where the chain opens and what a leg is worth. His 1029 chain-open ruling has to land
in one place, so the loop lives here and the drivers render it.

THREE THINGS IT OWNS:

    1  THE OPEN. LIN2_CHAIN_OPEN_ON 1 produces it from `v4_l2_cadence.chain_open` - his ws5Mage
       mech. At 0 it falls back to the old handed-in open: the window's first bar on a side passed
       in, which was never a mech.
    2  THE LEGS. Walk, reverse at each exhaust, repeat. The exhaust bar IS the rev-trade bar, so a
       leg opens one bar after the previous exhaust and its fill is priced there.
    3  THE SCORING. Per leg: MAE and MFE off the highs and lows over [open, exit], realised at the
       fill bar, and drag in its OWN column with its OWN total - never folded into a net.

NO CAP, NO HORIZON. Every leg between the open and the window's end is walked and scored.

THE ZERO-LENGTH LEG, which only shows up past one day: walk N exhausts at bar E, the opposite side
opens at E + 1, and walk N + 1 - whose scan starts AT E - also exhausts at E, because E carries a
cadence for both sides. Its open is then after its exit and it spans no bars. Those are RECORDED
and NOT scored, and whether such a leg pays the drag is UNRULED - `zero` carries them out so a
report can state it.
"""
import io
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K
import v4_l2_cadence as CAD
import v4_lineage2 as L2
import v4_signal as SG
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e

DRAG_PCT = 0.1975      # % round trip, o9-live drag_pct: 11.0 bps fee + 8.75 bps slippage


def opening(B1, MG, A, fallback_side=+1, open_at=None):
    """Where and how the chain opens. -> dict.

    `B1` is EMERGING ws1b and `MG` the EMERGING Mage ladder - his 1029 ruling that closed_prev is
    not an option. `bar` may be BEFORE `A`: his option B keeps the window where it is and lets the
    chain reach back for the open that was already running into it.
    """
    if open_at is not None:
        #   AN OPEN HANDED IN. The router owns the fire bar and the direction, so a comparison
        #   driver passes what the router decided rather than re-deriving it here.
        b, sd = int(open_at[0]), int(open_at[1])
        return dict(bar=b, side=sd, cand_side=-sd, anchor=None, lines=(), trig=float('nan'),
                    src='handed in by the caller - the router picked it')
    if int(K.LIN2_CHAIN_OPEN_ON):
        r = CAD.chain_open(B1, MG, int(A))
        assert r is not None, ('no ws1b oob->ib cross with the ws%dMage gate and %d lines away at'
                               ' the anchor, at or before %s - the chain has no open'
                               % (K.LIN2_CHAIN_OPEN_TF, K.LIN2_CHAIN_OPEN_LINES, ln.U(A)))
        r['src'] = 'ws1b oob->ib, ws%dMage gate, anchor %s' % (K.LIN2_CHAIN_OPEN_TF,
                                                               ln.U(r['anchor']))
        return r
    return dict(bar=int(A), side=int(fallback_side), cand_side=0, anchor=None, lines=(),
                trig=float('nan'), src='handed in at the window start')


def stop_bar(opn, ex, side, close, phi, plo, cap):
    """The first bar the adverse excursion reaches `cap`. -> bar or None. Walked, not inferred.

    Joe 1027 set the level: *"if MAE > 1.1, cap mae at 1.1 and print"*, and the 1028 take-profit
    sweep already walked it this way - the adverse excursion reaching LIN2_MAE_CAP gives a realised
    of minus the cap.

    INTRA-BAR TIES GO TO THE ADVERSE SIDE. Inside one 5 s bar the high and the low are both there
    and their order is unknown, so a bar that breaches the cap is the stop even if it also moved
    favourably. That convention is MINE, it is the conservative one, and it is stated here.
    """
    o = float(close[int(opn)])
    adv = np.asarray(plo[int(opn):int(ex) + 1], float) if side > 0 \
        else np.asarray(phi[int(opn):int(ex) + 1], float)
    pct = int(side) * (adv - o) / o * 100.0
    hit = np.flatnonzero(pct <= -float(cap))
    return int(opn) + int(hit[0]) if len(hit) else None


def legs(CL, BD, close, phi, plo, A, B, MG=None, fallback_side=+1, B1=None, open_at=None,
         mae_cap=None, resig=None):
    """Every leg of the chain from its open to `B`. -> (legs, zero, opening).

    Each leg dict carries: opn, side, exit, ctype, verdict, rows, mae, mfe, rel, held_min.
    """
    assert open_at is not None or not int(K.LIN2_CHAIN_OPEN_ON) \
        or (B1 is not None and MG is not None), \
        'the chain open needs ws1b and the Mage ladder handed in'
    op = opening(B1, MG, A, fallback_side, open_at)
    out, zero = [], []
    side, frm, prev = int(op['side']), int(op['bar']), None
    while frm < int(B):
        v, bar, rows = L2.walk(CL, BD, close, side, frm, int(B))
        opn = int(op['bar']) if prev is None else int(prev) + 1
        if bar is None:
            out.append(dict(opn=opn, side=side, exit=None, ctype='no exhaust', verdict=v,
                            rows=rows, stopped=False))
            break
        #   THE EXIT LABEL. The cadence exhausts carry a ctype on an EXHAUST row; the divergence
        #   rev-trade at v4_lineage2.py:412 returns a bar with a DIV row and NO EXHAUST row, so a
        #   reader that only looks for EXHAUST prints '-' for a real exit. Measured on 2026-08-30:
        #   1 leg of 21, the 22:04:00 SHORT, verdict 'DIV REV-TRADE'. The verdict is the fallback.
        ex = [r for r in rows if r['stage'] == 'EXHAUST']
        ct = str(ex[-1].get('ctype') or 'retest') if ex else str(v)
        assert ct and ct != '-', 'a scored leg has no exit label - a branch is unaccounted for'
        if int(bar) < opn:
            zero.append(dict(opn=opn, exit=int(bar), side=side, ctype=ct))
            prev = int(bar)
            frm, side = max(int(bar), frm + 1), -side
            continue
        #   THE CAP AS A STOP. When it bites, the leg ends at the stop bar with a realised of
        #   minus the cap, and THE CHAIN GOES FLAT - his own first line for lin2-reentry is
        #   *"there is no trade open (either because of a STOP, or because the machine is
        #   cold-starting)"*. The way back in is the next lin2-reentry signal after the stop.
        stopped = None
        if mae_cap is not None:
            stopped = stop_bar(opn, bar, side, close, phi, plo, mae_cap)
        if stopped is not None:
            bar = int(stopped)
            ct = 'STOP at %.2f%%' % float(mae_cap)
        lo, hi = int(opn), int(bar)
        H = np.asarray(phi[lo:hi + 1], float)
        L = np.asarray(plo[lo:hi + 1], float)
        assert len(H), 'a scored leg has no bars - the zero-length guard above was bypassed'
        if side > 0:
            ap, vp = float(np.nanmin(L)), float(np.nanmax(H))
        else:
            ap, vp = float(np.nanmax(H)), float(np.nanmin(L))
        o = float(close[opn])
        out.append(dict(opn=opn, side=side, exit=int(bar), ctype=ct, verdict=v, rows=rows,
                        mae=min(abs(side * (ap - o) / o * 100.0),
                                float(mae_cap) if mae_cap is not None else float('inf')),
                        mfe=side * (vp - o) / o * 100.0,
                        rel=(-float(mae_cap) if stopped is not None
                             else side * (float(close[int(bar) + 1]) - o) / o * 100.0),
                        held_min=(int(bar) - opn) * 5 / 60.0,
                        stopped=stopped is not None))
        prev = int(bar)
        if stopped is not None:
            #   FLAT after a stop. The next open is the next lin2-reentry signal, and its side
            #   comes from the layer's own two conversions, never from flipping the last trade.
            nxt = [g for g in (resig or []) if int(g['bar']) > int(bar)]
            if not nxt:
                break
            g = nxt[0]
            d = SG.direction(int(g['side']))
            nb = SG.fire_bar(g)
            assert nb > int(bar), 'a re-entry fire bar is not after the stop that caused it'
            prev = nb - 1
            frm, side = nb, SG.target_side(d)
            continue
        frm, side = max(int(bar), frm + 1), -side
    return out, zero, op


def score(lg, drag=None):
    """The totals over a leg list. -> dict. Drag keeps its own entry AND its own total."""
    d = DRAG_PCT if drag is None else float(drag)
    k = [x for x in lg if x['exit'] is not None]
    n = len(k)
    rel = sum(x['rel'] for x in k)
    return dict(n=n, unres=len(lg) - n, mae=sum(x['mae'] for x in k),
                mfe=sum(x['mfe'] for x in k), rel=rel, drag=d * n, net=rel - d * n,
                held=sum(x['held_min'] for x in k),
                win=sum(1 for x in k if x['rel'] - d > 0),
                stops=sum(1 for x in k if x.get('stopped')),
                barr=sum(1 for x in k if x['ctype'] == 'barrage'))
