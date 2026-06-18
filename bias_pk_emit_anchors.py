"""bias_pk_emit_anchors.py — emit one anchor + 22 prior:22 future anchors, to eyeball firing rate.
Anchors = right-side s6m reversals (the consumable peaks). Picks a lookahead example (floater lands
after the anchor). Labels: side + s6r value; example highlighted; its floater bar marked + a line."""
import sys; sys.path.insert(0,'/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import logging
for n in ('DatabaseManager',): logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm
H=bm.H
def dd(t): return dtm.datetime.fromtimestamp(t/1000,timezone.utc).strftime('%m%d')
def dts(t): return dtm.datetime.fromtimestamp(t/1000,timezone.utc).strftime('%Y-%m-%d %H:%M')
db=DatabaseManager(**get_db_config()); db.connect()
det=BLDetect(db,lookback_hours=168,warmup_hours=80); tp=det._tp
rng=db.execute(f'SELECT MIN(kc_timestamp) mn,MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}',fetch=True)[0]
earliest,latest=int(rng['mn']),int(rng['mx'])
ends=[]; e=latest
while e-(168+80)*H>=earliest: ends.append(e); e-=120*H
ends.reverse()
tgt=int(dtm.datetime(2026,6,7,1,24,tzinfo=timezone.utc).timestamp()*1000)
W=bm.BiasWindow(db,min(ends,key=lambda x:abs(x-tgt))); db.disconnect()
bclose=W.base['close'].to_numpy()
# anchors = right-side reversals (the floater-chain peaks), in time order
anchors=[]
for Wt in W.trigs(6):
    S=Wt['s']; v=Wt['s6r']
    if (S==1 and v>50) or (S==-1 and v<50):
        anchors.append(dict(t=Wt['t'], j=Wt['j'], s=S, v=round(float(v),1)))
# example = a lookahead pk (flt_bar > anc_bar), find via ups()
ups=W.ups(W.trigs(6),'oob')
ex=next((u for u in ups if u['flt_bar']>u['anc_bar']), ups[len(ups)//2])
ei=next(i for i,a in enumerate(anchors) if a['j']==ex['anc_bar'])
sl=anchors[max(0,ei-22):ei+23]
print(f"window {dts(W.W0)}→{dts(W.W1)}")
print(f"example anchor @ {dts(ex['t'])} side={'HI' if ex['side']==1 else 'LO'}  anc={ex['anc']} flt={ex['flt']}  flt_bar {'AFTER' if ex['flt_bar']>ex['anc_bar'] else 'before'} anchor (gap {(ex['anc_bar']-ex['flt_bar'])*5/60:.0f}m)")
print(f"showing {len(sl)} anchors: {dts(sl[0]['t'])} → {dts(sl[-1]['t'])}  (span {(sl[-1]['t']-sl[0]['t'])/3600000:.1f}h)")
arr=lambda v:'array.from('+', '.join(v)+')'
t=[str(a['t']) for a in sl]; px=[f"{float(bclose[a['j']]):.5f}" for a in sl]
sd=['"'+('HI' if a['s']==1 else 'LO')+'"' for a in sl]; vv=[f"{a['v']:.1f}" for a in sl]
isex=['true' if a['j']==ex['anc_bar'] else 'false' for a in sl]
fpx=f"{float(bclose[ex['flt_bar']]):.5f}"; ft=str(int(W.ts[ex['flt_bar']]))
body=f'''//@version=5
indicator("anchors 22:22 around example", overlay=true, max_labels_count=200, max_lines_count=10)
t={arr(t)}
px={arr(px)}
sd={arr(sd)}
vv={arr(vv)}
ex={arr(isex)}
var bool done=false
if barstate.islast and not done
    done:=true
    for i=0 to array.size(t)-1
        bool e=array.get(ex,i)
        col= e? color.new(color.yellow,0): (array.get(sd,i)=="HI"? color.new(color.red,40): color.new(color.teal,40))
        label.new(array.get(t,i), array.get(px,i), array.get(sd,i)+" "+str.tostring(array.get(vv,i),"#.0"), xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_down, color=col, textcolor=(e?color.black:color.white), size=(e?size.normal:size.small))
    // example floater (note: lands AFTER the anchor here = lookahead)
    label.new({ft}, {fpx}, "FLOATER", xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_up, color=color.new(color.orange,0), textcolor=color.black, size=size.small)
    line.new({str(ex['t'])}, {float(bclose[ex['anc_bar']]):.5f}, {ft}, {fpx}, xloc=xloc.bar_time, color=color.orange, width=2, style=line.style_dashed)
'''
open('/home/joe/thecodes/bias_pk_anchors.pine','w').write(body)
print("→ /home/joe/thecodes/bias_pk_anchors.pine")
