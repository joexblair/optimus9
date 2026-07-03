"""UiServer — o9-live's bespoke view (SRP: read o9's own tables → serve the live terminal). Homed on o9-live.

GET /            → the terminal (polls the APIs every ~2s — all objects update in realtime).
GET /api/state   → equity · day PnL · exposure · live DD vs backtest · feed health · cascade state · sizing.
GET /api/history → last N closed trades (o9_ledger).
Reads o9_ledger / o9_account / o9_decision (o9's OWN, not the exchange's fx_*); price/tape from the live tape.
"""
from __future__ import annotations

import datetime as dtm
import os
import time

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

START_EQUITY = float(os.environ.get("O9_START_EQUITY", "500"))
DD_REF = float(os.environ.get("O9_DD_REF", "21.8"))            # backtest max drawdown reference
SIZING = {"mode": os.environ.get("O9_SIZE_MODE", "fixed"),
          "max_order": int(os.environ.get("O9_MAX_ORDER", "66000")),
          "split": int(os.environ.get("O9_SPLIT", "1"))}
app = FastAPI(title="o9-live")


def _db(name="o9_live"):
    cfg = get_db_config(); cfg["database"] = name
    d = DatabaseManager(**cfg); d.connect()
    return d


def _closed(o9):
    return o9.execute("SELECT side, entry_px, exit_px, gross, net, closed_ms FROM o9_ledger "
                      "WHERE status='closed' ORDER BY closed_ms", fetch=True)


@app.get("/api/history")
def history(limit: int = 100):
    o9 = _db(); rows = _closed(o9); o9.disconnect()
    bal, out = START_EQUITY, []
    for r in rows:
        net = float(r["net"]); bal += net
        out.append({"ms": int(r["closed_ms"]), "dir": r["side"],
                    "gross": round(float(r["gross"] or net), 2), "net": round(net, 2),
                    "entry": float(r["entry_px"]), "exit": float(r["exit_px"] or 0), "bal": round(bal, 2)})
    return {"trades": out[-limit:][::-1]}


