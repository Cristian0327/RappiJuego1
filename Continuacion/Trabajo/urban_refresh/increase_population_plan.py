import json,math,shutil,numpy as np
from pathlib import Path
W=Path('new_map_audit');U=Path('urban_refresh');p=json.loads((W/'integration_plan.json').read_text())
if not (U/'integration_plan_before_population.json').exists():shutil.copy2(W/'integration_plan.json',U/'integration_plan_before_population.json')
rows=[]
for ri,route in enumerate(p['walk_routes']):
 for si in [2,10,18,26]:
  at=np.array(route[si]);at[2]+=88;dv=np.array(route[(si+1)%32])-np.array(route[si]);rows.append({'route':ri,'next':(si+1)%32,'position':at.tolist(),'yaw':math.degrees(math.atan2(dv[1],dv[0])),'model':len(rows)%60})
p['pedestrians']=rows;(W/'integration_plan.json').write_text(json.dumps(p));print('CROWD_POPULATION',len(rows))
