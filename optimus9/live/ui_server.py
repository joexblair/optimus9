"""UiServer — o9-live's bespoke view (SRP: read fx_* → serve the terminal). Homed on o9-live.

GET /              → the terminal page (fetches the APIs).
GET /api/state     → equity, net, trades, win%.
GET /api/history   → last N closed trades (dir, gross/net PnL, entry/exit, slippage, balance).
Read-only; the trades come from the fake-exchange (replay now, live collector later). PK_DB_NAME=o9_live.
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

START_EQUITY = float(os.environ.get("O9_START_EQUITY", "500"))
app = FastAPI(title="o9-live")


def _db():
    cfg = get_db_config()
    cfg["database"] = os.environ.get("PK_DB_NAME", "o9_live")
    d = DatabaseManager(**cfg); d.connect()
    return d


def _trades(limit=100):
    d = _db()
    rows = d.execute("""
        SELECT p.position_id, p.side, p.avg_entry, p.realized_pnl, p.total_fees, p.opened_ms, p.closed_ms,
          (SELECT f.exec_price FROM fx_fill f WHERE f.position_id=p.position_id AND f.closed_size>0
             ORDER BY f.exec_ms DESC LIMIT 1) exit_px,
          (SELECT AVG(f.slippage_bps) FROM fx_fill f WHERE f.position_id=p.position_id) slip
        FROM fx_position p WHERE p.status='closed' ORDER BY p.closed_ms""", fetch=True)
    d.disconnect()
    bal, out = START_EQUITY, []
    for r in rows:                                   # ascending → running balance
        net = float(r["realized_pnl"]); bal += net
        out.append({
            "ms": int(r["closed_ms"]), "dir": r["side"],
            "gross": round(net + float(r["total_fees"] or 0), 2), "net": round(net, 2),
            "entry": float(r["avg_entry"]), "exit": float(r["exit_px"] or 0),
            "slip": round(float(r["slip"] or 0), 2), "bal": round(bal, 2)})
    return out[-limit:][::-1], bal                    # newest first


@app.get("/api/history")
def history():
    trades, _ = _trades()
    return {"trades": trades}


@app.get("/api/state")
def state():
    trades, bal = _trades(limit=10_000)
    wins = sum(1 for t in trades if t["net"] > 0)
    n = len(trades)
    return {"equity": round(bal, 2), "start": START_EQUITY, "net": round(bal - START_EQUITY, 2),
            "trades": n, "win": round(wins / n * 100, 1) if n else 0.0,
            "peak": round(max([START_EQUITY] + [t["bal"] for t in trades]), 2)}


@app.get("/", response_class=HTMLResponse)
def index():
    return _PAGE


_PAGE = """<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>o9-live</title><style>
:root{--bg:#0A0C12;--panel:#111623;--line:#222A3C;--ink:#E7EBF3;--dim:#8B94A8;--faint:#586074;--accent:#2FD6BE;--long:#33D17A;--short:#FF5D5D;--mono:ui-monospace,'JetBrains Mono',Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:13px system-ui,-apple-system,'Segoe UI',sans-serif;background-image:radial-gradient(1000px 500px at 80% -10%,rgba(47,214,190,.06),transparent 60%)}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums}.pos{color:var(--long)}.neg{color:var(--short)}
.lbl{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--faint)}
.wrap{max-width:1100px;margin:0 auto;padding:16px;display:flex;flex-direction:column;gap:12px;height:100vh}
.bar{display:flex;align-items:center;gap:18px;padding:12px 16px;background:var(--panel);border:1px solid var(--line);border-radius:8px}
.brand{font-family:var(--mono);font-weight:600;font-size:15px}.brand b{color:var(--accent)}
.dot{width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 8px var(--accent)}
.env{font-family:var(--mono);font-size:10px;letter-spacing:.1em;padding:3px 8px;border-radius:5px;background:rgba(245,166,35,.12);color:#F5A623;border:1px solid rgba(245,166,35,.35)}
.kpi{display:flex;flex-direction:column;gap:3px}.kpi .v{font-family:var(--mono);font-size:17px;font-weight:600}
.spacer{flex:1}
.chart{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;height:150px;position:relative}
canvas{position:absolute;inset:12px;width:calc(100% - 24px);height:calc(100% - 24px)}
.hist{background:var(--panel);border:1px solid var(--line);border-radius:8px;flex:1;display:flex;flex-direction:column;min-height:0}
.hh{display:flex;gap:10px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--line)}.hh h2{margin:0;font-size:12px}.hh .c{font-family:var(--mono);font-size:11px;color:var(--faint)}
.scroll{overflow:auto;flex:1}table{width:100%;min-width:640px;border-collapse:collapse;font-family:var(--mono);font-size:12px}
th{position:sticky;top:0;background:var(--panel);font:500 10px system-ui;letter-spacing:.09em;text-transform:uppercase;color:var(--faint);text-align:right;padding:7px 16px;border-bottom:1px solid var(--line)}
th.l{text-align:left}td{padding:8px 16px;text-align:right;border-bottom:1px solid rgba(34,42,60,.5);white-space:nowrap}td.l{text-align:left}
tr:hover{background:rgba(47,214,190,.04)}.side{font-weight:600;font-size:11px;padding:2px 7px;border-radius:4px}.side.s{color:var(--short);background:rgba(255,93,93,.11)}.side.b{color:var(--long);background:rgba(51,209,122,.11)}
</style></head><body><div class=wrap>
<div class=bar><span class=dot></span><span class=brand>o9<b>&middot;</b>live</span><span class=env id=env>FAKE-API &middot; replay</span>
<div class=spacer></div>
<div class=kpi><span class=lbl>equity</span><span class="v num" id=eq>&mdash;</span></div>
<div class=kpi><span class=lbl>net</span><span class="v num" id=net>&mdash;</span></div>
<div class=kpi><span class=lbl>trades</span><span class="v num" id=tr>&mdash;</span></div>
<div class=kpi><span class=lbl>win</span><span class="v num" id=win>&mdash;</span></div></div>
<div class=chart><canvas id=eqc></canvas></div>
<div class=hist><div class=hh><h2>Trade history</h2><span class=c id=hc>&mdash;</span></div>
<div class=scroll><table><thead><tr><th class=l>Closed</th><th>Dir</th><th>Gross</th><th>Net</th><th>Entry</th><th>Exit</th><th>Slip</th><th>Balance</th></tr></thead><tbody id=tb></tbody></table></div></div>
</div><script>
function money(v){return (v<0?'-$':'+$')+Math.abs(v).toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g,',')}
function hhmm(ms){var d=new Date(ms);return d.toISOString().slice(5,19).replace('T',' ')}
Promise.all([fetch('/api/state').then(r=>r.json()),fetch('/api/history').then(r=>r.json())]).then(function(x){
 var s=x[0],h=x[1].trades;
 eq.textContent='$'+s.equity.toLocaleString();eq.className='v num pos';
 net.textContent=money(s.net);net.className='v num '+(s.net>=0?'pos':'neg');
 tr.textContent=s.trades;win.textContent=s.win+'%';hc.textContent=s.trades+' closed &middot; '+s.win+'% win &middot; start $'+s.start;
 tb.innerHTML=h.map(function(t){var cl=t.net>=0?'pos':'neg',sd=t.dir=='Sell'?'s':'b',nm=t.dir=='Sell'?'SHORT':'LONG';
  return '<tr><td class=l>'+hhmm(t.ms)+'</td><td class=l><span class=\"side '+sd+'\">'+nm+'</span></td>'+
   '<td class=\"'+(t.gross>=0?'pos':'neg')+'\">'+money(t.gross)+'</td><td class=\"'+cl+'\">'+money(t.net)+'</td>'+
   '<td>'+t.entry.toFixed(5)+'</td><td>'+t.exit.toFixed(5)+'</td><td>'+t.slip.toFixed(2)+'</td>'+
   '<td>$'+t.bal.toFixed(0).replace(/\\B(?=(\\d{3})+(?!\\d))/g,',')+'</td></tr>';}).join('');
 // equity curve (balances are newest-first → reverse for time order)
 var bal=h.map(t=>t.bal).reverse(),cv=eqc,ctx=cv.getContext('2d'),w=cv.width=cv.clientWidth,ht=cv.height=cv.clientHeight;
 if(bal.length){var lo=Math.min.apply(0,bal),hi=Math.max.apply(0,bal),X=i=>i/(bal.length-1)*w,Y=v=>ht-(v-lo)/(hi-lo||1)*ht;
  var g=ctx.createLinearGradient(0,0,0,ht);g.addColorStop(0,'rgba(47,214,190,.25)');g.addColorStop(1,'rgba(47,214,190,0)');
  ctx.beginPath();ctx.moveTo(0,Y(bal[0]));bal.forEach((v,i)=>ctx.lineTo(X(i),Y(v)));ctx.lineTo(w,ht);ctx.lineTo(0,ht);ctx.fillStyle=g;ctx.fill();
  ctx.beginPath();ctx.moveTo(0,Y(bal[0]));bal.forEach((v,i)=>ctx.lineTo(X(i),Y(v)));ctx.strokeStyle='#2FD6BE';ctx.lineWidth=1.6;ctx.stroke();}
});
</script></body></html>"""
