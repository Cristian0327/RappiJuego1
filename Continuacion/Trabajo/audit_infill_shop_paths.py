import json,math
from pathlib import Path
W=Path('new_map_audit');p=json.loads((W/'integration_plan.json').read_text());added={v['copy'] for v in json.loads((W/'urban_infill_report.json').read_text())};bad=[]
for b in p['building_footprints']:
 if b[4] not in added:continue
 for i,s in enumerate(p['shops']):
  if any(b[0]-150<v[0]<b[2]+150 and b[1]-150<v[1]<b[3]+150 for v in s['walk_link']):bad.append([b[4],i])
print('ADDED_BUILDING_SHOP_PATH_CONFLICTS',bad)
