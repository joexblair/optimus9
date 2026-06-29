"""
ui/app.py — the strat_review settings UI (Joe 0627). The "Strategy" page.

Left 75%: a grid of bias_producer modules (enable + a +/- unfold of producer-specific config) + a foldable
"Line configs (ic)" editor (value_mode · wobble · params per line). Right 25%: a persistent notes pane.
"Save & update" writes every edit then re-runs strat_review.

Data-driven, all DB-resident:
  bias_producer  — the module registry (enable flags)
  cascade detail — lp_cascade_rearm_ic (the re-arm/wob line, a dropdown)
  bl_state detail— bl_lines (enable + support-line dropdown, active-on-top)
  bro detail     — lp_bro_wob
  ic mods        — indicator_configs (ic_src/bb/k params · ic_ivm_pk value_mode · ic_wobble), ordered
                   by is_prefix, itf_label, il_suffix. EDIT-in-place (no new il/is/itf/ic rows — that's a
                   future Line-config page).

Run:  ui/venv/bin/python ui/app.py   → http://127.0.0.1:5000
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
from decimal import Decimal
from flask import Flask, render_template, request, jsonify
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from strat_review import build_strat_review

app = Flask(__name__)
END_MS = int(dtm.datetime(2026, 6, 22, tzinfo=timezone.utc).timestamp() * 1000)   # TODO: UI date control

_NAME = ("CONCAT(s.is_prefix, itf.itf_label, il.il_suffix)")
_JOIN = ("JOIN indicator_series s ON s.is_pk = ic.ic_is_pk "
         "JOIN indicator_lines il ON il.il_pk = ic.ic_il_pk "
         "JOIN indicator_timeframes itf ON itf.itf_pk = ic.ic_itf_pk")
_LIVE = "WHERE ic.ic_pk IN (SELECT ic_pk FROM vw_indicator_configs_live)"   # one row per line — the live version only
_ORDER = "ORDER BY s.is_prefix, itf.itf_label, il.il_suffix"


def _db():
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute('CREATE TABLE IF NOT EXISTS ui_notes (note_pk INT PRIMARY KEY, note_text TEXT, updated_at DATETIME)')
    return d


def _clean(r):
    return {k: (float(v) if isinstance(v, Decimal) else v) for k, v in r.items()}


def _lines(d):
    return [_clean(r) for r in d.execute(f'SELECT ic.ic_pk, {_NAME} nm FROM indicator_configs ic {_JOIN} {_LIVE} {_ORDER}', fetch=True)]


def _detail(d, name, lines):
    if name == 'cascade':
        # the lr (latch-release) cascade: DB-driven gate-sets (lr_gate) + knobs (lp_lr_*). Retires trade_gate.
        knobs = d.execute("SELECT name, val, note FROM lp_config WHERE name LIKE 'lp_lr_%' OR name='lp_s30r_lb' ORDER BY name", fetch=True)
        grows = d.execute("SELECT lrg_pk, lrg_role, lrg_name, lrg_op, lrg_active FROM lr_gate "
                          "ORDER BY FIELD(lrg_role,'arm','finisher','bias'), lrg_name", fetch=True)
        gates = [{'lrg_pk': g['lrg_pk'], 'role': g['lrg_role'], 'name': g['lrg_name'], 'op': g['lrg_op'],
                  'active': bool(g['lrg_active']),
                  'lines': [{'nm': r['nm'], 'check': r['ch']} for r in d.execute(
                      "SELECT i.ind_name nm, lgl.lrgl_check ch FROM lr_gate_line lgl "
                      "JOIN vw_indicator_configs_live i ON i.ic_pk = lgl.lrgl_ic_pk WHERE lgl.lrgl_lrg_pk = %s",
                      (g['lrg_pk'],), fetch=True)]} for g in grows]
        return {'kind': 'cascade', 'knobs': [dict(k) for k in knobs], 'gates': gates}
    if name == 'bl_state':
        bls = d.execute(f'''SELECT bl.bl_pk, {_NAME} nm, bl.bl_is_active, bl.bl_role, bl.bl_support_ic_pk
                            FROM bl_lines bl JOIN indicator_configs ic ON ic.ic_pk = bl.bl_ic_pk {_JOIN}
                            ORDER BY bl.bl_is_active DESC, s.is_prefix, itf.itf_label, il.il_suffix''', fetch=True)
        return {'kind': 'bl_state', 'lines': lines, 'bl_lines': [
            {'bl_pk': r['bl_pk'], 'nm': r['nm'], 'active': bool(r['bl_is_active']),
             'role': r['bl_role'], 'support_ic': r['bl_support_ic_pk']} for r in bls]}
    if name == 'bro_cross':
        v = d.execute("SELECT val FROM lp_config WHERE name='lp_bro_wob'", fetch=True)
        return {'kind': 'lp', 'lp': [{'key': 'lp_bro_wob', 'value': v[0]['val'] if v else None}],
                'summary': 'sets: hbhl16 · hblo16 · hbhi16 (in code — #35)'}
    return {'kind': 'none', 'summary': 'config in code (no DB knobs yet — #35 no-hardcode sweep)'}


@app.route('/')
def index():
    return render_template('strategy.html')


@app.route('/api/producers')
def producers():
    d = _db(); lines = _lines(d)
    out = [{'name': r['bp_name'], 'label': r['bp_label'], 'active': bool(r['bp_active']),
            'detail': _detail(d, r['bp_name'], lines)}
           for r in d.execute('SELECT bp_name, bp_label, bp_seq, bp_active FROM bias_producer ORDER BY bp_seq', fetch=True)]
    d.disconnect()
    return jsonify(out)


@app.route('/api/ic_mods')
def ic_mods():
    d = _db()
    rows = d.execute(f'''SELECT ic.ic_pk, {_NAME} nm, ic.ic_line_type, ic.ic_src, ic.ic_bb_len, ic.ic_bb_mult,
                         ic.ic_k_len, ic.ic_rsi_len, ic.ic_stc_len, ic.ic_ivm_pk, ic.ic_wobble
                         FROM indicator_configs ic {_JOIN} {_LIVE} {_ORDER}''', fetch=True)
    modes = [_clean(m) for m in d.execute('SELECT ivm_pk, ivm_label FROM indicator_value_modes ORDER BY ivm_pk', fetch=True)]
    d.disconnect()
    return jsonify({'rows': [_clean(r) for r in rows], 'modes': modes})


@app.route('/api/notes', methods=['GET', 'POST'])
def notes():
    d = _db()
    if request.method == 'POST':
        d.execute('''INSERT INTO ui_notes (note_pk, note_text, updated_at) VALUES (1, %s, %s)
                     ON DUPLICATE KEY UPDATE note_text=VALUES(note_text), updated_at=VALUES(updated_at)''',
                  ((request.json or {}).get('text', ''), dtm.datetime.utcnow()))
        d.disconnect(); return jsonify({'ok': True})
    r = d.execute('SELECT note_text FROM ui_notes WHERE note_pk=1', fetch=True)
    d.disconnect(); return jsonify({'text': (r[0]['note_text'] if r and r[0]['note_text'] else '')})


def _nz(v):
    return None if v in ('', None) else v


@app.route('/api/save', methods=['POST'])
def save():
    """Persist every edit (producer flags + cascade re-arm + bl_lines + lp knobs + ic mods + notes), re-run strat_review."""
    data = request.json or {}
    d = _db()
    for p in data.get('producers', []):
        d.execute('UPDATE bias_producer SET bp_active=%s WHERE bp_name=%s', (1 if p['active'] else 0, p['name']))
        det = p.get('detail', {})
        if det.get('kind') == 'cascade':
            for k in det.get('knobs', []):
                d.execute("UPDATE lp_config SET val=%s WHERE name=%s", (k['val'], k['name']))
            for g in det.get('gates', []):
                d.execute("UPDATE lr_gate SET lrg_active=%s, lrg_op=%s WHERE lrg_pk=%s",
                          (1 if g['active'] else 0, g['op'], g['lrg_pk']))
        elif det.get('kind') == 'bl_state':
            for bl in det.get('bl_lines', []):
                d.execute('UPDATE bl_lines SET bl_is_active=%s, bl_support_ic_pk=%s WHERE bl_pk=%s',
                          (1 if bl['active'] else 0, _nz(bl['support_ic']), bl['bl_pk']))
        elif det.get('kind') == 'lp':
            for c in det.get('lp', []):
                d.execute('UPDATE lp_config SET val=%s WHERE name=%s', (c['value'], c['key']))
    for ic in data.get('ic_mods', []):
        # stamp live_after = YESTERDAY (Joe 0627): immediately live, never future-dated → no calendar-drift
        # (the view picks MAX live_after <= NOW()). Edit-in-place; no version history kept.
        d.execute('''UPDATE indicator_configs SET ic_src=%s, ic_bb_len=%s, ic_bb_mult=%s, ic_k_len=%s,
                     ic_rsi_len=%s, ic_stc_len=%s, ic_ivm_pk=%s, ic_wobble=%s,
                     ic_live_after_dt=(CURDATE() - INTERVAL 1 DAY) WHERE ic_pk=%s''',
                  (_nz(ic['ic_src']), _nz(ic['ic_bb_len']), _nz(ic['ic_bb_mult']), _nz(ic['ic_k_len']),
                   _nz(ic['ic_rsi_len']), _nz(ic['ic_stc_len']), ic['ic_ivm_pk'], _nz(ic['ic_wobble']), ic['ic_pk']))
    if 'notes' in data:
        d.execute('''INSERT INTO ui_notes (note_pk, note_text, updated_at) VALUES (1, %s, %s)
                     ON DUPLICATE KEY UPDATE note_text=VALUES(note_text), updated_at=VALUES(updated_at)''',
                  (data['notes'], dtm.datetime.utcnow()))
    rows, counts = build_strat_review(d, END_MS)
    d.disconnect()
    return jsonify({'ok': True, 'rows': len(rows), 'counts': counts})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
