import json,collections,numpy as np
from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');m=json.loads((r/'outputs/BogotaUrban/manifest.json').read_text());groups=collections.defaultdict(list)
for v in m['instances']:
 if v['mesh'].startswith('SM_Mapa_Road') or 'Relieve' in v['source']:continue
 groups[v['mesh']].append((round(v['location'][2],3),tuple(np.round(v['scale'],5)),tuple(np.round(v['rotation'][:2],3))))
for name,rows in groups.items():
 if len(set(rows))>1:print(name,len(rows),len(set(rows)),rows[:3])
print('meshes',len(groups),'ranges',sorted(set(a[0] for rows in groups.values() for a in rows))[:25])
