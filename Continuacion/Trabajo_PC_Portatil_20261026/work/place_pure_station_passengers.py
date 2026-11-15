import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
# Keep both platform doorway openings aligned with the bus's front doors, in either direction.
b=unreal.load_asset('/Game/World/BlueprintWorld/BP_CityGeometry');cdo=unreal.get_default_object(b.generated_class());stations=[-27000.,-7000.,17000.,32000.];old=list(cdo.get_editor_property('Decor_7'));kept=[];removed=0
for t in old:
 q=t.translation
 if abs(abs(q.y)-160)<2 and abs(q.z-210)<2 and any(abs(q.x-x)<1400 for x in stations):removed+=1
 else:kept.append(t)
for x in stations:
 for y in [-160.,160.]:
  for lo,hi in [(-1375.,-560.),(-200.,200.),(560.,1375.)]:kept.append(unreal.Transform(location=unreal.Vector(x+(lo+hi)/2,y,210),scale=unreal.Vector((hi-lo)/100,.12,2)))
cdo.set_editor_property('Decor_7',kept)
for h in sub.k2_gather_subobject_data_for_blueprint(b):
 if str(lib.get_variable_name(lib.get_data(h)))=='Geometry_Decor_7':
  o=lib.get_object_for_blueprint(lib.get_data(h),b);o.clear_instances();o.add_instances(kept,False,False,False)
assert E.compile_blueprint(b);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
# Solid voxel seats inside the bus, with no invisible collision obstructing its aisle.
bus=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_Traffic_TransMilenio');root=sub.k2_gather_subobject_data_for_blueprint(bus)[0]
for h in sub.k2_gather_subobject_data_for_blueprint(bus):
 if str(lib.get_variable_name(lib.get_data(h)))=='VehicleRoot':root=h
for i in range(4):
 for part,z,scale,dx in [('Cushion',150,unreal.Vector(.48,.48,.12),0),('Back',178,unreal.Vector(.12,.48,.44),-24)]:
  name='PassengerSeat_'+str(i)+'_'+part;found=None
  for h in sub.k2_gather_subobject_data_for_blueprint(bus):
   if str(lib.get_variable_name(lib.get_data(h)))==name:found=h;break
  if found is None:
   found,why=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.StaticMeshComponent,blueprint_context=bus));assert not str(why);assert sub.rename_subobject(found,unreal.Text(name))
  o=lib.get_object_for_blueprint(lib.get_data(found),bus);o.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));o.set_editor_property('relative_location',unreal.Vector(300-200*i+dx,-65,z));o.set_editor_property('relative_scale3d',scale);o.set_collision_profile_name('NoCollision');o.set_editor_property('can_ever_affect_navigation',False)
assert E.compile_blueprint(bus);assert unreal.EditorAssetLibrary.save_loaded_asset(bus,only_if_is_dirty=False)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);models=json.loads((r/'work/pure_crowd_models.json').read_text());count=0
for path in ['/Game/Maps/Bogota_Blueprint_Integration','/Game/QA/PureIntegratedWorld']:
 assert unreal.EditorLoadingAndSavingUtils.load_map(path)
 for oldActor in actors.get_all_level_actors():
  if oldActor.get_class().get_path_name()=='/Game/Traffic/Transit/BP_StationPassenger.BP_StationPassenger_C':actors.destroy_actor(oldActor)
 for station,x in enumerate(stations):
  for i in range(4):
   model=models[(station*11+i*7)%len(models)];c=unreal.get_default_object(unreal.load_asset(model['asset']).generated_class());m=c.get_editor_property('mesh');p=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/Traffic/Transit/BP_StationPassenger.BP_StationPassenger_C'),unreal.Vector(x+380+i*70,0,198));p.set_editor_property('Model',m.get_skeletal_mesh_asset());p.set_editor_property('SkinMaterial',m.get_material(0));p.set_editor_property('Station',station);p.set_editor_property('PassengerId',i);p.set_actor_label('Station_'+str(station)+'_Passenger_'+str(i));count+=1
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,path)
(r/'work/pure_transit_placement.json').write_text(json.dumps({'passengers_per_map':16,'maps':2,'seats':4,'old_glass_panels_replaced':removed,'board_and_alight_runtime_checks':8,'status':'STAGING_NOT_MAIN'}));unreal.log('PURE_TRANSIT_STATIONS_PLACED_PASS')
