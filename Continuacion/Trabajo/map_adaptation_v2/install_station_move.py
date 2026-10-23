from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');row=json.loads((P/'station_move.json').read_text());origin=unreal.Vector(*row['old']);delta=unreal.Vector(*row['delta']);angle=math.radians(row['yaw']);t=unreal.Vector(math.cos(angle),math.sin(angle),0);n=unreal.Vector(-t.y,t.x,0);T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/World/BogotaUrban/Geometry'
for file in (P/'station_access_export').glob('*.fbx'):
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.automated_import_should_detect_type=False;im=opt.static_mesh_import_data;im.combine_meshes=True;im.auto_generate_collision=False;im.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;im.convert_scene=True;im.convert_scene_unit=True;task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=folder;task.destination_name=file.stem;task.options=opt;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task]);mesh=unreal.load_asset(folder+'/'+file.stem)
 for i in range(len(mesh.static_materials)):mesh.set_material(i,unreal.load_asset('/Game/World/BogotaUrban/M_BogotaUrban'))
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);mesh.get_editor_property('body_setup').set_editor_property('double_sided_geometry',True);save(mesh)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);station=next(a for a in aa.get_all_level_actors() if a.get_name()==row['actor']);sid=station.get_editor_property('StationId');moved=[]
# Idempotent: the cached original and new positions define the whole move.
if (station.get_actor_location()-origin).length()<100:
 station.set_actor_location(unreal.Vector(*row['new']),False,True)
 for a in aa.get_all_level_actors():
  cls=a.get_class().get_name();p=a.get_actor_location();offset=p-origin
  if cls=='BP_StationPassenger_C' and a.get_editor_property('Station')==sid:a.set_actor_location(p+delta,False,True);moved.append(a.get_name())
  if cls=='BP_BogotaSignal_C' and a.get_editor_property('SignalGroup')==2 and abs(offset.dot(t))<4000 and abs(offset.dot(n))<2800:a.set_actor_location(p+delta,False,True)
  if cls=='BP_CrosswalkCitizen_C':
   route=list(a.get_editor_property('Route'))
   if any(abs((q-origin).dot(t))<3500 and abs((q-origin).dot(n))<2500 and q.z>60 for q in route):a.set_editor_property('Route',[q+delta for q in route]);a.set_actor_location(p+delta,False,True)
b=use(TM);c=unreal.get_default_object(b.generated_class());points=list(c.get_editor_property('UrbanCrossingCenters'))
for i,p in enumerate(points):
 offset=p-origin
 if abs(offset.dot(t))<4000 and abs(offset.dot(n))<2800:points[i]=p+delta
c.set_editor_property('UrbanCrossingCenters',points);save(b)
for a in aa.get_all_level_actors():
 if a.get_class().get_name()=='BP_TrafficManager_C':a.set_editor_property('UrbanCrossingCenters',points)
lane=aa.spawn_actor_from_class(unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_6').generated_class(),unreal.Vector());v=unreal.load_asset(V.split('.')[0]);stops=list(unreal.get_default_object(v.generated_class()).get_editor_property('TransitStopPositions'));wanted=stops[sid]+delta;dist=lane.call_method('ClosestDistance',(wanted,));stops[sid]=lane.call_method('SamplePosition',(dist,))
for path in [V,'/Game/World/BlueprintWorld/Traffic/BP_Traffic_TransMilenio']:
 b=use(path);unreal.get_default_object(b.generated_class()).set_editor_property('TransitStopPositions',stops);save(b)
aa.destroy_actor(lane);assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False);(P/'station_move_report.json').write_text(json.dumps(dict(station=sid,delta=row['delta'],passengers=moved,bus_stop=list(stops[sid].to_tuple())),indent=2));unreal.log('V2_STATION_ACCESS_AND_STOP_SYNCHRONIZED')
