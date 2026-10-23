import json
from pathlib import Path
W=Path('new_map_audit');m=json.loads((W/'before_spacing_expansion/manifest.json').read_text());f=json.loads((W/'spacing_expansion_selected.json').read_text())['factor'];m['spacing_expansion']=f
for v in m['instances']:
 old=v['location'][:];v['location'][0]*=f;v['location'][1]*=f
 if v['source'].startswith('Relieve'):
  v['scale'][0]*=f;v['scale'][1]*=f
  for b in v.get('bounds',[]):b[0]*=f;b[1]*=f
 else:
  for b in v.get('bounds',[]):b[0]+=(f-1)*old[0];b[1]+=(f-1)*old[1]
for rd in m['roads']:
 for v in rd['center']:v[0]*=f;v[1]*=f
(W/'manifest.json').write_text(json.dumps(m));print('FINAL_EXPANSION',f)
