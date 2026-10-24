"""v4saviour's SIGNAL PRODUCER, and nothing else. Joe 1024.

ONE RESPONSIBILITY: given an open position block, state whether v4saviour prints a signal for it.

IT IS THE ONE PRODUCER THAT IS POSITION-BOUND, and that is by construction rather than by choice:
v4saviour's arm reads a 30-minute walkback from the trade open, and its whole mech runs under one
cap timer from that open. There is no open bar to read without a position.

ONE SAVIOUR, NOT ONE PER POSITION. Joe 1024, asked whether each open position gets its own:

    no.  a single saviour will open on qualification and defer to the router if `saviour-rev`
    prints.  the router will close them all together

So this file is called with the BLOCK - every position open on one side - and it reads the block's
EARLIEST open bar. That is my structural read and it is stated rather than defaulted: both the arm
walkback and the cap measure from when the position was established, and the earliest open is when
that happened.

A SAVIOUR SIGNAL CARRIES THE BLOCK'S TARGET-SIDE, so it closes the block and opens the opposite -
which is what `SAVIOUR REV` has always meant. `STAYS OPEN` and `NOT ARMED` produce no signal.

THE WALK IS NOT REIMPLEMENTED. `v4_saviour.walk` owns branch A, branch B, his route clause and the
verdicts.
"""
import io
import sys

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_saviour as SV
import v4_signal as SG
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e


def produce(block_open, block_dir, R, MG):
    """v4saviour on one open block. -> a signal, or None.

        block_open  the EARLIEST open bar of the block - see the module docstring
        block_dir   'LONG' or 'SHORT'. The block is one direction by definition
    """
    s = SG.target_side(block_dir)
    res = SV.walk(int(block_open), s, R, MG, ln.U)
    if res['verdict'] != 'SAVIOUR REV':
        return None
    return SG.signal(int(res['fill']), s, 'saviour', int(block_open),
                     'fill %s, armed on the %s block opened %s'
                     % (ln.U(res['fill']), block_dir, ln.U(block_open)))
