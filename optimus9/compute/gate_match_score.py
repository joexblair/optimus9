"""
gate_match_score — the gate sweep's objective (Stage 1 scorer).

Scores how well a gate's breach windows align with the price-intrinsic profit
partition (profit_partition.py). See gate_sweep_design.md.

POLARITY BRIDGE — the one place that owns it:
  The gate's oob_side is INVERTED vs trade direction. LO breach (gate=-1) is the
  LONG-enabling state; HI breach (gate=+1) the SHORT-enabling state — grounded in
  optimizer_runner's AND composition ("vote=+1 long needs oob_side=-1"). The
  profit partition uses natural trade polarity (long=+1). So a directional hit is

      gate == -P            (for bars where both are nonzero)

  i.e. LO breach(-1) ↔ long-P(+1), HI breach(+1) ↔ short-P(-1). This inversion is
  tested hard in test_gate_match_score.py — a `gate == P` slip would silently
  invert the entire gate objective.
"""
import numpy as np


def gate_match_score(gate_mask: np.ndarray, p_cls: np.ndarray) -> dict:
    """
    Gate match score = hits / painted — IoU over the union of breached bars and
    tradeable bars; both-silent bars (in-band ∧ neither) are excluded from the
    denominator so easy correct-silence can't inflate it.

    gate_mask : array {-1 LO breach, 0 in-band, +1 HI breach}
    p_cls     : array {+1 long-P, -1 short-P, 0 neither}, same length

    Returns dict:
      score       : hits / painted, or NaN if nothing is painted
      hits        : gate breaches the side that ENABLES P's direction (gate==-P)
      painted     : gate breaches OR P is tradeable
      gate_open   : bars the gate breaches (LO or HI)
      tradeable   : bars P is long/short
      false_open  : gate breaches but it is not a hit (wrong side or P neither)
      missed      : P tradeable but not a hit (gate shut or wrong side)
      wrong_side  : gate breaches the side enabling the OPPOSITE of P (harmful)
    """
    gate = np.asarray(gate_mask)
    P    = np.asarray(p_cls)
    if gate.shape != P.shape:
        raise ValueError(f'shape mismatch: gate {gate.shape} vs P {P.shape}')

    g_open  = gate != 0
    p_trade = P != 0
    both    = g_open & p_trade

    hit        = both & (gate == -P)      # the polarity bridge (LO<->long, HI<->short)
    wrong_side = both & (gate ==  P)      # breaching the harmful side
    painted    = g_open | p_trade

    n_painted = int(painted.sum())
    n_hits    = int(hit.sum())
    return {
        'score':      (n_hits / n_painted) if n_painted else float('nan'),
        'hits':       n_hits,
        'painted':    n_painted,
        'gate_open':  int(g_open.sum()),
        'tradeable':  int(p_trade.sum()),
        'false_open': int((g_open  & ~hit).sum()),
        'missed':     int((p_trade & ~hit).sum()),
        'wrong_side': int(wrong_side.sum()),
    }


def overlap_score(gate_mask: np.ndarray, target_mask: np.ndarray) -> dict:
    """
    Direction-agnostic gate objective (the LIVE scorer — `gate_match_score`
    above is the legacy trading-framed version). Measures how well the gate's
    OPEN windows (|gate| > 0, either side) overlap a target mask (e.g. the
    forward-walk "≥0.9% reachable from here" bars). See gate_sweep_design.md.

      score     : IoU = |open ∩ target| / |open ∪ target|  (NaN if nothing painted)
      recall    : fraction of target bars the gate is open during
      precision : fraction of open bars that are target bars
    """
    go = np.asarray(gate_mask) != 0
    tg = np.asarray(target_mask).astype(bool)
    if go.shape != tg.shape:
        raise ValueError(f'shape mismatch: gate {go.shape} vs target {tg.shape}')
    inter = int((go & tg).sum())
    uni   = int((go | tg).sum())
    n_go, n_tg = int(go.sum()), int(tg.sum())
    return {
        'score':     inter / uni  if uni  else float('nan'),
        'recall':    inter / n_tg if n_tg else 0.0,
        'precision': inter / n_go if n_go else 0.0,
        'open':      n_go,
        'target':    n_tg,
        'inter':     inter,
    }
