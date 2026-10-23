import bpy,json,numpy as np,collections
from pathlib import Path
R=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho');root=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');m=json.loads((root/'outputs/BogotaUrban/manifest.json').read_text());out=[];seen=set()
for v in m['instances']:
 if v['mesh'] in seen or not v['mesh'].startswith('SM_Mapa_') or v['mesh'].startswith('SM_Mapa_Road') or 'Relieve' in v['source']:continue
 seen.add(v['mesh']);o=bpy.data.objects.get(v['source'])
 if not o:continue
 mw=np.array(o.matrix_world);co=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',co);co=co.reshape(-1,3)@mw[:3,:3].T+mw[:3,3];areas=collections.defaultdict(float)
 for p in o.data.polygons:
  ids=list(p.vertices);verts=co[ids]
  if np.ptp(verts[:,2])<.001 and -.1<verts[0,2]<1.6:areas[round(float(verts[0,2]),3)]+=p.area*abs(mw[0,0]*mw[1,1]-mw[0,1]*mw[1,0])
 out.append(dict(mesh=v['mesh'],source=v['source'],levels=sorted(areas.items(),key=lambda x:-x[1])[:7]))
(R/'urban_safety/base_levels.json').write_text(json.dumps(out,indent=2,default=float));print('ARCHITECTURE_BASE_LEVELS_READY',len(out))

