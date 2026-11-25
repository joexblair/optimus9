"""fdm3-htf-oracle - HIS 1124 *"I need a parallel webservice built, named fdm3-htf-oracle"*.

fdm3-oracle's own file with FDM3_PAGE=htf: his 16 columns ws20..ws30, ws45, ws60, ws90, ws120, ws240 in place of every
column but the time, the same cell data as fdm3-oracle's ws1..ws15, rows on the 1-minute seam, and the b9 colours
against the target-side. Every rule is in fdm3_oracle.py under HTF; this file only sets the page and runs it.

usage: fdm3_htf_oracle.py [port]   then open http://127.0.0.1:<port>
"""
import os
import runpy
import sys

os.environ['FDM3_PAGE'] = 'htf'
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fdm3_oracle.py'), run_name='__main__')
