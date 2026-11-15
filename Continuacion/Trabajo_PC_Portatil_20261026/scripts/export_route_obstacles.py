import unreal,json,sys
from pathlib import Path
R=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(R/'python_deps'))
from shapely.geometry import LineString,MultiPoint,Point
from shapely.ops import unary_union
S=R.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2';lanes=json.loads((S/'actual_lanes.json').read_text());near=unary_union([LineString(p+[p[0]]).buffer(1800) for i,p in enumerate(lanes) if i not in [4,5]])
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
oldhits=json.loads((R/'lane_static_obstacles_low_clearance.json').read_text());targets={(x['actor'],x['component']) for x in oldhits};rows=[]
def clip(poly,z,above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ina=a[2]>=z if above else a[2]<=z;inb=b[2]>=z if above else b[2]<=z
  if ina:out.append(a)
  if ina!=inb:
   u=(z-a[2])/(b[2]-a[2]);out.append(tuple(a[k]+u*(b[k]-a[k]) for k in range(3)))
 return out
for a in aa.get_all_level_actors():
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if (a.get_name(),c.get_name()) not in targets or a.get_name()=='BP_MapaCompletoGeometry_C_1':continue
  mesh=c.static_mesh;dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(use_build_scale=False),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.RENDER_DATA))
  _,vl,_=unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dm,False);vs=unreal.GeometryScript_List.convert_vector_list_to_array(vl)
  _,tl,_=unreal.GeometryScript_MeshQueries.get_all_triangle_indices(dm,False);ts=unreal.GeometryScript_List.convert_triangle_list_to_array(tl)
  transforms=[c.get_instance_transform(i,True) for i in range(c.get_instance_count())] if isinstance(c,unreal.InstancedStaticMeshComponent) else [c.get_world_transform()]
  shapes=[]
  for tr in transforms:
   bounds=mesh.get_bounds();center=unreal.MathLibrary.transform_location(tr,bounds.origin);radius=bounds.box_extent.length()*max(abs(tr.scale3d.x),abs(tr.scale3d.y),abs(tr.scale3d.z));
   if not near.intersects(Point(center.x,center.y).buffer(radius+1)):continue
   world=[unreal.MathLibrary.transform_location(tr,v) for v in vs]
   for t in ts:
    if min(t.x,t.y,t.z)<0:continue
    pts=[world[t.x],world[t.y],world[t.z]]
    if max(v.z for v in pts)<35 or min(v.z for v in pts)>400:continue
    p=clip([tuple(v.to_tuple()) for v in pts],35,True)
    if p:p=clip(p,400,False)
    if not p:continue
    shape=MultiPoint([(v[0],v[1]) for v in p]).convex_hull
    if near.intersects(shape):shapes.append(shape.buffer(.5))
  geom=unary_union(shapes);rows.append(dict(actor=a.get_name(),component=c.get_name(),wkt=geom.wkt,triangles=len(ts)));(R/'route_obstacle_footprints.json').write_text(json.dumps(rows));unreal.log('RESUME_ROUTE_OBSTACLE '+a.get_name()+' '+str(len(shapes)))
rows.extend([dict(actor=x['actor'],component=x['component'],wkt=Point(x['impact'][:2]).buffer(100).wkt,triangles=0,approximation=True) for x in oldhits if x['actor']=='BP_MapaCompletoGeometry_C_1']);(R/'route_obstacle_footprints.json').write_text(json.dumps(rows));unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('RESUME_ROUTE_OBSTACLES_EXPORTED '+str(len(rows)))