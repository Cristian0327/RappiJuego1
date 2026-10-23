import bpy,json,math
from pathlib import Path
from mathutils import Vector
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');m=json.loads((W/'manifest.json').read_text());road=m['roads'][0];terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));inv=terrain.matrix_world.inverted();direction=inv.to_3x3()@Vector((0,0,-1));out=[]
c=[Vector((p[0]*100,-p[1]*100,0)) for p in road['center']]
for i in range(25,len(c)-25,6):
 t=(c[i+1]-c[i-1]).normalized();right=Vector((-t.y,t.x,0));half=road['halfwidth'][i]*100
 for side in [-1,1]:
  for extra in [900,1200,1600,2000,2500,3000,4200]:
   p=c[i]+right*side*(half+extra);zs=[]
   for dx,dy in [(0,0),(-650,-650),(-650,650),(650,-650),(650,650)]:
    origin=Vector(((p.x+dx)/300+121.6244,-(p.y+dy)/300+55.6001,200));hit,co,n,j=terrain.ray_cast(inv@origin,direction);zs.append((terrain.matrix_world@co).z*300 if hit else 99999)
   if max(zs)<30 and min(zs)>-30:out.append({'center':list(p),'road_index':i,'side':side,'extra':extra,'ground_samples':zs})
(W/'flat_shop_candidates.json').write_text(json.dumps(out));print('FLAT_SHOP_CANDIDATES',len(out))
