"""
ui/app.py — the strat_review settings UI (Joe 0627). The "Strategy" page: a grid of bias_producer
modules (enable + unfold config) + a persistent notes pane + "save & update" (re-runs strat_review).

Data-driven: the grid is a view over `bias_producer` (the module registry); config knobs come from
`lp_config` (per-producer mapping below). v1 exposes the lp_config dials + read-only table summaries;
richer per-producer config (gate chain, lines) follows as that config moves DB-resident (#35 no-hardcode).

Run:  ui/venv/bin/python ui/app.py   → http://127.0.0.1:5000
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
from flask import Flask, render_template, request, jsonify
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from alchemy_report import _active_breach_lines
from strat_review import build_strat_review

app = Flask(__name__)

# the analysis window strat_review reports on (matches strat_review.py; TODO make this a UI control)
END_MS = int(dtm.datetime(2026, 6, 22, tzinfo=timezone.utc).timestamp() * 1000)

# producer -> its editable lp_config knobs (v1). Empty = no DB-resident knobs yet (config still in code).
PRODUCER_LP = {
    'cascade':   ['lp_xm45_wob'],
    'bro_cross': ['lp_bro_wob'],
    'bl_state':  [],
    'pk':        [],
    'trades':    [],
}


def _db():
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute('''CREATE TABLE IF NOT EXISTS ui_notes (
        note_pk INT PRIMARY KEY, note_text MEDIUMTEXT, updated_at DATETIME)''')   # MEDIUMTEXT = 16MB ≫ 10k
    return d


def _summary(d, name):
    """A read-only one-liner of the producer's non-knob config (the bits not yet a clean DB dial)."""
    if name == 'cascade':
        gates = [g['tg_name'] for g in d.execute(
            'SELECT tg_name FROM trade_gate WHERE tg_active=1 ORDER BY tg_seq', fetch=True)]
        return 'gate chain: ' + ' → '.join(gates) if gates else 'no active gates'
    if name == 'bl_state':
        lines = _active_breach_lines(d)
        return 'breach lines: ' + (', '.join(lines) if lines else 'none active')
    if name == 'bro_cross':
        return 'sets: hbhl16 · hblo16 · hbhi16 (in code — #35)'
    return 'config in code (no DB knobs yet — #35 no-hardcode sweep)'


@app.route('/')
def index():
    return render_template('strategy.html')


@app.route('/api/producers')
def producers():
    d = _db()
    lpvals = {r['name']: r['val'] for r in d.execute('SELECT name, val FROM lp_config', fetch=True)}
    out = []
    for r in d.execute('SELECT bp_name, bp_label, bp_seq, bp_active FROM bias_producer ORDER BY bp_seq', fetch=True):
        cfg = [{'key': k, 'value': lpvals.get(k)} for k in PRODUCER_LP.get(r['bp_name'], [])]
        out.append({'name': r['bp_name'], 'label': r['bp_label'], 'active': bool(r['bp_active']),
                    'config': cfg, 'summary': _summary(d, r['bp_name'])})
    d.disconnect()
    return jsonify(out)


@app.route('/api/notes', methods=['GET', 'POST'])
def notes():
    d = _db()
    if request.method == 'POST':
        txt = (request.json or {}).get('text', '')
        d.execute('''INSERT INTO ui_notes (note_pk, note_text, updated_at) VALUES (1, %s, %s)
                     ON DUPLICATE KEY UPDATE note_text=VALUES(note_text), updated_at=VALUES(updated_at)''',
                  (txt, dtm.datetime.utcnow()))
        d.disconnect(); return jsonify({'ok': True})
    r = d.execute('SELECT note_text FROM ui_notes WHERE note_pk=1', fetch=True)
    d.disconnect(); return jsonify({'text': (r[0]['note_text'] if r and r[0]['note_text'] else '')})


@app.route('/api/save', methods=['POST'])
def save():
    """Persist enabled flags + lp_config edits + notes, then re-run strat_review. Returns the row/module counts."""
    data = request.json or {}
    d = _db()
    for p in data.get('producers', []):
        d.execute('UPDATE bias_producer SET bp_active=%s WHERE bp_name=%s', (1 if p['active'] else 0, p['name']))
        for c in p.get('config', []):
            d.execute('UPDATE lp_config SET val=%s WHERE name=%s', (c['value'], c['key']))
    if 'notes' in data:
        d.execute('''INSERT INTO ui_notes (note_pk, note_text, updated_at) VALUES (1, %s, %s)
                     ON DUPLICATE KEY UPDATE note_text=VALUES(note_text), updated_at=VALUES(updated_at)''',
                  (data['notes'], dtm.datetime.utcnow()))
    rows, counts = build_strat_review(d, END_MS)
    d.disconnect()
    return jsonify({'ok': True, 'rows': len(rows), 'counts': counts})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