@app.get("/api/state")
def state():
    o9 = _db(); dev = _db("pk_optimizer")                      # o9's own data + the live tape
    acct = o9.execute("SELECT equity FROM o9_account WHERE acct_id=1", fetch=True)
    rows = _closed(o9)
    pos = o9.execute("SELECT side, SUM(qty) q FROM o9_ledger WHERE status='open' GROUP BY side", fetch=True)
    dec = o9.execute("SELECT action, reason FROM o9_decision ORDER BY decision_id DESC LIMIT 1", fetch=True)
    k = dev.execute("SELECT kc_timestamp t, kc_close c FROM kline_collection ORDER BY kc_timestamp DESC LIMIT 1",
                    fetch=True)
    o9.disconnect(); dev.disconnect()

    equity = float(acct[0]["equity"]) if acct else START_EQUITY
    price = float(k[0]["c"]) if k else 0.0
    tape_age = round((int(time.time() * 1000) - int(k[0]["t"]) - 5000) / 1000.0, 1) if k else None
    bal, peak = START_EQUITY, START_EQUITY
    n = len(rows); wins = 0
    day0 = int(dtm.datetime.now(dtm.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
    day_pnl = 0.0
    for r in rows:
        net = float(r["net"]); bal += net; peak = max(peak, bal)
        if net > 0:
            wins += 1
        if int(r["closed_ms"]) >= day0:
            day_pnl += net
    dd = round((peak - equity) / peak * 100, 1) if peak > 0 else 0.0
    open_pos = {"side": pos[0]["side"], "size": float(pos[0]["q"])} if pos else None
    exposure = open_pos["size"] * price if open_pos else 0.0
    cascade = (dec[0]["action"] + ((" · " + dec[0]["reason"]) if dec[0]["reason"] else "")) if dec else "idle"
    return {"equity": round(equity, 2), "start": START_EQUITY, "net": round(equity - START_EQUITY, 2),
            "day_pnl": round(day_pnl, 2), "exposure": round(exposure, 0),
            "exposure_x": round(exposure / equity, 2) if equity else 0, "dd": dd, "dd_ref": DD_REF,
            "trades": n, "win": round(wins / n * 100, 1) if n else 0.0, "peak": round(peak, 2),
            "price": price, "tape_age": tape_age, "position": open_pos, "cascade": cascade, "sizing": SIZING}


@app.get("/", response_class=HTMLResponse)
def index():
    return _PAGE


_PAGE = r"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>o9-live</title><style>
:root{--bg:#0A0C12;--panel:#111623;--raise:#1A2233;--line:#28304400;--line:#2A3346;--ink:#EEF2F9;--dim:#AEB7CC;--faint:#7C8699;
--accent:#2FD6BE;--long:#33D17A;--short:#FF5D5D;--warn:#F5A623;--mono:ui-monospace,'JetBrains Mono',Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:13px system-ui,-apple-system,'Segoe UI',sans-serif;
background-image:radial-gradient(1100px 520px at 82% -10%,rgba(47,214,190,.07),transparent 60%)}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums}.pos{color:var(--long)}.neg{color:var(--short)}
.lbl{font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--dim)}
.wrap{max-width:1180px;margin:0 auto;padding:12px;display:flex;flex-direction:column;gap:10px;height:100vh}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:8px}
/* control sliver */
.sliver{display:flex;align-items:center;gap:14px;padding:9px 14px}
.brand{font-family:var(--mono);font-weight:600;font-size:15px}.brand b{color:var(--accent)}
.dot{width:8px;height:8px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 0 rgba(47,214,190,.6);animation:p 2s infinite}
@keyframes p{0%{box-shadow:0 0 0 0 rgba(47,214,190,.5)}70%{box-shadow:0 0 0 8px rgba(47,214,190,0)}100%{box-shadow:0 0 0 0 rgba(47,214,190,0)}}
.env{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;padding:3px 9px;border-radius:5px;background:rgba(245,166,35,.14);color:var(--warn);border:1px solid rgba(245,166,35,.4)}
.sizing{display:flex;align-items:center;gap:9px;margin-left:6px}
.seg{display:flex;background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:2px}
.seg span{font-size:11.5px;color:var(--dim);padding:5px 11px;border-radius:4px}
.seg span.on{background:var(--accent);color:#04120f;font-weight:600}
.chip2{font-family:var(--mono);font-size:11.5px;color:var(--dim);border:1px solid var(--line);border-radius:5px;padding:4px 9px}
.chip2 b{color:var(--ink)}
.spacer{flex:1}.kill{font:700 12px system-ui;letter-spacing:.05em;color:#fff;background:linear-gradient(180deg,#ff6b5f,#e33b30);border:1px solid #ff8a80;border-radius:6px;padding:7px 15px;cursor:pointer;box-shadow:0 0 16px rgba(255,60,48,.22)}
.px{font-family:var(--mono);font-size:14px;font-weight:600;margin-left:4px}
/* status strip */
.status{display:flex;align-items:stretch;overflow-x:auto}
.stat{display:flex;flex-direction:column;gap:3px;padding:10px 16px;border-right:1px solid var(--line);justify-content:center;white-space:nowrap}
.stat .v{font-family:var(--mono);font-size:15px;font-weight:600}
.feed{display:flex;gap:13px}.feed i{font-style:normal;display:flex;align-items:center;gap:5px;font-family:var(--mono);font-size:11.5px;color:var(--dim)}
.fdot{width:6px;height:6px;border-radius:50%;background:var(--long)}.fdot.warn{background:var(--warn)}.fdot.bad{background:var(--short)}
.casc{margin-left:auto;border-right:0;align-items:flex-end}
.chip{font-family:var(--mono);font-size:11.5px;padding:4px 10px;border-radius:5px;letter-spacing:.02em;background:rgba(47,214,190,.14);color:var(--accent);border:1px solid rgba(47,214,190,.34)}
.ddbar{width:130px;height:5px;border-radius:3px;background:var(--bg);overflow:hidden;margin-top:3px}.ddbar i{display:block;height:100%;background:linear-gradient(90deg,var(--long),var(--warn));border-radius:3px}
/* chart */
.chart{height:120px;position:relative;padding:10px}canvas{position:absolute;inset:10px;width:calc(100% - 20px);height:calc(100% - 20px)}
/* history */
.hist{flex:1;display:flex;flex-direction:column;min-height:0}
.hh{display:flex;gap:10px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--line)}.hh h2{margin:0;font-size:13px;color:var(--ink)}.hh .c{font-family:var(--mono);font-size:11.5px;color:var(--dim)}
.scroll{overflow:auto;flex:1}table{width:100%;min-width:640px;border-collapse:collapse;font-family:var(--mono);font-size:12px}
th{position:sticky;top:0;background:var(--panel);font:600 10.5px system-ui;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);text-align:right;padding:8px 16px;border-bottom:1px solid var(--line-2,#2A3346)}
th.l{text-align:left}td{padding:8px 16px;text-align:right;border-bottom:1px solid rgba(42,51,70,.5);white-space:nowrap;color:var(--ink)}td.l{text-align:left}
tr:hover{background:rgba(47,214,190,.05)}.side{font-weight:600;font-size:11px;padding:2px 7px;border-radius:4px}.side.s{color:var(--short);background:rgba(255,93,93,.12)}.side.b{color:var(--long);background:rgba(51,209,122,.12)}
.empty{padding:26px 16px;text-align:center;color:var(--dim);font-family:var(--mono);font-size:12px}
</style></head><body><div class=wrap>
<header class="sliver panel">
  <span class=dot></span><span class=brand>o9<b>&middot;</b>live</span><span class=env>FAKE-API &middot; realtime</span>
  <span class="px num" id=px>&mdash;</span>
  <div class=sizing><span class=lbl>size</span>
    <div class=seg id=seg><span data-m=smallest>Smallest</span><span data-m=fixed>Fixed</span><span data-m=dynamic5x>Dynamic 5&times;</span></div>
    <span class=chip2>max <b id=maxo>&mdash;</b></span><span class=chip2>split <b id=split>&mdash;</b></span></div>
  <div class=spacer></div><button class=kill>&#9632; FLATTEN &amp; HALT</button>
</header>
<div class="status panel">
  <div class=stat><span class=lbl>equity</span><span class="v num" id=eq>&mdash;</span></div>
  <div class=stat><span class=lbl>day pnl</span><span class="v num" id=day>&mdash;</span></div>
  <div class=stat><span class=lbl>exposure</span><span class="v num" id=exp>&mdash;</span></div>
  <div class=stat><span class=lbl>live drawdown vs backtest</span><span class="num" id=dd style=font-size:12px>&mdash;</span><span class=ddbar><i id=ddb style=width:0></i></span></div>
  <div class=stat><span class=lbl>feed health</span><div class=feed id=feed></div></div>
  <div class="stat casc"><span class=lbl>cascade state</span><span class=chip id=casc>&mdash;</span></div>
</div>
<div class="chart panel"><canvas id=eqc></canvas></div>
<div class="hist panel"><div class=hh><h2>Trade history</h2><span class=c id=hc>&mdash;</span></div>
  <div class=scroll><table><thead><tr><th class=l>Closed</th><th>Dir</th><th>Gross</th><th>Net</th><th>Entry</th><th>Exit</th><th>Balance</th></tr></thead><tbody id=tb></tbody></table>
  <div class=empty id=empty>waiting for the first realtime signal&hellip;</div></div>
</div></div><script>
function money(v){return (v<0?'-$':'+$')+Math.abs(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g,',')}
function commas(v){return Math.round(v).toLocaleString()}
function hhmm(ms){return new Date(ms).toISOString().slice(5,19).replace('T',' ')}
function fdot(age,warn,bad){return age==null?'bad':(age>bad?'bad':age>warn?'warn':'')}
function draw(bal){var cv=document.getElementById('eqc'),ctx=cv.getContext('2d'),w=cv.width=cv.clientWidth,h=cv.height=cv.clientHeight;
 if(bal.length<2){return} var lo=Math.min.apply(0,bal),hi=Math.max.apply(0,bal),X=i=>i/(bal.length-1)*w,Y=v=>h-(v-lo)/(hi-lo||1)*h;
 var g=ctx.createLinearGradient(0,0,0,h);g.addColorStop(0,'rgba(47,214,190,.25)');g.addColorStop(1,'rgba(47,214,190,0)');
 ctx.beginPath();ctx.moveTo(0,Y(bal[0]));bal.forEach((v,i)=>ctx.lineTo(X(i),Y(v)));ctx.lineTo(w,h);ctx.lineTo(0,h);ctx.fillStyle=g;ctx.fill();
 ctx.beginPath();ctx.moveTo(0,Y(bal[0]));bal.forEach((v,i)=>ctx.lineTo(X(i),Y(v)));ctx.strokeStyle='#2FD6BE';ctx.lineWidth=1.7;ctx.stroke();}
function tick(){Promise.all([fetch('/api/state').then(r=>r.json()),fetch('/api/history').then(r=>r.json())]).then(function(x){
 var s=x[0],h=x[1].trades;
 document.getElementById('px').textContent=s.price?s.price.toFixed(5):'—';
 document.getElementById('eq').textContent='$'+commas(s.equity);document.getElementById('eq').className='v num pos';
 var d=document.getElementById('day');d.textContent=money(s.day_pnl);d.className='v num '+(s.day_pnl>=0?'pos':'neg');
 document.getElementById('exp').textContent=s.exposure?('$'+commas(s.exposure)+' · '+s.exposure_x+'×'):'flat';
 document.getElementById('dd').innerHTML=s.dd+'% <span style=color:#7C8699>/ '+s.dd_ref+'%</span>';
 document.getElementById('ddb').style.width=Math.min(100,s.dd/s.dd_ref*100)+'%';
 document.getElementById('casc').textContent=s.cascade;
 document.getElementById('maxo').textContent=commas(s.sizing.max_order);document.getElementById('split').textContent=s.sizing.split;
 document.querySelectorAll('#seg span').forEach(e=>e.className=(e.dataset.m===s.sizing.mode?'on':''));
 document.getElementById('feed').innerHTML='<i><span class="fdot '+fdot(s.tape_age,6,12)+'"></span>publicTrade '+(s.tape_age==null?'—':s.tape_age+'s')+'</i>'
   +'<i><span class="fdot"></span>orderbook live</i>';
 document.getElementById('hc').textContent=s.trades+' closed · '+s.win+'% win · start $'+s.start;
 var emp=document.getElementById('empty');emp.style.display=h.length?'none':'block';
 document.getElementById('tb').innerHTML=h.map(function(t){var cl=t.net>=0?'pos':'neg',sd=t.dir=='Sell'?'s':'b',nm=t.dir=='Sell'?'SHORT':'LONG';
  return '<tr><td class=l>'+hhmm(t.ms)+'</td><td class=l><span class="side '+sd+'">'+nm+'</span></td>'+
   '<td class="'+(t.gross>=0?'pos':'neg')+'">'+money(t.gross)+'</td><td class="'+cl+'">'+money(t.net)+'</td>'+
   '<td>'+t.entry.toFixed(5)+'</td><td>'+t.exit.toFixed(5)+'</td><td>$'+commas(t.bal)+'</td></tr>';}).join('');
 draw(h.map(t=>t.bal).reverse());
})}
tick();setInterval(tick,2000);
</script></body></html>"""
