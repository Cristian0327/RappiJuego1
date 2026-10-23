import json,numpy as np,math,sys
from pathlib import Path
from scipy.ndimage import map_coordinates,gaussian_filter,gaussian_filter1d
from scipy.spatial import cKDTree
R=Path.cwd();C=R/'compact_city';O=R/'urban_refresh';U=R/'urban_corrections';sys.path.insert(0,str(O/'python_deps'));from shapely.geometry import LineString,Point;from shapely.ops import nearest_points
p=json.loads((O/'secondary_road_plan.json').read_text());m=json.loads((R/'new_map_audit/manifest.json').read_text());main=LineString((np.array(m['roads'][0]['center'])*[100,-100,100])[:,:2]);network=main
# Keep each authored street and join short open tips to the existing connected road network.
for row in p['secondary_roads']:
 line=LineString(row['samples'])
 if line.distance(network)>1:
  a,b=nearest_points(line,network);q=np.array(row['samples']);at=np.linalg.norm(q-np.array(a.coords[0]),axis=1).argmin();join=np.array(b.coords[0]);prefix=q[:at+1];tail=q[at:];connector=np.linspace(q[at],join,max(2,int(np.linalg.norm(q[at]-join)/50)+1));row['connection_branch']=connector.tolist();network=network.union(LineString(connector))
 network=network.union(LineString(row['samples']))
# Store the connector as a genuine junction branch; it never changes the principal route.
branches=[]
for row in p['secondary_roads']:
 if row.get('connection_branch'):branches.append(dict(name=row['name']+'_union_principal',samples=row.pop('connection_branch'),width=480,sidewalk=140))
p['secondary_roads']+=branches
h=np.load(C/'original_terrain_heights_2m.npy');smooth=gaussian_filter(np.nan_to_num(h),2)
mainpts=np.concatenate([np.array(v['center'])*[100,-100,100] for v in m['roads']]);tree=cKDTree(mainpts[:,:2])
def sample(q,source=smooth):return map_coordinates(source,[(q[:,1]+50000)/200,(q[:,0]+40000)/200],order=1,mode='nearest')
def limited(q,z):
 ds=np.linalg.norm(np.diff(q,axis=0),axis=1);z=np.maximum(0,z)
 for i in range(1,len(z)):z[i]=min(z[i],z[i-1]+.20*ds[i-1])
 for i in range(len(z)-2,-1,-1):z[i]=min(z[i],z[i+1]+.20*ds[i])
 return z
for row in p['secondary_roads']:
 q=np.array(row['samples']);d=tree.query(q)[0];z=sample(q)*np.clip((d-1600)/1000,0,1);row['heights_cm']=limited(q,z).tolist()
for _ in range(3):
 for i,a in enumerate(p['secondary_roads']):
  la=LineString(a['samples']);ta=cKDTree(a['samples'])
  for b in p['secondary_roads'][i+1:]:
   it=la.intersection(LineString(b['samples']));pts=[it] if it.geom_type=='Point' else list(it.geoms) if it.geom_type=='MultiPoint' else []
   for pt in pts:
    ia=ta.query(pt.coords[0])[1];ib=cKDTree(b['samples']).query(pt.coords[0])[1];z=min(a['heights_cm'][ia],b['heights_cm'][ib]);a['heights_cm'][ia]=z;b['heights_cm'][ib]=z
 for row in p['secondary_roads']:row['heights_cm']=limited(np.array(row['samples']),np.array(row['heights_cm'])).tolist()
(O/'secondary_road_plan.json').write_text(json.dumps(p))
# The original Monserrate tip is above the city. A player-only shared path uses two safe hairpin turns.
source=json.loads((C/'monserrate_authored_segment.json').read_text());base=np.array(source['base']);summit=np.array(source['summit']);u=summit-base;D=np.linalg.norm(u);u/=D;v=np.array([-u[1],u[0]]);Rturn=D/4;extent=7000.;best=None
from scipy.ndimage import distance_transform_edt
physical=distance_transform_edt(np.array(__import__('PIL.Image',fromlist=['Image']).open(R/'new_map_audit/obstacles.png'))==0)*100
cityTree=cKDTree(xyz[:,:2]) if 'xyz' in globals() else cKDTree(np.concatenate([np.array(v['samples']) for v in p['secondary_roads']]))
for orientation in [-1,1]:
 vv=v*orientation
 for center in np.linspace(-3500,3500,29):
  vmax=center+extent;vmin=center-extent;local=[]
  def segment(a,b):local.extend(np.linspace(a,b,max(2,int(np.linalg.norm(np.array(a)-b)/50)+1),endpoint=False).tolist())
  segment([0,0],[0,vmax])
  for theta in np.linspace(0,math.pi,60,endpoint=False):local.append([Rturn-Rturn*math.cos(theta),vmax+Rturn*math.sin(theta)])
  segment([2*Rturn,vmax],[2*Rturn,vmin])
  for theta in np.linspace(0,math.pi,60,endpoint=False):local.append([3*Rturn-Rturn*math.cos(theta),vmin-Rturn*math.sin(theta)])
  segment([D,vmin],[D,0]);local.append([D,0]);q=base+np.array(local)[:,0,None]*u+np.array(local)[:,1,None]*vv;length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))];z0=0.;zt=float(sample(summit[None,:],h)[0]);z=z0+(zt-z0)*length/length[-1];natural=sample(q,h);ix=np.clip(np.rint((q[:,0]+40000)/100).astype(int),0,799);iy=np.clip(np.rint((q[:,1]+50000)/100).astype(int),0,999);outside_entry=length>1200;conflicts=np.sum(outside_entry & ((tree.query(q)[0]<2000)|(physical[iy,ix]<175)|(cityTree.query(q)[0]<400)));cost=np.mean((z-natural)**2)+max(abs(z-natural))**2*.25+conflicts*1e9
  if best is None or cost<best[0]:best=(cost,q,z,length,natural)
_,q,z,length,natural=best;grade=float(np.max(abs(np.diff(z))/np.linalg.norm(np.diff(q,axis=0),axis=1)));assert grade<.20
hill=dict(name='Camino_Monserrate_Jugador',points=np.column_stack([q,z]).tolist(),base=[*q[0],float(z[0])],summit=[*q[-1],float(z[-1])],length_m=float(length[-1]/100),maximum_grade=grade,minimum_turn_radius_m=float(Rturn/100),width_cm=300,player_allowed=['walk','bicycle','motorcycle'],npc_vehicles_allowed=False,cars_allowed=False,maximum_cut_fill_m=float(np.max(abs(z-natural))/100));(C/'monserrate_path.json').write_text(json.dumps(hill,indent=2));print('MONSERRATE_PLAYER_PATH',hill['length_m'],'m','grade',grade,'turn',Rturn/100,'cutfill',hill['maximum_cut_fill_m'])
# A single authoritative height list drives both the pavement and the graded terrain.
xyz=np.concatenate([np.column_stack([np.array(v['samples']),v['heights_cm']]) for v in p['secondary_roads']]);np.save(C/'graded_city_road_samples.npy',xyz);print('ALL_AUTHORED_STREETS_CONNECTED',len(p['secondary_roads']),'with',len(branches),'short connectors')
