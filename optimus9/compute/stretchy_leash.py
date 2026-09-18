"""stretchy_leash — the coil on a line, and how many lines support it.

Joe 0917, verbatim:
    "we know that m and Mage will lead r around the board like it's on a stretchy leash. the
     further m and Mage are away from r, the more energy is coiled up in the stretchy leash"
    "stretchy leash: m and Mage vs r, does r still have room to be pushed"

ONE JOB: turn (m, Mage, r, dr) into a coil number. No rows, no moments, no DB, no Jig. The
grouping lives in coil_moment.py and the exit rule lives in coil_exit.py.

    coil(m, Mage, r, dr) = dr * ((m + Mage)/2 - r)

Positive means m and Mage sit AHEAD of r on the dr side, so r still has room to be pushed toward
dr. Negative means r has already run past them.

CAUSAL by construction — every value reads bar i of three lines that are themselves `emerging`.
Nothing reads forward.
"""
import numpy as np


def coil(m, mage, r, dr):
    """The stretchy leash on one line, dr-signed. Arrays in, array out (or scalars in, scalar out)."""
    return dr * ((np.asarray(m, float) + np.asarray(mage, float)) / 2.0 - np.asarray(r, float))


def combined_coil(lines, keys, dr):
    """The coil of several lines, summed.

    `lines` is {name: {'m': arr, 'Mage': arr, 'r': arr}}; `keys` is the ordered list of names to
    add, which is the `coil_lines` knob. Joe 0917 set it to the 30 s line plus the 1 min line.
    """
    out = None
    for k in keys:
        L = lines[k]
        c = coil(L['m'], L['Mage'], L['r'], dr)
        out = c if out is None else out + c
    return out


def support_count(lines, keys, dr, i):
    """How many of `keys` carry a POSITIVE coil at bar `i`. NaN counts as no support.

    This is the confluence measure: `support_min` of them all positive is a moment's entry test.
    """
    n = 0
    for k in keys:
        L = lines[k]
        v = coil(L['m'][i], L['Mage'][i], L['r'][i], dr)
        if np.isfinite(v) and v > 0:
            n += 1
    return n
