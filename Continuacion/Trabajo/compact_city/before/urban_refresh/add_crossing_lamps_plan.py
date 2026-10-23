import json,math
from pathlib import Path
U=Path('urban_refresh');p=json.loads((U/'placement_plan.json').read_text());p['furniture']=[v for v in p['furniture'] if not v.get('crossing_lamp')]
for c in p['crossings']:
 a=math.radians(c['yaw']);t=(math.cos(a),math.sin(a));rr=(-t[1],t[0])
 for sign in [-1,1]:p['furniture'].append({'type':'Farola','position':[c['position'][0]-t[0]*sign*1400+rr[0]*sign*(c['halfwidth']-35),c['position'][1]-t[1]*sign*1400+rr[1]*sign*(c['halfwidth']-35),20],'yaw':c['yaw']+(180 if sign<0 else 0),'crossing_lamp':True})
(U/'placement_plan.json').write_text(json.dumps(p,indent=2))
