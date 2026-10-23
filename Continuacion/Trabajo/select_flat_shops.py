import json,math,numpy as np
from pathlib import Path
W=Path('new_map_audit');p=json.loads((W/'integration_plan.json').read_text());raw=json.loads((W/'flat_shop_candidates.json').read_text());b=p['building_footprints'];good=[]
for s in raw:
 x,y,_=s['center']
 if any(x+750>v[0] and x-750<v[2] and y+750>v[1] and y-750<v[3] for v in b):continue
 good.append(s)
sel=[]
for i in range(120):
 if not good:break
 key=lambda s:min([math.dist(s['center'][:2],v['center'][:2]) for v in sel],default=100000-math.dist(s['center'][:2],[0,0]))
 s=max(good,key=key);good.remove(s)
 if sel and key(s)<1000:break
 sel.append(s)
p['shops']=sel;(W/'integration_plan.json').write_text(json.dumps(p));print('FLAT_CLEAR_SHOPS',len(sel))

