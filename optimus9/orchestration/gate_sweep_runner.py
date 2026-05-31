"""
gate_sweep_runner — composes the gate sweep (orchestration core).

Pure functions: given a base 5s DataFrame, a precomputed profit partition, a
list of grid combos, and a gate template, return per-combo gate match scores.
No DB — the driver (gate_sweep_report.py) loads klines, builds the grid, and
writes the report.

Composes IndicatorComputer (mask primitives) + gate_match_score (objective) +
profit_partition (ground truth, precomputed once). See gate_sweep_design.md.

The `template` is a list of per-line specs — swap it to sweep other line pairs
(the gate is a configurable line-pair, not hardcoded bnyM/bnyp):
  line_type / itf_seconds / low_b / high_b — the line's frame (15/85 gospel)
  fixed   — held-constant config fields
  params  — config field -> grid combo key that fills it
"""
import numpy as np

from ..compute.indicator_computer import IndicatorComputer as IC
from ..compute.gate_match_score import gate_match_score


# Scout A: bnyM (BB) + bnyp (K), AND-folded, 30s, boundaries 15/85.
SCOUT_A_TEMPLATE = [
    {'line_type': 'bb', 'itf_seconds': 30, 'low_b': 15, 'high_b': 85,
     'fixed': {},
     'params': {'ic_src': 'M_src', 'ic_bb_len': 'M_bb_len', 'ic_bb_mult': 'M_bb_mult'}},
    {'line_type': 'k',  'itf_seconds': 30, 'low_b': 15, 'high_b': 85,
     'fixed': {'ic_rsi_len': 114, 'ic_stc_len': 105},
     'params': {'ic_src': 'p_src', 'ic_k_len': 'p_k_len'}},
]


def build_gate_configs(combo: dict, template: list) -> list:
    """Map a grid combo + template into per-line config dicts that
    IndicatorComputer.compute_oob_side consumes."""
    cfgs = []
    for spec in template:
        cfg = {'ic_itf_seconds':  spec['itf_seconds'],
               'ic_line_type':    spec['line_type'],
               'ic_high_boundary': spec['high_b'],
               'ic_low_boundary':  spec['low_b']}
        cfg.update(spec['fixed'])
        for field, grid_key in spec['params'].items():
            cfg[field] = combo[grid_key]
        cfgs.append(cfg)
    return cfgs


def _line_side(cfg: dict, base_df) -> np.ndarray:
    """One line's aligned oob_side, cleaned to int8 {-1,0,+1} (NaN→0 via fold)."""
    gate_df = IC.resample(base_df, int(cfg['ic_itf_seconds']))
    oob     = IC.compute_oob_side(cfg, gate_df)
    side    = IC.align_to_base(oob, gate_df, base_df)
    return IC._fold_and([side])


def _fold(sides: list, fold: str):
    """OR (fold_gates) is the production rule for bny30M/p (either line OOB);
    AND (_fold_and) is retained for the conservative both-OOB variant."""
    return IC.fold_gates(sides) if fold == 'OR' else IC._fold_and(sides)


def score_combo(combo: dict, template: list, base_df, p_cls: np.ndarray,
                fold: str = 'OR') -> dict:
    """Score one combo: combined gate match score + per-line solo scores.
    fold defaults to OR (the bny30 rule: gate open when EITHER line is OOB)."""
    cfgs     = build_gate_configs(combo, template)
    sides    = [_line_side(cfg, base_df) for cfg in cfgs]
    combined = _fold(sides, fold)
    res = gate_match_score(combined, p_cls)
    res['solo_scores'] = [gate_match_score(s, p_cls)['score'] for s in sides]
    res['combo'] = combo
    return res


def run_sweep(combos: list, template: list, base_df, p_cls: np.ndarray,
              progress: int = 0, fold: str = 'OR') -> list:
    """Score every combo; return results sorted by match score (desc, NaN last)."""
    results = []
    for i, combo in enumerate(combos):
        results.append(score_combo(combo, template, base_df, p_cls, fold=fold))
        if progress and (i + 1) % progress == 0:
            print(f'  scored {i + 1}/{len(combos)}')
    results.sort(key=lambda r: (np.isnan(r['score']),
                                -r['score'] if not np.isnan(r['score']) else 0.0))
    return results
