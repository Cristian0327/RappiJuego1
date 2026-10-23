import json,math
from pathlib import Path
W=Path('new_map_audit');m=json.loads((W/'manifest.json').read_text());b=json.loads((W/'before_spacing_expansion/manifest.json').read_text());now={v['source']:v for v in m['instances']};fail=[]
for v in b['instances']:
 if v['source'].startswith('SM_Mapa_Road') or v['source'].startswith('Relieve'):continue
 n=now[v['source']]
 if max(abs(n['location'][i]-v['location'][i]*1.72) for i in [0,1])>1e-4 or n['scale']!=v['scale'] or n['rotation']!=v['rotation']:fail.append(v['source'])
print('ORIGINAL_BUILDINGS_TRANSFORM_MISMATCHES',len(fail));assert not fail
