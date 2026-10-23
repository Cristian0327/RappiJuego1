import bpy,json,numpy as np,copy,math
from pathlib import Path
from mathutils import Vector
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');m=json.loads((W/'manifest.json').read_text());p=json.loads((W/'integration_plan.json').read_text());boxes=np.array([v[:4] for v in p['building_footprints']]);terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));inv=terrain.matrix_world.inverted();direc=inv.to_3x3()@Vector((0,0,-1));road=np.concatenate([np.array(v['center'])[:,:2]*[100,-100] for v in m['roads']]);width=np.concatenate([np.array(v['halfwidth'])*100 for v in m['roads']]);walk=np.array([v[:2] for route in p['walk_routes'] for v in route]);shop=np.array([v['center'][:2] for v in json.loads((W/'spacing_expansion_selected.json').read_text())['shops']]);stations=np.array([v['position'][:2] for v in p['stations']]);added=[]
for item in list(m['instances']):
 if len(added)>=20:break
 if item['mesh'] in ['SM_Mapa_081'] or item['mesh'].startswith('SM_Mapa_Road'):continue
 lo,hi=np.array(item.get('bounds',[[0]*3,[0]*3]));sx,sy=(hi-lo)[:2]*100
 if hi[2]-lo[2]<9 or sx<400 or sy<400 or max(sx,sy)>2400:continue
 for dx,dy in [(sx+1000,0),(-sx-1000,0),(0,sy+1000),(0,-sy-1000)]:
  x=(lo[0]+hi[0])*50+dx;y=-(lo[1]+hi[1])*50+dy;hx=sx/2;hy=sy/2;rad=math.hypot(hx,hy)
  if abs(x)>60000 or abs(y)>75000:continue
  if np.any((x+hx+300>boxes[:,0])&(x-hx-300<boxes[:,2])&(y+hy+300>boxes[:,1])&(y-hy-300<boxes[:,3])):continue
  if np.any(np.linalg.norm(road-[x,y],axis=1)<width+rad+300):continue
  if np.min(np.linalg.norm(walk-[x,y],axis=1))<rad+400:continue
  if np.min(np.linalg.norm(shop-[x,y],axis=1))<rad+3200:continue
  if np.min(np.linalg.norm(stations-[x,y],axis=1))<rad+3000:continue
  zs=[]
  for xx,yy in [(x,y),(x-hx,y-hy),(x+hx,y-hy),(x-hx,y+hy),(x+hx,y+hy)]:
   hit,co,n,j=terrain.ray_cast(inv@Vector((xx/100,-yy/100,200)),direc);zs.append((terrain.matrix_world@co).z if hit else 9999)
  if max(zs)>.3 or min(zs)<-.3:continue
  ob=bpy.data.objects.get(item['source']);new=ob.copy();new.data=ob.data;new.name=ob.name+' | complemento';bpy.context.scene.collection.objects.link(new);new.location.x+=dx/100;new.location.y-=dy/100
  q=copy.deepcopy(item);q['source']=new.name;q['location'][0]+=dx/100;q['location'][1]-=dy/100
  for b in q['bounds']:b[0]+=dx/100;b[1]-=dy/100
  m['instances'].append(q);foot=[x-hx,y-hy,x+hx,y+hy,new.name];p['building_footprints'].append(foot);boxes=np.vstack([boxes,foot[:4]]);added.append({'source':item['source'],'copy':new.name,'position':[x,y,0]});break
m['urban_infill_count']=len(added);(W/'manifest.json').write_text(json.dumps(m));(W/'integration_plan.json').write_text(json.dumps(p));(W/'urban_infill_report.json').write_text(json.dumps(added,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(W/'Mapa_Completo_Andenes_Ampliado.blend'));print('SAFE_SAME_MODEL_INFILL',len(added))
